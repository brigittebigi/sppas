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

    anndata.annloc.disjoint.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from ...anndataexc import AnnDataTypeError

from .localization import sppasBaseLocalization
from .point import sppasPoint
from .interval import sppasInterval
from .duration import sppasDuration

# ---------------------------------------------------------------------------


class sppasDisjoint(sppasBaseLocalization):
    """Localization of a serie of intervals in time.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, intervals=None):
        """Create a new sppasDisjoint instance.

        :param intervals: (list of sppasInterval)

        """
        super(sppasDisjoint, self).__init__()

        self.__intervals = list()
        if intervals is not None:
            self.set_intervals(intervals)

    # -----------------------------------------------------------------------

    def set(self, other):
        """Set self members from another sppasDisjoint instance.

        :param other: (sppasDisjoint)

        """
        if isinstance(other, sppasDisjoint) is True:
            self.set_intervals(other.get_intervals())
        elif isinstance(other, sppasInterval) is True:
            self.set_intervals([other])
        else:
            raise AnnDataTypeError(other, "sppasDisjoint or sppasInterval")

    # -----------------------------------------------------------------------

    def is_disjoint(self):
        """Return True because self is representing a disjoint intervals."""
        return True

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of self."""
        intervals = list()
        for i in self.get_intervals():
            intervals.append(i.copy())

        return sppasDisjoint(intervals)

    # -----------------------------------------------------------------------

    def get_begin(self):
        """Return the first sppasPoint instance."""
        return min(interval.get_begin() for interval in self.__intervals)

    # -----------------------------------------------------------------------

    def set_begin(self, tp):
        """Set the begin sppasPoint instance to new sppasPoint.

        :param tp: (sppasPoint)

        """
        _min = self.get_begin()
        for interval in self.__intervals:
            if interval.get_begin() == _min:
                interval.set_begin(tp)

    # -----------------------------------------------------------------------

    def get_end(self):
        """Return the last sppasPoint instance."""
        return max(interval.get_end() for interval in self.__intervals)

    # -----------------------------------------------------------------------

    def set_end(self, tp):
        """Set the end sppasPoint instance to new sppasPoint.

        :param tp: (sppasPoint)

        """
        _max = self.get_end()
        for interval in self.__intervals:
            if interval.get_end() == _max:
                interval.set_end(tp)

    # -----------------------------------------------------------------------

    def append_interval(self, interval):
        """Return the sppasInterval at the given index.

        :param interval: (sppasInterval)

        """
        if isinstance(interval, sppasInterval) is False:
            raise AnnDataTypeError(interval, "sppasInterval")
        self.__intervals.append(interval)

    # -----------------------------------------------------------------------

    def get_interval(self, index):
        """Return the sppasInterval at the given index.

        :param index: (int)

        """
        return self.__intervals[index]

    # -----------------------------------------------------------------------

    def get_intervals(self):
        """Return the list of intervals."""
        return self.__intervals

    # -----------------------------------------------------------------------

    def set_intervals(self, intervals):
        """Set a new list of intervals.

        :param intervals: list of sppasInterval.

        """
        self.__intervals = list()
        if isinstance(intervals, list) is False:
            raise AnnDataTypeError(intervals, "list")
        for interval in intervals:
            self.append_interval(interval)

    # -----------------------------------------------------------------------

    def duration(self):
        """Return the sppasDuration.

        Make the sum of all interval' durations.

        """
        value = sum(interval.duration().get_value()
                    for interval in self.get_intervals())
        vagueness = sum(interval.duration().get_margin()
                        for interval in self.get_intervals())

        return sppasDuration(value, vagueness)

    # -----------------------------------------------------------------------

    def middle(self):
        """Return a sppasPoint() at the middle of the time interval.

        To be tested.

        :returns: (sppasPoint)

        """
        if len(self.__intervals) == 0:
            return None
        m = float((self.get_begin().get_midpoint() + self.get_end().get_midpoint())) / 2.
        r = float((self.get_begin().get_radius() + self.get_end().get_radius())) / 2.

        if self.__intervals[0].is_float():
            return sppasPoint(m, r)

        return sppasPoint(int(m), int(r))

    # -----------------------------------------------------------------------

    def is_bound(self, point):
        """Return True if point is a bound of an interval."""
        return any([i.is_bound(point) for i in self.__intervals])

    # -----------------------------------------------------------------------

    def set_radius(self, radius):
        """Set radius value to all points."""
        for i in self.__intervals:
            i.set_radius(radius)

    # -----------------------------------------------------------------------

    def shift(self, delay):
        """Shift all the intervals to a given delay.

        :param delay: (int, float) delay to shift bounds
        :raise: AnnDataTypeError

        """
        for i in self.__intervals:
            i.shift(delay)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "sppasDisjoint: {:s}" \
               "".format("".join([str(i) for i in self.get_intervals()]))

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Equal is required to use '==' between 2 sppasDisjoint instances.
        Two disjoint instances are equals iff all its intervals are equals.

        :param other: (sppasDisjoint) is the other disjoint to compare with.

        """
        if not isinstance(other, sppasDisjoint):
            return False

        if len(self) != len(other):
            return False

        return all(self.get_interval(i) == other.get_interval(i)
                   for i in range(len(self)))

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """LowerThan is required to use '<' between 2 sppasDisjoint instances.

        :param other: (sppasDisjoint) is the other disjoint to compare with.

        """
        if isinstance(other, (sppasPoint, float, int)):
            return self.get_end() < other

        if isinstance(other, (sppasInterval, sppasDisjoint)) is False:
            return False

        return self.get_begin() < other.get_begin()

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 TimeDisjoint instances.

        :param other: (sppasDisjoint) is the other disjoint to compare with.

        """
        if isinstance(other, (int, float, sppasPoint)):
            return self.get_begin() > other

        if isinstance(other, (sppasInterval, sppasDisjoint)) is False:
            return False

        return self.get_begin() > other.get_begin()

    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__intervals:
            yield a

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__intervals[i]

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__intervals)
