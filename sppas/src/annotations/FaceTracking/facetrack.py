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

    src.annotations.FaceTracking.facetracking.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires the "video" feature of SPPAS.
    Automatic face detection in a video, i.e. face tracking, based on opencv
    HaarCascadeClassifier and DNN.

"""

import numpy as np

from sppas.src.exceptions import NegativeValueError
from sppas.src.exceptions import sppasTypeError

# ---------------------------------------------------------------------------


class FaceTracking(object):
    """Search for faces on images of a video.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new FaceTracker instance."""
        # The expected number of faces. -1 means auto.
        self.__nb_faces = -1
        # A reference image to represent the face of each person
        # key=a name or any other identifier, value=sppasImage
        self.__img_known_faces = dict()      # user-defined persons
        self.__img_unknown_faces = dict()    # detected unknown persons

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_nb_faces(self, value=-1):
        """Force to detect at max the given number of faces.

        :param value: (int) Number of faces to detect or -1 to not force.

        """
        value = int(value)
        if value == 0 or value < -2:
            raise NegativeValueError(value)
        self.__nb_faces = value

    # -----------------------------------------------------------------------

    def set_reference_faces(self, known_faces=tuple()):
        """Set the list of images representing faces of known persons.

        The given images can be a list with images to represents the faces
        or a dictionary with key=string and value=the image.
        :param known_faces: (list of sppasImage or dict)

        """
        names = list()
        faces = list()
        if isinstance(known_faces, (list, tuple)):
            for i, img in enumerate(known_faces):
                if isinstance(img, np.ndarray) is False:
                    raise sppasTypeError(img, "(sppasImages, numpy.ndarray)")
                names.append("X{:03d}".format(i))
        elif isinstance(known_faces, dict):
            for key in enumerate(known_faces):
                img = known_faces[key]
                if isinstance(img, np.ndarray) is False:
                    raise sppasTypeError(img, "(sppasImages, numpy.ndarray)")
                names.append(str(key))
                faces.append(img)
        else:
            raise sppasTypeError(known_faces, "dict, list, tuple")

        self.__img_known_faces = dict()
        for key, value in zip(names, faces):
            self.__img_unknown_faces[key] = value

    # -----------------------------------------------------------------------
    # Automatic detection of the faces in a video
    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate the list of all detected faces."""
        self.__img_unknown_faces = list()

    # -----------------------------------------------------------------------

    def detect_buffer(self, video_buffer):
        """Search for faces in the currently loaded buffer of a video.

        :param video_buffer: (sppasFacesVideoBuffer) The video to be processed
        :return: (list of sppasCoordinates)

        """
        # Determine the coordinates of all the detected faces.
        # They are ranked from the highest score to the lowest one.
        video_buffer.detect_faces()

        # Assign a face to each known and unknown person
        tracked_faces = self.__track(video_buffer)

        return tracked_faces

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

        # distances = self.__face_distance(known_face_encodings, unknown_encoding)
        # result = list(distances <= tolerance)
    # -----------------------------------------------------------------------

    def __track(self, all_faces):
        """Compare given faces to the reference ones and sort them.

        :param all_faces: (list of list of sppasCoords)

        """
        all_identified = list()
        # Fill in the list with the appropriate coordinates
        for faces in all_faces:

            identified = list()
            # "faces" is a list of sppasCoords corresponding to a face in an image
            # Identify the person of each of these faces
            for i, coords in enumerate(faces):
                identified = i

            # Add unknown persons to the list

            # Append the identified
            all_identified.append(identified)

        nb_persons = len(self.__img_known_faces) + len(self.__img_unknown_faces)
        if self.__nb_faces != -1:
            nb_persons = self.__nb_faces

        # One list of sppasCoords for each person
        persons = [[None]*nb_persons for i in range(len(all_faces))]
        # Fill in the persons with the identified
        for i, faces in enumerate(all_faces):
            identified = all_identified[i]
            for x in range(len(identified)):
                persons[i][identified[x]] = faces[x]

        return persons
