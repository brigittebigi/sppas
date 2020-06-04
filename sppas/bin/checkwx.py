#!/usr/bin/env python
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

    bin.checkwx.py
    ~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Check wxpython, required (only) to use the GUI.

    Status is:

        - -1 if wxpython is not installed
        - 0 if wxpython is installed and is the right one
        - 1 if wxpython is installed and not the right one
        - 2 for an unknown error

"""

import sys

try:
    import wx
except ImportError:
    sys.exit(-1)


if __name__ == "__main__":

    # Version of python
    py = 2
    if sys.version_info >= (3, 0):
        py = 3

    # Version of wxpython
    try:
        wxv = wx.version().split()[0]
    except Exception:
        sys.exit(2)
    version = int(wxv[0])

    # Match between Python and WxPython
    if py == 3 and version == 4:
        sys.exit(0)
    if py == 2 and version == 3:
        sys.exit(0)

    sys.exit(1)
