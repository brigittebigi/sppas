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

    src.videodata.videolandmark.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os

from sppas.src.config import sppasPathSettings
from sppas.src.imagedata.facelandmark import FaceLandmark

# ---------------------------------------------------------------------------


class VideoLandmark(object):
    """Class to landmark faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new VideoLandmark instance."""
        # List of landmarks coordinates
        self.__landmarks = list()

        # List of five points coordinates for LFPC
        self.__five = dict()

        self.__cascade = self.__get_haarcascade()
        self.__size = 0

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_haarcascade():
        """Return the predictor file."""
        try:
            haarcascade = os.path.join(sppasPathSettings().resources, "image",
                                       "haarcascade_frontalface_alt2.xml")
            return haarcascade
        except OSError:
            return "File does not exist"

    # -----------------------------------------------------------------------

    def get_five(self):
        """Return a list of list of x-axis, y-axis coordinates."""
        return self.__five

    # -----------------------------------------------------------------------

    def get_points(self):
        """Return a list of tuple of x-axis, y-axis coordinates."""
        pass

    # -----------------------------------------------------------------------

    def __landmark(self, image):
        """Create a list of x-axis, y_axis value for each person.

        :param image: (np.ndarray) The image to be processed

        """
        try:
            # Initialize and use FaceLandmark
            face = FaceLandmark(self.__cascade)

            # Launch the process of FaceLandmark
            face.landmarks(image)
        except IndexError:
            raise IOError

        # Add the list of x-axis coordinates
        self.__landmarks.append(face.get_landmarks_x())

        # Add the list of y-axis coordinates
        self.__landmarks.append(face.get_landmarks_y())

    # -----------------------------------------------------------------------

    def __five_points(self, image):
        """Determined the five points needed for the LFPC."""
        (h, w) = image.shape[:2]

        self.__five["left_eyes"] = (0, 0)

        self.__five["left_mouth"] = (w, 0)

        self.__five["chin"] = (0, h)

        self.__five["throat"] = (w, h)

        self.__five["left_visage"] = (int(w/2), int(h/2))

        return self.__five

    # -----------------------------------------------------------------------

    def process(self, image):
        """Launch the process to determine the five points.

        :param image: (np.ndarray) The image to be processed

        """
        self.reset()
        # self.__landmark(image)
        five_points = self.__five_points(image)
        return five_points

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the privates attributes."""
        self.__landmarks = list()
        self.__five = dict()

    # -----------------------------------------------------------------------
