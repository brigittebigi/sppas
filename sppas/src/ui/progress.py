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

    src.ui.progress.py
    ~~~~~~~~~~~~~~~~~~

"""

import logging

# ----------------------------------------------------------------------------


class sppasBaseProgress(object):
    """Base class for a progress bar to be used while processing some task.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Print messages on the logging.

    """

    def __init__(self, *args, **kwargs):
        """Create a sppasBaseProgress instance."""
        self._percent = 0
        self._text = ""
        self._header = ""

    # ------------------------------------------------------------------

    def update(self, percent=None, message=None):
        """Update the progress.

        :param message: (str) progress bar value (default: 0)
        :param percent: (float) progress bar text  (default: None)

        """
        if percent is not None:
            self._percent = percent
        if message is not None:
            logging.info('  => ' + message)
            self._text = message

    # ------------------------------------------------------------------

    def clear(self):
        """Clear."""
        pass

    # ------------------------------------------------------------------

    def set_fraction(self, percent):
        """Set a new progress value.

        :param percent: (float) new progress value

        """
        self.update(percent=percent)

    # ------------------------------------------------------------------

    def set_text(self, text):
        """Set a new progress message text.

        :param text: (str) new progress text

        """
        self.update(message=text.strip())

    # ------------------------------------------------------------------

    def set_header(self, header):
        """Set a new progress header text.

        :param header: (str) new progress header text.

        """
        if len(header) > 0:
            self._header = "          * * *  " + header + "  * * *  "
        else:
            self._header = ""
        logging.info(self._header)

    # ------------------------------------------------------------------

    def set_new(self):
        """Initialize a new progress line."""
        self.set_header("")
        self.update(percent=0, message="")

    # ------------------------------------------------------------------

    def close(self):
        pass
