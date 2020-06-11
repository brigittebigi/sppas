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

    bin.sppasgui.py
    ~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This is the deprecated program to execute the Graphical User Interface of SPPAS.

"""

import os
import traceback
from argparse import ArgumentParser
import sys
import time
from os import path, getcwd
import subprocess

PROGRAM = path.abspath(__file__)
SPPAS = path.dirname(path.dirname(path.dirname(PROGRAM)))
sys.path.append(SPPAS)

# ----------------------------------------------------------------------------

EXIT_DELAY = 6
EXIT_STATUS = 1

# ----------------------------------------------------------------------------


def exit_error(msg="Unknown."):
    """Exit the program with status 1 and an error message.

    :param msg: (str) Message to print on stdout.

    """
    print("[ ERROR ] {:s}".format(msg))
    time.sleep(EXIT_DELAY)
    sys.exit(EXIT_STATUS)

# ----------------------------------------------------------------------------


def check_aligner():
    """Test if one of julius/HVite is available.

    :returns: False if none of them are available.

    """
    julius = True
    hvite = True
    try:
        NULL = open(os.devnull, "r")
        subprocess.call(['julius'], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        julius = False

    try:
        NULL = open(os.devnull, "r")
        subprocess.call(['HVite'], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        hvite = False

    return julius or hvite

# ----------------------------------------------------------------------------


if sys.version_info > (2, 8):
    msg = "Python is not the right one for this [deprecated] program.\n"
    msg += "This program requires version 2.7.\n"
    if sys.version_info > (3, 5):
        msg += "To execute SPPAS GUI for Python 3, launch: python -m sppas"
    else:
        msg += "The new SPPAS GUI is compatible with Python >3.6+."
    exit_error(msg)
    time.sleep(5)
    sys.exit(-1)

try:
    import wx
    v = wx.version().split()[0][0]
    if v != '3':
        raise ImportError
except ImportError:
    exit_error("WxPython is not installed on your system or the version is"
               "not the right one.\nThe Graphical User Interface can't work.")

# ---------------------------------------------------------------------------

try:
    from sppas.src.config import sppasLogSetup
    from sppas.src.ui.wxgui import SETTINGS_FILE
    from sppas.src.ui.wxgui.frames.mainframe import FrameSPPAS
    from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation
    from sppas.src.ui.wxgui.structs.prefs import Preferences_IO
    from sppas.src.ui.wxgui.structs.theme import sppasTheme
except Exception as e:
    print(str(e))
    exit_error("An unexpected error occurred.\n"
               "Verify the installation of SPPAS and try again. "
               "The error message is: %s" % traceback.format_exc())

# Arguments
# -------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} files".format(path.basename(PROGRAM)),
                        description="SPPAS Graphical User Interface.")
parser.add_argument("files", nargs="*", help='Input audio file name(s)')
args = parser.parse_args()

# force to add path
filenames = []
for f in args.files:
    p, b = path.split(f)
    if not p:
        p = getcwd()
    filenames.append(path.abspath(path.join(p, b)))

# Logging
# ----------------------------------------------------------------------------

applogging = sppasLogSetup(5)
applogging.stream_handler()

# Application:
# ----------------------------------------------------------------------------

sppas = wx.App(redirect=False, useBestVisual=True, clearSigInt=True)

# Fix language and translation
lang = wx.LANGUAGE_DEFAULT
locale = wx.Locale(lang)

# Fix preferences
prefsIO = Preferences_IO(SETTINGS_FILE)
if prefsIO.Read() is False:
    prefsIO.SetTheme(sppasTheme())

# Tests
if v == '2':
    message = "The version of WxPython is too old.\n" \
              "The Graphical User Interface will not display properly.\n"
    ShowInformation(None, prefsIO, message, style=wx.ICON_WARNING)

if check_aligner() is False:
    ShowInformation(None, prefsIO,
                    'None of julius or HVite is installed on your system.\n'
                    'The Alignment automatic annotation WONT WORK normally.',
                    style=wx.ICON_ERROR)

# Main frame
# ----------------------------------------------------------------------------

frame = FrameSPPAS(prefsIO)
if len(filenames) > 0:
    frame.flp.RefreshTree(filenames)

sppas.SetTopWindow(frame)
sppas.MainLoop()
