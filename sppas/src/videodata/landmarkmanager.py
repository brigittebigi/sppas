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

    src.videodata.landmarkmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.imagedata.facelandmark import FaceLandmark

# ---------------------------------------------------------------------------


class LandmarkManager(object):
    """Class to landmark faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    LEFT_FACE = (1, 8)
    RIGHT_FACE = (9, 17)
    LEFT_BROW_POINTS = (18, 22)
    RIGHT_BROW_POINTS = (23, 27)
    NOSE_POINTS = (28, 36)
    LEFT_EYE_POINTS = (37, 42)
    RIGHT_EYE_POINTS = (43, 48)
    MOUTH_POINTS = (49, 68)

    def __init__(self):
        """Create a new LandmarkManager instance."""
        # List of landmarks coordinates
        self.__landmarks_x = list()
        self.__landmarks_y = list()

        # List of five points coordinates for LFPC
        self.__five_x = {"left_eyes": None, "left_mouth": None, "chin": None, "throat": None, "left_visage": None}
        self.__five_y = {"left_eyes": None, "left_mouth": None, "chin": None, "throat": None, "left_visage": None}

        self.__size = 0

    # -----------------------------------------------------------------------

    def get_five_x(self):
        """Return a list of list of x-axis coordinates."""
        return self.__five_x

    # -----------------------------------------------------------------------

    def get_five_y(self):
        """Return a list of list of y-axis coordinates."""
        return self.__five_y

    # -----------------------------------------------------------------------

    def __landmark(self, buffer, tracker, mode):
        """Create a list of x-axis, y_axis value for each person.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param tracker: (FaceTracking) The FaceTracker object.
        :param mode: (str) The name of the mode option.

        """
        # Create a list of x-axis, y-axis values for each person
        for p in tracker.get_persons():
            self.__landmarks_x.append(list())
            self.__landmarks_y.append(list())

        # Initialise the iterator
        iterator = buffer.__iter__()

        # Loop over the buffer
        for i in range(0, buffer.__len__()):
            # Go to the next image
            img = next(iterator)

            # Loop over the persons
            for person in tracker.get_persons():
                # Get the index of the person
                index = tracker.get_persons().index(person)
                try:
                    # Initialize and use FaceLandmark
                    face = FaceLandmark(img, person[i])
                    face.process()
                except IndexError:
                    continue

                # If option is full then modify the x, y coordinates in landmark
                if mode == "full":
                    face.full_face()

                # Add the list of x-axis coordinates
                self.__landmarks_x[index].append(face.get_landmarks_x())

                # Add the list of y-axis coordinates
                self.__landmarks_y[index].append(face.get_landmarks_y())

    # -----------------------------------------------------------------------

    def __five_points(self):
        """Determined the five points needed for the LFPC."""
        self.__five_x["left_eyes"] = None
        self.__five_y["left_eyes"] = None

        self.__five_x["left_mouth"] = None
        self.__five_y["left_mouth"] = None

        self.__five_x["chin"] = None
        self.__five_y["chin"] = None

        self.__five_x["throat"] = None
        self.__five_y["throat"] = None

        self.__five_x["left_visage"] = None
        self.__five_y["left_visage"] = None

    # -----------------------------------------------------------------------

    def process(self, buffer, tracker, mode):
        """Launch the process to determine the five points.

        :param buffer: (VideoBuffer) The buffer which contains images.
        :param tracker: (FaceTracking) The FaceTracker object.
        :param mode: (str) The name of the mode option.

        """
        self.__landmark(buffer, tracker, mode)
        self.__five_points()

    # -----------------------------------------------------------------------

