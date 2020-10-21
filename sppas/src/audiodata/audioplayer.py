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

    A simple audio player based on simpleaudio library.
    https://simpleaudio.readthedocs.io/en/latest/index.html

"""

import logging
import simpleaudio as sa
import datetime

from sppas.src.config import MediaState
from sppas.src.utils import b

import sppas.src.audiodata.aio
from .audio import sppasAudioPCM


# ---------------------------------------------------------------------------


class sppasSimpleAudioPlayer(object):
    """An audio player based on simpleaudio library.

    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        super(sppasSimpleAudioPlayer, self).__init__()

        self._ms = MediaState().unknown
        self._filename = None   # duration of the media in milliseconds
        self._audio = None
        self._frames = b("")
        self._sa_play = None    # simpleaudio library PlayObject()

        # a period to play the audio. Default: whole.
        self._period = None
        self._time_value = None

    # -----------------------------------------------------------------------

    def __del__(self):
        self._audio.close()

    # -----------------------------------------------------------------------

    def duration(self):
        """Return the duration of the loaded audio."""
        if self._filename is None:
            return 0.
        return self._audio.get_duration()

    # -----------------------------------------------------------------------

    def reset(self):
        self._ms = MediaState().unknown
        self._filename = None    # duration of the media in milliseconds
        self._audio = None
        self._frames = b("")
        self._sa_play = None
        self._period = None
        self._time_value = None

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Load the file that filename refers to.

        :param filename: (str)
        :return: (bool) Always returns False

        """
        self.reset()
        try:
            self._filename = filename
            self._audio = sppas.src.audiodata.aio.open(filename)
            self._frames = self._audio.read_frames(self._audio.get_nframes())
            self._audio.rewind()
            print("{:s}: {:d} loaded frames".format(filename, len(self._frames)))
            self._ms = MediaState().stopped
            return True

        except Exception as e:
            logging.error("View of the audio file {:s} is un-available: "
                          "{:s}".format(filename, str(e)))
            self._audio = sppasAudioPCM()
            self._ms = MediaState().unknown
            return False

    # -----------------------------------------------------------------------

    def is_playing(self):
        """Return True if the audio is playing."""
        if self._filename is None:
            return False

        return self._ms == MediaState().playing

    # -----------------------------------------------------------------------

    def is_paused(self):
        """Return True if the audio is paused."""
        if self._filename is None:
            return False

        return self._ms == MediaState().paused

    # -----------------------------------------------------------------------

    def is_stopped(self):
        """Return True if the audio is stopped."""
        if self._filename is None:
            return False

        return self._ms == MediaState().stopped

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the audio stream from the current position.

        :return: (bool) True if the action of playing was performed

        """
        if self._filename is None:
            logging.error("No media file to play.")
            return False

        with MediaState() as ms:
            if self._ms == ms.unknown:
                logging.error("The media file {:s} can't be played for an unknown reason.".format(self._filename))
                played = False

            elif self._ms == ms.loading:
                logging.error("The media file {:s} can't be played: still loading".format(self._filename))
                played = False

            elif self._ms == ms.playing:
                logging.warning("Media file {:s} is already playing.".format(self._filename))
                played = True

            else:  # stopped or paused
                try:
                    self._sa_play = sa.play_buffer(
                        self.__extract_frames(),
                        self._audio.get_nchannels(),
                        self._audio.get_sampwidth(),
                        self._audio.get_framerate())
                    played = self._sa_play.is_playing()
                except Exception as e:
                    played = False
                    logging.error(str(e))

                if played is True:
                    self._ms = MediaState().playing
                    self._time_value = datetime.datetime.now()
                else:
                    # An error occurred while we attempted to play
                    self._ms = MediaState().unknown

        return played

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the audio.

        :return: (bool) True if the action of stopping was performed

        """
        if self._sa_play is not None:
            self._sa_play.stop()
            self._ms = MediaState().stopped
            self._audio.rewind()
            return True
        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) True if the action of pausing was performed

        """
        if self._sa_play is not None:
            if self._sa_play.is_playing():
                # simpleaudio library does not implement the 'pause'
                # so we stop playing
                self._sa_play.stop()
                # seek at the exact moment we stopped to play
                self._reposition()
                # manage our state
                self._ms = MediaState().paused
                return True

        return False

    # -----------------------------------------------------------------------

    def seek(self, time_pos=0):
        """Seek the audio stream at the given position in time.

        :param time_pos: (float) Time in seconds

        """
        # how many frames this time position is representing since the beginning
        time_pos = float(time_pos)
        position = time_pos * self._audio.get_framerate()

        was_playing = self.is_playing()
        if was_playing is True:
            self.pause()

        # seek at the expected position
        try:
            self._audio.seek(int(position))
        except:
            # It can happen if we attempted to seek after the audio length
            self.stop()
            return False

        else:
            # continue playing if the seek was requested when playing
            if was_playing is True:
                self.play()

        return True

    # -----------------------------------------------------------------------

    def _reposition(self):
        """Private method to seek at the current position in the stream."""
        # update the current time value
        cur_time_value = datetime.datetime.now()
        time_delta = cur_time_value - self._time_value
        self._time_value = cur_time_value

        # eval the exact delay since the previous estimation
        timer_delay = time_delta.total_seconds()

        # how many frames this delay is representing
        n_frames = timer_delay * self._audio.get_framerate()

        # seek at the new position in the audio
        position = self._audio.tell() + int(n_frames)
        self._audio.seek(position)

    # -----------------------------------------------------------------------

    def __extract_frames(self):
        """Private method to return the frames to play."""
        cur_pos = self._audio.tell() * self._audio.get_sampwidth()
        return self._frames[cur_pos:]
