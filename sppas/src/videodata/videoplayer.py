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

from sppas.src.config import MediaState
from .video import sppasVideoReader

# ---------------------------------------------------------------------------


class sppasSimpleVideoPlayer(object):
    """A video player based on opencv library.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can load, play and browse throw the video stream of a given file.

    """

    def __init__(self):
        super(sppasSimpleVideoPlayer, self).__init__()

        self._ms = MediaState().unknown
        self._filename = None    # name of the video file
        self._video = None       # sppasVideoReader() embedding a cv2.VideoCapture()

    # -----------------------------------------------------------------------

    def __del__(self):
        try:
            self._video.close()
        except:
            pass

    # -----------------------------------------------------------------------

    def duration(self):
        """Return the duration of the loaded video (float)."""
        if self._filename is None:
            return 0.
        return self._video.get_duration()

    # -----------------------------------------------------------------------

    def reset(self):
        """Re-initialize all known data."""
        self._ms = MediaState().unknown
        self._filename = None
        if self._video is not None:
            self._video.close()
            self._video = None

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Open the file that filename refers to and load a buffer of frames.

        :param filename: (str) Name of a video file
        :return: (bool) True if successfully opened.

        """
        self.reset()
        try:
            self._filename = filename
            self._video = sppasVideoReader()
            self._video.open(filename)
            self._ms = MediaState().stopped
            return True

        except Exception as e:
            logging.error("Error when opening file {:s}: "
                          "{:s}".format(filename, str(e)))
            self._video = sppasVideoReader()
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
        """Return True if the media is still loading."""
        if self._filename is None:
            return False

        return self._ms == MediaState().loading

    # -----------------------------------------------------------------------

    def is_playing(self):
        """Return True if the media is playing."""
        if self._filename is None:
            return False

        return self._ms == MediaState().playing

    # -----------------------------------------------------------------------

    def is_paused(self):
        """Return True if the media is paused."""
        if self._filename is None:
            return False

        return self._ms == MediaState().paused

    # -----------------------------------------------------------------------

    def is_stopped(self):
        """Return True if the media is stopped."""
        if self._filename is None:
            return False

        return self._ms == MediaState().stopped

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the video stream from the current position.

        Start playing only is the video stream is currently stopped or
        paused.

        :return: (bool) True if the action of playing was performed

        """
        if self._filename is None:
            logging.error("No media file to play.")
            return False

        played = False
        with MediaState() as ms:
            if self._ms == ms.unknown:
                logging.error("The video stream of {:s} can't be played for "
                              "an unknown reason.".format(self._filename))

            elif self._ms == ms.loading:
                logging.error("The video stream of {:s} can't be played: "
                              "still loading".format(self._filename))

            elif self._ms == ms.playing:
                logging.warning("The video stream of {:s} is already "
                                "playing.".format(self._filename))

            else:  # stopped or paused
                self._play()
                played = True

        return played

    # -----------------------------------------------------------------------

    def _play(self):
        """Run the process of playing in a thread."""
        cv2.namedWindow("window", cv2.WINDOW_NORMAL)
        self._ms = MediaState().playing
        time_value = datetime.datetime.now()
        time_delay = round(1. / self._video.get_framerate(), 3)

        while self._video.is_opened():
            # stop the loop.
            # Either the stop() method was invoked or the reset() one.
            if self._ms in (MediaState().stopped, MediaState().unknown):
                break

            elif self._ms == MediaState().playing:
                # read the next frame from the file
                frame = self._video.read_frame(process_image=False)
                if frame is not None:
                    cv2.imshow('window', frame)
                    # Sleep as many time as required to get the appropriate read speed
                    cur_time = datetime.datetime.now()
                    delta = cur_time - time_value
                    delta_seconds = delta.seconds + delta.microseconds / 1000000.
                    waiting_time = round(time_delay - delta_seconds, 3)
                    if waiting_time > 0:
                        time.sleep(waiting_time)
                    time_value = datetime.datetime.now()
                else:
                    # we reached the end of the file
                    self.stop()

            if cv2.waitKey(1) & 0xFF == 27:
                self.stop()

        cv2.destroyWindow("window")

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        self._ms = MediaState().stopped

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the video stream (float)."""
        offset = self._video.tell()
        return float(offset) / float(self._video.get_framerate())

