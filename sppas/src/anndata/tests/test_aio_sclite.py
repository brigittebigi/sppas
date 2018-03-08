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

    src.anndata.tests.test_aio_sclite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the reader/writer of SPPAS for CTM/STM files.

"""
import unittest
import os.path
import shutil

from sppas.src.utils.fileutils import sppasFileUtils

from ..anndataexc import AioMultiTiersError
from ..aio.sclite import sppasBaseSclite
from ..aio.sclite import sppasCTM
from ..anndataexc import AioLineFormatError

from ..annlocation.interval import sppasInterval
from ..annlocation.point import sppasPoint
from ..annlabel.tag import sppasTag
from ..annlabel.label import sppasLabel
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestBaseSclite(unittest.TestCase):
    """
    Base text is mainly made of utility methods.

    """
    def test_members(self):
        txt = sppasBaseSclite()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertTrue(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertFalse(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertTrue(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertTrue(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_make_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(sppasPoint(3., 0.005), sppasBaseSclite.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.005), sppasBaseSclite.make_point("3."))
        self.assertEqual(sppasPoint(3), sppasBaseSclite.make_point("3"))
        with self.assertRaises(TypeError):
            sppasBaseSclite.make_point("3a")

    # -----------------------------------------------------------------

    def test_is_comment(self):
        """ Check if the line is a comment. """

        self.assertTrue(sppasBaseSclite.is_comment(";;"))
        self.assertTrue(sppasBaseSclite.is_comment(";; comment"))
        self.assertTrue(sppasBaseSclite.is_comment("   \t ;; comment"))
        self.assertFalse(sppasBaseSclite.is_comment("; not a comment"))
        self.assertFalse(sppasBaseSclite.is_comment("2"))


# ---------------------------------------------------------------------------


class TestScliteCTM(unittest.TestCase):
    """
    CTM file format, from Sclite tool.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------

    def test_detect(self):
        """ Test the file format detection method. """

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith('.ctm'):
                self.assertTrue(sppasCTM.detect(f))
            else:
                self.assertFalse(sppasCTM.detect(f))

    # -----------------------------------------------------------------

    def test_check_line(self):
        """ Check whether a line is correct or not. """

        # Ignore comments
        self.assertFalse(sppasCTM.check_line(";;"))
        self.assertFalse(sppasCTM.check_line(";; comment"))
        self.assertFalse(sppasCTM.check_line("   \t ;; comment"))

        # Blank line
        self.assertFalse(sppasCTM.check_line(""))

        # malformed line
        with self.assertRaises(AioLineFormatError):
            sppasCTM.check_line("not enough columns")
        with self.assertRaises(AioLineFormatError):
            sppasCTM.check_line("too many columns that should be less than 7")

    # -----------------------------------------------------------------
    # read
    # -----------------------------------------------------------------

    def test_get_tier(self):
        """ Return the tier related to the given line. """

        ctm = sppasCTM()

        # a tier will be created
        line = "D_NONE 1 108.74 0.31 SO"
        tier = ctm.get_tier(line)
        self.assertIsNotNone(tier)
        self.assertEqual(tier.get_name(), "D_NONE-1")
        self.assertEqual(len(ctm), 1)

        # the same tier is returned
        line = "D_NONE 1 109.05 0.2 FULL"
        tier = ctm.get_tier(line)
        self.assertIsNotNone(tier)
        self.assertEqual(tier.get_name(), "D_NONE-1")
        self.assertEqual(len(ctm), 1)
        self.assertEqual(tier.get_meta("media_channel"), "1")

        # a new tier is created
        line = "SHOW_1 1 1.0 0.2 JAVA 0.98"
        tier = ctm.get_tier(line)
        self.assertIsNotNone(tier)
        self.assertEqual(tier.get_name(), "SHOW_1-1")
        self.assertEqual(len(ctm), 2)
        self.assertEqual(tier.get_meta("media_channel"), "1")

    # -----------------------------------------------------------------

    def test_get_score(self):
        """ Return the score of the label of a given line. """

        # no score
        self.assertIsNone(sppasCTM.get_score("D_NONE 1 108.74 0.31 SO"))
        # score is not a float
        self.assertIsNone(sppasCTM.get_score("D_NONE 1 108.74 0.31 SO aw"))
        # normal score
        self.assertEqual(sppasCTM.get_score("D_NONE 1 108.74 0.31 SO 3"), 3.)
        # normal score with an error in writing the word!
        self.assertEqual(sppasCTM.get_score("D_NONE 1 108.74 0.31 SO SO SO 3"), 3.)

    # -----------------------------------------------------------------

    def test_parse_comment(self):
        """ Parse a comment and eventually fill metadata. """

        ctm = sppasCTM()
        line = ";; this is a simple comment."
        sppasCTM._parse_comment(line, ctm)
        self.assertEqual(len(ctm.get_meta_keys()), 0)

        line = ";; meta_key=meta_value"
        sppasCTM._parse_comment(line, ctm)
        self.assertEqual(len(ctm.get_meta_keys()), 1)
        self.assertEqual(ctm.get_meta("meta_key"), "meta_value")

        line = ";; \t meta key whitespace   =   meta value\t whitespace   "
        sppasCTM._parse_comment(line, ctm)
        self.assertEqual(len(ctm.get_meta_keys()), 2)
        self.assertEqual(ctm.get_meta("meta key whitespace"), "meta value whitespace")

    # -----------------------------------------------------------------

    def test_create_annotation(self):
        """ Return the annotation corresponding to data of a line. """

        # basic
        ann = sppasCTM._create_annotation(0.3, 0.22, "toto", score=None)
        self.assertEqual(ann.get_location().get_best().get_begin().get_midpoint(), 0.3)
        self.assertEqual(ann.get_location().get_best().get_end().get_midpoint(), 0.52)
        self.assertEqual(ann.get_label().get_best().get_content(), "toto")
        self.assertIsNone(ann.get_label().get_score(ann.get_label().get_best()))

        # tag with score
        ann = sppasCTM._create_annotation(0.3, 0.22, "toto", score=0.95)
        self.assertEqual(ann.get_location().get_best().get_begin().get_midpoint(), 0.3)
        self.assertEqual(ann.get_location().get_best().get_end().get_midpoint(), 0.52)
        self.assertEqual(ann.get_label().get_best().get_content(), "toto")
        self.assertEqual(ann.get_label().get_score(ann.get_label().get_best()), 0.95)

        # tag with whitespace
        # (in theory, ctm files contain only time-aligned words)
        ann = sppasCTM._create_annotation(0.3, 0.22, "bye bye", score=0.95)
        self.assertEqual(ann.get_location().get_best().get_begin().get_midpoint(), 0.3)
        self.assertEqual(ann.get_location().get_best().get_end().get_midpoint(), 0.52)
        self.assertEqual(ann.get_label().get_best().get_content(), "bye_bye")
        self.assertEqual(ann.get_label().get_score(ann.get_label().get_best()), 0.95)

    # -----------------------------------------------------------------

    def test_parse_lines(self):
        """ Fill the transcription from the lines of the CTM file. """

        # 1 media, 1 channel, no alt: the basic (... with a gap and an overlap)
        # -------------------------------------

        lines = list()
        lines.append("D_NONE 1 108.74 0.31 THIS")
        lines.append("D_NONE 1 109.05 0.25 IS")
        lines.append("D_NONE 1 109.25 0.15 AN")
        lines.append("D_NONE 1 109.53 0.16 EXAMPLE")

        ctm = sppasCTM()
        ctm._parse_lines(lines)
        self.assertEqual(len(ctm), 1)
        self.assertEqual(ctm[0].get_name(), "D_NONE-1")
        self.assertEqual(len(ctm[0]), 4)
        self.assertEqual(ctm[0][0].get_label().get_best().get_content(), "THIS")
        self.assertEqual(ctm[0][1].get_label().get_best().get_content(), "IS")
        self.assertEqual(ctm[0][2].get_label().get_best().get_content(), "AN")
        self.assertEqual(ctm[0][3].get_label().get_best().get_content(), "EXAMPLE")
        self.assertEqual(ctm[0][0].get_location().get_best().get_begin(), sppasPoint(108.74))
        self.assertEqual(ctm[0][0].get_location().get_best().get_end(), sppasPoint(109.05))
        self.assertEqual(ctm[0][1].get_location().get_best().get_begin(), sppasPoint(109.05))
        self.assertEqual(ctm[0][1].get_location().get_best().get_end(), sppasPoint(109.30))
        self.assertEqual(ctm[0][2].get_location().get_best().get_begin(), sppasPoint(109.25))
        self.assertEqual(ctm[0][2].get_location().get_best().get_end(), sppasPoint(109.40))
        self.assertEqual(ctm[0][3].get_location().get_best().get_begin(), sppasPoint(109.53))
        self.assertEqual(ctm[0][3].get_location().get_best().get_end(), sppasPoint(109.69))

        # 1 media, 2 channels, no alt
        # ---------------------------

        lines = list()
        lines.append("D_NONE 1 108.74 0.31 THIS")
        lines.append("D_NONE 1 109.05 0.25 IS")
        lines.append("D_NONE 1 109.25 0.15 AN")
        lines.append("D_NONE 1 109.53 0.16 EXAMPLE")
        lines.append("D_NONE 2 109.8 0.2 YEP")

        ctm = sppasCTM()
        ctm._parse_lines(lines)
        self.assertEqual(len(ctm), 2)
        self.assertEqual(ctm[0].get_name(), "D_NONE-1")
        self.assertEqual(ctm[1].get_name(), "D_NONE-2")
        self.assertEqual(len(ctm[0]), 4)
        self.assertEqual(len(ctm[1]), 1)
        self.assertEqual(ctm[1][0].get_label().get_best().get_content(), "YEP")
        self.assertEqual(ctm[1][0].get_location().get_best().get_begin(), sppasPoint(109.8))
        self.assertEqual(ctm[1][0].get_location().get_best().get_end(), sppasPoint(110.))

        # 2 medias, 1 channel, no alt
        # ---------------------------

        lines = list()
        lines.append("D_WAV 1 108.74 0.31 THIS")
        lines.append("D_WAV 1 109.05 0.25 IS")
        lines.append("D_WAV 1 109.25 0.15 AN")
        lines.append("D_WAV 1 109.53 0.16 EXAMPLE")
        lines.append("D_NONE 1 109.8 0.2 YEP")

        ctm = sppasCTM()
        ctm._parse_lines(lines)
        self.assertEqual(len(ctm), 2)
        self.assertEqual(ctm[0].get_name(), "D_WAV-1")
        self.assertEqual(ctm[1].get_name(), "D_NONE-1")
        self.assertEqual(len(ctm[0]), 4)
        self.assertEqual(len(ctm[1]), 1)
        self.assertEqual(ctm[1][0].get_label().get_best().get_content(), "YEP")
        self.assertEqual(ctm[1][0].get_location().get_best().get_begin(), sppasPoint(109.8))
        self.assertEqual(ctm[1][0].get_location().get_best().get_end(), sppasPoint(110.))

        # alternations! currently ignored...
        # ----------------------------------
        lines = list()
        lines.append("D_WAV 1 * * <ALT_BEGIN>")
        lines.append("D_WAV 1 12.00 0.34 THIS")
        lines.append("D_WAV 1 * * <ALT>")
        lines.append("D_WAV 1 12.00 0.34 IS")
        lines.append("D_WAV 1 * * <ALT_END>")

        ctm = sppasCTM()
        ctm._parse_lines(lines)
        self.assertEqual(len(ctm), 1)
        self.assertEqual(ctm[0].get_name(), "D_WAV-1")
        self.assertEqual(len(ctm[0]), 1)

    # -----------------------------------------------------------------

    def test_read(self):
        """ Sample ctm. """

        ctm = sppasCTM()
        ctm.read(os.path.join(DATA, "sample.ctm"))
        self.assertEqual(len(ctm), 4)
        self.assertEqual(len(ctm.get_media_list()), 3)
        self.assertEqual(ctm[0].get_name(), "SHOW_1-1")
        self.assertEqual(ctm[1].get_name(), "SHOW_2-1")
        self.assertEqual(ctm[2].get_name(), "SHOW_2-2")
        self.assertEqual(ctm[3].get_name(), "SHOW_3-1")
        self.assertEqual(len(ctm[0]), 7)
        self.assertEqual(len(ctm[1]), 3)
        self.assertEqual(len(ctm[2]), 6)
        self.assertEqual(len(ctm[3]), 6)

    # -----------------------------------------------------------------
    # Write
    # -----------------------------------------------------------------

    def test_serialize_tag(self):
        """ Convert a tag with its score into a line for CTM files. """

        line = sppasCTM._serialize_tag("WAV", "A", 0.5, 0.22, sppasTag('byebye'), None)
        self.assertEqual("WAV A 0.5 0.22 byebye\n", line)

        line = sppasCTM._serialize_tag("WAV", "A", 0.5, 0.22, sppasTag('byebye'), 0.96)
        self.assertEqual("WAV A 0.5 0.22 byebye 0.96\n", line)

        line = sppasCTM._serialize_tag("WAV", "A", 0.5, 0.22, sppasTag(''), 0.96)
        self.assertEqual("WAV A 0.5 0.22 @ 0.96\n", line)

    # -----------------------------------------------------------------

    def test_serialize_annotation(self):
        """ Convert an annotation into lines for CTM files. """

        # annotation without label
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        line = sppasCTM._serialize_annotation(a1, "WAV", "A")
        self.assertEqual("WAV A 1.0 2.5 @\n", line)

        # annotation with 1 tag in the label
        a2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))),
                             sppasLabel(sppasTag("label")))
        line = sppasCTM._serialize_annotation(a2, "WAV", "A")
        self.assertEqual("WAV A 1.0 2.5 label\n", line)

        # annotation with 2 tags + scores
        a3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))),
                             sppasLabel([sppasTag("label"), sppasTag("level")],
                                        [0.60, 0.4]))
        line = sppasCTM._serialize_annotation(a3, "WAV", "A")
        self.assertEqual("WAV A * * <ALT_BEGIN>\n"
                         "WAV A 1.0 2.5 label 0.6\n"
                         "WAV A * * <ALT>\n"
                         "WAV A 1.0 2.5 level 0.4\n"
                         "WAV A * * <ALT_END>\n", line)

    # -----------------------------------------------------------------

    def test_serialize_metadata(self):
        """ Serialize the metadata of an object in a multi-lines comment. """

        ctm = sppasCTM()
        line = sppasCTM._serialize_metadata(ctm)
        self.assertEqual("", line)

        ctm = sppasCTM()
        ctm.set_meta("meta_key", "meta_value")
        line = sppasCTM._serialize_metadata(ctm)
        self.assertEqual(";; meta_key=meta_value\n", line)

        ctm = sppasCTM()
        ctm.set_meta("meta key whitespace", "meta value\t whitespace  ")
        line = sppasCTM._serialize_metadata(ctm)
        self.assertEqual(";; meta key whitespace=meta value whitespace\n", line)

    # -----------------------------------------------------------------

    def test_serialize_header(self):
        """ Serialize the header of a CTM file with metadata. """

        ctm = sppasCTM()
        lines = ctm._serialize_header("sample.ctm")
        self.assertEqual(len(lines.split('\n')), 15)

        ctm = sppasCTM()
        ctm.set_meta("meta_key", "meta_value")
        lines = ctm._serialize_header("sample.ctm")
        self.assertEqual(len(lines.split('\n')), 16)

    # -----------------------------------------------------------------

    def test_read_write(self):
        """ Write a transcription into a file. """

        ctm = sppasCTM()
        ctm.read(os.path.join(DATA, "sample.ctm"))
        self.assertEqual(len(ctm), 4)
        ctm.write(os.path.join(TEMP, "sample.ctm"))

        ctm2 = sppasCTM()
        ctm2.read(os.path.join(TEMP, "sample.ctm"))
        self.assertEqual(len(ctm2), 4)
        self.assertEqual(len(ctm2.get_media_list()), 3)
        self.assertEqual(ctm2[0].get_name(), "SHOW_1-1")
        self.assertEqual(ctm2[1].get_name(), "SHOW_2-1")
        self.assertEqual(ctm2[2].get_name(), "SHOW_2-2")
        self.assertEqual(ctm2[3].get_name(), "SHOW_3-1")
        self.assertEqual(len(ctm2[0]), 7)
        self.assertEqual(len(ctm2[1]), 3)
        self.assertEqual(len(ctm2[2]), 6)
        self.assertEqual(len(ctm2[3]), 6)