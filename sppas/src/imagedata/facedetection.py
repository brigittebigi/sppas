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
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A faceDetection object allows to analyze an image, detect visage in it
    and then returns a list of sppasCoordinates for each object you detected.

    This class uses a model in 300x300 because it's more accurate, for example
    with a HD image the deep learning neural network will automaticaly split
    the image and then analyze each part to obtain a better accuracy.

    For example:

    Create a FaceDetection object
    >>> f = FaceDetection(image)

    Detect all the objects in the image
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
        """Create a new FaceDetection instance.

        :param image: (numpy.ndarray) The image to be processed.

        """
        # The image to be processed.
        self.__image = image

        # The future serialized model, type: "cv2.dnn_Net"
        # it allows to create and manipulate comprehensive artificial neural networks.
        self.__net = cv2.dnn_Net

        # Represent the coordinates of objects from an image.
        self.__coordinates = list()

        self.__init_files()

    # -----------------------------------------------------------------------

    def __init_files(self):
        """Initialize proto file and model file."""
        try:
            # Load the model file from resources.video.
            # The Artificial Neural Network, it's composed of several artificial neurons.
            model = os.path.join(sppasPathSettings().resources, "video",
                                 "res10_300x300_ssd_iter_140000.caffemodel")

            # Load the prototxt file from resources.video.
            # The Caffe prototxt file, it's the solver of the model.
            proto = os.path.join(sppasPathSettings().resources, "video", "deploy.prototxt.txt")

            # Create and load the serialized model, type: "cv2.dnn_Net"
            self.__net = cv2.dnn.readNetFromCaffe(proto, model)
            raise OSError
        except OSError:
            return "File does not exist"

    # -----------------------------------------------------------------------

    def __init_process(self):
        """Initialize net and blob for the processing.

        :returns: The width, the height of an image and detections.

        """
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
        self.__net.setInput(blob)

        # Then create detections which contains predictions about
        # what the image contains, type: "numpy.ndarray"
        detections = self.__net.forward()
        return w, h, detections

    # -----------------------------------------------------------------------

    def detect_all(self):
        """Determine the coordinates of all the objects.

        :returns: A list of coordinates objects.

        """
        w, h, detections = self.__init_process()

        # Loops over the detections and for each object in detection
        # get the confidence
        for i in range(0, detections.shape[2]):
            # Sets the confidence score of the current object
            conf = detections[0, 0, i, 2]

            # Filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if conf > 0.2:
                self.__detect(detections, i, w, h, conf)

    # -----------------------------------------------------------------------

    def detect_confidence(self, confidence):
        """Determine the coordinates of all the objects with a score > confidence.

        :returns: A list of coordinates objects.

        """
        if isinstance(confidence, float) is False:
            raise ValueError
        w, h, detections = self.__init_process()

        # Loops over the detections and for each object in detection
        # get the confidence
        for i in range(0, detections.shape[2]):

            # Sets the confidence score of the current object
            conf = detections[0, 0, i, 2]

            # Filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if conf > confidence:
                self.__detect(detections, i, w, h, conf)

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
        # and for each object in detection get the confidence
        for i in range(0, number):
            # Sets the confidence score of the current object
            conf = detections[0, 0, i, 2]
            self.__detect(detections, i, w, h, conf)

    # -----------------------------------------------------------------------

    def __detect(self, detections, index, width, height, confidence):
        """Determine the coordinates of "number" objects.

        :returns: A list of coordinates objects.

        """
        # Determines the hitbox of the current object
        box = detections[0, 0, index, 3:7] * np.array([width, height, width, height])

        # Sets the values of the corners of the box
        (startX, startY, endX, endY) = box.astype("int")

        x, y, w, h = startX, startY, endX - startX, endY - startY

        # Then creates an Coordinates object with these values
        self.__coordinates.append(Coordinates(x, y, w, h, confidence))

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

    def get_nbest(self, number):
        """Return a list with the n best coordinates.

        :param number: (int) The number of faces to get.

        """
        number = int(number)
        if isinstance(number, int) is False:
            raise ValueError
        liste = list()
        for c in range(0, number):
            try:
                liste.append(self.__coordinates[c])
            except IndexError:
                pass
        return liste

    # -----------------------------------------------------------------------

    def get_image(self):
        """Return the image."""
        return self.__image

    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of coordinates."""
        return len(self.__coordinates)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for coordinates in self.__coordinates:
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

    # -----------------------------------------------------------------------

