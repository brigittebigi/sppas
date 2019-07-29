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

    src.anndata.tests.test_location
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the classes of the annlocation package.

"""
import unittest

from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlocation import sppasDisjoint
from ..anndataexc import AnnDataTypeError
from ..anndataexc import IntervalBoundsError
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasLocalizationCompare

# ---------------------------------------------------------------------------


class TestLocation(unittest.TestCase):

    def test_apppend(self):
        loc0 = sppasPoint(1)
        loc1 = sppasPoint(1.8)
        loc2 = sppasPoint(1.8)

        location0 = sppasLocation(loc0)
        self.assertEqual(len(location0), 1)
        location0.append(loc2)
        self.assertEqual(len(location0), 2)
        self.assertEqual(location0.get_best(), loc0)

        location1 = sppasLocation(loc0, score=0.5)

        # expect error (types inconsistency)
        with self.assertRaises(TypeError):
            location1.append(sppasInterval(loc0, loc2), score=0.5)

    # -----------------------------------------------------------------------

    def test_get(self):
        location = sppasLocation(sppasPoint(1))
        location.append(sppasPoint(1.8), score=0.5)
        with self.assertRaises(AttributeError):
            location.get_best().get_begin()

        p1 = sppasPoint(1.8)
        p2 = sppasPoint(2.4)
        location = sppasLocation(p1)

        i = sppasInterval(p1, p2)
        location = sppasLocation(i)
        self.assertEqual(p1, location.get_best().get_begin())
        self.assertEqual(p2, location.get_best().get_end())
        with self.assertRaises(AttributeError):
            location.get_best().get_point()

    # -----------------------------------------------------------------------

    def test_equal(self):
        loc = sppasLocation(sppasPoint(0), score=0.5)
        self.assertTrue(loc == loc)
        self.assertEqual(loc, loc)
        self.assertEqual(loc, sppasLocation(sppasPoint(0), score=0.5))
        self.assertFalse(loc == sppasLocation(sppasPoint(0), score=1.))
        self.assertFalse(loc == sppasLocation(sppasPoint(1), score=0.5))

# ---------------------------------------------------------------------------


class TestPoint(unittest.TestCase):

    def setUp(self):
        pass

    # -----------------------------------------------------------------------

    def test_init(self):
        point = sppasPoint(0)    # int is identified
        point = sppasPoint("0")  # converted to float
        self.assertEqual(point.get_midpoint(), 0)
        self.assertEqual(point.get_radius(), None)
        point = sppasPoint(0.)
        self.assertEqual(point.get_midpoint(), 0.)
        self.assertEqual(point.get_radius(), None)
        with self.assertRaises(AnnDataTypeError):
            point = sppasPoint(0, 0.)
        with self.assertRaises(AnnDataTypeError):
            point = sppasPoint(0., 0)
        point = sppasPoint(0.)
        with self.assertRaises(AnnDataTypeError):
            point.set_radius(0)

    # -----------------------------------------------------------------------

    def test_check_types(self):
        self.assertTrue(sppasPoint.check_types(2, 2))
        self.assertFalse(sppasPoint.check_types(2.0, 2))
        self.assertFalse(sppasPoint.check_types(2, 2.0))
        self.assertFalse(sppasPoint.check_types(2, sppasPoint(1)))

# ---------------------------------------------------------------------------


class TestTimePoint(unittest.TestCase):

    def setUp(self):
        self.point0 = sppasPoint(0)
        self.pointV = sppasPoint(1.000, 0.001)
        self.pointW = sppasPoint(1.001, 0.001)
        self.pointX = sppasPoint(1.002, 0.001)
        self.pointY = sppasPoint(1.003, 0.003)
        self.pointZ = sppasPoint(1.003, 0.001)

    # -----------------------------------------------------------------------

    def test__eq__(self):
        """
        x = y iff
        |x - y| < dx + dy
        """
        # abs(1.000 - 1.001) < 0.001 + 0.001
        self.assertEqual(self.pointV, self.pointW)

        # abs(1.000 - 1.003) < 0.001 + 0.003
        self.assertEqual(self.pointV, self.pointY)

        # abs(1.000 - 1.002) < 0.001 + 0.001
        self.assertNotEqual(self.pointV, self.pointX)

    # -----------------------------------------------------------------------

    def test__lt__(self):
        """
        x < y iff:
        x != y && x < y
        """
        # 1.000 + (0.001 + 0.001) < 1.003
        # self.assertTrue(self.pointV < self.pointZ)
        self.assertLess(self.pointV, self.pointZ)

        # 1.000 + (0.001 + 0.001) < 1.002
        self.assertLess(self.pointV, self.pointX)

    # -----------------------------------------------------------------------

    def test__gt__(self):
        """
        x > y iff:
        x != y && x > y
        """
        # 1.003 - (0.001 + 0.001) > 1.001
        self.assertGreater(self.pointZ, self.pointV)

        # 1.002 - (0.001 + 0.001) > 1.001
        self.assertGreater(self.pointX, self.pointV)

    # -----------------------------------------------------------------------

    def test__ne__(self):
        self.assertNotEqual(self.pointV, self.pointX)

    # -----------------------------------------------------------------------

    def test__le__(self):
        self.assertLessEqual(self.pointV, self.pointZ)
        self.assertLessEqual(self.pointV, self.pointW)

    # -----------------------------------------------------------------------

    def test__ge__(self):
        self.assertGreaterEqual(self.pointX, self.pointV)
        self.assertGreaterEqual(self.pointV, self.pointW)

    # -----------------------------------------------------------------------

    def test_others(self):
        point0 = sppasPoint(0.1, 0.2)
        self.assertEqual(point0.get_midpoint(), 0.1)
        self.assertEqual(point0.get_radius(),   0.1)
        point1 = point0
        self.assertEqual(point0.get_midpoint(), point1.get_midpoint())
        self.assertEqual(point0.get_radius(), point1.get_radius())
        self.assertTrue(point1 is point0)
        point2 = point0.copy()
        self.assertEqual(point0.get_midpoint(), point2.get_midpoint())
        self.assertEqual(point0.get_radius(), point2.get_radius())
        self.assertFalse(point2 is point0)
        point3 = sppasPoint(0.1, 0.2)
        point2.set(point3)
        self.assertFalse(point2 is point3)
        self.assertEqual(point0.duration(), 0.)
        pointd = sppasPoint(0.3, 0.1)
        self.assertEqual(pointd.duration(), 0.)
        self.assertEqual(pointd.duration(), 0.1)

        # now, test errors
        point0 = sppasPoint(0.1)
        with self.assertRaises(AnnDataTypeError):
            point0.set([9])
        with self.assertRaises(AnnDataTypeError):
            point0.set_midpoint([9])
        with self.assertRaises(AnnDataTypeError):
            point0.set_radius([9])
        # with self.assertRaises(AnnDataNegValueError):
        #     point0.set_midpoint(-5)
        # with self.assertRaises(AnnDataNegValueError):
        #     point0.set_radius(-5.)
        with self.assertRaises(AnnDataTypeError):
            point0.set_radius(-5)

# ---------------------------------------------------------------------------


class TestFramePoint(unittest.TestCase):

    def setUp(self):
        self.point0 = sppasPoint(0)
        self.pointV = sppasPoint(1, 0)
        self.pointW = sppasPoint(1, 1)
        self.pointX = sppasPoint(1, 1)
        self.pointY = sppasPoint(2, 1)
        self.pointZ = sppasPoint(3, 1)

    # -----------------------------------------------------------------------

    def test__eq__(self):
        """
        x = y iff
        |x - y| < dx + dy
        """
        self.assertEqual(self.pointV, self.pointW)
        self.assertEqual(self.pointV, self.pointY)

    # -----------------------------------------------------------------------

    def test__lt__(self):
        """
        x < y iff:
        x != y && x < y
        """
        self.assertLess(self.pointV, self.pointZ)

    # -----------------------------------------------------------------------

    def test__gt__(self):
        """
        x > y iff:
        x != y && x > y
        """
        self.assertGreater(self.pointZ, self.pointV)

    # -----------------------------------------------------------------------

    def test__ne__(self):
        self.assertNotEqual(self.pointV, self.pointZ)

    # -----------------------------------------------------------------------

    def test__le__(self):
        self.assertLessEqual(self.pointV, self.pointY)
        self.assertLessEqual(self.pointV, self.pointZ)

    # -----------------------------------------------------------------------

    def test__ge__(self):
        self.assertGreaterEqual(self.pointZ, self.pointW)
        self.assertGreaterEqual(self.pointV, self.pointW)

    # -----------------------------------------------------------------------

    def test_others(self):
        point0 = sppasPoint(1, 0)
        self.assertEqual(point0.get_midpoint(), 1)
        self.assertEqual(point0.get_radius(), 0)
        point0 = sppasPoint(1, 2)
        self.assertEqual(point0.get_midpoint(), 1)
        self.assertEqual(point0.get_radius(), 1)
        point1 = point0
        point2 = point0.copy()
        self.assertEqual(point0, point1)
        self.assertEqual(point0, point2)
        self.assertTrue(point1 is point0)
        self.assertFalse(point2 is point0)

    # -----------------------------------------------------------------------

    def test_duration(self):
        point0 = sppasPoint(10, 1)
        self.assertEqual(point0.duration().get_value(), 0)
        self.assertEqual(point0.duration().get_margin(), 2)

# ---------------------------------------------------------------------------


class TestTimeInterval(unittest.TestCase):

    def setUp(self):
        self.point1000 = sppasPoint(1.000, 0.0005)
        self.point1001 = sppasPoint(1.001, 0.0005)
        self.point1002 = sppasPoint(1.002, 0.0005)
        self.point1003 = sppasPoint(1.003, 0.0005)
        self.point1004 = sppasPoint(1.004, 0.0005)
        self.point1005 = sppasPoint(1.005, 0.0005)
        self.point1006 = sppasPoint(1.006, 0.0005)
        self.point1007 = sppasPoint(1.007, 0.0005)

    # -----------------------------------------------------------------------

    def test__init__(self):
        """
        Raise ValueError if end < begin
        """
        with self.assertRaises(ValueError):
            sppasInterval(self.point1000, self.point1000)

    # -----------------------------------------------------------------------

    def test_check_interval_bounds(self):
        """Check if bounds form an interval."""

        self.assertTrue(sppasInterval(sppasPoint(1), sppasPoint(2)))
        self.assertTrue(sppasInterval(sppasPoint(1, 1), sppasPoint(2, 1)))
        self.assertTrue(sppasInterval(sppasPoint(3, 3), sppasPoint(4, 3)))

        with self.assertRaises(IntervalBoundsError):
            sppasInterval(sppasPoint(1), sppasPoint(1))
        with self.assertRaises(IntervalBoundsError):
            sppasInterval(sppasPoint(2), sppasPoint(1))

    # -----------------------------------------------------------------------

    def test_set_begin(self):
        """
        Raise ValueError if the given TimePoint >= self.End
        """
        interval = sppasInterval(self.point1000, self.point1002)
        with self.assertRaises(ValueError):
            interval.set_begin(self.point1003)
        with self.assertRaises(ValueError):
            interval.set_begin(self.point1002)

        with self.assertRaises(AnnDataTypeError):
            interval.set_begin(1.0)

    # -----------------------------------------------------------------------

    def test_set_end(self):
        """
        Raise ValueError if self.Begin >= the given TimePoint.
        """
        interval = sppasInterval(self.point1000, self.point1002)
        with self.assertRaises(ValueError):
            interval.set_end(self.point1000)

        with self.assertRaises(AnnDataTypeError):
            interval.set_end(1.00)

    # -----------------------------------------------------------------------

    def test_middle(self):
        interval = sppasInterval(self.point1000, self.point1002)
        self.assertEqual(1.001, interval.middle_value())

        interval = sppasInterval(sppasPoint(1), sppasPoint(3))
        self.assertEqual(2., interval.middle_value())

    # -----------------------------------------------------------------------

    def test__eq__(self):
        """
        x = y iff
        x.begin = y.begin && x.end = y.end
        """
        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 == interval2)

    # -----------------------------------------------------------------------

    def test__lt__(self):
        """
        x < y iff
        x.begin < y.begin && x.end < y.end
        """
        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 < interval2)

        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1001, self.point1004)
        self.assertFalse(interval1 < interval2)

        # interval |-----|
        # point            |
        self.assertTrue(interval1 < 1.004)
        self.assertTrue(interval1 < self.point1005)
        self.assertTrue(interval1 < 1.003)

        interval1 = sppasInterval(sppasPoint(1.5), sppasPoint(2.))
        interval2 = sppasInterval(sppasPoint(1.0), sppasPoint(2.))
        # 1      |----|
        # 2 |---------|
        self.assertFalse(interval1 < interval2)

    # -----------------------------------------------------------------------

    def test__gt__(self):
        """
        x > y iff
        x.begin > y.begin && x.end > y.end
        """
        interval1 = sppasInterval(self.point1004, self.point1006)
        interval2 = sppasInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 > interval2)

        # interval   |-----|
        # point    |
        self.assertTrue(interval1 > 1.002)
        self.assertTrue(interval1 > 1.003)
        self.assertTrue(interval1 > sppasPoint(1.003, 0.))
        self.assertTrue(interval1 > sppasPoint(1.003))
        self.assertFalse(interval1 > 1.006)

    # -----------------------------------------------------------------------

    def test__ne__(self):
        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 != interval2)

    # -----------------------------------------------------------------------

    def test__le__(self):
        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 <= interval2)

        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 <= interval2)

        # self  |-------|
        # other |----|
        # False
        interval1 = sppasInterval(self.point1000, self.point1006)
        interval2 = sppasInterval(self.point1000, self.point1003)
        self.assertFalse(interval1 <= interval2)

        # self  |----|
        # other |-------|
        # True
        interval1 = sppasInterval(self.point1000, self.point1003)
        interval2 = sppasInterval(self.point1000, self.point1006)
        self.assertFalse(interval1 <= interval2)

    # -----------------------------------------------------------------------

    def test__ge__(self):
        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 >= interval2)

        interval1 = sppasInterval(self.point1004, self.point1006)
        interval2 = sppasInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 >= interval2)

        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1002, self.point1004)
        self.assertFalse(interval1 >= interval2)

    # -----------------------------------------------------------------------

    def test_duration(self):
        point1 = sppasPoint(1., 0.001)
        point3 = sppasPoint(3., 0.001)
        interval13 = sppasInterval(point1, point3)
        self.assertEqual(interval13.duration(), 2)
        self.assertEqual(interval13.duration(), 2.0)
        self.assertEqual(interval13.duration(), 1.999)
        self.assertEqual(interval13.duration(), 2.001)
        self.assertGreaterEqual(interval13.duration(), 2.002)

    # -----------------------------------------------------------------------

    def test_others(self):
        point0 = sppasPoint(0.)
        point1 = sppasPoint(1., 0.001)
        point2 = sppasPoint(2.)
        point3 = sppasPoint(3., 0.001)
        interval01 = sppasInterval(point0, point1)
        interval001 = interval01
        self.assertEqual(interval01.get_begin(), interval001.get_begin())
        self.assertEqual(interval01.get_end(), interval001.get_end())
        self.assertTrue(interval01 is interval001)
        interval0001 = interval01.copy()
        self.assertEqual(interval01.get_begin(), interval0001.get_begin())
        self.assertEqual(interval01.get_end(), interval0001.get_end())
        self.assertFalse(interval01 is interval0001)
        interval23 = sppasInterval(point2, point3)
        interval23.set(interval01)
        self.assertFalse(interval23 is interval001)
        interval23 = sppasInterval(point2, point3)
        self.assertTrue(interval23.is_bound(point2))
        self.assertTrue(interval23.is_bound(point3))
        self.assertTrue(interval23.is_bound(sppasPoint(2.)))
        self.assertFalse(interval23.is_bound(point0))

# ---------------------------------------------------------------------------


class TestFrameInterval(unittest.TestCase):

    def setUp(self):
        self.point1000 = sppasPoint(0, 1)
        self.point1001 = sppasPoint(1, 1)
        self.point1002 = sppasPoint(2, 0)
        self.point1003 = sppasPoint(3, 0)
        self.point1004 = sppasPoint(4, 0)
        self.point1005 = sppasPoint(5, 0)
        self.point1006 = sppasPoint(6, 0)
        self.point1007 = sppasPoint(7, 1)

    # -----------------------------------------------------------------------

    def test__init__(self):
        """
        Raise ValueError if end < begin
        """
        with self.assertRaises(IntervalBoundsError):
            sppasInterval(self.point1000, self.point1000)

    # -----------------------------------------------------------------------

    def test_check_types(self):
        """
        Accept begin/end only if both are sppasPoint().
        """
        self.assertTrue(sppasInterval.check_types(self.point1000, sppasPoint(7, 1)))
        self.assertFalse(sppasInterval.check_types(self.point1000, sppasPoint(7.0, 1.0)))
        self.assertFalse(sppasInterval.check_types(self.point1000, 2))
        self.assertFalse(sppasInterval.check_types(2, 2))

    # -----------------------------------------------------------------------

    def test_set_begin(self):
        """
        Raise ValueError if the given FramePoint >= self.End
        """
        interval = sppasInterval(self.point1000, self.point1002)
        with self.assertRaises(IntervalBoundsError):
            interval.set_begin(self.point1003)

        with self.assertRaises(AnnDataTypeError):
            interval.set_begin(1)

    # -----------------------------------------------------------------------

    def test_set_end(self):
        """
        Raise ValueError if self.Begin >= the given FramePoint.
        """
        interval = sppasInterval(self.point1000, self.point1002)
        with self.assertRaises(IntervalBoundsError):
            interval.set_end(self.point1000)

        with self.assertRaises(AnnDataTypeError):
            interval.set_end(1)

    # -----------------------------------------------------------------------

    def test__eq__(self):
        """
        x = y iff
        x.begin = y.begin && x.end = y.end
        """
        interval1 = sppasInterval(self.point1000, self.point1003)
        interval2 = sppasInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 == interval2)

    # -----------------------------------------------------------------------

    def test__lt__(self):
        """
        x < y iff
        x.begin < y.begin && x.end < y.end
        """
        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 < interval2)

        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1001, self.point1004)
        self.assertFalse(interval1 < interval2)

        # interval |-----|
        # point            |
        self.assertTrue(interval1 < 4)
        self.assertTrue(interval1 < self.point1005)
        self.assertTrue(interval1 < 3)

        interval1 = sppasInterval(sppasPoint(2), sppasPoint(3))
        interval2 = sppasInterval(sppasPoint(1), sppasPoint(3))
        # 1      |----|
        # 2 |---------|
        self.assertFalse(interval1 < interval2)

    # -----------------------------------------------------------------------

    def test__gt__(self):
        """
        x > y iff
        x.begin > y.begin && x.end > y.end
        """
        interval1 = sppasInterval(self.point1004, self.point1006)
        interval2 = sppasInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 > interval2)

        # interval   |-----|
        # point    |
        self.assertTrue(interval1 > 2)
        self.assertTrue(interval1 > 3)
        self.assertTrue(interval1 > sppasPoint(3, 0))
        self.assertTrue(interval1 > sppasPoint(3))
        self.assertFalse(interval1 > 6)

    # -----------------------------------------------------------------------

    def test__ne__(self):
        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 != interval2)

    # -----------------------------------------------------------------------

    def test__le__(self):
        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1002, self.point1004)
        self.assertTrue(interval1 <= interval2)

        interval1 = sppasInterval(self.point1000, self.point1003)
        interval2 = sppasInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 <= interval2)

        # self  |-------|
        # other |----|
        # False
        interval1 = sppasInterval(self.point1000, self.point1006)
        interval2 = sppasInterval(self.point1000, self.point1003)
        self.assertFalse(interval1 <= interval2)

        # self  |----|
        # other |-------|
        # True
        interval1 = sppasInterval(self.point1000, self.point1003)
        interval2 = sppasInterval(self.point1000, self.point1006)
        self.assertFalse(interval1 <= interval2)

    # -----------------------------------------------------------------------

    def test__ge__(self):
        interval1 = sppasInterval(self.point1000, self.point1003)
        interval2 = sppasInterval(self.point1001, self.point1003)
        self.assertTrue(interval1 >= interval2)

        interval1 = sppasInterval(self.point1004, self.point1006)
        interval2 = sppasInterval(self.point1000, self.point1002)
        self.assertTrue(interval1 >= interval2)

        interval1 = sppasInterval(self.point1000, self.point1002)
        interval2 = sppasInterval(self.point1002, self.point1004)
        self.assertFalse(interval1 >= interval2)

    # -----------------------------------------------------------------------

    def test_duration(self):
        interval1 = sppasInterval(self.point1000, self.point1007)
        self.assertEqual(interval1.duration().get_value(), 7)
        self.assertEqual(interval1.duration(), 6)
        self.assertEqual(interval1.duration(), 7)
        self.assertEqual(interval1.duration(), 8)

    # -----------------------------------------------------------------------

    def test_others(self):
        point0 = sppasPoint(0)
        point1 = sppasPoint(1, 1)
        point2 = sppasPoint(2)
        point3 = sppasPoint(3, 1)
        interval01 = sppasInterval(point0, point1)
        toto = sppasInterval(sppasPoint(2, 1), sppasPoint(3, 2))
        with self.assertRaises(ValueError):
            tata = sppasInterval(sppasPoint(2, 1), sppasPoint(3, 3))

        interval001 = interval01
        self.assertEqual(interval01, interval001)
        self.assertTrue(interval01 is interval001)
        interval0001 = interval01.copy()
        self.assertEqual(interval01, interval0001)
        self.assertFalse(interval01 is interval0001)
        interval23 = sppasInterval(point2, point3)
        interval23.set(interval01)
        self.assertFalse(interval23 is interval001)

# ---------------------------------------------------------------------------


class TestTimeDisjoint(unittest.TestCase):

    def test__init__(self):
        with self.assertRaises(TypeError):
            sppasDisjoint(10)

    # -----------------------------------------------------------------------

    def test__eq__(self):
        intervals1 = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        intervals2 = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        self.assertEqual(intervals1, intervals2)

    # -----------------------------------------------------------------------

    def test_duration(self):
        intervals = [sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(5)]
        t_disjoint = sppasDisjoint(intervals)
        self.assertEqual(t_disjoint.duration().get_value(), 5)
        self.assertEqual(t_disjoint.duration().get_margin(), 0)

    # -----------------------------------------------------------------------

    def test_get_interval(self):
        t_disjoint = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        for i in range(10):
            self.assertEqual(t_disjoint.get_interval(i), sppasInterval(sppasPoint(i), sppasPoint(i+1)))

    # -----------------------------------------------------------------------

    def test_is(self):
        t_disjoint = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        self.assertFalse(t_disjoint.is_point())
        self.assertFalse(t_disjoint.is_interval())
        self.assertTrue(t_disjoint.is_disjoint())

    # -----------------------------------------------------------------------

    def test_set(self):
        t_disjoint = sppasDisjoint([sppasInterval(sppasPoint(float(i)), sppasPoint(float(i)+1.)) for i in range(10)])
        t_disjoint.set_begin(sppasPoint(0.5))
        self.assertEqual(t_disjoint.get_begin(), sppasPoint(0.5))
        with self.assertRaises(ValueError):
            t_disjoint.set_begin(sppasPoint(1.))

        t_disjoint.End = sppasPoint(11)
        self.assertEqual(t_disjoint.End, sppasPoint(11))
        with self.assertRaises(ValueError):
            t_disjoint.set_end(sppasPoint(9.))

    # -----------------------------------------------------------------------

    def test_is_bound(self):
        t_disjoint = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        self.assertTrue(t_disjoint.is_bound(sppasPoint(2)))
        self.assertFalse(t_disjoint.is_bound(sppasPoint(11)))

# ---------------------------------------------------------------------------


class TestFrameDisjoint(unittest.TestCase):

    def test__init__(self):
        """
        Raise TypeError
        """
        with self.assertRaises(AnnDataTypeError):
            sppasDisjoint(10)

    # -----------------------------------------------------------------------

    def test__eq__(self):
        intervals1 = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        intervals2 = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        self.assertEqual(intervals1, intervals2)

    # -----------------------------------------------------------------------

    def test_duration(self):
        intervals = [sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(5)]
        t_disjoint = sppasDisjoint(intervals)
        self.assertEqual(t_disjoint.duration().get_value(), 5)
        self.assertEqual(t_disjoint.duration().get_margin(), 0)

    # -----------------------------------------------------------------------

    def test_get_interval(self):
        t_disjoint = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        for i in range(10):
            self.assertEqual(t_disjoint.get_interval(i), sppasInterval(sppasPoint(i), sppasPoint(i+1)))

    # -----------------------------------------------------------------------

    def test_is(self):
        t_disjoint = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        self.assertFalse(t_disjoint.is_point())
        self.assertFalse(t_disjoint.is_interval())
        self.assertTrue(t_disjoint.is_disjoint())

    # -----------------------------------------------------------------------

    def test_set(self):
        t_disjoint = sppasDisjoint([sppasInterval(sppasPoint(i), sppasPoint(i+1)) for i in range(10)])
        t_disjoint.set_begin(sppasPoint(0))
        self.assertEqual(t_disjoint.get_begin(), sppasPoint(0))

        with self.assertRaises(ValueError):
            t_disjoint.set_begin(sppasPoint(1))
        t_disjoint.set_end(sppasPoint(11))
        self.assertEqual(t_disjoint.get_end(), sppasPoint(11))
        with self.assertRaises(ValueError):
            t_disjoint.set_end(sppasPoint(9))

# ---------------------------------------------------------------------------


class TestLocalizationCompare(unittest.TestCase):

    def test_range(self):
        pass

    def setUp(self):
        self.lc = sppasLocalizationCompare()

    # -----------------------------------------------------------------------

    def test_members(self):
        """Test methods getter."""

        self.assertEqual(self.lc.methods['rangefrom'], self.lc.rangefrom)
        self.assertEqual(self.lc.get('rangefrom'), self.lc.rangefrom)

        self.assertEqual(self.lc.methods['rangeto'], self.lc.rangeto)
        self.assertEqual(self.lc.get('rangeto'), self.lc.rangeto)

    # -----------------------------------------------------------------------

    def test_rangefrom(self):
        """localization <= x."""

        self.assertTrue(self.lc.rangefrom(sppasPoint(1., 0.02), 1.01))
        self.assertTrue(self.lc.rangefrom(sppasPoint(1., 0.02), 0.5))
        self.assertFalse(self.lc.rangefrom(sppasPoint(1., 0.02), sppasPoint(2)))

        with self.assertRaises(TypeError):
            self.lc.rangefrom(1, 1)
