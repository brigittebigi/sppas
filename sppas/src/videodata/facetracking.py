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
import _testbuffer as tb

import numpy as np
import imutils
import cv2
import os
import wx
from pympler.asizeof import asizeof

from sppas.src.config import sppasPathSettings
from sppas.src.imagedata.facedetection import FaceDetection

# ---------------------------------------------------------------------------


class RingBuffer:
    def __init__(self, size):
        self.data = [None for i in range(size)]

    # -----------------------------------------------------------------------

    def append(self, x):
        self.data.pop(0)
        self.data.append(x)

    # -----------------------------------------------------------------------

    def get_data(self):
        return self.data

    # -----------------------------------------------------------------------

    def __str__(self):
        string = str()
        for i in self.get_data():
            string += str(i) + "\n"
        return string

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

# ---------------------------------------------------------------------------


class FaceTracking(object):
    """Class to detect faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create a new faceTracking instance."""
        self.__coordinates = list()
        self.__persons = list()

        self.__buffer = RingBuffer(4)

        liste = list()
        img = cv2.imread("../../../../../../trump.jpg")
        # for i in range(0, 6):
        #     liste.append(img)
        #
        # self.init_images(liste)

        print(self.__buffer)
        print(asizeof(self.__buffer))

    # -----------------------------------------------------------------------

    def init_images(self, liste):
        """Returns all the faces coordinates in a list"""
        if isinstance(liste, list) is False:
            raise TypeError
        for image in liste:
            self.__buffer.append(image)

    # -----------------------------------------------------------------------

    def video_process(self, video):
        """Returns all the faces coordinates in a list"""

    # -----------------------------------------------------------------------


f = FaceTracking()
