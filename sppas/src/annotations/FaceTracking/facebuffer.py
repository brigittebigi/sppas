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

    src.annotations.FaceTracking.facebuffer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires the "video" feature of SPPAS.
    A VideoBuffer with results of FaceDetection and FaceLandmark on each
    image of the buffer.

"""

import logging

from sppas.src.exceptions import NegativeValueError
from sppas.src.exceptions import IndexRangeException
from sppas.src.exceptions import sppasError
from sppas.src.videodata import sppasVideoBuffer

from ..FaceDetection import FaceDetection
from ..FaceMark import FaceLandmark

# ---------------------------------------------------------------------------


class sppasFacesVideoBuffer(sppasVideoBuffer):
    """Class to manage a video with a buffer of images and annotation results.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to use a buffer of images on a video and to estimate
    coordinates of the faces in each of such images and the landmark sights
    on each of the detected faces.

    """

    def __init__(self, video=None,
                 size=sppasVideoBuffer.DEFAULT_BUFFER_SIZE):
        """Create a new sppasFacesVideoBuffer instance.

        :param video: (mp4, etc...) The video filename to browse
        :param size: (int) Number if images of the buffer

        """
        super(sppasFacesVideoBuffer, self).__init__(video=None, size=size, overlap=0)

        # The face detection and face landmark systems
        self.__fd = FaceDetection()
        self.__fl = FaceLandmark()

        # The list of coordinates of detected faces in each image of the
        # current buffer (list of list of sppasCoords).
        self.__faces = list()
        self.__nbest = 0
        self.__confidence = self.__fd.get_min_score()

        # The list of landmarks points of detected faces in each image of
        # the current buffer (list of list of sppasCoords).
        self.__landmarks = list()

        # The list of persons of the faces&landmarks
        self.__persons = list()

        # Then, open the video, if any
        if video is not None:
            self.open(video)

    # -----------------------------------------------------------------------

    def reset(self):
        """Override. Reset all the info related to the buffer content."""
        sppasVideoBuffer.reset(self)
        self.__reset()

    # -----------------------------------------------------------------------

    def __reset(self):
        """Reset the data related to the face detection&landmark detections."""
        self.__faces = list()
        self.__landmarks = list()
        self.__persons = list()
        self.__fl.invalidate()
        self.__fd.invalidate()

    # -----------------------------------------------------------------------

    def next(self):
        """Override. Fill in the buffer with the next images & reset results.

        """
        ret = sppasVideoBuffer.next(self)
        self.__reset()
        return ret

    # -----------------------------------------------------------------------
    # Face detection & face landmark
    # -----------------------------------------------------------------------

    def load_fd_model(self, model, *args):
        """Instantiate face detector(s) from the given models.

        Calling this method invalidates the existing detectors and the results.

        :param model: (str) Default model filename
        :param args: Other models to load in order to create object detectors
        :raise: IOError, Exception

        """
        self.__fd.load_model(model, *args)
        self.__reset()

    # -----------------------------------------------------------------------

    def load_fl_model(self, model_fd, model_landmark, *args):
        """Initialize the face landmark recognizer.

        Calling this method invalidates the existing detectors and the results.

        :param model_fd: (str) A filename of a model for face detection
        :param model_landmark: (str) Filename of a recognizer model (Kazemi, LBF, AAM).
        :param args: (str) Other filenames of models for face landmark
        :raise: IOError, Exception

        """
        self.__fl.load_model(model_fd, model_landmark, *args)
        self.__reset()

    # -----------------------------------------------------------------------

    def get_filter_best(self):
        """Return the max nb of faces to detect."""
        return self.__nbest

    # -----------------------------------------------------------------------

    def set_filter_best(self, value=-1):
        """Force to detect at max the given number of faces.

        :param value: (int) Number of faces to detect or -1 to not force.

        """
        self.__nbest = value

    # -----------------------------------------------------------------------

    def get_filter_confidence(self):
        """Return the min scores of faces to detect."""
        return self.__confidence

    # -----------------------------------------------------------------------

    def set_filter_confidence(self, value=0.2):
        """Force to detect only the faces with a confidence score > value.

        It means that any detected object with a score lesser than the given
        one will be ignored. The score of detected faces are supposed to
        range between 0. and 1.

        :param value: (float) Value ranging [0., 1.]
        :raise: ValueError

        """
        self.__confidence = value

    # -----------------------------------------------------------------------

    def detect_buffer(self):
        """Search for faces and landmarks in the current images of the buffer.

        Calling this method invalidates the existing results.

        :raise: sppasError if no model was loaded.

        """
        self.detect_faces_buffer()
        if self.__fl.get_nb_recognizers() > 0:
            self.detect_landmarks_buffer()

    # -----------------------------------------------------------------------

    def detect_faces_buffer(self):
        """Search for faces in the current images of the buffer.

        Calling this method invalidates the existing results.

        :raise: sppasError if no model was loaded.

        """
        # Invalidate previous lists of faces
        self.__reset()

        # No buffer is in-use.
        if self.__len__() == 0:
            logging.warning("Nothing to detect: no images in the buffer.")
            return
        if self.__fd.get_nb_recognizers() == 0:
            raise sppasError("A face recognizer must be initialized first")

        # Determine the coordinates of faces in each image.
        # They are ranked from the highest score to the lowest one.
        iter_images = self.__iter__()
        for i in range(self.__len__()):
            image = next(iter_images)
            # Perform face detection to detect all faces in the current image
            self.__fd.detect(image)
            logging.debug(" ... {:d} faces detected".format(len(self.__fd)))
            # Filter to keep the better ones
            if self.__nbest != 0:
                self.__fd.filter_best(self.__nbest)
            self.__fd.filter_confidence(self.__confidence)
            # Resize the detected face to the portrait, for further uses.
            self.__fd.to_portrait(image)
            # Save results into the list
            self.__faces.append([c.copy() for c in self.__fd])
            logging.debug(" ... {:d} faces after filter".format(len(self.__fd)))
            self.__fd.invalidate()

            self.__landmarks.append([None]*len(self.__faces[i]))
            self.__persons.append([None]*len(self.__faces[i]))

    # -----------------------------------------------------------------------

    def detect_landmarks_buffer(self):
        """Search for landmarks in each detected face of the buffer.

        :raise: sppasError if no model was loaded.

        """
        # No buffer is in-use.
        if self.__len__() == 0:
            logging.warning("Nothing to detect: no images in the buffer.")
            return

        if len(self.__faces) == 0:
            logging.warning("Nothing to detect: no faces were detected in "
                            "the images of the buffer.")
            return
        if self.__fl.get_nb_recognizers() == 0:
            raise sppasError("A landmark recognizer must be initialized first")

        # Determine the landmarks of all the detected faces of each image.
        iter_images = self.__iter__()
        for i in range(self.__len__()):
            image = next(iter_images)
            self.__landmarks[i] = list()
            # Perform face landmark on each detected face
            for coord in self.__faces[i]:
                # Create an image of the Region Of Interest (the portrait)
                cropped_face = image.icrop(coord)
                try:
                    self.__fl.mark(cropped_face)
                    # face_coords = self.__fl.get_detected_face()
                    # face_coords.x += coord.x
                    # face_coords.y += coord.y
                    self.__landmarks[i].append([c.copy() for c in self.__fl])
                    self.__fl.invalidate()

                except Exception as e:
                    logging.warning(
                        "A face was detected at coords {} of the {:d}-th "
                        "image, but no landmarks can be estimated: {:s}."
                        "".format(coord, i+1, str(e)))

    # -----------------------------------------------------------------------

    def set_default_detected_persons(self):
        """Set a default person name to each detected face."""
        self.__persons = list()
        iter_images = self.__iter__()
        for i in range(self.__len__()):
            image = next(iter_images)
            self.__persons.append(list())
            for j in range(len(self.__faces[i])):
                self.__persons[i].append(("X{:03d}".format(j), j))

    # -----------------------------------------------------------------------

    def get_detected_faces(self, buffer_index):
        """Return the coordinates of the faces detected at the given image index.

        :param buffer_index: (int) Index of the image in the buffer
        :return: (list of sppasCoords) Coordinates of the faces

        """
        buffer_index = self.__check_buffer_index(buffer_index)
        if len(self.__faces) != self.__len__():
            raise ValueError("No face was detected on the images of the buffer")
        return self.__faces[buffer_index]

    # -----------------------------------------------------------------------

    def get_detected_landmarks(self, buffer_index):
        """Return the landmarks of the faces detected at the given image index.

        :param buffer_index: (int) Index of the image in the buffer
        :return: (list of sppasCoords or list of list of sppasCoords) Coordinates of the face landmarks

        """
        buffer_index = self.__check_buffer_index(buffer_index)
        if len(self.__landmarks) != self.__len__():
            raise ValueError("No landmarks were detected on the images of the buffer")
        return self.__landmarks[buffer_index]

    # -----------------------------------------------------------------------

    def get_detected_persons(self, buffer_index):
        """Return the identifier of each detected face at the given image index.

        :param buffer_index: (int) Index of the image in the buffer
        :return: The person defined at the index

        """
        buffer_index = self.__check_buffer_index(buffer_index)
        if len(self.__faces) != self.__len__():
            raise ValueError("No person was defined on the faces of the images of the buffer")
        return self.__persons[buffer_index]

    # -----------------------------------------------------------------------

    def set_detected_persons(self, buffer_index, information=None):
        """Set the identifier of each detected face at the given image index.

        The information can be None, the name of the person, a dict
        with key=name and value=probability or  anything else.

        :param buffer_index: (int) Index in the current buffer.
        :param information: (any type)

        """
        buffer_index = self.__check_buffer_index(buffer_index)
        if len(self.__faces) != self.__len__():
            raise ValueError("No person was defined on the faces of the images of the buffer")
        self.__persons[buffer_index] = information

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __check_buffer_index(self, value):
        """Raise an exception if the given index is not valid."""
        value = int(value)
        if value < 0:
            raise NegativeValueError(value)
        (begin, end) = self.get_range()
        if begin == -1 or end == -1:
            raise ValueError("Invalid index value: no buffer is loaded.")
        if value < self.get_size():
            return value
        raise IndexRangeException(value, 0, self.get_size())

