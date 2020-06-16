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

    src.imgdata.facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import numpy
import cv2

from sppas.src.config import paths
from sppas.src.exceptions import sppasTypeError
from .coordinates import sppasCoords
from .image import sppasImage

# ---------------------------------------------------------------------------


class FaceDetection(object):
    """Class to detect faces.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A faceDetection instance allows to analyze an image in order to detect
    faces. It estimates a list of sppasCoordinates for each detected face.

    This class uses a model in 300x300 because it's more accurate, for example
    with an HD image the deep learning neural network will automaticaly split
    the image and then analyze each part to obtain a better accuracy.

    :Example:

        >>> f = FaceDetection(image)
        >>> # Detect all the faces in the image
        >>> f.detect()
        >>> # Get all the detected objects
        >>> f.get_all()
        >>> # Get the detected object with the highest score
        >>> f.get_best()
        >>> # Get the 2 faces with the highest scores
        >>> f.get_number(2)

    """

    def __init__(self):
        """Create a new FaceDetection instance.

        :raise: OSError if models are not loaded.

        """
        # The future serialized model, type: "cv2.dnn_Net"
        # it allows to create and manipulate comprehensive artificial neural networks.
        self.__net = cv2.dnn_Net
        self.load_resources()

        # List of coordinates of detected faces
        self.__coords = list()

    # -----------------------------------------------------------------------

    def load_resources(self):
        """Initialize proto file and model file."""
        try:
            # Load the Artificial Neural Network model
            model = os.path.join(paths.resources, "video",
                                 "res10_300x300_ssd_iter_140000.caffemodel")

            # Load the Caffe prototxt file
            proto = os.path.join(paths.resources, "video", "deploy.prototxt.txt")

            # Create and load the serialized model, type: "cv2.dnn_Net"
            self.__net = cv2.dnn.readNetFromCaffe(proto, model)
            raise OSError
        except OSError:
            return "File does not exist"

    # -----------------------------------------------------------------------

    def detect(self, image):
        """Determine the coordinates of all the detected faces.

        :param image: (sppasImage or numpy.ndarray)

        """
        # Convert image to sppasImage if necessary
        if isinstance(image, numpy.ndarray) is True:
            image = sppasImage(input_array=image)
        if isinstance(image, sppasImage) is False:
            raise sppasTypeError("image", "sppasImage")

        # Extract the w, h of the image
        (h, w) = image.shape[:2]

        # initialize the net and make predictions
        detections = self.__detections(image)

        # Loops over the detections and for each object in detection
        # get the confidence
        for i in range(0, detections.shape[2]):
            # Sets the confidence score of the current object
            confidence = detections[0, 0, i, 2]

            # Filter out weak detections by ensuring the `confidence` is
            # greater than a minimum empirically fixed confidence.
            if confidence > 0.2:
                self.__to_coords(detections, i, w, h, confidence)

    # -----------------------------------------------------------------------

    def get_best(self, nb=1):
        """Return the coordinate object with the n-best scores.

        :param nb: (int) number of coordinates to return
        :return: (list of sppasCoords or sppasCoords or None)

        """
        # No face was previously detected
        if len(self.__coords) == 0:
            return None

        # Only the best face is requested.
        nb = self.__to_dtype(nb)
        if nb == 1:
            return self.__coords[0]

        # Make a copy of the detected coords and select n-best
        nbest = [c.copy() for c in self.__coords[:nb]]

        # More faces are requested than those detected
        if nb > len(nbest):
            nbest.extend([None]*(nb-len(nbest)))

        return nbest

    # -----------------------------------------------------------------------

    def get_confidence(self, confidence=0.2):
        """Return the coordinate object with the better scores.

        :param confidence: (float) Minimum confidence score
        :return: (list of sppasCoords or sppasCoords or None)

        """
        # No face was previously detected
        if len(self.__coords) == 0:
            return None
        c = self.__to_dtype(confidence, dtype=float)

        return [coord.copy() for coord in self.__coords if coord.get_confidence() > c]

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __to_dtype(self, value, dtype=int):
        """Convert a value to int or raise the appropriate exception."""
        try:
            value = dtype(value)
            if isinstance(value, dtype) is False:
                raise sppasTypeError(value, str(dtype))
        except ValueError:
            raise sppasTypeError(value, str(dtype))

        return value

    # -----------------------------------------------------------------------

    def __to_coords(self, detections, index, width, height, confidence):
        """Determine the coordinates of "number" objects.

        :returns: A list of coordinates objects.

        """
        # Determines the hitbox of the current object
        box = detections[0, 0, index, 3:7] * numpy.array([width, height, width, height])

        # Sets the values of the corners of the box
        (startX, startY, endX, endY) = box.astype("int")

        x, y, w, h = startX, startY, endX - startX, endY - startY

        # Then creates an sppasCoords object with these values
        self.__coords.append(sppasCoords(x, y, w, h, confidence))

    # -----------------------------------------------------------------------

    def __detections(self, image):
        """Initialize net and blob for the processing.

        :returns: The width, the height of an image and detections.

        """
        # Load the image and construct an input blob for the image
        # by resizing to a fixed 300x300 pixels and then normalizing
        # its type: "numpy.ndarray"
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)),
            1.0, (300, 300), (104.0, 177.0, 123.0))

        # To detect faces, pass the blob through the net to analyze it
        self.__net.setInput(blob)

        # Then return the detections. They contain predictions about
        # what the image contains, type: "numpy.ndarray"
        return self.__net.forward()

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of coordinates."""
        return len(self.__coords)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for coordinates in self.__coords:
            yield coordinates

    # ----------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__coords[i]

    # ----------------------------------------------------------------------

    def __contains__(self, value):
        """Return true if value in self.__coordinates."""
        for c in self.__coords:
            if c == value:
                return True
        return False

    # -----------------------------------------------------------------------

    def __str__(self):
        for c in self.__coords:
            print(c.__str__())

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

