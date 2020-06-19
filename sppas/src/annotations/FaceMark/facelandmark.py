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
import numpy

from sppas.src.config import paths
from sppas.src.exceptions import sppasIOError, sppasError
from sppas.src.imgdata import sppasCoords
from ..FaceDetection.facedetection import FaceDetection

# ---------------------------------------------------------------------------


class FaceLandmark(object):
    """Estimate face landmarks on an image of a face or a portrait.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is intentionally limited to mark only one face.
    It then expects an image cropped on the face or the portrait of a person.

    """

    def __init__(self):
        """Create a new FaceLandmark instance."""
        # Coordinates of the 68 points detected on the face
        self.__landmarks = list()

        # The face detection
        self.__fd = FaceDetection()
        # The landmark recognizer
        self.__recognizer = None
        # The expected number of points for this model
        self.__nb_points = 68

    # -----------------------------------------------------------------------

    def load_model(self, model_landmark, model_face):
        """Initialize proto file and model file.

        :param model_landmark: (str) Filename of the recognizer model.
        :param model_face: (str) Filename of the model for face detection
        :raise: IOError, Exception

        """
        # Use the given model and haar cascade
        if os.path.exists(model_landmark) is False:
            raise sppasIOError(model_landmark)
        if os.path.exists(model_face) is False:
            raise sppasIOError(model_face)

        self.__fd.load_model(model_face)
        self.__recognizer = cv2.face.createFacemarkLBF()
        self.__recognizer.loadModel(model_landmark)

    # -----------------------------------------------------------------------
    # Getters of specific points
    # -----------------------------------------------------------------------

    def get_left_face(self):
        """Return coordinates of the left side of the face.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [1-9].

        """
        if len(self.__landmarks) == 68:
            return self.__landmarks[:9]
        return list()

    # -----------------------------------------------------------------------

    def get_right_face(self):
        """Return coordinates of the right side of the face.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [10-16].

        """
        if len(self.__landmarks) == 68:
            return self.__landmarks[9:16]
        return list()

    # -----------------------------------------------------------------------

    def get_left_brow(self):
        """Return coordinates of the left brow.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [18-22].

        """
        if len(self.__landmarks) == 68:
            return self.__landmarks[17:22]
        return list()

    # -----------------------------------------------------------------------

    def get_right_brow(self):
        """Return coordinates of the right brow.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [23-27].

        """
        if len(self.__landmarks) == 68:
            return self.__landmarks[22:27]
        return list()

    # -----------------------------------------------------------------------

    def get_nose(self):
        """Return coordinates of the nose.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [28-36].

        """
        if len(self.__landmarks) == 68:
            return self.__landmarks[27:36]
        return list()

    # -----------------------------------------------------------------------

    def get_left_eyes(self):
        """Return coordinates of the left eye.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [37-42].

        """
        if len(self.__landmarks) == 68:
            return self.__landmarks[36:42]
        return list()

    # -----------------------------------------------------------------------

    def get_right_eyes(self):
        """Return coordinates of the right eye.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [43-48].

        """
        if len(self.__landmarks) == 68:
            return self.__landmarks[42-48]
        return list()

    # -----------------------------------------------------------------------

    def get_mouth(self):
        """Return coordinates of the mouth.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [49-68].

        """
        if len(self.__landmarks) == 68:
            return self.__landmarks[48:]
        return list()

    # -----------------------------------------------------------------------
    # Automatic detection of the landmark points
    # -----------------------------------------------------------------------

    def mark(self, image):
        """Evaluate landmark points on an image representing a face.

        :param image: (sppasImage or numpy.ndarray) The image to be processed.

        """
        self.__landmarks = list()
        if self.__recognizer is None:
            raise sppasError("A model must be loaded first.")

        self.__fd.detect(image)
        if len(self.__fd) == 0:
            raise sppasError("No face detected in the image.")
        if len(self.__fd) > 1:
            logging.warning("Only one face was expected in the image but {}"
                            "were found. Only the first one will be considered."
                            "".format(len(self.__fd)))
        coords = self.__fd.get_best()
        rects = numpy.array([[coords.x, coords.y, coords.w, coords.h]], dtype=numpy.int32)
        try:
            # Detect facial landmarks from an image
            success, landmarks = self.__recognizer.fit(image, rects)
        except cv2.error as e:
            self.__landmarks = list()
            raise sppasError("Landmark detection failed: {}".format(str(e)))

        # If a face has been detected, and only one
        if success is True:
            # Store the landmark points
            points = landmarks[0][0]
            if len(points) != self.__nb_points:
                raise sppasError(
                    "Normally, {} landmark points should be detected. "
                    "Got {} instead.".format(self.__nb_points, len(points)))

            for (x, y) in points:
                self.__landmarks.append(sppasCoords(x, y))
        else:
            raise sppasError("No landmaks detected in the image.")

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of landmarks."""
        return len(self.__landmarks)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for i in range(len(self.__landmarks)):
            yield self.__landmarks[i]

    # ----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__landmarks[i]

    # ----------------------------------------------------------------------

    def __contains__(self, other):
        """Return true if value in landmark points.

        :param other: a list/tuple of (x,y,...) or a sppasCoords

        """
        if isinstance(other, (list, tuple)) is True:
            if len(other) > 1:
                other = sppasCoords(other[0], other[1])
            else:
                return False

        return other in self.__landmarks

    # -----------------------------------------------------------------------

    def __str__(self):
        """Return coords separated by CR."""
        return "\n".join([str(coords) for coords in self.__landmarks])

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)
