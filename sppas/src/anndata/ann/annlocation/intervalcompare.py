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

    anndata.annlocation.intervalcompare.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This class is inspired by both the "Allen's Interval Algebra" and INDU.

    James Allen, in 1983, proposed an algebraic framework named Interval
    Algebra (IA), for qualitative reasoning with time intervals where the
    binary relationship between a pair of intervals is represented  by a
    subset of 13 atomic relation, that are:

      - distinct because no pair of definite intervals can be related
      by more than one of the relationships;

      - exhaustive because any pair of definite intervals are described
      by one of the relations;

      - qualitative (rather than quantitative) because no numeric time
      spans are considered.

    These relations and the operations on them form the
    "Allen's Interval Algebra".

    Using this calculus, given facts can be formalized and then used for
    automatic reasoning. Relations are: before, after, meets, met by,
    overlaps, overlapped by, starts, started by, finishes, finished by,
    contains, during and equals.

    Pujari, Kumari and Sattar proposed INDU in 1999: an Interval & Duration
    network. They extended the IA to model qualitative information about
    intervals and durations in a single binary constraint network. Duration
    relations are: greater, lower and equal.
    INDU comprises of 25 basic relations between a pair of two intervals.

    For convenience reasons, and because this class will be used to filter
    annotated data (and not reasoning), it implements the following methods:

            'before'
            'before_equal'
            'before_greater'
            'before_lower'
            'after'
            'after_equal'
            'after_greater'
            'after_lower'
            'meets'
            'meets_equal'
            'meets_greater'
            'meets_lower'
            'metby'
            'metby_equal'
            'metby_greater'
            'metby_lower'
            'overlaps'
            'overlaps_equal'
            'overlaps_greater'
            'overlaps_lower'
            'overlappedby'
            'overlappedby_equal'
            'overlappedby_greater'
            'overlappedby_lower'
            'starts'
            'startedby'
            'finishes'
            'finishedby'
            'contains'
            'during'
            'equals'

    So that they are not distinct. Some of them accept parameters so they
    are not exhaustive too.

