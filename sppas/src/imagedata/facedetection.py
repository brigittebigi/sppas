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

    src.imagedata.facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import numpy as np
import cv2

from sppas.src.config import sppasPathSettings
from sppas.src.imagedata.coordinates import Coordinates


# ---------------------------------------------------------------------------


class FaceDetection(object):
    """Class to detect faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    A faceDetection object allows to analyze an image, detect visage in it
    and then returns a list of sppasCoordinates for each object you detected.

    For example :

    Create a FaceDetection object
    >>> f = FaceDetection(image)

    Detect all the objects in image
    >>> f.detect_all()

    Detect all the objects with a score > 0.2 in the image
    >>> f.detect_confidence(0.2)

    Detect 2 objects in the image
    >>> f.detect_number(2)

    Get all the detected objects
    >>> f.get_all()

    Get the detected object with the highest score
    >>> f.get_best()

    Get the 2 objects with the highest score
    >>> f.get_number(2)

    """

    def __init__(self, image):
        """Create a new faceDetection instance.

        :param image: (numpy.ndarray) The image to be processed.

        """
        # The image to be processed.
        self.__image = image

        # The Artificial Neural Network, it's composed of several
        # artificial neurons.
        self.__model = None

        # The Caffe prototxt file, it's the solver of the model.
        self.__proto = None

        # Represent the coordinates of objects from an image.
        self.__coordinates = list()

        self.__init_files()

    # -----------------------------------------------------------------------

    def __init_files(self):
        """Initialize proto file and model file."""
        try:
            # Load the prototxt file from resources.video.
            self.__proto = os.path.join(sppasPathSettings().resources, "video", "deploy.prototxt.txt")
            # Load the model file from resources.video.
            self.__model = os.path.join(sppasPathSettings().resources, "video",
                                        "res10_300x300_ssd_iter_140000.caffemodel")
            raise OSError
        except OSError:
            return "File does not exist"

    # -----------------------------------------------------------------------

    def __init_process(self):
        """Initialize net and blob for the processing.

        :returns: The width, the height of an image and detections.

        """
        # Create and load the serialized model, type: "cv2.dnn_Net"
        net = cv2.dnn.readNetFromCaffe(self.__proto, self.__model)

        # Extract the dimensions of self.__image which are
        # the width and the height of self.__image
        (h, w) = self.__image.shape[:2]

        # Load self.__image and construct an input blob for the image
        # by resizing to a fixed 300x300 pixels and then normalizing
        # it type: "numpy.ndarray"
        blob = cv2.dnn.blobFromImage(cv2.resize(self.__image, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))

        # To detect faces, pass the blob throught the net
        # which will analyze it
        net.setInput(blob)

        # Then create detections which contains predictions about
        # what the image contains, type: "numpy.ndarray"
        detections = net.forward()
        return w, h, detections

    # -----------------------------------------------------------------------

    def detect_all(self):
        """Determine the coordinates of all the objects.

        :returns: A list of coordinates objects.

        """
        w, h, detections = self.__init_process()

        # Loops over the detections
        for i in range(0, 10):

            # Sets the confidence score of the current object
            conf = detections[0, 0, i, 2]

            # Determines the hitbox of the current object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

            # Sets the values of the corners of the box
            (startX, startY, endX, endY) = box.astype("int")

            # Then creates an Coordinates object with these values
            self.__coordinates.append(Coordinates(startX, startY, endX - startX, endY - startY, conf))

    # -----------------------------------------------------------------------

    def detect_confidence(self, confidence):
        """Determine the coordinates of all the objects with a score > confidence.

        :returns: A list of coordinates objects.

        """
        if isinstance(confidence, float) is False:
            raise ValueError
        w, h, detections = self.__init_process()

        # Loops over the detections
        for i in range(0, detections.shape[2]):

            # Sets the confidence score of the current object
            conf = detections[0, 0, i, 2]

            # Filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if conf > confidence:

                # Determines the hitbox of the current object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

                # Sets the values of the corners of the box
                (startX, startY, endX, endY) = box.astype("int")

                # Then creates an Coordinates object with these values
                self.__coordinates.append(Coordinates(startX, startY, endX - startX, endY - startY, conf))

    # -----------------------------------------------------------------------

    def detect_number(self, number):
        """Determine the coordinates of "number" objects.

        :returns: A list of coordinates objects.

        """
        number = int(number)
        if isinstance(number, int) is False:
            raise ValueError
        w, h, detections = self.__init_process()

        # Loops over the detections a certain "number" of times
        for i in range(0, number):

            # Sets the confidence score of the current object
            conf = detections[0, 0, i, 2]

            # Determines the hitbox of the current object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

            # Sets the values of the corners of the box
            (startX, startY, endX, endY) = box.astype("int")

            # Then creates an Coordinates object with these values
            self.__coordinates.append(Coordinates(startX, startY, endX - startX, endY - startY, conf))

    # -----------------------------------------------------------------------

    def get_all(self):
        """Return a list of coordinates objects."""
        return self.__coordinates

    # -----------------------------------------------------------------------

    def get_best(self):
        """Return the coordinate object with the best score."""
        best = None
        best_score = float()
        for c in self.__coordinates:
            if c.get_confidence() > best_score:
                best_score = c.get_confidence()
                best = c
        return best

    # -----------------------------------------------------------------------

    def get_number(self, number):
        """Return a list with the "number" first coordinates."""
        number = int(number)
        if isinstance(number, int) is False:
            raise ValueError
        liste = list()
        for c in range(0, number):
            liste.append(self.__coordinates[c])
        return liste

    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of coordinates."""
        return len(self.__coordinates)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for coordinates in list(self.__coordinates):
            yield coordinates

    # ----------------------------------------------------------------------

    def __contains__(self, value):
        """Return true if value in self.__coordinates."""
        if isinstance(value, Coordinates) is False:
            raise ValueError
        else:
            for c in self.__coordinates:
                if c.__eq__(value):
                    return True
        return False

    # -----------------------------------------------------------------------

    def __str__(self):
        for c in self.__coordinates:
            print(c.__str__())

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

