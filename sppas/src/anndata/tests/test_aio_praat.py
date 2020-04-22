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

    src.anndata.tests.test_aio_praat
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the reader/writer of SPPAS for Praat files.

"""
import unittest
import os

from sppas import paths
from sppas.src.utils.makeunicode import u

from ..anndataexc import AioLineFormatError
from ..anndataexc import AioEmptyTierError
from ..anndataexc import AioNoTiersError

from ..aio.praat import sppasBasePraat
from ..aio.praat import sppasTextGrid
from ..aio.praat import sppasBaseNumericalTier
from ..aio.praat import sppasPitchTier
from ..ann.annlocation import sppasInterval
from ..ann.annlocation import sppasPoint
from ..ann.annlabel import sppasTag
from ..ann.annlabel import sppasLabel
from ..ann.annotation import sppasAnnotation
from ..tier import sppasTier
from ..ann.annlocation import sppasLocation

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestBasePraat(unittest.TestCase):
    """

    """
    def test_members(self):
        txt = sppasBasePraat()
        self.assertTrue(txt.multi_tiers_support())
        self.assertFalse(txt.no_tiers_support())
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
        self.assertFalse(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_make_point(self):
        """Convert data into the appropriate digit type, or not."""

        self.assertEqual(sppasPoint(3., 0.005), sppasBasePraat.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.005), sppasBasePraat.make_point("3."))
        self.assertEqual(sppasPoint(3), sppasBasePraat.make_point("3"))
        self.assertEqual(sppasPoint(0.), sppasBasePraat.make_point("0."))

        with self.assertRaises(TypeError):
            sppasBasePraat.make_point("3a")

    # -----------------------------------------------------------------

    def test_parse_int(self):
        """Parse an integer value from a line of a Praat formatted file."""

        # long textgrid
        value = sppasBasePraat._parse_int("size = 1")
        self.assertEqual(value, 1)

        value = sppasBasePraat._parse_int("intervals: size = 23")
        self.assertEqual(value, 23)

        value = sppasBasePraat._parse_int("\t\tintervals:    size   =   \t 23")
        self.assertEqual(value, 23)

        # short textgrid
        value = sppasBasePraat._parse_int("1")
        self.assertEqual(value, 1)

        with self.assertRaises(AioLineFormatError):
            sppasBasePraat._parse_int("n'importe quoi")

        with self.assertRaises(AioLineFormatError):
            sppasBasePraat._parse_int("a = b")

    # -----------------------------------------------------------------

    def test_parse_float(self):
        """Parse a float value from a line of a Praat formatted file."""

        # long textgrid
        value = sppasBasePraat._parse_float("xmax = 21.3471")
        self.assertEqual(value, 21.3471)

        value = sppasBasePraat._parse_float("\t\tmax   =   \t 23")
        self.assertEqual(value, 23.)

        # short textgrid
        value = sppasBasePraat._parse_float("1.098765432")
        self.assertEqual(value, 1.098765432)

        with self.assertRaises(AioLineFormatError):
            sppasBasePraat._parse_float("n'importe quoi")

        with self.assertRaises(AioLineFormatError):
            sppasBasePraat._parse_float("a = b")

    # -----------------------------------------------------------------

    def test_parse_string(self):
        """Parse a float value from a line of a Praat formatted file."""

        # long standard
        text = sppasBasePraat._parse_string('class = "IntervalTier"\n')
        self.assertEqual(text, "IntervalTier")
        text = sppasBasePraat._parse_string('File type = "TextGrid"\n')
        self.assertEqual(text, "TextGrid")
        text = sppasBasePraat._parse_string('name = "TierName"\n')
        self.assertEqual(text, "TierName")
        text = sppasBasePraat._parse_string(' \t text = "a b c"\n')
        self.assertEqual(text, "a b c")

        # short standard
        text = sppasBasePraat._parse_string('"IntervalTier"\n')
        self.assertEqual(text, "IntervalTier")
        text = sppasBasePraat._parse_string(' "a b c"\n')
        self.assertEqual(text, "a b c")

        # long standard with "
        text = sppasBasePraat._parse_string(' \t text = "a ""b"" c"\n')
        self.assertEqual(text, 'a "b" c')

        # short standard with "
        text = sppasBasePraat._parse_string('"a ""b"" c"\n')
        self.assertEqual(text, 'a "b" c')

        # long, empty text
        text = sppasBasePraat._parse_string(' \t text = "   "\n')
        self.assertEqual(text, "")

        # short, empty text
        text = sppasBasePraat._parse_string('"   "\n')
        self.assertEqual(text, "")

        # long, multi-line, first-line
        text = sppasBasePraat._parse_string(' \t text = "the guy     \n')
        self.assertEqual(text, 'the guy')

        # short, multi-line, first-line
        text = sppasBasePraat._parse_string('"the guy    \n')
        self.assertEqual(text, 'the guy')

        # long&short, multi-line, middle-line
        text = sppasBasePraat._parse_string('and the other guy     \n')
        self.assertEqual(text, 'and the other guy')

        # long&short, multi-line, last-line
        text = sppasBasePraat._parse_string('and the last ""ONE""."\n')
        self.assertEqual(text, 'and the last "ONE".')

    # -----------------------------------------------------------------

    def test_serialize_header(self):
        """Serialize the header of a Praat file."""

        header = sppasBasePraat._serialize_header("TextGrid", 0., 10.).split("\n")
        self.assertEqual(len(header), 6)
        self.assertTrue('File type = "ooTextFile"' in header[0])
        self.assertTrue('Object class = "TextGrid"' in header[1])
        self.assertTrue('xmin = 0.' in header[3])
        self.assertTrue('xmax = 10.' in header[4])

    # -----------------------------------------------------------------

    def test_serialize_label_text(self):
        """Convert a label into a text string."""

        a = sppasAnnotation(sppasLocation(sppasPoint(1)), sppasLabel(sppasTag("")))
        line = sppasBasePraat._serialize_labels_text(a)
        self.assertEqual(line, '\t\t\ttext = ""\n')

        a = sppasAnnotation(sppasLocation(sppasPoint(1)), sppasLabel(sppasTag("toto")))
        line = sppasBasePraat._serialize_labels_text(a)
        self.assertEqual(line, '\t\t\ttext = "toto"\n')

        a = sppasAnnotation(sppasLocation(sppasPoint(1)), sppasLabel(sppasTag('"toto"')))
        line = sppasBasePraat._serialize_labels_text(a)
        self.assertEqual(line, '\t\t\ttext = """toto"""\n')

        a = sppasAnnotation(sppasLocation(sppasPoint(1)), sppasLabel(sppasTag('This is "toto" and "titi"')))
        line = sppasBasePraat._serialize_labels_text(a)
        self.assertEqual(line, '\t\t\ttext = "This is ""toto"" and ""titi"""\n')

        a = sppasAnnotation(sppasLocation(sppasPoint(1)), [sppasLabel(sppasTag('"toto"')),
                                                           sppasLabel(sppasTag('titi'))])
        line = sppasBasePraat._serialize_labels_text(a)
        self.assertEqual(line, '\t\t\ttext = """toto""\ntiti"\n')

    # -----------------------------------------------------------------

    def test_serialize_label_value(self):
        """Convert a label with a numerical value into a string."""

        with self.assertRaises(IOError):
            sppasBasePraat._serialize_labels_value([sppasLabel(sppasTag(""))])

        line = sppasBasePraat._serialize_labels_value([sppasLabel(sppasTag("2", tag_type="float"))])
        self.assertEqual(line, '\tvalue = 2.0\n')

        with self.assertRaises(IOError):
            sppasBasePraat._serialize_labels_value([sppasLabel(sppasTag("2"))])

