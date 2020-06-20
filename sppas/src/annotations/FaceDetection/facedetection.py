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

    src.annotations.FaceDetection.facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires the "video" feature of SPPAS.
    Automatic face detection, based on opencv.

"""

import logging
import os
import numpy
import cv2

from sppas.src.exceptions import sppasTypeError, sppasIOError, sppasError
from sppas.src.exceptions import IntervalRangeException
from sppas.src.exceptions import IOExtensionError
from sppas.src.imgdata.coordinates import sppasCoords
from sppas.src.imgdata.image import sppasImage

# ---------------------------------------------------------------------------


class BaseObjectsDetector(object):
    """Detect objects in an image.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to analyze an image in order to detect objects. It
    stores a list of sppasCoords() for each detected object. The detected
    object corresponds to the one of the trained model (human face, human
    profile, cat face, car...).

    :Example:

        >>> f = BaseObjectsDetector()
        >>> f.load_model(model_filename)
        >>> # Detect all the objects in an image
        >>> f.detect(sppasImage(filename="image path"))
        >>> # Get number of detected objects
        >>> len(f)
        >>> # Browse through the detected object coordinates:
        >>> for c in f:
        >>>     print(c)

    """

    DEFAULT_MIN_RATIO = 0.05
    DEFAULT_MIN_SCORE = 0.2
    DEFAULT_MAX_SCORE = 1.0

    # -----------------------------------------------------------------------

    def __init__(self):
        """Create a new detector instance."""
        # The future serialized model
        self._detector = None
        self._extension = ""

        # List of coordinates of detected objects, sorted by confidence score.
        self._coords = list()

        # Minimum ratio of an object compared to the image
        self.__min_ratio = BaseObjectsDetector.DEFAULT_MIN_RATIO

        # Minimum confidence score of a detected object
        # It is suppose that the confidence scores of detected object is
        # ranging [0., 1.]
        self.__min_score = BaseObjectsDetector.DEFAULT_MIN_SCORE

    # -----------------------------------------------------------------------

    def get_extension(self):
        """Return the expected extension of the model filename."""
        return self._extension

    # -----------------------------------------------------------------------

    def get_min_ratio(self):
        """Return the minimum ratio of an object compared to the image."""
        return self.__min_ratio

    # -----------------------------------------------------------------------

    def set_min_ratio(self, value):
        """Set the minimum ratio of an object compared to the image.

        It means that width and height of a detected object must be at
        least 'value' percent of the image width and height respectively

        :param value: (float) Value ranging [0., 1.]
        :raise: ValueError

        """
        value = BaseObjectsDetector.to_dtype(value, dtype=float)
        if value < 0. or value > 1.:
            raise IntervalRangeException(value, 0., 1.)
        self.__min_ratio = value

    # -----------------------------------------------------------------------

    def get_min_score(self):
        """Return the minimum score of a detected object to consider it."""
        return self.__min_score

    # -----------------------------------------------------------------------

    def set_min_score(self, value):
        """Set the minimum score of a detected object to consider it.

        It means that any detected object with a score lesser than the given
        one will be ignored. The score of detected objects are supposed to
        range between 0. and 1.

        :param value: (float) Value ranging [0., 1.]
        :raise: ValueError

        """
        value = BaseObjectsDetector.to_dtype(value, dtype=float)
        if value < 0. or value > BaseObjectsDetector.DEFAULT_MAX_SCORE:
            raise IntervalRangeException(value, 0., BaseObjectsDetector.DEFAULT_MAX_SCORE)
        self.__min_score = value

    # -----------------------------------------------------------------------

    def load_model(self, model, *args):
        """Load at least a model.

        :param model: Filename of the model (DNN, HaarCascade, ...)
        :raise: OSError if model is not loaded.

        """
        if model.endswith(self._extension) is False:
            raise IOExtensionError(model)

        if os.path.exists(model) is False:
            raise sppasIOError(model)

        # Create and load the model
        self._set_detector(model)

    # -----------------------------------------------------------------------

    def detect(self, image):
        """Determine the coordinates of all the detected objects.

        :param image: (sppasImage or numpy.ndarray)

        """
        # Invalidate current list of coordinates
        self.invalidate()

        # Convert image to sppasImage if necessary
        if isinstance(image, numpy.ndarray) is True:
            image = sppasImage(input_array=image)
        if isinstance(image, sppasImage) is False:
            raise sppasTypeError("image", "sppasImage")

        # Verify if a model is instantiated
        if self._detector is None:
            raise sppasError("A model must be loaded first")

        self._detection(image)

    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate current list of detected objects."""
        self._coords = list()

    # -----------------------------------------------------------------------

    def get_best(self, nb=1):
        """Return a copy of the coordinates with the n-best scores.

        :param nb: (int) number of coordinates to return
        :return: (list of sppasCoords or sppasCoords or None)

        """
        # No face was previously detected
        if len(self._coords) == 0:
            return None

        # Only the best face is requested.
        nb = BaseObjectsDetector.to_dtype(nb)
        if nb == 1:
            return self._coords[0]

        # Make a copy of the detected coords and select n-best
        nbest = [c.copy() for c in self._coords[:nb]]

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
        if len(self._coords) == 0:
            return None

        # Verify given comparison score
        score = BaseObjectsDetector.to_dtype(confidence, dtype=float)

        # return the list of sppasCoords with highest confidence
        return [c.copy() for c in self._coords if c.get_confidence() > score]

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
        if nb < len(self._coords):
            self._coords = best

    # -----------------------------------------------------------------------

    def filter_confidence(self, confidence=0.2):
        """Filter the coordinates to select only the n-best scores.

        If there are less coordinates than those requested, nothing is changed.

        :param confidence: (float) Minimum confidence score

        """
        # check confidence value and select the best coordinates
        best = self.get_confidence(confidence)
        # apply only if requested n-best is less than actual size
        if len(best) < len(self._coords):
            self._coords = best

    # -----------------------------------------------------------------------

    @staticmethod
    def to_dtype(value, dtype=int):
        """Convert a value to dtype or raise the appropriate exception.

        """
        try:
            value = dtype(value)
            if isinstance(value, dtype) is False:
                raise sppasTypeError(value, str(dtype))
        except ValueError:
            raise sppasTypeError(value, str(dtype))

        return value

    # -----------------------------------------------------------------------
    # Methods to be overridden to create an object detector
    # -----------------------------------------------------------------------

    def _set_detector(self, model):
        """Really load the model and instantiate the detector.

        To be overridden.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _detection(self, image):
        """Really determine the coordinates of the detected objects.

        To be overridden.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._coords)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for coordinates in self._coords:
            yield coordinates

    # ----------------------------------------------------------------------

    def __getitem__(self, i):
        return self._coords[i]

    # ----------------------------------------------------------------------

    def __contains__(self, value):
        """Return true if value in self.__coordinates."""
        for c in self._coords:
            if c == value:
                return True
        return False

    # -----------------------------------------------------------------------

    def __str__(self):
        return "\n".join([str(c) for c in self._coords])

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

