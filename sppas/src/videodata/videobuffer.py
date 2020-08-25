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

from ..exceptions import NegativeValueError
from ..exceptions import IntervalRangeException
from .video import sppasVideo

# ---------------------------------------------------------------------------


class sppasVideoBuffer(sppasVideo):
    """Class to manage a video with a buffer of images.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to use a buffer of images on a video to manage it
    sequentially and to have a better control on it.

    :Example:

    Initialize a VideoBuffer, with a size of 100 images, an overlap of 10:
    >>> v = sppasVideoBuffer(video, 100, 10)

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
        """Create a new sppasVideoBuffer instance.

        :param size: (int) Number if images of the buffer
        :param overlap: (overlap) The number of images to keep
        from the previous buffer
        :param video: (mp4, etc...) The video filename to browse

        """
        super(sppasVideoBuffer, self).__init__()

        # Initialization of the buffer size and buffer overlaps
        self.__size = 0
        self.__overlap = 0
        self.set_size(size)
        self.set_overlap(overlap)

        # List of images
        self.__data = list()

        # Last bufferized frame
        self.__last_frame = 0

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
        sppasVideo.open(self, video)

    # -----------------------------------------------------------------------

    def close(self):
        """Override. Release the flow taken by the reading of the video."""
        self.reset()
        sppasVideo.close(self)

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the buffer but does not change anything to the video."""
        # List of images
        self.__data = list()

        # Last read frame
        self.__last_frame = 0

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return the defined size of the buffer."""
        return self.__size

    # -----------------------------------------------------------------------

    def set_size(self, value):
        """Set the size of the buffer.

        The new value is applied to the next buffer, it won't affect the
        currently in-use data.

        :param value: (int) The new size of the buffer.
        :raise: ValueError

        """
        value = int(value)
        if value <= 0:
            raise NegativeValueError(value)
        if self.video_capture() is True and value > self.get_nframes():
            raise IntervalRangeException(value, 1, self.get_nframes())

        if self.__overlap >= value:
            raise ValueError("The already defined overlap value {:d} can't be "
                             "greater than the buffer size.")

        self.__size = value

    # -----------------------------------------------------------------------

    def get_overlap(self):
        """Return the overlap of the buffer."""
        return self.__overlap

    # -----------------------------------------------------------------------

    def set_overlap(self, value):
        """Set the number of images to keep from the previous buffer.

        The new value is applied to the next buffer, it won't affect the
        currently in-use data.

        :param value: (int)

        """
        overlap = int(value)
        if overlap >= self.__size or overlap < 0:
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
        self.__last_frame = value

    # -----------------------------------------------------------------------

    def tell_buffer(self):
        """Return the current frame position for the buffer.

        Possibly, it can't match the current position in the stream, if
        video.read() was invoked for example.

        """
        return self.__last_frame

    # -----------------------------------------------------------------------

    def next(self):
        """Go to the next sequence of the video.

        :returns: False if it's the end of the video.

        """
        if self.video_capture() is False:
            return

        # Fix the number of frames to read
        nb_frames = self.__size - self.__overlap
        # But if it's the first frame loading, we'll fill in the buffer of the
        # full size, i.e. no overlap is to be applied.
        if self.__last_frame == 0:
            nb_frames = self.__size

        # Launch and store the result of the reading
        result = self.__load_frames(nb_frames)

        # Update the Buffer
        # Delete the n"self.__size - self.__overlap"
        # first images from the buffer and keep
        # the n"self.__overlap" images in the Buffer
        del self.__data[0:self.__size - self.__overlap]

        # Add the images in the buffer
        self.__data.extend(result)
        result.clear()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __load_frames(self, nb_frames):
        """Browse a sequence of a video.

        :returns: a list of sppasImage instances

        """
        # Create the list to store the images
        images = list()

        # Set the beginning of the video to the last frameID
        self.seek(self.__last_frame)

        # Browse the video
        for i in range(nb_frames):
            # Grab the next frame. Stop if we reach the end of the video.
            image_array = self.read()
            if image_array is None:
                self.__eov = False
                break

            # Add the image in the storage list
            images.append(image_array)

        # Set the last frameID to the last frameID the loop goes to
        self.__last_frame = self.tell()

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

