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


from ..SpkLexVar.sppaslexvar import sppasLexVar

# ---------------------------------------------------------------------------


class test_sppaslexvar(unittest.TestCase):
    def setUp(self):
        self.lexvar = sppasLexVar()

        # creating the tier list
        # ----------------------

        # here is how our tier list look like
        # -tier_spk1 (str)
        #     -annot1
        #         -label1
        #             -tag1
        #             -tag2
        #     -annot2
        #         -label2
        #             -tag3
        #             -tag4
        #     -annot3
        #         -label3
        #             -tag5
        #             -tag6
        # -tier_spk2 (int)
        #     -annot4
        #         -label4
        #             -tag7
        #             -tag8
        #     -annot5
        #         -label5
        #             -tag9
        #     -annot6
        #         -label6
        #             -tag10
        #         -label7
        #             -tag11

        # tiers
        self.tier_spk1 = sppasTier()
        self.tier_spk2 = sppasTier()

        # annotations
        annot1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2))))
        annot2 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(2), sppasPoint(3))))
        annot3 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))))

        annot4 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(5))))
        annot5 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(6))))
        annot6 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(7))))

        # tags
        tag1 = sppasTag("bonjour")
        tag2 = sppasTag("bonsoir")
        tag3 = sppasTag("@")
        tag4 = sppasTag("#")
        tag5 = sppasTag("é")
        tag6 = sppasTag("è")

        tag7 = sppasTag(789)
        tag8 = sppasTag(9)
        tag9 = sppasTag(422)
        tag10 = sppasTag(4)
        tag11 = sppasTag(27)

        # labels
        label1 = sppasLabel([tag1, tag2])

        label2 = sppasLabel(tag3)
        label2.append(tag4)

        label3 = sppasLabel([tag5, tag6])

        label4 = sppasLabel([tag7, tag8])

        label5 = sppasLabel(tag9)
        label6 = sppasLabel(tag10)
        label7 = sppasLabel(tag11)

        annot1.append_label(label1)
        annot2.append_label(label2)
        annot3.append_label(label3)

        self.tier_spk1.add(annot2)
        self.tier_spk1.add(annot1)
        self.tier_spk1.add(annot3)

        annot4.append_label(label4)
        annot5.append_label(label5)
        annot6.append_label(label6)
        annot6.append_label(label7)
        self.tier_spk2.add(annot4)
        self.tier_spk2.add(annot5)
        self.tier_spk2.add(annot6)

        # browsing tests
        # --------------

        for ann in self.tier_spk1:
            print("\n")
            for label in ann.get_labels():
                print(type(label))
                print(label)
                for elem in label:
                    print(type(elem[0]))
                    label.set_score(elem[0], 10000)
                    print(elem[0])
                print(label)
                print("\n")
        print("\n")
        for ann in self.tier_spk2:
            print(ann.get_labels())

    # -----------------------------------------------------------------------

    def test_detect(self):
        return