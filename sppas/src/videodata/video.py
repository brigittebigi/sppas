# -*- coding : UTF-8 -*-
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

    src.videodata.video.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

import numpy as np
import logging
import cv2

from ..imgdata import sppasImage
from ..exceptions import NegativeValueError
from ..exceptions import IntervalRangeException
from ..exceptions import RangeBoundsException

from .videodataexc import VideoReadError

# ---------------------------------------------------------------------------


class sppasVideo(object):
    """Class to wrap a video with OpenCV.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is embedding a VideoCapture() object or None and define some
    getters and setters to manage such video easily.

    :Example:
    
    >>> # Create the instance and open the video
    >>> vid = sppasVideo()
    >>> vid.open("my_video_file.xxx")
    
    >>> # Read one frame from the current position
    >>> image = vid.read()

    >>> # Set the current position
    >>> vid.seek(frame_pos)
    >>> # Get the current position
    >>> vid.tell()


    """

    def __init__(self):
        """Create a sppasVideo. """
        # The OpenCV video to browse
        self.__video = None

    # -----------------------------------------------------------------------

    def open(self, video):
        """Initialize a VideoCapture.

        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to browse.

        """
        if self.__video is not None:
            self.close()

        # Create an OpenCV VideoCapture object and open the video
        self.__video = cv2.VideoCapture()
        try:
            self.__video.open(video)
            if not self.__video.isOpened():
                logging.error("OpenCV failed to open the video. "
                              "Video file not supported?")
                raise Exception
        except:
            self.__video = None
            raise VideoReadError(video)

        # Set the beginning of the video to the frame 0
        self.__video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # -----------------------------------------------------------------------

    def close(self):
        """Release the flow taken by the reading of the video."""
        self.__video.release()
        self.__video = None

    # -----------------------------------------------------------------------

    def _read(self):
        """Read a frame of the video.

        :return: (ndarray, None)

        """
        if self.__video is None:
            return None
        success, img = self.__video.read()
        if img is None or success is False:
            return None
        return sppasVideo._preprocess_image(img)

    # -----------------------------------------------------------------------

    def read(self, from_pos=-1, to_pos=-1):
        """Browse a sequence of a video.

        If both from_pos and to_pos are -1, only one frame is read.

        :param from_pos: (int) frameID value to start reading. -1 means the current position.
        :param to_pos: (int) frameID value to stop reading. -1 means the last frame of the video.
        :returns: None, an image or a list of images(numpy.ndarray).

        """
        if self.__video is None:
            return None

        if from_pos == -1 and to_pos == -1:
            from_pos = self.tell()
            to_pos = from_pos + 1
        else:
            # Fix the position to start reading the video
            if from_pos == -1:
                from_pos = self.tell()
            else:
                from_pos = self.check_frame(from_pos)

            # Fix the position to stop reading the video
            if to_pos == -1:
                to_pos = self.get_nframes()
            else:
                to_pos = self.check_frame(to_pos)

            if from_pos >= to_pos:
                raise RangeBoundsException(from_pos, to_pos)

        # Create the list to store the images
        images = list()

        # Set the position to start reading the frames
        self.seek(from_pos)

        # Read as many frames as expected or as possible
        for i in range(from_pos, to_pos):
            frame = self._read()
            if frame is None:
                # this should never happen...
                break
            images.append(frame)

        if len(images) == 0:
            return None
        if len(images) == 1:
            return images[0]
        return images

    # -----------------------------------------------------------------------

    def check_frame(self, value):
        """Raise an exception is the given value is an invalid frameID.

        :param value: (int)
        :raise: ValueError
        :return: (int)

        """
        value = int(value)
        if value < 0:
            raise NegativeValueError(value)
        if self.video_capture() is True and value > self.get_nframes():
            raise IntervalRangeException(value, 1, self.get_nframes())
        return value

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def get_framerate(self):
        """Return the FPS of the current video."""
        if self.__video is None:
            return 0
        return self.__video.get(cv2.CAP_PROP_FPS)

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the index of the current frame position."""
        if self.__video is None:
            return 0
        return int(self.__video.get(cv2.CAP_PROP_POS_FRAMES))

    # -----------------------------------------------------------------------

    def seek(self, value):
        """Set a new frame position in the video.

        :param value: (int)
        :raise: ValueError

        """
        value = self.check_frame(value)
        self.__video.set(cv2.CAP_PROP_POS_FRAMES, value)

    # -----------------------------------------------------------------------

    def get_ms(self):
        """Return the current position (milliseconds) of the video."""
        if self.__video is None:
            return 0
        return self.__video.get(cv2.CAP_PROP_POS_MSEC)

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the frames in the video."""
        if self.__video is None:
            return 0
        return self.__video.get(cv2.CAP_PROP_FRAME_WIDTH)

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the frames in the video."""
        if self.__video is None:
            return 0
        return self.__video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # -----------------------------------------------------------------------

    def get_nframes(self):
        """Return the number of frames in the video."""
        if self.__video is None:
            return 0
        return int(self.__video.get(cv2.CAP_PROP_FRAME_COUNT))

    # -----------------------------------------------------------------------

    def video_capture(self):
        """Return True if a video was properly initialized."""
        return self.__video is not None

    # -----------------------------------------------------------------------

    @staticmethod
    def _preprocess_image(image):
        """Change size and array size of the image.

        :param image: (np.array)
        :return: (sppasImage)

        """
        # image = cv2.resize(image, (width, height))
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = np.array(image, dtype=np.uint8)  # Unsigned integer (0 to 255)
        image = np.expand_dims(image, -1)
        return sppasImage(input_array=image)