# ---------------------------------------------------------------------------


class TestTextGrid(unittest.TestCase):

    def test_members(self):
        tg = sppasTextGrid()
        self.assertTrue(tg.multi_tiers_support())
        self.assertFalse(tg.no_tiers_support())
        self.assertFalse(tg.metadata_support())
        self.assertFalse(tg.ctrl_vocab_support())
        self.assertFalse(tg.media_support())
        self.assertFalse(tg.hierarchy_support())
        self.assertTrue(tg.point_support())
        self.assertTrue(tg.interval_support())
        self.assertFalse(tg.disjoint_support())
        self.assertFalse(tg.alternative_localization_support())
        self.assertFalse(tg.alternative_tag_support())
        self.assertFalse(tg.radius_support())
        self.assertFalse(tg.gaps_support())
        self.assertFalse(tg.overlaps_support())

    # -----------------------------------------------------------------------

    def test_detect(self):
        """Test the file format detection method."""

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith(sppasTextGrid().default_extension):
                self.assertTrue(sppasTextGrid.detect(f))
            elif filename.endswith(".heuristic"):
                self.assertTrue(sppasTextGrid.detect(f))
            else:
                self.assertFalse(sppasTextGrid.detect(f))

    # -----------------------------------------------------------------------

    def test_parse_tier_long(self):
        """Test the read of a tier."""

        tier_content = 'item [1]:\n'\
                       '  class = "IntervalTier"\n'\
                       '  name = "transcription"\n'\
                       '  xmin = 0.000000\n'\
                       '  xmax = 5.6838880379\n'\
                       '  intervals: size = 2\n'\
                       '  intervals [1]:\n' \
                       '    xmin = 0.0\n' \
                       '    xmax = 2.4971007546\n' \
                       '    text = "gpf_0"\n' \
                       '  intervals [2]:\n' \
                       '    xmin = 2.4971007546\n' \
                       '    xmax = 5.6838880379\n' \
                       '    text = "hier soir j\'ai ouvert la\n' \
                       'porte d\'entrée pour laisser chort- sortir le chat"\n'

        lines = tier_content.split("\n")
        txt = sppasTextGrid()
        txt._parse_tier(lines, 1, is_long=True)
        self.assertEqual(len(txt), 1)
        self.assertEqual(txt[0].get_name(), "transcription")
        self.assertEqual(len(txt[0]), 2)

        with self.assertRaises(AioLineFormatError):
            txt._parse_tier(lines, 2, is_long=True)

        tier_content = 'item [1]:\n'\
                       '  class = "TextTier"\n'\
                       '  name = "INTSINT"\n'\
                       '  xmin = 0.153845\n'\
                       '  xmax = 0.2446326069\n'\
                       '  intervals: size = 2\n'\
                       '  points [1]:\n' \
                       '    time = 0.1538453443\n' \
                       '    mark = "M"\n' \
                       '  points [2]:\n' \
                       '    time = 0.2446326069\n' \
                       '    mark = "T"\n'\
                       'item [2]:\n' \
                       '  class = "TextTier"\n'
        lines = tier_content.split("\n")
        txt = sppasTextGrid()
        txt._parse_tier(lines, 1, is_long=True)
        self.assertEqual(len(txt), 1)
        self.assertEqual(txt[0].get_name(), "INTSINT")
        self.assertEqual(len(txt[0]), 2)

    # -----------------------------------------------------------------------

    def test_parse_tier_short(self):
        """Test the parsing of a tier."""

        tier_content = '"IntervalTier"\n'\
                       '"transcription"\n'\
                       '0\n'\
                       '21.3471\n'\
                       '11\n'\
                       '0\n'\
                       '2.4971007546\n'\
                       '"gpf_0"\n' \
                       '2.4971007546\n'\
                       '5.6838880379\n'\
                       '"ipu_1 hier soir j\'ai ouvert la\n'\
                       'porte d\'entrée pour laisser chort- sortir le chat"\n'
        lines = tier_content.split("\n")
        txt = sppasTextGrid()
        txt._parse_tier(lines, 0, is_long=False)
        self.assertEqual(len(txt), 1)
        self.assertEqual(txt[0].get_name(), "transcription")
        self.assertEqual(len(txt[0]), 2)

        with self.assertRaises(AioLineFormatError):
            txt._parse_tier(lines, 1, is_long=False)

        tier_content = '"TextTier"\n'\
                       '"INTSINT"\n'\
                       '0.153845\n'\
                       '0.2446326069\n'\
                       '2\n'\
                       '0.1538453443\n' \
                       '"M"\n' \
                       '0.2446326069\n' \
                       '"T"\n'
        lines = tier_content.split("\n")
        txt = sppasTextGrid()
        txt._parse_tier(lines, 0, is_long=False)
        self.assertEqual(len(txt), 1)
        self.assertEqual(txt[0].get_name(), "INTSINT")
        self.assertEqual(len(txt[0]), 2)

    # -----------------------------------------------------------------------

    def test_parse_annotation_long(self):
        """Test the parsing of an annotation."""

        ann_content = '    xmin = 0.0\n' \
                      '    xmax = 2.4971007546\n' \
                      '    text = "gpf_0"\n'
        lines = ann_content.split("\n")
        ann, nb = sppasTextGrid._parse_annotation(lines, 0, True)
        self.assertEqual(nb, 3)
        self.assertEqual(sppasInterval(
            sppasTextGrid.make_point(0.),
            sppasTextGrid.make_point(2.4971007546)
        ), ann.get_location().get_best())
        self.assertEqual(sppasTag("gpf_0"), ann.get_labels()[0].get_best())

        ann_content = '  intervals [2]:\n' \
                      '    xmin = 2.4971007546\n' \
                      '    xmax = 5.6838880379\n' \
                      '    text = "hier soir j\'ai ouvert la \n'\
                      'porte d\'entrée pour laisser chort- sortir le ""chat"""\n'
        lines = ann_content.split("\n")
        ann, nb = sppasTextGrid._parse_annotation(lines, 1, True)
        self.assertEqual(nb, 5)
        self.assertEqual(sppasInterval(
                            sppasTextGrid.make_point(2.4971007546),
                            sppasTextGrid.make_point(5.6838880379)),
                         ann.get_location().get_best())
        self.assertEqual(u('hier soir j\'ai ouvert la'),
                         ann.get_labels()[0].get_best().get_content())
        self.assertEqual(u('porte d\'entrée pour laisser chort- sortir le "chat"'),
                         ann.get_labels()[1].get_best().get_content())

        ann_content = 'points [1]:\n'\
                      '    number = 0.054406250000000066\n'\
                      '    value = "Top"\n'
        lines = ann_content.split("\n")
        ann, nb = sppasTextGrid._parse_annotation(lines, 1, False)
        self.assertEqual(sppasTextGrid.make_point(0.054406250000000066),
                         ann.get_location().get_best())
        self.assertEqual(sppasTag("Top"), ann.get_labels()[0].get_best())

    # -----------------------------------------------------------------------

    def test_parse_annotation_short(self):
        """Test the parsing of an annotation."""

        ann_content = '0.0\n' \
                      '2.4971007546\n' \
                      '"gpf_0"\n'
        lines = ann_content.split("\n")
        ann, nb = sppasTextGrid._parse_annotation(lines, 0, True)
        self.assertEqual(nb, 3)
        self.assertEqual(sppasInterval(
            sppasTextGrid.make_point(0.),
            sppasTextGrid.make_point(2.4971007546)
        ), ann.get_location().get_best())
        self.assertEqual(sppasTag("gpf_0"), ann.get_labels()[0].get_best())

        ann_content = '2.4971007546\n' \
                      '5.6838880379\n' \
                      '"hier soir j\'ai ouvert la \n'\
                      'porte d\'entrée pour laisser chort- sortir le ""chat"""\n'
        lines = ann_content.split("\n")
        ann, nb = sppasTextGrid._parse_annotation(lines, 0, True)
        self.assertEqual(nb, 4)
        self.assertEqual(sppasInterval(
            sppasTextGrid.make_point(2.4971007546),
            sppasTextGrid.make_point(5.6838880379)), ann.get_location().get_best())
        self.assertEqual(u('hier soir j\'ai ouvert la'),
                         ann.get_labels()[0].get_best().get_content())
        self.assertEqual(u('porte d\'entrée pour laisser chort- sortir le "chat"'),
                         ann.get_labels()[1].get_best().get_content())

    # -----------------------------------------------------------------------

    def test_parse_localization_long(self):
        """Test parse_localization of a long TextGrid."""

        # interval
        ann_content = '    xmin = 0.0\n' \
                      '    xmax = 2.4971007546\n' \
                      '    text = "gpf_0"\n'
        lines_i = ann_content.split("\n")
        loc, nb = sppasTextGrid._parse_localization(lines_i, 0, True)
        self.assertEqual(sppasInterval(
            sppasTextGrid.make_point(0.),
            sppasTextGrid.make_point(2.4971007546)
        ), loc)
        self.assertEqual(nb, 2)

        # point
        ann_content = '        number = 0.054406250000000066\n'\
                      '        value = 62.49343439812383\n'
        lines_p = ann_content.split("\n")
        loc, nb = sppasTextGrid._parse_localization(lines_p, 0, False)
        self.assertEqual(sppasTextGrid.make_point(0.054406250000000066), loc)
        self.assertEqual(nb, 1)

    # -----------------------------------------------------------------------

    def test_parse_localization_short(self):
        """Test parse_localization of a long TextGrid."""

        # interval
        ann_content = '0.0\n' \
                      '2.4971007546\n' \
                      '"gpf_0"\n'
        lines_i = ann_content.split("\n")
        loc, nb = sppasTextGrid._parse_localization(lines_i, 0, True)
        self.assertEqual(sppasInterval(
            sppasTextGrid.make_point(0.),
            sppasTextGrid.make_point(2.4971007546)
        ), loc)
        self.assertEqual(nb, 2)

        # point
        ann_content = '0.054406250000000066\n'\
                      '"Top"\n'
        lines_p = ann_content.split("\n")
        loc, nb = sppasTextGrid._parse_localization(lines_p, 0, False)
        self.assertEqual(sppasTextGrid.make_point(0.054406250000000066), loc)
        self.assertEqual(nb, 1)

    # -----------------------------------------------------------------------

    def test_parse_text_short(self):
        """Test text parser."""

        # standard tag
        ann_content = '0.0\n' \
                      '2.4971007546\n' \
                      '"gpf_0"\n'
        lines_i = ann_content.split("\n")
        labels, nb = sppasTextGrid._parse_text(lines_i, 2)
        self.assertEqual(sppasTag("gpf_0"), labels[0].get_best())
        self.assertEqual(nb, 3)

        # multi-lines tag
        ann_content = '0.0\n' \
                      '2.4971007546\n' \
                      '"hier soir j\'ai ouvert la\n' \
                      'porte d\'entrée\n'\
                      'pour laisser chort- sortir le ""chat"""\n'
        lines = ann_content.split("\n")
        labels, nb = sppasTextGrid._parse_text(lines, 2)
        self.assertEqual(sppasTag('hier soir j\'ai ouvert la'),
                         labels[0].get_best())
        self.assertEqual(sppasTag('porte d\'entrée'),
                         labels[1].get_best())
        self.assertEqual(sppasTag('pour laisser chort- sortir le "chat"'),
                         labels[2].get_best())
        self.assertEqual(nb, 5)

        with self.assertRaises(AioLineFormatError):
            ann_content = '0.0\n' \
                          '2.4971007546\n' \
                          '"hier soir j\'ai ouvert la\n' \
                          'porte d\'entrée\n'
            lines = ann_content.split("\n")
            sppasTextGrid._parse_text(lines, 2)

    # -----------------------------------------------------------------------

    def test_parse_text_long(self):
        """Test text parser."""

        # standard tag
        ann_content = '\t\txmin = 0.0\n' \
                      '\t\txmax = 2.4971007546\n' \
                      '\t\ttext = "gpf_0"\n'
        lines_i = ann_content.split("\n")
        tag, nb = sppasTextGrid._parse_text(lines_i, 2)
        self.assertEqual([sppasLabel(sppasTag("gpf_0"))], tag)
        self.assertEqual(nb, 3)

        # multi-lines tag
        ann_content = '\t\txmin = 0.0\n' \
                      '\t\txmax = 2.4971007546\n' \
                      '\t\ttext = "hier soir j\'ai ouvert la\n' \
                      'porte d\'entrée\n' \
                      'pour laisser chort- sortir le ""chat"""\n'
        lines = ann_content.split("\n")
        labels, nb = sppasTextGrid._parse_text(lines, 2)
        self.assertEqual(u('hier soir j\'ai ouvert la'),
                         labels[0].get_best().get_content())
        self.assertEqual(u('porte d\'entrée'),
                         labels[1].get_best().get_content())
        self.assertEqual(u('pour laisser chort- sortir le "chat"'),
                         labels[2].get_best().get_content())
        self.assertEqual(nb, 5)

        with self.assertRaises(AioLineFormatError):
            ann_content = '\t\txmin = 0.0\n' \
                          '\t\txmax = 2.4971007546\n' \
                          '\t\ttext = "hier soir j\'ai ouvert la\n' \
                          'porte d\'entrée\n'
            lines = ann_content.split("\n")
            sppasTextGrid._parse_text(lines, 2)

    # -----------------------------------------------------------------------

    def test_read(self):
        txt = sppasTextGrid()
        txt.read(os.path.join(DATA, "sample.TextGrid"))
        self.assertEqual(len(txt), 2)
        self.assertEqual(txt[0].get_name(), "transcription")
        self.assertEqual(txt[1].get_name(), "P-Tones")
        self.assertEqual(len(txt[0]), 4)
        self.assertEqual(len(txt[1]), 2)

        txt = sppasTextGrid()
        txt.read(os.path.join(DATA, "sample2.TextGrid"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(txt[0].get_name(), "Tokens")
        self.assertEqual(len(txt[0]), 1)

    # -----------------------------------------------------------------------

    def test_read_annotated_samples(self):
        phons = os.path.join(DATA, "F_F_B003-P8-phon.TextGrid")
        tokens = os.path.join(DATA, "F_F_B003-P8-token.TextGrid")
        txt_phon = sppasTextGrid()
        txt_phon.read(phons)
        txt_tok = sppasTextGrid()
        txt_tok.read(tokens)
        tier_phon = txt_phon.find("Phones")
        tier_tok = txt_tok.find("Tokens")

        self.assertEqual(len(tier_phon), len(tier_tok))
        for ann_phon, ann_tok in zip(tier_phon, tier_tok):
            print(ann_phon)
            print(ann_tok)
            self.assertEqual(len(ann_phon.get_labels()),
                             len(ann_tok.get_labels()))

    # -----------------------------------------------------------------------
    # Writer
    # -----------------------------------------------------------------------

    def test_serialize_textgrid_header(self):
        """Create a string with the header of the textgrid."""

        header = sppasTextGrid._serialize_textgrid_header(xmin=0.,
                                                          xmax=10.,
                                                          size=3)
        lines = header.split("\n")
        self.assertEqual(len(lines), 9)
        self.assertTrue('File type = "ooTextFile"' in lines[0])
        self.assertTrue('Object class = "TextGrid"' in lines[1])
        self.assertTrue('xmin = 0.' in lines[3])
        self.assertTrue('xmax = 10.' in lines[4])
        self.assertTrue('tiers? <exists>' in lines[5])
        self.assertTrue('size = 3' in lines[6])
        self.assertTrue('item []:' in lines[7])

    # -----------------------------------------------------------------------

    def test_serialize_tier_header(self):
        """Create the string with the header for a new tier."""

        tier = sppasTier('toto')
        with self.assertRaises(AioEmptyTierError):
            sppasTextGrid._serialize_tier_header(tier, 0)

        tier.create_annotation(sppasLocation(sppasPoint(10.)))
        header = sppasTextGrid._serialize_tier_header(tier, 1)
        lines = header.split("\n")
        self.assertEqual(len(lines), 7)
        self.assertTrue('item [1]:' in lines[0])
        self.assertTrue('class = "TextTier"' in lines[1])
        self.assertTrue('name = "toto"' in lines[2])
        self.assertTrue('xmin = 10.' in lines[3])
        self.assertTrue('xmax = 10.' in lines[4])
        self.assertTrue('intervals: size = 1' in lines[5])

        tier.create_annotation(sppasLocation(sppasPoint(20.)),
                               sppasLabel(sppasTag("T")))
        header = sppasTextGrid._serialize_tier_header(tier, 1)
        lines = header.split("\n")
        self.assertEqual(len(lines), 7)
        self.assertTrue('item [1]:' in lines[0])
        self.assertTrue('class = "TextTier"' in lines[1])
        self.assertTrue('name = "toto"' in lines[2])
        self.assertTrue('xmin = 10.' in lines[3])
        self.assertTrue('xmax = 20.' in lines[4])
        self.assertTrue('intervals: size = 2' in lines[5])

    # -----------------------------------------------------------------------

    def test_serialize_point_annotation(self):
        """Converts an annotation consisting of points to the TextGrid format."""

        ann = sppasAnnotation(sppasLocation(sppasPoint(0.881936360608634579)))
        ann_content = sppasTextGrid._serialize_point_annotation(ann, 3)
        lines = ann_content.split("\n")
        self.assertEqual(len(lines), 4)
        self.assertTrue('points [3]:' in lines[0])
        self.assertTrue('time = 0.881936360' in lines[1])
        self.assertTrue('mark = ""' in lines[2])

# ---------------------------------------------------------------------------


class TestNumerical(unittest.TestCase):

    def test_members(self):
        tg = sppasBaseNumericalTier()
        self.assertFalse(tg.multi_tiers_support())
        self.assertFalse(tg.no_tiers_support())
        self.assertFalse(tg.metadata_support())
        self.assertFalse(tg.ctrl_vocab_support())
        self.assertFalse(tg.media_support())
        self.assertFalse(tg.hierarchy_support())
        self.assertTrue(tg.point_support())
        self.assertFalse(tg.interval_support())
        self.assertFalse(tg.disjoint_support())
        self.assertFalse(tg.alternative_localization_support())
        self.assertFalse(tg.alternative_tag_support())
        self.assertFalse(tg.radius_support())
        self.assertFalse(tg.gaps_support())
        self.assertFalse(tg.overlaps_support())

    # -----------------------------------------------------------------------

    def test_read(self):
        txt = sppasBaseNumericalTier()
        txt._read(os.path.join(DATA, "sample.PitchTier"))

        self.assertTrue(txt[0].is_point())
        self.assertTrue(txt[0].is_float())


# ---------------------------------------------------------------------------


class TestPitchTier(unittest.TestCase):

    def test_detect(self):
        """Test the file format detection method."""

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith(sppasPitchTier().default_extension):
                self.assertTrue(sppasPitchTier.detect(f))
            else:
                self.assertFalse(sppasPitchTier.detect(f))

    def test_to_pitch(self):
        p = sppasPitchTier()
        with self.assertRaises(AioNoTiersError):
            p.to_pitch()
        p.create_tier("toto")
        with self.assertRaises(AioNoTiersError):
            p.to_pitch()
        t = p.find('toto')
        t.set_name('PitchTier')
        with self.assertRaises(AioEmptyTierError):
            p.to_pitch()

        t.create_annotation(sppasLocation(sppasPoint(0.20440625000000007, 0.005)),
                            sppasLabel(sppasTag(172.05311434014578, "float")))
        t.create_annotation(sppasLocation(sppasPoint(0.24440625000000007, 0.005)),
                            sppasLabel(sppasTag(531.0482270311373, "float")))
        t.create_annotation(sppasLocation(sppasPoint(0.26440625000000006, 0.005)),
                            sppasLabel(sppasTag(526.6646688488254, "float")))

        result = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 172.053114,
                  261.801893, 351.550671, 441.299449,
                  531.048227, 528.856448, 526.664669]
        self.assertEqual(result, p.to_pitch())
