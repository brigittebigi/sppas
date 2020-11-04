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

    Notice that the simpleplayer library only allows to play/stop.
    Seek, tell or pause are not supported.

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

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can load, play and browse throw the audio stream of a given file.

    """

    def __init__(self):
        super(sppasSimpleAudioPlayer, self).__init__()

        self._ms = MediaState().unknown
        self._filename = None    # name of the audio file
        self._audio = None       # sppasAudioPCM() instance
        self._frames = b("")     # loaded frames of the audio stream
        self._sa_play = None     # simpleaudio library PlayObject()

        self._time_value = None  # date of start playing

    # -----------------------------------------------------------------------

    def __del__(self):
        try:
            self._audio.close()
        except:
            pass

    # -----------------------------------------------------------------------

    def get_filename(self):
        return self._filename

    # -----------------------------------------------------------------------

    def reset(self):
        """Re-initialize all known data."""
        self._ms = MediaState().unknown
        self._filename = None
        if self._audio is not None:
            self._audio.close()
            self._audio = None
        self._frames = b("")
        self._sa_play = None
        self._time_value = None

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Load the file that filename refers to.

        :param filename: (str) Name of an audio file
        :return: (bool) True if both successfully opened and loaded.

        """
        self.reset()
        self._ms = MediaState().loading
        try:
            self._filename = filename
            self._audio = sppas.src.audiodata.aio.open(filename)
            self._frames = self._audio.read_frames(self._audio.get_nframes())
            self._audio.rewind()
            self._ms = MediaState().stopped
            return True

        except Exception as e:
            logging.error("Error when opening or loading file {:s}: "
                          "{:s}".format(filename, str(e)))
            self._audio = sppasAudioPCM()
            self._ms = MediaState().unknown
            return False

    # -----------------------------------------------------------------------

    def is_unknown(self):
        """Return True if the media is unknown."""
        if self._filename is None:
            return False

        return self._ms == MediaState().unknown

    # -----------------------------------------------------------------------

    def is_loading(self):
        """Return True if the audio is still loading."""
        if self._filename is None:
            return False

        return self._ms == MediaState().loading

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

    def play(self, start_time=None, to_time=None):
        """Start to play the audio stream from the current position.

        Start playing only is the audio stream is currently stopped or
        paused.

        :return: (bool) True if the action of playing was performed

        """
        if self._filename is None:
            logging.error("No media file to play.")
            return False
        if start_time is None:
            start_time = 0.
        if to_time is None:
            to_time = self.get_duration()

        played = False
        with MediaState() as ms:
            if self._ms == ms.unknown:
                logging.error("The audio stream of {:s} can't be played for "
                              "an unknown reason.".format(self._filename))

            elif self._ms == ms.loading:
                logging.error("The audio stream of {:s} can't be played: "
                              "still loading".format(self._filename))

            elif self._ms == ms.playing:
                logging.warning("The audio stream of {:s} is already "
                                "playing.".format(self._filename))

            else:  # stopped or paused
                try:
                    # Ask simpleaudio library to play a buffer of frames
                    frames = self._extract_frames(start_time, to_time)
                    if len(frames) > 0:
                        self._sa_play = sa.play_buffer(
                            frames,
                            self._audio.get_nchannels(),
                            self._audio.get_sampwidth(),
                            self._audio.get_framerate())
                        # Check if the audio is really playing
                        played = self._sa_play.is_playing()
                    else:
                        logging.warning("No frames to play in the given period "
                                        "for audio {:s}.".format(self._filename))

                except Exception as e:
                    logging.error("An error occurred when attempted to play "
                                  "the audio stream of {:s} with the "
                                  "simpleaudio library: {:s}".format(self._filename, str(e)))

                if played is True:
                    self._ms = MediaState().playing
                    self._time_value = datetime.datetime.now()
                else:
                    # An error occurred while we attempted to play
                    self._ms = MediaState().unknown

        return played

    # -----------------------------------------------------------------------

    def get_time_value(self):
        """Return the exact time the audio started to play."""
        return self._time_value

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the audio.

        :return: (bool) True if the action of stopping was performed

        """
        if self._sa_play is not None:
            self._sa_play.stop()

        if self._ms not in (MediaState().unknown, MediaState().loading):
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
                # The simpleaudio library does not implement the 'pause'
                # so we stop playing the PlayObject().
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
        if self._ms in (MediaState().unknown, MediaState().loading):
            return False

        time_pos = float(time_pos)
        if time_pos < 0.:
            time_pos = 0.
        if time_pos > self.get_duration():
            time_pos = self.get_duration()

        # how many frames this time position is representing since the beginning
        time_pos = float(time_pos)
        position = time_pos * self._audio.get_framerate()

        was_playing = self.is_playing()
        if was_playing is True:
            self.pause()

        # seek at the expected position
        try:
            self._audio.seek(int(position))
            # continue playing if the seek was requested when playing
            if was_playing is True:
                self.play()
        except:
            # It can happen if we attempted to seek after the audio length
            self.stop()
            return False

        return True

    # -----------------------------------------------------------------------
    # About the audio
    # -----------------------------------------------------------------------

    def get_nchannels(self):
        """Return the number of channels."""
        if self._audio is not None:
            return self._audio.get_nchannels()
        return 0

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        if self._audio is not None:
            return self._audio.get_sampwidth()
        return 0

    # -----------------------------------------------------------------------

    def get_framerate(self):
        if self._audio is not None:
            return self._audio.get_framerate()
        return 0

    # -----------------------------------------------------------------------

    def get_duration(self):
        if self._audio is not None:
            return self._audio.get_duration()
        return 0.

    # -----------------------------------------------------------------------

    def update_playing(self):
        if self._ms == MediaState().playing and self._sa_play.is_playing() is False:
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
        time_delta = cur_time_value - self._time_value
        self._time_value = cur_time_value

        # eval the exact delay since the previous estimation
        timer_delay = time_delta.total_seconds()

        # how many frames this delay is representing
        n_frames = timer_delay * self._audio.get_framerate()

        # seek at the new position in the audio
        position = self._audio.tell() + int(n_frames)
        if position < self._audio.get_nframes():
            self._audio.seek(position)

        return self._time_value

    # -----------------------------------------------------------------------

    def _extract_frames(self, from_time, to_time):
        """Return the frames to play in the given period.

        """
        logging.debug(" ... {} extract frame for the period: {} {}".format(self._filename, from_time, to_time))
        # Check if the current period is inside or overlapping this audio
        end_time = min(to_time, self.get_duration())
        if from_time < end_time:
            # Convert the time (in seconds) into a position in the frames
            start_pos = self._time_to_frames(from_time)
            end_pos = self._time_to_frames(end_time)
            return self._frames[start_pos:end_pos]
        else:
            logging.debug("Period out of range {} > duration: {}".format(to_time, self.get_duration()))

        return b("")

    # -----------------------------------------------------------------------

    def _time_to_frames(self, time_value):
        return int(time_value * float(self._audio.get_framerate())) * \
               self._audio.get_sampwidth() * \
               self._audio.get_nchannels()
