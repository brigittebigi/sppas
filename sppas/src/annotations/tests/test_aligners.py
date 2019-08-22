# -*- coding: utf8 -*-
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

    src.annotations.tests.test_aligners.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os

from sppas.src.config import paths

from ..Align.aligners import sppasAligners
from ..Align.aligners.basealigner import BaseAligner
from ..Align.aligners.basicalign import BasicAligner
from ..Align.aligners.juliusalign import JuliusAligner
from ..Align.aligners.hvitealign import HviteAligner
from ..Align.aligners.alignerio import BaseAlignersReader
from ..Align.aligners.alignerio import palign, walign, mlf

# ---------------------------------------------------------------------------

MODELDIR = os.path.join(paths.resources, "models")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestAlignersIO(unittest.TestCase):
    """Readers/writer of the output files of the aligners."""

    def test_BaseAlignersReader(self):
        b = BaseAlignersReader()
        self.assertEqual('', b.extension)
        with self.assertRaises(NotImplementedError):
            b.read('toto')

    def test_getlines(self):
        b = BaseAlignersReader()
        lines = b.get_lines(os.path.join(DATA, "track_000002.palign"))
        self.assertEqual(311, len(lines))

    def test_get_time_units_palign(self):
        b = BaseAlignersReader()
        lines = b.get_lines(os.path.join(DATA, "track_000002.palign"))
        expected_units = [(0, 2), (3, 5), (6, 15), (16, 22), (23, 31),\
                          (32, 34), (35, 37), (38, 40), (41, 60), (61, 63),\
                          (64, 69), (70, 75), (76, 80), (81, 84), (85, 102),\
                          (103, 108), (109, 120), (121, 127), (128, 137),\
                          (138, 141), (142, 145), (146, 155), (156, 167),\
                          (168, 175), (176, 187), (188, 193), (194, 196),\
                          (197, 208), (209, 214), (215, 227), (228, 236),\
                          (237, 240), (241, 252), (253, 264), (265, 282)]

        units = b.get_units_julius(lines)
        self.assertEqual(expected_units, units)
        units = b.units_to_time(units, 100)
        self.assertEqual(0., units[0][0])
        self.assertEqual(0.03, units[0][1])
        self.assertEqual(2.65, units[-1][0])
        self.assertEqual(2.82, units[-1][1])

    def test_shift_time_units(self):
        units = [(0., 0.03), (0.03, 1.)]
        shifted = BaseAlignersReader.shift_time_units(units, 0.01)
        self.assertEqual([(0., 0.04), (0.04, 1.)], shifted)
        shifted = BaseAlignersReader.shift_time_units(shifted, -0.01)
        self.assertEqual(units, shifted)

    def test_get_words_julius_phonemes(self):
        b = BaseAlignersReader()
        lines = b.get_lines(os.path.join(DATA, "track_000002.palign"))
        phonemes = b.get_phonemes_julius(lines)
        words = b.get_words_julius(lines)
        scores = b.get_word_scores_julius(lines)
        self.assertEqual(11, len(words))
        self.assertEqual(11, len(phonemes))
        self.assertEqual(11, len(scores))

    def test_read_palign(self):
        b = palign()
        self.assertEqual("palign", b.extension)
        expected_tokens = \
            [(0.0, 0.07, 'the', None), (0.07, 0.36, 'flight', None),\
             (0.36, 0.62, 'was', None), (0.62, 0.86, 'twelve', None),\
             (0.86, 1.22, 'hours', None), (1.22, 1.43, 'long', None),\
             (1.43, 1.57, 'and', None), (1.57, 1.77, 'we', None),\
             (1.77, 2.1, 'really', None), (2.10, 2.38, 'got', None),\
             (2.38, 2.82, 'bored', None)]

        phones, tokens, prons = b.read(os.path.join(DATA, "track_000002.palign"))
        self.assertEqual(expected_tokens, tokens)
        self.assertEqual(len(expected_tokens), len(prons))
        self.assertEqual(35, len(phones))
        self.assertEqual((0., 0.07, 'dh-ax', '0.618'), prons[0])
        self.assertEqual((1.43, 1.57, 'n-d', '0.510'), prons[6])

    def test_read_walign(self):
        b = walign()
        self.assertEqual("walign", b.extension)
        tokens = b.read(os.path.join(DATA, "track_000000.walign"))
        self.assertEqual(21, len(tokens))
        self.assertEqual((0.21, 0.38, '感', '0.306'), tokens[1])

    def test_get_time_units_mlf(self):
        b = mlf()
        lines = b.get_lines(os.path.join(DATA, "track_sample.mlf"))
        expected_units = [
            (0, 200000), (200000, 400000), (400000, 800000),\
            (800000, 1200000), (1200000, 1500000), (1500000, 1800000),\
            (1800000, 1900000), (1900000, 2400000), (2400000, 2800000)]
        units = b.get_units(lines)
        self.assertEqual(expected_units, units)
        units = b.units_to_time(units, 10e6)
        self.assertEqual(0., units[0][0])
        self.assertEqual(0.02, units[0][1])
        self.assertEqual(0.28, units[-1][1])

    def test_get_phonemes_mlf(self):
        b = mlf()
        lines = b.get_lines(os.path.join(DATA, "track_sample.mlf"))
        phonemes = b.get_phonemes(lines)
        words = b.get_words(lines)
        self.assertEqual(3, len(phonemes))
        self.assertEqual(3, len(words))

    def test_read_mlf(self):
        b = mlf()
        self.assertEqual("mlf", b.extension)
        phones, tokens, prons = b.read(os.path.join(DATA, "track_sample.mlf"))
        expected_tokens = \
            [(0.0, 0.09, 'h#', None),\
             (0.09, 0.19, 'q', None),\
             (0.19, 0.28, 'iy', None)]
        self.assertEqual(expected_tokens, tokens)
        self.assertEqual(len(expected_tokens), len(prons))
        self.assertEqual((0., 0.09, 'h#_s2-h#_s3-h#_s4', None), prons[0])
        self.assertEqual(9, len(phones))