"""

from sppas.src.structs.basecompare import sppasBaseCompare

from ...anndataexc import AnnDataTypeError
from ...anndataexc import AnnDataValueError

from .point import sppasPoint
from .interval import sppasInterval
from .disjoint import sppasDisjoint
from .duration import sppasDuration

# ---------------------------------------------------------------------------


class sppasIntervalCompare(sppasBaseCompare):
    """SPPAS implementation of interval'comparisons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Includes "Allen's Interval Algebra" and INDU, with several options.

    This class can be used to compare any of the localization-derived classes:

        - sppasInterval(): begin and end points are used,
        - sppasDisjoint(): the first and the last points are used and then it\
        is considered a full interval.
        - sppasPoint(): considered like a degenerated interval.

    """

    def __init__(self):
        """Create a sppasIntervalCompare instance."""
        super(sppasIntervalCompare, self).__init__()

        # Allen
        self.methods['before'] = sppasIntervalCompare.before
        self.methods['after'] = sppasIntervalCompare.after
        self.methods['meets'] = sppasIntervalCompare.meets
        self.methods['metby'] = sppasIntervalCompare.metby
        self.methods['overlaps'] = sppasIntervalCompare.overlaps
        self.methods['overlappedby'] = sppasIntervalCompare.overlappedby
        self.methods['starts'] = sppasIntervalCompare.starts
        self.methods['startedby'] = sppasIntervalCompare.startedby
        self.methods['finishes'] = sppasIntervalCompare.finishes
        self.methods['finishedby'] = sppasIntervalCompare.finishedby
        self.methods['during'] = sppasIntervalCompare.during
        self.methods['contains'] = sppasIntervalCompare.contains
        self.methods['equals'] = sppasIntervalCompare.equals

        # INDU
        self.methods['before_equal'] = sppasIntervalCompare.before_equal
        self.methods['before_greater'] = sppasIntervalCompare.before_greater
        self.methods['before_lower'] = sppasIntervalCompare.before_lower
        self.methods['after_equal'] = sppasIntervalCompare.after_equal
        self.methods['after_greater'] = sppasIntervalCompare.after_greater
        self.methods['after_lower'] = sppasIntervalCompare.after_lower
        self.methods['meets_equal'] = sppasIntervalCompare.meets_equal
        self.methods['meets_greater'] = sppasIntervalCompare.meets_greater
        self.methods['meets_lower'] = sppasIntervalCompare.meets_lower
        self.methods['metby_equal'] = sppasIntervalCompare.metby_equal
        self.methods['metby_greater'] = sppasIntervalCompare.metby_greater
        self.methods['metby_lower'] = sppasIntervalCompare.metby_lower
        self.methods['overlaps_equal'] = sppasIntervalCompare.overlaps_equal
        self.methods['overlaps_greater'] = sppasIntervalCompare.overlaps_greater
        self.methods['overlaps_lower'] = sppasIntervalCompare.overlaps_lower
        self.methods['overlappedby_equal'] = sppasIntervalCompare.overlappedby_equal
        self.methods['overlappedby_greater'] = sppasIntervalCompare.overlappedby_greater
        self.methods['overlappedby_lower'] = sppasIntervalCompare.overlappedby_lower

    # ---------------------------------------------------------------------------

    @staticmethod
    def before(i1, i2, max_delay=None, **kwargs):
        """Return True if i1 precedes i2.

        This is part of the Allen algebra.

        :param i1:  |-------|
        :param i2:                  |-------|
        :param max_delay: (int/float/sppasDuration) Maximum delay between the \
            end of i1 and the beginning of i2.
        :param **kwargs: un-used.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        is_before = x2 < y1
        if is_before is True and max_delay is not None:
            delay = sppasInterval(x2, y1)
            return delay.duration() < max_delay

        return is_before

    # ---------------------------------------------------------------------------

    @staticmethod
    def before_equal(i1, i2, *args):
        """Return True if i1 precedes i2 and the durations are equals.

        This is part of the INDU algebra.

        :param i1:  |-------|
        :param i2:                  |-------|
        :param max_delay: (int/float/sppasDuration) Maximum delay between the \
            end of i1 and the beginning of i2.

        """
        return sppasIntervalCompare.before(i1, i2, *args) and \
               i1.duration() == i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def before_greater(i1, i2, *args):
        """Return True if i1 precedes i2 and the duration of i1 is greater.

        This is part of the INDU algebra.

        :param i1:  |-----------|
        :param i2:                  |-----|
        :param max_delay: (int/float/sppasDuration) Maximum delay between the \
            end of i1 and the beginning of i2.

        """
        return sppasIntervalCompare.before(i1, i2, *args) and \
               i1.duration() > i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def before_lower(i1, i2, *args):
        """Return True if i1 precedes i2 and the duration of i1 is lower.

        This is part of the INDU algebra.

        :param i1:  |-----|
        :param i2:                  |------------|
        :param max_delay: (int/float/sppasDuration) Maximum delay between the \
            end of i1 and the beginning of i2.

        """
        return sppasIntervalCompare.before(i1, i2, *args) and \
               i1.duration() < i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def after(i1, i2, max_delay=None, **kwargs):
        """Return True if i1 follows i2.

        This is part of the Allen algebra.

        :param i1:                  |--------|
        :param i2:  |-------|
        :param max_delay: (int/float/sppasDuration) Maximum delay between \
            the end of i2 and the beginning of i1.
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        is_after = y2 < x1
        if is_after and max_delay is not None:
            interval = sppasInterval(y2, x1)
            return interval.duration() < max_delay

        return is_after

    # ---------------------------------------------------------------------------

    @staticmethod
    def after_equal(i1, i2, *args):
        return sppasIntervalCompare.after(i1, i2, *args) and \
               i1.duration() == i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def after_greater(i1, i2, *args):
        return sppasIntervalCompare.after(i1, i2, *args) and \
               i1.duration() > i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def after_lower(i1, i2, *args):
        return sppasIntervalCompare.after(i1, i2, *args) and \
               i1.duration() < i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def meets(i1, i2, **kwargs):
        """Return True if i1 meets i2.

        :param i1:  |-------|
        :param i2:          |-------|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return not sppasIntervalCompare.equals(i1, i2) and x2 == y1

    # ---------------------------------------------------------------------------

    @staticmethod
    def meets_equal(i1, i2, **kwargs):
        return sppasIntervalCompare.meets(i1, i2) and \
               i1.duration() == i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def meets_greater(i1, i2, **kwargs):
        return sppasIntervalCompare.meets(i1, i2) and \
               i1.duration() > i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def meets_lower(i1, i2, **kwargs):
        return sppasIntervalCompare.meets(i1, i2) and \
               i1.duration() < i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def metby(i1, i2, **kwargs):
        """Return True if i1 is met by i2.

        :param i1:          |-------|
        :param i2:  |-------|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return not sppasIntervalCompare.equals(i1, i2) and x1 == y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def metby_equal(i1, i2, **kwargs):
        return sppasIntervalCompare.metby(i1, i2) and \
               i1.duration() == i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def metby_greater(i1, i2, **kwargs):
        return sppasIntervalCompare.metby(i1, i2) and \
               i1.duration() > i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def metby_lower(i1, i2, **kwargs):
        return sppasIntervalCompare.metby(i1, i2) and \
               i1.duration() < i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlaps(i1, i2, overlap_min=None, percent=False, **kwargs):
        """Return True if i1 overlaps with i2.

        :param i1:  |-------|
        :param i2:      |------|
        :param overlap_min: (int/float/sppasDuration) Minimum duration of the \
            overlap between i1 and i2.
        :param percent: (bool) The min_dur parameter is a percentage of i1, \
            instead of an absolute duration.
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        is_overlap = x1 < y1 < x2 < y2

        if is_overlap and overlap_min is not None:

            overlap_interval = sppasInterval(y1, x2)
            if percent is True:
                # relative duration (min_dur parameter represents a percentage of i1)
                if overlap_min < 0. or overlap_min > 100.:
                    raise AnnDataValueError("min_dur/percentage", overlap_min)
                # relative duration (min_dur parameter represents a percentage of i1)
                v, m = i1.duration().get_value(), i1.duration().get_margin()
                duration = sppasDuration(v * float(overlap_min) / 100., m)
            else:
                # absolute duration
                duration = overlap_min

            return overlap_interval.duration() >= duration

        return is_overlap

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlaps_equal(i1, i2, overlap_min=None, percent=False, **kwargs):
        return sppasIntervalCompare.overlaps(i1, i2, overlap_min, percent) and \
               i1.duration() == i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlaps_greater(i1, i2, overlap_min=None, percent=False, **kwargs):
        return sppasIntervalCompare.overlaps(i1, i2, overlap_min, percent) and \
               i1.duration() > i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlaps_lower(i1, i2, overlap_min=None, percent=False, **kwargs):
        return sppasIntervalCompare.overlaps(i1, i2, overlap_min, percent) and \
               i1.duration() < i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlappedby(i1, i2, overlapped_min=None, percent=False, **kwargs):
        """Return True if i1 overlapped by i2.

        :param i1:      |-------|
        :param i2:  |-------|
        :param overlapped_min: (int/float/sppasDuration) Minimum duration of the
            overlap between i1 and i2.
        :param percent: (bool) The min_dur parameter is a percentage of i1,
            instead of an absolute duration.
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        is_overlap = y1 < x1 < y2 < x2

        if is_overlap and overlapped_min is not None:
            # create an interval of the overlap part.
            overlap_interval = sppasInterval(i1.get_begin(), i2.get_end())
            if percent is True:
                if overlapped_min < 0. or overlapped_min > 100.:
                    raise AnnDataValueError("min_dur/percentage", overlapped_min)
                # relative duration (min_dur parameter represents a percentage of i1)
                v, m = i1.duration().get_value(), i1.duration().get_margin()
                duration = sppasDuration(v * float(overlapped_min) / 100., m)
            else:
                # absolute duration
                # (min_dur parameter represents the minimum duration)
                duration = overlapped_min
            return overlap_interval.duration() >= duration

        return is_overlap

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlappedby_equal(i1, i2, overlapped_min=None, percent=False, **kwargs):
        return sppasIntervalCompare.overlappedby(i1, i2,
                                                 overlapped_min, percent) and \
               i1.duration() == i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlappedby_greater(i1, i2, overlapped_min=None, percent=False, **kwargs):
        return sppasIntervalCompare.overlappedby(i1, i2,
                                                 overlap_min, percent) and \
               i1.duration() > i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def overlappedby_lower(i1, i2, overlapped_min=None, percent=False, **kwargs):
        return sppasIntervalCompare.overlappedby(i1, i2,
                                                 overlap_min, percent) and \
               i1.duration() < i2.duration()

    # ---------------------------------------------------------------------------

    @staticmethod
    def starts(i1, i2, **kwargs):
        """Return True if i1 starts at the start of i2 and finishes within it.

        :param i1:  |----|
        :param i2:  |----------|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 == y1 and x2 < y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def startedby(i1, i2, **kwargs):
        """Return True if i1 is started at the start of i2 interval.

        :param i1:  |----------|
        :param i2:  |----|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 == y1 and y2 < x2

    # ---------------------------------------------------------------------------

    @staticmethod
    def finishes(i1, i2, **kwargs):
        """Return True if i1 finishes the same and starts within of i2.

        :param i1:       |----|
        :param i2:  |---------|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return y1 < x1 and x2 == y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def finishedby(i1, i2, **kwargs):
        """Return True if i1 finishes the same and starts before of i2.

        :param i1:  |---------|
        :param i2:       |----|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 < y1 and x2 == y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def during(i1, i2, **kwargs):
        """Return True if i1 is located during i2.

        :param i1:      |----|
        :param i2:  |------------|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return y1 < x1 and x2 < y2

    # ---------------------------------------------------------------------------

    @staticmethod
    def contains(i1, i2, **kwargs):
        """Return True if i1 contains i2.

        :param i1:  |------------|
        :param i2:      |----|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 < y1 and y2 < x2

    # ---------------------------------------------------------------------------

    @staticmethod
    def equals(i1, i2, **kwargs):
        """Return True if i1 equals i2.

        :param i1:  |-------|
        :param i2:  |-------|
        :param **kwargs: unused.

        """
        x1, x2 = sppasIntervalCompare._unpack(i1)
        y1, y2 = sppasIntervalCompare._unpack(i2)
        return x1 == y1 and x2 == y2

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    @staticmethod
    def _unpack(localization):
        """Return the 2 extremities of a localization."""
        if isinstance(localization, (sppasInterval, sppasDisjoint)):
            return localization.get_begin(), localization.get_end()

        elif isinstance(localization, sppasPoint):
            return localization, localization

        raise AnnDataTypeError(localization, "sppasBaseLocalization")
