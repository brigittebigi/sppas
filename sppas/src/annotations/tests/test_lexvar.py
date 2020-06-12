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

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasInterval


from ..SelfRepet.datastructs import DataSpeaker
from ..SpkLexVar.sppaslexvar import sppasLexVar

# ---------------------------------------------------------------------------

class test_sppaslexvar(unittest.TestCase):

    def setUp(self):
        self.lexvar = sppasLexVar()
        self.lexvar.__sources = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]

        # tiers
        self.tier_spk1 = sppasTier()
        self.tier_spk2 = sppasTier()

        # annotations
        annot1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2))))
        annot2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2), sppasPoint(3))))
        annot3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))))
        annot4 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(5))))
        annot5 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(5), sppasPoint(6))))

        annot6 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(6), sppasPoint(7))))
        annot7 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(7), sppasPoint(8))))
        annot8 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(8), sppasPoint(9))))
        annot9 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(9), sppasPoint(10))))
        annot10 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(10), sppasPoint(11))))

        # tags
        tag1 = sppasTag("bonjour")
        tag2 = sppasTag("ca")
        tag3 = sppasTag("va")
        tag4 = sppasTag("bien")
        tag5 = sppasTag("toi")

        tag6 = sppasTag("salut")
        tag7 = sppasTag("oui")
        tag8 = sppasTag("ca")
        tag9 = sppasTag("va")
        tag10 = sppasTag("bien")

        # labels
        label1 = sppasLabel(tag1)
        label2 = sppasLabel(tag2)
        label3 = sppasLabel(tag3)
        label4 = sppasLabel(tag4)
        label5 = sppasLabel(tag5)

        label6 = sppasLabel(tag6)
        label7 = sppasLabel(tag7)
        label8 = sppasLabel(tag8)
        label9 = sppasLabel(tag9)
        label10 = sppasLabel(tag10)

        annot1.append_label(label1)
        annot2.append_label(label2)
        annot3.append_label(label3)
        annot4.append_label(label4)
        annot5.append_label(label5)

        self.tier_spk1.add(annot1)
        self.tier_spk1.add(annot2)
        self.tier_spk1.add(annot3)
        self.tier_spk1.add(annot4)
        self.tier_spk1.add(annot5)

        annot6.append_label(label6)
        annot7.append_label(label7)
        annot8.append_label(label8)
        annot9.append_label(label9)
        annot10.append_label(label10)

        self.tier_spk2.add(annot6)
        self.tier_spk2.add(annot7)
        self.tier_spk2.add(annot8)
        self.tier_spk2.add(annot9)
        self.tier_spk2.add(annot10)

        # browsing tests
        # --------------

        # for ann in self.tier_spk1:
        #     for label in ann.get_labels():
        #         for tag, score in label:
        #             print(tag)
        # print("\n")
        # for ann1 in self.tier_spk2:
        #     for label1 in ann1.get_labels():
        #         for tag1, score in label1:
        #             print(tag1)

    # -----------------------------------------------------------------------

    def test_contains(self):
        list1 = ["a", "b", "c", "d", "e", "f"]
        list2 = ["c", "d", "e"]
        list3 = [1, 21, 23]
        list4 = []
        tuple1 = ("b", "c", "d")
        list5 = [("a", "b"), ("c", "d"), ("e", "f")]
        list6 = [("c", "d")]
        list7 = ["a", "b", "c", "z"]

        self.assertTrue(self.lexvar.contains(list1, list2))
        self.assertFalse(self.lexvar.contains(list1, list3))
        # /!\ an empty list is always contained in an other list
        self.assertTrue(self.lexvar.contains(list1, list4))

        self.assertTrue(self.lexvar.contains(list5, list6))

        self.assertFalse(self.lexvar.contains(list1, tuple1))

        self.assertFalse(self.lexvar.contains(list1, list7))

    # -----------------------------------------------------------------------

    def test_window(self):
        sequence = ["a", "b", "c", "d", "e", "f"]
        sub2 = [(1, 45), (45, 4), (78, 9)]
        window_list = list()

        for window in self.lexvar.window(sequence, 3):
            window_list.append(window)
        for sub in window_list:
            self.assertTrue(self.lexvar.contains(sequence, list(sub)))
            self.assertFalse(self.lexvar.contains(sequence, sub2))

    # -----------------------------------------------------------------------

    def test_lexical_variation_detect(self):
        self.lexvar.lexical_variation_detect(self.tier_spk1, self.tier_spk2, 2)

    # -----------------------------------------------------------------------

    def test_get_longest(self):
        pass

    # -----------------------------------------------------------------------

    def test_select(self):
        dataspk1 = DataSpeaker(["oui", "ça", "va", "très", "bien"])
        dataspk2 = DataSpeaker(["oui", "ça", "va", "très", "bien"])
        self.lexvar.select(4, dataspk1, dataspk2)

    # -----------------------------------------------------------------------

    def test_content_listing(self):
        a = ["bonjour", "ca", "va", "bien", "toi"]
        content, time = self.lexvar.tier_content_listing(self.tier_spk1, True)
        self.assertEqual(a, content)

    # -----------------------------------------------------------------------

    def test_create_tier(self):
        content = ["bonjour", "ca", "va", "bien", "toi"]

        time_list = [sppasLocation(sppasPoint(1.)),
                     sppasLocation(sppasPoint(2.)),
                     sppasLocation(sppasPoint(3.)),
                     sppasLocation(sppasPoint(4.)),
                     sppasLocation(sppasPoint(5.))]

        lexvar = sppasLexVar()
        lexvar.__sources = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
        tier = lexvar.create_tier(content, time_list)








