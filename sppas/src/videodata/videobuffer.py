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
from cv2 import CAP_PROP_POS_FRAMES, CAP_PROP_FPS, CAP_PROP_POS_MSEC,\
                CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_COUNT

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
    >>> v = VideoBuffer(video, 100, 10)

    Go to the next sequence of the video
    >>> v.next()

    Go to the previous sequence of the video
    >>> v.previous()

    Release the flow taken by the reading of the video.
    >>> v.close()

    """

    def __init__(self, video, size=200, overlap=0):
        """Create a new ImageBuffer instance.

        :param size: (int) The size of the buffer.
        :param overlap: (overlap) The number of values to keep
        from the previous buffer.
        :param video: (mp4, etc...) The video to browse

        """
        # Initialization of the size
        self.__size = None
        self.set_size(size)

        # Initialization of the overlap
        overlap = int(overlap)
        if isinstance(overlap, int) is False:
            raise TypeError
        if overlap > 200:
            raise ValueError
        self.__overlap = overlap

        # The video capture to use
        self.__video = None

        # List of images
        self.__data = list()

        # Last read frame
        self.__last_frame = 0

        # End of the video
        self.__eov = True

        # Initialization of the video
        self.init_video(video)

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return the size of the buffer."""
        return self.__size

    # -----------------------------------------------------------------------

    def set_size(self, value):
        """Set the size of the buffer.

        :param value: (int) The new size of the buffer.

        """
        value = int(value)
        if isinstance(value, int) is False:
            raise TypeError
        if value > 1000:
            raise ValueError
        self.__size = value

    # -----------------------------------------------------------------------

    def get_overlap(self):
        """Return the overlap of the buffer."""
        return self.__overlap

    # -----------------------------------------------------------------------

    def get_eov(self):
        """Return True if it's the end of the video."""
        return self.__eov

    # -----------------------------------------------------------------------

    # Allows to use simplified versions of getter and setter
    eov = property(get_eov, None)

    # -----------------------------------------------------------------------

    def init_video(self, video):
        """Initialize the video.

        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to browse.

        """
        if self.__video is not None:
            self.close()

        # List of images
        self.__data = list()

        # Last read frame
        self.__last_frame = 0

        # Create a videoCapture object
        self.__video = cv2.VideoCapture()

        # Open the video to browse
        try:
            self.__video.open(video)
        except TypeError:
            raise

        # Set the begining of the video to the frame 0
        self.__video.set(CAP_PROP_POS_FRAMES, 0)

    # -----------------------------------------------------------------------

    def get_fps(self):
        """Return the FPS of the video."""
        if self.__video is None:
            return 0
        else:
            return self.__video.get(CAP_PROP_FPS)

    # -----------------------------------------------------------------------

    def get_frame(self):
        """Return the index of the current frame."""
        if self.__video is None:
            return 0
        else:
            return self.__video.get(CAP_PROP_POS_FRAMES)

    # -----------------------------------------------------------------------

    def get_ms(self):
        """Return the current position of the video file in milliseconds."""
        if self.__video is None:
            return 0
        else:
            return self.__video.get(CAP_PROP_POS_MSEC)

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the frames in the video."""
        if self.__video is None:
            return 0
        else:
            return self.__video.get(CAP_PROP_FRAME_WIDTH)

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the frames in the video."""
        if self.__video is None:
            return 0
        else:
            return self.__video.get(CAP_PROP_FRAME_HEIGHT)

    # -----------------------------------------------------------------------

    def get_frame_count(self):
        """Return the number of frames in the video."""
        if self.__video is None:
            return 0
        else:
            return self.__video.get(CAP_PROP_FRAME_COUNT)

    # -----------------------------------------------------------------------

    def __next_append(self, images):
        """Replace the n"size - overlap" last values.

        :param images: (list) The list of images to add.

        """
        for image in images:
            if isinstance(image, np.ndarray) is False:
                raise TypeError

        # Delete the n"self.__size - self.__overlap"
        # first images from the Buffer and keep
        # the n"self.__overlap" images in the Buffer
        del self.__data[0:self.__size - self.__overlap]

        # Add the images in the Buffer
        self.__data.extend(images)

    # -----------------------------------------------------------------------

    def __prev_append(self, images):
        """Replace the n"size - overlap" first values.

        :param images: (list) The list of images to add.

        """
        for image in images:
            if isinstance(image, np.ndarray) is False:
                raise TypeError

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

    def __load_frames(self, nb_time):
        """Browse a sequence of a video.

        :param nb_time: (int) The number of time to loop over the video.
        :returns: False if it's the end of the video or
        a list of images(numpy.ndarray).

        """
        nb_time = int(nb_time)
        if isinstance(nb_time, int) is False:
            raise TypeError
        # if nb_time < 0 or nb_time > 50000:
        #     raise ValueError

        # Create the list to store the images
        images = list()

        # If it's the first frame loop n"self.size" time
        # to initialize the buffer with n"self.size" values
        if self.__last_frame == 0:
            nb_time = self.__size

        # Browse the video
        for i in range(0, nb_time):

            # Grab the next frame
            frame = self.__video.read()

            # To only get the image (numpy.ndarray) from the frame
            frame = frame[1]

            # If it's the end of the video return False
            if frame is None:
                self.__eov = False
                break

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

    def read(self, begining=0, end=0):
        """Browse a sequence of a video.

        :param begining: (int) From which frameID the loop will start.
        :param end: (int) At which frameID the loop will end.
        :returns: False if it's the end of the video or
        a list of images(numpy.ndarray).

        """
        begining = int(begining)
        if isinstance(begining, int) is False:
            raise TypeError
        if begining < 0 or begining > 50000:
            raise ValueError

        end = int(end)
        if isinstance(end, int) is False:
            raise TypeError
        if end < 0 or end > 50000:
            raise ValueError

        if begining != 0 and end == 0:
            end = begining + self.__size

        if end != 0 and begining == 0:
            begining = end - self.__size

        if begining == 0 and end == 0:
            begining = self.__last_frame
            end = self.__last_frame + self.__size

        if begining != 0 and end != 0:
            self.set_size(end - begining)

        self.__video.set(CAP_PROP_POS_FRAMES, begining)

        # Create the list to store the images
        images = list()

        for i in range(begining, end):

            frame = self.__video.read()
            frame = frame[1]
            if frame is None:
                self.__eov = False
                break
            images.append(frame)

        # Set the last frameID to the last frameID the loop goes to
        self.__last_frame = self.__video.get(CAP_PROP_POS_FRAMES)
        cv2.destroyAllWindows()

        # Update the Buffer
        self.__next_append(images)

        # Clear the list
        images.clear()

    # -----------------------------------------------------------------------

    def next(self):
        """Go to the next sequence of the video.

        :returns: False if it's the end of the video.

        """
        if self.__video is None:
            raise IOError

        # Set the begining of the video to the last frameID the Buffer
        # goes to
        self.__video.set(CAP_PROP_POS_FRAMES, self.__last_frame)

        # Launch and store the result of the reading
        result = self.__load_frames(self.__size - self.__overlap)

        # If the video is invald
        if self.__eov is False and self.__video.get(CAP_PROP_POS_FRAMES) == 0:
            raise IOError("The input video is not a valid one")

        # Update the Buffer
        self.__next_append(result)

        # Clear the list
        result.clear()

    # -----------------------------------------------------------------------

    def previous(self):
        """Go to the previous sequence of the video.

        :returns: False if it's the end of the video.

        """
        if self.__video is None:
            raise IOError

        # If the frameID to go to is less than 0 raise an error
        if self.__last_frame - (self.__size + self.__size - self.__overlap) < 0:
            raise ValueError("You can't reach a frameID inferior to 0")

        # Set the begining of the video to the frameID of the precedent Buffer
        self.__video.set(CAP_PROP_POS_FRAMES, self.__last_frame - (self.__size + self.__size - self.__overlap))

        # Launch and store the result of the reading
        result = self.__load_frames(self.__size - self.__overlap)

        # If the video is invalid
        if self.__eov is False and self.__video.get(CAP_PROP_POS_FRAMES) == 0:
            raise IOError("The input video is not a valid one")

        # Update the Buffer
        self.__prev_append(result)

        # Clear the list
        result.clear()

    # -----------------------------------------------------------------------

    def close(self):
        """Release the flow taken by the reading of the video."""
        # Release the video
        self.__video.release()
        self.__video = None

        # List of images
        self.__data = list()

        # Last read frame
        self.__last_frame = 0

        # End of the video
        self.__eov = True

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
        liste = list()
        iterator = self.__iter__()
        for i in range(0, self.__len__()):
            liste.append(str(next(iterator)) + "\n")
        return liste

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

