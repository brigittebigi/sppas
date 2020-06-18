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

    Requires the "video" feature of SPPAS.

"""

import logging
import os
import numpy
import cv2

from sppas.src.config import paths
from sppas.src.exceptions import sppasTypeError, sppasIOError, sppasError
from sppas.src.exceptions import IntervalRangeException
from .coordinates import sppasCoords
from .image import sppasImage

# ---------------------------------------------------------------------------


class FaceDetection(object):
    """Detect faces in an image.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to analyze an image in order to detect faces. It
    stores a list of sppasCoords() for each detected face.

    This class uses a model in 300x300 because it's more accurate, for example
    with an HD image the deep learning neural network will automaticaly split
    the image and then analyze each part to obtain a better accuracy.

    :Example:

        >>> f = FaceDetection()
        >>> # Detect all the faces in an image
        >>> f.detect(sppasImage(filename="image path"))
        >>> # Get number of detected faces
        >>> len(f)
        >>> # Browse through the detected face coordinates:
        >>> for c in f:
        >>>     print(c)
        >>> # Get the detected object with the highest score
        >>> f.get_best()
        >>> # Get the 2 faces with the highest scores
        >>> f.get_best(2)
        >>> # Get detected faces with a confidence score greater than 0.9
        >>> f.get_confidence(0.9)

    """

    MIN_CONFIDENCE = 0.2
    MAX_CONFIDENCE = 1.

    # -----------------------------------------------------------------------

    def __init__(self):
        """Create a new FaceDetection instance.

        :raise: OSError if models are not loaded.

        """
        # The future serialized model, type: "cv2.dnn_Net"
        # it allows to create and manipulate comprehensive artificial neural networks.
        self.__net = cv2.dnn_Net
        self.load_model()

        # List of coordinates of detected faces, sorted by confidence score.
        self.__coords = list()

    # -----------------------------------------------------------------------

    def load_model(self, model=None, proto=None):
        """Initialize proto file and model file.

        :param model: (str) Filename of the caffe model.
        :param proto: (str) Filename of the proto describing the model
        :raise: IOError, Exception

        """
        if model is None:
            model = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000.caffemodel")
        if os.path.exists(model) is False:
            raise sppasIOError(model)

        if proto is None:
            proto = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000.prototxt")
        if os.path.exists(proto) is False:
            raise sppasIOError(proto)

        try:
            # Create and load the serialized model, type: "cv2.dnn_Net"
            self.__net = cv2.dnn.readNetFromCaffe(proto, model)
        except cv2.error as e:
            logging.error("Artificial Neural Network model or proto for "
                          "FaceDetection can't be read.")
            raise sppasError(str(e))

    # -----------------------------------------------------------------------

    def detect(self, image):
        """Determine the coordinates of all the detected faces.

        :param image: (sppasImage or numpy.ndarray)

        """
        # Invalidate current list of coordinates
        self.__coords = list()

        # Convert image to sppasImage if necessary
        if isinstance(image, numpy.ndarray) is True:
            image = sppasImage(input_array=image)
        if isinstance(image, sppasImage) is False:
            raise sppasTypeError("image", "sppasImage")

        # Extract the w, h of the image
        (h, w) = image.shape[:2]
        logging.debug("Image size is ({:d}, {:d})".format(w, h))

        # initialize the net and make predictions
        detections = self.__detections(image)

        # Loops over the detections and for each object in detection
        # get the confidence
        for i in range(detections.shape[2]):
            # Sets the confidence score of the current object
            confidence = detections[0, 0, i, 2]

            # Filter out weak detections by ensuring the `confidence` is
            # greater than a minimum empirically fixed confidence.
            if confidence > FaceDetection.MIN_CONFIDENCE:
                new_coords = self.__to_coords(detections, i, w, h, confidence)
                logging.debug("Face detected: {}".format(new_coords))
                self.__coords.append(new_coords)

    # -----------------------------------------------------------------------

    def to_portrait(self, image=None):
        """Scale coordinates of faces to a portrait size.

        The given image allows to ensure we wont scale larger than what the
        image can do.

        :param image: (sppasImage) The original image.
        :raise: ImageXXXError if scale or shift are not possible

        """
        portraits = [c.copy() for c in self.__coords]
        for c in portraits:
            # Scale the image. Shift values indicate how to shift x,y to get
            # the face exactly at the center of the new coordinates.
            shift_x, shift_y = c.scale(2.2, image)
            # Re-frame the image on the face.
            shift_y = int(float(shift_y) / 1.5)
            c.shift(shift_x, shift_y, image)

        # no error occurred, all faces can be converted to their portrait
        self.__coords = portraits

    # -----------------------------------------------------------------------

    def get_best(self, nb=1):
        """Return the coordinates with the n-best scores.

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

        :param confidence: (float) Minimum confidence score ranging [0.2, 1]
        :return: (list of sppasCoords or sppasCoords or None)

        """
        # No face was previously detected
        if len(self.__coords) == 0:
            return None

        # Verify given comparison score
        c = self.__to_dtype(confidence, dtype=float)
        if confidence < FaceDetection.MIN_CONFIDENCE or \
                confidence > FaceDetection.MAX_CONFIDENCE:
            raise IntervalRangeException(confidence, FaceDetection.MIN_CONFIDENCE, FaceDetection.MAX_CONFIDENCE)

        # return the list of sppasCoords with highest confidence
        return [coord.copy() for coord in self.__coords if coord.get_confidence() > c]

    # -----------------------------------------------------------------------

    def filter_best(self, nb=1):
        """Filter the coordinates to select only the n-best scores.

        If there are less coordinates than those requested, nothing is changed.

        :param nb: (int) number of coordinates to keep

        """
        # check nb value and select the n-best coordinates
        best = self.get_best(nb)
        if nb == 1:
            best = [best]
        # apply only if requested n-best is less than actual size
        if nb < len(self.__coords):
            self.__coords = best

    # -----------------------------------------------------------------------

    def filter_confidence(self, confidence=0.2):
        """Filter the coordinates to select only the n-best scores.

        If there are less coordinates than those requested, nothing is changed.

        :param confidence: (float) Minimum confidence score

        """
        # check confidence value and select the best coordinates
        best = self.get_confidence(confidence)
        # apply only if requested n-best is less than actual size
        if len(best) < len(self.__coords):
            self.__coords = best

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

        # Then creates a sppasCoords object with these values
        return sppasCoords(x, y, w, h, confidence)

    # -----------------------------------------------------------------------

    def __detections(self, image):
        """Initialize net and blob for the processing.

        :returns: detections.

        """
        # Load the image and construct an input blob for the image.
        # This blob corresponds to the defaults proto and model:
        # resize image to a fixed 300x300 pixels
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)),
            1.0, (300, 300), (104.0, 177.0, 123.0))

        # To detect faces, pass the blob through the net to analyze it
        self.__net.setInput(blob)

        # Runs forward pass to compute output of layer.
        # Then return the detections. They contain predictions about
        # what the image contains, type: "numpy.ndarray"
        return self.__net.forward()

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
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

