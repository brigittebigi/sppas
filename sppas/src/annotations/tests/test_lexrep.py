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

    src.annotations.tests.test_lexrep.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
    :summary:      Test the SPPAS LexRep automatic annotation.

"""

import unittest

from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasInterval

from ..SelfRepet.datastructs import DataSpeaker
from ..SpkLexRep.sppaslexrep import sppasLexRep
from ..SpkLexRep.sppaslexrep import LexReprise

# ---------------------------------------------------------------------------


class test_sppasLexReprise(unittest.TestCase):

    def test_eq(self):
        r1 = LexReprise(1, 3)
        r2 = LexReprise(1, 5)
        r3 = LexReprise(1, 3)
        reprises = [r1, r2, r3]

        self.assertEqual(r1, r3)
        self.assertNotEqual(r1, r2)
        self.assertEqual(r1, (1, 3))
        self.assertNotEqual(r1, (1, 4))

        self.assertTrue(r1 in reprises)
        self.assertTrue((1, 3) in reprises)
        self.assertFalse(1 in reprises)

# ---------------------------------------------------------------------------


class test_sppasLexRep(unittest.TestCase):

    def setUp(self):

        # tiers
        self.tier_spk1 = sppasTier()
        self.tier_spk2 = sppasTier()

        # annotations
        self.content1 = ["bonjour", "ca", "va", "bien", "toi"]
        self.content2 = ["salut", "oui", "ca", "va", "bien"]
        self.loc1 = list()
        for i, c in enumerate(self.content1):
            loc = sppasLocation(sppasInterval(sppasPoint(float(i)), sppasPoint(float(i) + 1.)))
            self.loc1.append(loc)
            self.tier_spk1.create_annotation(loc, sppasLabel(sppasTag(c)))
        for i, c in enumerate(self.content2):
            self.tier_spk2.create_annotation(
                sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))),
                sppasLabel(sppasTag(c)))

    # -----------------------------------------------------------------------

    def test_init(self):
        lex = sppasLexRep()
        self.assertEqual(lex._options["span"], 10)
        self.assertEqual(lex._options["spandur"], 3.)

    # -----------------------------------------------------------------------

    def test_tier_to_list(self):
        content, loc = sppasLexRep.tier_to_list(self.tier_spk1, True)
        self.assertEqual(self.content1, content)
        self.assertEqual(self.loc1, loc)

        content, loc = sppasLexRep.tier_to_list(self.tier_spk2, False)
        self.assertEqual(self.content2, content)
        self.assertEqual(0, len(loc))

    # -----------------------------------------------------------------------

    def test_get_longest(self):
        dataspk1 = DataSpeaker(["oui", "ça", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["toto", "oui", "ça"])
        self.assertEqual(sppasLexRep.get_longest(dataspk1, dataspk2), 1)
        self.assertEqual(sppasLexRep.get_longest(dataspk2, dataspk1), -1)
        self.assertEqual(sppasLexRep.get_longest(dataspk2, dataspk2), 2)

        # no matter if a non-speech event occurs in the middle of the
        # repeated sequence
        dataspk2 = DataSpeaker(["toto", "oui", "#", "ça", "va"])
        self.assertEqual(sppasLexRep.get_longest(dataspk1, dataspk2), 2)

        # no matter if a non-speech event occurs in the middle of the
        # source sequence
        dataspk1 = DataSpeaker(["oui", "#", "ça", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["toto", "oui", "ça"])
        self.assertEqual(sppasLexRep.get_longest(dataspk1, dataspk2), 2)

        # no matter if tokens are not repeated in the same order
        dataspk1 = DataSpeaker(["ça", "#", "oui", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["toto", "oui", "ça"])
        self.assertEqual(sppasLexRep.get_longest(dataspk1, dataspk2), 2)

        # no matter if tokens are not repeated in the same order
        dataspk1 = DataSpeaker(["ça", "va", "bien"])
        dataspk2 = DataSpeaker(["ça", "#", "va"])
        self.assertEqual(sppasLexRep.get_longest(dataspk1, dataspk2), 1)

    # -----------------------------------------------------------------------

    def test_select(self):
        lexvar = sppasLexRep()

        dataspk1 = DataSpeaker(["ça", "va", "très", "bien", "oui"])
        dataspk2 = DataSpeaker(["bonjour", "ça", "va", "très", "bien"])
        self.assertTrue(lexvar.select(4, dataspk1, dataspk2))

        dataspk1 = DataSpeaker(["oui", "oui", "oui", "ça", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["ah", "oui"])
        self.assertTrue(lexvar.select(2, dataspk1, dataspk2))

    # -----------------------------------------------------------------------

    def test_get_longest_selected(self):
        lexvar = sppasLexRep()

        dataspk1 = DataSpeaker(["ça", "va", "très", "bien", "oui"])
        dataspk2 = DataSpeaker(["bonjour", "ça", "va", "très", "bien"])
        self.assertEqual(3, lexvar._get_longest_selected(dataspk1, dataspk2))

        dataspk2 = DataSpeaker(["bonjour", "#", "non", "pas", "vraiment"])
        self.assertEqual(-1, lexvar._get_longest_selected(dataspk1, dataspk2))

        dataspk2 = DataSpeaker(["bien", "#", "oui"])
        self.assertEqual(-1, lexvar._get_longest_selected(dataspk1, dataspk2))

        dataspk2 = DataSpeaker(["ça", "#", "ça", "ça", "ça"])
        self.assertEqual(0, lexvar._get_longest_selected(dataspk1, dataspk2))

        dataspk2 = DataSpeaker(["ça", "#", "va", "xx", "xx"])
        self.assertEqual(1, lexvar._get_longest_selected(dataspk1, dataspk2))

    # -----------------------------------------------------------------------

    def test_add_source(self):
        dataspk = DataSpeaker(["bonjour", "#", "non", "pas", "vraiment", "non"])
        sources = list()
        sppasLexRep._add_source(sources, 1, 3, dataspk)
        self.assertEqual(len(sources), 1)
        self.assertTrue((1, 3) in sources)

        sppasLexRep._add_source(sources, 1, 5, dataspk)
        self.assertEqual(len(sources), 2)
        self.assertTrue((1, 5) in sources)

        sppasLexRep._add_source(sources, 1, 3, dataspk)
        self.assertEqual(len(sources), 2)
        self.assertTrue((1, 3) in sources)

    # -----------------------------------------------------------------------

    def test_detect_all_sources(self):
        dataspk1 = ["bonjour", "moi", "ca", "va", "bien", "#", "et", "toi", "ca", "ok", "#"]
        dataspk2 = ["oui", "toi", "#", "comment", "ca", "#", "va"]
        lexvar = sppasLexRep()
        lexvar.set_span(2)
        lexvar.set_span_duration(20)
        winspk1 = lexvar.windowing(dataspk1)
        winspk2 = lexvar.windowing(dataspk2)

        # in the other way
        sources = lexvar._detect_all_sources(winspk2, winspk1)
        self.assertEqual(len(sources), 2)

        self.assertTrue((1, 0) in sources)
        self.assertEqual("toi", serialize_labels(sources[0].get_labels(), " "))

        self.assertTrue((4, 2) in sources)
        self.assertEqual("ca # va", serialize_labels(sources[1].get_labels(), " "))

        # in one way
        sources = lexvar._detect_all_sources(winspk1, winspk2)
        self.assertEqual(len(sources), 3)

        self.assertTrue((2, 1) in sources)
        self.assertEqual("ca va", serialize_labels(sources[0].get_labels(), " "))

        self.assertTrue((7, 0) in sources)
        self.assertEqual("toi", serialize_labels(sources[1].get_labels(), " "))

        self.assertTrue((8, 0) in sources)
        self.assertEqual("ca", serialize_labels(sources[2].get_labels(), " "))

    # -----------------------------------------------------------------------

    def test_sources_identifiers(self):
        content = ["bonjour", "moi", "ca", "va", "bien", "#", "et", "toi", "ca", "va", "#"]
        dataspk = DataSpeaker(content)

        sources = list()
        sppasLexRep._add_source(sources, 1, 3, dataspk)    # moi ca va
        sppasLexRep._add_source(sources, 1, 6, dataspk)    # moi ca va bien # et
        sppasLexRep._add_source(sources, 1, 3, dataspk)    # moi ca va
        sppasLexRep._add_source(sources, 2, 4, dataspk)    # ca va bien
        sppasLexRep._add_source(sources, 8, 10, dataspk)   # ca va bien
        self.assertEqual(len(sources), 4)
        expected_keys = [(1, 3), (1, 6), (2, 4), (8, 10)]
        for expected in expected_keys:
            self.assertTrue(expected in sources)

        # (2,4) and (8,10) should be merged: they are corresponding to the same content

    # -----------------------------------------------------------------------

    def test_create_tier(self):
        sources = list()

        lexvar = sppasLexRep()
        lexvar.set_span(3)
        lexvar._add_source(sources, 1, 2, DataSpeaker(self.content1[1:4]))   # ca va bien

        tier_tok = lexvar.create_tier(sources, self.loc1)
        self.assertEqual(1, len(tier_tok))
        self.assertEqual("ca va bien", serialize_labels(tier_tok[0].get_labels(), " "))

        lexvar._add_source(sources, 4, 0, DataSpeaker(self.content1[4:5]))   # toi
        tier_tok = lexvar.create_tier(sources, self.loc1)
        self.assertEqual(2, len(tier_tok))
        self.assertEqual("ca va bien", serialize_labels(tier_tok[0].get_labels(), " "))
        self.assertEqual("toi", serialize_labels(tier_tok[1].get_labels(), " "))

    # -----------------------------------------------------------------------

    def test_windowing(self):
        lexvar = sppasLexRep()
        lexvar.set_span(3)
        lexvar.set_span_duration(5.)
        wins = lexvar.windowing(self.content1)
        self.assertEqual(len(wins), 5)
        for w in wins:
            self.assertEqual(3, len(w))
        wins = lexvar.windowing(self.content1, self.loc1)
        self.assertEqual(len(wins), 5)

        lexvar.set_span_duration(2.5)
        wins = lexvar.windowing(self.content1, self.loc1)
        self.assertEqual(len(wins), 5)

    # -----------------------------------------------------------------------

    def test_lexrep_detect(self):
        lexvar = sppasLexRep()
        lexvar.set_span(3)
        t1, t2 = lexvar.lexical_variation_detect(self.tier_spk1, self.tier_spk2)
        self.assertEqual(len(t1), 1)
        self.assertEqual(len(t2), 1)
        self.assertEqual(t1.get_name(), "LexRepContent-1")
        self.assertEqual(t2.get_name(), "LexRepContent-2")
        self.assertEqual("ca va bien", serialize_labels(t1[0].get_labels(), " "))
        self.assertEqual("ca va bien", serialize_labels(t2[0].get_labels(), " "))

