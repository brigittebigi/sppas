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
import threading
import multiprocessing

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

    def play(self):
        """Start to play the audio stream from the current position.

        Start playing only is the audio stream is currently stopped or
        paused.

        :return: (bool) True if the action of playing was performed

        """
        if self._filename is None:
            logging.error("No media file to play.")
            return False

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
                    frames = self._extract_frames()
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
                    print("Start playing {} at: {}".format(self._filename, self._time_value))
                else:
                    # An error occurred while we attempted to play
                    self._ms = MediaState().unknown

        return played

    # -----------------------------------------------------------------------

    def prepare_to_play(self):
        """return the frames to play."""
        if self._filename is None:
            logging.error("No media file to play.")
            return False

        frames = b('')
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
                    # Ask simpleaudio library to play a buffer of frames
                    frames = self._extract_frames()
                    print(len(frames))
                    if len(frames) > 0:
                        return frames
                    else:
                        logging.warning("No frames to play in the given period "
                                        "for audio {:s}.".format(self._filename))

        return frames

    # -----------------------------------------------------------------------

    def play_frames(self, frames):
        try:
            self._sa_play = sa.play_buffer(
                frames,
                self._audio.get_nchannels(),
                self._audio.get_sampwidth(),
                self._audio.get_framerate())
            # Check if the audio is really playing
            played = self._sa_play.is_playing()

            if played is True:
                self._ms = MediaState().playing
                self._time_value = datetime.datetime.now()
                print("Start playing {} at: {}".format(self._filename, self._time_value))
            else:
                # An error occurred while we attempted to play
                self._ms = MediaState().unknown

        except Exception as e:
            logging.error("An error occurred when attempted to play "
                          "the audio stream of {:s} with the "
                          "simpleaudio library: {:s}".format(self._filename, str(e)))

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
                # The simpleaudio library does not implement the 'pause'
                # so we stop playing with the PlayObject().
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
    # Protected methods
    # -----------------------------------------------------------------------

    def _reposition(self):
        """Seek at the current position in the stream using time_value.

        :return: (float) Time position in the stream (seconds)

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
        self._audio.seek(position)

        return self._time_value

    # -----------------------------------------------------------------------

    def _extract_frames(self):
        """Return the frames to play."""
        cur_pos = self._audio.tell() * self._audio.get_sampwidth() * self._audio.get_nchannels()
        return self._frames[cur_pos:]

    # -----------------------------------------------------------------------

    def _time_to_frames(self, time_value):
        return int(time_value * float(self._audio.get_framerate())) * \
               self._audio.get_sampwidth() * \
               self._audio.get_nchannels()


# ---------------------------------------------------------------------------


class sppasMultiAudioPlayer(object):
    """An audio player based on simpleaudio library.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can load, play and browse throw several audio streams of given files.

    """

    def __init__(self):
        """Instantiate the multi audio player."""
        # Key = sppasSimpleAudioPlayer / value = bool:enabled
        self.__audios = dict()

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Add an audio into the list of audio managed by this control.

        The new media is not disabled.

        :param filename: (str)
        :return: (bool)

        """
        new_audio = sppasSimpleAudioPlayer()
        loaded = new_audio.load(filename)
        if loaded is True:
            self.__audios[new_audio] = False
        return loaded

    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration this player must consider (in seconds).

        This estimation does not take into account the fact that an audio is
        enabled or disabled. All audio are considered.

        :return: (float)

        """
        if len(self.__audios) > 0:
            return max(a.get_duration() for a in self.__audios)
        else:
            return 0.

    # -----------------------------------------------------------------------

    def exists(self, filename):
        """Return True if the filename is matching an existing audio."""
        for a in self.__audios:
            if a.get_filename() == filename:
                return True
        return False

    # -----------------------------------------------------------------------

    def is_enabled(self, filename=None):
        """Return True if any audio or the one of the given filename is enabled."""
        if filename is None:
            return any([self.__audios[audio] for audio in self.__audios])

        for audio in self.__audios:
            if self.__audios[audio] is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def enable(self, filename, value=True):
        """Enable or disable the given audio.

        When an audio is disabled, it can't be paused nor played. It can only
        stay in the stopped state.

        :param filename: (str)
        :param value: (bool)
        :return: (bool)

        """
        for a in self.__audios:
            if a.get_filename() == filename:
                self.__audios[a] = bool(value)
                if a.is_playing():
                    a.stop()

        return False

    # -----------------------------------------------------------------------

    def are_playing(self):
        """Return True if all enabled audio are playing.

        :return: (bool)

        """
        playing = [audio.is_playing() for audio in self.__audios if self.__audios[audio] is True]
        if len(playing) == 0:
            return False

        # all([]) is True
        return all(playing)

    # -----------------------------------------------------------------------

    def is_playing(self, filename=None):
        """Return True if any audio or if the given audio is playing.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([audio.is_playing() for audio in self.__audios])

        for audio in self.__audios:
            if audio.is_playing() is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def are_paused(self):
        """Return True if all enabled audio are paused.

        :return: (bool)

        """
        paused = [audio.is_paused() for audio in self.__audios if self.__audios[audio] is True]
        if len(paused) == 0:
            return False

        # all([]) is True
        return all(paused)

    # -----------------------------------------------------------------------

    def is_paused(self, filename=None):
        """Return True if any audio or if the given audio is paused.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([audio.is_paused() for audio in self.__audios])

        for audio in self.__audios:
            if audio.is_paused() is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def are_stopped(self):
        """Return True if all enabled audio are stopped.

        :return: (bool)

        """
        stopped = [audio.is_stopped() for audio in self.__audios if self.__audios[audio] is True]
        if len(stopped) == 0:
            return False

        # all([]) is True
        return all(stopped)

    # -----------------------------------------------------------------------

    def is_stopped(self, filename=None):
        """Return True if any audio or if the given audio is stopped.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([audio.is_stopped() for audio in self.__audios])

        for audio in self.__audios:
            if audio.is_stopped() is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_loading(self, filename=None):
        """Return True if any audio or if the given audio is loading.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([audio.is_loading() for audio in self.__audios])

        for audio in self.__audios:
            if audio.is_loading() is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def remove(self, filename):
        """Remove a media of the list of media managed by this control.

        :param filename: (str)
        :return: (bool)

        """
        audio = None
        for a in self.__audios:
            if a.get_filename() == filename:
                audio = a
                break

        if audio is not None:
            audio.stop()
            del self.__audios[audio]
            return True

        return False

    # -----------------------------------------------------------------------
    # Player
    # -----------------------------------------------------------------------

    def play(self):
        """Start to play all the enabled audio streams from the current position.

        Start playing only if the audio stream is currently stopped or
        paused and if enabled.

        :return: (bool) True if the action of playing was performed

        """
        for audio in self.__audios:
            if self.__audios[audio] is True:
                audio.play()

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause the media and notify parent."""
        for audio in self.__audios:
            if audio.is_playing():
                audio.pause()

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the audios."""
        for audio in self.__audios:
            if audio.is_playing():
                audio.stop()

    # -----------------------------------------------------------------------

    def seek(self, value):
        """Seek all audio to the given position in time.

        :param value: (float) Time value in seconds.

        """
        force_pause = False
        if self.is_playing() is not None:
            self.pause()
            force_pause = True

        # Debug("Media seek to position {}".format(offset))
        for audio in self.__audios:
            audio.seek(value)

        if force_pause is True:
            self.play()

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self.__audios)
