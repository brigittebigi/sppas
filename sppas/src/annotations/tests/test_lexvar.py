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

    src.annotations.tests.test_lexmetric.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
    :summary:      Test the SPPAS LexMetric automatic annotation.

"""

import unittest

from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasInterval

from sppas.src.utils import sppasCompare
from ..SelfRepet.datastructs import DataSpeaker
from ..SpkLexVar.sppaslexvar import sppasLexVar

# ---------------------------------------------------------------------------


class test_sppaslexvar(unittest.TestCase):

    def setUp(self):

        # tiers
        self.tier_spk1 = sppasTier()
        self.tier_spk2 = sppasTier()

        # annotations
        self.content1 = ["bonjour", "ca", "va", "bien", "toi"]
        self.content2 = ["salut", "oui", "ca", "va", "bien"]
        self.loc1 = list()
        for i, c in enumerate(self.content1):
            loc = sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i + 1)))
            self.loc1.append(loc)
            self.tier_spk1.create_annotation(loc, sppasLabel(sppasTag(c)))
        for i, c in enumerate(self.content2):
            self.tier_spk2.create_annotation(
                sppasLocation(sppasInterval(sppasPoint(i), sppasPoint(i+1))),
                sppasLabel(sppasTag(c)))

    # -----------------------------------------------------------------------

    def test_tier_to_list(self):
        content, loc = sppasLexVar.tier_to_list(self.tier_spk1, True)
        self.assertEqual(self.content1, content)
        self.assertEqual(self.loc1, loc)

        content, loc = sppasLexVar.tier_to_list(self.tier_spk2, False)
        self.assertEqual(self.content2, content)
        self.assertEqual(0, len(loc))

    # -----------------------------------------------------------------------

    def test_get_longest(self):
        dataspk1 = DataSpeaker(["oui", "ça", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["toto", "oui", "ça"])
        self.assertEqual(sppasLexVar.get_longest(dataspk1, dataspk2), 1)
        self.assertEqual(sppasLexVar.get_longest(dataspk2, dataspk1), -1)
        self.assertEqual(sppasLexVar.get_longest(dataspk2, dataspk2), 2)

        # no matter if a non-speech event occurs in the middle of the
        # repeated sequence
        dataspk2 = DataSpeaker(["toto", "oui", "#", "ça", "va"])
        self.assertEqual(sppasLexVar.get_longest(dataspk1, dataspk2), 2)

        # no matter if a non-speech event occurs in the middle of the
        # source sequence
        dataspk1 = DataSpeaker(["oui", "#", "ça", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["toto", "oui", "ça"])
        self.assertEqual(sppasLexVar.get_longest(dataspk1, dataspk2), 2)

        # no matter if tokens are not repeated in the same order
        dataspk1 = DataSpeaker(["ça", "#", "oui", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["toto", "oui", "ça"])
        self.assertEqual(sppasLexVar.get_longest(dataspk1, dataspk2), 2)

    # -----------------------------------------------------------------------

    def test_select(self):
        lexvar = sppasLexVar()

        dataspk1 = DataSpeaker(["ça", "va", "très", "bien", "oui"])
        dataspk2 = DataSpeaker(["bonjour", "ça", "va", "très", "bien"])
        self.assertTrue(lexvar.select(4, dataspk1, dataspk2))

        dataspk1 = DataSpeaker(["oui", "oui", "oui", "ça", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["ah", "oui"])
        self.assertTrue(lexvar.select(2, dataspk1, dataspk2))

    # -----------------------------------------------------------------------

    def test_get_longest_selected(self):
        lexvar = sppasLexVar()

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

    def test_detect_all_sources(self):
        pass

    # -----------------------------------------------------------------------

    def test_add_source(self):
        sources = dict()
        sppasLexVar._add_source(sources, 1, 3)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[(1, 3)], 1)
        sppasLexVar._add_source(sources, 1, 5)
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[(1, 5)], 1)
        sppasLexVar._add_source(sources, 1, 3)
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[(1, 3)], 2)

    # -----------------------------------------------------------------------

    def test_merge_sources(self):
        self.content1 = ["bonjour", "moi", "ca", "va", "bien", "#", "et", "toi", "ca" "va", "bien"]

        sources = dict()
        sppasLexVar._add_source(sources, 1, 3)    # moi ca va
        sppasLexVar._add_source(sources, 1, 6)    # moi ca va bien # et
        sppasLexVar._add_source(sources, 1, 3)    # moi ca va
        sppasLexVar._add_source(sources, 2, 4)    # ca va bien
        sppasLexVar._add_source(sources, 8, 10)   # ca va bien
        self.assertEqual(len(sources), 4)
        expected_keys = [(1, 3), (1, 6), (2, 4), (8, 10)]
        for expected in expected_keys:
            self.assertTrue(expected in sources)

        # (2,4) and (8,10) should be merged: they are corresponding to the same content

    # -----------------------------------------------------------------------

    def test_create_tier(self):
        sources = dict()
        sources[(1, 3)] = 1
        lexvar = sppasLexVar()
        tier_tok, tier_occ = lexvar.create_tier(sources, self.content1, self.loc1)
        self.assertEqual(1, len(tier_tok))
        self.assertEqual(1, len(tier_occ))
        self.assertEqual("ca va bien", serialize_labels(tier_tok[0].get_labels(), " "))
        self.assertEqual("1", serialize_labels(tier_occ[0].get_labels(), " "))



