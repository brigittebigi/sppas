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
        """Create a new PersonBuffer instance.

        :param size: (int) The size of the buffer.
        :param overlap: (overlap) The number of values to keep
        from the previous buffer.
        :param video: (name of video file, image sequence, url or video stream,
        GStreamer pipeline, IP camera) The video to be processed.

        """
        # Use the constructor of the mother class
        super(PersonsBuffer, self).__init__(video, size, overlap)

        # The list of coordinates for each person on the video
        self.__persons = list()

        # The list of landmarks points for each person on the video
        self.__landmarks = list()

    # -----------------------------------------------------------------------

    def get_person(self, index):
        """Return Coordinates of a person.

        :param index: (int) The index of the person in the list.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        return self.__persons[index]

    # -----------------------------------------------------------------------

    def add_person(self, nb_person=1):
        """Add a person (list) in the list of persons."""
        for i in range(nb_person):
            self.__persons.append(list())

    # -----------------------------------------------------------------------

    def get_coordinate(self, index, index2):
        """Return Coordinates of a person at a certain frame.

        :param index: (int) The index of the person in the list.
        :param index2: (int) The index of the frame in the Buffer.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        index2 = int(index2)
        if isinstance(index2, int) is False:
            raise TypeError
        return self.__persons[index][index2]

    # -----------------------------------------------------------------------

    def add_coordinate(self, index, coord):
        """Add a coordinate for a person.

        :param index: (int) The index of the person in the list.
        :param coord: (Coordinate) The coordinate to add.

        """
        if isinstance(index, int) is False:
            raise TypeError

        if isinstance(coord, Coordinates) is False and coord is not None:
            raise TypeError

        self.__persons[index].append(coord)

    # -----------------------------------------------------------------------

    def get_landmarks(self, index):
        """Return landmark points of a person.

        :param index: (int) The index of the person in the list.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        return self.__landmarks[index]

    # -----------------------------------------------------------------------

    def get_landmark(self, index, index2):
        """Return landmark points of a person at a certain frame.

        :param index: (int) The index of the person in the list.
        :param index2: (int) The index of the frame in the Buffer.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        index2 = int(index2)
        if isinstance(index2, int) is False:
            raise TypeError
        return self.__landmarks[index][index2]

    # -----------------------------------------------------------------------

    def add_landmarks(self, nb_person=1):
        """Add a person (list) in the list of landmarks."""
        for i in range(nb_person):
            self.__landmarks.append(list())

    # -----------------------------------------------------------------------

    def add_landmark(self, index, landmark):
        """Add landmark points for a person.

        :param index: (int) The index of the person in the list.
        :param landmark: (list) The list of landmark points to add.

        """
        index = int(index)
        if isinstance(index, int) is False:
            raise TypeError

        if isinstance(landmark, list) is False and landmark is not None:
            raise TypeError

        self.__landmarks[index].append(landmark)

    # -----------------------------------------------------------------------

    def clear(self):
        """Clear the storage lists of the buffer."""
        self.__persons = list()
        self.__landmarks = list()

    # -----------------------------------------------------------------------

    def is_tracked(self):
        """Return False if the list of persons is empty."""
        if len(self.__persons) == 0:
            return False
        return True

    # -----------------------------------------------------------------------

    def is_landmarked(self):
        """Return False if the list of landmarks is empty."""
        if len(self.__landmarks) == 0:
            return False
        return True

    # -----------------------------------------------------------------------

    def nb_persons(self):
        """Return the number of persons."""
        if len(self.__persons) != 0:
            return len(self.__persons)
        return len(self.__landmarks)

    # ------------------------------------------------------------------------
