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

    anndata.annloc.location.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import copy

from ...anndataexc import AnnDataTypeError
from .localization import sppasBaseLocalization

# ---------------------------------------------------------------------------


class sppasLocation(object):
    """Location of the annotations of a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    sppasLocation allows to store a set of localizations with their scores.
    This class is using a list of lists, i.e. a list of pairs (localization,
    score). This is the best compromise between memory usage, speed and
    readability.

    """

    def __init__(self, localization=None, score=None):
        """Create a new sppasLocation instance and add the entry.

        :param localization: (Localization or list of localizations)
        :param score: (float or list of float)

        If a list of alternative localizations are given, the same score
        is assigned to all items.

        """
        self.__localizations = list()

        if localization is not None:
            if isinstance(localization, list):
                if isinstance(score, list) and len(localization) == len(score):
                    for l, s in zip(localization, score):
                        self.append(l, s)
                else:
                    for loc in localization:
                        self.append(loc, 1./len(localization))
            else:
                self.append(localization, score)

    # -----------------------------------------------------------------------

    def append(self, localization, score=None):
        """Add a localization into the list.

        :param localization: (Localization) the localization to append
        :param score: (float)

        """
        if isinstance(localization, sppasBaseLocalization) is False:
            raise AnnDataTypeError(localization, "sppasBaseLocalization")

        if localization not in self.__localizations:
            # check types consistency.
            if len(self.__localizations) > 0:
                if self.is_point() != localization.is_point():
                    raise AnnDataTypeError(localization, "sppasPoint")
                if self.is_interval() != localization.is_interval():
                    raise AnnDataTypeError(localization, "sppasInterval")
                if self.is_disjoint() != localization.is_disjoint():
                    raise AnnDataTypeError(localization, "sppasDisjoint")

            self.__localizations.append([localization, score])

    # -----------------------------------------------------------------------

    def remove(self, localization):
        """Remove a localization of the list.

        :param localization: (sppasLocalization) the loc to be removed

        """
        if isinstance(localization, sppasBaseLocalization) is False:
            raise AnnDataTypeError(localization, "sppasBaseLocalization")

        if len(self.__localizations) == 1:
            self.__localizations = list()
        else:
            for l in self.__localizations:
                if l[0] == localization:
                    self.__localizations.remove(l)

    # -----------------------------------------------------------------------

    def get_score(self, loc):
        """Return the score of a localization or None if it is not in.

        :param loc: (sppasLocalization)
        :returns: score: (float)

        """
        if not isinstance(loc, sppasBaseLocalization):
            raise AnnDataTypeError(loc, "sppasLocalization")

        for l in self.__localizations:
            if l[0] == loc:
                return l[1]

        return None

    # -----------------------------------------------------------------------

    def set_score(self, loc, score):
        """Set a score to a given localization.

        :param loc: (sppasLocalization)
        :param score: (float)

        """
        if not isinstance(loc, sppasBaseLocalization):
            raise AnnDataTypeError(loc, "sppasLocalization")

        if self.__localizations is not None:
            for i, l in enumerate(self.__localizations):
                if l[0] == loc:
                    self.__localizations[i][1] = score

    # -----------------------------------------------------------------------

    def get_best(self):
        """Return a copy of the best localization.

        :returns: (sppasLocalization) localization with the highest score.

        """
        if len(self.__localizations) == 1:
            return self.__localizations[0][0]

        _max_t = self.__localizations[0][0]
        _max_score = self.__localizations[0][1]
        for (t, s) in reversed(self.__localizations):
            if _max_score is None or (s is not None and s > _max_score):
                _max_score = s
                _max_t = t

        return _max_t.copy()

    # -----------------------------------------------------------------------

    def is_point(self):
        """Return True if the location is made of sppasPoint localizations."""
        return self.__localizations[0][0].is_point()

    # -----------------------------------------------------------------------

    def is_interval(self):
        """Return True if the location is made of sppasInterval locs."""
        return self.__localizations[0][0].is_interval()

    # -----------------------------------------------------------------------

    def is_disjoint(self):
        """Return True if the location is made of sppasDisjoint locs."""
        return self.__localizations[0][0].is_disjoint()

    # -----------------------------------------------------------------------

    def contains(self, point):
        """Return True if the localization point is in the list."""
        if self.is_point():
            return any([point == l[0] for l in self.__localizations])
        else:
            return any([l[0].is_bound(point) for l in self.__localizations])

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of the location."""
        return copy.deepcopy(self)

    # -----------------------------------------------------------------------

    def match_duration(self, dur_functions, logic_bool="and"):
        """Return True if a duration matches all or any of the functions.

        :param dur_functions: list of (function, value, logical_not)
        :param logic_bool: (str) Apply a logical "and" or "or"
        :returns: (bool)

        - function: a function in python with 2 arguments: dur/value
        - value: the expected value for the duration (int/float/sppasDuration)
        - logical_not: boolean

        :Example: Search if a duration is exactly 30ms

            >>> d.match([(eq, 0.03, False)])

        :Example: Search if a duration is not 30ms

            >>> d.match([(eq, 0.03, True)])
            >>> d.match([(ne, 0.03, False)])

        :Example: Search if a duration is comprised between 0.3 and 0.7
            >>> l.match([(ge, 0.03, False),
            >>>          (le, 0.07, False)], logic_bool="and")

        See sppasDurationCompare() to get a list of functions.

        """
        is_matching = False

        # any localization can match
        for loc, score in self.__localizations:

            dur = loc.duration()
            matches = list()
            for func, value, logical_not in dur_functions:
                if logical_not is True:
                    matches.append(not func(dur, value))
                else:
                    matches.append(func(dur, value))

            if logic_bool == "and":
                is_matching = all(matches)
            else:
                is_matching = any(matches)

            # no need to test the next locs if the current one is matching.
            if is_matching is True:
                return True

        return is_matching

    # -----------------------------------------------------------------------

    def match_localization(self, loc_functions, logic_bool="and"):
        """Return True if a localization matches all or any of the functions.

        :param loc_functions: list of (function, value, logical_not)
        :param logic_bool: (str) Apply a logical "and" or a logical "or"
        between the functions.
        :returns: (bool)

        - function: a function in python with 2 arguments: loc/value
        - value: the expected value for the localization (int/float/sppasPoint)
        - logical_not: boolean

        :Example: Search if a localization is after (or starts at) 1 minutes

            >>> l.match([(rangefrom, 60., False)])

        :Example: Search if a localization is before (or ends at) 3 minutes

            >>> l.match([(rangeto, 180., True)])

        :Example: Search if a localization is between 1 min and 3 min

            >>> l.match([(rangefrom, 60., False),
            >>>          (rangeto, 180., False)], logic_bool="and")

        See sppasLocalizationCompare() to get a list of functions.

        """
        is_matching = False

        # any localization can match
        for loc, score in self.__localizations:

            matches = list()
            for func, value, logical_not in loc_functions:
                if logical_not is True:
                    matches.append(not func(loc, value))
                else:
                    matches.append(func(loc, value))

            if logic_bool == "and":
                is_matching = all(matches)
            else:
                is_matching = any(matches)

            # no need to test the next locs if the current one is matching.
            if is_matching is True:
                return True

        return is_matching

    # -----------------------------------------------------------------------

    def set_radius(self, radius):
        """Set a radius value to all localizations.

        :param radius: (int, float) New radius value
        :raise: AnnDataTypeError, AnnDataNegValueError

        """
        for t, s in self.__localizations:
            t.set_radius(radius)

    # -----------------------------------------------------------------------

    def shift(self, delay):
        """Shift the location to a given delay.

        :param delay: (int, float) delay to shift all localizations
        :raise: AnnDataTypeError

        """
        for loc, score in self.__localizations:
            loc.shift(delay)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self, *args, **kwargs):
        st = ""
        for t, s in self.__localizations:
            st += "sppasLocalization({!s:s}, score={:s}), ".format(t, s)
        return st

    # ------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        st = ""
        for t, s in self.__localizations:
            st += "{!s:s}, {!s:s} ; ".format(t, s)
        return st

    # -----------------------------------------------------------------------

    def __iter__(self):
        for l in self.__localizations:
            yield l

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__localizations[i]

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__localizations)

    # -----------------------------------------------------------------------

    def __eq__(self, other):

        if len(self.__localizations) != len(other):
            return False
        for (l1, l2) in zip(self.__localizations, other):
            if l1[0] != l2[0]:
                return False
            if l1[1] != l2[1]:
                return False

        return True

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        return not self == other
