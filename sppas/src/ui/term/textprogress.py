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

    src.term.textprogress.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""
import sys

from sppas.src.utils.makeunicode import u, b

from ..progress import sppasBaseProgress
from .terminalcontroller import TerminalController

# ----------------------------------------------------------------------------

WIDTH = 74
BAR = '%3d%% ${GREEN}[${BOLD}%s%s${NORMAL}${GREEN}]${NORMAL}\n'
HEADER = '${BOLD}${CYAN}%s${NORMAL}\n\n'

# ----------------------------------------------------------------------------


class ProcessProgressTerminal(sppasBaseProgress):
    """A 3-lines progress bar to be used while processing from a terminal.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    It looks like:

                            header
    20% [===========----------------------------------]
                        message text

    The progress self._bar is colored, if the terminal supports color
    output; and adjusts to the width of the terminal.

    """

    def __init__(self):
        """Create a ProcessProgressTerminal instance."""
        super(ProcessProgressTerminal, self).__init__()
        try:
            self._term = TerminalController()
            if not (self._term.CLEAR_EOL and self._term.UP and self._term.BOL):
                self._term = None
            self._bar = self._term.render(BAR)
        except Exception as e:
            import traceback
            print('[WARNING] The progress bar is disabled because this terminal'
                  ' does not support colors, EOL, UP, etc. Returned error: {}'
                  ''.format(traceback.format_exc()))
            self._term = None
            self._bar = ""

        self._cleared = True  # We haven't drawn the self._bar yet.

    # ------------------------------------------------------------------

    def update(self, percent=None, message=None):
        """Update the progress.

        :param message: (str) progress bar value (default: 0)
        :param percent: (float) progress bar text (default: None)

        """
        if percent is None:
            percent = self._percent
        if message is None:
            message = self._text
        else:
            message = u(message)

        if self._term:
            n = int((WIDTH - 10) * percent)
            if self._cleared is True:
                self._cleared = False

                sys.stdout.write(u(self._term.BOL + self._term.CLEAR_EOL +
                                   self._term.UP + self._term.CLEAR_EOL +
                                   self._term.UP + self._term.CLEAR_EOL))

            val = self._bar % (100*percent, b('=')*n, b('-')*(WIDTH-10-n))
            sys.stdout.write(
                str(self._term.BOL + self._term.UP + self._term.CLEAR_EOL) +
                str(val) +
                str(self._term.CLEAR_EOL) +
                str(message.center(WIDTH)))
        else:
            print('  => ' + message)

        self._percent = percent
        self._text = message

    # ------------------------------------------------------------------

    def clear(self):
        """Clear."""
        if self._cleared is False:
            sys.stdout.write("\n\n")
            self._cleared = True

    # ------------------------------------------------------------------

    def set_header(self, header):
        """Set a new progress header text.

        :param header: (str) new progress header text.

        """
        if header is None:
            header = ""
        if self._term:
            self._header = self._term.render(HEADER % header.center(WIDTH))
            self._header = u(self._header)
            sys.stdout.write("\n" + self._header + "\n")
            sys.stdout.write("\n")

        else:
            self._header = u("\n         * * *  " + header + "  * * *  ")
            print(self._header)

    # ------------------------------------------------------------------

    def set_new(self):
        """Initialize a new progress line."""
        self.clear()
        self._text = ""
        self._percent = 0
        self._header = ""
