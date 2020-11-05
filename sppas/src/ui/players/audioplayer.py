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

    src.audiodata.audioplayer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description:
    ============

    A simple audio player based on simpleaudio library.
    https://simpleaudio.readthedocs.io/en/latest/index.html

    Notice that the simpleplayer library only allows to play/stop.
    Seek, tell or pause are not supported.

    Example:
    ========

        >>> p = sppasSimpleAudioPlayer()
        >>> p.load("an audio filename")
        >>> if p.prepare_play(0., p.get_duration()) is True:
        >>>     p.play()

"""

import logging
import simpleaudio as sa
import datetime

from sppas.src.utils import b
import sppas.src.audiodata.aio
from src.audiodata.audio import sppasAudioPCM

from .baseplayer import sppasBasePlayer
from .pstate import PlayerState

# ---------------------------------------------------------------------------


class sppasSimpleAudioPlayer(sppasBasePlayer):
    """An audio player based on simpleaudio library.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can load, play and browse throw the audio stream of a given file.

    """

    def __init__(self):
        super(sppasSimpleAudioPlayer, self).__init__()

        self._frames = b("")     # loaded frames of the audio stream
        self.__time_value = None  # datetime of start playing

    # -----------------------------------------------------------------------

    def __del__(self):
        try:
            self._media.close()
        except:
            pass

    # -----------------------------------------------------------------------

    def reset(self):
        """Re-initialize all known data."""
        if self._media is not None:
            self._media.close()
        self._frames = b("")
        self.__time_value = None
        self._from_time = 0.
        self._to_time = 0.
        sppasBasePlayer.reset(self)

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Load all the frames of the file that filename refers to.

        :param filename: (str) Name of an audio file
        :return: (bool) True if both successfully opened and loaded.

        """
        self.reset()
        self._ms = PlayerState().loading
        try:
            self._filename = filename
            self._media = sppas.src.audiodata.aio.open(filename)
            self._frames = self._media.read_frames(self._media.get_nframes())
            self._media.rewind()
            self._ms = PlayerState().stopped
            self._to_time = self.get_duration()
            return True

        except Exception as e:
            logging.error("Error when opening or loading file {:s}: "
                          "{:s}".format(filename, str(e)))
            self._media = sppasAudioPCM()
            self._ms = PlayerState().unknown
            return False

    # -----------------------------------------------------------------------

    def play(self):
        """Play the media into the currently defined range of time.

        The method prepare_play() should be invoked first.

        :return: (bool) True if the action of playing was performed

        """
        played = False
        if self._ms in (PlayerState().paused, PlayerState().stopped):

            try:
                # Ask simpleaudio library to play a buffer of frames
                frames = self._extract_frames()
                if len(frames) > 0:
                    self._player = sa.play_buffer(
                        frames,
                        self._media.get_nchannels(),
                        self._media.get_sampwidth(),
                        self._media.get_framerate())
                    # Check if the audio is really playing
                    played = self._player.is_playing()
                else:
                    logging.warning("No frames to play in the given period "
                                    "for audio {:s}.".format(self._filename))

            except Exception as e:
                logging.error("An error occurred when attempted to play "
                              "the audio stream of {:s} with the "
                              "simpleaudio library: {:s}".format(self._filename, str(e)))

            if played is True:
                self._ms = PlayerState().playing
                self.__time_value = datetime.datetime.now()
            else:
                # An error occurred while we attempted to play
                self._ms = PlayerState().unknown

        return played

    # -----------------------------------------------------------------------

    def get_time_value(self):
        """Return the exact time the audio started to play."""
        return self.__time_value

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the audio and invalidate the time range.

        :return: (bool) True if the action of stopping was performed

        """
        if self._player is not None:
            self._player.stop()

        if self._ms not in (PlayerState().unknown, PlayerState().loading):
            self._ms = PlayerState().stopped
            self._media.rewind()
            self._from_time = 0.
            self._to_time = self.get_duration()
            return True

        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) True if the action of pausing was performed

        """
        if self._player is not None:
            if self._player.is_playing():
                # The simpleaudio library does not implement the 'pause'
                # so we stop playing the PlayObject().
                self._player.stop()
                # seek at the exact moment we stopped to play
                self._reposition()
                # manage our state
                self._ms = PlayerState().paused
                return True

        return False

    # -----------------------------------------------------------------------

    def seek(self, time_pos=0):
        """Seek the audio stream at the given position in time.

        :param time_pos: (float) Time in seconds

        """
        if self._ms in (PlayerState().unknown, PlayerState().loading):
            return False

        time_pos = float(time_pos)
        if time_pos < 0.:
            time_pos = 0.
        if time_pos > self.get_duration():
            time_pos = self.get_duration()

        # how many frames this time position is representing since the beginning
        self._from_time = float(time_pos)
        position = self._from_time * self._media.get_framerate()
        if self._from_time >= self._to_time:
            self.stop()

        was_playing = self.is_playing()
        if was_playing is True:
            self.pause()

        # seek at the expected position
        try:
            self._media.seek(int(position))
            # continue playing if the seek was requested when playing
            if was_playing is True:
                self.play()
        except:
            # It can happen if we attempted to seek after the audio length
            self.stop()
            return False

        return True

    # -----------------------------------------------------------------------

    def audio_tell(self):
        if self._ms not in (PlayerState().unknown, PlayerState().loading):
            return self._media.tell()
        return 0

    # -----------------------------------------------------------------------
    # About the audio
    # -----------------------------------------------------------------------

    def get_nchannels(self):
        """Return the number of channels."""
        if self._media is not None:
            return self._media.get_nchannels()
        return 0

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        if self._media is not None:
            return self._media.get_sampwidth()
        return 0

    # -----------------------------------------------------------------------

    def get_framerate(self):
        if self._media is not None:
            return self._media.get_framerate()
        return 0

    # -----------------------------------------------------------------------

    def get_duration(self):
        if self._media is not None:
            return self._media.get_duration()
        return 0.

    # -----------------------------------------------------------------------

    def update_playing(self):
        if self._ms == PlayerState().playing and self._player.is_playing() is False:
            self.stop()

    # -----------------------------------------------------------------------
    # Protected methods
    # -----------------------------------------------------------------------

    def _reposition(self):
        """Seek the audio at the current position in the played stream.

        The current position in the played stream is estimated using the
        delay between the stored time value and now().

        :return: (datetime) New time value

        """
        # update the current time value
        cur_time_value = datetime.datetime.now()
        time_delta = cur_time_value - self.__time_value
        self.__time_value = cur_time_value

        # eval the exact delay since the previous estimation
        self._from_time = time_delta.total_seconds()

        # how many frames this delay is representing
        n_frames = self._from_time * self._media.get_framerate()

        # seek at the new position in the audio
        position = self._media.tell() + int(n_frames)
        if position < self._media.get_nframes():
            self._media.seek(position)

        return self.__time_value

    # -----------------------------------------------------------------------

    def _extract_frames(self):
        """Return the frames to play in the currently stored time values.

        """
        logging.debug(" ... {} extract frame for the period: {} {}"
                      "".format(self._filename, self._from_time, self._to_time))
        # Check if the current period is inside or overlapping this audio
        end_time = min(self._to_time, self.get_duration())
        if self._from_time < end_time:
            # Convert the time (in seconds) into a position in the frames
            start_pos = self._time_to_frames(self._from_time)
            end_pos = self._time_to_frames(end_time)
            return self._frames[start_pos:end_pos]

        return b("")

    # -----------------------------------------------------------------------

    def _time_to_frames(self, time_value):
        return int(time_value * float(self._media.get_framerate())) * \
               self._media.get_sampwidth() * \
               self._media.get_nchannels()
