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

    src.annotations.FaceMark.facelandmark.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires the "video" feature of SPPAS.
    Automatic face landmark detection.

"""

import logging
import cv2
import os

from sppas.src.config import paths
from sppas.src.exceptions import sppasIOError, sppasError

# ---------------------------------------------------------------------------


class FaceLandmark(object):
    """Estimate face landmarks on an image of a face or a portrait.

    :author:       Florian Hocquet, Brigitte Bigi
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

    def __init__(self):
        """Create a new FaceLandmark instance."""
        # Coordinates of the 68 points detected on the face
        self.__landmarks = list()

        # Load the model
        # The cascade model for a supervised face detection
        self.__cascade = None
        self.__recognizer = None

    # -----------------------------------------------------------------------

    def load_model(self, model=None, haarcascade=None):
        """Initialize proto file and model file.

        :param model: (str) Filename of the recognizer model.
        :param haarcascade: (str) Filename of the Haar cascade classifier
        :raise: IOError, Exception

        """
        # Set default model and haar cascade files
        # in order to be able to test the class
        if model is None:
            model = os.path.join(paths.resources, "faces", "lbfmodel68.yaml")
        if haarcascade is None:
            haarcascade = os.path.join(paths.resources, "faces", "haarcascade_frontalface_alt2.xml")

        # Use the given model and haar cascade
        if os.path.exists(model) is False:
            raise sppasIOError(model)
        if os.path.exists(haarcascade) is False:
            raise sppasIOError(haarcascade)

        self.__cascade = cv2.CascadeClassifier(haarcascade)
        self.__recognizer = cv2.face.createFacemarkLBF()
        self.__recognizer.loadModel(model)

    # -----------------------------------------------------------------------
    # Getters of specific points
    # -----------------------------------------------------------------------

    def get_left_face(self):
        """Return coordinates of the left side of the face."""
        if len(self.__landmarks) == 0:
            return list()
        return self.__landmarks[FaceLandmark.LEFT_FACE[0] - 1: FaceLandmark.LEFT_FACE[1]]

    # -----------------------------------------------------------------------

    def get_right_face(self):
        """Return coordinates of the right side of the face."""
        if len(self.__landmarks) == 0:
            return list()
        return self.__landmarks[FaceLandmark.RIGHT_FACE[0] - 1: FaceLandmark.RIGHT_FACE[1]]

    # -----------------------------------------------------------------------

    def get_left_brow(self):
        """Return coordinates of the left brow."""
        if len(self.__landmarks) == 0:
            return list()
        return self.__landmarks[FaceLandmark.LEFT_BROW_POINTS[0] - 1: FaceLandmark.LEFT_BROW_POINTS[1]]

    # -----------------------------------------------------------------------

    def get_right_brow(self):
        """Return coordinates of the right brow."""
        if len(self.__landmarks) == 0:
            return list()
        return self.__landmarks[FaceLandmark.RIGHT_BROW_POINTS[0] - 1: FaceLandmark.RIGHT_BROW_POINTS[1]]

    # -----------------------------------------------------------------------

    def get_nose(self):
        """Return coordinates of the nose."""
        if len(self.__landmarks) == 0:
            return list()
        return self.__landmarks[FaceLandmark.NOSE_POINTS[0] - 1: FaceLandmark.NOSE_POINTS[1]]

    # -----------------------------------------------------------------------

    def get_left_eyes(self):
        """Return coordinates of the left eye."""
        if len(self.__landmarks) == 0:
            return list()
        return self.__landmarks[FaceLandmark.LEFT_EYE_POINTS[0] - 1: FaceLandmark.LEFT_EYE_POINTS[1]]

    # -----------------------------------------------------------------------

    def get_right_eyes(self):
        """Return coordinates of the right eye."""
        if len(self.__landmarks) == 0:
            return list()
        return self.__landmarks[FaceLandmark.RIGHT_EYE_POINTS[0] - 1: FaceLandmark.RIGHT_EYE_POINTS[1]]

    # -----------------------------------------------------------------------

    def get_mouth(self):
        """Return coordinates of the mouth."""
        if len(self.__landmarks) == 0:
            return list()
        return self.__landmarks[FaceLandmark.MOUTH_POINTS[0] - 1: FaceLandmark.MOUTH_POINTS[1]]

    # -----------------------------------------------------------------------
    # Automatic detection of the landmark points
    # -----------------------------------------------------------------------

    def __store_points(self, coordinates):
        """Store x-axis, y-axis values in each list."""
        if len(coordinates) != 68:
            raise ValueError
        if coordinates is None:
            self.__landmarks.append(None)
        for coord in coordinates:
            self.__landmarks.append((int(coord[0]), int(coord[1])))

    # -----------------------------------------------------------------------

    def mark(self, image):
        """Evaluate landmark points on an image representing a face.

        :param image: (sppasImage or numpy.ndarray) The image to be processed.

        """
        if self.__recognizer is None:
            self.load_model()
        self.__landmarks = list()

        try:
            # Detect face (0.010 second)
            faces = self.__cascade.detectMultiScale(image, scaleFactor=1.05, minNeighbors=3, flags=0)
            # Apply the landmark (0.0030 second)
            ok, landmarks = self.__recognizer.fit(image, faces)

            # If a face has been detected
            if ok is True:
                # Store the landmark points
                coordinates = landmarks[0][0]
                self.__store_points(coordinates)

            # If any face has been detected
            else:
                # Store None
                self.__store_points(None)

        except cv2.error as e:
            self.__landmarks = list()
            raise sppasError("Landmark detection failed: {}".format(str(e)))

        size = len(self.__landmarks)
        if size != 68:
           self.__landmarks = list()
           raise sppasError("Normally, 68 landmark points should be detected. "
                            "Got {} instead.".format(size))

    # -----------------------------------------------------------------------

    def __landmark_points(self, image):
        """Determine points for tests if face module does not work.

        :param image: (numpy.ndarray) The image to be processed.

        """
        h, w = image.shape[:2]

        for i in range(10):
            x = int(3 * w / 4 * ((i + 1) / 10))
            y = int((h / 10) * 2)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3 * w / 4 * ((i + 1) / 10))
            y = int((h / 10) * 3)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3 * w / 4 * ((i + 1) / 10))
            y = int((h / 10) * 4)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3 * w / 4 * ((i + 1) / 10))
            y = int((h / 10) * 5)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3 * w / 4 * ((i + 1) / 10))
            y = int((h / 10) * 6)
            self.__landmarks.append((x, y))

        for i in range(10):
            x = int(3 * w / 4 * ((i + 1) / 10))
            y = int((h / 10) * 7)
            self.__landmarks.append((x, y))

        for i in range(8):
            x = int(3 * w / 4 * ((i + 1) / 10))
            y = int((h / 10) * 8)
            self.__landmarks.append((x, y))

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of x, y coordinates."""
        return len(self.__landmarks)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for i in range(0, self.__len__()):
            yield self.__landmarks[i]

    # ----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__landmarks[i]

    # ----------------------------------------------------------------------

    def __contains__(self, x_axis, y_axis):
        """Return true if value in self.__landmarks_x, self.__landmarks_y.

        :param x_axis: (int) The x-axis coordinate.
        :param y_axis: (int) The y-axis coordinate.

        """
        if isinstance(x_axis, int) is False:
            raise ValueError
        if isinstance(y_axis, int) is False:
            raise ValueError

        if self.__landmarks.__contains__((x_axis, y_axis)):
            return True
        return False

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
