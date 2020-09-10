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

    src.videodata.videobuffer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.exceptions import NegativeValueError
from sppas.src.exceptions import IntervalRangeException
from .video import sppasVideoReader

# ---------------------------------------------------------------------------


class sppasVideoReaderBuffer(sppasVideoReader):
    """Class to manage a video with a buffer of images.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to use a buffer of images on a video to manage it
    sequentially and to have a better control on it.

    :Example:

    Initialize a VideoBuffer with a size of 100 images and overlap of 10:
    >>> v = sppasVideoReaderBuffer(video, 100, 10)

    Bufferize the next sequence of images of the video:
    >>> v.next()

    Release the flow taken by the reading of the video:
    >>> v.close()

    """

    DEFAULT_BUFFER_SIZE = 200
    DEFAULT_BUFFER_OVERLAP = 0

    def __init__(self, video=None,
                 size=DEFAULT_BUFFER_SIZE,
                 overlap=DEFAULT_BUFFER_OVERLAP):
        """Create a new sppasVideoReaderBuffer instance.

        :param size: (int) Number if images of the buffer
        :param overlap: (overlap) The number of images to keep
        from the previous buffer
        :param video: (mp4, etc...) The video filename to browse

        """
        super(sppasVideoReaderBuffer, self).__init__()

        # Initialization of the buffer size and buffer overlaps
        self.__nb_img = 0
        self.__overlap = 0
        self.set_buffer_size(size)
        self.set_buffer_overlap(overlap)

        # List of images
        self.__data = list()

        # First and last frame indexes of the buffer
        self.__buffer_idx = (-1, -1)

        # Initialization of the video
        if video is not None:
            self.open(video)

    # -----------------------------------------------------------------------

    def open(self, video):
        """Override. Create an opencv video capture from the given video.

        :param video: (name of video file, image sequence, url or video
        stream, GStreamer pipeline, IP camera) The video to browse.

        """
        self.reset()
        sppasVideoReader.open(self, video)

    # -----------------------------------------------------------------------

    def close(self):
        """Override. Release the flow taken by the reading of the video."""
        self.reset()
        sppasVideoReader.close(self)

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the buffer but does not change anything to the video."""
        # List of images
        self.__data = list()

        # Last read frame
        self.__buffer_idx = (-1, -1)

    # -----------------------------------------------------------------------

    def get_buffer_size(self):
        """Return the defined size of the buffer."""
        return self.__nb_img

    # -----------------------------------------------------------------------

    def set_buffer_size(self, value):
        """Set the size of the buffer.

        The new value is applied to the next buffer, it won't affect the
        currently in-use data.

        :param value: (int) The new size of the buffer.
        :raise: ValueError

        """
        value = int(value)
        if value <= 0:
            raise NegativeValueError(value)
        if self.is_opened() is True and value > self.get_nframes():
            raise IntervalRangeException(value, 1, self.get_nframes())

        if self.__overlap >= value:
            raise ValueError("The already defined overlap value {:d} can't be "
                             "greater than the buffer size.")

        self.__nb_img = value

    # -----------------------------------------------------------------------

    def get_buffer_overlap(self):
        """Return the overlap of the buffer."""
        return self.__overlap

    # -----------------------------------------------------------------------

    def set_buffer_overlap(self, value):
        """Set the number of images to keep from the previous buffer.

        The new value is applied to the next buffer, it won't affect the
        currently in-use data.

        :param value: (int)

        """
        overlap = int(value)
        if overlap >= self.__nb_img or overlap < 0:
            raise ValueError
        self.__overlap = value

    # -----------------------------------------------------------------------

    def seek_buffer(self, value):
        """Set the position of the frame for the next buffer to be read.

        It won't change the current position in the video until "next" is
        invoked. It invalidates the current buffer.

        :param value: (int) Frame position

        """
        value = self.check_frame(value)
        self.reset()
        self.__buffer_idx = (-1, value-1)

    # -----------------------------------------------------------------------

    def tell_buffer(self):
        """Return the frame position for the next buffer to be read.

        Possibly, it can't match the current position in the stream, if
        video.read() was invoked for example.

        """
        return self.__buffer_idx[1] + 1

    # -----------------------------------------------------------------------

    def get_buffer_range(self):
        """Return the indexes of the frames of the current buffer.

        :return: (tuple) start index, end index of the frames in the buffer

        """
        if -1 in self.__buffer_idx:
            return -1, -1
        return self.__buffer_idx

    # -----------------------------------------------------------------------

    def next(self):
        """Fill in the buffer with the next sequence of images of the video.

        :return: False if we reached the end of the video

        """
        if self.is_opened() is False:
            return False

        # Fix the number of frames to read
        nb_frames = self.__nb_img - self.__overlap
        # But if it's the first frame loading, we'll fill in the buffer of the
        # full size, i.e. no overlap is to be applied.
        if self.__buffer_idx[1] == -1:
            nb_frames = self.__nb_img

        # Set the beginning position to read in the video
        start_frame = self.__buffer_idx[1] + 1
        self.seek(start_frame)

        # Launch and store the result of the reading
        result = self.__load_frames(nb_frames)
        next_frame = self.tell()

        # Update the buffer and the frame indexes with the current result
        delta = self.__nb_img - self.__overlap
        self.__data = self.__data[delta:]
        self.__buffer_idx = (start_frame - len(self.__data), next_frame - 1)
        self.__data.extend(result)
        result.clear()

        return next_frame != self.get_nframes()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __load_frames(self, nb_frames):
        """Browse a sequence of a video.

        :returns: a list of sppasImage instances

        """
        # Create the list to store the images
        images = list()

        # Browse the video
        for i in range(nb_frames):
            # Grab the next frame. Stop if we reach the end of the video.
            image_array = self.read()
            if image_array is None:
                self.__eov = False
                break

            # Add the image in the storage list
            images.append(image_array)

        # Return the list of images
        return images

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of images in the current data buffer."""
        return len(self.__data)

    # -----------------------------------------------------------------------

    def __iter__(self):
        """Browse the current data buffer."""
        for data in self.__data:
            yield data

    # -----------------------------------------------------------------------

    def __getitem__(self, item):
        return self.__data[item]

    # -----------------------------------------------------------------------

    def __str__(self):
        liste = list()
        iterator = self.__iter__()
        for i in range(len(self.__data)):
            liste.append(str(next(iterator)) + "\n")
        return liste

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

