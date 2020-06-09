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

    __main__.py
    ~~~~~~~~~~~~~~~

    In Python, '__main__' is the name of the scope in which top-level code
    executes. Within SPPAS, it allows to launch the Graphical User Interface.

    To launch the GUI, it allows the followings 3 possibilities:

    >>> python3 -m sppas
    >>> python3 sppas
    >>> python3 sppas/__main__.py

"""

import sys
import time
import os

if sys.version_info < (3, 6):
    print("The version of Python is not the right one. "
          "This program requires at least version 3.6.")
    time.sleep(5)
    sys.exit(-1)

try:
    import wx
except ImportError:
    msg = "WxPython is not installed on your system.\n"\
          "The Graphical User Interface of SPPAS can't work."
    print("[ ERROR ] {:s}".format(msg))
    print("SPPAS exits with error status: -1")
    time.sleep(5)
    sys.exit(-1)

v = wx.version().split()[0][0]
if v != '4':
    print("The version of wxPython is too old. "
          "This program requires at least version 4.x.")
    time.sleep(5)
    sys.exit(-1)

if __package__ is None or len(__package__) == 0:
    dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, dir)
    __package__ = "sppas"

from sppas import *
from sppas.src.ui.phoenix.main_app import sppasApp

# Create and run the wx application
app = sppasApp()
status = app.run()
if status != 0:
    print("Program exited with error status: {:d}".format(status))
sys.exit(status)
