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

    src.ui.baseplayer.py
    ~~~~~~~~~~~~~~~~~~~~

    Base class to implement inherited audio/video players.

"""

import logging
import datetime

from .pstate import PlayerState
from .pstate import PlayerType

# ---------------------------------------------------------------------------


class sppasBasePlayer(object):
    """A base class for any stream player.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can load, play and stop the data stream of a given file.

    """

    def __init__(self):
        """A base class for any player."""
        # The state of the player: unknown, loading, playing, paused or stopped
        self._ms = PlayerState().unknown
        # The type of the player: unknown, unsupported, audio, video...
        self._mt = PlayerType().unknown

        # The name of the media file
        self._filename = None

        # The instance of the media - i.e. its content, when loading is finished
        self._media = None

        # The instance of the media player - when playing, and the boundaries
        self._player = None
        self._start_datenow = None  # datetime.now() of the last start playing
        self._from_time = 0.        # position (in seconds) of start playing
        self._to_time = 0.          # position (in seconds) to stop playing

    # -----------------------------------------------------------------------
    # State of this player
    # -----------------------------------------------------------------------

    def is_loading(self):
        """Return True if the media state is loading."""
        if self._filename is None:
            return False

        return self._ms == PlayerState().loading

    # -----------------------------------------------------------------------

    def is_playing(self):
        """Return True if the media state is playing."""
        if self._filename is None:
            return False

        return self._ms == PlayerState().playing

    # -----------------------------------------------------------------------

    def is_paused(self):
        """Return True if the media state is paused."""
        if self._filename is None:
            return False

        return self._ms == PlayerState().paused

    # -----------------------------------------------------------------------

    def is_stopped(self):
        """Return True if the media state is stopped."""
        if self._filename is None:
            return False

        return self._ms == PlayerState().stopped

    # -----------------------------------------------------------------------
    # Type of this player
    # -----------------------------------------------------------------------

    def is_unknown(self):
        """Return True if the media type is unknown."""
        if self._filename is None:
            return False

        return self._mt == PlayerType().unknown

    # -----------------------------------------------------------------------

    def is_unsupported(self):
        """Return True if the media type is known but unsupported."""
        if self._filename is None:
            return False

        return self._mt == PlayerType().unsupported

    # -----------------------------------------------------------------------

    def is_audio(self):
        """Return True if the media type is a valid audio."""
        if self._filename is None:
            return False

        return self._mt == PlayerType().audio

    # -----------------------------------------------------------------------

    def is_video(self):
        """Return True if the media type is a valid video."""
        if self._filename is None:
            return False

        return self._mt == PlayerType().video

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the name of the file this media refers to or None."""
        return self._filename

    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the media or 0."""
        return 0.

    # -----------------------------------------------------------------------

    def get_time_value(self):
        """Return the exact time the audio started to play or None."""
        return self._start_datenow

    # -----------------------------------------------------------------------
    # The methods to be overriden.
    # -----------------------------------------------------------------------

    def reset(self):
        """Re-initialize all known data."""
        self._ms = PlayerState().unknown
        self._mt = PlayerType().unknown
        self._filename = None
        self._media = None
        self._start_datenow = None
        self._from_time = 0.    # position (in seconds) to start playing
        self._to_time = 0.      # position (in seconds) to stop playing

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Load all the frames of the file that filename refers to.

        :param filename: (str) Name of an audio file
        :return: (bool) True if both successfully opened and loaded.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate the current range of time."""
        self._from_time = 0.
        self._to_time = self.get_duration()

    # -----------------------------------------------------------------------

    def prepare_play(self, from_time=None, to_time=None):
        """Prepare to play the media stream: fix the period to play.

        :param from_time: (float) Start to play at this given time or at the current from time if None
        :param to_time: (float) Stop to play at this given time or at the current end time if None
        :return: (bool) True if the action of playing can be performed

        """
        can_play = False

        if self._media is not None:

            if from_time is not None:
                self._from_time = from_time
            if to_time is not None:
                self._to_time = to_time

            with PlayerState() as ms:
                if self._ms == ms.unknown:
                    if self._mt not in (PlayerType().unknown, PlayerType().unsupported):
                        logging.error("The media stream of {:s} can't be played for "
                                      "an unknown reason.".format(self._filename))

                elif self._ms == ms.loading:
                    logging.error("The media stream of {:s} can't be played; "
                                  "it is still loading".format(self._filename))

                elif self._ms == ms.playing:
                    logging.warning("The media stream of {:s} is already "
                                    "playing.".format(self._filename))

                else:  # stopped or paused
                    can_play = True
        else:
            logging.error("No media file to play.")

        return can_play

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the audio stream.

        Start playing only if the media stream is currently stopped or
        paused.

        :return: (bool) True if the action of playing was performed

        """
        played = False
        if self._ms in (PlayerState().paused, PlayerState().stopped):
            played = self._play_process()
            if played is True:
                self._ms = PlayerState().playing
            else:
                # An error occurred while we attempted to play
                self._ms = PlayerState().unknown

        return played

    # -----------------------------------------------------------------------

    def _play_process(self):
        """Launch the player and fix the start time of playing. """
        self._start_datenow = datetime.datetime.now()
        return False

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the audio and invalidate the time range.

        :return: (bool) True if the action of stopping was performed

        """
        self._ms = PlayerState().stopped
        self._start_datenow = None
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) True if the action of pausing was performed

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def media_tell(self):
        raise NotImplementedError
