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
    
    sppasVideoReader and sppasVideoWriter are abstract classes to manipulate
    the opencv cv2.VideoCapture and cv2.VideoWriter.

"""

import logging
import numpy as np
import cv2

from sppas.src.imgdata import sppasImage
from sppas.src.exceptions import NegativeValueError
from sppas.src.exceptions import IntervalRangeException
from sppas.src.exceptions import RangeBoundsException
from sppas.src.exceptions import sppasKeyError
from sppas.src.utils.datatype import bidict

from .videodataexc import VideoOpenError
from .videodataexc import VideoBrowseError
from .videodataexc import VideoWriteError
from .videodataexc import VideoLockError

# ---------------------------------------------------------------------------


class sppasVideoReader(object):
    """Class to wrap a VideoCapture with OpenCV.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is embedding a VideoCapture() object and define some
    getters and setters to manage such video easily.
    It was tested only to open/read videos from files, not to capture a
    video stream from a camera, etc.

    :Example:
    
    >>> # Create the instance and open the video
    >>> vid = sppasVideoReader()
    >>> vid.open("my_video_file.xxx")
    
    >>> # Read one frame from the current position
    >>> image = vid.read()

    >>> # Set the current position
    >>> vid.seek(frame_pos)
    >>> # Get the current position
    >>> vid.tell()

    >>> # Release the video stream
    >>> vid.close()

    """

    def __init__(self):
        """Create a sppasVideoReader. """
        # The OpenCV video to capture
        self.__video = cv2.VideoCapture()
        self.__lock = False

    # -----------------------------------------------------------------------

    def open(self, video):
        """Initialize a VideoCapture.

        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to browse.

        """
        if self.__lock is True:
            logging.error("The video can't be opened because another video "
                          "stream is not already opened.")
            raise VideoLockError

        # Create an OpenCV VideoCapture object and open the video
        try:
            self.__video.open(video)
            if self.__video.isOpened() is False:
                raise Exception("The video was not opened by OpenCV Library "
                                "for an unknown reason.")
            self.__lock = True
        except Exception as e:
            self.__lock = False
            logging.error("Video {} can't be opened: {}".format(video, str(e)))
            raise VideoOpenError(video)

        # Test the video under this platform...
        success = True
        test_pos = self.get_nframes() - 10
        if test_pos > 0:
            success = self.__video.set(cv2.CAP_PROP_POS_FRAMES, test_pos)
            if success is True:
                real_pos = self.__video.get(cv2.CAP_PROP_POS_FRAMES)
                if real_pos != test_pos:
                    success = False
        if success is False:
            self.close()
            raise VideoBrowseError(video)

        # Set the beginning of the video to the frame 0
        self.__video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # -----------------------------------------------------------------------

    def is_opened(self):
        """Return True if a video is already opened and ready to write."""
        return self.__lock

    # -----------------------------------------------------------------------

    def close(self):
        """Release the flow taken by the reading of the video."""
        self.__video.release()
        self.__lock = False

    # -----------------------------------------------------------------------

    def read_frame(self, process_image=True):
        """Read a frame of the video.

        :return: (ndarray, None)

        """
        if self.__lock is False:
            return None
        success, img = self.__video.read()
        if img is None or success is False:
            return None

        if process_image is False:
            return img
        return sppasVideoReader._preprocess_image(img)

    # -----------------------------------------------------------------------

    def read(self, from_pos=-1, to_pos=-1, process_image=True):
        """Browse a sequence of a video.

        If both from_pos and to_pos are -1, only one frame is read.

        :param from_pos: (int) frameID value to start reading. -1 means the current position.
        :param to_pos: (int) frameID value to stop reading. -1 means the last frame of the video.
        :param process_image: (bool) convert the image to reduce size, uint8, etc
        :returns: None, an image or a list of images(numpy.ndarray).

        """
        if self.__lock is False:
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
        for i in range(to_pos-from_pos):
            frame = self.read_frame(process_image)
            if frame is None:
                break
            images.append(frame)

        if len(images) == 0:
            return None
        if len(images) == 1:
            return images[0]
        return images

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the index of the current frame position."""
        if self.__lock is False:
            return 0
        return int(self.__video.get(cv2.CAP_PROP_POS_FRAMES))

    # -----------------------------------------------------------------------

    def seek(self, value):
        """Set a new frame position in the video.

        :param value: (int)
        :raise: ValueError

        """
        if self.__lock is False:
            raise IOError("No video is opened: seek is not possible.")
        value = self.check_frame(value)
        success = self.__video.set(cv2.CAP_PROP_POS_FRAMES, value)
        if success is False:
            raise IOError("Seek is not supported by your platform for this video.")

    # -----------------------------------------------------------------------

    def check_frame(self, value):
        """Raise an exception is the given value is an invalid frameID.

        :param value: (int)
        :raise: ValueError
        :return: (int) -1 if no video is opened

        """
        if self.__lock is False:
            return -1
        value = int(value)
        if value < 0:
            raise NegativeValueError(value)
        if self.is_opened() is True and value > self.get_nframes():
            raise IntervalRangeException(value, 1, self.get_nframes())
        return value

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the video in seconds (float)."""
        if self.__lock is False:
            return 0.
        return float(self.get_nframes()) * (1. / float(self.get_framerate()))

    # -----------------------------------------------------------------------

    def get_framerate(self):
        """Return the FPS of the current video."""
        if self.__lock is False:
            return 0
        return int(self.__video.get(cv2.CAP_PROP_FPS))

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the frames in the video."""
        if self.__lock is False:
            return 0
        return int(self.__video.get(cv2.CAP_PROP_FRAME_WIDTH))

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the frames in the video."""
        if self.__lock is False:
            return 0
        return int(self.__video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # -----------------------------------------------------------------------

    def get_nframes(self):
        """Return the number of frames in the video."""
        if self.__lock is False:
            return 0
        return int(self.__video.get(cv2.CAP_PROP_FRAME_COUNT))

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def _preprocess_image(image):
        """Change size and array size of the image.

        :param image: (np.array)
        :return: (sppasImage)

        """
        image = np.array(image, dtype=np.uint8)  # Unsigned integer (0 to 255)
        return sppasImage(input_array=image)
        # image = np.expand_dims(image, -1)
        # image = cv2.resize(image, (width, height))
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------


class sppasVideoWriter(object):
    """Class to write a video on disk, image by image.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is embedding a VideoWriter() object and define some
    getters and setters to manage such video easily.

    """

    # Actually, I don't know what exactly is the max value of cv2.VideoWriter
    # 1000 is the max my nvidia GE Force GT 80 accepts in its configuration
    MAX_FPS = 1000

    # Associate a human-readable FOURCC code and a file extension
    FOURCC = {
        ".mp4": "mpv4",
        ".avi": "mjpg",
        ".mkv": "h264"
    }

    # Non-exhaustive list of standard resolutions
    RESOLUTIONS = {
        "LD": (640, 480, 15),       # 4:3
        "SD": (704, 528, 25),       # 4:3
        "HD": (1920, 1080, 25),     # 16:9
        "WFHD": (2560, 1080, 25),   # 21:9
        "UHD": (2560, 1440, 25),
        "WQHD": (3440, 1440, 25),   # 21:9
        "DFHD": (3840, 1080, 30),   # 32:9
        "4K": (3840, 2160, 30),     # 16:9
        "WUHD": (5120, 2160, 30),   # 21:9
        "DQHD": (5120, 1440, 30),   # 32:9
        "UW5K": (5760, 2400, 30),   # 21:9
        "6K": (6400, 1800, 30),     # 32:9
        "UW7K": (7680, 3200, 30),   # 21:9
        "DUHD": (7680, 2160, 30),   # 32:9
        "8K": (7680, 4320, 60),     # 16:9
        "UW8K": (8620, 3600, 60),   # 21:9
        "UW10K": (10240, 4320, 60)  # 21:9
    }

    # Strategy in case the given image size to write does not match the
    # video size. Stretch does not preserve the aspect ratio but the others do.
    ASPECT = bidict()
    ASPECT[0] = "center"   # Center the image into a blank image of the given size.
    ASPECT[1] = "stretch"  # Resize to the specified size.
    ASPECT[2] = "extend"   # Scale the image to match the given width or height.
    ASPECT[3] = "zoom"     # Resize and crop the image to zoom to the given size.

    # -----------------------------------------------------------------------

    def __init__(self):
        """Create a sppasVideoWriter. """
        # The OpenCV video
        self.__video = cv2.VideoWriter()

        # Members to fix properties of the video stream - before opening
        self._fps = 25             # frames per second
        self._size = (704, 528)    # (width, height) of the images
        self._aspect = sppasVideoWriter.ASPECT["extend"]

        # Members to help to manage the video stream - when opened
        self.__lock = False        # True if a video stream is opened
        self.__nframes = 0         # number of images already been written

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    @staticmethod
    def get_extensions():
        """Return the list of supported extensions."""
        return sppasVideoWriter.FOURCC.keys()

    # -----------------------------------------------------------------------

    @staticmethod
    def get_fourcc(ext):
        """Return the FOURCC string corresponding to an extension.

        :param ext: (str) Extension of a filename
        :return: (str)

        """
        ext = str(ext)
        if ext.startswith(".") is False:
            ext = "." + ext.lower()

        return sppasVideoWriter.FOURCC.get(ext, "")

    # -----------------------------------------------------------------------

    @staticmethod
    def get_ext(fourcc):
        """Return the extension string corresponding to the fourcc.

        :param fourcc: (str) FOURCC name
        :return: (str)

        """
        if isinstance(fourcc, (list, tuple)):
            fourcc = "".join(fourcc)
        else:
            fourcc = str(fourcc)
            fourcc = fourcc.replace(" ", "")
        fourcc = fourcc.lower()

        for ext in sppasVideoWriter.FOURCC:
            if sppasVideoWriter.FOURCC[ext] == fourcc:
                return ext

        return ""

    # -----------------------------------------------------------------------

    def set_resolution(self, name="SD"):
        """Set the video resolution: images size and frame rate.

        Some of the possible values for the name of the resolution are:

            - LD: 640×480 / 15 fps
            - SD: 704×576 / 25 fps
            - HD: 1920x1,080 / 25 fps
            - WFHD: 2560 x 1080 / 25 fps
            - UHD: 2560 x 1440 / 25 fps
            - 4K: 3840 x 2160 / 30 fps
            - 8K: 7680 x 4320 / 60 fps

        :param name: (str) Name of the resolution
        :raise: VideoLockError, sppasKeyError

        """
        if self.__lock is True:
            logging.error("The video resolution can only be changed if the "
                          "video stream is not already opened.")
            raise VideoLockError

        if name.upper() not in sppasVideoWriter.RESOLUTIONS.keys():
            raise sppasKeyError(name, "RESOLUTIONS")

        resolution = sppasVideoWriter.RESOLUTIONS[name.upper()]
        self._size = (resolution[0], resolution[1])
        self._fps = resolution[2]

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return the (width, height) of the video."""
        return self._size

    # -----------------------------------------------------------------------

    def set_size(self, width, height):
        """Fix a personalized size for the video to write.

        :param width: (int) number of columns in range (20, 12000)
        :param height: (int) number of rows in range (20, 5000)

        """
        if self.__lock is True:
            logging.error("The video size can only be changed if the video "
                          "stream is not already opened.")
            raise VideoLockError

        width = int(width)
        height = int(height)
        if width < 0 or width > 10000:
            raise IntervalRangeException(width, 0, 5000)
        if height < 0 or height > 5000:
            raise IntervalRangeException(height, 0, 5000)

    # -----------------------------------------------------------------------

    def get_fps(self):
        """Return the defined fps value to write video files."""
        return self._fps

    # -----------------------------------------------------------------------

    def set_fps(self, value):
        """Fix the framerate of the output video.

        :param value: (int) frame per seconds
        :raise: NegativeValueError, IntervalRangeError

        """
        if self.__lock is True:
            logging.error("The video fps can only be changed if the video "
                          "stream is not already opened.")
            raise VideoLockError

        value = int(value)
        if value < 0:
            raise NegativeValueError(value)
        if value > sppasVideoWriter.MAX_FPS:
            raise IntervalRangeException(value, 0, sppasVideoWriter.MAX_FPS)
        self._fps = value

    # -----------------------------------------------------------------------
    # Manage the video stream
    # -----------------------------------------------------------------------

    def open(self, video):
        """Open a file stream to write images into.

        :param video: (str) Filename

        """
        if self.__lock is True:
            logging.error("The video can't be opened because another video "
                          "stream is not already opened.")
            raise VideoLockError

        # Create the fourcc corresponding to the image file extension
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 'H', '2', '6', '4'
        try:
            self.__video.open(video, fourcc, self._fps, self._size)
            if self.__video.isOpened() is False:
                raise IOError("The video was not opened by OpenCV Library "
                              "for an unknown reason.")
            self.__lock = True
            self.__nframes = 0
        except Exception as e:
            logging.error("Video {} can't be created: {}".format(video, str(e)))
            raise VideoWriteError(video)

    # -----------------------------------------------------------------------

    def is_opened(self):
        """Return True if a video is already opened and ready to write."""
        return self.__lock

    # -----------------------------------------------------------------------

    def close(self):
        """Release the flow taken by the reading of the video."""
        self.__video.release()
        self.__lock = False
        self.__nframes = 0

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def get_framerate(self):
        """Return the FPS of the current video."""
        return self._fps

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the frames in the video."""
        return self._size[0]

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the frames in the video."""
        return self._size[1]

    # -----------------------------------------------------------------------

    def get_nframes(self):
        """Return the number of frames written in the video."""
        return self.__nframes

    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the written video in seconds (float)."""
        if self.__lock is False:
            return 0.
        return float(self.get_nframes()) * (1. / float(self.get_framerate()))

    # -----------------------------------------------------------------------
    # Write into the video stream
    # -----------------------------------------------------------------------
    
    def get_aspect(self, as_int=True):
        """Return a string defining the aspect strategy to write images."""
        if as_int is True:
            return self._aspect
        return sppasVideoWriter.ASPECT[self._aspect]

    # -----------------------------------------------------------------------

    def set_aspect(self, aspect):
        """Set the aspect strategy to write the image.

        :param aspect: (int or str)

        """
        if aspect not in sppasVideoWriter.ASPECT:
            raise KeyError("Unknown image aspect {}".format(self._aspect))

        if isinstance(aspect, int):
            aspect = sppasVideoWriter.ASPECT[aspect]

        self._aspect = sppasVideoWriter.ASPECT[aspect]

    # -----------------------------------------------------------------------

    def write(self, image):
        """Append an image to the video stream."""
        if self.__lock is False:
            raise Exception("Actually there's no video stream defined.")

        # Resize the image and/or add black background all around and/or 
        # center...
        w, h = self._size
        if self._aspect in ("center", sppasVideoWriter.ASPECT["center"]):
            img = image.icenter(w, h)
        elif self._aspect in ("stretch", sppasVideoWriter.ASPECT["stretch"]):
            img = image.iresize(w, h)
        elif self._aspect in ("extend", sppasVideoWriter.ASPECT["extend"]):
            img = image.iextend(w, h)
        elif self._aspect in ("zoom", sppasVideoWriter.ASPECT["zoom"]):
            img = image.izoom(w, h)
        else:
            raise Exception("Can't write image: unknown image aspect {}"
                            "".format(self._aspect))
        
        # This should not happen but some mult with floats can be imprecise
        if img.width != w or img.height != h:
            img = img.iresize(w, h)
            
        self.__video.write(img)
