# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.aio.xra.py
    ~~~~~~~~~~~~~~~~~~~~~~

SPPAS native XRA reader and writer.

"""
import logging
import xml.etree.cElementTree as ET

from sppas.src.config import sg
from sppas.src.utils.makeunicode import u
from sppas.src.utils.datatype import sppasTime

from ..media import sppasMedia
from ..ctrlvocab import sppasCtrlVocab
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlocation import sppasDisjoint
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag

from .basetrs import sppasBaseIO

# ---------------------------------------------------------------------------


class sppasJRA(object):
    """JRA is intended to be the next default format of annotated files."""

    # -----------------------------------------------------------------------

    @staticmethod
    def format_label(label_root, label):
        """Add a 'Label' in the dict from a sppasLabel().

        :param label_root: (list)
        :param label: (sppasLabel)

        """
        tags = list()
        for tag, score in label:
            tag_node = dict()
            tag_node['score'] = score
            sppasJRA._format_tag(tag_node, tag)
            tags.append(tag_node)
        label_root.append(tags)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_tag(tag_node, tag):
        """Add a 'Tag' element from a sppasTag().

        :param tag_node: (dict)
        :param tag: (sppasTag)

        """
        tag_node['type'] = tag.get_type()
        tag_node['text'] = tag.get_content()

    # -----------------------------------------------------------------------

    @staticmethod
    def parse_label(tags_list):
        """Create a sppasLabel from a list of tag dictionaries.

        """
        tags = list()
        scores = list()
        for tag_item in tags_list:
            tags.append(sppasJRA._parse_tag(tag_item))
            scores.append(tag_item['score'])

        return sppasLabel(tags, scores)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_tag(tag_dict):
        """Create a 'sppasTag' from a 'Tag' dict.

        :param tag_dict: (dict) 2 keys expected: text and type
        :return: (sppasTag)

        """
        return sppasTag(tag_dict['text'], tag_dict['type'])

# ---------------------------------------------------------------------------


class sppasXRA(sppasBaseIO):
    """SPPAS XRA reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    xra files are the native file format of the GPL tool SPPAS.

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of XRA format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with open(filename, 'r') as fp:
                for i in range(10):
                    line = fp.readline()
                    if "<Document" in line:
                        return True
                fp.close()
        except IOError:
            return False

        return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new XRA instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasXRA, self).__init__(name)

        self.default_extension = "xra"
        self.software = "SPPAS"

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = True
        self._accept_media = True
        self._accept_hierarchy = True
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = True
        self._accept_alt_localization = True
        self._accept_alt_tag = True
        self._accept_radius = True
        self._accept_gaps = True
        self._accept_overlaps = True

        self.__format = "1.4"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read an XRA file and fill the Transcription.

        :param filename: (str)

        """
        tree = ET.parse(filename)
        root = tree.getroot()

        if "name" in root.attrib:
            self.set_name(root.attrib['name'])

        if "version" in root.attrib:
            self.set_meta('file_created_format_version',
                          root.attrib['version'])

        if "date" in root.attrib:
            self.set_meta('file_created_date',
                          root.attrib['date'])

        if "author" in root.attrib:
            self.set_meta('file_created_author',
                          root.attrib['author'])

        metadata_root = root.find('Metadata')
        if metadata_root is not None:
            sppasXRA._parse_metadata(self, metadata_root)

        for tier_root in root.findall('Tier'):
            self._parse_tier(tier_root)

        for media_root in root.findall('Media'):
            self._parse_media(media_root)

        hierarchy_root = root.find('Hierarchy')
        if hierarchy_root is not None:
            self._parse_hierarchy(hierarchy_root)

        for vocabulary_root in root.findall('Vocabulary'):
            self._parse_vocabulary(vocabulary_root)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_metadata(meta_object, metadata_root):
        """Read any kind of metadata.

        :param meta_object: (sppasMetadata)
        :param metadata_root: (ET) XML Element tree root.

        """
        if metadata_root is not None:
            for entry_node in metadata_root.findall('Entry'):
                try:
                    key = entry_node.attrib['key']
                except Exception:
                    # XRA < 1.2
                    key = entry_node.attrib['Key']

                if entry_node.text is not None:
                    meta_object.set_meta(key, entry_node.text)

    # -----------------------------------------------------------------------

    def _parse_tier(self, tier_root):
        """Parse a 'Tier' element to create a sppasTier().

        :param tier_root: (ET) XML Element tree root.

        """
        name = None
        if "tiername" in tier_root.attrib:
            name = tier_root.attrib['tiername']

        try:
            tid = tier_root.attrib['id']
        except Exception:
            # XRA < 1.2
            tid = tier_root.attrib['ID']
        if name is not None:
            tier = self.create_tier(name)
        else:
            tier = self.create_tier(tid)

        # Set metadata
        sppasXRA._parse_metadata(tier, tier_root.find('Metadata'))
        tier.set_meta("id", tid)

        for annotation_root in tier_root.findall('Annotation'):
            sppasXRA._parse_annotation(tier, annotation_root)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_annotation(tier, annotation_root):
        """Parse an 'Annotation' element and create a sppasAnnotation().

        :param tier: (sppasTier) Tier to add the newly created annotation.
        :param annotation_root: (ET) XML Element tree root.

        """
        location_root = annotation_root.find('Location')
        location = sppasXRA._parse_location(location_root)

        labels = list()
        for label_root in annotation_root.findall('Label'):
            labels.append(sppasXRA.parse_label(label_root))

        ann = tier.create_annotation(location, labels)
        sppasXRA._parse_metadata(ann, annotation_root.find('Metadata'))

        # Attributes (from XRA 1.4)

        if 'id' in annotation_root.attrib:     # required
            ann.set_meta('id', annotation_root.attrib['id'])

        if 'score' in annotation_root.attrib:  # optional
            ann.set_score(float(annotation_root.attrib['score']))

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_location(location_root):
        """Parse a 'Location' element an create a sppasLocation().

        :param location_root: (ET) XML Element tree root.
        :returns: (sppasLocation)

        """
        # read list of localizations
        location = sppasLocation()
        for localization_root in list(location_root):
            localization, score = sppasXRA._parse_localization(localization_root)
            if localization is not None:
                location.append(localization, score)

        if len(location) == 0:
            # XRA < 1.3
            for localization_root in location_root.findall('Localization'):
                for loc_root in list(localization_root):
                    localization, score = sppasXRA._parse_localization(loc_root)
                    score = float(localization_root.attrib["score"])
                    location.append(localization, score)

        return location

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_localization(localization_root):
        """Parse a 'Localization' element and create a sppasLocalization().

        :param localization_root: (ET) XML Element tree root.
        :returns: (sppasLocalization)

        """
        localization = None
        score = None
        loc_str = localization_root.tag.lower()  # to be compatible with all versions

        if 'point' in loc_str:
            localization, score = sppasXRA._parse_point(localization_root)

        elif 'interval' in loc_str:
            localization, score = sppasXRA._parse_interval(localization_root)

        elif 'disjoint' in loc_str:
            localization, score = sppasXRA._parse_disjoint(localization_root)

        return localization, score

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_point(point_node):
        """Parse a 'Point' element and create a sppasPoint().

        :param point_node: (ET) XML Element node.
        :returns: (sppasPoint)

        """
        # Attribute score
        if 'score' in point_node.attrib:
            score = float(point_node.attrib['score'])
        else:
            score = None

        midpoint_str = point_node.attrib['midpoint']
        try:
            radius_str = point_node.attrib['radius']
        except:
            radius_str = None

        if midpoint_str.isdigit():
            midpoint = int(midpoint_str)
            try:
                radius = int(radius_str)
            except:
                radius = None
        else:
            try:
                midpoint = float(midpoint_str)
                try:
                    radius = float(radius_str)
                except:
                    radius = None
            except:
                midpoint = midpoint_str
                radius = radius_str

        return sppasPoint(midpoint, radius), score

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_interval(interval_root):
        """Parse an 'Interval' element and create a sppasInterval().

        :param interval_root: (ET) XML Element tree root.
        :returns: (sppasInterval)

        """
        # Attribute score
        if 'score' in interval_root.attrib:
            score = float(interval_root.attrib['score'])
        else:
            score = None

        begin_node = interval_root.find('Begin')
        end_node = interval_root.find('End')

        begin, s1 = sppasXRA._parse_point(begin_node)
        end, s2 = sppasXRA._parse_point(end_node)

        return sppasInterval(begin, end), score

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_disjoint(disjoint_root):
        """Parse a 'Disjoint' element and create a sppasDisjoint().

        :param disjoint_root: (ET) XML Element tree root.
        :returns: (sppasDisjoint)

        """
        # Attribute score
        if 'score' in disjoint_root.attrib:
            score = float(disjoint_root.attrib['score'])
        else:
            score = None

        disjoint = sppasDisjoint()
        for interval_root in disjoint_root.findall('Interval'):
            interval = sppasXRA._parse_interval(interval_root)
            disjoint.append_interval(interval)

        # XRA < 1.3
        if len(disjoint) == 0:
            for interval_root in disjoint_root.findall('TimeInterval'):
                interval = sppasXRA._parse_interval(interval_root)
                disjoint.append_interval(interval)
            for interval_root in disjoint_root.findall('FrameInterval'):
                interval = sppasXRA._parse_interval(interval_root)
                disjoint.append_interval(interval)

        return disjoint, score

    # -----------------------------------------------------------------------

    @staticmethod
    def parse_label(label_root):
        """Parse a 'Label' element and return it.

        :param label_root: (ET) XML Element tree root.
        :returns: (sppasLabel)

        """
        # read list of tags
        label = None
        for tag_root in label_root.findall('Tag'):
            tag, score = sppasXRA._parse_tag(tag_root)
            if label is None:
                label = sppasLabel(tag, score)
            else:
                label.append(tag, score)

        if label is None:
            # XRA < 1.3
            for tag_root in label_root.findall('Text'):
                tag, score = sppasXRA._parse_tag(tag_root)
                if label is None:
                    label = sppasLabel(tag, score)
                else:
                    label.append(tag, score)

        return label

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_tag(tag_node):
        """Parse a 'Tag' element and create a sppasTag().

        :param tag_node: (ET) XML Element node.
        :returns: (sppasTag)

        """
        # Attribute score
        if 'score' in tag_node.attrib:
            score = float(tag_node.attrib['score'])
        else:
            score = None

        # Attribute type (str, bool, int, float)
        if 'type' in tag_node.attrib:
            data_type = tag_node.attrib['type']
        else:
            data_type = "str"

        # Tag content
        content = (tag_node.text if tag_node.text is not None else '')
        tag = sppasTag(content, data_type)

        return tag, score

    # -----------------------------------------------------------------------

    def _parse_media(self, media_root):
        """Parse a 'Media' element and add create a sppasMedia().

        :param media_root: (ET) XML Element tree root.

        """
        # Create a sppasMedia instance
        media_url = media_root.attrib['url']
        media_id = media_root.attrib['id']
        media_mime = None
        if 'mimetype' in media_root.attrib:
            media_mime = media_root.attrib['mimetype']

        media = sppasMedia(media_url, media_id, media_mime)
        self.add_media(media)
        sppasXRA._parse_metadata(media, media_root.find('Metadata'))

        # Add content if any
        content_root = media_root.find('Content')
        if content_root:
            media.set_content(content_root.text)

        # Link to tiers
        for tier_node in media_root.findall('Tier'):
            tier_id = tier_node.attrib['id']
            for tier in self._tiers:
                if tier.get_id() == tier_id:
                    tier.set_media(media)

    # -----------------------------------------------------------------------

    def _parse_hierarchy(self, hierarchy_root):
        """Parse a 'Hierarchy' element and set it.

        :param hierarchy_root: (ET) XML Element tree root.

        """
        for link_node in hierarchy_root.findall('Link'):
            try:
                hierarchy_type = link_node.attrib['type']
                parent_tier_id = link_node.attrib['from']
                child_tier_id = link_node.attrib['to']
            except:
                # XRA < 1.2
                hierarchy_type = link_node.attrib['Type']
                parent_tier_id = link_node.attrib['From']
                child_tier_id = link_node.attrib['To']

            parent_tier = None
            child_tier = None
            for tier in self:
                if tier.get_id() == parent_tier_id:
                    parent_tier = tier
                if tier.get_id() == child_tier_id:
                    child_tier = tier

            try:
                self.add_hierarchy_link(hierarchy_type,
                                        parent_tier,
                                        child_tier)
            except Exception as e:
                # print(e)
                logging.error("Corrupted hierarchy link: {:s}".format(str(e)))
                pass

    # -----------------------------------------------------------------------

    def _parse_vocabulary(self, vocabulary_root):
        """Parse a 'Vocabulary' element and set it.

        :param hierarchy_root: (ET) XML Element tree root.

        """
        # Create a CtrlVocab instance
        if 'id' in vocabulary_root.attrib:
            id_vocab = vocabulary_root.attrib['id']
        else:
            # XRA < 1.2
            id_vocab = vocabulary_root.attrib['ID']
        ctrl_vocab = sppasCtrlVocab(id_vocab)
        self.add_ctrl_vocab(ctrl_vocab)
        sppasXRA._parse_metadata(ctrl_vocab, vocabulary_root.find('Metadata'))

        # Description
        if "description" in vocabulary_root.attrib:
            ctrl_vocab.set_description(vocabulary_root.attrib['description'])

        # Add the list of entries
        for entry_node in vocabulary_root.findall('Entry'):
            # Type of the entry
            if "type" in entry_node.attrib:
                tag_type = entry_node.attrib['type']
            else:
                tag_type = "str"
            entry_text = sppasTag(entry_node.text, tag_type)
            entry_desc = ""
            if "description" in entry_node.attrib:
                entry_desc = entry_node.attrib['description']
            ctrl_vocab.add(entry_text, entry_desc)

        # Link to tiers
        for tier_node in vocabulary_root.findall('Tier'):
            if 'id' in tier_node.attrib:
                tier_id = tier_node.attrib['id']
            else:
                # XRA < 1.2
                tier_id = tier_node.attrib['ID']
            for tier in self:
                if tier.get_meta('id') == tier_id:
                    tier.set_ctrl_vocab(ctrl_vocab)

    # -----------------------------------------------------------------------
    # Write XRA 1.4
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write an XRA file.

        :param filename: (str)

        """
        root = ET.Element('Document')
        author = sg.__name__ + " " + sg.__version__ + " (C) " + sg.__author__
        root.set('author', author)
        root.set('date', sppasTime().now)
        root.set('format', self.__format)
        root.set('name', self.get_name())

        metadata_root = ET.SubElement(root, 'Metadata')
        sppasXRA.format_metadata(metadata_root, self)
        if len(metadata_root.findall('Entry')) == 0:
            root.remove(metadata_root)

        for tier in self:
            tier_root = ET.SubElement(root, 'Tier')
            sppasXRA.format_tier(tier_root, tier)

        for media in self.get_media_list():
            media_root = ET.SubElement(root, 'Media')
            self._format_media(media_root, media)

        hierarchy_root = ET.SubElement(root, 'Hierarchy')
        self._format_hierarchy(hierarchy_root)

        for vocabulary in self.get_ctrl_vocab_list():
            vocabulary_root = ET.SubElement(root, 'Vocabulary')
            self._format_vocabulary(vocabulary_root, vocabulary)

        sppasXRA.indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename,
                   encoding=sg.__encoding__,
                   method="xml",
                   xml_declaration=True)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_metadata(metadata_root, meta_object, exclude=[]):
        """Add 'Metadata' element in the tree from a sppasMetaData().

        :param metadata_root: (ET) XML Element tree root.
        :param meta_object: (sppasMetadata)
        :param exclude: (list) List of keys to exclude

        """
        for key in meta_object.get_meta_keys():
            if key not in exclude:
                value = meta_object.get_meta(key)

                entry = ET.SubElement(metadata_root, 'Entry')
                entry.set('key', key)
                entry.text = value

    # -----------------------------------------------------------------------

    @staticmethod
    def format_tier(tier_root, tier):
        """Add a 'Tier' object in the tree from a sppasTier().

        :param tier_root: (ET) XML Element tree root.
        :param tier: (sppasTier)

        """
        # Tier identifier
        tier_id = tier.get_meta('id')
        tier_root.set("id", tier_id)

        # Tier name
        tier_root.set("tiername", tier.get_name())

        # Tier Metadata
        metadata_root = ET.SubElement(tier_root, 'Metadata')
        sppasXRA.format_metadata(metadata_root, tier, exclude=['id'])
        if len(metadata_root.findall('Entry')) == 0:
            tier_root.remove(metadata_root)

        # Tier annotations list
        for annotation in tier:
            annotation_root = ET.SubElement(tier_root, 'Annotation')
            sppasXRA.format_annotation(annotation_root, annotation)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_annotation(annotation_root, annotation):
        """Add an 'Annotation' element in the tree from a sppasAnnotation().

        :param annotation_root: (ET) XML Element tree root.
        :param annotation: (sppasAnnotation)

        """
        # Attributes:
        ann_id = annotation.get_meta('id')
        annotation_root.set("id", ann_id)
        if annotation.get_score() is not None:
            annotation_root.set("score", annotation.get_score())

        # Elements:
        metadata_root = ET.SubElement(annotation_root, 'Metadata')
        sppasXRA.format_metadata(metadata_root, annotation, exclude=['id'])
        if len(metadata_root.findall('Entry')) == 0:
            annotation_root.remove(metadata_root)

        location_root = ET.SubElement(annotation_root, 'Location')
        sppasXRA.format_location(location_root, annotation.get_location())

        for label in annotation.get_labels():
            label_root = ET.SubElement(annotation_root, 'Label')
            sppasXRA.format_label(label_root, label)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_location(location_root, location):
        """Add a 'Location' element in the tree from a sppasLocation().

        :param location_root: (ET) XML Element tree root.
        :param location: (sppasLocation)

        """
        for localization, score in location:
            if localization.is_point():
                point_node = ET.SubElement(location_root, 'Point')
                sppasXRA._format_point(point_node, localization)
                if score is not None:
                    point_node.set('score', u(str(score)))

            elif localization.is_interval():
                interval_root = ET.SubElement(location_root, 'Interval')
                sppasXRA._format_interval(interval_root, localization)
                if score is not None:
                    interval_root.set('score', u(str(score)))

            elif localization.IsTimeDisjoint():
                disjoint_root = ET.SubElement(location_root, 'Disjoint')
                sppasXRA._format_disjoint(disjoint_root, localization)
                if score is not None:
                    disjoint_root.set('score', u(str(score)))

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_point(point_node, point):
        """Add a 'Point' element in the tree from a sppasPoint().

        :param point_node: (ET) XML Element node.
        :param point: (sppasPoint)

        """
        point_node.set('midpoint', u(str(point.get_midpoint())))
        if point.get_radius() is not None:
            point_node.set('radius', u(str(point.get_radius())))

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_interval(interval_root, interval):
        """Add an 'Interval' element in the tree from a sppasInterval().

        :param interval_root: (ET) XML Element node.
        :param interval: (sppasInterval)

        """
        begin = ET.SubElement(interval_root, 'Begin')
        sppasXRA._format_point(begin, interval.get_begin())

        end = ET.SubElement(interval_root, 'End')
        sppasXRA._format_point(end, interval.get_end())

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_disjoint(disjoint_root, disjoint):
        """Add a 'Disjoint' element in the tree from a sppasDisjoint().

        :param disjoint_root: (ET) XML Element node.
        :param disjoint: (sppasDisjoint)

        """
        for interval in disjoint:
            interval_root = ET.SubElement(disjoint_root, 'Interval')
            sppasXRA._format_interval(interval_root, interval)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_label(label_root, label):
        """Add a 'Label' element in the tree from a sppasLabel().

        :param label_root: (ET) XML Element tree root.
        :param label: (sppasLabel)

        """
        for tag, score in label:
            tag_node = ET.SubElement(label_root, 'Tag')
            if score is not None:
                tag_node.set("score", str(score))
            sppasXRA._format_tag(tag_node, tag)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_tag(tag_node, tag):
        """Add a 'Tag' element in the tree from a sppasTag().

        :param tag_node: (ET) XML Element node.
        :param tag: (sppasTag)

        """
        if tag.get_type() != "str":
            tag_node.set('type', tag.get_type())
        tag_node.text = tag.get_content()

    # -----------------------------------------------------------------------

    def _format_media(self, media_root, media):
        """Add a 'Media' element in the tree from a sppasMedia.

        :param media_root: (ET) XML Element tree root.
        :param media: (sppasMedia)

        """
        # Set attribute
        media_root.set('id', media.get_meta('id'))
        media_root.set('url', media.get_filename())
        media_root.set('mimetype', media.get_mime_type())

        # Element Tier
        for tier in self:
            if tier.get_media() is None:
                continue
            if tier.get_media() == media:
                tier_node = ET.SubElement(media_root, 'Tier')
                tier_node.set('id', tier.get_meta('id'))

        # Element Metadata (except 'id')
        metadata_root = ET.SubElement(media_root, 'Metadata')
        if len(media.get_meta_keys()) > 1:
            sppasXRA.format_metadata(metadata_root, media, exclude=['id'])
        if len(metadata_root.findall('Entry')) == 0:
            media_root.remove(metadata_root)

        # Element Content
        if len(media.get_content()) > 0:
            content_node = ET.SubElement(media_root, 'Content')
            content_node.text = media.get_content()

    # -----------------------------------------------------------------------

    def _format_hierarchy(self, hierarchy_root):
        """Add a 'Hierarchy' element in the tree from a sppasHierarchy().

        :param hierarchy_root: (ET) XML Element tree root.

        """
        for child_tier in self:
            parent_tier = self._hierarchy.get_parent(child_tier)

            if parent_tier is not None:
                link_type = self._hierarchy.get_hierarchy_type(child_tier)
                link = ET.SubElement(hierarchy_root, 'Link')
                link.set('type', link_type)
                link.set('from', parent_tier.get_meta('id'))
                link.set('to', child_tier.get_meta('id'))

    # -----------------------------------------------------------------------

    def _format_vocabulary(self, vocabulary_root, vocabulary):
        """Add a 'Vocabulary' element in the tree from a sppasVocabulary().

         :param vocabulary_root: (ET) XML Element tree root.
         :param vocabulary: (sppasCtrlVocab)

        """
        # Set attribute
        vocabulary_root.set('id', vocabulary.get_name())
        if len(vocabulary.get_description()) > 0:
            vocabulary_root.set('description', vocabulary.get_description())

        # Write the list of entries (an entry is a sppasTag instance)
        for entry in vocabulary:
            entry_node = ET.SubElement(vocabulary_root, 'Entry')
            entry_node.text = entry.get_content()

            if entry.get_type() != "str":
                entry_node.set('type', entry.get_type())

            if len(vocabulary.get_tag_description(entry)) > 0:
                entry_node.set('description',
                               vocabulary.get_tag_description(entry))

        # Element Tier
        for tier in self:
            if tier.get_ctrl_vocab() == vocabulary:
                tier_node = ET.SubElement(vocabulary_root, 'Tier')
                tier_node.set('id', tier.get_meta('id'))

        # Element Metadata (except 'id')
        metadata_root = ET.SubElement(vocabulary_root, 'Metadata')
        sppasXRA.format_metadata(metadata_root, vocabulary)
        if len(metadata_root.findall('Entry')) == 0:
            vocabulary_root.remove(metadata_root)

    # -----------------------------------------------------------------------

    @staticmethod
    def indent(elem, level=0):
        """Pretty indent.

        http://effbot.org/zone/element-lib.htm#prettyprint

        """
        i = "\n" + level * "\t"
        if len(elem) > 0:
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                if level < 2:
                    elem.tail = "\n" + i
                else:
                    elem.tail = i
            for elem in elem:
                sppasXRA.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
