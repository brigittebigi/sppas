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

    src.anndata.aio.elan.py
    ~~~~~~~~~~~~~~~~~~~~~~~


"""
import xml.etree.cElementTree as ET
from operator import itemgetter
from collections import OrderedDict
import logging

import sppas
from sppas.src.resources.mapping import sppasMapping
from sppas.src.utils.datatype import sppasTime

from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioNoTiersError
from ..anndataexc import AioEmptyTierError
from ..anndataexc import AioLocationTypeError
from ..anndataexc import AioFormatError
from ..anndataexc import AioLocationTypeError
from ..anndataexc import CtrlVocabSetTierError
from ..anndataexc import CtrlVocabContainsError
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag
from ..media import sppasMedia
from ..tier import sppasTier
from ..annotation import sppasAnnotation

from ..ctrlvocab import sppasCtrlVocab

from .basetrs import sppasBaseIO
from .aioutils import serialize_labels
from .aioutils import format_labels
from .aioutils import point2interval
from .aioutils import merge_overlapping_annotations

# ---------------------------------------------------------------------------

ETYPES = {'iso12620',
          'ecv',
          'cve_id',
          'lexen_id',
          'resource_url'}

CONSTRAINTS = {
    'Time_Subdivision': "Time subdivision of parent annotation's time inte"
    'rval, no time gaps allowed within this interval',
    'Symbolic_Subdivision': 'Symbolic subdivision of a parent annotation. '
    'Annotations refering to the same parent are ordered',
    'Symbolic_Association': '1-1 association with a parent annotation',
    'Included_In': 'Time alignable annotations within the parent annotatio'
    "n's time interval, gaps are allowed"}

MIMES = {'wav': 'audio/x-wav',
         'mpg': 'video/mpeg',
         'mpeg': 'video/mpg',
         'xml': 'text/xml'}

# ---------------------------------------------------------------------------


class sppasEAF(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS ELAN EAF files reader and writer.

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of XRA format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with open(filename, 'r') as fp:
                for i in range(10):
                    line = fp.readline()
                    if "<ANNOTATION_DOCUMENT" in line:
                        return True
                fp.close()
        except IOError:
            return False

        return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasMLF instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__

        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = True
        self._accept_media = True
        self._accept_hierarchy = True
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = False  # to be verified

        self.default_extension = "eaf"

        # Information that are both used by ELAN and another software tool
        self._map_meta = sppasMapping()
        self._map_meta.add('PARTICIPANT', 'speaker_name')
        self._map_meta.add('ANNOTATOR', 'annotator_name')

        # ELAN only supports (and assumes) milliseconds.
        self.unit = 0.001

    # -----------------------------------------------------------------------

    def make_point(self, midpoint):
        """ Convert data into the appropriate sppasPoint().

        :param midpoint: (str) a time in ELAN format
        :returns: (sppasPoint) Representation of time in seconds with a (very)
        large vagueness!

        """
        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint * self.unit, radius=0.02)

    # -----------------------------------------------------------------------

    def format_point(self, second_count):
        """ Convert a time in seconds into ELAN format.

        :param second_count: (float) Time value (in seconds)
        :returns: (int) a time in ELAN format

        """
        try:
            second_count = float(second_count)
        except ValueError:
            raise AnnDataTypeError(second_count, "float")

        return int((1./self.unit) * float(second_count))

    # -----------------------------------------------------------------------
    # reader
    # -----------------------------------------------------------------------

    def read(self, filename):
        """ Read a ELAN EAF file.

        :param filename: (str) input filename.

        """
        tree = ET.parse(filename)
        root = tree.getroot()

        # 1. Document
        self._parse_document(root)

        # 2. License (0..*)
        for i, license_root in enumerate(root.findall('LICENSE')):
            self._parse_license(license_root, i)

        # 3. Header (1..1)
        header_root = root.find('HEADER')
        if header_root is None:
            raise AioFormatError('HEADER')
        self._parse_header(root.find('HEADER'))

        # 4. Time order (1..1)
        time_order_root = root.find('TIME_ORDER')
        if time_order_root is None:
            raise AioFormatError('TIME_ORDER')
        time_slots = sppasEAF._parse_time_order(time_order_root)

        # 5. Controlled vocabularies (0..*)
        for vocabulary_root in root.findall('CONTROLLED_VOCABULARY'):
            ctrl_vocab = sppasEAF._parse_ctrl_vocab(vocabulary_root)
            if len(ctrl_vocab) > 0:
                self.add_ctrl_vocab(ctrl_vocab)

        # 6. Tiers (0..*)
        self._parse_tiers(root, time_slots)

        # 7. Linguistic type
        for linguistic_root in root.findall('LINGUISTIC_TYPE'):
            self._parse_linguistic_type(linguistic_root)

        # 8. Locale (0..*)
        for i, locale_root in enumerate(root.findall('LOCALE')):
            self._parse_locale(locale_root, i)

        # 9. Language
        for i, language_root in enumerate(root.findall('LANGUAGE')):
            self._parse_language(language_root, i)

        # 10. Constraint

        # 11. Lexicon ref

        # 12. External ref

    # -----------------------------------------------------------------------

    def _parse_document(self, document_root):
        """ Get the main element root.

        :param document_root: (ET) Main root.

        """
        if "DATE" in document_root.attrib:
            self.set_meta('file_created_date', document_root.attrib['DATE'])

        if "VERSION" in document_root.attrib:
            self.set_meta('file_format_version', document_root.attrib['VERSION'])

        if "AUTHOR" in document_root.attrib:
            self.set_meta('file_author', document_root.attrib['AUTHOR'])

    # -----------------------------------------------------------------------

    def _parse_license(self, license_root, idx=0):
        """ Get an element 'LICENSE'.
        The current version of ELAN does not yet provide a means to edit
        or view the contents of the license.

        :param license_root: (ET) License root.
        :param idx: (int) Index of the license

        """
        self.set_meta('file_license_%s' % idx, license_root.text)

        if "LICENSE_URL" in license_root.attrib:
            self.set_meta('file_license_%s_url' % idx, license_root.attrib['LICENSE_URL'])
        else:
            self.set_meta('file_license_%s_url' % idx, "")

    # -----------------------------------------------------------------------

    def _parse_header(self, header_root):
        """ Get the element 'HEADER'.
        There should be exactly one HEADER element. It can contain sequences
        of three elements and has two attributes.

        :param header_root: (ET) Header root.

        """
        # Fix the time unit
        unit_string = header_root.attrib['TIME_UNITS']
        if unit_string == 'seconds':
            # it should never happen if the EAF file was generated with Elan software
            self.unit = 1.0

        for media_root in header_root.findall('MEDIA_DESCRIPTOR'):
            media = sppasEAF._parse_media_descriptor(media_root, header_root)
            self.add_media(media)

        for linked_root in header_root.findall('LINKED_FILE_DESCRIPTOR'):
            media = sppasEAF._parse_linked_file_descriptor(linked_root, header_root)
            self.add_media(media)

        for property_root in header_root.findall('PROPERTY'):
            self._parse_property(property_root)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_media_descriptor(media_root, header_root):
        """ Get the elements 'MEDIA_DESCRIPTOR'.
        This element describes one primary media source.
        Create a sppasMedia instance and add it.

        :param media_root: (ET) Media root element.

        """
        media_url = media_root.attrib['MEDIA_URL']
        media_mime = media_root.attrib['MIME_TYPE']

        # Create the new Media and put all information in metadata
        media = sppasMedia(media_url, mime_type=media_mime)
        media.set_meta('media_source', 'primary')
        for attrib in ['RELATIVE_MEDIA_URL', 'TIME_ORIGIN', 'EXTRACTED_FROM']:
            if attrib in media_root.attrib:
                media.set_meta(attrib, media_root.attrib[attrib])

        # media identifier
        for property_root in header_root.findall('PROPERTY'):
            if 'NAME' in property_root.attrib:
                name = property_root.attrib['NAME']
                if name == 'media_id_'+media.get_filename():
                    media.set_meta('id', property_root.text)

        return media

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_linked_file_descriptor(linked_root, header_root):
        """ Get the elements 'LINKED_FILE_DESCRIPTOR'.
        This element describes a “secondary”, additional source.
        Create a sppasMedia instance and add it.

        :param linked_root: (ET) Linked file descriptor root element.

        """
        media_url = linked_root.attrib['LINK_URL']
        media_mime = linked_root.attrib['MIME_TYPE']

        # Create the new Media and put all information in metadata
        media = sppasMedia(media_url, mime_type=media_mime)
        media.set_meta('media_source', 'secondary')
        for attrib in ['RELATIVE_LINK_URL', 'TIME_ORIGIN', 'ASSOCIATED_WITH']:
            if attrib in linked_root.attrib:
                media.set_meta(attrib, linked_root.attrib[attrib])

        # media identifier
        for property_root in header_root.findall('PROPERTY'):
            if 'NAME' in property_root.attrib:
                name = property_root.attrib['NAME']
                if name == 'media_id_'+media.get_filename():
                    media.set_meta('id', property_root.text)

        return media

    # -----------------------------------------------------------------------

    def _parse_property(self, property_root):
        """ Get the elements 'PROPERTY' -> sppasMetadata().
        This is a general purpose element for storing key-value pairs.

        This method store all metadata except the identifiers (media, tier...).

        :param property_root: (ET) Property root element.

        """
        if 'NAME' in property_root.attrib:
            name = property_root.attrib['NAME']
            if "_id_" not in name:
                self.set_meta(name, property_root.text)

    # -----------------------------------------------------------------------

    def _parse_locale(self, locale_root, idx=0):
        """ Get an element 'LOCALE'.

        :param locale_root: (ET) Locale root.
        :param idx: (int) Index of the locale

        """
        self.set_meta('locale_%s' % idx, locale_root.attrib['LANGUAGE_CODE'])

        if "COUNTRY_CODE" in locale_root.attrib:
            self.set_meta('locale_%s_country' % idx, locale_root.attrib['COUNTRY_CODE'])
        if "VARIANT" in locale_root.attrib:
            self.set_meta('locale_%s_variant' % idx, locale_root.attrib['VARIANT'])

    # -----------------------------------------------------------------------

    def _parse_language(self, language_root, idx=0):
        """ Get an element 'LANGUAGE'.

        Extracted information are:
            - language iso639-3 code,
            - language name,
            - language url, except if cdb.iso.org which is wrong (changed to the SIL one).

        :param language_root: (ET) Language element.
        :param idx: (int) Index of the language

        """
        iso = language_root.attrib['LANG_ID']
        self.set_meta('language_iso_%s' % idx, iso)

        if "LANG_LABEL" in language_root.attrib:
            self.set_meta('language_name_%s' % idx, language_root.attrib['LANG_LABEL'])

        url = 'http://iso639-3.sil.org/code/'+iso
        if "LANG_DEF" in language_root.attrib:
            url = language_root.attrib['LANG_DEF']
            if 'cdb.iso.org' in url:
                url = 'http://iso639-3.sil.org/code/'+iso
        self.set_meta('language_url_%s' % idx, url)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_time_order(time_order_root):
        """ Get the elements 'TIME_ORDER'.
        The TIME_ORDER element is a container for ordered TIME_SLOT elements.

        :param time_order_root: (ET) Time order root element.

        """
        time_slots = dict()

        # parse each of the <TIME_SLOT> elements
        for time_slot_node in time_order_root.findall('TIME_SLOT'):
            time_id = time_slot_node.attrib['TIME_SLOT_ID']

            # time slots without time values are ignored.
            if 'TIME_VALUE' in time_slot_node.attrib:
                value = time_slot_node.attrib['TIME_VALUE']
                time_slots[time_id] = value

        return time_slots

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_ctrl_vocab(ctrl_vocab_root):
        """ Get the elements 'CONTROLLED_VOCABULARY' -> sppasCtrlVocab().

        In version 2.8, the locale is ignored.

        :param ctrl_vocab_root: (ET) Controlled vocabulary root element.

        """
        # Create a sppasCtrlVocab instance
        vocab_id = ctrl_vocab_root.attrib['CV_ID']
        ctrl_vocab = sppasCtrlVocab(vocab_id)

        # Description
        if "DESCRIPTION" in ctrl_vocab_root.attrib:
            ctrl_vocab.set_description(ctrl_vocab_root.attrib['DESCRIPTION'])

        # Add the list of entries
        # if Elan eaf format < 2.8
        for entry_node in ctrl_vocab_root.findall('CV_ENTRY'):
            entry_text = entry_node.text
            entry_desc = ""
            if "DESCRIPTION" in entry_node.attrib:
                entry_desc = entry_node.attrib['DESCRIPTION']
            ctrl_vocab.add(sppasTag(entry_text), entry_desc)

        # if Elan eaf format = 2.8
        for entry_node in ctrl_vocab_root.findall('CV_ENTRY_ML'):
            entry_value_node = entry_node.find('CVE_VALUE')
            entry_text = entry_value_node.text
            entry_desc = ""
            if "DESCRIPTION" in entry_value_node.attrib:
                entry_desc = entry_value_node.attrib['DESCRIPTION']
            ctrl_vocab.add(sppasTag(entry_text), entry_desc)
        # mutually exclusive with a sequence of CV_ENTRY_ML elements:
        if 'EXT_REF' in ctrl_vocab_root.attrib:
            ctrl_vocab_url = ctrl_vocab_root.attrib['EXT_REF']
            ctrl_vocab.set_meta('EXT_REF', ctrl_vocab_url)
            # todo: open and parse the ctrl vocab external file.

        return ctrl_vocab

    # -----------------------------------------------------------------

    def _parse_linguistic_type(self, linguistic_root):
        """ Get the elements 'LINGUISTIC_TYPE'.

        This is a collection of attributes and constraints for TIER objects.

        :param linguistic_root: (ET) Tier root.

        """
        linguistic_type = linguistic_root.attrib['LINGUISTIC_TYPE_ID']

        # which tier is using this linguistic type?
        found = False
        for tier in self:
            if linguistic_type == tier.get_meta('LINGUISTIC_TYPE_REF'):

                # Add linguistic type info in the metadata of the tier
                for key in ['CONSTRAINTS', 'GRAPHIC_REFERENCES', 'TIME_ALIGNABLE']:
                    if key in linguistic_root.attrib:
                        tier.set_meta(key, linguistic_root.attrib[key])

                # Associate tier with a controlled vocabulary
                if 'CONTROLLED_VOCABULARY_REF' in linguistic_root.attrib:
                    ctrl_vocab_name = linguistic_root.attrib['CONTROLLED_VOCABULARY_REF']
                    ctrl_vocab = self.get_ctrl_vocab_from_name(ctrl_vocab_name)
                    if ctrl_vocab is not None:
                        try:
                            tier.set_ctrl_vocab(ctrl_vocab)
                        except CtrlVocabContainsError:
                            # There's a bug in Elan: accepts non-controlled text in controlled tier
                            tier.set_meta("controlled_vocabulary", ctrl_vocab.get_meta('id'))
                            logging.info(str(CtrlVocabSetTierError(ctrl_vocab.get_name(), tier.get_name())))
                        # todo: CtrlVocab <-> Tier must deal with the locale...
                found = True

        # what to do with an unused linguistic type?
        if not found:
            pass

    # -----------------------------------------------------------------------

    def _parse_tiers(self, root, time_slots):
        """ Get all the elements 'TIER' -> sppasTier().

        :param root: (ET) Document root.
        :param time_slots: (dict)

        """
        # list of alignable annotations that are not saved in SPPAS because
        # they don't have a localization. Their label is added to the closest
        # time-aligned annotations.
        removed_annotations = dict()

        # We first parse only alignable tiers
        for tier_root in root.findall('TIER'):
            if sppasEAF.__is_alignable_tier(tier_root) is True:
                self._parse_tier(tier_root, time_slots, removed_annotations)

        # We then parse ref tiers
        for tier_root in root.findall('TIER'):
            if sppasEAF.__is_alignable_tier(tier_root) is False:
                self._parse_tier(tier_root, time_slots, removed_annotations)

        # We have to re-organize tiers: we restore the original rank of each tier
        for i, tier_root in enumerate(root.findall('TIER')):
            tier_name = tier_root.attrib['TIER_ID']
            self.set_tier_index(tier_name, i)

    # -----------------------------------------------------------------------

    @staticmethod
    def __is_alignable_tier(tier_root):
        if 'PARENT_REF' in tier_root.attrib:
            for annotation_root in tier_root.findall('ANNOTATION'):
                if annotation_root.find('REF_ANNOTATION') is not None:
                    return False
        return True

    # -----------------------------------------------------------------------

    def _parse_tier(self, tier_root, time_slots, removed_annotations=dict()):
        """ Get the element 'TIER' -> sppasTier().

        :param tier_root: (ET) Tier root.
        :param time_slots: (dict)

        """
        # The name is used as identifier.
        tier = self.create_tier(tier_root.attrib['TIER_ID'])

        # meta information (required or optional)
        self._map_meta.set_reverse(False)
        for key in ['LINGUISTIC_TYPE_REF', 'DEFAULT_LOCALE', 'PARTICIPANT', 'ANNOTATOR', 'LANG_REF']:
            if key in tier_root.attrib:
                tier.set_meta(self._map_meta.map_entry(key), tier_root.attrib[key])

        # get annotations
        if sppasEAF.__is_alignable_tier(tier_root):
            self._parse_alignable_tier(tier_root, tier, time_slots, removed_annotations)
        else:
            self._parse_ref_tier(tier_root, tier, removed_annotations)

    # -----------------------------------------------------------------------

    def _parse_alignable_tier(self, tier_root, tier, time_slots, removed_annotations=dict()):
        """ Get the elements 'TIER' -> sppasTier().

        :param tier_root: (ET) Tier root.
        :param tier: (sppasTier) The tier to add the annotation
        :param time_slots: (dict)
        :param removed_annotations: (dict) Alignable annotations without time values.

        """
        # Some time slots don't have a time value, so some annotations do not
        # starts/ends at a given localization.
        # From the SPPAS opinion, it's not an annotation...
        begin_time = None
        end_time = None
        text = list()
        removed = list()

        for annotation_root in tier_root.findall('ANNOTATION'):

            # In an alignable tier, we expect only alignable annotations
            align_ann_root = sppasEAF.__get_ann_root(annotation_root, tier, 'ALIGNABLE_ANNOTATION')

            # The (only) 'annotation value' in ELan is a text of a tag of a 'label' in SPPAS.
            # Store in a list of labels.
            value_node = align_ann_root.find('ANNOTATION_VALUE')
            if value_node.text is not None:
                text.append(value_node.text)

            # Localization
            if begin_time is None:
                begin_key = align_ann_root.attrib['TIME_SLOT_REF1']
                begin_time = time_slots.get(begin_key, None)
            if end_time is None:
                end_key = align_ann_root.attrib['TIME_SLOT_REF2']
                end_time = time_slots.get(end_key, None)

            # If the annotation has a localization, we can create it.
            if begin_time is not None and end_time is not None:
                ann = self.__add_ann_in_tier(begin_time, end_time, text, tier)
                if len(removed) > 0:
                    # the first removed annotation is the one we use to store metadata
                    sppasEAF.__add_meta_in_ann(removed[0], ann)
                    removed.pop(0)
                    removed.append(align_ann_root)
                else:
                    sppasEAF.__add_meta_in_ann(align_ann_root, ann)

                # update
                for a in removed:
                    ann_id = a.attrib['ANNOTATION_ID']
                    removed_annotations[ann_id] = ann.get_meta('id')

                # prepare for the next annotation
                begin_time = None
                end_time = None
                text = list()
                removed = list()

            else:
                removed.append(align_ann_root)
                logging.info('No time value for the annotation {:s} in an alignable tier {:s}'
                             ''.format(align_ann_root.attrib['ANNOTATION_ID'], tier.get_name()))

    # -----------------------------------------------------------------

    @staticmethod
    def __get_ann_root(annotation_root, tier, element):
        align_ann_root = annotation_root.find(element)
        if align_ann_root is None:
            raise AioFormatError('TIER: {:s}: ANNOTATION:{:s}'
                                 ''.format(tier.get_name(), element))
        return align_ann_root

    # -----------------------------------------------------------------

    def __add_ann_in_tier(self, begin_time, end_time, text_list, tier):
        localization = sppasInterval(self.make_point(begin_time),
                                     self.make_point(end_time))
        labels = format_labels("\n".join(text_list), separator="\n")
        ann = tier.create_annotation(sppasLocation(localization), labels)
        return ann

    # -----------------------------------------------------------------------

    @staticmethod
    def __add_meta_in_ann(ann_root, ann):
        ann.set_meta('id', ann_root.attrib['ANNOTATION_ID'])
        for attrib in ['SVG_REF', 'EXT_REF', 'LANG_REF', 'CVE_REF']:
            if attrib in ann_root.attrib:
                ann.set_meta(attrib, ann_root.attrib[attrib])

    # -----------------------------------------------------------------------

    def _parse_ref_tier(self, tier_root, tier, removed_annotations=dict()):
        """ Get the elements 'TIER'.

        :param tier_root: (ET) Tier root element.
        :param tier: (sppasTier) The tier to add the annotations

        """
        # we expect that the parent tier has already been included in self
        parent_tier_ref = tier_root.attrib['PARENT_REF']
        parent_tier = self.find(parent_tier_ref)
        if parent_tier is None:
            raise AioFormatError('tier:{:s} parent:{:s}'.format(tier.get_name(), parent_tier_ref))

        # while we have the aligned parent, we can fill the child tier
        for i, annotation_root in enumerate(tier_root.findall('ANNOTATION')):

            ref_ann_root = sppasEAF.__get_ann_root(annotation_root, tier, 'REF_ANNOTATION')
            ann_ref_id = ref_ann_root.attrib['ANNOTATION_REF']

            ann_ref = parent_tier.get_annotation(removed_annotations.get(ann_ref_id, ann_ref_id))
            if ann_ref is None:
                raise AioFormatError('tier:{:s} annotation:{:s}'.format(tier.get_name(), ann_ref_id))
            label = sppasLabel(sppasTag(ref_ann_root.find('ANNOTATION_VALUE').text))

            if ann_ref_id in removed_annotations:
                # we append the label like it's done into the reference, instead of
                # creating a new annotation. We suppose that the annotation to be
                # appended is the last alignable annotation that we previously saved
                # (because annotations are time-sorted)... is it a strong hypothesis?
                # to be verified.
                tier[-1].append_label(label)
                logging.info('Label {:s} appended to annotation {:s}.'
                             ''.format(label.get_best().get_content(), tier[-1].get_meta('id')))
            else:
                location = ann_ref.get_location().copy()
                new_ann = sppasAnnotation(location, label)
                tier.append(new_ann)
                sppasEAF.__add_meta_in_ann(ref_ann_root, new_ann)

    # -----------------------------------------------------------------------
    # writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """ Write an ELAN EAF file.

        :param filename: output filename.

        """
        # 1. Document
        root = sppasEAF._format_document()
        self.unit = 0.001

        # 2. License
        self._format_license(root)

        # 3. Header: media, linked media, property
        self._format_header(root)

        # 4. Time Order
        time_slots = self.__build_time_slots()
        time_order_root = ET.SubElement(root, 'TIME_ORDER')
        #self._format_time_slots(time_order_root, time_slots)

        # 5. Tier
        # Create the root of each tier
        self._format_tier_root(root)
        # Fill alignable tiers with their annotations
        self._format_alignable_tiers(root)
        # Fill reference tiers with their annotations
        #self._format_reference_tiers(root)

        # 6. Linguistic Type

        # 7. Locale
        self._format_locales(root)

        # 8. Language
        self._format_languages(root)

        # 9. Constraint

        # 10. Controlled vocabulary
        for ctrl_vocab in self.get_ctrl_vocab_list():
            sppasEAF._format_ctrl_vocab(root, ctrl_vocab)

        # 11. Lexicon ref

        # 12. External ref

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_document():
        """ Create a root element tree for EAF format. """

        root = ET.Element('ANNOTATION_DOCUMENT')
        author = sppas.__name__ + " " + sppas.__version__ + " (C) " + sppas.__author__

        root.set('AUTHOR', author)
        root.set('DATE', sppasTime().now)
        root.set('FORMAT', '2.8')
        root.set('VERSION', '2.8')
        root.set('xmlns:xsi',
                 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:noNamespaceSchemaLocation',
                 'http://www.mpi.nl.tools/elan/EAFv2.8.xsd')

        return root

    # -----------------------------------------------------------------------

    def _format_license(self, root):
        """ Add an element 'LICENSE' into the ElementTree (if any).

        :param root: (ElementTree)
        :returns: (ET) License root.

        """
        # we have to restore the licenses in their original order.
        licenses = dict()
        for key in self.get_meta_keys():
            if 'file_license_' in key:
                if 'url' not in key:
                    url = ""
                    for url_key in self.get_meta_keys():
                        if url_key == key+"_url":
                            url = self.get_meta(url_key)
                    licenses[key] = (self.get_meta(key), url)

        for key in sorted(licenses):
                license_root = ET.SubElement(root, "LICENSE")
                license_root.text = licenses[key][0]
                license_root.set('LICENSE_URL', licenses[key][1])

    # -----------------------------------------------------------------------

    def _format_languages(self, root):
        """ Add the elements 'LANGUAGE' into the ElementTree (if any).

        :param root: (ElementTree)
        :returns: (ET) License root.

        """
        # we have to restore the languages in their original order.
        languages = dict()
        for key in self.get_meta_keys():
            if key.startswith('language_') and key.endswith('_iso'):
                name = None
                url = None
                for key2 in self.get_meta_keys():
                    if key2 == key.replace('iso', 'url'):
                        url = self.get_meta(key2)
                    if key2 == key.replace('iso', 'name'):
                        name = self.get_meta(key2)
                languages[key] = (self.get_meta(key), name, url)

        for key in sorted(languages):
            language_root = ET.SubElement(root, "LANGUAGE")
            language_root.set('LANG_ID', languages[key][0])
            if languages[key][1] is not None:
                language_root.set('LANG_LABEL', languages[key][1])
            if languages[key][2] is not None:
                language_root.set('LANG_DEF', languages[key][2])

    # -----------------------------------------------------------------------

    def _format_header(self, root):
        """ Add 'HEADER' into the ElementTree. """

        header_root = ET.SubElement(root, 'HEADER')
        header_root.set('TIME_UNITS', 'milliseconds')

        for media in self.get_media_list():
            self._format_media(header_root, media)

        for media in self.get_media_list():
            self._format_linked_media(header_root, media)

        sppasEAF._format_property(header_root, self)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_media(root, media):
        """ Add 'MEDIA_DESCRIPTOR' into the ElementTree (if any).

        :param root: (ElementTree)
        :param media: (sppasMedia)

        """
        # do not add the media if it's not a primary one
        if media.is_meta_key('media_source'):
            if media.get_meta('media_source') != 'primary':
                return

        media_root = ET.SubElement(root, 'MEDIA_DESCRIPTOR')

        # Write all the elements SPPAS has interpreted (required by EAF)
        media_root.set('MEDIA_URL', media.get_filename())
        media_root.set('MIME_TYPE', media.get_mime_type())

        # other EAF optional elements
        for key in ['RELATIVE_MEDIA_URL', 'TIME_ORIGIN', 'EXTRACTED_FROM']:
            if media.is_meta_key(key):
                media_root.set(key, media.get_meta(key))

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_linked_media(root, media):
        """ Add 'LINKED_FILE_DESCRIPTOR' into the ElementTree (if any).

        :param root: (ElementTree)
        :param media: (sppasMedia)

        """
        # do not add the media if it's a primary one
        if media.is_meta_key('media_source'):
            if media.get_meta('media_source') == 'primary':
                return

        media_root = ET.SubElement(root, 'LINKED_FILE_DESCRIPTOR')

        # Write all the elements SPPAS has interpreted (required by EAF)
        media_root.set('LINK_URL', media.get_filename())
        media_root.set('MIME_TYPE', media.get_mime_type())

        # other EAF optional elements
        for key in ['RELATIVE_LINK_URL', 'TIME_ORIGIN', 'ASSOCIATED_WITH']:
            if media.is_meta_key(key):
                media_root.set(key, media.get_meta(key))

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_property(header_root, meta_object):
        """ Add 'PROPERTY' elements into the ElementTree (if any).

        :param root: (ElementTree)

        """
        for key in meta_object.get_meta_keys():
            if key == 'id':
                if isinstance(meta_object, sppasMedia):
                    sppasEAF.__add_property(header_root,
                                            "media_id_"+meta_object.get_filename(),
                                            meta_object.get_meta('id'))
                elif isinstance(meta_object, sppasTier):
                    sppasEAF.__add_property(header_root,
                                            "tier_id_" + meta_object.get_name(),
                                            meta_object.get_meta('id'))
                # we can't preserve the 'id' of other objects
            else:
                sppasEAF.__add_property(header_root, key, meta_object.get_meta(key))

    # -----------------------------------------------------------------------

    @staticmethod
    def __add_property(header_root, name, text):
        property_root = ET.SubElement(header_root, 'PROPERTY')
        property_root.set('NAME', name)
        property_root.text = text

    # -----------------------------------------------------------------------

    def _format_locales(self, root):
        """ Add the elements 'LOCALE' into the ElementTree (if any).

        :param root: (ElementTree)

        """
        # we have to restore the locales in their original order.
        locales = dict()
        for key in self.get_meta_keys():
            if 'locale_' in key:
                if 'country' not in key and 'variant' not in key:
                    country = None
                    variant = None
                    for key2 in self.get_meta_keys():
                        if key2 == key+"_country":
                            country = self.get_meta(key2)
                        if key2 == key+"_variant":
                            variant = self.get_meta(key2)
                    locales[key] = (self.get_meta(key), country, variant)

        for key in sorted(locales):
            locale_root = ET.SubElement(root, "LOCALE")
            locale_root.set('LANGUAGE_CODE', locales[key][0])
            if locales[key][1] is not None:
                locale_root.set('COUNTRY_CODE', locales[key][1])
            if locales[key][2] is not None:
                locale_root.set('VARIANT', locales[key][2])

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_ctrl_vocab(root, ctrl_vocab):
        """ Add 'CONTROLLED_VOCABULARY' elements into the ElementTree (if any).

        :param root: (ElementTree)

        """
        ctrl_root = ET.SubElement(root, 'CONTROLLED_VOCABULARY')
        ctrl_root.set('CV_ID', ctrl_vocab.get_name())
        description = ctrl_vocab.get_description()
        if len(description) > 0:
            ctrl_root.set('DESCRIPTION', description)
        if ctrl_vocab.is_meta_key('EXT_REF'):
            ctrl_root.set('EXT_REF', ctrl_vocab.get_meta('EXT_REF'))

        for tag in ctrl_vocab:
            entry_root = ET.SubElement(ctrl_root, 'CV_ENTRY_ML')
            entry_value_root = ET.SubElement(entry_root, 'CVE_VALUE')
            entry_value_root.text = tag.get_content()
            entry_descr_root = ET.SubElement(entry_root, 'DESCRIPTION')
            entry_descr_root.text = ctrl_vocab.get_tag_description(tag)

    # -----------------------------------------------------------------------

    def _format_tier_root(self, root):
        """ Create the root of each tier. Do not fill at all.
        It allows to preserve the rank of each tier in the tree and to fill
        all-in-one alignable-tiers then ref-tiers.

        """
        if self.is_empty():
            return

        for tier in self:
            if tier.is_disjoint() is False:
                tier_root = ET.SubElement(root, 'TIER')
                tier_root.set('TIER_ID', tier.get_name())

    # -----------------------------------------------------------------------

    def _format_alignable_tiers(self, root):
        """ Add the elements 'TIER' into the ElementTree (if any).
        Only for alignable tiers.

        :param root: (ElementTree)
        :returns: (dict) Time slots

        """
        # no tier, nothing to do!
        if self.is_empty():
            return

        min_time_point = self.get_min_loc()
        max_time_point = self.get_max_loc()
        if min_time_point is None or max_time_point is None:
            # only empty tiers in the transcription: nothing to add in the tree
            return

        alignable_tiers = list()

        for tier in self:
            # if it's not an alignable tier, go to the next...

            if tier.is_disjoint() is True:
                continue

            if tier.is_interval() is True:
                new_tier = merge_overlapping_annotations(tier)
            else:
                new_tier = point2interval(tier, 0.02)
            new_tier.set_meta('id', tier.get_meta('id'))
            alignable_tiers.append(new_tier)

        # create the annotation
        time_values = list()
        for tier in alignable_tiers:
            for tier_root in root.findall('TIER'):
                if tier_root.attrib['TIER_ID'] == tier.get_name():
                    sppasEAF._format_alignable_annotations(tier_root, tier, time_values)

        # assign time slots to annotations
        time_slots = sppasEAF._fix_time_slots(time_values)

        # then, we can assign the time slots to annotations, instead of time values
        for tier in alignable_tiers:
            for tier_root in root.findall('TIER'):
                if tier_root.attrib['TIER_ID'] == tier.get_name():
                    sppasEAF._re_format_alignable_annotations(tier_root, tier, time_slots)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_alignable_annotations(tier_root, tier, time_values):
        """ Add the elements 'ANNOTATION' into the ElementTree (if any).
        Only for alignable tiers.

        Attention: we assign time values instead of time slots. An annotation
        without time value has 'none' instead.

        :param root: (ElementTree)
        :param tier: (sppasTier)
        :param time_values: (list) The list of time values of the tiers. Will be completed.

        """
        for ann in tier:

            # create an ANNOTATION for each label.
            # specific time slots will have to be generated for un-aligned annotations.
            created_anns = sppasEAF._create_alignable_annotation_element(ann, tier_root)

            # we save only once a couple (time_value, tier).
            # it allows to link consecutive annotations like it's done in Elan.
            for align_ann_root in created_anns:
                b = align_ann_root.attrib['TIME_SLOT_REF1']
                e = align_ann_root.attrib['TIME_SLOT_REF2']
                if (b, tier) not in time_values:
                    time_values.append((b, tier))
                if (e, tier) not in time_values:
                    time_values.append((e, tier))

    # -----------------------------------------------------------------------

    @staticmethod
    def _create_alignable_annotation_element(ann, tier_root):
        """ Create ANNOTATION in ElementTree.
        Returns the list of created nodes of 'ALIGNABLE_ANNOTATION'.

        """
        begin = round(ann.get_lowest_localization().get_midpoint(), 4)
        end = round(ann.get_highest_localization().get_midpoint(), 4)

        # a label (and only one) is required in an annotation
        labels = ann.get_labels()
        if len(labels) == 0:
            labels = [sppasLabel(sppasTag(""))]

        created_anns = list()

        for j, label in enumerate(labels):

            ann_root = ET.SubElement(tier_root, "ANNOTATION")
            align_ann_root = ET.SubElement(ann_root, 'ALIGNABLE_ANNOTATION')
            align_ann_root.text = label.get_best().get_content()

            align_ann_root.set('TIME_SLOT_REF1', '%s_none_%s' % (begin, j))
            align_ann_root.set('TIME_SLOT_REF2', '%s_none_%s' % (begin, j + 1))
            if j > 0:
                align_ann_root.set('ANNOTATION_ID', ann.get_meta('id') + "_" + str(j+1))
            else:
                align_ann_root.set('ANNOTATION_ID', ann.get_meta('id'))
            for attrib in ['SVG_REF', 'EXT_REF', 'LANG_REF', 'CVE_REF']:
                if ann.is_meta_key(attrib):
                    align_ann_root.set(attrib, ann.get_meta(attrib))

            created_anns.append(align_ann_root)

        # Fix begin/end to the first/last created alignable annotations
        created_anns[0].set('TIME_SLOT_REF1', str(begin))
        created_anns[-1].set('TIME_SLOT_REF2', str(end))

        return created_anns

    # -----------------------------------------------------------------------

    @staticmethod
    def _re_format_alignable_annotations(tier_root, tier, time_slots):
        """ Replace time values instead of time slots in 'ANNOTATION' elements.

        :param root: (ElementTree)
        :param tier: (sppasTier)
        :param time_slots: (dict) The link between time values/tier and time slots.

        """
        for ann_root in tier_root.findall('ANNOTATION'):
            align_ann_root = ann_root.find('ALIGNABLE_ANNOTATION')

            # get the time values we previously assigned.
            begin = align_ann_root.attrib["TIME_SLOT_REF1"]
            end = align_ann_root.attrib["TIME_SLOT_REF2"]

            # replace by the time slot in the tree
            ts_begin = time_slots[(begin, tier)]
            ts_end = time_slots[(end, tier)]
            align_ann_root.set('TIME_SLOT_REF1', ts_begin)
            align_ann_root.set('TIME_SLOT_REF2', ts_end)

    # -----------------------------------------------------------------------
    # PRIVATE
    # -----------------------------------------------------------------

    @staticmethod
    def _fix_time_slots(time_values):

        # sort by time values and assign the 'ts<num>' id
        time_slots = OrderedDict()
        i = 0
        for key in sorted(time_values, key=itemgetter(0)):
            i += 1
            ts = 'ts%s' % i
            time_slots[key] = ts

        return time_slots