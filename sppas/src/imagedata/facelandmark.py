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

from sppas.src.config import sppasPathSettings


# ---------------------------------------------------------------------------


class FaceLandmark(object):
    """Class to landmark faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    LEFT_FACE = (1, 8)
    RIGHT_FACE = (9, 17)
    LEFT_BROW_POINTS = (18, 22)
    RIGHT_BROW_POINTS = (23, 27)
    NOSE_POINTS = (28, 36)
    LEFT_EYE_POINTS = (37, 42)
    RIGHT_EYE_POINTS = (43, 48)
    MOUTH_POINTS = (49, 68)

    def __init__(self, cascade, model):
        """Create a new FaceLandmark instance.

        :param cascade: (numpy.ndarray) The model which detects landmark.
        :param model: (numpy.ndarray) The model which detects landmark.

        """

        # The x-axis coordinates
        self.__landmarks_x = list()

        # The y-axis coordinates
        self.__landmarks_y = list()

        # The cascade model
        self.__cascade = cv2.CascadeClassifier(cascade)

        # The detector
        self.__model = model

    # -----------------------------------------------------------------------

    def get_landmarks_x(self):
        """Return a list of x-axis values."""
        return self.__landmarks_x

    # -----------------------------------------------------------------------

    def get_landmark_x(self, index):
        """Return a x-axis value."""
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        return self.__landmarks_x[index]

    # -----------------------------------------------------------------------

    def get_landmarks_y(self):
        """Return a list of y-axis values."""
        return self.__landmarks_y

    # -----------------------------------------------------------------------

    def get_landmark_y(self, index):
        """Return a y-axis value."""
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        return self.__landmarks_y[index]

    # -----------------------------------------------------------------------

    def __store_points(self, coordinates):
        """Store x-axis, y-axis values in each list."""
        for i in range(0, 68):
            self.__landmarks_x.append(coordinates.part(i).x)
            self.__landmarks_x.append(coordinates.part(i).y)

    # -----------------------------------------------------------------------

    def landmarks(self, image):
        """Determined landmarks from a face.

        :param image: (numpy.ndarray) The image to be processed.

        """
        cv2.imshow("Output", image)
        # cv2.waitKey(0)

        faces = self.__cascade.detectMultiScale(image, 1.5, 5)
        print(faces)
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.loadModel(self.__model)
        ok, landmarks = recognizer.fit(image, faces)
        print("landmarks LBF", ok, landmarks)

        # # Loop over coordinates and draw circle around points
        # for index in range(0, 68):
        #     cv2.circle(face_image, (self.__landmarks_x[index], self.__landmarks_y[index]), 1, (0, 0, 255), -1)
        # else:
        #     raise ImageError
        # # Show image
        # cv2.imshow("Output", face_image)
        # cv2.waitKey(0)

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


# haarcascade = os.path.join(sppasPathSettings().resources, "image",
#                            "haarcascade_frontalface_alt2.xml")
# f = FaceLandmark(haarcascade)
# image = "../../../../../video_test/image0.jpg"
# image = cv2.imread(image)
# f.landmarks(image)
# print(help(cv2))
