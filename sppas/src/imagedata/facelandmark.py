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

    src.imagedata.facelandmark.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import numpy as np
import cv2
import dlib

from sppas.src.config import sppasPathSettings
from sppas.src.imagedata.coordinates import Coordinates, ImageError
from sppas.src.imagedata.imageutils import crop


# ---------------------------------------------------------------------------


class FaceLandmark(object):
    """Class to landmark faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, image, coords):
        """Create a new FaceLandmark instance.

        :param image: (numpy.ndarray) The image to be processed.
        :param coords: (Coordinates) The coordinates of the face.

        """
        # The image to be processed
        if isinstance(image, np.ndarray) is False:
            raise TypeError
        self.__image = image

        # The coordinate of the face in the image
        if isinstance(coords, Coordinates) is False:
            raise TypeError
        self.__coordinates = coords

        # The x-axis coordinates
        self.__landmarks_x = list()

        # The y-axis coordinates
        self.__landmarks_y = list()

        # The detector
        self.__detector = dlib.get_frontal_face_detector()

        # The predictor
        self.__predictor = dlib.shape_predictor(self.__get_predictor())

    # -----------------------------------------------------------------------

    def get_landmarks_x(self):
        """Return a list of x-axis coordinates."""
        return self.__landmarks_x

    # -----------------------------------------------------------------------

    def get_landmarks_y(self):
        """Return a list of y-axis coordinates."""
        return self.__landmarks_y

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_predictor():
        """Return the predictor file."""
        try:
            predictor = os.path.join(sppasPathSettings().resources, "video",
                                     "shape_predictor_68_face_landmarks.dat")
            return predictor
        except OSError:
            return "File does not exist"

    # -----------------------------------------------------------------------

    def store_points(self, coordinates):
        """Store x-axis, y-axis values in each list."""
        for i in range(0, 68):
            self.__landmarks_x.append(coordinates.part(i).x)
            self.__landmarks_x.append(coordinates.part(i).y)

    # -----------------------------------------------------------------------

    def __prepare_face(self):
        """Crop the face from the image."""
        return crop(self.__image, self.__coordinates)

    # -----------------------------------------------------------------------

    def full_face(self):
        """Recalibrate x-axis, y-axis coordinates for the image."""
        for x in self.__landmarks_x:
            x += self.__coordinates.x
        for y in self.__landmarks_y:
            y += self.__coordinates.y

    # -----------------------------------------------------------------------

    def __landmarks(self, face_image):
        """Determined landmarks from a face.

        :param face_image: (numpy.ndarray) The image to be processed.

        """
        # Transform image into gray scale image
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        # Create the bounding box of the face
        rects = self.__detector(gray, 1)

        # Loop over the face detections
        if len(rects) == 1:
            # Determine the facial landmarks of the face
            rect = rects[0]
            coordinates = self.__predictor(gray, rect)

            # Store the x, y coordinates in the right list
            self.store_points(coordinates)

            # Loop over coordinates and draw circle around points
            for index in range(0, 68):
                cv2.circle(face_image, (self.__landmarks_x[index], self.__landmarks_y[index]), 1, (0, 0, 255), -1)
        else:
            raise ImageError
        # Show image
        cv2.imshow("Output", face_image)
        cv2.waitKey(0)

    # -----------------------------------------------------------------------

    def process(self):
        """Launch the landmarks process."""
        self.__landmarks(self.__prepare_face())

    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of x, y coordinates."""
        return len(self.__landmarks_x)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for i in range(0, self.__len__()):
            yield self.__landmarks_x[i], self.__landmarks_y[i]

    # ----------------------------------------------------------------------

    def __contains__(self, x_axis, y_axis):
        """Return true if value in self.__landmarks_x, self.__landmarks_y.

        :param x_axis: (int) The x-axis coordinate.
        :param y_axis: (int) The y-axis coordinate.

        """
        isIN = True
        if isinstance(x_axis, int) is False:
            raise ValueError
        if isinstance(y_axis, int) is False:
            raise ValueError

        for x in self.__landmarks_x:
            if x.__eq__(x_axis) is False:
                isIN = False
        for y in self.__landmarks_y:
            if y.__eq__(y_axis) is False:
                isIN = False

        return isIN

    # -----------------------------------------------------------------------

    def __str__(self):
        both = ""
        for x in self.__landmarks_x:
            both += "(" + str(x)
        for y in self.__landmarks_y:
            both += ", " + str(y) + ")"

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

