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

    src.imagedata.facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import time

import cv2
from imutils.video import FileVideoStream
from pympler.asizeof import asizeof
from sppas.src.imagedata.facedetection import FaceDetection

# ---------------------------------------------------------------------------


class ImageBuffer(object):
    """Class to detect faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class allows to create a buffer and manage it.

    """

    def __init__(self, size, overlap):
        """Create a new ImageBuffer instance.

        :param size: (int) The size of the buffer.
        :param overlap: (overlap) The number of values to keep
        from the previous buffer.

        """
        self.__size = size
        self.__overlap = overlap
        self.__data = [None]*self.__size
        self.__current = self.__data[0]

    # -----------------------------------------------------------------------

    def append(self, list_values):
        """Replace the "size - overlap" last values with the values in list_values."""
        del self.__data[0:(self.__size - self.__overlap)]
        self.__data.extend(list_values)
        self.__current = self.__data[0]

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return a list of data."""
        return self.__data

    # -----------------------------------------------------------------------

    def __iter__(self):
        return self.__current

    # -----------------------------------------------------------------------

    def next(self):
        """Return the next value in self.__data."""
        index = self.__data.index(self.__current)
        if index == len(self.__data):
            raise StopIteration
        self.__current = self.__data[index + 1]
        return self.__current

    # -----------------------------------------------------------------------

    def previous(self):
        """Return the previous value in self.__data."""
        index = self.__data.index(self.__current)
        if index == 0:
            raise StopIteration
        self.__current = self.__data[index - 1]
        return self.__current

    # -----------------------------------------------------------------------

    def __str__(self):
        string = str()
        for i in self.get_data():
            string += str(i) + "\n"
        return string

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

