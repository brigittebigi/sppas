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

    src.audiodata.audiomplayer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A simple audio player based on simpleaudio library.
    https://simpleaudio.readthedocs.io/en/latest/index.html

"""

import logging
import datetime

from .audioplayer import sppasSimpleAudioPlayer

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
        self._audios = dict()
        # Observed delays between 2 consecutive "play".
        # Used to synchronize files.
        self._all_delays = [0.01]

    # -----------------------------------------------------------------------

    def reset(self):
        """Forget everything about audio."""
        for audio in self._audios:
            audio.reset()

    # -----------------------------------------------------------------------

    def add_audio(self, filename):
        """Add an audio into the list of audio managed by this control.

        The new audio is disabled.

        :param filename: (str)
        :return: (bool)

        """
        if self.exists(filename):
            return False
        new_audio = sppasSimpleAudioPlayer()
        self._audios[new_audio] = False
        loaded = new_audio.load(filename)
        return loaded

    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration this player must consider (in seconds).

        This estimation does not take into account the fact that an audio is
        enabled or disabled. All audio are considered.

        :return: (float)

        """
        if len(self._audios) > 0:
            return max(a.get_duration() for a in self._audios if a.is_unknown() is False)
        else:
            return 0.

    # -----------------------------------------------------------------------

    def exists(self, filename):
        """Return True if the filename is matching an existing audio."""
        for a in self._audios:
            if a.get_filename() == filename:
                return True
        return False

    # -----------------------------------------------------------------------

    def is_enabled(self, filename=None):
        """Return True if any audio or the one of the given filename is enabled."""
        if filename is None:
            return any([self._audios[audio] for audio in self._audios])

        for audio in self._audios:
            if self._audios[audio] is True and filename == audio.get_filename():
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
        for a in self._audios:
            if a.get_filename() == filename:
                self._audios[a] = bool(value)
                if a.is_playing():
                    a.stop()

        return False

    # -----------------------------------------------------------------------

    def are_playing(self):
        """Return True if all enabled audio are playing.

        :return: (bool)

        """
        playing = [audio.is_playing() for audio in self._audios if self._audios[audio] is True]
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
            return any([audio.is_playing() for audio in self._audios])

        for audio in self._audios:
            if audio.is_playing() is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def are_paused(self):
        """Return True if all enabled audio are paused.

        :return: (bool)

        """
        paused = [audio.is_paused() for audio in self._audios if self._audios[audio] is True]
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
            return any([audio.is_paused() for audio in self._audios])

        for audio in self._audios:
            if audio.is_paused() is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def are_stopped(self):
        """Return True if all enabled audio are stopped.

        :return: (bool)

        """
        stopped = [audio.is_stopped() for audio in self._audios if self._audios[audio] is True]
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
            return any([audio.is_stopped() for audio in self._audios])

        for audio in self._audios:
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
            return any([audio.is_loading() for audio in self._audios])

        for audio in self._audios:
            if audio.is_loading() is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_unknown(self, filename=None):
        """Return True if any audio or if the given audio is unknown.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([audio.is_unknown() for audio in self._audios])

        for audio in self._audios:
            if audio.is_unknown() is True and filename == audio.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def remove(self, filename):
        """Remove a media of the list of media managed by this control.

        :param filename: (str)
        :return: (bool)

        """
        audio = None
        for a in self._audios:
            if a.get_filename() == filename:
                audio = a
                break

        if audio is not None:
            audio.stop()
            del self._audios[audio]
            return True

        return False

    # -----------------------------------------------------------------------
    # Player
    # -----------------------------------------------------------------------

    def play(self, from_time=0., to_time=None):
        """Start to play all the enabled audio streams from the current position.

        Start playing only if the audio stream is currently stopped or
        paused and if enabled.

        Under Windows and MacOS, the interval among 2 audio "play" is 11ms.
        Except the 1st one, the other audios will be 'in late' so we do not
        play during the elapsed time instead of playing the audio shifted!
        This problem can't be solved with:
        - threading because of the GIL;
        - multiprocessing because the elapsed time is only reduced to 4ms
        instead of 11ms, but the audios can't be eared!

        :return: (bool) True if the action of playing was performed for at least one audio

        """
        if to_time is None:
            to_time = self.get_duration()
        started_time = None
        process_time = None
        shift = 0.
        nb_playing = 0

        for audio in self._audios:
            if self._audios[audio] is True:
                if started_time is not None and process_time is not None:
                    delta = process_time - started_time
                    delay = delta.seconds + delta.microseconds / 1000000.
                    logging.info(" ... Observed delay is {:.4f}".format(delay))
                    self._all_delays.append(delay)
                    shift += delay

                played = audio.play(from_time + shift, to_time)
                if played is True:
                    nb_playing += 1
                    started_time = process_time
                    process_time = audio.get_time_value()
                    if started_time is None:
                        mean_delay = sum(self._all_delays) / float(len(self._all_delays))
                        started_time = process_time - datetime.timedelta(seconds=mean_delay)

        logging.info(" ... {:d} audio files are playing".format(nb_playing))
        return nb_playing > 0

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause the media and notify parent."""
        paused = False
        for audio in self._audios:
            if audio.is_playing():
                p = audio.pause()
                if p is True:
                    paused = True
        return paused

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the audios.

        :return: (bool) True if at least one audio was stopped.

        """
        stopped = False
        for audio in self._audios:
            s = audio.stop()
            if s is True:
                stopped = True
        return stopped

    # -----------------------------------------------------------------------

    def seek(self, value):
        """Seek all audio to the given position in time.

        :param value: (float) Time value in seconds.

        """
        force_pause = False
        if self.is_playing() is True:
            self.pause()
            force_pause = True

        for audio in self._audios:
            if audio.is_unknown() is False:
                audio.seek(value)

        if force_pause is True:
            self.play()

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._audios)
