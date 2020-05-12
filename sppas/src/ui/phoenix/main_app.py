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

    ui.phoenix.main_app.py
    ~~~~~~~~~~~~~~~~~~~~~~

This is the main application for SPPAS, based on the Phoenix API.
Create and run the application:

>>> app = sppasApp()
>>> app.run()

"""

import traceback
import time
import wx
import logging
from os import path
from argparse import ArgumentParser
try:
    import wx.adv
    adv_import = True
except ImportError:
    adv_import = False

from sppas import sg, cfg
from .main_settings import WxAppSettings
from .main_window import sppasMainWindow
from .tools import sppasSwissKnife

from sppas.src.config.logs import sppasLogSetup

# ---------------------------------------------------------------------------


class sppasApp(wx.App):
    """Create the SPPAS Phoenix application.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Wx Application initialization.

        Create the application for the GUI of SPPAS based on Phoenix.

        """
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        self.SetAppName(sg.__name__)
        self.SetAppDisplayName(sg.__name__ + " " + sg.__version__)
        wx.SystemOptions.SetOption("mac.window-plain-transition", 1)
        wx.SystemOptions.SetOption("msw.font.no-proof-quality", 0)

        # Fix language and translation
        lang = wx.LANGUAGE_DEFAULT
        self.locale = wx.Locale(lang)

        # Fix logging. Notice that Settings will be fixed at 'run'.
        self.settings = None
        self._logging = None
        self.process_command_line_args()
        self.setup_python_logging()

    # -----------------------------------------------------------------------
    # Methods to configure and starts the app
    # -----------------------------------------------------------------------

    def process_command_line_args(self):
        """Process the command line.

        This is an opportunity for users to fix some args.

        """
        # create a parser for the command-line arguments
        parser = ArgumentParser(
            usage="{:s} [options]".format(path.basename(__file__)),
            description="... " + sg.__name__ + " " + sg.__title__)

        # add arguments here
        parser.add_argument("-l", "--log_level",
                            required=False,
                            type=int,
                            default=cfg.log_level,
                            help='Log level (default={:d}).'
                                 ''.format(cfg.log_level))

        # add arguments here
        parser.add_argument("-s", "--splash_delay",
                            required=False,
                            type=int,
                            default=cfg.splash_delay,
                            help='Splash delay (default={:d}).'
                                 ''.format(cfg.splash_delay))

        # then parse
        args = parser.parse_args()

        # and do things with arguments
        cfg.log_level = args.log_level
        cfg.splash_delay = args.splash_delay

    # -----------------------------------------------------------------------

    def setup_python_logging(self):
        """Setup python logging to the standard stream handler."""
        self._logging = sppasLogSetup(cfg.log_level)
        self._logging.stream_handler()

    # -----------------------------------------------------------------------

    def show_splash_screen(self):
        """Create and show the splash image.

        It is supposed that wx.adv is available (test it first!).

        """
        delay = cfg.splash_delay
        if delay <= 0:
            return None

        bitmap = sppasSwissKnife.get_bmp_image('splash')
        splash = wx.adv.SplashScreen(
            bitmap,
            wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
            delay*1000,
            None,
            -1,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.BORDER_SIMPLE | wx.STAY_ON_TOP)
        self.Yield()
        return splash

    # -----------------------------------------------------------------------

    def background_initialization(self):
        """Initialize the application.

        Load the settings... and various other stuff to do.

        """
        self.settings = WxAppSettings()
        # here, we could be doing something... in future versions.

    # -----------------------------------------------------------------------

    def run(self):
        """Run the application and starts the main loop.

        A splash screen is displayed while a background initialization is
        doing things, then the main frame is created.

        :returns: (int) Exit status

        """
        try:

            splash = None
            if adv_import:
                splash = self.show_splash_screen()
            self.background_initialization()

            # here we could fix things like:
            #  - is first launch? No? so create config! and/or display a welcome msg!
            #  - check for update,
            #  - etc

            # Create the main frame of the application and show it.
            window = sppasMainWindow()
            self.SetTopWindow(window)
            if splash:
                splash.Close()
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
            logging.warning('The application has pending events.')

        # Save settings and configuration
        self.settings.save()
        cfg.save()

        # then it will exit. Nothing special to do. Return the exit status.
        return 0