# ---------------------------------------------------------------------------
# OpenCV HaarCascadeClassifier for objects detection
# ---------------------------------------------------------------------------


class HaarCascadeDetector(BaseObjectsDetector):
    """Detect objects in an image with Haar Cascade Classifier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """
    def __init__(self):
        super(HaarCascadeDetector, self).__init__()
        self._extension = ".xml"

    # -----------------------------------------------------------------------

    def _set_detector(self, model):
        """Initialize the detector with the given file.

        :param model: (str) Filename of the XML Haar Cascade file
        :raises: Exception

        """
        try:
            self._detector = cv2.CascadeClassifier(model)
        except cv2.error as e:
            logging.error("Loading the XML Haar Cascade model failed.")
            raise sppasError(str(e))

    # -----------------------------------------------------------------------

    def _detection(self, image):
        """Really determine the coordinates of the detected objects.

        :param image: (sppasImage or numpy.ndarray)

        """
        # make predictions
        detections = self.__haar_detections(image)

        # Convert detections into a list of sppasCoords

        # Detection weights normalization into confidence scores
        # TODO: weight normalization into confidence scores
        scores = list()
        for weight in detections[2]:
            if weight < 0.:
                weight = 0.
            weight = weight / 200.
            scores.append(weight)

        # convert the detected positions into a list of sppasCoords
        detected_objects = list()
        for rect, score in zip(detections[0], scores):
            coords = sppasCoords(rect[0], rect[1], rect[2], rect[3])
            # Enable the condition as soon as weight are normalized into scores
            # if score > self.get_min_score():
            detected_objects.append((coords, score))

        # sort by confidence score (the highest the better)
        for coords, score in reversed(sorted(detected_objects, key=lambda x: x[1])):
            coords.set_confidence(score)
            self._coords.append(coords)

    # -----------------------------------------------------------------------

    def __haar_detections(self, image):
        """Detect faces using the Haar Cascade classifier.

        This classifier already delete overlapped detections and too small
        detected faces.
        Return detections has a tuple with 3 values:
            - a list of N-list of rectangles
            - a list of N time the value 20 (???)
            - a list of N weight values

        :return: (numpy arrays)

        """
        # Ignore too small detections, ie less than 5% of the image size
        w, h = image.size()
        min_w = int(float(w) * self.get_min_ratio())
        min_h = int(float(h) * self.get_min_ratio())
        try:
            detections = self._detector.detectMultiScale3(
                image,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(min_w, min_h),
                flags=0,
                outputRejectLevels=True  # cv2.error if set to False
            )

        except cv2.error as e:
            self._coords = list()
            raise sppasError("HaarCascadeClassifier detection failed: {}"
                             "".format(str(e)))

        return detections

