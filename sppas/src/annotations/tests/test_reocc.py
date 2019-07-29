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


"""

import unittest

from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasTier

from ..ReOccurrences.reoccurrences import ReOccurences
from ..ReOccurrences.reoccset import sppasAnnReOccSet
from ..ReOccurrences.sppasreocc import sppasReOcc

# ---------------------------------------------------------------------------


class TestReOccurences(unittest.TestCase):
    """Test of the re-occurrences search.

    """

    def setUp(self):
        pass

    # -----------------------------------------------------------------------

    def test_compare_labels(self):
        """Compare two labels.

        Return the number of tags they have in common.

        """
        # Only one tag in the label

        self.assertEqual(1, ReOccurences.compare_labels(
            sppasLabel(sppasTag("a")),
            sppasLabel(sppasTag("a")))
        )

        self.assertEqual(1, ReOccurences.compare_labels(
            sppasLabel(sppasTag(2, "int")),
            sppasLabel(sppasTag(2, "int")))
        )

        self.assertEqual(0, ReOccurences.compare_labels(
            sppasLabel(sppasTag("2", "str")),
            sppasLabel(sppasTag(2, "int")))
        )

        # Several tags in one of the labels

        self.assertEqual(1, ReOccurences.compare_labels(
            sppasLabel([sppasTag("a"), sppasTag("b")]),
            sppasLabel(sppasTag("a")))
        )

        self.assertEqual(1, ReOccurences.compare_labels(
            sppasLabel(sppasTag("a")),
            sppasLabel([sppasTag("a"), sppasTag("b")]))
        )

        self.assertEqual(0, ReOccurences.compare_labels(
            sppasLabel([sppasTag("2"), sppasTag("3")]),
            sppasLabel(sppasTag(2, "int")))
        )

        # Several tags in both labels

        self.assertEqual(0, ReOccurences.compare_labels(
            sppasLabel([sppasTag("a"), sppasTag("b")]),
            sppasLabel([sppasTag("x"), sppasTag("y")]))
                         )

        self.assertEqual(1, ReOccurences.compare_labels(
            sppasLabel([sppasTag("a"), sppasTag("b")]),
            sppasLabel([sppasTag("a"), sppasTag("y")]))
        )

        self.assertEqual(1, ReOccurences.compare_labels(
            sppasLabel([sppasTag("a"), sppasTag("b")]),
            sppasLabel([sppasTag("x"), sppasTag("a")]))
        )

        self.assertEqual(1, ReOccurences.compare_labels(
            sppasLabel([sppasTag("2", "int"), sppasTag("3", "int")]),
            sppasLabel([sppasTag("2", "int"), sppasTag("2", "int")]))
        )

    # -----------------------------------------------------------------------

    def test_eval(self):
        """Return the list of re-occurrences.

        An annotation in anns2 is matching ann1 if all labels of ann1 are
        in ann2. It is not one-to-one: some labels of ann2 could not match
        those of ann1.

        """

        # Annotations have only one label. Labels have only one tag.

        one = sppasLabel(sppasTag("1"))
        two = sppasLabel(sppasTag("2"))
        three = sppasLabel(sppasTag("3"))

        a1 = sppasAnnotation(sppasLocation(sppasPoint(1)), one)
        a1bis = sppasAnnotation(sppasLocation(sppasPoint(1)), one)
        a2 = sppasAnnotation(sppasLocation(sppasPoint(2)), two)
        a3 = sppasAnnotation(sppasLocation(sppasPoint(3)), three)

        reocc = ReOccurences.eval(a1, [a1, a2, a3])
        self.assertEqual(1, len(reocc))
        self.assertEqual(a1, reocc[0])
        reocc = ReOccurences.eval(a1, [a2, a1, a3])
        self.assertEqual(1, len(reocc))
        self.assertEqual(a1, reocc[0])
        reocc = ReOccurences.eval(a1, [a3, a2, a1])
        self.assertEqual(1, len(reocc))
        self.assertEqual(a1, reocc[0])
        reocc = ReOccurences.eval(a1, [a2, a2, a3])
        self.assertEqual(0, len(reocc))
        reocc = ReOccurences.eval(a1, [a1, a2, a3, a1bis, a2])
        self.assertEqual(2, len(reocc))
        self.assertEqual(a1, reocc[0])
        self.assertEqual(a1, reocc[1])

        # Annotations have several labels. Labels have only one tag.

        l1 = [
            sppasLabel(sppasTag("le")),
            sppasLabel(sppasTag("petit")),
            sppasLabel(sppasTag("chat"))
        ]

        l2 = [
            sppasLabel(sppasTag("le")),
            sppasLabel(sppasTag("petit")),
            sppasLabel(sppasTag("chien")),
            sppasLabel(sppasTag("et")),
            sppasLabel(sppasTag("le")),
            sppasLabel(sppasTag("chat")),
        ]

        a1 = sppasAnnotation(sppasLocation(sppasPoint(1)), l1)
        a2 = sppasAnnotation(sppasLocation(sppasPoint(2)), l2)
        reocc = ReOccurences.eval(a1, [a3, a1bis, a3])
        self.assertEqual(0, len(reocc))
        reocc = ReOccurences.eval(a1, [a3, a2])
        self.assertEqual(1, len(reocc))
        self.assertEqual(a2, reocc[0])

        l2 = [
            sppasLabel(sppasTag("le")),
            sppasLabel(sppasTag("petit")),
            sppasLabel(sppasTag("chien")),
        ]
        a2 = sppasAnnotation(sppasLocation(sppasPoint(2)), l2)
        reocc = ReOccurences.eval(a1, [a2, a1bis, a3])
        self.assertEqual(0, len(reocc))

        # Annotations have several labels. Labels have 1 or 2 tags.

        chat_multi = sppasLabel(sppasTag("chat"), score=0.6)
        chat_multi.append(sppasTag("sa"), score=0.4)

        l2 = [
            sppasLabel(sppasTag("le")),
            sppasLabel(sppasTag("petit")),
            sppasLabel(sppasTag("chien")),
            sppasLabel(sppasTag("et")),
            sppasLabel(sppasTag("le")),
            chat_multi
        ]
        a2 = sppasAnnotation(sppasLocation(sppasPoint(2)), l2)
        reocc = ReOccurences.eval(a1, [a3, a2])
        self.assertEqual(1, len(reocc))
        self.assertEqual(a2, reocc[0])

# ---------------------------------------------------------------------------


class TestOccAnnSet(unittest.TestCase):
    """Test the re-occurrence annotation set.

    """

    def test_to_tier(self):
        """Create tiers from a set of annotations.

        """

        one = sppasLabel(sppasTag("1"))
        two = sppasLabel(sppasTag("2"))
        second = sppasLabel(sppasTag("2"))
        a1 = sppasAnnotation(sppasLocation(sppasPoint(1)), one)
        a1bis = sppasAnnotation(sppasLocation(sppasPoint(10)), one)
        a2 = sppasAnnotation(sppasLocation(sppasPoint(2)), two)
        a2bis = sppasAnnotation(sppasLocation(sppasPoint(20)), [two, second])
        a2ter = sppasAnnotation(sppasLocation(sppasPoint(22)), second)

        # The simplest as possible: a single annotation re-occurring only once
        annset = sppasAnnReOccSet()
        annset.append(a1, [a1bis])
        tiers = annset.to_tier()
        self.assertEqual(3, len(tiers))
        for t in tiers:
            self.assertEqual(1, len(t))
        self.assertEqual("S0", tiers[0][0].get_best_tag().get_content())
        self.assertEqual("1", tiers[1][0].get_best_tag().get_content())
        self.assertEqual("R0", tiers[2][0].get_best_tag().get_content())
        self.assertEqual(sppasPoint(1), tiers[0][0].get_lowest_localization())
        self.assertEqual(sppasPoint(1), tiers[1][0].get_lowest_localization())
        self.assertEqual(sppasPoint(10), tiers[2][0].get_lowest_localization())

        annset = sppasAnnReOccSet()
        annset.append(a2, [a2bis])
        tiers = annset.to_tier()
        self.assertEqual(3, len(tiers))
        for t in tiers:
            self.assertEqual(1, len(t))
        self.assertEqual("S0", tiers[0][0].get_best_tag().get_content())
        self.assertEqual("1", tiers[1][0].get_best_tag().get_content())
        self.assertEqual("R0", tiers[2][0].get_best_tag().get_content())
        self.assertEqual(sppasPoint(2), tiers[0][0].get_lowest_localization())
        self.assertEqual(sppasPoint(2), tiers[1][0].get_lowest_localization())
        self.assertEqual(sppasPoint(20), tiers[2][0].get_lowest_localization())

        # Two annotations re-occur only once
        annset = sppasAnnReOccSet()
        annset.append(a1, [a1bis])
        annset.append(a2, [a2bis])

        tiers = annset.to_tier()
        self.assertEqual(3, len(tiers))
        for t in tiers:
            self.assertEqual(2, len(t))

        self.assertEqual("S0", tiers[0][0].get_best_tag().get_content())
        self.assertEqual("1", tiers[1][0].get_best_tag().get_content())
        self.assertEqual("R0", tiers[2][0].get_best_tag().get_content())
        self.assertEqual("S1", tiers[0][1].get_best_tag().get_content())
        self.assertEqual("1", tiers[1][1].get_best_tag().get_content())
        self.assertEqual("R1", tiers[2][1].get_best_tag().get_content())

        self.assertEqual(sppasPoint(1), tiers[0][0].get_lowest_localization())
        self.assertEqual(sppasPoint(1), tiers[1][0].get_lowest_localization())
        self.assertEqual(sppasPoint(10), tiers[2][0].get_lowest_localization())
        self.assertEqual(sppasPoint(2), tiers[0][1].get_lowest_localization())
        self.assertEqual(sppasPoint(2), tiers[1][1].get_lowest_localization())
        self.assertEqual(sppasPoint(20), tiers[2][1].get_lowest_localization())

        # Two annotations re-occur severals
        annset = sppasAnnReOccSet()
        annset.append(a1, [a1bis])
        annset.append(a2, [a2bis, a2ter])

        tiers = annset.to_tier()
        self.assertEqual(3, len(tiers))

        self.assertEqual("S0", tiers[0][0].get_best_tag().get_content())
        self.assertEqual("1", tiers[1][0].get_best_tag().get_content())
        self.assertEqual("R0", tiers[2][0].get_best_tag().get_content())
        self.assertEqual("S1", tiers[0][1].get_best_tag().get_content())
        self.assertEqual("2", tiers[1][1].get_best_tag().get_content())
        self.assertEqual("R1", tiers[2][1].get_best_tag().get_content())
        self.assertEqual("R1", tiers[2][2].get_best_tag().get_content())

# ---------------------------------------------------------------------------


class TestSPPASOcc(unittest.TestCase):
    """Test the SPPAS integration of re-occurrence annotation.

    """

    def test_init(self):
        r = sppasReOcc()
        self.assertEqual(20, r.max_span)

    def test_detection(self):
        one = sppasLabel(sppasTag("1"))
        two = sppasLabel(sppasTag("2"))
        second = sppasLabel(sppasTag("2"))
        a1 = sppasAnnotation(sppasLocation(sppasPoint(1)), one)
        a1bis = sppasAnnotation(sppasLocation(sppasPoint(10)), one)
        a2 = sppasAnnotation(sppasLocation(sppasPoint(2)), two)
        a2bis = sppasAnnotation(sppasLocation(sppasPoint(20)), [two, second])
        a2ter = sppasAnnotation(sppasLocation(sppasPoint(22)), second)

        t1 = sppasTier("tier1")
        t2 = sppasTier("tier2")
        t1.append(a1)
        t1.append(a2)
        t2.append(a1bis)
        t2.append(a2bis)
        t2.append(a2ter)

        r = sppasReOcc()
        tiers = r.detection(t1, t2)
        self.assertEqual(3, len(tiers))

        self.assertEqual("S0", tiers[0][0].get_best_tag().get_content())
        self.assertEqual("1", tiers[1][0].get_best_tag().get_content())
        self.assertEqual("R0", tiers[2][0].get_best_tag().get_content())
        self.assertEqual("S1", tiers[0][1].get_best_tag().get_content())
        self.assertEqual("2", tiers[1][1].get_best_tag().get_content())
        self.assertEqual("R1", tiers[2][1].get_best_tag().get_content())
        self.assertEqual("R1", tiers[2][2].get_best_tag().get_content())

