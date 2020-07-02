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

    OpenCV’s facial landmark API is called Facemark. It has three different
    implementations of landmark detection based on three different papers:

        - FacemarkKazemi: This implementation is based on a paper titled
        "One Millisecond Face Alignment with an Ensemble of Regression Trees"
         by V.Kazemi and J. Sullivan published in CVPR 2014.
        - FacemarkAAM: This implementation uses an Active Appearance Model
        and is based on an the paper titled "Optimization problems for fast
        AAM fitting in-the-wild" by G. Tzimiropoulos and M. Pantic, published
        in ICCV 2013.
        - FacemarkLBF: This implementation is based a paper titled "Face
        alignment at 3000 fps via regressing local binary features" by
        S. Ren published in CVPR 2014.

"""

import logging
import cv2
import os
import numpy

from sppas.src.exceptions import sppasIOError, sppasError
from sppas.src.imgdata import sppasCoords
from ..FaceDetection.facedetection import FaceDetection

# ---------------------------------------------------------------------------


class FaceLandmark(object):
    """Estimate face landmarks on an image of a portrait.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is intentionally limited to mark only one face.
    It then expects an image cropped on the portrait of a person.

    """

    def __init__(self):
        """Create a new FaceLandmark instance."""
        # Coordinates of the 68 points detected on the face
        self.__landmarks = list()

        # The face detection
        self.__fd = FaceDetection()
        # The landmark recognizers
        self.__markers = list()
        # The expected number of points for the recognizers
        self.__nb_points = 68

    # -----------------------------------------------------------------------

    def load_model(self, model_landmark, model_fd, *args):
        """Initialize the face detection and recognizer from model files.

        :param model_landmark: (str) Filename of the recognizer model.
        :param model_fd: (str) A filename of a model for face detection
        :param *args: (str) Other filenames of models for face detection
        :raise: IOError, Exception

        """
        if os.path.exists(model_landmark) is False:
            raise sppasIOError(model_landmark)

        # Face landmark recognizer
        if model_landmark.endswith("yaml"):
            fm = cv2.face.createFacemarkLBF()
        elif model_landmark.endswith("xml"):
            fm = cv2.face.createFacemarkAAM()
        elif model_landmark.endswith("dat"):
            fm = cv2.face.createFacemarkKazemi()
        else:
            raise sppasIOError(model_landmark)
        fm.loadModel(model_landmark)
        self.__markers.append(fm)

        # Face detection
        self.__fd.load_model(model_fd, *args)

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

    def get_detected_face(self):
        """Return coordinates of the detected face, or None."""
        if len(self.__fd) > 0:
            return self.__fd.get_best()
        return None

    # -----------------------------------------------------------------------
    # Automatic detection of the landmark points
    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate current list of landmark coordinates."""
        self.__landmarks = list()

    # -----------------------------------------------------------------------

    def mark(self, image):
        """Evaluate landmark points on an image representing a face.

        :param image: (sppasImage or numpy.ndarray) The image to be processed.

        """
        self.__landmarks = list()
        if len(self.__markers) == 0:
            raise sppasError("At least a model must be loaded first.")

        self.__fd.detect(image)
        if len(self.__fd) == 0:
            raise sppasError("No face detected in the image.")
        if len(self.__fd) > 1:
            logging.warning("Only one face was expected in the image but {} "
                            "were found. Only the best one will be considered."
                            "".format(len(self.__fd)))
        coords = self.__fd.get_best()
        shift_x, shift_y = coords.scale(1.)
        coords.shift(shift_x, shift_y)

        rects = numpy.array([[coords.x, coords.y, coords.w, coords.h]], dtype=numpy.int32)
        # Estimate all the 68 points detected by each instantiated face-marker
        all_points = {i:list() for i in range(self.__nb_points)}

        for face_marker in self.__markers:
            try:
                # Detect facial landmarks from the image with the face-marker
                marked, landmarks = face_marker.fit(image, rects)
                points = landmarks[0][0]
                if marked is True:
                    if len(points) != self.__nb_points:
                        raise sppasError(
                            "Normally, {} landmark points should be detected. "
                            "Got {} instead.".format(self.__nb_points, len(points)))
                    for i in range(self.__nb_points):
                        all_points[i].append(points[i])
            except cv2.error as e:
                logging.error("Landmark detection failed: {}".format(str(e)))

        # If all points of the face have been detected...
        if len(all_points) == 0:
            raise sppasError("No landmarks detected in the image.")

        # Add the empirically fixed points, to smooth...
        empirical = self.__landmark_points(image, coords)
        for i, c in enumerate(empirical):
            all_points[i].append((c.x, c.y))

        # Interpolate all the points and store into our landmarks
        for i in range(self.__nb_points):
            sum_x = sum(result[0] for result in all_points[i])
            sum_y = sum(result[1] for result in all_points[i])
            x = sum_x // len(all_points[i])
            y = sum_y // len(all_points[i])
            self.__landmarks.append(sppasCoords(x, y))

    # -----------------------------------------------------------------------

    def __landmark_points(self, image, coords):
        """Empirically fixed points.

        :param image: (numpy.ndarray) The image to be processed.

        """
        img = image.icrop(coords)
        h, w = img.shape[:2]

        sx = w // 20
        sy = h // 20
        x = w // 2
        y = h // 2

        # All points where estimated supposing that w = 0.8*h
        points = list()
        points.append(sppasCoords(1, y - sy))            # 1
        points.append(sppasCoords(sx // 3, y + sy))      # 2
        points.append(sppasCoords(sx // 2, y + (3*sy)))  # 3
        points.append(sppasCoords(sx, y + (5*sy)))       # 4
        points.append(sppasCoords(2*sx, y + (7*sy)))     # 5
        points.append(sppasCoords(4*sx, y + (9*sy)))     # 6
        points.append(sppasCoords(6*sx, h))              # 7
        points.append(sppasCoords(8*sx, h + (sy//2)))    # 8  --> y-outside
        points.append(sppasCoords(x, h + sy))            # 9  --> x-middle ; y-outside
        points.append(sppasCoords(x + (2*sx), h + (sy//2)))    # 10  --> y-outside
        points.append(sppasCoords(x + (4*sx), h))              # 11
        points.append(sppasCoords(x + (6*sx), y + (9*sy)))     # 12
        points.append(sppasCoords(x + (8*sx), y + (7*sy)))     # 13
        points.append(sppasCoords(w - sx, y + (5*sy)))         # 14
        points.append(sppasCoords(w - (sx // 2), y + (3*sy)))  # 15
        points.append(sppasCoords(w - (sx // 3), y + sy))      # 16
        points.append(sppasCoords(w - 1, y - sy))              # 17

        points.append(sppasCoords(2*sx, 7*sy))                               # 18
        points.append(sppasCoords((3*sx) + (sx//2), (6*sy) + (sy//2)))       # 19
        points.append(sppasCoords(5*sx, 6*sy))                               # 20
        points.append(sppasCoords((6*sx) + (sx//2), (6*sy) + (sy//2)))       # 21
        points.append(sppasCoords(8*sx, 7*sy))                               # 22
        points.append(sppasCoords(x + 2*sx, 7*sy))                           # 23
        points.append(sppasCoords(x + (3*sx) + (sx//2), (6*sy) + (sy//2)))   # 24
        points.append(sppasCoords(x + 5*sx, 6*sy))                           # 25
        points.append(sppasCoords(x + (6*sx) + (sx//2), (6*sy) + (sy//2)))   # 26
        points.append(sppasCoords(x + (8*sx), 7*sy))                         # 27

        # nose
        points.append(sppasCoords(x, y - (2*sy)))                      # 28
        points.append(sppasCoords(x, y - sy))                          # 29
        points.append(sppasCoords(x, y))                          # 30
        points.append(sppasCoords(x, y + sy))                      # 31
        points.append(sppasCoords(x - (3*sx), y + (3*sy) - (sy//2)))   # 32
        points.append(sppasCoords(x - (2*sx), y + (3*sy) - (sy//3)))   # 33
        points.append(sppasCoords(x, y + (3*sy)))                      # 34
        points.append(sppasCoords(x + (2*sx), y + (3*sy) - (sy//3)))   # 35
        points.append(sppasCoords(x + (3*sx), y + (3*sy) - (sy//2)))   # 36

        # eyes
        points.append(sppasCoords(x - (6*sx), 8*sy + (sy//2)))   # 37
        points.append(sppasCoords(x - (5*sx) - (sx//4), 8*sy))   # 38
        points.append(sppasCoords(x - (4*sx), 8*sy))   # 39
        points.append(sppasCoords(x - (3*sx), 8*sy + (sy//2)))   # 40
        points.append(sppasCoords(x - (4*sx), 9*sy))   # 41
        points.append(sppasCoords(x - (5*sx), 9*sy))   # 42
        points.append(sppasCoords(x + (3*sx), 8*sy + (sy//2)))   # 43
        points.append(sppasCoords(x + (4*sx), 8*sy))   # 44
        points.append(sppasCoords(x + (5*sx), 8*sy))   # 45
        points.append(sppasCoords(x + (6*sx), 8*sy + (sy//2)))   # 46
        points.append(sppasCoords(x + (5*sx), 9*sy))   # 47
        points.append(sppasCoords(x + (4*sx), 9*sy))   # 48

        # mouth
        points.append(sppasCoords(x - (4*sx), y + (5*sy) + (sy//2)))   # 49
        points.append(sppasCoords(x - (2*sx) - (sx//2), y + (5*sy)))   # 50
        points.append(sppasCoords(x - sx, y + (5*sy) - (sy//3)))       # 51
        points.append(sppasCoords(x, y + (5*sy) - (sy//4)))            # 52
        points.append(sppasCoords(x + sx, y + (5*sy) - (sy//3)))       # 53
        points.append(sppasCoords(x + (2*sx) + (sx//2), y + (5*sy)))   # 54
        points.append(sppasCoords(x + (4*sx), y + (5*sy) + (sy//2)))   # 55
        points.append(sppasCoords(x + (2*sx) + (sx//2), y + (6*sy) + (sy//4)))  # 56
        points.append(sppasCoords(x + sx, y + (7*sy) - (sy//4)))                # 57
        points.append(sppasCoords(x, y + (7*sy)))                               # 58
        points.append(sppasCoords(x - sx, y + (7*sy) - (sy//4)))                # 59
        points.append(sppasCoords(x - (2*sx) - (sx//2), y + (6*sy) + (sy//4)))  # 60
        points.append(sppasCoords(x - (2*sx) - (sx//2), y + (5*sy) + (sy//2)))  # 61
        points.append(sppasCoords(x - sx, y + (5*sy) + (sy//4)))                # 62
        points.append(sppasCoords(x, y + (5*sy) + (sy//2)))                     # 63
        points.append(sppasCoords(x + sx, y + (5*sy) + (sy//4)))                # 64
        points.append(sppasCoords(x + (2*sx) + (sx//2), y + (5*sy) + (sy//2)))  # 65
        points.append(sppasCoords(x + sx, y + (6*sy)))                          # 66
        points.append(sppasCoords(x, y + (6*sy) + (sy//4)))                     # 67
        points.append(sppasCoords(x - sx, y + (6*sy)))                          # 68

        for p in points:
            p.x += coords.x
            p.y += coords.y

        return points

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
