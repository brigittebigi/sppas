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

    src.videodata.personsbuffer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import numpy as np
import cv2
from cv2 import CAP_PROP_POS_FRAMES, CAP_PROP_FPS

from sppas.src.videodata.videobuffer import VideoBuffer
from sppas.src.imagedata.coordinates import Coordinates

# ---------------------------------------------------------------------------


class PersonsBuffer(VideoBuffer):
    """Class to detect faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to use a Buffer on a video to manage it
    sequentially and to have a better control on it.

    """

    def __init__(self, video, size=200, overlap=0):
        """Create a new ImageBuffer instance.

        :param size: (int) The size of the buffer.
        :param overlap: (overlap) The number of values to keep
        from the previous buffer.
        :param video: (mp4, etc...) The video to browse

        """
        super(PersonsBuffer, self).__init__(video, size, overlap)

        # The list of the coordinates for each person on the video
        self.__persons = list()

        # The list of landmarks points for each person on the video
        self.__landmarks = list()

    # -----------------------------------------------------------------------

    def get_persons(self):
        """Return a list of persons with coordinates."""
        return self.__persons

    # -----------------------------------------------------------------------

    def get_person(self, index, index2):
        """Return a list of persons with coordinates."""
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        index2 = int(index2)
        if isinstance(index2, int) is False:
            raise TypeError

        return self.__persons[index][index2]

    # -----------------------------------------------------------------------

    def add_person(self):
        """Add a person (list) in the list of persons."""
        self.__persons.append(list())

    # -----------------------------------------------------------------------

    def add_coordinate(self, index, coord):
        """Add a coordinate for a person.

        :param index: (int) The index of the person in the list.
        :param coord: (Coordinate) The coordinate to add.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        if isinstance(coord, Coordinates) is False:
            raise TypeError

        self.__persons[index].append(coord)

    # -----------------------------------------------------------------------

    def get_landmarks(self):
        """Return a list of persons with landmarks."""
        return self.__landmarks

    # -----------------------------------------------------------------------

    def get_landmark(self, index, index2):
        """Return a list of persons with landmarks."""
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        index2 = int(index2)
        if isinstance(index2, int) is False:
            raise TypeError

        return self.__landmarks[index][index2]

    # -----------------------------------------------------------------------

    def add_landmarks(self):
        """Add a person (list) in the list of landmarks."""
        self.__landmarks.append(list())

    # -----------------------------------------------------------------------

    def add_landmark(self, index, landmark):
        """Add a landmark for a person.

        :param index: (int) The index of the person in the list.
        :param landmark: (list) The list of five points to add.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        if isinstance(landmark, dict) is False:
            raise TypeError

        self.__landmarks[index].append(landmark)

    # -----------------------------------------------------------------------

    def clear(self):
        """Clear the differents storage list of the buffer."""
        self.__persons = list()
        self.__landmarks = list()

    # -----------------------------------------------------------------------

    def len_persons(self):
        """Return the len of the list of persons."""
        return len(self.__persons)

    # -----------------------------------------------------------------------

    def len_landmarks(self):
        """Return the len of the list of landmarks."""
        return len(self.__landmarks)

    # ------------------------------------------------------------------------