# ---------------------------------------------------------------------------


class TestAligners(unittest.TestCase):
    """Manager of the aligners implemented in the package."""

    def test_check(self):
        """Check whether the aligner name is known or not."""
        aligners = sppasAligners()
        for a in aligners.names():
            self.assertEqual(a, aligners.check(a))

        with self.assertRaises(KeyError):
            aligners.check("invalid")

    # -----------------------------------------------------------------------

    def test_instantiate(self):
        """Instantiate an aligner to the appropriate Aligner system."""
        aligners = sppasAligners()
        for a in aligners.names():
            aligner = aligners.instantiate(None, a)
            self.assertTrue(isinstance(aligner,
                                       aligners.classes(a)))

        with self.assertRaises(KeyError):
            aligners.instantiate(None, "invalid")

# ---------------------------------------------------------------------------


class TestBaseAligner(unittest.TestCase):
    """Base class for any automatic alignment system."""

    def setUp(self):
        self._aligner = BaseAligner()

    def test_get_members(self):
        self.assertEqual("", self._aligner.outext())
        self.assertEqual(list(), self._aligner.extensions())
        self.assertEqual("", self._aligner.name())
    #
    # def test_infersp(self):
    #     self.assertFalse(self._aligner.get_infersp())
    #     self._aligner.set_infersp(True)
    #     self.assertTrue(self._aligner.get_infersp())
    #     self._aligner.set_infersp("ejzkjg")
    #     self.assertFalse(self._aligner.get_infersp())

    def test_norun(self):
        with self.assertRaises(NotImplementedError):
            self._aligner.run_alignment("audio", "output")

    def test_set_data(self):
        # tokens and phones must be strings
        with self.assertRaises(Exception):
            self._aligner.set_phones(3)
        with self.assertRaises(Exception):
            self._aligner.set_tokens(3)

        # tokens matching phones
        self._aligner.set_phones("a b c")
        self._aligner.set_tokens("w1 w2 w3")
        self.assertEqual("", self._aligner.check_data())  # no error msg
        self.assertEqual("w1 w2 w3", self._aligner._tokens)

        # tokens not matching phones
        self._aligner.set_tokens("w1www")
        self.assertTrue(len(self._aligner.check_data()) > 20)  # error msg
        self.assertEqual("w_0 w_1 w_2", self._aligner._tokens)

# ---------------------------------------------------------------------------


class TestBasicAlign(unittest.TestCase):
    """Basic automatic alignment system."""

    def setUp(self):
        self._aligner = BasicAligner()

    def test_run_basic(self):

        self._aligner.set_phones("")
        self.assertEqual([(0, 0, "")], self._aligner.run_basic(0.))
        self.assertEqual([(0, 1, "")], self._aligner.run_basic(0.01))
        self.assertEqual([(0, 2, "")], self._aligner.run_basic(0.02))
        self.assertEqual([(0, 20, "")], self._aligner.run_basic(0.2))
        self.assertEqual([(0, 1000, "")], self._aligner.run_basic(10.))

        self._aligner.set_phones("a")
        self.assertEqual([(0, 0, "")], self._aligner.run_basic(0.))
        self.assertEqual([(0, 1, "a")], self._aligner.run_basic(0.02))
        self.assertEqual([(0, 1, "a")], self._aligner.run_basic(0.02))

        self._aligner.set_phones("a b c")
        self.assertEqual([(0, 2, "")], self._aligner.run_basic(0.02))

        self._aligner.set_phones("a b")
        self.assertEqual([(0, 9, "a"), (10, 19, "b")],
                          self._aligner.run_basic(0.2))

        self._aligner.set_phones("a|aa b|bb")
        self.assertEqual([(0, 9, "a"), (10, 19, "b")],
                          self._aligner.run_basic(0.2))

        self._aligner.set_phones("a|A b|B")
        self.assertEqual([(0, 9, "a"), (10, 19, "b")],
                          self._aligner.run_basic(0.2))

# ---------------------------------------------------------------------------


class TestJuliusAlign(unittest.TestCase):

    def setUp(self):
        self._modeldir = os.path.join(MODELDIR, "models-fra")
        self._aligner = JuliusAligner(self._modeldir)

# ---------------------------------------------------------------------------


class TestHviteAlign(unittest.TestCase):

    def setUp(self):
        self._modeldir = os.path.join(MODELDIR, "models-fra")
        self._aligner = HviteAligner(self._modeldir)
