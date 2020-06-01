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

from sppas.src.imagedata.facedetection import FaceDetection

# ---------------------------------------------------------------------------


class FaceTracking(object):
    """Class to track a face.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, nb_person=0):
        """Create a new FaceTraking instance."""
        self.__nb_person = nb_person
        self.__faces = list()
        self.__size = 0

    # -----------------------------------------------------------------------

    def detect(self, buffer):
        """Create a list of coordinates for each images.

        :param buffer: (VideoBuffer) The buffer which contains images.

        """
        iterator = buffer.__iter__()
        for i in range(0, buffer.__len__()):
            face = FaceDetection(next(iterator))
            face.detect_all()
            self.__faces.append(face.get_all())

    # -----------------------------------------------------------------------

    def person(self, buffer):
        """Create a list for each person."""
        if self.__nb_person == 0:
            self.all_persons(buffer)
        else:
            self.several_persons(buffer)

    # -----------------------------------------------------------------------

    def all_persons(self, buffer):
        """Create a list for each person."""
        for face in self.__faces:
            for coord in face:
                index = face.index(coord)
                self.__size = len(face)
                if buffer.len_persons() < self.__size:
                    buffer.add_person()
                buffer.add_coordinate(index, coord)

    # -----------------------------------------------------------------------

    def several_persons(self, buffer):
        """Create a list for each person."""
        liste = list()
        for face in self.__faces:
            liste.append(face[0:self.__nb_person])
        for face in liste:
            for coord in face:
                index = face.index(coord)
                self.__size = len(face)
                if buffer.len_persons() < self.__size:
                    buffer.add_person()
                buffer.add_coordinate(index, coord)

    # -----------------------------------------------------------------------

    def clear(self):
        """Reset the tracker."""
        self.__faces = list()
        self.__size = 0

    # -----------------------------------------------------------------------

