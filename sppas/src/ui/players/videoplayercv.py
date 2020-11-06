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

    A simple video player based on opencv library.
    https://opencv.org/

    OpenCV is only reading the images, not the sounds of the video media.

"""

import logging
import cv2
import datetime
import time
import threading

from sppas.src.videodata.video import sppasVideoReader
from .pstate import PlayerState
from .baseplayer import sppasBasePlayer

# ---------------------------------------------------------------------------


class sppasSimpleVideoPlayerCV(sppasBasePlayer):
    """A video player based on opencv library.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can load, play and browse throw the video stream of a given file.

    """

    def __init__(self):
        super(sppasSimpleVideoPlayerCV, self).__init__()
        # no self._player member. opencv is used to display frames.

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
        try:
            self._filename = filename
            self._media = sppasVideoReader()
            self._media.open(filename)
            self._ms = PlayerState().stopped
            return True

        except Exception as e:
            logging.error("Error when opening or loading file {:s}: "
                          "{:s}".format(filename, str(e)))
            self._media = sppasVideoReader()
            self._ms = PlayerState().unknown
            return False

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the video stream from the current position.

        Start playing only is the video stream is currently stopped or
        paused.

        :return: (bool) True if the action of playing was performed

        """
        if self._ms in (PlayerState().paused, PlayerState().stopped):
            th = threading.Thread(target=self._play_process, args=())
            self._ms = PlayerState().playing
            self._start_datenow = datetime.datetime.now()
            th.start()
            return True

        return False
        # ::::: at some time of the development, I had this problem :::::
        # A threaded play does not work under Linux & MacOS.
        # Under Linux, the following error occurs:
        # QObject::killTimer: Timers cannot be stopped from another thread
        # QBasicTimer::start: QBasicTimer can only be used with threads started with QThread
        # Under MacOS, the application is crashing, and exit with error 132.
        # Instead... we play and wait to be stopped to return:

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        if self._ms == PlayerState().playing:
            self._ms = PlayerState().paused

    # -----------------------------------------------------------------------

    def _play_process(self):
        """Run the process of playing."""
        cv2.namedWindow("window", cv2.WINDOW_NORMAL)
        time_value = datetime.datetime.now()
        time_delay = round(1. / self._media.get_framerate(), 3)

        while self._media.is_opened():
            # stop the loop.
            # Either the stop() method was invoked or the reset() one.
            if self._ms in (PlayerState().stopped, PlayerState().unknown):
                break

            elif self._ms == PlayerState().playing:
                # read the next frame from the file
                frame = self._media.read_frame(process_image=False)
                if frame is not None:
                    cv2.imshow('window', frame)
                    # Sleep as many time as required to get the appropriate read speed
                    cur_time = datetime.datetime.now()
                    delta = cur_time - time_value
                    delta_seconds = delta.seconds + delta.microseconds / 1000000.
                    waiting_time = round(time_delay - delta_seconds, 3)
                    if waiting_time > 0.005:
                        time.sleep(waiting_time)
                    time_value = datetime.datetime.now()
                else:
                    # we reached the end of the file
                    self.stop()

            elif self._ms == PlayerState().paused:
                time.sleep(time_delay/4.)
                time_value = datetime.datetime.now()

            if cv2.waitKey(1) & 0xFF == 27:
                self.stop()

        cv2.destroyWindow("window")
        return True

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
