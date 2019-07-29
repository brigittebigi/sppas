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

    ui.logs.py
    ~~~~~~~~~~

"""

import os
import platform
import logging
from datetime import date

try:
    import wx
    IMPORT_WX = True
except:
    IMPORT_WX = False

from sppas.src.utils.datatype import sppasTime
from sppas.src.config import paths
from sppas.src.config import sg

# ---------------------------------------------------------------------------


class sppasLogFile(object):
    """Utility file name manager for logs.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self):
        """Create a sppasLogFile instance.

        Create the log directory if not already existing then fix the
        log filename with increment=0.

        """
        log_dir = paths.logs
        if os.path.exists(log_dir) is False:
            os.mkdir(log_dir)

        self.__filename = "{:s}_log_".format(sg.__name__)
        self.__filename += str(date.today()) + "_"
        self.__filename += str(os.getpid()) + "_"

        self.__current = 1
        while os.path.exists(self.get_filename()) is True:
            self.__current += 1

    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the current log filename."""
        fn = os.path.join(paths.logs, self.__filename)
        fn += "{0:04d}".format(self.__current)
        return fn + ".txt"

    # -----------------------------------------------------------------------

    def increment(self):
        """Increment the current log filename."""
        self.__current += 1

    # -----------------------------------------------------------------------

    @staticmethod
    def get_header():
        """Return a string with an header for logs."""
        header = "-"*78
        header += "\n\n"
        header += " {:s} {:s}".format(sg.__name__, sg.__version__)
        header += "\n"
        header += " {:s}".format(sppasTime().now)
        header += "\n"
        header += " {:s}".format(platform.platform())
        header += "\n"
        header += " python {:s}".format(platform.python_version())
        if IMPORT_WX:
            header += "\n"
            header += " wxpython {:s}".format(wx.version())
        header += "\n\n"
        header += "-"*78
        header += "\n\n"
        return header

# ---------------------------------------------------------------------------


class sppasLogSetup(object):
    """Utility class to initialize the python logging system.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, log_level=0):
        """Create a sppasLogSetup instance.

        By default, the NullHandler is assigned.

        The numeric values of logging levels are given in the following:

            - CRITICAL 	50
            - ERROR 	40
            - WARNING 	30
            - INFO 	    20
            - DEBUG 	10
            - NOTSET 	 0

        :param log_level: Sets the threshold for this logger. Logging messages
        which are less severe than this value will be ignored. When NOTSET is
        assigned, all messages are printed.

        """
        # Fix the format of the messages
        format_msg = "%(asctime)s [%(levelname)s] %(message)s"

        self._log_level = int(log_level)
        self._formatter = logging.Formatter(format_msg)

        # Remove all existing handlers in the logging
        for h in reversed(list(logging.getLogger().handlers)):
            logging.getLogger().removeHandler(h)

        # Add our own handler in the logging
        self._handler = logging.NullHandler()
        logging.getLogger().addHandler(self._handler)
        logging.getLogger().setLevel(self._log_level)

    # -----------------------------------------------------------------------

    def set_log_level(self, log_level):
        """Fix the log level.

        :param log_level: Sets the threshold for this logger. Logging messages
        which are less severe than this value will be ignored. When NOTSET is
        assigned, all messages are printed.

        """
        if log_level == self._log_level:
            return

        self._log_level = int(log_level)
        if self._handler is not None:
            self._handler.setLevel(self._log_level)
        logging.getLogger().setLevel(self._log_level)

        logging.info("Logging set up level={:d}"
                     "".format(self._log_level))

    # -----------------------------------------------------------------------

    def stream_handler(self):
        """Starts to redirect to logging StreamHandler."""
        self.__stop_handler()
        self._handler = logging.StreamHandler()  # sys.stderr
        self._handler.setFormatter(self._formatter)
        self._handler.setLevel(self._log_level)
        logging.getLogger().addHandler(self._handler)

        logging.info("Logging redirected to StreamHandler (level={:d})."
                     "".format(self._log_level))

    # -----------------------------------------------------------------------

    def null_handler(self):
        """Starts to redirect to logging NullHandler."""
        self.__stop_handler()
        self._handler = logging.NullHandler()
        logging.getLogger().addHandler(self._handler)

    # -----------------------------------------------------------------------

    def file_handler(self, filename):
        """Starts to redirect to logging FileHandler.

        :param filename: Specifies that a FileHandler be created, using the
        specified filename.

        """
        self.__stop_handler()
        self._handler = logging.FileHandler(filename, "a+")
        self._handler.setFormatter(self._formatter)
        self._handler.setLevel(self._log_level)
        logging.getLogger().addHandler(self._handler)

        logging.info("Logging redirected to FileHandler (level={:d})."
                     "".format(self._log_level))

    # -----------------------------------------------------------------------

    def __stop_handler(self):
        """Stops the current handler."""
        if self._handler is not None:
            # Show a bye message on the console!
            logging.info("Stops current logging handler.")
            # Remove the current handler
            logging.getLogger().removeHandler(self._handler)

        self._handler = None
