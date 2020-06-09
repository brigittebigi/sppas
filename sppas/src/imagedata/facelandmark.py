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

from random import randint
import cv2

import os
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
        self.__landmarks = list()

        # The cascade model
        self.__cascade = cv2.CascadeClassifier(cascade)

        # The detector
        self.__model = model

    # -----------------------------------------------------------------------

    def get_landmarks(self):
        """Return a list of x-axis values."""
        return self.__landmarks

    # -----------------------------------------------------------------------

    def get_landmark(self, index):
        """Return a x-axis value."""
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        return self.__landmarks[index]

    # -----------------------------------------------------------------------

    def get_left_face(self):
        """Return coordinates of the left side of the face."""
        return self.__landmarks[FaceLandmark.LEFT_FACE[0] - 1: FaceLandmark.LEFT_FACE[1] - 1]

    # -----------------------------------------------------------------------

    def get_right_face(self):
        """Return coordinates of the right side of the face."""
        return self.__landmarks[FaceLandmark.RIGHT_FACE[0] - 1: FaceLandmark.RIGHT_FACE[1] - 1]

    # -----------------------------------------------------------------------

    def get_left_brow(self):
        """Return coordinates of the left brow."""
        return self.__landmarks[FaceLandmark.LEFT_BROW_POINTS[0] - 1: FaceLandmark.LEFT_BROW_POINTS[1] - 1]

    # -----------------------------------------------------------------------

    def get_right_brow(self):
        """Return coordinates of the right brow."""
        return self.__landmarks[FaceLandmark.RIGHT_BROW_POINTS[0] - 1: FaceLandmark.RIGHT_BROW_POINTS[1] - 1]

    # -----------------------------------------------------------------------

    def get_nose(self):
        """Return coordinates of the nose."""
        return self.__landmarks[FaceLandmark.NOSE_POINTS[0] - 1: FaceLandmark.NOSE_POINTS[1] - 1]

    # -----------------------------------------------------------------------

    def get_left_eyes(self):
        """Return coordinates of the left eye."""
        return self.__landmarks[FaceLandmark.LEFT_EYE_POINTS[0] - 1: FaceLandmark.LEFT_EYE_POINTS[1] - 1]

    # -----------------------------------------------------------------------

    def get_right_eyes(self):
        """Return coordinates of the right eye."""
        return self.__landmarks[FaceLandmark.RIGHT_EYE_POINTS[0] - 1: FaceLandmark.RIGHT_EYE_POINTS[1] - 1]

    # -----------------------------------------------------------------------

    def get_mouth(self):
        """Return coordinates of the mouth."""
        return self.__landmarks[FaceLandmark.MOUTH_POINTS[0] - 1: FaceLandmark.MOUTH_POINTS[1] - 1]

    # -----------------------------------------------------------------------

    def __store_points(self, coordinates):
        """Store x-axis, y-axis values in each list."""
        for i in range(0, 68):
            self.__landmarks.append((coordinates.part(i).x, coordinates.part(i).y))

    # -----------------------------------------------------------------------

    def landmarks(self, image):
        """Determined landmarks from a face.

        :param image: (numpy.ndarray) The image to be processed.

        """
        # cv2.imshow("Output", image)
        # cv2.waitKey(0)

        # faces = self.__cascade.detectMultiScale(image, 1.5, 5)
        # recognizer = cv2.face.createFacemarkLBF()
        # recognizer.loadModel(self.__model)
        # ok, landmarks = recognizer.fit(image, faces)
        # print("landmarks LBF", ok, landmarks)

        self.__landmark_points(image)

    # -----------------------------------------------------------------------

    def __landmark_points(self, image):
        """Determined points for tests because face module does not work.

        :param image: (numpy.ndarray) The image to be processed.

        """
        h, w = image.shape[:2]
        # for i in range(68):
        #     x = randint(0, w + 1)
        #     y = randint(0, h + 1)
        #     self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3*w/4 * ((i+1)/10))
            y = int((h/10) * 2)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3*w/4 * ((i+1)/10))
            y = int((h/10) * 3)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3*w/4 * ((i+1)/10))
            y = int((h/10) * 4)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3*w/4 * ((i+1)/10))
            y = int((h/10) * 5)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3*w/4 * ((i+1)/10))
            y = int((h/10) * 6)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3*w/4 * ((i+1)/10))
            y = int((h/10) * 7)
            self.__landmarks.append((x, y))

        for i in range(8):
            x = int(3*w/4 * ((i+1)/10))
            y = int((h/10) * 8)
            self.__landmarks.append((x, y))

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the storage list of FaceLandmark."""
        self.__landmarks = list()

    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of x, y coordinates."""
        return len(self.__landmarks)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for i in range(0, self.__len__()):
            yield self.__landmarks[i]

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

        for value in self.__landmarks:
            if value[0].__eq__(x_axis) is False:
                isIN = False

        for value in self.__landmarks:
            if value[1].__eq__(y_axis) is False:
                isIN = False

        return isIN

    # -----------------------------------------------------------------------

    def __str__(self):
        both = ""
        for value in self.__landmarks:
            both += str(value)
        return both

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

