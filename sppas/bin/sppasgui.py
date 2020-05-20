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
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This is the main program to execute the Graphical User Interface of SPPAS.

"""

import logging
import traceback
from argparse import ArgumentParser
import sys
import time
from os import path, getcwd

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

try:
    import wx
except ImportError:
    exit_error("WxPython is not installed on your system\n."
               "The Graphical User Interface of SPPAS can't work.")

# ---------------------------------------------------------------------------
# If Phoenix is installed...
# ---------------------------------------------------------------------------

v = wx.version().split()[0][0]
if v == '4':
    try:
        from sppas.src.ui.phoenix.main_app import sppasApp
    except:
        exit_error("An unexpected error occurred.\n"
                   "Verify the the installation of SPPAS and try again.\n"
                   "The full error message is: %s" % traceback.format_exc())

    # Create and run the wx application
    app = sppasApp()
    status = app.run()
    if status != 0:
        print("SPPAS exits with error status: {:d}"
              "".format(status))
    sys.exit(status)

# ---------------------------------------------------------------------------
# If wxPython3 is installed...
# ---------------------------------------------------------------------------


try:
    from sppas.src.ui.wxgui import SETTINGS_FILE
    from sppas.src.ui.wxgui.frames.mainframe import FrameSPPAS
    from sppas.bin import check_aligner
    from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation
    from sppas.src.ui.wxgui.structs.prefs import Preferences_IO
    from sppas.src.ui.wxgui.structs.theme import sppasTheme
    from sppas import sppasLogSetup  #, sppasLogFile
    # from sppas import sppasAppConfig
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
