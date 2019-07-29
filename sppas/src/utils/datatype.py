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

    utils.datatype.py
    ~~~~~~~~~~~~~~~~~

"""

import time

from .utilsexc import UtilsDataTypeError

# ---------------------------------------------------------------------------


class bidict(dict):
    """A simple bidirectional dictionary.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Implements a 1:1 dictionary.
    It implies that two keys can't have the same value.

    >>> relation = bidict()
    >>> relation['Alice'] = 'Bob'
    >>> print(relation['Bob'])
    >>> 'Alice'
    >>> print(relation['Alice'])
    >>> 'Bob'

    """

    def __init__(self, *args, **kwargs):
        super(bidict, self).__init__(*args, **kwargs)

        # add all value=key in the dictionary
        inverse = dict()
        for key in self:
            inverse[self[key]] = key
        self.update(inverse)

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        super(bidict, self).__setitem__(key, value)
        super(bidict, self).__setitem__(value, key)

    def __delitem__(self, key):
        value = self[key]
        super(bidict, self).__delitem__(key)
        super(bidict, self).__delitem__(value)

# ---------------------------------------------------------------------------


class sppasTime(object):
    """Utility class to represent date time with a string.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    How SPPAS works with the date...

    """

    def __init__(self, now=None):
        """Create a sppasTime() instance.

        Given time must be formatted exactly like:
        '%Y-%m-%dT%H:%M:%S{:0=+3d}:{:0=2d}'

        :param now: (str) String representing the current time

        :Example:

        >>> p = sppasTime('2018-04-09T15:00:37+02:00')
        >>> p.now
        >>> '2018-04-09T15:00:37+02:00'
        >>> p.gmt
        >>> '+02:00'

        """
        # Fix now
        if now is None:
            ctz = -time.altzone if time.localtime(time.time()).tm_isdst and \
                                   time.daylight else -time.timezone
            self.now = time.strftime('%Y-%m-%dT%H:%M:%S{:0=+3d}:{:0=2d}'
                                     '').format(ctz // 3600, ctz % 3600)
        else:
            self.now = now

        # Fix other members from now
        if 'T' not in self.now or \
           '-' not in self.now or \
           ":" not in self.now:
            raise UtilsDataTypeError("sppasTime(now)",
                                     "%Y-%m-%dT%H:%M:%S{:0=+3d}:{:0=2d}", now)

        try:
            self.year = self.now.split('T')[0].split('-')[0]
            self.month = self.now.split('T')[0].split('-')[1]
            self.day = self.now.split('T')[0].split('-')[2]
            self.hours = self.now.split('T')[1].split(':')[0]
            self.min = self.now.split('T')[1].split(':')[1]
            self.sec = self.now[-8:-6]
            self.gmt = self.now[-6:]
        except IndexError:
            raise UtilsDataTypeError("sppasTime(now)",
                                     "%Y-%m-%dT%H:%M:%S{:0=+3d}:{:0=2d}", now)

# ---------------------------------------------------------------------------


class sppasType(object):
    """Utility class to check data type.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def is_bool(entry):
        """Check if the entry is boolean.

        :param entry: (any type)
        :returns: (bool)

        """
        return str(entry) in ['True', 'False']

    # -----------------------------------------------------------------------

    @staticmethod
    def is_number(entry):
        """Check if the entry is numeric.

        :param entry: (any type)
        :returns: (bool)

        """
        try:
            float(entry)
            return True
        except (TypeError, ValueError):
            pass

        try:
            import unicodedata
            unicodedata.numeric(entry)
            return True
        except (TypeError, ValueError):
            pass

        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def is_dict(entry):
        """Check if the entry is of any type of dictionary.

        :param entry: (any type)
        :returns: (bool)

        """
        if type(entry) is dict:
            return True

        if "collections." in str(type(entry)):
            return True

        return False
