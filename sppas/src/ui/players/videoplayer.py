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

    src.videodata.videoplayer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A simple video player that set the current image but does not display it.

"""

import logging
import datetime
import time
import threading

from sppas.src.videodata.video import sppasVideoReader
from .baseplayer import sppasBasePlayer
from .pstate import PlayerState
from .pstate import PlayerType

# ---------------------------------------------------------------------------


class sppasSimpleVideoPlayer(sppasBasePlayer):
    """A video player that must be overridden to display the images.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can load, play and browse throw the video stream of a given file.

    """

    def __init__(self):
        super(sppasSimpleVideoPlayer, self).__init__()
        # no self._player member.
        self._current_image = None

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
        sppasBasePlayer.reset(self)

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Open the file that filename refers to and load a buffer of frames.

        :param filename: (str) Name of a video file
        :return: (bool) True if successfully opened and loaded.

        """
        self.reset()
        self._filename = filename
        self._ms = PlayerState().loading
        try:
            self._media = sppasVideoReader()
            self._media.open(filename)
            self._ms = PlayerState().stopped
            self._mt = PlayerType().video
            return True

        except Exception as e:
            logging.error("Error when opencv was opening file {:s}: "
                          "{:s}".format(filename, str(e)))
            self._media = sppasVideoReader()
            self._ms = PlayerState().unknown
            self._mt = PlayerType().unknown
            return False

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the video stream.

        :return: (bool) True if the action of playing was performed

        """
        if self._ms in (PlayerState().paused, PlayerState().stopped):
            th = threading.Thread(target=self._play_process, args=())
            self._ms = PlayerState().playing
            self._start_datenow = datetime.datetime.now()
            th.start()
            return True

        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        if self._ms == PlayerState().playing:
            self._ms = PlayerState().stopped
            # seek at the exact moment we stopped to play
            self._from_time = self.tell()
            # set our state
            self._ms = PlayerState().paused
            return True

        return False

    # -----------------------------------------------------------------------

    def _play_process(self):
        """Run the process of playing."""
        # the position to start and to stop playing
        start_offset = int(self._from_time * float(self._media.get_framerate()))
        end_offset = int(self._to_time * float(self._media.get_framerate()))
        self._media.seek(start_offset)

        time_delay = round(1. / self._media.get_framerate(), 3)
        min_sleep = time_delay / 4.

        # the time when we started to play and the number of frames we displayed.
        frm = 0
        self._start_datenow = datetime.datetime.now()
        self._current_image = None

        while self._media.is_opened():
            if self._ms == PlayerState().playing:
                # read the next frame from the file
                frame = self._media.read_frame(process_image=False)
                frm += 1
                cur_offset = start_offset + frm

                if frame is None or cur_offset > end_offset:
                    # we reached the end of the file or the end of the period
                    self.stop()
                else:
                    self._current_image = frame.irgb()

                    expected_time = self._start_datenow + datetime.timedelta(seconds=(frm * time_delay))
                    cur_time = datetime.datetime.now()
                    if cur_time < expected_time:
                        # I'm reading too fast, wait a little time.
                        delta = expected_time - cur_time
                        delta_seconds = delta.seconds + delta.microseconds / 1000000.
                        if delta_seconds > min_sleep:
                            time.sleep(delta_seconds)

                    elif cur_time > expected_time:
                        # I'm reading too slow, I'm in late.
                        delta = cur_time - expected_time
                        delta_seconds = delta.seconds + delta.microseconds / 1000000.

                        if delta_seconds > time_delay:
                            # in late of at least 1 frame
                            nf = int(delta_seconds / time_delay)
                            self._media.seek(self._media.tell() + nf)
                            frm += nf
                            logging.warning("Ignored {:d} frame just after {:f} seconds"
                                            "".format(nf, float(cur_offset) * self._media.get_framerate()))

            else:
                # stop the loop if any other state than playing
                break

        self._start_datenow = None
        self._current_image = None

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        if self._ms not in (PlayerState().loading, PlayerState().unknown):
            self._ms = PlayerState().stopped
            self._media.seek(0)
            return True
        return False

    # -----------------------------------------------------------------------

    def seek(self, time_pos=0):
        """Seek the video stream at the given position in time.

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

    def media_tell(self):
        return self._media.tell()

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the video stream (float)."""
        offset = self._media.tell()
        return float(offset) / float(self._media.get_framerate())

    # -----------------------------------------------------------------------
    # About the video
    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the loaded video (float)."""
        if self._media is None:
            return 0.
        return self._media.get_duration()

    # -----------------------------------------------------------------------

    def get_framerate(self):
        if self._media is not None:
            return self._media.get_framerate()
        return 0

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the frames in the video."""
        if self._media is None:
            return 0
        return self._media.get_width()

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the frames in the video."""
        if self._media is None:
            return 0
        return self._media.get_height()
