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

    src.annotations.tests.test_lpc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the SPPAS LPC sgmts generator.

"""

import unittest
import os.path

from sppas.src.config import paths
from ..LPC.keyrules import KeyRules
from ..LPC.lpckeys import LPC
from ..LPC.sppaslpc import sppasLPC

# ---------------------------------------------------------------------------

FRA_KEYS = os.path.join(paths.resources, "lpc", "fra.txt")

# ---------------------------------------------------------------------------


class TestRules(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        # No file is defined
        rules = KeyRules()
        self.assertIsNone(rules.get_key("p"))
        self.assertIsNone(rules.get_key("#"))
        self.assertEqual(rules.get_class("p"), KeyRules.BREAK_SYMBOL)
        self.assertEqual(rules.get_class("#"), KeyRules.BREAK_SYMBOL)
        self.assertEqual(rules.get_class("cnil"), "C")
        self.assertEqual(rules.get_class("vnil"), "V")

        # A wrong file is given
        rules = KeyRules("toto.txt")
        self.assertIsNone(rules.get_key("p"))
        self.assertIsNone(rules.get_key("#"))
        self.assertEqual(rules.get_class("p"), KeyRules.BREAK_SYMBOL)
        self.assertEqual(rules.get_class("#"), KeyRules.BREAK_SYMBOL)

        # The expected file is given
        rules = KeyRules(FRA_KEYS)
        self.assertEqual(rules.get_class("p"), "C")
        self.assertEqual(rules.get_class("e"), "V")
        self.assertEqual(rules.get_class("#"), KeyRules.BREAK_SYMBOL)
        self.assertEqual(rules.get_key("p"), "1")
        self.assertEqual(rules.get_key("e"), "5")
        self.assertEqual(rules.get_key("#"), None)

    # -----------------------------------------------------------------------

    def test_load(self):
        rules = KeyRules()

        # Wrong filename
        result = rules.load("toto.txt")
        self.assertFalse(result)

        # No rule defined in the file
        result = rules.load(os.path.abspath(__file__))
        self.assertFalse(result)

        # A well-formed file
        result = rules.load(FRA_KEYS)
        self.assertTrue(result)
        self.assertEqual(rules.get_class("p"), "C")
        self.assertEqual(rules.get_class("e"), "V")
        self.assertEqual(rules.get_key("p"), "1")
        self.assertEqual(rules.get_key("e"), "5")

        self.assertEqual(rules.get_class("cnil"), "C")
        self.assertEqual(rules.get_class("vnil"), "V")
        self.assertEqual(rules.get_key("cnil"), "5")
        self.assertEqual(rules.get_key("vnil"), "0")

    # -----------------------------------------------------------------------

    def test_getters(self):
        rules = KeyRules()
        self.assertEqual(rules.get_nil_vowel(), "0")
        self.assertEqual(rules.get_nil_consonant(), "5")

        rules = KeyRules(FRA_KEYS)
        self.assertEqual(rules.get_nil_vowel(), "0")
        self.assertEqual(rules.get_nil_consonant(), "5")

    # -----------------------------------------------------------------------

    def test_get_keys(self):
        rules = KeyRules(FRA_KEYS)

        # well-formed syllables (C-V or C- or -V)

        keys = rules.get_syll_key("p-a")
        self.assertEqual(("1", "3"), keys)

        keys = rules.get_syll_key("p")
        self.assertEqual(("1", "0"), keys)

        keys = rules.get_syll_key("a")
        self.assertEqual(("5", "3"), keys)

        # badly-formed syllables

        with self.assertRaises(ValueError):
            rules.get_syll_key("")

        with self.assertRaises(ValueError):
            rules.get_syll_key("p-a-p")

        with self.assertRaises(ValueError):
            rules.get_syll_key("p-p")

        with self.assertRaises(ValueError):
            rules.get_syll_key("a-a")

        with self.assertRaises(ValueError):
            rules.get_syll_key("a-p")

# ---------------------------------------------------------------------------


class TestGenKeys(unittest.TestCase):

    def setUp(self):
        self.lpc = LPC(FRA_KEYS)

    # -----------------------------------------------------------------------

    def test_annotate_breaks(self):
        phonemes = list()
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, list())

        phonemes = ["#"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, list())

        phonemes = ["fp"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, list())

    # -----------------------------------------------------------------------

    def test_annotate_consonants(self):
        phonemes = ["p"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0)])

        phonemes = ["s", "p"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1)])

        phonemes = ["s", "p", "p"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1), (2, 2)])

        phonemes = ["s", "p", "#", "p"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1), (3, 3)])

        phonemes = ["#", "s", "p", "#", "p"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(1, 1), (2, 2), (4, 4)])

    # -----------------------------------------------------------------------

    def test_annotate_vowels(self):
        phonemes = ["a"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0)])

        phonemes = ["a", "e"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1)])

        phonemes = ["a", "e", "u"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1), (2, 2)])

        phonemes = ["a", "e", "#", "u"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1), (3, 3)])

        phonemes = ["#", "a", "e", "#", "u"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(1, 1), (2, 2), (4, 4)])

    # -----------------------------------------------------------------------

    def test_annotate_unknown(self):
        # Unknown phonemes are not coded!
        phonemes = ["X"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, list())

        phonemes = ["a", "X"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0)])

        phonemes = ["a", "X", "a"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 0), (2, 2)])

    # -----------------------------------------------------------------------

    def test_annotate(self):
        phonemes = ['b', 'O~', 'Z', 'u', 'r']
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 1), (2, 3), (4, 4)])

        phonemes = ['b', 'O~', '#', 'Z', 'u', 'r']
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 1), (3, 4), (5, 5)])

        phonemes = ['b', 'O~', 'fp', 'Z', 'u', 'r', "#"]
        sgmts = self.lpc.annotate(phonemes)
        self.assertEqual(sgmts, [(0, 1), (3, 4), (5, 5)])

    # -----------------------------------------------------------------------

    def test_phonetize(self):
        phonemes = ['b', 'O~', 'Z', 'u', 'R']
        sgmts = self.lpc.annotate(phonemes)
        phons = self.lpc.phonetize_syllables(phonemes, sgmts)
        self.assertEqual(phons, "b-O~.Z-u.R")

        phonemes = ['b', 'O~', 'fp', 'Z', 'u', 'R', "#"]
        sgmts = self.lpc.annotate(phonemes)
        phons = self.lpc.phonetize_syllables(phonemes, sgmts)
        self.assertEqual(phons, "b-O~.Z-u.R")

    # -----------------------------------------------------------------------

    def test_keys(self):
        phonemes = ['b', 'O~', 'Z', 'u', 'R']
        sgmts = self.lpc.annotate(phonemes)
        phons = self.lpc.phonetize_syllables(phonemes, sgmts)
        keys = self.lpc.keys_phonetized(phons)
        self.assertEqual(keys, "4-4.1-2.8-0")

        phonemes = ['b', 'O~', 'fp', 'Z', 'u', 'R', "#"]
        sgmts = self.lpc.annotate(phonemes)
        phons = self.lpc.phonetize_syllables(phonemes, sgmts)
        keys = self.lpc.keys_phonetized(phons)
        self.assertEqual(keys, "4-4.1-2.8-0")

# ---------------------------------------------------------------------------


class TestRunLPC(unittest.TestCase):

    def setUp(self):
        self.lpc = sppasLPC()
        self.lpc.load_resources(FRA_KEYS)