# ---------------------------------------------------------------------------
# OpenCV Artifical Neural Networks for objects detection
# ---------------------------------------------------------------------------


class NetDetector(BaseObjectsDetector):
    """Detect objects in an image with Artificial Neural Networks.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        super(NetDetector, self).__init__()
        self._extension = ".caffemodel"

    # -----------------------------------------------------------------------

    def _set_detector(self, model):
        """Initialize the model with the given file.

        :param model: (str) Filename of the Caffe model file
        :raise: IOError, Exception

        """
        fn, fe = os.path.splitext(model)
        proto = fn + ".prototxt"
        if os.path.exists(proto) is False:
            raise sppasIOError(proto)

        try:
            self._detector = cv2.dnn.readNetFromCaffe(proto, model)
        except cv2.error as e:
            logging.error("Artificial Neural Network model or proto "
                          "failed to be read.")
            raise sppasError(str(e))

    # -----------------------------------------------------------------------

    def _detection(self, image):
        """Really determine the coordinates of the detected objects.

        :param image: (sppasImage or numpy.ndarray)

        """
        # make predictions
        try:
            detections = self.__net_detections(image)
        except cv2.error as e:
            raise sppasError("DNN detection failed: {}".format(str(e)))

        # Loops over the detections and for each object in detection
        # get the confidence
        w, h = image.size()
        selected = list()
        for i in range(detections.shape[2]):
            # Sets the confidence score of the current object
            confidence = detections[0, 0, i, 2]

            # Filter out weak detections:
            # 1. by ensuring the `confidence` is greater than a minimum
            #    empirically fixed confidence.
            # 2. by ignoring too small faces, ie less than 5% of the image size
            if confidence > self.get_min_score():
                new_coords = self.__to_coords(detections, i, w, h, confidence)
                if new_coords.w > int(float(w) * self.get_min_ratio()) and new_coords.h > int(
                        float(w) * self.get_min_ratio()):
                    selected.append(new_coords)

        # Filter out detections:
        # 3. Overlapping faces
        for i, coord in enumerate(selected):
            # does this coord is overlapping some other ones?
            keep_me = True
            for j, other in enumerate(selected):
                if i != j and coord.intersection_area(other) > 0:
                    area_o, area_s = coord.overlap(other)
                    # reject this face if more than 50% of its area is
                    # overlapping another one and the other one has a
                    # bigger dimension, either w or h or both
                    if area_s > 50. and (coord.w < other.w or coord.h < other.h):
                        keep_me = False
                        break

            if keep_me is True:
                self._coords.append(coord)

    # -----------------------------------------------------------------------

    def __net_detections(self, image):
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
        self._detector.setInput(blob)

        # Runs forward pass to compute output of layer.
        # Then return the detections. They contain predictions about
        # what the image contains, type: "numpy.ndarray"
        return self._detector.forward()

    # -----------------------------------------------------------------------

    def __to_coords(self, detections, index, width, height, confidence):
        """Convert net detections into a list of sppasCoords.

        :returns: A list of coordinates objects.

        """
        # Determines the hitbox of the current object
        box = detections[0, 0, index, 3:7] * numpy.array([width, height, width, height])

        # Sets the values of the corners of the box
        (startX, startY, endX, endY) = box.astype("int")

        x, y, w, h = startX, startY, endX - startX, endY - startY

        # Then creates a sppasCoords object with these values
        return sppasCoords(x, y, w, h, confidence)

# ---------------------------------------------------------------------------
# Detect object with a detector
# ---------------------------------------------------------------------------


class FaceDetection(BaseObjectsDetector):
    """Detect faces in an image.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to analyze an image in order to detect faces. It
    stores a list of sppasCoords() for each detected face.

    :Example:

        >>> f = FaceDetection()
        >>> f.load_model(filename1, filename2...)
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

    Below is a list of things to do to improve FaceDetection results:
        - Normalize properly FaceDetection scores or HaarCascadeClassifier
        - Allow to estimate all face detections and fusion of results

    Contrariwise to the base class, this class allows multiple models
    in order to launch multiple detections.

    """

    DETECTORS = dict()
    DETECTORS[HaarCascadeDetector().get_extension().lower()] = HaarCascadeDetector
    DETECTORS[NetDetector().get_extension().lower()] = NetDetector

    def __init__(self):
        """Create a new FaceDetection instance."""
        super(FaceDetection, self).__init__()
        self._extension = ""

    # -----------------------------------------------------------------------

    def load_model(self, model, *args):
        """Instantiate detectors from the given models.

        :param model: (str) Default model filename
        :param args: Other models to load in order to create object detectors
        :raise: IOError, Exception

        """
        self._detector = list()
        detector = FaceDetection.create_detector_from_extension(model)
        self._detector.append(detector)

        for filename in args:
            detector = FaceDetection.create_detector_from_extension(filename)
            self._detector.append(detector)

    # -----------------------------------------------------------------------

    @staticmethod
    def extensions():
        """Return the whole list of supported extensions in lower case."""
        return list(FaceDetection.DETECTORS.keys())

    # -----------------------------------------------------------------------

    @staticmethod
    def create_detector_from_extension(filename):
        """Return an object detector according to a given filename.

        Only the extension of the filename is used.

        :param filename: (str)
        :returns: BaseObjectsDetector

        """
        extension = os.path.splitext(filename)[1][1:]
        extension = extension.lower()
        if extension in FaceDetection.extensions():
            return FaceDetection.DETECTORS[extension]()

        raise IOExtensionError(filename)

    # -----------------------------------------------------------------------

    def _detection(self, image):
        """Determine the coordinates of all the detected faces.

        :param image: (sppasImage or numpy.ndarray)

        """
        for i in range(len(self._detector)):
            # If several models were loaded, priority is given to the first one
            self._detector[i].detect(image)
            # We stop to detect as soon as a detector can find objects
            if len(self._coords) > 0:
                break

    # -----------------------------------------------------------------------

    def to_portrait(self, image=None):
        """Scale coordinates of faces to a portrait size.

        The given image allows to ensure we wont scale larger than what the
        image can do.

        :param image: (sppasImage) The original image.
        :raise: ImageXXXError if scale or shift are not possible

        """
        if len(self.__coords) == 0:
            return

        portraits = [c.copy() for c in self.__coords]
        for c in portraits:
            # Scale the image. Shift values indicate how to shift x,y to get
            # the face exactly at the center of the new coordinates.
            shift_x = shift_y = 0
            factor = 2.2
            while factor > 1.0:
                try:
                    # We need to be sure we wont scale larger than the
                    # original image. If not, reduce the scale factor.
                    shift_x, shift_y = c.scale(factor, image)
                    factor = 0.
                except:
                    factor -= 0.1

            # Re-frame the image on the face if we really scaled the image
            if shift_x != 0 and shift_y != 0:
                # TODO: to_portrait does not shift outside of the original image
                try:
                    c.shift(shift_x, 0, image)
                    shift_y = int(float(shift_y) / 1.5)
                    c.shift(0, shift_y, image)
                except:
                    # pass
                    raise

        # no error occurred, all faces can be converted to their portrait
        self._coords = portraits
