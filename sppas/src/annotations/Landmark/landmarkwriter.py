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


    src.videodata.coordswriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import numpy as np

from sppas.src.imagedata.imageutils import draw_points
from sppas.src.annotations.Landmark.landmarkoptions import LandmarkOptions
from sppas.src.annotations.Landmark.landmarkoutputs import LandmarkOutputs

# ---------------------------------------------------------------------------


class LandmarkWriter(object):
    """Class to manage outputs files.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, path, fps, pattern, usable=False, csv=False, video=False, folder=False):
        """Create a new sppasImgCoordsWriter instance.

        :param path: (str) The path of the video.
        :param fps: (int) The FPS of the video.
        :param pattern: (str) The pattern to use for the creation of the files.
        :param csv: (boolean) If is True extract images in csv file.
        :param video: (boolean) If is True extract images in a video.
        :param folder: (boolean) If is True extract images in a folder.

        """
        # Initialize the options manager
        self._mOptions = LandmarkOptions(pattern, usable=usable, csv=csv, video=video, folder=folder)

        # The outputs manager
        self._mOutputs = LandmarkOutputs(path, fps, self._mOptions)

        # The index of the current image
        self.__number = 0

    # -----------------------------------------------------------------------

    def set_options(self, draw=True):
        """Set the values of the options."""
        self._mOptions.set_options(draw)

    # -----------------------------------------------------------------------

    def process(self, buffer):
        """Browse the buffer.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        # Initialise the iterator
        iterator = buffer.__iter__()

        # Loop over the buffer
        for frameID in range(0, buffer.__len__()):

            # If image in the overlap continue
            if frameID < buffer.get_overlap():
                continue

            # Go to the next frame
            img = next(iterator)

            image1 = img.copy()
            image2 = img.copy()

            self.manage_modifications(buffer, image1, image2, frameID)

            # Increment the number of image by 1
            self.__number += 1

    # -----------------------------------------------------------------------

    def manage_modifications(self, buffer, image1, image2, frameid):
        """Verify the option values.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image1: (numpy.ndarray) The first image to be processed.
        :param image2: (numpy.ndarray) The second to be processed.
        :param frameid: (int) The ID of the image in the buffer.

        """
        # Loop over the persons
        for i in range(buffer.nb_persons()):

            # If any visage has been detected continue
            if buffer.get_landmark(i, frameid) is None:
                continue

            if self._mOptions.get_usable() is True:
                # Write the usable output videos
                self._manage_usable(buffer, image1, i, frameid)

            if self._mOptions.get_csv() is True or self._mOptions.get_video() is True or \
                    self._mOptions.get_folder() is True:
                # Write the outputs
                self.__manage_verification(buffer, image2, i, frameid)

    # -----------------------------------------------------------------------

    def _manage_usable(self, buffer, image, index, frameid):
        """Manage the creation of one of the usable output video.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameid: (int) The ID of the image in the buffer.

        """
        # Apply landmark
        self.__apply_landmarked(buffer, image, index, frameid)

        # Store the width and the height of the image
        (h, w) = image.shape[:2]

        # Create the usable output videos
        self._mOutputs.out_base(buffer.nb_persons(), w, h)

        # Write the image in usable output video
        self._mOutputs.write_base(image, index)

    # -----------------------------------------------------------------------

    def __manage_verification(self, buffer, image, index, frameid):
        """Manage the creation of the verification outputs.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameid: (int) The ID of the image in the buffer.

        """
        # Apply landmark
        self.__apply_landmarked(buffer, image, index, frameid)

        # Store the width and the height of the image
        (h, w) = image.shape[:2]

        # Create the output files
        self._mOutputs.create_out(buffer.nb_persons(), w, h)

        # Write the output files
        self._mOutputs.write(image, index, self.__number, landmark=buffer.get_landmark(index, frameid))

    # -----------------------------------------------------------------------

    def __apply_landmarked(self, buffer, image, index, frameid):
        """Apply modification based on the landmark.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (numpy.ndarray) The image to be processed.
        :param index: (int) The ID of the person.
        :param frameid: (int) The ID of the image in the buffer.

        """
        # If draw is not None
        if buffer.get_landmark(index, frameid) is not None:
            # Draw the shape on landmarks points
            self.__draw_points(image, buffer.get_landmark(index, frameid), index)

    # -----------------------------------------------------------------------

    def __draw_points(self, img_buffer, landmark_points, index):
        """Draw circle, ellipse or rectangle on landmark points.

        :param img_buffer: (numpy.ndarray) The image to be processed.
        :param landmark_points: (dict) A list of x-axis, y-axis values,
        landmark points.
        :param index: (int) The index of the person in the list of person.

        """
        if isinstance(landmark_points, list) is False:
            raise TypeError

        if isinstance(img_buffer, np.ndarray) is False:
            raise TypeError

        # Get a different color for each person
        number = (index * 80) % 120

        # Draw shape on each landmark points
        for t in landmark_points:
            x, y = t
            draw_points(img_buffer, x, y, number)

    # -----------------------------------------------------------------------

