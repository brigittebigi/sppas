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

    src.videodata.facetracking.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""


from sppas.src.imagedata.facedetection import FaceDetection, np


# ---------------------------------------------------------------------------


class FaceTracking(object):
    """Class to track a face.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new FaceTraking instance."""
        self.__faces = list()
        self.__persons = list()
        self.__size = 0

    # -----------------------------------------------------------------------

    def append(self, image):
        """Add a FaceDetection object in the list."""
        if isinstance(image, np.ndarray) is False:
            raise TypeError
        self.__faces.append(FaceDetection(image))

    # -----------------------------------------------------------------------

    def persons(self, buffer):
        """Add a FaceDetection object in the list."""
        iterator = buffer.__iter__()
        for i in range(0, buffer.__len__()):
            face = FaceDetection(next(iterator))
            face.detect_all()
            coordinates = face.get_all()
            for coord in coordinates:
                index = coordinates.index(coord)
                self.__size = len(coordinates)
                if len(self.__persons) < self.__size:
                    self.__persons.append(list())
                self.__persons[index].append(coord)

    # -----------------------------------------------------------------------

    def get_persons(self):
        """Add a FaceDetection object in the list."""
        return self.__persons

    # -----------------------------------------------------------------------

    def apply(self):
        for face in self.__faces:
            face.detect_all()

    # -----------------------------------------------------------------------

    def get_faces(self):
        """Return a list of FaceDetection objects."""
        return self.__faces

    # -----------------------------------------------------------------------

