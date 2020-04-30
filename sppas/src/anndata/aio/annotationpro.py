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

    src.anndata.aio.annotationpro.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Annotation Pro is a tool for annotation of audio and text files:

| Klessa, K., Karpiński, M., Wagner, A. (2013).
| Annotation Pro – a new software tool for annotation of linguistic and
| paralinguistic features.
| In D. Hirst & B. Bigi (Eds.)
| Proceedings of the Tools and Resources for the Analysis of Speech Prosody
| (TRASP) Workshop, Aix en Provence, 51-54.

http://annotationpro.org/

"""

import os
import zipfile
import shutil
import random
from datetime import datetime
import xml.etree.cElementTree as ET

from sppas.src.config import sg
from sppas.src.wkps.fileutils import sppasFileUtils
from sppas.src.utils.datatype import bidict

from ..media import sppasMedia
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..anndataexc import AioFormatError
from ..anndataexc import AnnDataTypeError

from .basetrs import sppasBaseIO
from .aioutils import merge_overlapping_annotations
from .aioutils import point2interval
from .aioutils import format_labels

# ---------------------------------------------------------------------------


def pick_random_color(v1=0, v2=255):
    """Return a random RGB color."""
    c = [random.uniform(v1, v2) for _ in range(5)]
    random.shuffle(c)
    return int(c[0]), int(c[1]), int(c[2])


def rgb_to_color(r, g, b):
    """Convert a RGB color into ANTX decimal color."""
    r = int(r)
    g = int(g)
    b = int(b)

    r_hexa = hex(r % 256)[2:]   # remove '0x'
    g_hexa = hex(g % 256)[2:]   # remove '0x'
    b_hexa = hex(b % 256)[2:]   # remove '0x'
    hexa = str(r_hexa) + str(g_hexa) + str(b_hexa)
    return (int(hexa, 16)*-1) - 1


def color_to_rgb(color):
    """Convert an ANTX decimal color into RGB."""
    hexa = hex((color-1)*-1)
    l = ['0']*6
    for i in range(len(hexa) - 2):
        l[len(l) - i - 1] = hexa[len(hexa) - i - 1]

    r = int(''.join(l[0:2]), 16)
    g = int(''.join(l[2:4]), 16)
    b = int(''.join(l[4:6]), 16)

    return r, g, b

# ---------------------------------------------------------------------------


class sppasANTX(sppasBaseIO):
    """AnnotationPro ANTX reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of ANTX format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with open(filename, 'r') as fp:
                fp.readline()
                doctype_line = fp.readline().strip()
                fp.close()
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

        return 'AnnotationSystemDataSet' in doctype_line

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint, sample_rate=44100):
        """The localization is a frame value, so an integer."""
        try:
            midpoint = int(midpoint)
            midpoint = float(midpoint) / float(sample_rate)
        except ValueError:
            raise AnnDataTypeError(midpoint, "int")

        return sppasPoint(midpoint, radius=0.0005)

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasANTX instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasANTX, self).__init__(name)

        self.default_extension = "antx"
        self.software = "AnnotationPro"

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = False
        self._accept_media = True
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = False

        # Information that are both used by AnnotationPro and
        # another software tool
        self._map_meta = bidict()
        self._map_meta['Id'] = 'id'
        self._map_meta['Created'] = 'file_created_date'
        self._map_meta['Modified'] = 'file_write_date'
        self._map_meta['FileVersion'] = 'file_version'
        self._map_meta['Author'] = 'file_author'
        self._map_meta['Samplerate'] = 'media_sample_rate'
        self._map_meta['IsSelected'] = 'tier_is_selected'
        self._map_meta['IsClosed'] = 'tier_is_closed'
        self._map_meta['Height'] = 'tier_height'
        self._map_meta['Language'] = 'language_name_0'

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read an ANTX file and fill the Transcription.

        :param filename: (str)

        """
        tree = ET.parse(filename)
        root = tree.getroot()
        uri = root.tag[:root.tag.index('}')+1]

        # Create metadata
        for child in tree.iter(tag=uri+'Configuration'):
            self._parse_configuration(child, uri)

        # Create media
        for child in tree.iter(tag=uri+"AudioFile"):
            self._parse_audiofile(child, uri)

        # Create tiers
        for child in tree.iter(tag=uri+"Layer"):
            self._parse_layer(child, uri)

        # Create annotations
        for child in tree.iter(tag=uri+"Segment"):
            self._parse_segment(child, uri)

    # -----------------------------------------------------------------------

    def _parse_configuration(self, configuration_root, uri=""):
        """Get the elements 'Configuration'.

        Fill metadata of the sppasANTX instance.

        :param configuration_root: (ET) Configuration root.
        :param uri: (str)

        """
        key = configuration_root.find(uri + 'Key')
        value = configuration_root.find(uri + 'Value')

        if key is not None and value is not None:
            new_key = key.text.replace(uri, "")
            if value.text is not None:
                self.set_meta(self._map_meta.get(new_key, new_key),
                              value.text.replace(uri, ""))

    # -----------------------------------------------------------------------

    def _parse_audiofile(self, audio_root, uri=""):
        """Get the elements 'AudioFile'.

        Create a sppasMedia instance and add it.

        :param audio_root: (ET) AudioFile root.
        :param uri: (str)

        """
        media_id = audio_root.find(uri + 'Id').text
        media_url = audio_root.find(uri + 'FileName').text

        if media_id is not None and media_url is not None:

            media_id = media_id.replace(uri, '')
            media_url = media_url.replace(uri, '')

            # Create the new Media and put all information in metadata
            media = sppasMedia(media_url)
            media.set_meta("id", media_id)
            media.set_meta('media_source', 'primary')
            media.set_meta("media_sample_rate",
                           self.get_meta("media_sample_rate", "44100"))
            self.elt_to_meta(audio_root, media, uri)
            self.add_media(media)

    # -----------------------------------------------------------------------

    def _parse_layer(self, tier_root, uri=''):
        """Get the elements 'Layer'.

        :param tier_root: (ET) Layer root.
        :param uri: (str)

        """
        tier_name = tier_root.find(uri + 'Name').text
        tier = self.create_tier(tier_name)
        self.elt_to_meta(tier_root, tier, uri, ['Name'])

    # -----------------------------------------------------------------------

    def _parse_segment(self, annotation_root, uri=""):
        """Get the elements 'Segment'.

        :param annotation_root: (ET) Segment root.
        :param uri: (str)

        """
        # fix parent tier
        tier_id = annotation_root.find(uri + 'IdLayer').text
        tier = self.find_id(tier_id)
        if tier is None:
            raise AioFormatError("Layer id="+tier_id)

        segment_id = annotation_root.find(uri + 'Id').text

        # fix localization
        b = annotation_root.find(uri + 'Start').text
        d = annotation_root.find(uri + 'Duration').text
        if b in ['0', '0.', '0.0'] and d in ['0', '0.', '0.0']:
            # when annotationpro imports a PointTier, it assigns
            # start=0 and duration=0 to all points in the tier...
            # Here, we just ignore such annotations.
            return

        try:
            begin = float(b)
            duration = float(d)
        except ValueError:
            raise AioFormatError("Segment id="+segment_id)

        sample_rate = self.get_meta('media_sample_rate', '44100')
        if annotation_root.find(uri + 'Duration').text == "0":
            localization = sppasANTX.make_point(begin, sample_rate)
        else:
            localization = sppasInterval(
                sppasANTX.make_point(begin, sample_rate),
                sppasANTX.make_point(begin + duration, sample_rate))

        # fix labels
        text = annotation_root.find(uri + 'Label').text
        labels = format_labels(text)

        # create annotation
        ann = tier.create_annotation(sppasLocation(localization),
                                     labels)

        # fix other information in metadata
        self.elt_to_meta(
            annotation_root, ann, uri,
            ['IdLayer', 'Start', 'Duration', 'Label', 'IsSelected'])

        is_selected = annotation_root.find(uri + 'IsSelected')
        if is_selected is not None:
            ann.set_meta("IsSelected", is_selected.text)

    # ----------------------------------------------------------------------

    def elt_to_meta(self, root, meta_object, uri, exclude_list=[]):
        """Add nodes of root in meta_object."""
        for node in root:
            if node.text is not None:
                key = node.tag.replace(uri, '')
                if key not in exclude_list:
                    key = self._map_meta.get(key, key)
                    meta_object.set_meta(key, node.text)

                if 'Color' in key:
                    color = meta_object.get_meta(key)
                    r, g, b = color_to_rgb(int(color))
                    meta_object.set_meta(key,
                                         ",".join([str(r), str(g), str(b)]))

    # ----------------------------------------------------------------------
    # Writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write an Antx file.

        :param filename:

        """
        root = ET.Element('AnnotationSystemDataSet')
        root.set('xmlns', 'http://tempuri.org/AnnotationSystemDataSet.xsd')

        # we have to remove the hierarchy because instead we can't merge
        # overlapping annotations
        hierarchy_backup = self.get_hierarchy().copy()
        for tier in self:
            self.get_hierarchy().remove_tier(tier)

        # Write layers
        for tier in self:
            sppasANTX._format_tier(root, tier)

        # Write segments
        for tier in self:
            original_id = tier.get_meta('id')
            if tier.is_point():
                tier = point2interval(tier, 0.01)
            tier = merge_overlapping_annotations(tier)
            tier.set_meta('id', original_id)
            for ann in tier:
                self._format_segment(root, tier, ann)

        # Write media
        for media in self.get_media_list():
            if media:
                sppasANTX._format_media(root, media)

        # Write configurations
        self._format_configuration(root)

        sppasANTX.indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename,
                   encoding=sg.__encoding__,
                   xml_declaration=True,
                   method="xml")
        # we should add 'standalone="yes"' in the declaration
        # (but not available with ElementTree)

        # restore the hierarchy...
        self._hierarchy = hierarchy_backup

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_media(root, media):
        """Add 'AudioFile' into the ElementTree.

        :param root: (ElementTree)
        :param media: (sppasMedia)

        """
        media_root = ET.SubElement(root, 'AudioFile')

        # Write all the elements SPPAS has interpreted
        child_id = ET.SubElement(media_root, 'Id')
        child_id.text = media.get_meta('id')
        child_id = ET.SubElement(media_root, 'FileName')
        child_id.text = media.get_filename()

        # other ANTX required elements
        child = ET.SubElement(media_root, "Name")
        child.text = media.get_meta("Name", "NoName")

        child = ET.SubElement(media_root, "External")
        child.text = media.get_meta("External", "false")

        child = ET.SubElement(media_root, "Current")
        child.text = media.get_meta("Current", "false")

    # -----------------------------------------------------------------------

    def _format_configuration(self, root):
        """Add 'Configuration' into the ElementTree."""
        now = datetime.now().strftime("%Y-%M-%d %H:%M")

        # File format version
        sppasANTX._add_configuration(root, "Version", "5")

        # Author
        author = sg.__name__ + " " + sg.__version__ + " (C) " + sg.__author__
        sppasANTX._add_configuration(root, "Author", author)

        # FileVersion
        sppasANTX._add_configuration(root,
                                     self._map_meta["file_version"],
                                     self.get_meta("file_version",
                                                   "1"))

        # Samplerate
        sppasANTX._add_configuration(root,
                                     self._map_meta["media_sample_rate"],
                                     self.get_meta("media_sample_rate",
                                                   "44100"))

        # Created
        sppasANTX._add_configuration(root,
                                     self._map_meta["file_created_date"],
                                     self.get_meta("file_created_date",
                                                   now))

        # Modified
        sppasANTX._add_configuration(root,
                                     self._map_meta["file_write_date"],
                                     self.get_meta("file_write_date",
                                                   now))

    # -----------------------------------------------------------------------

    @staticmethod
    def _add_configuration(root, key, value):
        """Add a new 'Configuration' key/value element in root."""
        conf_root = ET.SubElement(root, 'Configuration')
        child_key = ET.SubElement(conf_root, 'Key')
        child_key.text = key
        child_value = ET.SubElement(conf_root, 'Value')
        child_value.text = value

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_tier(root, tier):
        """Add 'Layer' and its content into the ElementTree."""
        tier_root = ET.SubElement(root, 'Layer')

        # Write all the elements SPPAS has interpreted
        child_id = ET.SubElement(tier_root, 'Id')
        tier_id = tier.get_meta('id')
        child_id.text = tier_id

        child_name = ET.SubElement(tier_root, 'Name')
        child_name.text = tier.get_name()

        # Layer required elements:
        child = ET.SubElement(tier_root, 'ForeColor')
        col = tier.get_meta('ForeColor', '')
        if col == '':
            r, g, b = pick_random_color(0, 20)
        else:
            r, g, b = col.split(',')
        child.text = str(rgb_to_color(r, g, b))

        child = ET.SubElement(tier_root, 'BackColor')
        col = tier.get_meta('BackColor', '')
        if col == '':
            r, g, b = pick_random_color(20, 255)
        else:
            r, g, b = col.split(',')
        child.text = str(rgb_to_color(r, g, b))

        child = ET.SubElement(tier_root, 'IsSelected')
        child.text = tier.get_meta("tier_is_selected", "false")

        child = ET.SubElement(tier_root, 'Height')
        child.text = tier.get_meta("tier_height", "70")

        # Layer optional elements:
        child = ET.SubElement(tier_root, 'IsClosed')
        child.text = tier.get_meta("tier_is_closed", "false")

        # for each element key, assign either the stored value
        # (in the metadata), or the default one.
        elt_opt_layer = {'CoordinateControlStyle': "0",
                         'IsLocked': "false",
                         'ShowOnSpectrogram': "false",
                         'ShowAsChart': "false",
                         'ChartMinimum': "-50",
                         'ChartMaximum': "50",
                         'ShowBoundaries': "true",
                         'IncludeInFrequency': "true",
                         'Parameter1Name': "Parameter 1",
                         'Parameter2Name': "Parameter 2",
                         'Parameter3Name': "Parameter 3",
                         'IsVisible': "true",
                         'FontSize': "10"}

        for key in elt_opt_layer:
            child = ET.SubElement(tier_root, key)
            child.text = tier.get_meta(key, elt_opt_layer[key])

    # -----------------------------------------------------------------------

    def _format_segment(self, root, tier, ann):
        """Add 'Segment' into the ElementTree."""
        segment_root = ET.SubElement(root, 'Segment')
        is_point = tier.is_point()

        # Write all the elements SPPAS has interpreted
        child_id = ET.SubElement(segment_root, 'Id')            # Id
        child_id.text = ann.get_meta('id')

        child_id_layer = ET.SubElement(segment_root, 'IdLayer')  # IdLayer
        child_id_layer.text = tier.get_meta('id')

        child_id_label = ET.SubElement(segment_root, 'Label')    # Label
        child_id_label.text = ann.serialize_labels(separator="\n",
                                                   empty="",
                                                   alt=True)

        child_id_start = ET.SubElement(segment_root, 'Start')    # Start
        child_id_dur = ET.SubElement(segment_root, 'Duration')   # Duration
        if is_point:
            start = ann.get_location().get_lowest_localization()
            duration = 0
        else:
            start = ann.get_location().get_best().get_begin().get_midpoint()
            duration = ann.get_location().get_best().duration().get_value()
            duration *= float(self.get_meta('sample_rate', 44100))
            duration = max(int(duration), 1)

        start *= float(self.get_meta('sample_rate', 44100))
        child_id_start.text = str(int(start))
        child_id_dur.text = str(duration)

        # Segment required elements
        fore_r, fore_g, fore_b = tier.get_meta('ForeColor',
                                               '0,0,0').split(',')
        back_r, back_g, back_b = tier.get_meta('BackColor',
                                               '255,255,255').split(',')
        elt_segment = {'ForeColor': rgb_to_color(fore_r, fore_g, fore_b),
                       'BackColor': rgb_to_color(back_r, back_g, back_b),
                       'BorderColor': '-8355172',  # grey
                       'IsSelected': 'false'}

        for key in elt_segment:
            child = ET.SubElement(segment_root, key)
            if 'Color' not in key:
                child.text = ann.get_meta(key, elt_segment[key])
            else:
                child.text = str(elt_segment[key])

        # Segment optional elements

        elt_opt_segment = {'Feature': None, 'Group': None, 'Name': None,
                           'Parameter1': None, 'Parameter2': None,
                           'Parameter3': None, 'IsMarker': "false",
                           'Marker': None, 'RScript': None}

        # in SPPAS, the language can be defined at any level
        # (trs, tier, annotation).
        meta_key_language = self._map_meta['Language']
        elt_opt_segment['Language'] = tier.get_meta(
            meta_key_language,
            self.get_meta(meta_key_language, None))

        for key in elt_opt_segment:
            child = ET.SubElement(segment_root, key)
            meta_key = self._map_meta.get(key, key)
            child.text = ann.get_meta(meta_key, elt_opt_segment[key])

    # -----------------------------------------------------------------------

    @staticmethod
    def indent(elem, level=0):
        """Pretty indent of an ElementTree.

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
                sppasANTX.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

# ---------------------------------------------------------------------------


class sppasANT(sppasBaseIO):
    """AnnotationPro ANT reader and writer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    An ANT file is a ZIPPED directory.

    """

    @staticmethod
    def detect(filename):
        """Check whether a file is of ANT format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        if zipfile.is_zipfile(filename) is False:
            return False
        z = zipfile.ZipFile(filename, "r")
        return any(x.endswith("annotation.xml") for x in z.namelist())

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new sppasANT instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasANT, self).__init__(name)

        self.default_extension = "ant"
        self.software = "AnnotationPro"

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = False
        self._accept_media = True
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = False

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read an ANT file and fill the Transcription.

        :param filename: (str)

        """
        zf = zipfile.ZipFile(filename, 'r')
        unzip_dir = sppasFileUtils().set_random()
        zf.extractall(unzip_dir)
        zf.close()

        antx_filename = os.path.join(unzip_dir, "annotation.xml")
        antx = sppasANTX()
        antx.read(antx_filename)
        self.set(antx)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write an Ant file.

        :param filename: (str)

        """
        # Create a directory with the annotations in ANTX format
        os.mkdir(filename)
        antx = sppasANTX()
        antx.set(self)
        antx.write(os.path.join(filename, "annotation.xml"))

        # Create the zip archive "filename.zip" of the directory
        shutil.make_archive(filename, 'zip', filename)

        # Remove the directory
        shutil.rmtree(filename)

        # Rename the archive to the expected filename
        os.rename(filename+".zip", filename)
