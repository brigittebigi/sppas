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
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

*****************************************************************************
exceptions: global exceptions of this software.
*****************************************************************************

This package includes classes to fix all global exceptions.
Requires the following other packages:

* config

"""

from .exc import sppasError               # 0000
from .exc import sppasTypeError           # 0100
from .exc import sppasIndexError          # 0200
from .exc import sppasValueError          # 0300
from .exc import sppasKeyError            # 0400
from .exc import sppasInstallationError   # 0510
from .exc import sppasEnableFeatureError  # 0520

from .exc import NegativeValueError       # 0310
from .exc import RangeBoundsException     # 0320
from .exc import IntervalRangeException   # 0330
from .exc import IndexRangeException      # 0340

from .exc import IOExtensionError         # 0610
from .exc import NoDirectoryError         # 0620

# ---------------------------------------------------------------------------


__all__ = (
    "sppasError",
    "sppasTypeError",
    "sppasIndexError",
    "sppasValueError",
    "sppasKeyError",
    "sppasInstallationError",
    "sppasEnableFeatureError",
    "NegativeValueError",
    "RangeBoundsException",
    "IntervalRangeException",
    "IndexRangeException",
    "IOExtensionError",
    "NoDirectoryError"
)
