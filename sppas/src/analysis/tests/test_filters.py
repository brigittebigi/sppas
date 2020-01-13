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

    src.anndata.tests.test_filter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Tests of the filter system.

"""

import unittest
import os.path
import time

from sppas.src.utils.makeunicode import u
from sppas.src.anndata.aio.readwrite import sppasRW
from sppas.src.anndata.tier import sppasTier
from sppas.src.anndata.ann.annlocation import sppasLocation
from sppas.src.anndata.ann.annlocation import sppasInterval
from sppas.src.anndata.ann.annlocation import sppasPoint
from sppas.src.anndata.ann.annlabel import sppasTag
from sppas.src.anndata.ann.annlabel import sppasLabel
from sppas.src.anndata.ann.annotation import sppasAnnotation

from sppas.src.anndata.ann.annset import sppasAnnSet
from ..tierfilters import sppasTierFilters
from ..tierfilters import FilterTier

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestSetFilter(unittest.TestCase):
    """Test filter result."""

    def setUp(self):
        self.p1 = sppasPoint(1)
        self.p2 = sppasPoint(2)
        self.p4 = sppasPoint(4)
        self.p9 = sppasPoint(9)
        self.it1 = sppasInterval(self.p1, self.p2)
        self.it2 = sppasInterval(self.p2, self.p4)
        self.it3 = sppasInterval(self.p4, self.p9)
        self.a1 = sppasAnnotation(sppasLocation(self.it1),
                                  sppasLabel(
                                      sppasTag(" \t\t  être    être  \n ")))
        self.a2 = sppasAnnotation(sppasLocation(self.it2),
                                  sppasLabel([sppasTag("toto"),
                                              sppasTag("titi")]))
        self.a3 = sppasAnnotation(sppasLocation(self.it3),
                                  [sppasLabel(sppasTag("tata")),
                                   sppasLabel(sppasTag("titi"))])

    # -----------------------------------------------------------------------

    def test_append(self):
        """Append an annotation and values."""

        d = sppasAnnSet()
        self.assertEqual(0, len(d))

        d.append(self.a1, ['contains = t'])
        self.assertEqual(1, len(d))
        self.assertEqual(1, len(d.get_value(self.a1)))

        # do not append the same value
        d.append(self.a1, ['contains = t'])
        self.assertEqual(1, len(d))
        self.assertEqual(1, len(d.get_value(self.a1)))

        d.append(self.a1, ['contains = o'])
        self.assertEqual(1, len(d))
        self.assertEqual(2, len(d.get_value(self.a1)))

    # -----------------------------------------------------------------------

    def test_copy(self):
        """Test the copy of a data set."""

        d = sppasAnnSet()
        d.append(self.a1, ['contains = t', 'contains = o'])
        d.append(self.a2, ['exact = titi'])

        dc = d.copy()
        self.assertEqual(len(d), len(dc))
        for ann in d:
            self.assertEqual(d.get_value(ann), dc.get_value(ann))

    # -----------------------------------------------------------------------

    def test_or(self):
        """Test logical "or" between two data sets."""

        d1 = sppasAnnSet()
        d2 = sppasAnnSet()

        d1.append(self.a1, ['contains = t'])
        d2.append(self.a1, ['contains = t'])

        res = d1 | d2
        self.assertEqual(1, len(res))
        self.assertEqual(1, len(res.get_value(self.a1)))

        d2.append(self.a1, ['contains = o'])
        res = d1 | d2
        self.assertEqual(1, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))

        d2.append(self.a2, ['exact = toto'])
        res = d1 | d2
        self.assertEqual(2, len(res))
        self.assertEqual(1, len(res.get_value(self.a2)))

        d2.append(self.a2, ['exact = toto', 'istartswith = T'])
        res = d1 | d2
        self.assertEqual(2, len(res))
        self.assertEqual(2, len(res.get_value(self.a2)))

        d1.append(self.a3, ['istartswith = t'])
        res = d1 | d2
        self.assertEqual(3, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))
        self.assertEqual(2, len(res.get_value(self.a2)))
        self.assertEqual(1, len(res.get_value(self.a3)))

    # -----------------------------------------------------------------------

    def test_and(self):
        """Test logical "and" between two data sets."""

        d1 = sppasAnnSet()
        d2 = sppasAnnSet()

        d1.append(self.a1, ['contains = t'])
        d2.append(self.a1, ['contains = o'])

        res = d1 & d2
        self.assertEqual(1, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))

        # nothing changed. a2 is only in d1.
        d1.append(self.a2, ['exact = toto'])
        res = d1 & d2
        self.assertEqual(1, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))

        # ok. add a2 in d2 too...
        d2.append(self.a2, ['exact = toto'])
        res = d1 & d2
        self.assertEqual(2, len(res))
        self.assertEqual(2, len(res.get_value(self.a1)))
        self.assertEqual(1, len(res.get_value(self.a2)))

    # -----------------------------------------------------------------------

    def test_to_tier(self):
        """Create a tier from the data set."""

        d = sppasAnnSet()
        d.append(self.a3, ['contains = t'])
        d.append(self.a1, ['contains = t'])
        d.append(self.a2, ['contains = t', 'exact = toto', ])

        # with default parameters
        t = d.to_tier()
        self.assertEqual("AnnSet", t.get_name())
        self.assertEqual(3, len(t))

        self.assertEqual(self.a1, t[0])
        self.assertEqual(self.a2, t[1])
        self.assertEqual(self.a3, t[2])

        # with parameters
        t = d.to_tier(name="Filter", annot_value=True)
        self.assertEqual("Filter", t.get_name())
        self.assertEqual(3, len(t))

        self.assertEqual(self.a1.get_location(), t[0].get_location())
        self.assertEqual(self.a2.get_location(), t[1].get_location())
        self.assertEqual(self.a3.get_location(), t[2].get_location())

        self.assertEqual(sppasTag('contains = t'), t[0].get_labels()[0].get_best())
        self.assertEqual(sppasTag('contains = t'), t[2].get_labels()[0].get_best())
        self.assertEqual(sppasTag('contains = t'), t[1].get_labels()[0].get_best())
        self.assertEqual(sppasTag('exact = toto'), t[1].get_labels()[1].get_best())

# ---------------------------------------------------------------------------


class TestFiltersTier(unittest.TestCase):
    """Test filters on a single tier."""

    def setUp(self):
        parser = sppasRW(os.path.join(DATA, "grenelle.antx"))
        self.trs = parser.read(heuristic=False)

    # -----------------------------------------------------------------------

    def test_tag(self):
        """Test tag is matching str."""

        tier = self.trs.find('P-Phonemes')

        with self.assertRaises(KeyError):
            f = sppasTierFilters(tier)
            f.tag(function="value")

        start_time = time.time()
        f = sppasTierFilters(tier)
        d1 = f.tag(startswith=u("l"))
        d2 = f.tag(endswith=u("l"))
        res = d1 | d2
        end_time = time.time()
        # print("  - elapsed time: {:f} seconds".format(end_time - start_time))
        # print("  - res size = {:d}".format(len(res)))

        start_time = time.time()
        f = sppasTierFilters(tier)
        res = f.tag(startswith=u("l"), endswith=u("l"), logic_bool="and")
        end_time = time.time()
        # print("  - elapsed time: {:f} seconds".format(end_time - start_time))
        # print("  - res size = {:d}".format(len(res)))

        start_time = time.time()
        f = sppasTierFilters(tier)
        res = f.tag(startswith=u("l"), endswith=u("l"), logic_bool="or")
        end_time = time.time()
        # print("  - elapsed time: {:f} seconds".format(end_time - start_time))
        # print("  - res size = {:d}".format(len(res)))

    # -----------------------------------------------------------------------

    def test_not_tag(self):
        """Test tag is not matching str."""

        tier = self.trs.find('P-Phonemes')
        f = sppasTierFilters(tier)
        l = f.tag(exact=u("l"))
        not_l = f.tag(not_exact=u('l'))
        self.assertEqual(len(tier), len(l)+len(not_l))

    # -----------------------------------------------------------------------

    def test_dur(self):
        """Test localization duration."""

        tier = self.trs.find('P-Phonemes')
        f = sppasTierFilters(tier)

        # phonemes during 30ms
        res = f.dur(eq=0.03)
        self.assertEqual(2, len(res))

        # phonemes during more than 200ms
        res = f.dur(ge=0.2)

    # -----------------------------------------------------------------------

    def test_loc(self):
        """Test localization range."""

        tier = self.trs.find('P-Phonemes')
        f = sppasTierFilters(tier)

        # the first 10 phonemes
        res = f.loc(rangeto=0.858)
        self.assertEqual(10, len(res))

        # the last 9 phonemes
        res = f.loc(rangefrom=241.977)
        self.assertEqual(9, len(res))

        # phonemes ranging from .. seconds of speech to .. seconds
        res1 = f.loc(rangefrom=219.177) & f.loc(rangeto=sppasPoint(221.369, 0.002))
        self.assertEqual(34, len(res1))

        res2 = f.loc(rangefrom=219.177,
                     rangeto=sppasPoint(221.369, 0.002),
                     logic_bool="and")
        self.assertEqual(34, len(res2))

        self.assertEqual(res1, res2)

    # -----------------------------------------------------------------------

    def test_combined(self):
        """Test both tag and duration."""

        tier = self.trs.find('P-Phonemes')
        f = sppasTierFilters(tier)

        # silences or pauses during more than 200ms
        res1 = (f.tag(exact=u("#")) | f.tag(exact=u("+"))) & f.dur(ge=0.2)
        res2 = f.dur(ge=0.2) & (f.tag(exact=u("#")) | f.tag(exact=u("+")))
        res3 = f.dur(ge=0.2) & (f.tag(exact=u("+")) | f.tag(exact=u("#")))

        self.assertEqual(len(res1), len(res2))
        self.assertEqual(len(res1), len(res3))

# ---------------------------------------------------------------------------


class TestFilterRelationTier(unittest.TestCase):
    """Test relations.

    Example:
    ========

        tier1:      0-----------3-------5-------7-------9---10---11
        tier2:      0---1---2---3-------5-----------8------------11

    Relations:
    ----------

    tier1                     tier2
    interval    relation      interval

    [0,3]       started by    [0,1]
    [0,3]       contains      [1,2]
    [0,3]       finished by   [2,3]
    [0,3]       meets         [3,5]
    [0,3]       before        [5,8], [8,11]

    [3,5]       after         [0,1], [1,2]
    [3,5]       met by        [2,3]
    [3,5]       equals        [3,5]
    [3,5]       meets         [5,8]
    [3,5]       before        [8,11]

    [5,7]       after         [0,1], [1,2], [2,3]
    [5,7]       met by        [3,5]
    [5,7]       starts        [5,8]
    [5,7]       before        [8,11]

    [7,9]       after         [0,1], [1,2], [2,3], [3,5]
    [7,9]       overlapped by [5,8]
    [7,9]       overlaps      [8,11]

    [9,10]      after         [0,1], [1,2], [2,3], [3,5], [5,8]
    [9,10]      during        [8,11]

    [10,11]     after         [0,1], [1,2], [2,3], [3,5], [5,8]
    [10,11]     finishes      [8,11]

    """
    def setUp(self):
        self.tier = sppasTier("Tier")
        self.tier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(0), sppasPoint(3))))
        self.tier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(3), sppasPoint(5))))
        self.tier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(5), sppasPoint(7))))
        self.tier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(7), sppasPoint(9))))
        self.tier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(9), sppasPoint(10))))
        self.tier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(10), sppasPoint(11))))

        self.rtier = sppasTier("RelationTier")
        self.rtier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(0), sppasPoint(1))))
        self.rtier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(1), sppasPoint(2))))
        self.rtier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(2), sppasPoint(3))))
        self.rtier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(3), sppasPoint(5))))
        self.rtier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(5), sppasPoint(8))))
        self.rtier.create_annotation(sppasLocation(
            sppasInterval(sppasPoint(8), sppasPoint(11))))

    def test_one_relation(self):

        f = sppasTierFilters(self.tier)

        # 'equals': [3,5]
        res = f.rel(self.rtier, "equals")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[1], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("equals", values[0])

        # 'contains': [0,3]
        res = f.rel(self.rtier, "contains")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[0], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("contains", values[0])

        # 'during': [9,10]
        res = f.rel(self.rtier, "during")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[4], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("during", values[0])

        # 'starts': [5,7]
        res = f.rel(self.rtier, "starts")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[2], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("starts", values[0])

        # 'startedby': [0,3]
        res = f.rel(self.rtier, "startedby")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[0], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("startedby", values[0])

        # 'finishedby': [0,3]
        res = f.rel(self.rtier, "finishedby")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[0], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("finishedby", values[0])

        # 'finishes': [10,11]
        res = f.rel(self.rtier, "finishes")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[5], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("finishes", values[0])

        # 'meets': [0,3]; [3,5]
        res = f.rel(self.rtier, "meets")
        self.assertEqual(2, len(res))
        self.assertTrue(self.tier[0] in res)
        self.assertTrue(self.tier[1] in res)
        values = res.get_value(self.tier[0])
        self.assertEqual(1, len(values))
        self.assertEqual("meets", values[0])
        values = res.get_value(self.tier[1])
        self.assertEqual(1, len(values))
        self.assertEqual("meets", values[0])

        # 'metby': [3,5]; [5,7]
        res = f.rel(self.rtier, "metby")
        self.assertEqual(2, len(res))
        self.assertTrue(self.tier[1] in res)
        self.assertTrue(self.tier[2] in res)
        values = res.get_value(self.tier[1])
        self.assertEqual(1, len(values))
        self.assertEqual("metby", values[0])
        values = res.get_value(self.tier[2])
        self.assertEqual(1, len(values))
        self.assertEqual("metby", values[0])

        # 'overlaps': [7,9]
        res = f.rel(self.rtier, "overlaps")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[3], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("overlaps", values[0])

        # 'overlappedby': [7,9]
        res = f.rel(self.rtier, "overlappedby")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[3], ann)
        values = res.get_value(ann)
        self.assertEqual(1, len(values))
        self.assertEqual("overlappedby", values[0])

        # 'after': all except the first interval
        res = f.rel(self.rtier, "after")
        self.assertEqual(5, len(res))
        self.assertFalse(self.tier[0] in res)
        self.assertTrue(self.tier[1] in res)
        self.assertTrue(self.tier[2] in res)
        self.assertTrue(self.tier[3] in res)
        self.assertTrue(self.tier[4] in res)
        self.assertTrue(self.tier[5] in res)

        # 'before': [0,3], [3,5], [5,7]
        res = f.rel(self.rtier, "before")
        self.assertEqual(3, len(res))
        self.assertTrue(self.tier[0] in res)
        self.assertTrue(self.tier[1] in res)
        self.assertTrue(self.tier[2] in res)
        self.assertFalse(self.tier[3] in res)
        self.assertFalse(self.tier[4] in res)
        self.assertFalse(self.tier[5] in res)

        # 'before_equal': [0,3]
        res = f.rel(self.rtier, "before_equal")
        self.assertEqual(1, len(res))
        self.assertTrue(self.tier[0] in res)

        # 'before_greater':
        res = f.rel(self.rtier, "before_greater")
        self.assertEqual(0, len(res))

        # before_lower: [3,5], [5,7]
        res = f.rel(self.rtier, "before_lower")
        self.assertEqual(2, len(res))
        self.assertTrue(self.tier[1] in res)
        self.assertTrue(self.tier[2] in res)

        with self.assertRaises(KeyError):
            f.rel(self.rtier, "relation")

    # -----------------------------------------------------------------------

    def test_several_relations(self):

        f = sppasTierFilters(self.tier)
        res = f.rel(self.rtier, "overlaps", "overlappedby")
        self.assertEqual(1, len(res))
        ann = [a for a in res][0]
        self.assertEqual(self.tier[3], ann)
        values = res.get_value(ann)
        self.assertTrue(2, len(values))
        self.assertTrue("overlaps" in values)
        self.assertTrue("overlappedby" in values)

        f = sppasTierFilters(self.tier)
        res = f.rel(self.rtier, "overlaps", "overlappedby", overlap_min=1)
        self.assertEqual(1, len(res))
        values = res.get_value(ann)
        self.assertTrue(2, len(values))

        f = sppasTierFilters(self.tier)
        res = f.rel(self.rtier, "overlaps", "overlappedby", overlap_min=2)
        self.assertEqual(0, len(res))

        f = sppasTierFilters(self.tier)
        res = f.rel(self.rtier, "overlaps", "overlappedby",
                    overlap_min=50,
                    percent=True)
        self.assertEqual(1, len(res))

        # Add tests with after/before for a better testing of options and results
        # after/before: max_delay

    # -----------------------------------------------------------------------

    def test_combined_relations(self):
        f = sppasTierFilters(self.tier)
        res1 = f.rel(self.rtier, "overlaps", "overlappedby")
        res2 = f.rel(self.rtier, "overlaps") | f.rel(self.rtier, "overlappedby")
        self.assertEqual(res1, res2)

# ---------------------------------------------------------------------------


class TestFilterTier(unittest.TestCase):
    """Test filters on a single tier."""

    def setUp(self):
        parser = sppasRW(os.path.join(DATA, "grenelle.antx"))
        self.trs = parser.read(heuristic=False)

    # -----------------------------------------------------------------------

    def test_tag(self):
        """Test tag is matching str."""
        tier = self.trs.find('P-Phonemes')

        f = sppasTierFilters(tier)
        l = f.tag(exact=u("l"))
        not_l = f.tag(not_exact=u('l'))

        ft = FilterTier([("tag", "exact", ["l"])], match_all=True, annot_format=False)
        nft = FilterTier([("tag", "not_exact", ["l"])], match_all=True, annot_format=False)
        self.assertEqual(len(ft.single_filter(tier)), len(l))
        self.assertEqual(len(nft.single_filter(tier)), len(not_l))
