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

    src.ui.phoenix.players.undplayer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A player that doesn't play anything.

"""

from sppas.src.ui.players import sppasBasePlayer
from sppas.src.ui.players import PlayerType

# ---------------------------------------------------------------------------


class sppasUndPlayer(sppasBasePlayer):
    """A media player that simply store a filename and its duration.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        super(sppasUndPlayer, self).__init__()
        self._duration = 0.

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Store the filename.

        :param filename: (str) Name of a file
        :return: (bool) True

        """
        self._filename = filename
        self._mt = PlayerType().unsupported
        return True

    # -----------------------------------------------------------------------

    def get_duration(self):
        return self._duration

    # -----------------------------------------------------------------------

    def set_duration(self, value):
        """Set the duration of the file."""
        self._duration = value

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play.

        :return: (bool) False

        """
        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) False

        """
        return False

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the audio stream.

        :return: (bool) False

        """
        return False
