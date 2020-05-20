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

    src.anndata.tests.test_aio_text
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the reader/writer of SPPAS for TXT files.

"""

import unittest
import os.path

from ..aio.text import sppasRawText
from ..aio.text import sppasCSV
from ..aio.text import sppasBaseText
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestBaseText(unittest.TestCase):
    """
    Base text is mainly made of utility methods.
    """
    def test_members(self):
        txt = sppasBaseText()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertFalse(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertTrue(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertTrue(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_make_point(self):
        """Convert data into the appropriate digit type, or not."""

        self.assertEqual(sppasPoint(3., 0.001), sppasBaseText.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.001), sppasBaseText.make_point("3."))
        self.assertEqual(sppasPoint(3), sppasBaseText.make_point("3"))
        with self.assertRaises(TypeError):
            sppasBaseText.make_point("3a")

    # -----------------------------------------------------------------

    def test_format_quotation_marks(self):
        """Remove initial and final quotation mark."""

        self.assertEqual("ab", sppasBaseText.format_quotation_marks("ab"))
        self.assertEqual("ab", sppasBaseText.format_quotation_marks('"ab"'))
        self.assertEqual("ab", sppasBaseText.format_quotation_marks("'ab'"))
        self.assertEqual("ab", sppasBaseText.format_quotation_marks(' "ab" '))
        self.assertEqual("", sppasBaseText.format_quotation_marks(""))
        self.assertEqual("'", sppasBaseText.format_quotation_marks("'"))

    # -----------------------------------------------------------------

    def test_split_lines(self):
        """Split the lines with the given separator."""

        self.assertEqual(list(), sppasBaseText.split_lines(list()))
        self.assertEqual([['a']], sppasBaseText.split_lines(['a']))
        self.assertEqual([['a'], ['b']], sppasBaseText.split_lines(['a', 'b']))
        self.assertEqual([['a', 'a'], ['b', 'b']], sppasBaseText.split_lines(['a a', 'b b']))
        self.assertEqual([['a', 'a'], ['b', 'b']], sppasBaseText.split_lines(['a;a', 'b;b'], ";"))
        self.assertIsNone(sppasBaseText.split_lines(['a;a;a', 'b;b'], ";"))

        lines = list()
        lines.append("7.887\t10.892\tGo maith anois a mhac. Anois cé acub?\t0")
        lines.append("11.034\t12.343\tTá neart ábhair ansin anois agat.\t1")
        columns = sppasBaseText.split_lines(lines, separator=" ")
        self.assertIsNone(columns)

        columns = sppasBaseText.split_lines(lines, separator="\t")
        self.assertIsNotNone(columns)
        self.assertEqual(len(columns), 2)     # 2 lines
        self.assertEqual(len(columns[0]), 4)  # 4 columns in each line
        self.assertEqual(columns[1][0], "11.034")
        self.assertEqual(columns[1][1], "12.343")
        self.assertEqual(columns[1][2], "Tá neart ábhair ansin anois agat.")
        self.assertEqual(columns[1][3], "1")

        lines.append(' ')
        lines.append(';; comment')
        columns = sppasBaseText.split_lines(lines, separator="\t")
        self.assertIsNotNone(columns)
        self.assertEqual(len(columns), 2)     # 2 lines
        self.assertEqual(len(columns[0]), 4)  # 4 columns in each line

    # -----------------------------------------------------------------

    def test_location(self):
        """Fix the location from the content of the data."""

        # Point/Interval (int)
        self.assertEqual(sppasLocation(sppasPoint(3)), sppasBaseText.fix_location("3", "3"))
        self.assertEqual(sppasLocation(sppasPoint(3)), sppasBaseText.fix_location('"3"', '"3"'))
        self.assertEqual(sppasLocation(sppasPoint(3)), sppasBaseText.fix_location('"3"', ''))
        self.assertEqual(sppasLocation(sppasPoint(3)), sppasBaseText.fix_location('', '3'))
        self.assertEqual(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))),
                         sppasBaseText.fix_location("3", "4"))
        # Point/Interval (float)
        self.assertEqual(sppasLocation(sppasPoint(3.)), sppasBaseText.fix_location("3.0", "3."))
        self.assertEqual(sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(4.))),
                         sppasBaseText.fix_location("3.0", "4.0"))
        # Errors
        with self.assertRaises(TypeError):
            sppasBaseText.fix_location("a", "b")
        with self.assertRaises(ValueError):
            sppasBaseText.fix_location("4", "3")

        # None
        self.assertIsNone(sppasBaseText.fix_location("", ""))

    # -----------------------------------------------------------------

    def test_is_comment(self):
        """Check if the line is a comment."""

        self.assertTrue(sppasBaseText.is_comment(";;"))
        self.assertTrue(sppasBaseText.is_comment(";; comment"))
        self.assertTrue(sppasBaseText.is_comment("   \t ;; comment"))
        self.assertFalse(sppasBaseText.is_comment("; not a comment"))
        self.assertFalse(sppasBaseText.is_comment("2"))

    # -----------------------------------------------------------------

    def test_create_media(self):
        """Return the media of the given name (create it if necessary)."""

        trs = sppasBaseText()
        self.assertEqual(len(trs.get_media_list()), 0)

        media = sppasBaseText.create_media("filename.wav", trs)
        self.assertEqual(len(trs.get_media_list()), 1)
        self.assertEqual(trs.get_media_list()[0], media)
        self.assertEqual(media.get_filename(), "filename.wav")

        media2 = sppasBaseText.create_media("filename.wav", trs)
        self.assertEqual(len(trs.get_media_list()), 1)
        self.assertEqual(media2, media)

    # -----------------------------------------------------------------

    def test_parse_comment(self):
        """Parse a comment and eventually fill metadata."""

        ctm = sppasRawText()
        line = ";; this is a simple comment."
        sppasBaseText._parse_comment(line, ctm)

        line = ";; meta_key=meta_value"
        sppasBaseText._parse_comment(line, ctm)
        self.assertTrue(ctm.is_meta_key("meta_key"))
        self.assertEqual("meta_value", ctm.get_meta("meta_key"))

        line = ";; \t meta key whitespace   =   meta value\t whitespace   "
        sppasBaseText._parse_comment(line, ctm)
        self.assertTrue(ctm.is_meta_key("meta key whitespace"))
        self.assertEqual("meta value whitespace", ctm.get_meta("meta key whitespace"))

    # -----------------------------------------------------------------

    def test_serialize_header(self):
        """Create a comment with the metadata to be written."""

        ctm = sppasRawText()
        lines = sppasBaseText.serialize_header("sample.ctm", ctm)
        nb_lines = len(lines.split('\n'))

        ctm = sppasRawText()
        ctm.set_meta("meta_key", "meta_value")
        lines = sppasBaseText.serialize_header("sample.ctm", ctm)
        self.assertEqual(nb_lines+1, len(lines.split('\n')))

    # -----------------------------------------------------------------

    def test_serialize_header_software(self):
        """Create a comment with the metadata to be written."""

        header = sppasBaseText.serialize_header_software().split("\n")
        self.assertEqual(len(header), 9)
        for i in range(8):
            self.assertTrue(header[i].startswith(";;"))

    # -----------------------------------------------------------------

    def test_serialize_metadata_private(self):
        """Serialize the metadata of an object in a multi-lines comment."""

        ctm = sppasRawText()
        ctm.set_meta("meta_key", "meta_value")
        line = sppasBaseText.serialize_metadata(ctm)
        self.assertTrue(";; meta_key=meta_value\n" in line)

        stm = sppasRawText()
        stm.set_meta("meta key whitespace", "meta value\t whitespace  ")
        line = sppasBaseText.serialize_metadata(stm)
        self.assertTrue(";; meta key whitespace=meta value whitespace\n" in line)

# ---------------------------------------------------------------------


class TestRawText(unittest.TestCase):
    """
    Represents a Text reader/writer.
    """
    def test_members(self):
        txt = sppasRawText()
        self.assertFalse(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertFalse(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertTrue(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertTrue(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_read1(self):
        """Simple transcription, one utterance a line."""

        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-1.txt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 6)

    # -----------------------------------------------------------------

    def test_read2(self):
        """Column-based transcription."""

        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample-irish-2.txt"))
        self.assertEqual(len(txt), 2)
        self.assertEqual(len(txt[0]), 5)
        self.assertEqual(len(txt[1]), 5)
        self.assertEqual(txt[0].get_name(), "Transcription")
        self.assertEqual(txt[1].get_name(), "Tier-1")

    # -----------------------------------------------------------------

    def test_read3(self):
        """Column-based transcription."""

        txt = sppasRawText()
        txt.read(os.path.join(DATA, "sample.txt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 18)
        self.assertEqual(txt[0].get_name(), "Transcription")
        for i in range(1, 18, 2):
            self.assertEqual(txt[0][i].get_labels()[0].get_best().get_content(), 'sil')
        for i in range(0, 18, 2):
            self.assertEqual(txt[0][i].get_labels()[0].get_best().get_content(), 'speech')

# ---------------------------------------------------------------------


class TestCSVText(unittest.TestCase):
    """
    Represents a CSV reader/writer.

    """
    def test_detect(self):
        """Test the file format detection method."""

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith('.csv'):
                self.assertTrue(sppasCSV.detect(f))
            else:
                self.assertFalse(sppasCSV.detect(f))

    # -----------------------------------------------------------------

    def test_members(self):
        txt = sppasCSV()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertFalse(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertTrue(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertTrue(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_format_lines(self):
        """Append lines content into self."""

        csv = sppasCSV()
        lines = list()
        lines.append('"transcript"\t"7.887"\t"10.892"\t"Go maith anois a mhac. Anois cé acub?"')
        lines.append('"transcript"\t"11.034"\t"12.343"\t"Tá neart ábhair ansin anois agat."')
        csv.format_columns_lines(lines)
        self.assertEqual(len(csv), 1)
        self.assertEqual(csv[0].get_name(), "transcript")
        self.assertEqual(len(csv[0]), 2)

        csv = sppasCSV()
        lines = list()
        lines.append('"transcript";"7.887";"10.892";"Go maith anois a mhac. Anois cé acub?"')
        lines.append('"transcript";"11.034";"12.343";"Tá neart ábhair ansin anois agat."')
        csv.format_columns_lines(lines)
        self.assertEqual(len(csv), 1)
        self.assertEqual(csv[0].get_name(), "transcript")
        self.assertEqual(len(csv[0]), 2)

        csv = sppasCSV()
        lines = list()
        lines.append('"transcript","7.887","10.892","Go maith anois a mhac. Anois cé acub?"')
        lines.append('"transcript","11.034","12.343","Tá neart, ábhair, ansin anois agat."')
        csv.format_columns_lines(lines)
        self.assertEqual(len(csv), 1)
        self.assertEqual(csv[0].get_name(), "transcript")
        self.assertEqual(len(csv[0]), 2)

    # -----------------------------------------------------------------

    def test_read(self):
        txt = sppasCSV()
        txt.read(os.path.join(DATA, "sample-irish.csv"))
        self.assertEqual(len(txt), 2)
        self.assertEqual(len(txt[0]), 5)
        self.assertEqual(len(txt[1]), 5)
