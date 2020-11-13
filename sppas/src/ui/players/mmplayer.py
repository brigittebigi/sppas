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

    src.ui.players.mmplayer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Multi-media player: play several media really synchronously.
    Video streams are not displayed but images are updated. This class must
    be overridden to display videos in a GUI.

    Requires simpleaudio to play the audio files and opencv to read the videos.

    Limitations that will raise a Runtime error:

        1. can't add a new media when playing or paused;
        2. can't play if at least a media is loading.

"""

import logging
import datetime

from sppas.src.ui.players.baseplayer import sppasBasePlayer
from sppas.src.ui.players.audioplayer import sppasSimpleAudioPlayer
from sppas.src.ui.players.videoplayer import sppasSimpleVideoPlayer

# ---------------------------------------------------------------------------


class sppasMultiMediaPlayer(object):
    """A player which can play several media synchronously.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can load, play and browse throw several media streams of given files.

    """

    def __init__(self):
        """Instantiate the multi media player."""
        # Key = the media player / value = bool:enabled
        self._medias = dict()
        # Observed delays between 2 consecutive "play".
        # Used to synchronize files.
        self._all_delays = [0.01]
        self.__from_time = 0.    # position (in seconds) to start playing
        self.__to_time = 0.      # position (in seconds) of ending play

    # -----------------------------------------------------------------------

    def reset(self):
        """Forget everything about the media players."""
        for mp in self._medias:
            mp.reset()

    # -----------------------------------------------------------------------

    def add_audio(self, filename):
        """Add an audio into the list of media managed by this control.

        The new audio is disabled.

        :param filename: (str)
        :return: (bool)

        """
        if self.is_playing() or self.is_paused():
            raise RuntimeError("Can't add audio: at least a media is still playing.")

        if self.exists(filename):
            return False
        new_audio = sppasSimpleAudioPlayer()
        self._medias[new_audio] = False
        loaded = new_audio.load(filename)
        return loaded

    # -----------------------------------------------------------------------

    def add_video(self, filename):
        """Add a video into the list of media managed by this control.

        The new video is disabled.

        :param filename: (str)
        :return: (bool)

        """
        if self.is_playing() or self.is_paused():
            raise RuntimeError("Can't add video: at least a media is still playing.")

        if self.exists(filename):
            return False
        new_video = sppasSimpleVideoPlayer()
        self._medias[new_video] = False
        loaded = new_video.load(filename)
        return loaded

    # -----------------------------------------------------------------------

    def add_media(self, media):
        """Add a media into the list of media managed by this control.

        The new media is disabled.

        :param media: (sppasBasePlayer)
        :return: (bool)

        """
        if self.is_playing() or self.is_paused():
            raise RuntimeError("Can't add media: at least a media is still playing.")

        if isinstance(media, sppasBasePlayer) is False:
            return False
        self._medias[media] = False

    # -----------------------------------------------------------------------

    def remove(self, filename):
        """Remove a media of the list.

        :param filename: (str) Name of the file of the media to be removed
        :return: (bool)

        """
        if self.exists(filename) is False:
            return False

        media_obj = None
        for mp in self._medias:
            if mp.get_filename() == filename:
                mp.stop()
                media_obj = mp
                break
        del self._medias[media_obj]
        return True

    # -----------------------------------------------------------------------

    def get_duration(self, filename=None):
        """Return the duration this player must consider (in seconds).

        This estimation does not take into account the fact that a media is
        enabled or disabled. All valid media are considered.

        :param filename: (str) The media to get duration or None to get the max duration
        :return: (float)

        """
        if filename is None:
            dur = list()
            if len(self._medias) > 0:
                for mp in self._medias:
                    if mp.is_unknown() is False and mp.is_loading() is False:
                        dur.append(mp.get_duration())

            if len(dur) > 0:
                return max(dur)

        elif self.exists(filename) is True:
            return self._get_media(filename).get_duration()

        return 0.

    # -----------------------------------------------------------------------

    def exists(self, filename):
        """Return True if the given filename is matching an existing media.

        :param filename: (str)
        :return: (bool)

        """
        for mp in self._medias:
            if mp.get_filename() == filename:
                return True
        return False

    # -----------------------------------------------------------------------

    def is_enabled(self, filename=None):
        """Return True if any media or the given one is enabled.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([self._medias[mp] for mp in self._medias])

        for mp in self._medias:
            if self._medias[mp] is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def enable(self, filename, value=True):
        """Enable or disable the given media.

        When a media is disabled, it can't be paused nor played. It can only
        stay in the stopped state.

        :param filename: (str)
        :param value: (bool)
        :return: (bool)

        """
        for mp in self._medias:
            if mp.get_filename() == filename:
                self._medias[mp] = bool(value)
                if mp.is_playing():
                    mp.stop()

        return False

    # -----------------------------------------------------------------------

    def are_playing(self):
        """Return True if all enabled media are playing.

        :return: (bool)

        """
        playing = [mp.is_playing() for mp in self._medias if self._medias[mp] is True]
        if len(playing) == 0:
            return False

        # all([]) is True
        return all(playing)

    # -----------------------------------------------------------------------

    def is_playing(self, filename=None):
        """Return True if any media or if the given media is playing.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_playing() for mp in self._medias])

        for mp in self._medias:
            if mp.is_playing() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def are_paused(self):
        """Return True if all enabled media are paused.

        :return: (bool)

        """
        paused = [mp.is_paused() for mp in self._medias if self._medias[mp] is True]
        if len(paused) == 0:
            return False

        # all([]) is True
        return all(paused)

    # -----------------------------------------------------------------------

    def is_paused(self, filename=None):
        """Return True if any media or if the given media is paused.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_paused() for mp in self._medias])

        for mp in self._medias:
            if mp.is_paused() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def are_stopped(self):
        """Return True if all enabled media are stopped.

        :return: (bool)

        """
        stopped = [mp.is_stopped() for mp in self._medias if self._medias[mp] is True]
        if len(stopped) == 0:
            return False

        # all([]) is True
        return all(stopped)

    # -----------------------------------------------------------------------

    def is_stopped(self, filename=None):
        """Return True if any media or if the given one is stopped.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_stopped() for mp in self._medias])

        for mp in self._medias:
            if mp.is_stopped() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_loading(self, filename=None):
        """Return True if any media or if the given one is loading.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_loading() for mp in self._medias])

        for mp in self._medias:
            if mp.is_loading() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_unknown(self, filename=None):
        """Return True if any media or if the given one is unknown.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_unknown() for mp in self._medias])

        for mp in self._medias:
            if mp.is_unknown() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_audio(self, filename=None):
        """Return True if any media or if the given one is an audio.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_audio() for mp in self._medias])

        for mp in self._medias:
            if mp.is_audio() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_video(self, filename=None):
        """Return True if any media or if the given one is a video.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_video() for mp in self._medias])

        for mp in self._medias:
            if mp.is_video() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def remove(self, filename):
        """Remove a media of the list of media managed by this control.

        :param filename: (str)
        :return: (bool)

        """
        media_player = None
        for mp in self._medias:
            if mp.get_filename() == filename:
                media_player = mp
                break

        if media_player is not None:
            media_player.stop()
            del self._medias[media_player]
            return True

        return False

    # -----------------------------------------------------------------------
    # Player
    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the current interval or the whole streams."""
        self.play_interval()

    # -----------------------------------------------------------------------

    def play_interval(self, from_time=None, to_time=None):
        """Start to play an interval of the enabled media streams.

        Start playing only the media streams that are currently stopped or
        paused and if enabled.

        Under Windows and MacOS, the delay between 2 runs of "play" is 11ms.
        Except the 1st one, the other medias will be 'in late' so we do not
        play during the elapsed time instead of playing the media shifted!
        This problem CANNOT be solved with:
            - threading because of the GIL;
            - multiprocessing because the elapsed time is only reduced to 4ms
              instead of 11ms, but the audios can't be eared!

        :param from_time: (float) Start to play at this given time or at the current from time if None
        :param to_time: (float) Stop to play at this given time or at the current end time if None
        :return: (bool) True if the action of playing was performed for at least one media

        """
        if self.is_loading():
            raise RuntimeError("Can't play: at least a media is still loading.")

        if from_time is not None:
            self.__from_time = from_time
        if to_time is not None:
            self.__to_time = to_time

        # start to play all videos
        nb_playing = 0
        started_time = None
        for mp in self._medias:
            if self._medias[mp] is True and mp.is_video() is True:
                if mp.prepare_play(self.__from_time, self.__to_time):
                    played = mp.play()
                    if played is True:
                        nb_playing += 1
                        if started_time is None:
                            started_time = mp.get_time_value()

        process_time = None
        shift = 0.

        # start to play & synchronize all audios
        for mp in self._medias:
            if self._medias[mp] is True and mp.is_audio() is True:
                if started_time is not None and process_time is not None:
                    delta = process_time - started_time
                    delay = delta.seconds + delta.microseconds / 1000000.
                    logging.debug(" ... observed delay is {:.4f}".format(delay))
                    self._all_delays.append(delay)
                    shift += delay

                if mp.prepare_play(self.__from_time + shift, self.__to_time):
                    played = mp.play()
                    if played is True:
                        nb_playing += 1
                        started_time = process_time
                        process_time = mp.get_time_value()
                        if started_time is None:
                            mean_delay = sum(self._all_delays) / float(len(self._all_delays))
                            logging.debug(" ... mean delay is {:.4f}".format(mean_delay))
                            started_time = process_time - datetime.timedelta(seconds=mean_delay)

        logging.debug(" ... {:d} media files are playing".format(nb_playing))
        return nb_playing > 0

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause the medias that are currently playing."""
        paused = False
        for mp in self._medias:
            p = mp.pause()
            if p is True and paused is False:
                paused = True
                position = mp.media_tell()
                self.__from_time = float(position) / float(mp.get_framerate())
        return paused

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the medias.

        :return: (bool) True if at least one media was stopped.

        """
        stopped = False
        for mp in self._medias:
            s = mp.stop()
            if s is True:
                stopped = True
        if stopped is True:
            self.__from_time = 0.
            self.__to_time = self.get_duration()
        return stopped

    # -----------------------------------------------------------------------

    def seek(self, value):
        """Seek all media streams to the given position in time.

        :param value: (float) Time value in seconds.

        """
        force_pause = False
        if self.is_paused() is True:
            force_pause = True
        if self.is_playing() is True:
            self.pause()
            force_pause = True

        for mp in self._medias:
            if mp.is_unknown() is False and mp.is_loading() is False:
                mp.seek(value)

        if force_pause is True:
            self.__from_time = value
            self.play()

    # -----------------------------------------------------------------------
    # About the audio
    # -----------------------------------------------------------------------

    def get_nchannels(self, filename):
        """Return the number of channels."""
        for mp in self._medias:
            if mp.is_audio() is True and filename == mp.get_filename():
                return mp.get_nchannels()
        return 0

    # -----------------------------------------------------------------------

    def get_sampwidth(self, filename):
        for mp in self._medias:
            if mp.is_audio() is True and filename == mp.get_filename():
                return mp.get_sampwidth()
        return 0

    # -----------------------------------------------------------------------

    def get_framerate(self, filename):
        for mp in self._medias:
            if (mp.is_audio() is True or mp.is_video() is True) and filename == mp.get_filename():
                return mp.get_framerate()
        return 0

    # -----------------------------------------------------------------------

    def get_frames(self, filename):
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # About the video
    # -----------------------------------------------------------------------

    def get_video_width(self, filename):
        for mp in self._medias:
            if mp.is_video() is True and filename == mp.get_filename():
                return mp.get_width()
        return 0

    def get_video_height(self, filename):
        for mp in self._medias:
            if mp.is_video() is True and filename == mp.get_filename():
                return mp.get_height()
        return 0

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _get_media(self, filename):
        """Return the media matching the given filename."""
        for mp in self._medias:
            if filename == mp.get_filename():
                return mp
        raise KeyError

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._medias)
