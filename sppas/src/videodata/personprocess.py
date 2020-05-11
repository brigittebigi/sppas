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

    src.videodata.personProcess.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.videodata.facetracking import faceTracking
import sys
from pympler.asizeof import asizeof

# ---------------------------------------------------------------------------


class personProcess(object):
    """Class to manage the person.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create a new personProcess instance."""
        self.__f = faceTracking("../../../../../LFPC_test_1.mp4")
        self.__persons = list()
        self.__coord_to_person()

    # -----------------------------------------------------------------------

    def nb_persons(self):
        """return the maximum number of person."""
        detections = dict()
        for f in self.__f.get_coordinates():
            if len(f) not in detections.keys():
                detections[len(f)] = 1
            else:
                detections[len(f)] += 1
        nb_person = 0
        for keys in detections.keys():
            if keys > nb_person:
                nb_person = keys
        return nb_person

    # -----------------------------------------------------------------------

    def __coord_to_person(self):
        """Create a list of coordinates for each person."""
        nb_persons = self.nb_persons()
        for i in range(0, nb_persons):
            self.__persons.append(list())
        for f in self.__f.get_coordinates():
            for i in f:
                self.__persons[f.index(i)].append(i)

    # -----------------------------------------------------------------------

    def get_persons(self):
        """Returns list with coordinates of faces for each frame."""
        return self.__persons

    # -----------------------------------------------------------------------

    def get_coordinates(self, index):
        """Returns list with coordinates for a frame."""
        try:
            return self.__persons[index]
        except IndexError:
            pass

    # -----------------------------------------------------------------------

