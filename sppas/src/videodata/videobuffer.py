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

import numpy as np
import cv2
from cv2 import CAP_PROP_POS_FRAMES

from sppas.src.imagedata.coordinates import ImageError

# ---------------------------------------------------------------------------


class VideoBuffer(object):
    """Class to detect faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to use a Buffer on a video to manage it
    sequentially and to have a better control on it.

    For example:

    Initialize a Buffer, with a size of 100, an overlap of 10,
    and a video
    >>> v = VideoBuffer(100, 10, video)

    Go to the next sequence of the video
    >>> v.next()

    Go to the previous sequence of the video
    >>> v.previous()

    Release the flow taken by the reading of the video.
    >>> v.release()

    """

    def __init__(self, size, overlap, video):
        """Create a new ImageBuffer instance.

        :param size: (int) The size of the buffer.
        :param overlap: (overlap) The number of values to keep
        from the previous buffer.
        :param video: (mp4, etc...) The video to browse

        """
        # Initialization of size and overlap of the buffer
        self.__size = size
        self.__overlap = overlap

        # Initialization of the video
        self.__video = None
        self.init_video(video)

        # List of images
        self.__data = list()

        # Last read frame
        self.__last_frame = 0

    # -----------------------------------------------------------------------

    def init_video(self, video):
        """Initialize the video."""
        # Create a videoCapture object
        self.__video = cv2.VideoCapture()

        # Open the video to browse
        self.__video.open(video)

        # Set the begining of the video to the frame 0
        self.__video.set(CAP_PROP_POS_FRAMES, 0)

    # -----------------------------------------------------------------------

    def next_append(self, images):
        """Replace the n"size - overlap" last values."""
        for image in images:
            if isinstance(image, np.ndarray) is False:
                raise ImageError

        # Delete the n"self.__size - self.__overlap"
        # first images from the Buffer and keep
        # the n"self.__overlap" images in the Buffer
        del self.__data[0:self.__size - self.__overlap]

        # Add the images in the Buffer
        self.__data.extend(images)
        return True

    # -----------------------------------------------------------------------

    def prev_append(self, images):
        """Replace the n"size - overlap" first values."""
        for image in images:
            if isinstance(image, np.ndarray) is False:
                raise ImageError

        # Set the last frame to last frame + overlap because
        # while the browse of the video with the method previous
        # we browse n"self.size - self.overlap" times and
        # because of it, in the buffer the last frameID in memorie
        # is n"self.overlap" times above the last frame the loop goes to.
        # So to adjust the real last frame to the last frame in the
        # Buffer it's needed to add the overlap to the last frame ID
        self.__last_frame = self.__last_frame + self.__overlap

        # Store the n"self.overlap" first value in the buffer
        liste = self.__data[0:self.__overlap]

        # Clear the buffer
        self.__data.clear()

        # Add the images in the Buffer
        self.__data.extend(images)

        # Add the storage images in the Buffer
        self.__data.extend(liste)

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return a list of images."""
        return self.__data

    # -----------------------------------------------------------------------

    def read(self, end):
        """Browse a sequence of a video.

        :returns: False if it's the end of the video or
        a list of images(numpy.ndarray).

        """
        # Create the list to store the images
        images = list()

        # If it's the first frame loop n"self.size" time
        # to initialize the buffer with n"self.size" values
        if self.__last_frame == 0:
            end = self.__size

        # Browse the video
        for i in range(0, end):

            # Grab the next frame
            frame = self.__video.read()

            # To only get the image (numpy.ndarray) from the frame
            frame = frame[1]

            # If it's the end of the video return False
            if frame is None:
                return False

            # Add the image in the storage list
            images.append(frame)

            # Show the frame
            # cv2.imshow("Input", frame)
            # key = cv2.waitKey(1) & 0xFF
            # if key == ord("q"):
            #     break

        # Set the last frameID to the last frameID the loop goes to
        self.__last_frame = self.__video.get(CAP_PROP_POS_FRAMES)

        # Destroy the showing window
        cv2.destroyAllWindows()

        # Return the list of images
        return images

    # -----------------------------------------------------------------------

    def next(self):
        """Go to the next sequence of the video.

        :returns: False if it's the end of the video.

        """
        # Set the begining of the video to the last frameID the Buffer
        # goes to
        self.__video.set(CAP_PROP_POS_FRAMES, self.__last_frame)

        # Launch and store the result of the reading
        result = self.read(self.__size - self.__overlap)

        # If it's the end of the video return False
        if result is False:
            return False

        # Update the Buffer
        self.next_append(result)

        # Clear the list
        result.clear()

    # -----------------------------------------------------------------------

    def previous(self):
        """Go to the previous sequence of the video.

        :returns: False if it's the end of the video.

        """
        # If the frameID to go to is less than 0 raise an error
        if self.__last_frame - (self.__size + self.__size - self.__overlap) < 0:
            raise ImageError("You can't reach a frameID inferior to 0")

        # Set the begining of the video to the frameID of the precedent Buffer
        self.__video.set(CAP_PROP_POS_FRAMES, self.__last_frame - (self.__size + self.__size - self.__overlap))

        # Launch and store the result of the reading
        result = self.read(self.__size - self.__overlap)

        # If it's the end of the video return False
        if result is False:
            return False

        # Update the Buffer
        self.prev_append(result)

        # Clear the list
        result.clear()

    # -----------------------------------------------------------------------

    def release(self):
        """Release the flow taken by the reading of the video."""
        self.__video.release()

    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of coordinates."""
        return len(self.__data)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for data in self.__data:
            yield data

    # -----------------------------------------------------------------------

    def __str__(self):
        string = str()
        for i in self.get_data():
            string += str(i) + "\n"
        return string

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

