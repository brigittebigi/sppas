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

    This class allows to use a buffer of images on a video to manage it
    sequentially and to have a better control on it.

    """

    def __init__(self, video=None,
                 size=sppasVideoBuffer.DEFAULT_BUFFER_SIZE,
                 overlap=sppasVideoBuffer.DEFAULT_BUFFER_OVERLAP):
        """Create a new sppasFacesVideoBuffer instance.

        :param size: (int) Number if images of the buffer
        :param overlap: (overlap) The number of images to keep
        from the previous buffer
        :param video: (mp4, etc...) The video filename to browse

        """
        super(sppasFacesVideoBuffer, self).__init__()

        # The face detection and face landmark systems
        self.__fd = FaceDetection()
        self.__fl = FaceLandmark()

        # The list of coordinates of detected faces in each image of the
        # current buffer (list of list of sppasCoords).
        self.__faces = list()

        # The list of landmarks points of detected faces in each image of
        # the current buffer (list of list of sppasCoords).
        self.__landmarks = list()

    # -----------------------------------------------------------------------

    def load_fd_model(self, model, *args):
        """Instantiate face detector(s) from the given models.

        Calling this method invalidates the existing detectors.

        :param model: (str) Default model filename
        :param args: Other models to load in order to create object detectors
        :raise: IOError, Exception

        """
        self.__fd.load_model(model, *args)

    # -----------------------------------------------------------------------

    def load_fl_model(self, model_fd, model_landmark, *args):
        """Initialize the face landmark recognizer.

        :param model_fd: (str) A filename of a model for face detection
        :param model_landmark: (str) Filename of a recognizer model (Kazemi, LBF, AAM).
        :param args: (str) Other filenames of models for face landmark
        :raise: IOError, Exception

        """
        self.__fl.load_model(model_fd, model_landmark, *args)

    # -----------------------------------------------------------------------

    def detect_buffer(self):
        """Search for faces in the currently loaded buffer of a video.

        :raise: sppasError if no model was loaded.

        """
        # Invalidate previous lists of faces
        self.__faces = list()
        self.__landmarks = list()

        # Determine the coordinates of all the detected faces.
        # They are ranked from the highest score to the lowest one.
        iter_images = self.__iter__()
        for i in range(self.__len__()):
            image = next(iter_images)

            # Perform face detection to detect all faces in the current image
            self.__fd.detect(image)
            self.__fd.to_portrait(image)
            self.__faces.append([c.copy() for c in self.__fd])

            # Perform face landmark on each detected face
            iter_coords = self.__fd.__iter__()
            for j in range(0, self.__fd.__len__()):
                coord = next(iter_coords)
                # Create an image of the Region Of Interest (the portrait)
                cropped_face = image.icrop(coord)
                try:
                    self.__fl.mark(cropped_face)
                    face_coords = self.__fl.get_detected_face()
                    # face_coords.x += coord.x
                    # face_coords.y += coord.y
                    self.__landmarks.append(face_coords)

                except Exception as e:
                    logging.warning(
                        "A face was detected at coords {} of the {:d}-th "
                        "image, but no landmarks can be estimated: {:s}."
                        "".format(coord, i+1, str(e)))
                    self.__landmarks.append(tuple())

            self.__fd.invalidate()
            self.__fl.invalidate()

    # -----------------------------------------------------------------------

    def get_detected_faces(self, buffer_index):
        """"""
        return self.__faces[buffer_index]



