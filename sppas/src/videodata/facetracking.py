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

from sppas.src.imgdata.facedetection import FaceDetection

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

        self.__max_persons = 0

    # -----------------------------------------------------------------------

    def detect(self, buffer):
        """Create a list of sppasCoords for each image.

        :param buffer: (PersonBuffer) The buffer which contains images.

        """
        iterator = buffer.__iter__()
        for i in range(len(buffer)):
            face = FaceDetection(next(iterator))
            face.detect_all()
            if len(face.get_all()) > self.__max_persons:
                self.__max_persons = len(face.get_all())
            self.__faces.append(face.get_all())

    # -----------------------------------------------------------------------

    def create_persons(self, buffer, nb_person=0):
        """Browse the list of sppasCoords and create a list for each person.

        :param buffer: (PersonBuffer) The buffer which contains images.
        :param nb_person: (int) The number of person to store.

        """
        if nb_person == 0:
            self.all_persons(buffer)
        else:
            self.several_persons(buffer, nb_person)

    # -----------------------------------------------------------------------

    def all_persons(self, buffer):
        """Create a list for each person.

        :param buffer: (PersonBuffer) The buffer which contains images.

        """
        buffer.add_person(self.__max_persons)

        for face in self.__faces:
            for i in range(self.__max_persons):
                try:
                    buffer.add_coordinate(i, face[i])
                except IndexError:
                    buffer.add_coordinate(i, None)

    # -----------------------------------------------------------------------

    def several_persons(self, buffer, nb_person):
        """Create a list for each person with a maximum of nb_person.

        :param buffer: (PersonBuffer) The buffer which contains images.
        :param nb_person: (int) The number of person to store.

        """
        liste = list()
        for face in self.__faces:
            liste.append(face[0:nb_person])

        for i in range(nb_person):
            buffer.add_person()

        for face in liste:
            for i in range(nb_person):
                try:
                    buffer.add_coordinate(i, face[i])
                except IndexError:
                    buffer.add_coordinate(i, None)

    # -----------------------------------------------------------------------

    def clear(self):
        """Reset the private members of the FaceTracker."""
        self.__faces = list()
        self.__max_persons = 0

    # -----------------------------------------------------------------------

