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

    src.wkps.filebase.py
    ~~~~~~~~~~~~~~~~~~~~~

"""
import os
from sppas.src.utils import sppasUnicode

# ---------------------------------------------------------------------------


class FileBase(object):
    """Represent any type of data linked to a filename.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, identifier):
        """Constructor of a FileBase.

        Data structure to store an identifier (str) and a state (States).

        :param identifier: (str) Any un-modifiable string.

        """
        self.__id = FileBase.validate_id(identifier)
        self._state = States().UNUSED

    # -----------------------------------------------------------------------

    @staticmethod
    def validate_id(identifier):
        """Return the given identifier if it matches the requirements.

        An identifier should contain between 3 and 36 characters.

        :param identifier: (str) Key to be validated
        :raise: ValueError
        :returns: (unicode)

        """
        su = sppasUnicode(identifier)
        ide = su.unicode().strip()

        if len(ide) < 1:
            raise ValueError('An identifier must contain at least 2 characters.')

        return ide

    # -----------------------------------------------------------------------

    def get_id(self):
        """Return the identifier (str)."""
        return self.__id

    # -----------------------------------------------------------------------

    def get_state(self):
        """Return the state (States)."""
        return self._state

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Set a state (to be overridden).

        :param value: (States) The state value to assign
        :returns: (bool or list)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def match(self, functions, logic_bool="and"):
        """Return True if the file matches all or any of the functions.

        Functions are defined in a comparator. They return a boolean.
        The type of the value depends on the function.
        The logical not is used to reverse the result of the function.

        :param functions: list of (function, value, logical_not)
        :param logic_bool: (str) Apply a logical "and" or a logical "or" between the functions.
        :returns: (bool)

        """
        matches = list()
        for func, value, logical_not in functions:
            if logical_not is True:
                matches.append(not func(self, value))
            else:
                matches.append(func(self, value))

        if logic_bool == "and":
            is_matching = all(matches)
        else:
            is_matching = any(matches)

        return is_matching

    # -----------------------------------------------------------------------

    def serialize(self):
        """Return a dict representing this instance for json format."""
        d = dict()
        d['id'] = self.id.split(os.sep)[-1]
        d['state'] = int(self.get_state())
        return d

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    id = property(get_id, None)
    state = property(get_state, set_state)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        """Allow to show the class at a given format.

        :param fmt: (str) the wanted format of string
        :returns: (str)

        """
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __str__(self):
        """The string conversion of the object.

        :returns: (str)

        """
        return '{!s:s}'.format(self.__id)

    # -----------------------------------------------------------------------

    def __repr__(self):
        """Function called by print.

        :returns: (str) Printed representation of the object.

        """
        return 'File: {!s:s}'.format(self.__id)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Allows to compare self with other by using "==".

        :param other: (FileName, str)

        """
        if other is not None:
            if isinstance(other, FileBase):
                return self.id == other.id
            else:
                return self.id == other
        return False

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        if other is not None:
            return not self == other
        return False

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """Allows to compare self with other by using ">".

        Can be used, for example, to sort a list of FileName() instances
        alphabetically.

        :param other: (FileName, str)

        """
        if other is not None:
            return self.id > other.id
        return False

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """Allows to compare self with other by using "<".

        Can be used, for example, to sort a list of FileName() instances
        alphabetically.

        :param other: (FileName, str)

        """
        if other is not None:
            return self.id < other.id
        return False

# ---------------------------------------------------------------------------


class States(object):
    """All states of any FileBase.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :Example:

        >>>with States() as s:
        >>>    print(s.UNUSED)

    This class is a solution to mimic an 'Enum' but is compatible with both
    Python 2.7 and Python 3+.

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            UNUSED=0,
            CHECKED=1,
            LOCKED=2,
            AT_LEAST_ONE_CHECKED=3,
            AT_LEAST_ONE_LOCKED=4
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass
