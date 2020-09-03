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

    src.annotations.tests.test_phonetize.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the SPPAS Phonetization.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

"""

import unittest
import os.path

from sppas.src.config import paths
from sppas.src.config import symbols
from sppas.src.config import annots

from sppas.src.resources.dictpron import sppasDictPron
from sppas.src.resources.mapping import sppasMapping
from sppas.src.anndata import sppasRW

from sppas.src.annotations.Phon.phonetize import sppasDictPhonetizer
from sppas.src.annotations.Phon.dagphon import sppasDAGPhonetizer
from sppas.src.annotations.Phon.phonunk import sppasPhonUnk
from sppas.src.annotations.Phon.sppasphon import sppasPhon

# ---------------------------------------------------------------------------

SIL = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]
SP = list(symbols.phone.keys())[list(symbols.phone.values()).index("pause")]
SP_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("pause")]

# ---------------------------------------------------------------------------


class TestDictPhon(unittest.TestCase):
    """Test sppasDictPhonetizer: a dictionary-based phonetization."""

    def setUp(self):
        self.dd = sppasDictPron()
        self.grph = sppasDictPhonetizer(self.dd)
        self.dd.add_pron("a", "a")
        self.dd.add_pron("b", "b")
        self.dd.add_pron("c", "c")
        self.dd.add_pron(SP_ORTHO, SP)

    # -----------------------------------------------------------------------

    def test_get_phon_entry(self):
        """... Phonetization of an entry."""

        # a silence
        self.assertEqual(SIL, self.grph.get_phon_entry("gpf_1"))
        self.assertEqual(SIL, self.grph.get_phon_entry("gpf_1 "))
        self.assertEqual(SIL, self.grph.get_phon_entry(" gpf_13 "))

        # an unknown entry
        self.assertEqual(self.grph.get_phon_entry("ipu"), symbols.unk)
        self.assertEqual(self.grph.get_phon_entry("gpd"), symbols.unk)
        self.assertEqual(self.grph.get_phon_entry("gpf"), symbols.unk)
        self.assertEqual(self.grph.get_phon_entry("aa"), symbols.unk)
        self.assertEqual(self.grph.get_phon_entry("a-a"), symbols.unk)

        # a filled entry
        self.assertEqual("a", self.grph.get_phon_entry("a"))
        self.assertEqual("", self.grph.get_phon_entry("<>"))
        self.assertEqual("a", self.grph.get_phon_entry("<a>"))
        self.assertEqual("", self.grph.get_phon_entry("gpd_1"))
        self.assertEqual("", self.grph.get_phon_entry("ipu_1"))

    # -----------------------------------------------------------------------

    def test_get_phon_tokens(self):
        """... Phonetization of a list of tokens, with the status returned."""

        self.assertEqual([], self.grph.get_phon_tokens([' \n \t']))

        self.assertEqual([('a', 'a', annots.ok)],
                         self.grph.get_phon_tokens(['a']))

        self.assertEqual([('gpf_1', SIL, annots.ok)],
                         self.grph.get_phon_tokens(['gpf_1']))

        self.assertEqual([], self.grph.get_phon_tokens(['gpd_1']))

        self.assertEqual([('a', 'a', annots.ok), ('b', 'b', annots.ok)],
                         self.grph.get_phon_tokens(['a', 'b']))

        self.assertEqual([('a-a', 'a-a', annots.warning), ('b', 'b', annots.ok)],
                         self.grph.get_phon_tokens(['a-a', 'b']))

        self.assertEqual([('a-', 'a', annots.warning)],
                         self.grph.get_phon_tokens(['a-']))

        self.assertEqual([('A', 'a', annots.ok), ('B', 'b', annots.ok)],
                         self.grph.get_phon_tokens(['A', 'B']))

        self.assertEqual([('a', 'a', annots.ok), ('aa', 'a-a', annots.warning)],
                         self.grph.get_phon_tokens(['a', 'aa']))

        self.assertEqual([('a', 'a', annots.ok), ('aa', symbols.unk, annots.error)],
                         self.grph.get_phon_tokens(['a', 'aa'], phonunk=False))

        self.assertEqual([('a', 'a', annots.ok), ('d', symbols.unk, annots.error)],
                         self.grph.get_phon_tokens(['a', 'd']))

        self.assertEqual([('/a/', 'a', annots.ok), ('d', symbols.unk, annots.error)],
                         self.grph.get_phon_tokens(['/a/', 'd']))

        self.assertEqual([('/A-a/', 'A-a', annots.ok), ('d', symbols.unk, annots.error)],
                         self.grph.get_phon_tokens(['/A-a/', 'd']))

    # -----------------------------------------------------------------------

    def test_phonetize(self):
        """... Phonetization of an utterance."""

        with self.assertRaises(TypeError):
            self.grph.phonetize('A', delimiter="_-")

        self.assertEqual("", self.grph.phonetize(' \n \t'))
        self.assertEqual("a", self.grph.phonetize('a'))
        self.assertEqual("a b a c", self.grph.phonetize('a b a c'))
        self.assertEqual("a b a c "+symbols.unk, self.grph.phonetize('a b a c d'))
        self.assertEqual("a sp a", self.grph.phonetize('a + a'))
        self.assertEqual("a b c", self.grph.phonetize('A B C'))
        self.assertEqual("a_b_c", self.grph.phonetize('A_B_C', delimiter="_"))
        self.assertEqual("a-b-a c", self.grph.phonetize("a'b-a c"))
        self.assertEqual("a-b-a c", self.grph.phonetize("ipu_4 a'b-a c"))
        self.assertEqual("a-b-a sp c", self.grph.phonetize("gpd_4 a'b-a + c"))
        self.assertEqual("a-a-b-a", self.grph.phonetize("gpd_4 aa'b-a"))
        self.assertEqual(SIL, self.grph.phonetize("gpf_4 "))

    # -----------------------------------------------------------------------

    def test_phonetize_with_map_table(self):
        """... Phonetization of an utterance if a sppasMapping() is fixed."""

        mapt = sppasMapping()
        mapt.add('a', 'A')
        mapt.add('b', 'B')
        mapt.add('b', 'v')
        mapt.add('a-c', 'a-C')
        self.grph.set_maptable(mapt)

        self.assertEqual("c", self.grph._map_phonentry("c"))

        self.assertEqual(set("a|A".split('|')),
                         set(self.grph._map_phonentry("a").split('|')))

        self.assertEqual(set("B|b|v".split('|')),
                         set(self.grph._map_phonentry("b").split('|')))

        self.assertEqual('c.c', self.grph._map_phonentry("c.c"))

        self.assertEqual(set('a-b|a-B|A-b|A-B|A-v|a-v'.split("|")),
                         set(self.grph._map_phonentry("a-b").split("|")))

        self.assertEqual(set("a-c|a-C".split("|")),
                         set(self.grph._map_phonentry("a-c").split("|")))

        self.assertEqual(set("a-c-A|a-c-a|a-C-A|a-C-a".split("|")),
                         set(self.grph._map_phonentry("a-c-a").split("|")))

        self.assertEqual(set("c-a-c|c-a-C".split("|")),
                         set(self.grph._map_phonentry("c-a-c").split("|")))

        mapt.add('a', 'a')
        mapt.add('b', 'b')
        mapt.add('c', 'c')
        self.assertEqual("c", self.grph._map_phonentry("c"))

        self.assertEqual(set("a|A".split('|')),
                         set(self.grph._map_phonentry("a").split('|')))

        self.assertEqual(set("B|b|v".split('|')),
                         set(self.grph._map_phonentry("b").split('|')))

        # reset the mapping table for the next tests...
        self.grph.set_maptable(None)

    # -----------------------------------------------------------------------

    def test_phon_from_loaded_data(self):
        """... Phonetization using real resource data."""

        dict_file = os.path.join(paths.resources, "dict", "eng.dict")
        map_table = os.path.join(paths.resources, "dict", "eng-fra.map")
        mapt = sppasMapping(map_table)
        dd = sppasDictPron(dict_file)
        grph = sppasDictPhonetizer(dd)

        self.assertEqual(set("D-@|D-V|D-i:".split('|')),
                         set(grph.get_phon_entry("THE").split('|')))

        self.assertEqual(set("3:r|U-r\\".split('|')),
                         set(grph.get_phon_entry("UR").split('|')))

        self.assertEqual(set("A-r\\|3:r".split('|')),
                         set(grph.get_phon_entry("ARE").split('|')))

        self.assertEqual(set("b-{-N-k".split('|')),
                         set(grph.get_phon_entry("BANC").split('|')))

        grph.set_maptable(mapt)
        grph.set_unk_variants(0)
        # DICT:   the [] D @   /    the(2) [] D V    /    the(3) [] D i:
        # MAP:    D z   /   i: i    /    V 9    /   V @
        self.assertEqual(set("D-@|D-V|D-i:|z-@|z-V|z-i:|D-i|z-i|D-9|z-9|z-@".split("|")),
                         set(grph.get_phon_entry("THE").split("|")))

        # DICT:  ur [] 3:r   /   ur(2) [] U r\
        # MAP:   3:r 9-R   /  U u   /    r\ R   /   r\ w
        self.assertEqual(set("3:r|U-r\\|9-R|u-r\\|U-R|U-w|u-R|u-w".split("|")),
                         set(grph.get_phon_entry("UR").split("|")))

        # DICT =   are [] A r\    /    are(2) [] 3:r
        # MAP:  r\ R   /   r\ w    /   3:r 9-R    / A a
        self.assertEqual(set("A-r\\|3:r|a-r\\|9-R|A-R|A-w|a-R|a-w".split("|")),
                         set(grph.get_phon_entry("ARE").split("|")))

# ---------------------------------------------------------------------------


class TestDAGPhon(unittest.TestCase):
    """Test phonetization of unknown entries with a DAG."""

    def setUp(self):
        self.dd = sppasDAGPhonetizer()

    # -----------------------------------------------------------------------

    def test_decompose(self):
        self.assertEqual(set("a|b".split('|')),
                         set(self.dd.decompose("a", "b").split('|')))

        self.assertEqual(set("a-b|A-b".split('|')),
                         set(self.dd.decompose("a|A b").split('|')))

        self.assertEqual(set("a|A|B|b".split('|')),
                         set(self.dd.decompose("a|A", "b|B").split('|')))

        result = "p1-p2-x3|p1-x2-x3|p1-p2-p3|p1-x2-p3"
        self.assertEqual(set(result.split("|")),
                         set(self.dd.decompose("p1 p2|x2 p3|x3").split("|")))

        result = 'p1-p2-p3|x1-x2-x3'
        self.assertEqual(set(result.split("|")),
                         set(self.dd.decompose("p1 p2 p3", "x1 x2 x3").split("|")))

        result = 'p1-p2-p3|p1-x2-p3|x1-x2-x3'
        self.assertEqual(set(result.split("|")),
                         set(self.dd.decompose("p1 p2|x2 p3", "x1 x2 x3").split("|")))

# ---------------------------------------------------------------------------


class TestPhonUnk(unittest.TestCase):
    """Unknown words phonetization."""

    def setUp(self):
        d = {'a': 'a|aa',
             'b': 'b',
             'c': 'c|cc',
             'abb': 'abb',
             'bac': 'bac'
             }
        self.p = sppasPhonUnk(d)

    # -----------------------------------------------------------------------

    def test_phon(self):
        """... Phonetization of an unknown entry."""

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon('abba').split('|')))

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon('abba-').split('|')))

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon("abba'").split('|')))

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon("<abba>").split('|')))

        self.assertEqual("",
                         self.p.get_phon("<>"), "")

        self.assertEqual(set("abb-a|abb-aa".split('|')),
                         set(self.p.get_phon("abb-a").split('|')))

        self.assertEqual(set('a-b-c|a-b-cc|aa-b-c|aa-b-cc'.split('|')),
                         set(self.p.get_phon('abc').split('|')))

        self.assertEqual(set('a-b|aa-b'.split('|')),
                         set(self.p.get_phon('abd').split('|')))


# ---------------------------------------------------------------------------


class TestPhonetization(unittest.TestCase):
    """Test the SPPAS integration of the Phonetization."""

    def setUp(self):
        dict_file = os.path.join(paths.resources, "dict", "eng.dict")
        map_file = os.path.join(paths.resources, "dict", "eng-fra.map")
        self.sp = sppasPhon()
        self.sp.load_resources(dict_filename=dict_file)
        self.spl = sppasPhon()
        self.spl.load_resources(dict_filename=dict_file, map_filename=map_file)

    # -----------------------------------------------------------------------

    def test_phonetize(self):
        """... Phonetization of an utterance."""

        self.sp.set_unk(True)
        self.assertEqual([symbols.unk], self.sp._phonetize("é à"))

        self.assertEqual(set("D-@|D-V|D-i:".split('|')),
                         set(self.sp._phonetize("THE")[0].split('|')))

        self.assertEqual("h-i:",
                         self.sp._phonetize("HE")[0])

        self.sp.set_unk(False)  # do not try to phonetize if missing of the dict
        self.assertEqual([symbols.unk], self.sp._phonetize("THE BANCI THE"))

        self.sp.set_unk(True)

        # an utterance made only of a silence.
        self.assertEqual([SIL], self.sp._phonetize("#"))
        self.assertEqual([SIL], self.sp._phonetize("+"))
        self.assertEqual([SIL], self.sp._phonetize("  gpf_12  "))
        self.assertEqual([SIL], self.sp._phonetize("   gpd_1   +  "))

    # -----------------------------------------------------------------------

    def test_phonetize_learners(self):
        """... Phonetization of an utterance with a map table defined."""

        self.assertEqual(set("D-@|D-V|D-i:|z-@|z-V|z-i:|D-i|z-i|D-9|z-9|z-@".split('|')),
                         set(self.spl._phonetize("THE")[0].split('|')))

        self.assertEqual(set("i|h-i:|h-i|i:".split("|")),
                         set(self.spl._phonetize("HE")[0].split('|')))

    # -----------------------------------------------------------------------

    def test_samples(self):
        """... Compare the current result is the same as the existing one."""
        # Test the automatic annotation with its default parameters only.

        # the place where are the samples to be tested.
        samples_path = os.path.join(paths.samples, "annotation-results")

        # each samples folder is tested
        for samples_folder in os.listdir(samples_path):
            if samples_folder.startswith("samples-") is False:
                continue

            # Create a Phonetizer for the given set of samples of the given language
            lang = samples_folder[-3:]
            pron_dict = os.path.join(paths.resources, "dict", lang+".dict")
            tn = sppasPhon()
            tn.load_resources(dict_filename=pron_dict)

            # Apply Phonetization on each sample
            for filename in os.listdir(os.path.join(samples_path, samples_folder)):
                if filename.endswith("-token.xra") is False:
                    continue

                # Get the expected result
                expected_result_filename = os.path.join(samples_path, samples_folder,
                                                        filename[:-10] + "-phon.xra")
                if os.path.exists(expected_result_filename) is False:
                    print("no match token/phon for:", filename)
                    continue
                parser = sppasRW(expected_result_filename)
                expected_result = parser.read()

                # Estimate the result and check if it's like expected.
                input_file = os.path.join(samples_path, samples_folder, filename)
                result = tn.run([input_file])

                expected_tier_phones = expected_result.find('Phones')
                if expected_tier_phones is not None:
                    self.compare_tiers(expected_tier_phones, result.find('Phones'))

    # -----------------------------------------------------------------------

    def compare_tiers(self, expected, result):
        self.assertEqual(len(expected), len(result))
        for a1, a2 in zip(expected, result):
            self.assertEqual(a1.get_location(), a2.get_location())
            self.assertEqual(len(a1.get_labels()), len(a2.get_labels()))
            for l1, l2 in zip(a1.get_labels(), a2.get_labels()):
                self.assertEqual(l1, l2)
            for key in a1.get_meta_keys():
                if key != 'id':
                    self.assertEqual(a1.get_meta(key), a2.get_meta(key))
        for key in expected.get_meta_keys():
            if key != 'id':
                self.assertEqual(expected.get_meta(key), result.get_meta(key))
