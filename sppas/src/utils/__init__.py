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

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

*****************************************************************************
utils: utility classes.
*****************************************************************************

This package includes any utility class to extend python features.
Currently, it implements a class to manage identically unicode data
with all versions of python. It also includes a comparator of data
which is very powerful for lists and dictionaries, a bidirectional
dictionary, a representation of time, etc.

Requires the following other packages:

* config

"""

from .datatype import sppasTime
from .datatype import sppasType
from .datatype import bidict
from .compare import sppasCompare
from .makeunicode import u, b
from .makeunicode import sppasUnicode

__all__ = (
    "sppasTime",
    "sppasType",
    "sppasCompare",
    "sppasUnicode",
    "u",
    "b",
    "bidict"
)
