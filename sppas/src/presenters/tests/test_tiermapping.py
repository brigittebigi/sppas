#!/usr/bin/env python
# -*- coding:utf-8 -*-
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

    src.presenters.tests.test_tiermapping.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os.path

from sppas.src.anndata import sppasTag, sppasLabel
from sppas.src.anndata import sppasLocation, sppasInterval, sppasPoint
from sppas.src.anndata import sppasAnnotation, sppasTier
from sppas.src.anndata.aio import sppasTextGrid
from sppas.src.anndata.aio.aioutils import serialize_labels

from ..tiermapping import sppasMappingTier

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTierMapping(unittest.TestCase):
    """Map content of annotations of a tier from a mapping table."""

    def setUp(self):
        # Create tiers
        self.tierP = sppasTier("PointTier")
        self.tierI = sppasTier("IntervalTier")
        for i in range(8):
            self.tierP.create_annotation(
                sppasLocation(sppasPoint(i)),
                sppasLabel(sppasTag(str(i))))
            self.tierI.create_annotation(
                sppasLocation(
                    sppasInterval(sppasPoint(i), sppasPoint(i+1))),
                sppasLabel(sppasTag(str(i*10))))

        self.tierI.create_annotation(
            sppasLocation(
                sppasInterval(sppasPoint(9), sppasPoint(10))),
            sppasLabel(sppasTag("{quatre-vingts-dix|nonante}")))

        # Create TierMapping
        self.map = sppasMappingTier()
        self.map.add("1", "un")
        self.map.add("2", "deux")
        self.map.add("3", "trois")
        self.map.add("4", "quatre")
        self.map.add("5", "cinq")
        self.map.add("6", "six")
        self.map.add("7", "sept")
        self.map.add("8", "huit")
        self.map.add("9", "neuf")
        self.map.add("10", "dix")
        self.map.add("20", "vingt")
        self.map.add("30", "trente")
        self.map.add("40", "quarante")
        self.map.add("50", "cinquante")
        self.map.add("60", "soixante")
        self.map.add("70", "septante")
        self.map.add("70", "soixante-dix")
        self.map.add("80", "octante")
        self.map.add("80", "quatre-vingts")
        self.map.set_delimiters((";", ",", " ", ".", "|"))

    # -----------------------------------------------------------------------

    def test_map_tag(self):
        """Map a single tag."""
        # Single text, string (normal situation)
        self.assertEqual([sppasTag("un")],
                         self.map.map_tag(sppasTag("1")))

        # Single text, string, but map returns several results
        self.assertEqual([sppasTag("septante"), sppasTag("soixante-dix")],
                         self.map.map_tag(sppasTag("70")))

        # Single text, empty
        self.assertEqual([sppasTag('')],
                         self.map.map_tag(sppasTag('')))

        # Single text, not string
        self.assertEqual([sppasTag(1, 'int')],
                         self.map.map_tag(sppasTag(1, 'int')))

        # Text with delimiter, string
        self.assertEqual([sppasTag("un,deux,trois")],
                         self.map.map_tag(sppasTag("1,2,3")))

        # Text with delimiter, string
        self.assertEqual([sppasTag("septante"), sppasTag("soixante-dix")],
                         self.map.map_tag(sppasTag("70")))

        # Test with existing X-SAMPA mapping table
        local_map = sppasMappingTier(os.path.join(DATA, "ita_mapping.repl"))
        self.assertEqual("#", local_map.get("sil"))
        self.assertEqual([sppasTag("a")],
                         local_map.map_tag(sppasTag("a")))
        self.assertEqual([sppasTag(" ")],
                         local_map.map_tag(sppasTag(" ")))

        # only speech can be converted, not silence, pause, laugh, etc
        self.assertEqual([sppasTag("sil")],
                         local_map.map_tag(sppasTag("sil")))
        local_map.set_reverse(True)
        self.assertEqual([sppasTag("#")],
                         local_map.map_tag(sppasTag("#")))

    # -----------------------------------------------------------------------

    def test_map_tag_reverse(self):
        """Map a single tag, reversing the mapping table."""
        # Map normally
        self.map.set_keep_miss(True)
        self.map.set_reverse(False)
        t_un = self.map.map_tag(sppasTag("1"))
        t_sept = self.map.map_tag(sppasTag("70"))

        # Reverse the mapping table...
        self.map.set_reverse(True)

        # Re-map. Expect the initial result
        self.assertEqual([sppasTag("1")],
                         self.map.map_tag(t_un[0]))
        self.assertEqual([sppasTag("70")],
                         self.map.map_tag(t_sept[0]))
        self.assertEqual([sppasTag("70")],
                         self.map.map_tag(t_sept[1]))

        # Map normally (for other tests!)
        self.map.set_reverse(False)

    # -----------------------------------------------------------------------

    def test_map_label(self):
        """Map a single label."""
        # Single tag, with text, string (normal situation)
        self.assertEqual(sppasLabel(sppasTag("un")),
                         self.map.map_label(sppasLabel(sppasTag("1"))))

        # Single tag, with text, string, but map returns several results
        self.assertEqual(sppasLabel([sppasTag("septante"),
                                     sppasTag("soixante-dix")]),
                         self.map.map_label(sppasLabel(sppasTag("70"))))

        # Single tag, with text+score, string
        self.assertEqual(sppasLabel(sppasTag("un"), 1.),
                         self.map.map_label(sppasLabel(sppasTag("1"), 1.)))

        # Single tag, with text+score, string, but map returns several results
        self.assertEqual(sppasLabel([sppasTag("septante"),
                                     sppasTag("soixante-dix")],
                                    [0.5, 0.5]),
                         self.map.map_label(sppasLabel(sppasTag("70"), 1.)))

        # Label with alternative tags
        label = sppasLabel([sppasTag("60"), sppasTag("70")], [0.5, 0.5])
        self.assertEqual(sppasLabel([sppasTag("soixante"),
                                     sppasTag("septante"),
                                     sppasTag("soixante-dix")],
                                    [0.5, 0.25, 0.25]),
                         self.map.map_label(label))

        # the same label, serialized (scores are lost)
        serialized_label = sppasLabel(sppasTag(label.serialize()))
        self.assertEqual(sppasLabel([sppasTag("soixante"),
                                     sppasTag("septante"),
                                     sppasTag("soixante-dix")]),
                         self.map.map_label(serialized_label))

    # -----------------------------------------------------------------------

    def test_map_label_reverse(self):
        """Map a single label, with reversed mapping table."""
        # Map normally
        self.map.set_keep_miss(True)
        self.map.set_reverse(False)
        l_un = self.map.map_label(sppasLabel(sppasTag("1")))
        l_sept = self.map.map_label(sppasLabel(sppasTag("70")))

        # Reverse the mapping table...
        self.map.set_reverse(True)

        # Re-map. Expect the initial result
        self.assertEqual(sppasLabel(sppasTag("1")),
                         self.map.map_label(l_un))

        self.assertEqual(sppasLabel(sppasTag("70")),
                         self.map.map_label(l_sept))

        # Map normally (for other tests!)
        self.map.set_reverse(False)

    # -----------------------------------------------------------------------

    def test_map_annotation(self):
        """Map a single annotation."""
        a = sppasAnnotation(sppasLocation(sppasPoint(1)))
        b = a.copy()

        # annotation without label
        self.assertEqual(a, self.map.map_annotation(a))

        # annotation with one label and no alternatives
        a.set_labels(sppasLabel(sppasTag("1")))
        b.set_labels(sppasLabel(sppasTag("un")))
        self.assertEqual(b, self.map.map_annotation(a))

        # annotation with several labels
        a.set_labels([sppasLabel(sppasTag("1")), sppasLabel(sppasTag("1"))])
        b.set_labels([sppasLabel(sppasTag("un")), sppasLabel(sppasTag("un"))])
        self.assertEqual(b, self.map.map_annotation(a))

        # annotation with several labels serialized
        l = [sppasLabel(sppasTag("1")), sppasLabel(sppasTag("1"))]
        a.set_labels(l)
        str_l = serialize_labels(a.get_labels())
        a.set_labels(sppasLabel(sppasTag(str_l)))

        l = [sppasLabel(sppasTag("un")), sppasLabel(sppasTag("un"))]
        b.set_labels(l)
        str_l = serialize_labels(b.get_labels())
        b.set_labels(sppasLabel(sppasTag(str_l)))

        self.assertEqual(b, self.map.map_annotation(a))

        # TODO: annotation with several labels with alternative tags serialized
        # CURRENTLY NOT SUPPORTED
        # l = [sppasLabel([sppasTag("1"), sppasTag("2")]),
        #      sppasLabel([sppasTag("1"), sppasTag("2")])]
        # a.set_labels(l)
        # str_l = serialize_labels(a.get_labels())
        # a.set_labels(sppasLabel(sppasTag(str_l)))
        #
        # l = [sppasLabel([sppasTag("un"), sppasTag("deux")]),
        #      sppasLabel([sppasTag("un"), sppasTag("deux")])]
        # b.set_labels(l)
        # str_l = serialize_labels(b.get_labels())
        # b.set_labels(sppasLabel(sppasTag(str_l)))
        #
        # self.assertEqual(b, self.map.map_annotation(a))

    # -----------------------------------------------------------------------

    def test_map_tier(self):
        """Map the whole content of a tier."""
        self.map.set_keep_miss(True)
        self.map.set_reverse(False)

        # map the content of 2 tiers
        t1 = self.map.map_tier(self.tierP)
        self.assertEqual(len(self.tierP), len(t1))

        t2 = self.map.map_tier(self.tierI)
        self.assertEqual(len(self.tierI), len(t2))

        # reverse to get back the original tier
        self.map.set_reverse(True)

        tP = self.map.map_tier(t1)
        self.assertEqual(len(t1), len(tP))

        for a1, a2 in zip(tP, self.tierP):
            self.assertEqual(a2, a1)

        tI = self.map.map_tier(t2)
        self.assertEqual(len(t2), len(tI))

        for a1, a2 in zip(tI, self.tierI):
            self.assertEqual(serialize_labels(a2.get_labels()),
                             serialize_labels(a1.get_labels()))

    # -----------------------------------------------------------------------

    def test_aligned_sample(self):
        tg = sppasTextGrid()
        tg.read(os.path.join(DATA, "DGtdA05Np1_95-palign.TextGrid"))
        tier = tg.find('PhonAlign')
        mapper = sppasMappingTier(os.path.join(DATA, "ita_mapping.repl"))
        mapper.set_delimiters((";", ",", " ", ".", "|"))

        mapper.set_reverse(False)
        tier_mapped = mapper.map_tier(tier)
        mapper.set_reverse(True)
        tier_re_mapped = mapper.map_tier(tier_mapped)

        for a1, a2 in zip(tier, tier_re_mapped):
            self.assertEqual(a1, a2)
