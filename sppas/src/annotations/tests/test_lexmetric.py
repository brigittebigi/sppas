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

from ..LexMetric.occrank import OccRank

# ---------------------------------------------------------------------------


class TestOccRank(unittest.TestCase):
    """Test of the class OccRank

    """

    def test_create(self):
        """... Test initialize."""
        with self.assertRaises(TypeError):
             OccRank(tier="toto")

    def test_alt(self):
        """... Test get and set of the option alt."""
        ocrk = OccRank(sppasTier("test"))
        self.assertTrue(ocrk.get_use_alt())

        ocrk.set_use_alt(False)
        self.assertFalse(ocrk.get_use_alt())

    def test_occ(self):
        """... Test estimation of occurrences."""
        ocrk = OccRank(sppasTier("test"), alt=True)
        occ_tier = ocrk.occ()
        self.assertEqual(0, len(occ_tier))

        # Test a tier without / with one or more labels.
        tier = sppasTier("")
        tier.create_annotation(sppasLocation(sppasPoint(1)))
        tier.create_annotation(sppasLocation(sppasPoint(2)), [])
        tier.create_annotation(sppasLocation(sppasPoint(3)), sppasLabel(sppasTag("a")))
        tier.create_annotation(sppasLocation(sppasPoint(4)),
                               [sppasLabel(sppasTag("a")), sppasLabel(sppasTag("b"))])

        ocrk = OccRank(tier, alt=True)
        occ_tier = ocrk.occ()
        self.assertEqual(2, len(occ_tier))
        # sppasPoint(3)=a
        self.assertEqual(2, occ_tier[0].get_best_tag().get_typed_content())
        # sppasPoint(4), label1=a
        self.assertEqual(2, occ_tier[1].get_best_tag(0).get_typed_content())
        # sppasPoint(4), label2=b
        self.assertEqual(1, occ_tier[1].get_best_tag(1).get_typed_content())

        # Test a tier with one or more labels, with alternative tags.
        tier.create_annotation(sppasLocation(sppasPoint(5)),
                               sppasLabel([sppasTag("a"), sppasTag("c")], [0.2, 0.8]))
        tier.create_annotation(sppasLocation(sppasPoint(6)),
                               [sppasLabel([sppasTag("c"), sppasTag("a")], [0.8, 0.2])])

        ocrk = OccRank(tier, alt=True)
        occ_tier = ocrk.occ()
        self.assertEqual(4, len(occ_tier))
        # sppasPoint(3)=a
        self.assertEqual(4, occ_tier[0].get_best_tag().get_typed_content())
        # sppasPoint(4), label1=a
        self.assertEqual(4, occ_tier[1].get_best_tag(0).get_typed_content())
        # sppasPoint(4), label2=b
        self.assertEqual(1, occ_tier[1].get_best_tag(1).get_typed_content())
        # sppasPoint(5), label=tag1=a
        self.assertEqual(4, occ_tier[2].get_labels()[0][0][0].get_typed_content())
        # sppasPoint(5), label=tag2=c
        self.assertEqual(2, occ_tier[2].get_labels()[0][1][0].get_typed_content())
        # sppasPoint(6), label=tag1=c
        self.assertEqual(2, occ_tier[3].get_labels()[0][0][0].get_typed_content())
        # sppasPoint(5), label=tag2=a
        self.assertEqual(4, occ_tier[3].get_labels()[0][1][0].get_typed_content())

        ocrk.set_use_alt(False)
        occ_tier = ocrk.occ()
        self.assertEqual(4, len(occ_tier))
        # sppasPoint(3)=a
        self.assertEqual(2, occ_tier[0].get_best_tag().get_typed_content())
        # sppasPoint(4), label1=a
        self.assertEqual(2, occ_tier[1].get_best_tag(0).get_typed_content())
        # sppasPoint(4), label2=b
        self.assertEqual(1, occ_tier[1].get_best_tag(1).get_typed_content())
        # sppasPoint(5), label=c
        self.assertEqual(2, occ_tier[2].get_best_tag().get_typed_content())
        # sppasPoint(6), label=c
        self.assertEqual(2, occ_tier[3].get_best_tag().get_typed_content())

    def test_rank(self):
        """... Test estimation of rank."""
        ocrk = OccRank(sppasTier("test"), alt=True)
        occ_tier = ocrk.occ()
        self.assertEqual(0, len(occ_tier))

        # Test a tier without / with one or more labels.
        tier = sppasTier("")
        tier.create_annotation(sppasLocation(sppasPoint(1)))
        tier.create_annotation(sppasLocation(sppasPoint(2)), [])
        tier.create_annotation(sppasLocation(sppasPoint(3)), sppasLabel(sppasTag("a")))
        tier.create_annotation(sppasLocation(sppasPoint(4)),
                               [sppasLabel(sppasTag("a")), sppasLabel(sppasTag("b"))])
        tier.create_annotation(sppasLocation(sppasPoint(5)),
                               sppasLabel([sppasTag("a"), sppasTag("c")], [0.2, 0.8]))
        tier.create_annotation(sppasLocation(sppasPoint(6)),
                               [sppasLabel([sppasTag("c"), sppasTag("a")], [0.8, 0.2])])

        ocrk = OccRank(tier, alt=True)
        rank_tier = ocrk.rank()
        self.assertEqual(4, len(rank_tier))
        # sppasPoint(3)=a
        self.assertEqual(1, rank_tier[0].get_best_tag().get_typed_content())
        # sppasPoint(4), label1=a
        self.assertEqual(2, rank_tier[1].get_best_tag(0).get_typed_content())
        # sppasPoint(4), label2=b
        self.assertEqual(1, rank_tier[1].get_best_tag(1).get_typed_content())
        # sppasPoint(5), label=tag1=a
        self.assertEqual(3, rank_tier[2].get_labels()[0][0][0].get_typed_content())
        # sppasPoint(5), label=tag2=c
        self.assertEqual(1, rank_tier[2].get_labels()[0][1][0].get_typed_content())
        # sppasPoint(6), label=tag1=c
        self.assertEqual(2, rank_tier[3].get_labels()[0][0][0].get_typed_content())
        # sppasPoint(5), label=tag2=a
        self.assertEqual(4, rank_tier[3].get_labels()[0][1][0].get_typed_content())

        ocrk.set_use_alt(False)
        rank_tier = ocrk.rank()
        self.assertEqual(4, len(rank_tier))
        # sppasPoint(3)=a
        self.assertEqual(1, rank_tier[0].get_best_tag().get_typed_content())
        # sppasPoint(4), label1=a
        self.assertEqual(2, rank_tier[1].get_best_tag(0).get_typed_content())
        # sppasPoint(4), label2=b
        self.assertEqual(1, rank_tier[1].get_best_tag(1).get_typed_content())
        # sppasPoint(5), label=c
        self.assertEqual(1, rank_tier[2].get_best_tag().get_typed_content())
        # sppasPoint(6), label=c
        self.assertEqual(2, rank_tier[3].get_best_tag().get_typed_content())
