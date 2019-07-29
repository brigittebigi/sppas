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

    src.utils.makeunicode
    ~~~~~~~~~~~~~~~~~~~~~

makeunicode is useful for the compatibility of strings between
Python 2.7 and Python > 3.2.

>>> token = "  \n Ỹ  \t\r   ỏ  "
>>> sp = sppasUnicode(token)
>>> token = sp.to_strip()
>>> token == u('Ỹ ỏ')
>>> True

"""

from __future__ import unicode_literals
import sys
import re

from sppas.src.config import sg
from .utilsexc import UtilsDataTypeError

# ---------------------------------------------------------------------------

"""Unicode conversion for Python 2.7."""

if sys.version_info < (3,):

    text_type = unicode
    binary_type = str
    basestring = basestring

    def u(x):
        """Convert to unicode using decode().

        :param x: a string
        :returns: a unicode string

        """
        # here we take care to not raise "AttributeError", like:
        # AttributeError: 'int' object has no attribute 'decode'
        s = str(x)
        try:
            return s.decode(sg.__encoding__)
        except UnicodeDecodeError:
            return s

    def b(x):
        """Convert to byte using encode().

        :param x: a unicode string
        :returns: a string

        """
        s = str(x)
        try:
            return s.encode(sg.__encoding__)
        except UnicodeDecodeError:
            return s

else:
    """Unicode conversion for Python > 3.2 """

    text_type = str
    binary_type = bytes
    basestring = str

    def u(x):
        """Convert to unicode (i.e. do nothing).

        :param x: a string
        :returns: a unicode string

        """
        return str(x)

    def b(x):
        """Convert to byte using encode().

        :param x: a unicode string
        :returns: a string

        """
        s = str(x)
        return s.encode(sg.__encoding__)


# ---------------------------------------------------------------------------


class sppasUnicode(object):
    """Make a string as unicode and operates on it.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, entry):
        """Create a sppasUnicode instance.

        :param entry: (str or unicode or bytes in python 2)

        """
        if isinstance(entry, (binary_type, text_type)) is False:
            raise UtilsDataTypeError(entry, "str", type(entry))
        self._entry = entry

    # -----------------------------------------------------------------------

    def unicode(self):
        """Return the unicode string of the given entry.

        :returns: unicode

        """
        e = self._entry
        if isinstance(self._entry, binary_type):
            e = u(self._entry)
        return e

    # -----------------------------------------------------------------------

    def to_lower(self):
        """Return the unicode string with lower case.

        :returns: unicode

        """
        e = self.unicode()
        self._entry = e.lower()

        return self._entry

    # -----------------------------------------------------------------------

    def to_strip(self):
        """Strip the string.

        Remove also multiple whitespace, tab and CR/LF inside the string.

        :returns: unicode

        """
        # Remove multiple whitespace
        e = self.unicode()
        self._entry = re.sub("[\s]+", r" ", e)

        # Remove whitespace at beginning and end
        if self._entry.startswith(" "):
            self._entry = re.sub("^[ ]+", r"", self._entry)
        if self._entry.endswith(' '):
            self._entry = re.sub("[ ]+$", r"", self._entry)
        if "\ufeff" in self._entry:
            self._entry = re.sub("\ufeff", r"", self._entry)

        return self._entry

    # ----------------------------------------------------------------------------

    def clear_whitespace(self):
        """Replace the whitespace by underscores.

        :returns: unicode

        """
        e = self.to_strip()
        e = re.sub('\s', r'_', e)
        self._entry = e

        return self._entry

    # ------------------------------------------------------------------------

    def to_ascii(self):
        """Replace the non-ASCII characters by underscores.

        :returns: unicode

        """
        e = self.unicode()
        e = re.sub(r'[^\x00-\x7F]', "_", e)
        self._entry = e

        return self._entry

    # ------------------------------------------------------------------------

    def is_restricted_ascii(self):
        """Check if the entry key is using only a-Z_ characters.

        :returns: (bool)

        """
        ra = re.sub(r'[^a-zA-Z0-9_]', '', self._entry)
        return self._entry == ra
