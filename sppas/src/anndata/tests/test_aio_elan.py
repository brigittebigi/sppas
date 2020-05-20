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

    src.anndata.tests.test_aio_elan.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the reader/writer of ELAN files.

"""
import unittest
import os.path
import xml.etree.cElementTree as ET

from sppas.src.config import sg
from sppas.src.utils.datatype import sppasTime

from ..aio.elan import sppasEAF
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasInterval
from ..ann.annlocation import sppasPoint
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag
from ..tier import sppasTier
from ..ann.annotation import sppasAnnotation
from ..media import sppasMedia
from ..ctrlvocab import sppasCtrlVocab
from ..aio.aioutils import format_labels

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestEAF(unittest.TestCase):
    """
    Test reader/writer of EAF files.

    """
    def test_detect(self):
        """Test the file format detection method."""

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith(sppasEAF().default_extension):
                self.assertTrue(sppasEAF.detect(f))
            else:
                self.assertFalse(sppasEAF.detect(f))

    # -----------------------------------------------------------------------

    def test_members(self):
        txt = sppasEAF()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertTrue(txt.metadata_support())
        self.assertTrue(txt.ctrl_vocab_support())
        self.assertTrue(txt.media_support())
        self.assertTrue(txt.hierarchy_support())
        self.assertFalse(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------------

    def test_make_point(self):
        """Convert data into the appropriate digit type, or not."""

        self.assertEqual(sppasPoint(132.3), sppasEAF().make_point("132300"))
        self.assertEqual(sppasPoint(4.2), sppasEAF().make_point("4200."))

        with self.assertRaises(TypeError):
            sppasEAF().make_point("3a")

    # -----------------------------------------------------------------------

    def test_format_point(self):
        """Convert data into the appropriate digit type, or not."""

        self.assertEqual(132300, sppasEAF().format_point(132.3))
        self.assertEqual(4200, sppasEAF().format_point(4.2))

        with self.assertRaises(TypeError):
            sppasEAF().format_point("3a")

    # -----------------------------------------------------------------------

    def test_document_root(self):
        """document <-> root."""

        # create an element tree for EAF format
        root = sppasEAF._format_document()

        # then, create a Transcription from the element tree
        eaf = sppasEAF()
        eaf._parse_document(root)

        # so, test the result!
        author = sg.__name__ + " " + sg.__version__ + " (C) " + sg.__author__
        self.assertEqual(sppasTime().now, eaf.get_meta("file_created_date"))
        self.assertEqual("3.0", eaf.get_meta("file_created_format_version"))
        self.assertEqual(author, eaf.get_meta("file_created_author"))

    # -----------------------------------------------------------------------

    def test_license(self):
        """LICENSE <-> root element."""

        # create an element tree for EAF format
        root = sppasEAF._format_document()
        eaf = sppasEAF()

        # override the license (content only)
        eaf.set_meta('file_license_text_0', 'This is the license content of the document.')
        eaf._format_license(root)
        for i, license_root in enumerate(root.findall('LICENSE')):
            eaf._parse_license(license_root, i)
        self.assertTrue(eaf.is_meta_key('file_license_text_0'))
        self.assertEqual('This is the license content of the document.', eaf.get_meta('file_license_text_0'))
        self.assertEqual('https://www.gnu.org/licenses/gpl-3.0.en.html', eaf.get_meta('file_license_url_0'))

        # a license (content + url)
        eaf.set_meta('file_license_url_0', 'filename.txt')
        eaf._format_license(root)
        for i, license_root in enumerate(root.findall('LICENSE')):
            eaf._parse_license(license_root)
        self.assertTrue(eaf.is_meta_key('file_license_text_0'))
        self.assertTrue(eaf.is_meta_key('file_license_url_0'))
        self.assertEqual('This is the license content of the document.', eaf.get_meta('file_license_text_0'))
        self.assertEqual('filename.txt', eaf.get_meta('file_license_url_0'))

    # -----------------------------------------------------------------------

    def test_locale(self):
        """LOCALE <-> root element."""

        # create an element tree for EAF format
        root = sppasEAF._format_document()
        eaf = sppasEAF()

        # no license
        eaf._format_locales(root)
        self.assertFalse(eaf.is_meta_key('locale_code_0'))

        # a locale
        eaf.set_meta('locale_code_0', 'en')
        eaf._format_locales(root)
        for i, locale_root in enumerate(root.findall('LOCALE')):
            eaf._parse_locale(locale_root, i)
        self.assertTrue(eaf.is_meta_key('locale_code_0'))
        self.assertFalse(eaf.is_meta_key('locale_country_0'))
        self.assertFalse(eaf.is_meta_key('locale_variant_0'))
        self.assertEqual('en', eaf.get_meta('locale_code_0'))

        # a license (content + url)
        eaf.set_meta('locale_country_0', 'US')
        eaf._format_locales(root)
        for i, locale_root in enumerate(root.findall('LOCALE')):
            eaf._parse_locale(locale_root)
        self.assertTrue(eaf.is_meta_key('locale_code_0'))
        self.assertTrue(eaf.is_meta_key('locale_country_0'))
        self.assertEqual('en', eaf.get_meta('locale_code_0'))
        self.assertEqual('US', eaf.get_meta('locale_country_0'))

    # -----------------------------------------------------------------------

    def test_language(self):
        """LANGUAGE <-> root element."""

        # create an element tree for EAF format
        root = sppasEAF._format_document()
        eaf = sppasEAF()

        # no language defined (sppas assign 'und')
        eaf._format_languages(root)
        self.assertTrue(eaf.is_meta_key('language_code_0'))
        self.assertTrue(eaf.is_meta_key('language_name_0'))
        self.assertTrue(eaf.is_meta_key('language_url_0'))
        self.assertEqual('und', eaf.get_meta('language_code_0'))
        self.assertEqual('Undetermined', eaf.get_meta('language_name_0'))
        self.assertEqual('https://iso639-3.sil.org/code/und', eaf.get_meta('language_url_0'))

        # create an element tree for EAF format
        root = sppasEAF._format_document()
        eaf = sppasEAF()

        # a language (override the default)
        eaf.set_meta('language_code_0', 'eng')
        self.assertEqual('eng', eaf.get_meta('language_code_0'))
        eaf._format_languages(root)  # add the language into the tree
        for i, language_root in enumerate(root.findall('LANGUAGE')):
            # get the language from the tree to eaf
            eaf._parse_language(language_root, i)
        self.assertEqual('eng', eaf.get_meta('language_code_0'))

        # a language (content + url)
        eaf.set_meta('language_code_0', 'fra')
        eaf.set_meta('language_name_0', 'French')
        eaf.set_meta('language_url_0', 'https://iso639-3.sil.org/code/fra')
        eaf._format_languages(root)
        for i, language_root in enumerate(root.findall('LANGUAGE')):
            eaf._parse_language(language_root)
        self.assertTrue(eaf.is_meta_key('language_code_0'))
        self.assertTrue(eaf.is_meta_key('language_name_0'))
        self.assertTrue(eaf.is_meta_key('language_url_0'))
        self.assertEqual('fra', eaf.get_meta('language_code_0'))
        self.assertEqual('French', eaf.get_meta('language_name_0'))
        self.assertEqual('https://iso639-3.sil.org/code/fra', eaf.get_meta('language_url_0'))

    # -----------------------------------------------------------------------

    def test_media(self):
        """MEDIA_DESCRIPTOR <-> sppasMedia()."""

        root = sppasEAF._format_document()
        header_root = ET.SubElement(root, "HEADER")
        media = sppasMedia("filename.wav")

        # Format eaf: from sppasMedia() to 'MEDIA'
        sppasEAF._format_media(root, media)
        sppasEAF._format_property(header_root, media)

        # Parse the tree: from 'MEDIA' to sppasMedia()
        parsed_media = list()
        for child in root.iter('MEDIA_DESCRIPTOR'):
            parsed_media.append(sppasEAF._parse_media_descriptor(child, header_root))

        self.assertEqual(1, len(parsed_media))
        self.assertEqual(media.get_filename(), parsed_media[0].get_filename())
        self.assertEqual(media.get_mime_type(), parsed_media[0].get_mime_type())
        self.assertEqual(media.get_id(), parsed_media[0].get_id())
        self.assertFalse(parsed_media[0].is_meta_key('RELATIVE_MEDIA_URL'))
        self.assertFalse(parsed_media[0].is_meta_key('TIME_ORIGIN'))
        self.assertFalse(parsed_media[0].is_meta_key('EXTRACTED_FROM'))

        root = sppasEAF._format_document()
        header_root = ET.SubElement(root, "HEADER")
        media.set_meta('media_source', 'secondary')

        sppasEAF._format_media(root, media)
        sppasEAF._format_property(header_root, media)
        parsed_media = list()
        for child in root.iter('MEDIA_DESCRIPTOR'):
            parsed_media.append(sppasEAF._parse_media_descriptor(child, header_root))
        self.assertEqual(0, len(parsed_media))

        media.set_meta('media_source', 'primary')
        media.set_meta('EXTRACTED_FROM', 'filename.mov')
        sppasEAF._format_media(root, media)
        for child in root.iter('MEDIA_DESCRIPTOR'):
            parsed_media.append(sppasEAF._parse_media_descriptor(child, header_root))

        self.assertEqual(1, len(parsed_media))
        self.assertEqual(parsed_media[0], media)
        self.assertFalse(parsed_media[0].is_meta_key('RELATIVE_MEDIA_URL'))
        self.assertFalse(parsed_media[0].is_meta_key('TIME_ORIGIN'))
        self.assertTrue(parsed_media[0].is_meta_key('EXTRACTED_FROM'))

    # -----------------------------------------------------------------------

    def test_linked_file(self):
        """LINKED_FILE_DESCRIPTOR <-> sppasMedia()."""

        root = sppasEAF._format_document()
        header_root = ET.SubElement(root, "HEADER")
        media = sppasMedia("filename.wav")
        media.set_meta('media_source', 'secondary')

        # Format eaf: from sppasMedia() to 'MEDIA'
        sppasEAF._format_linked_media(root, media)
        sppasEAF._format_property(header_root, media)

        # Parse the tree: from 'LINKED' to sppasMedia()
        parsed_media = list()
        for child in root.iter('LINKED_FILE_DESCRIPTOR'):
            parsed_media.append(sppasEAF._parse_linked_file_descriptor(child, header_root))

        self.assertEqual(1, len(parsed_media))
        self.assertEqual(media, parsed_media[0])
        self.assertFalse(parsed_media[0].is_meta_key('RELATIVE_LINK_URL'))
        self.assertFalse(parsed_media[0].is_meta_key('TIME_ORIGIN'))
        self.assertFalse(parsed_media[0].is_meta_key('ASSOCIATED_WITH'))

        root = sppasEAF._format_document()
        header_root = ET.SubElement(root, "HEADER")
        media.set_meta('media_source', 'primary')

        sppasEAF._format_linked_media(root, media)
        sppasEAF._format_property(header_root, media)
        parsed_media = list()
        for child in root.iter('LINKED_FILE_DESCRIPTOR'):
            parsed_media.append(sppasEAF._parse_linked_file_descriptor(child, header_root))
        self.assertEqual(0, len(parsed_media))

        media.set_meta('media_source', 'secondary')
        media.set_meta('ASSOCIATED_WITH', 'filename.mov')
        sppasEAF._format_linked_media(root, media)
        sppasEAF._format_property(header_root, media)
        for child in root.iter('LINKED_FILE_DESCRIPTOR'):
            parsed_media.append(sppasEAF._parse_linked_file_descriptor(child, header_root))

        self.assertEqual(1, len(parsed_media))
        self.assertEqual(media, parsed_media[0])
        self.assertFalse(parsed_media[0].is_meta_key('RELATIVE_LINK_URL'))
        self.assertFalse(parsed_media[0].is_meta_key('TIME_ORIGIN'))
        self.assertTrue(parsed_media[0].is_meta_key('ASSOCIATED_WITH'))

    # -----------------------------------------------------------------------

    def test_property(self):
        """PROPERTY <-> sppasMetadata()."""

        root = sppasEAF._format_document()
        eaf = sppasEAF()
        eaf.set_meta('key1', 'value1')
        eaf.set_meta('key2', 'value2')
        sppasEAF._format_property(root, eaf)

        eaf2 = sppasEAF()
        for property_root in root.findall('PROPERTY'):
            eaf2._parse_property(property_root)

        self.assertTrue(eaf2.is_meta_key('key1'))
        self.assertTrue(eaf2.is_meta_key('key2'))
        self.assertEqual(eaf.get_meta('key1'), eaf2.get_meta('key1'))
        self.assertEqual(eaf.get_meta('key2'), eaf2.get_meta('key2'))

    # -----------------------------------------------------------------------

    def test_ctrl_vocab(self):
        """CONTROLLED_VOCABULARY <-> sppasCtrlVocab()."""

        root = sppasEAF._format_document()
        ctrl_vocab = sppasCtrlVocab(name="c")

        eaf = sppasEAF()
        eaf.add_ctrl_vocab(ctrl_vocab)
        eaf._format_ctrl_vocab(root, ctrl_vocab)
        c = list()
        for c_node in root.findall('CONTROLLED_VOCABULARY'):
            c.append(sppasEAF._parse_ctrl_vocab(c_node))
        self.assertEqual(1, len(c))
        self.assertEqual(0, len(c[0]))

    # -----------------------------------------------------------------------

    def test_parse_alignable_tier(self):
        """TIER <-> sppasTier()."""

        # two aligned annotations in the tier
        tier_xml = '<TIER TIER_ID="test" LINGUISTIC_TYPE_REF="utterance" DEFAULT_LOCALE="en">\n'\
                   '  <ANNOTATION>\n'\
                   '    <ALIGNABLE_ANNOTATION ANNOTATION_ID="a1" TIME_SLOT_REF1="ts2" TIME_SLOT_REF2="ts5">\n'\
                   '      <ANNOTATION_VALUE>label</ANNOTATION_VALUE>\n'\
                   '    </ALIGNABLE_ANNOTATION>\n'\
                   ' </ANNOTATION>\n' \
                   ' <ANNOTATION>\n' \
                   '      <ALIGNABLE_ANNOTATION ANNOTATION_ID="a2" TIME_SLOT_REF1="ts22" TIME_SLOT_REF2="ts24">\n' \
                   '          <ANNOTATION_VALUE></ANNOTATION_VALUE>\n' \
                   '     </ALIGNABLE_ANNOTATION>\n' \
                   '  </ANNOTATION>\n' \
                   '</TIER>'
        time_slots = dict()
        time_slots['ts2'] = "0"
        time_slots['ts5'] = "1000"
        time_slots['ts22'] = "2000"
        time_slots['ts24'] = "3567"

        tree = ET.ElementTree(ET.fromstring(tier_xml))
        tier_root = tree.getroot()
        eaf = sppasEAF()
        tier = eaf.create_tier('test')
        eaf._parse_alignable_tier(tier_root, tier, time_slots)
        self.assertEqual(2, len(tier))
        self.assertEqual(format_labels('label'), tier[0].get_labels())
        self.assertEqual(sppasPoint(0.), tier[0].get_lowest_localization())
        self.assertEqual(sppasPoint(1.), tier[0].get_highest_localization())
        self.assertEqual('a1', tier[0].get_meta('id'))
        self.assertEqual([sppasLabel(sppasTag(''))], tier[1].get_labels())
        self.assertEqual(sppasPoint(2.), tier[1].get_lowest_localization())
        self.assertEqual(sppasPoint(3.567), tier[1].get_highest_localization())
        self.assertEqual('a2', tier[1].get_meta('id'))

        # two aligned annotations in the tier + 1 non-aligned
        tier_xml = '<TIER TIER_ID="test" LINGUISTIC_TYPE_REF="utterance" DEFAULT_LOCALE="en">\n'\
                   ' <ANNOTATION>\n'\
                   '    <ALIGNABLE_ANNOTATION ANNOTATION_ID="a1" TIME_SLOT_REF1="ts2" TIME_SLOT_REF2="ts5">\n'\
                   '      <ANNOTATION_VALUE>label1</ANNOTATION_VALUE>\n'\
                   '    </ALIGNABLE_ANNOTATION>\n'\
                   ' </ANNOTATION>\n' \
                   ' <ANNOTATION>\n' \
                   '      <ALIGNABLE_ANNOTATION ANNOTATION_ID="a2" TIME_SLOT_REF1="ts5" TIME_SLOT_REF2="ts6">\n' \
                   '          <ANNOTATION_VALUE>label2</ANNOTATION_VALUE>\n'\
                   '     </ALIGNABLE_ANNOTATION>\n' \
                   '  </ANNOTATION>\n' \
                   ' <ANNOTATION>\n' \
                   '      <ALIGNABLE_ANNOTATION ANNOTATION_ID="a3" TIME_SLOT_REF1="ts22" TIME_SLOT_REF2="ts24">\n' \
                   '          <ANNOTATION_VALUE />\n' \
                   '     </ALIGNABLE_ANNOTATION>\n' \
                   '  </ANNOTATION>\n' \
                   '</TIER>'
        time_slots = dict()
        time_slots['ts2'] = 0
        time_slots['ts6'] = 1000
        time_slots['ts22'] = 2000
        time_slots['ts24'] = 3567

        # we'll have only 2 annotations because ts5 is omitted in the time_slots
        tree = ET.ElementTree(ET.fromstring(tier_xml))
        tier_root = tree.getroot()
        eaf = sppasEAF()
        tier = eaf.create_tier('test')
        eaf._parse_alignable_tier(tier_root, tier, time_slots)
        self.assertEqual(2, len(tier))
        self.assertEqual(format_labels('label1\nlabel2'), tier[0].get_labels())
        self.assertEqual(sppasPoint(0.), tier[0].get_lowest_localization())
        self.assertEqual(sppasPoint(1.), tier[0].get_highest_localization())
        self.assertEqual('a1', tier[0].get_meta('id'))
        self.assertEqual([sppasLabel(sppasTag(''))], tier[1].get_labels())
        self.assertEqual(sppasPoint(2.), tier[1].get_lowest_localization())
        self.assertEqual(sppasPoint(3.567), tier[1].get_highest_localization())
        self.assertEqual('a3', tier[1].get_meta('id'))

    # -----------------------------------------------------------------------

    def test_parse_ref_tier(self):
        """TIER <-> sppasTier()."""

        # two aligned annotations in the aligned tier + 2 annotations in the ref tier
        tier_xml = '<TIER TIER_ID="test" LINGUISTIC_TYPE_REF="speech" DEFAULT_LOCALE="en">\n'\
                   '  <ANNOTATION>\n'\
                   '    <ALIGNABLE_ANNOTATION ANNOTATION_ID="a1" TIME_SLOT_REF1="ts2" TIME_SLOT_REF2="ts5">\n'\
                   '      <ANNOTATION_VALUE>label</ANNOTATION_VALUE>\n'\
                   '    </ALIGNABLE_ANNOTATION>\n'\
                   ' </ANNOTATION>\n' \
                   ' <ANNOTATION>\n' \
                   '      <ALIGNABLE_ANNOTATION ANNOTATION_ID="a2" TIME_SLOT_REF1="ts22" TIME_SLOT_REF2="ts24">\n' \
                   '          <ANNOTATION_VALUE></ANNOTATION_VALUE>\n' \
                   '     </ALIGNABLE_ANNOTATION>\n' \
                   '  </ANNOTATION>\n' \
                   '</TIER>'
        ref_tier_xml = '<TIER TIER_ID="testref" LINGUISTIC_TYPE_REF="motion" PARENT_REF="test">\n'\
                       '  <ANNOTATION>\n'\
                       '    <REF_ANNOTATION ANNOTATION_ID="a3" ANNOTATION_REF="a1">\n'\
                       '      <ANNOTATION_VALUE>lemme</ANNOTATION_VALUE>\n'\
                       '    </REF_ANNOTATION>\n'\
                       ' </ANNOTATION>\n' \
                       ' <ANNOTATION>\n' \
                       '      <REF_ANNOTATION ANNOTATION_ID="a4" ANNOTATION_REF="a2">\n' \
                       '         <ANNOTATION_VALUE>blabla</ANNOTATION_VALUE>\n' \
                       '     </REF_ANNOTATION>\n' \
                       '  </ANNOTATION>\n' \
                       '</TIER>'
        time_slots = dict()
        time_slots['ts2'] = 0
        time_slots['ts5'] = 1000
        time_slots['ts22'] = 2000
        time_slots['ts24'] = 3567

        tree = ET.ElementTree(ET.fromstring(tier_xml))
        tier_root = tree.getroot()
        tree = ET.ElementTree(ET.fromstring(ref_tier_xml))
        ref_tier_root = tree.getroot()
        eaf = sppasEAF()
        tier = eaf.create_tier('test')
        ref_tier = eaf.create_tier('ref_test')
        eaf._parse_alignable_tier(tier_root, tier, time_slots)
        self.assertEqual(2, len(tier))
        eaf._parse_ref_tier(ref_tier_root, ref_tier)
        self.assertEqual(2, len(ref_tier))
        self.assertEqual(format_labels('lemme'), ref_tier[0].get_labels())
        self.assertEqual(sppasPoint(0.), ref_tier[0].get_lowest_localization())
        self.assertEqual(sppasPoint(1.), ref_tier[0].get_highest_localization())
        self.assertEqual('a3', ref_tier[0].get_meta('id'))
        self.assertEqual(format_labels('blabla'), ref_tier[1].get_labels())
        self.assertEqual(sppasPoint(2.), ref_tier[1].get_lowest_localization())
        self.assertEqual(sppasPoint(3.567), ref_tier[1].get_highest_localization())
        self.assertEqual('a4', ref_tier[1].get_meta('id'))

    # -----------------------------------------------------------------------

    def test_create_alignable_annotation_element(self):

        # An annotation without label
        tier_xml = '<TIER TIER_ID="test"></TIER>'
        tree = ET.ElementTree(ET.fromstring(tier_xml))
        tier_root = tree.getroot()
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        a1.set_meta('id', "a1")
        created_anns = sppasEAF._create_alignable_annotation_element(a1, tier_root)
        self.assertEqual(1, len(created_anns))
        self.assertEqual(None, created_anns[0].text)
        label_value = created_anns[0].find('ANNOTATION_VALUE')
        self.assertEqual("", label_value.text)
        self.assertEqual("1.0", created_anns[0].attrib['TIME_SLOT_REF1'])
        self.assertEqual("3.5", created_anns[0].attrib['TIME_SLOT_REF2'])
        self.assertEqual("a1", created_anns[0].attrib['ANNOTATION_ID'])

        # An annotation with one label
        tier_xml = '<TIER TIER_ID="test"></TIER>'
        tree = ET.ElementTree(ET.fromstring(tier_xml))
        tier_root = tree.getroot()
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))),
                             sppasLabel(sppasTag("toto")))
        a2.set_meta('id', "a2")
        created_anns = sppasEAF._create_alignable_annotation_element(a2, tier_root)
        self.assertEqual(1, len(created_anns))
        label_value = created_anns[0].find('ANNOTATION_VALUE')
        self.assertEqual("toto", label_value.text)
        self.assertEqual("1.0", created_anns[0].attrib['TIME_SLOT_REF1'])
        self.assertEqual("3.5", created_anns[0].attrib['TIME_SLOT_REF2'])
        self.assertEqual("a2", created_anns[0].attrib['ANNOTATION_ID'])

        # An annotation with two labels
        tier_xml = '<TIER TIER_ID="test"></TIER>'
        tree = ET.ElementTree(ET.fromstring(tier_xml))
        tier_root = tree.getroot()
        a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))),
                             [sppasLabel(sppasTag("toto1")),
                             sppasLabel(sppasTag("toto2"))])
        a3.set_meta('id', "a3")
        created_anns = sppasEAF._create_alignable_annotation_element(a3, tier_root)
        self.assertEqual(2, len(created_anns))
        label_value = created_anns[0].find('ANNOTATION_VALUE')
        self.assertEqual("toto1", label_value.text)
        self.assertEqual("1.0", created_anns[0].attrib['TIME_SLOT_REF1'])
        self.assertEqual("1.0_none_1", created_anns[0].attrib['TIME_SLOT_REF2'])
        self.assertEqual("a3", created_anns[0].attrib['ANNOTATION_ID'])
        label_value = created_anns[1].find('ANNOTATION_VALUE')
        self.assertEqual("toto2", label_value.text)
        self.assertEqual("1.0_none_1", created_anns[1].attrib['TIME_SLOT_REF1'])
        self.assertEqual("3.5", created_anns[1].attrib['TIME_SLOT_REF2'])
        self.assertEqual("a3_2", created_anns[1].attrib['ANNOTATION_ID'])

        # An annotation with 3 labels
        tier_xml = '<TIER TIER_ID="test"></TIER>'
        tree = ET.ElementTree(ET.fromstring(tier_xml))
        tier_root = tree.getroot()
        a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))),
                             [sppasLabel(sppasTag("toto1")),
                              sppasLabel(sppasTag("toto2")),
                              sppasLabel(sppasTag("toto3"))])
        a3.set_meta('id', "a3")
        created_anns = sppasEAF._create_alignable_annotation_element(a3, tier_root)
        self.assertEqual(3, len(created_anns))
        label_value = created_anns[0].find('ANNOTATION_VALUE')
        self.assertEqual("toto1", label_value.text)
        self.assertEqual("1.0", created_anns[0].attrib['TIME_SLOT_REF1'])
        self.assertEqual("1.0_none_1", created_anns[0].attrib['TIME_SLOT_REF2'])
        self.assertEqual("a3", created_anns[0].attrib['ANNOTATION_ID'])
        label_value = created_anns[1].find('ANNOTATION_VALUE')
        self.assertEqual("toto2", label_value.text)
        self.assertEqual("1.0_none_1", created_anns[1].attrib['TIME_SLOT_REF1'])
        self.assertEqual("1.0_none_2", created_anns[1].attrib['TIME_SLOT_REF2'])
        self.assertEqual("a3_2", created_anns[1].attrib['ANNOTATION_ID'])
        label_value = created_anns[2].find('ANNOTATION_VALUE')
        self.assertEqual("toto3", label_value.text)
        self.assertEqual("1.0_none_2", created_anns[2].attrib['TIME_SLOT_REF1'])
        self.assertEqual("3.5", created_anns[2].attrib['TIME_SLOT_REF2'])
        self.assertEqual("a3_3", created_anns[2].attrib['ANNOTATION_ID'])

    # -----------------------------------------------------------------------

    def test_format_alignable_annotations(self):
        """(0..*) ANNOTATION <-> sppasAnnotation (0..*)."""

        tier_xml = '<TIER TIER_ID="test"></TIER>'
        tree = ET.ElementTree(ET.fromstring(tier_xml))
        tier_root = tree.getroot()
        tier = sppasTier('Test')
        a1 = tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        a1.set_meta('id', "a1")
        a2 = tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.5), sppasPoint(5.))),
                                    sppasLabel(sppasTag("toto_a2")))
        a2.set_meta('id', "a2")
        a3 = tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(6.), sppasPoint(6.5))),
                                    [sppasLabel(sppasTag("toto1_a3")),
                                     sppasLabel(sppasTag("toto2_a3"))])
        a3.set_meta('id', "a3")
        time_values = list()
        sppasEAF._format_alignable_annotations(tier_root, tier, time_values)

        created = dict()
        for ann_root in tier_root.findall('ANNOTATION'):
            align_ann_root = ann_root.find('ALIGNABLE_ANNOTATION')

            # get the time values we previously assigned.
            begin = align_ann_root.attrib["TIME_SLOT_REF1"]
            end = align_ann_root.attrib["TIME_SLOT_REF2"]
            ann_id = align_ann_root.attrib["ANNOTATION_ID"]
            created[ann_id] = (begin, end)

        self.assertEqual(4, len(created))
        self.assertEqual(("1.0", "3.5"), created["a1"])
        self.assertEqual(("3.5", "5.0"), created["a2"])
        self.assertEqual(("6.0", "6.0_none_1"), created["a3"])
        self.assertEqual(("6.0_none_1", "6.5"), created["a3_2"])

        self.assertEqual(6, len(time_values))
        self.assertTrue((1.0, 0, tier) in time_values)
        self.assertTrue((3.5, 0, tier) in time_values)
        self.assertTrue((5.0, 0, tier) in time_values)
        self.assertTrue((6.0, 0, tier) in time_values)
        self.assertTrue((6.0, 1, tier) in time_values)
        self.assertTrue((6.5, 0, tier) in time_values)

        time_slots = sppasEAF._fix_time_slots(time_values)
        self.assertEqual("ts1", time_slots[(1.0, 0, tier)])
        self.assertEqual("ts2", time_slots[(3.5, 0, tier)])
        self.assertEqual("ts3", time_slots[(5.0, 0, tier)])
        self.assertEqual("ts4", time_slots[(6.0, 0, tier)])
        self.assertEqual("ts5", time_slots[(6.0, 1, tier)])
        self.assertEqual("ts6", time_slots[(6.5, 0, tier)])

        sppasEAF._re_format_alignable_annotations(tier_root, tier, time_slots)

        created = dict()
        for ann_root in tier_root.findall('ANNOTATION'):
            align_ann_root = ann_root.find('ALIGNABLE_ANNOTATION')

            # get the time values we previously assigned.
            begin = align_ann_root.attrib["TIME_SLOT_REF1"]
            end = align_ann_root.attrib["TIME_SLOT_REF2"]
            ann_id = align_ann_root.attrib["ANNOTATION_ID"]
            created[ann_id] = (begin, end)

        self.assertEqual(4, len(created))
        self.assertEqual(("ts1", "ts2"), created["a1"])
        self.assertEqual(("ts2", "ts3"), created["a2"])
        self.assertEqual(("ts4", "ts5"), created["a3"])
        self.assertEqual(("ts5", "ts6"), created["a3_2"])

    # -----------------------------------------------------------------------

    def test_format_alignable_tiers(self):

        # Create two tiers and generate the Elan element tree.
        eaf = sppasEAF()
        tier1 = eaf.create_tier('Test1')
        a1 = tier1.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        a1.set_meta('id', "a1")
        a2 = tier1.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.5), sppasPoint(5.))),
                                     sppasLabel(sppasTag("toto_a2")))
        a2.set_meta('id', "a2")
        a3 = tier1.create_annotation(sppasLocation(sppasInterval(sppasPoint(6.), sppasPoint(6.5))),
                                     [sppasLabel(sppasTag("toto1_a3")),
                                      sppasLabel(sppasTag("toto2_a3"))])
        a3.set_meta('id', "a3")

        tier2 = eaf.create_tier('Test2')
        a4 = tier2.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        a4.set_meta('id', "a4")
        a5 = tier2.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.5), sppasPoint(5.))),
                                     sppasLabel(sppasTag("toto_a2")))
        a5.set_meta('id', "a5")
        a6 = tier2.create_annotation(sppasLocation(sppasInterval(sppasPoint(6.), sppasPoint(7.))),
                                     [sppasLabel(sppasTag("toto1_a3")),
                                      sppasLabel(sppasTag("toto2_a3"))])
        a6.set_meta('id', "a6")

        # Create the tiers (not filled)
        root = sppasEAF._format_document()
        eaf._format_tier_root(root)
        alignables = [tier for tier in eaf]
        # Fill with annotations
        eaf._format_alignable_tiers(root, alignables)

        created = dict()
        for tier_root in root.findall('TIER'):
            for ann_root in tier_root.findall('ANNOTATION'):
                align_ann_root = ann_root.find('ALIGNABLE_ANNOTATION')

                # get the time values we previously assigned.
                begin = align_ann_root.attrib["TIME_SLOT_REF1"]
                end = align_ann_root.attrib["TIME_SLOT_REF2"]
                ann_id = align_ann_root.attrib["ANNOTATION_ID"]
                created[ann_id] = (begin, end)

        self.assertEqual(8, len(created))
        self.assertEqual(("ts1", "ts3"), created["a1"])
        self.assertEqual(("ts3", "ts5"), created["a2"])
        self.assertEqual(("ts7", "ts8"), created["a3"])
        self.assertEqual(("ts8", "ts11"), created["a3_2"])
        self.assertEqual(("ts2", "ts4"), created["a4"])
        self.assertEqual(("ts4", "ts6"), created["a5"])
        self.assertEqual(("ts9", "ts10"), created["a6"])
        self.assertEqual(("ts10", "ts12"), created["a6_2"])

    # -----------------------------------------------------------------------

    def test_format_ref_tier(self):
        # Create two tiers and generate the Elan element tree.
        eaf = sppasEAF()
        tier1 = eaf.create_tier('Test1')
        a1 = tier1.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        a1.set_meta('id', "a1")
        a2 = tier1.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.5), sppasPoint(5.))),
                                     sppasLabel(sppasTag("toto_a2")))
        a2.set_meta('id', "a2")
        a3 = tier1.create_annotation(sppasLocation(sppasInterval(sppasPoint(6.), sppasPoint(6.5))),
                                     sppasLabel(sppasTag("toto1_a3")))
        a3.set_meta('id', "a3")

        tier2 = eaf.create_tier('Test2')
        a4 = tier2.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        a4.set_meta('id', "a4")
        a5 = tier2.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.5), sppasPoint(5.))),
                                     sppasLabel(sppasTag("toto_t2_a2")))
        a5.set_meta('id', "a5")
        a6 = tier2.create_annotation(sppasLocation(sppasInterval(sppasPoint(6.), sppasPoint(6.5))),
                                     sppasLabel(sppasTag("toto1_t2_a3")))
        a6.set_meta('id', "a6")
        eaf.add_hierarchy_link("TimeAssociation", tier1, tier2)

        # Create the tiers (not filled)
        root = sppasEAF._format_document()
        eaf._format_tier_root(root)
        alignables = eaf._fix_alignable_tiers()
        # Fill with annotations (alignable then ref)
        eaf._format_alignable_tiers(root, alignables)
        eaf._format_reference_tiers(root, alignables)

        created = dict()
        for tier_root in root.findall('TIER'):
            for ann_root in tier_root.findall('ANNOTATION'):
                align_ann_root = ann_root.find('ALIGNABLE_ANNOTATION')
                if align_ann_root is not None:
                    # get the time values we previously assigned.
                    begin = align_ann_root.attrib["TIME_SLOT_REF1"]
                    end = align_ann_root.attrib["TIME_SLOT_REF2"]
                    ann_id = align_ann_root.attrib["ANNOTATION_ID"]
                    created[ann_id] = (begin, end)
                else:
                    ref_ann_root = ann_root.find('REF_ANNOTATION')
                    ann_id = ref_ann_root.attrib["ANNOTATION_ID"]
                    ref = ref_ann_root.attrib['ANNOTATION_REF']
                    created[ann_id] = (ref, ref)

        self.assertEqual(6, len(created))
        self.assertEqual(("ts1", "ts2"), created["a1"])
        self.assertEqual(("ts2", "ts3"), created["a2"])
        self.assertEqual(("ts4", "ts5"), created["a3"])
        self.assertEqual(("a1", "a1"), created["a4"])
        self.assertEqual(("a2", "a2"), created["a5"])
        self.assertEqual(("a3", "a3"), created["a6"])
