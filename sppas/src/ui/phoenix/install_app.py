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

    ui.phoenix.install_app.py
    ~~~~~~~~~~~~~~~~~~~~~~

This is an application for SPPAS, based on the Phoenix API, to install SPPAS
other required programs or packages.

Create and run the application with:

>>> app = sppasInstallApp()
>>> app.run()

"""

import traceback
import wx
import logging

from sppas import sg, cfg
from sppas import sppasLogSetup
from sppas import sppasLogFile
from .main_settings import WxAppSettings
from .install_window import sppasInstallWindow

# ---------------------------------------------------------------------------


class sppasInstallApp(wx.App):
    """Create the SPPAS Phoenix installer application.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Wx Application initialization.

        Create the application for the GUI Install of SPPAS dependencies.

        """
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # Fix application configuration and settings for look&feel
        self.settings = WxAppSettings()
        self.SetAppName(sg.__name__)
        self.SetAppDisplayName(sg.__name__ + " " + sg.__version__)
        wx.SystemOptions.SetOption("mac.window-plain-transition", 1)
        wx.SystemOptions.SetOption("msw.font.no-proof-quality", 0)

        # Fix language and translation
        lang = wx.LANGUAGE_DEFAULT
        self.locale = wx.Locale(lang)

        # Fix logging
        self._logging = sppasLogSetup(cfg.log_level)
        log_report = sppasLogFile(pattern="install")
        self._logging.file_handler(log_report.get_filename())

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def run(self):
        """Run the application and starts the main loop.

        :returns: (int) Exit status

        """
        try:
            # Create the main frame of the application and show it.
            window = sppasInstallWindow()
            self.SetTopWindow(window)
            self.MainLoop()

        except Exception as e:
            # All exception messages of SPPAS are normalized.
            # We assign the error number at the exit status
            msg = str(e)
            error = -1
            if msg.startswith(":ERROR "):
                logging.error(msg)
                try:
                    msg = msg[msg.index(" "):]
                    if ':' in msg:
                        msg = msg[:msg.index(":")]
                        error = int(msg)
                except:
                    logging.error(traceback.format_exc())
                    pass
            else:
                logging.error(traceback.format_exc())
            return error

        return 0

    # -----------------------------------------------------------------------

    def OnExit(self):
        """Override the already existing method to kill the app.

        This method is invoked when the user:

            - clicks on the [X] button of the frame manager
            - does "ALT-F4" (WindowsInstaller) or CTRL+X (Unix)
            - click on a custom 'exit' button

        In case of crash or SIGKILL (or bug!) this method is not invoked.

        """
        logging.info('Exit the wx.App() of {:s}.'.format(sg.__name__))

        if self.HasPendingEvents() is True:
            self.DeletePendingEvents()

        # Save settings
        self.settings.save()
        cfg.save()

        # then it will exit. Nothing special to do. Return the exit status.
        return 0
