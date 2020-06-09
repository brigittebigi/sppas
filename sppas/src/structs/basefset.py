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

    structs.basefset.py
    ~~~~~~~~~~~~~~~~~~~

    Base class for the result of any kind of SPPAS filter.

"""

import collections
from sppas.src.exceptions import sppasTypeError

# ---------------------------------------------------------------------------


class sppasBaseSet(object):
    """Manager for a set of data.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Mainly used with the data that are the result of the filter system.

    A sppasBaseSet() manages a dictionary with:

        - key: an object
        - value: a list of strings

    It implements the operators '|' and '&'.

    """

    def __init__(self):
        """Create a sppasBaseSet instance."""
        self._data_set = collections.OrderedDict()

    # -----------------------------------------------------------------------

    def get_value(self, data):
        """Return the string value corresponding to a data.

        :param data: (object)
        :returns: (list of str) the string value to associate to the data.

        """
        return self._data_set.get(data, None)

    # -----------------------------------------------------------------------

    def append(self, data, value):
        """Append a data in the data set, with the given value.

        :param data: (object)
        :param value: (list of str) List of any string.

        """
        if value is None:
            raise sppasTypeError(value, "list")
        if isinstance(value, list) is False:
            raise sppasTypeError(value, "list")

        if data in self._data_set:
            old_value_list = self._data_set[data]
            self._data_set[data] = list(set(old_value_list + value))
        else:
            self._data_set[data] = value

    # -----------------------------------------------------------------------

    def remove(self, data):
        """Remove the data of the data set.

        :param data: (object)

        """
        if data in self._data_set:
            del self._data_set[data]

    # -----------------------------------------------------------------------

    def copy(self):
        """Make a deep copy of self."""
        d = sppasBaseSet()
        for data, value in self._data_set.items():
            d.append(data, value)

        return d

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __iter__(self):
        for data in list(self._data_set.keys()):
            yield data

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._data_set)

    # -----------------------------------------------------------------------

    def __contains__(self, data):
        return data in self._data_set

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Check if data sets are equals, i.e. share the same data."""
        # check len
        if len(self) != len(other):
            return False

        # check keys and values
        for key, value in self._data_set.items():
            if key not in other:
                return False
            other_value = other.get_value(key)
            if set(other_value) != set(value):
                return False

        return True

    # -----------------------------------------------------------------------
    # Operators
    # -----------------------------------------------------------------------

    def __or__(self, other):
        """Implements the '|' operator between 2 data sets.

        The operator '|' does the intersection operation.

        """
        d = self.copy()
        for data in other:
            d.append(data, other.get_value(data))

        return d

    # -----------------------------------------------------------------------

    def __and__(self, other):
        """Implements the '&' operator between 2 data sets.

        The operator '&' does the union operation.

        """
        d = sppasBaseSet()
        for data in self:
            if data in other:
                d.append(data, self.get_value(data))
                d.append(data, other.get_value(data))

        return d
