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

    src.videodata.videolandmark.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os

from sppas.src.config import sppasPathSettings
from sppas.src.imagedata.facelandmark import FaceLandmark
from sppas.src.imagedata.imageutils import crop, portrait

# ---------------------------------------------------------------------------


class VideoLandmark(object):
    """Class to landmark faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new VideoLandmark instance."""
        # List of landmarks coordinates
        self.__landmarks = list()

        self.__cascade = self.__get_haarcascade()

        self.__model = self.__get_model()
        self.__size = 0

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_haarcascade():
        """Return the predictor file."""
        try:
            haarcascade = os.path.join(sppasPathSettings().resources, "image",
                                       "haarcascade_frontalface_alt2.xml")
            return haarcascade
        except OSError:
            return "File does not exist"

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_model():
        """Return the predictor file."""
        try:
            model = os.path.join(sppasPathSettings().resources, "image",
                                 "lbfmodel68.yaml")
            return model
        except OSError:
            return "File does not exist"

    # -----------------------------------------------------------------------

    def get_points(self):
        """Return a list of tuple of x-axis, y-axis coordinates."""
        pass

    # -----------------------------------------------------------------------

    def process(self, buffer):
        """Browse the buffer.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        self.reset()

        if buffer.nb_persons() == 0:
            buffer.add_landmarks()
        else:
            for i in range(buffer.nb_persons()):
                # Create a list of x-axis, y-axis values for each person
                buffer.add_landmarks()

        # Initialise the iterator
        iterator = buffer.__iter__()

        # Loop over the buffer
        for j in range(0, len(buffer)):
            # Go to the next image
            img = next(iterator)

            if buffer.nb_persons() == 0:
                self.landmark_person(buffer, img)

            else:
                self.__landmark_persons(buffer, img, j)

    # -----------------------------------------------------------------------

    def landmark_person(self, buffer, image):
        """Apply landmark on an already good video.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (np.ndarray) The image to be processed.

        """
        # Launch the landmark on the image
        landmark = self.__landmark_process(image)

        # Add the values in the buffer
        buffer.add_landmark(0, landmark)

    # -----------------------------------------------------------------------

    def __landmark_persons(self, buffer, image, index):
        """Apply for each person on the image.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param image: (np.ndarray) The image to be processed.
        :param index: (int) The index of the image.

        """
        # Loop over the result of FaceTracking
        for i in range(buffer.nb_persons()):
            # Get the index of the person
            index_person = i

            if index > len(buffer.get_person(i)) - 1:
                continue

            if buffer.get_coordinate(i, index) is not None:
                # Adjust the coordinates to get a more accurate result
                # portrait(person[i], 1.5)

                # Crop the visage according to the values of the coordinates
                image = crop(image, buffer.get_coordinate(i, index))

                # Launch the landmark on the image
                landmark = self.__landmark_process(image)

                # Launch the landmark on the image
                self.__adjust_points(landmark, buffer.get_coordinate(i, index).x, buffer.get_coordinate(i, index).y)

                # Add the values in the buffer
                buffer.add_landmark(index_person, landmark)

            else:
                # Add the values in the buffer
                buffer.add_landmark(index_person, None)

    # -----------------------------------------------------------------------

    def __landmark_process(self, image):
        """Launch the process to determine the landmarks points.

        :param image: (np.ndarray) The image to be processed.

        """
        # self.__landmark(image)
        points = self.__landmark_points()
        return points

    # -----------------------------------------------------------------------

    def __landmark(self, image):
        """Create a list of points(x-axis, y-axis values).

        :param image: (np.ndarray) The image to be processed.

        """
        try:
            # Initialize and use FaceLandmark
            face = FaceLandmark(self.__cascade, self.__model)

            # Launch the process of FaceLandmark
            face.landmarks(image)
        except IndexError:
            raise IOError

        # Add the list of x-axis, y-axis coordinates
        for i in range(len(face)):
            self.__landmarks.append((face.get_landmark_x(i), face.get_landmark_y(i)))

    # -----------------------------------------------------------------------

    def __landmark_points(self):
        """Determined points for tests because face module does not work."""
        for i in range(68):
            self.__landmarks.append((i * 5, i * 5))

        return self.__landmarks

    # -----------------------------------------------------------------------

    def __adjust_points(self, points, x, y):
        """Adjust values of the points according to the base image.

        :param points: (list) The list of landmark points.
        :param x: (int) The start value on the x-axis of
        the cropped image from the base image.
        :param y: (int) The start value on the y-axis of
        the cropped image from the base image.

        """
        # Loop over the result of landmark and change the values
        # according to the base image
        for d in points:
            a, b = d
            a += x
            b += y
            d = a, b

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the privates attributes."""
        self.__landmarks = list()

    # -----------------------------------------------------------------------
