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

    structs.basecompare.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.exceptions import sppasValueError

# ---------------------------------------------------------------------------


class sppasBaseCompare(object):
    """Base class for comparisons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Constructor of a sppasBaseCompare."""
        self.methods = dict()

    # -----------------------------------------------------------------------

    def get(self, name):
        """Return the function of the given name.

        :param name: (str) Simple name of a method of this class

        """
        if name in self.methods:
            return self.methods[name]
        raise sppasValueError(name, "function name")

    # -----------------------------------------------------------------------

    def get_function_names(self):
        """Return the list of comparison functions."""
        return list(self.methods.keys())
