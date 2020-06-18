# -*- coding: UTF-8 -*-
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

    src.imgdata.coordinates.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.exceptions import sppasTypeError
from sppas.src.exceptions import IntervalRangeException
from .imgdataexc import ImageEastingError, ImageNorthingError
from .imgdataexc import ImageWidthError, ImageHeightError, ImageBoundError

# ---------------------------------------------------------------------------


class sppasCoords(object):
    """Class to illustrate coordinates of an area.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A sppasCoords object represents the coordinates of an image.
    It has 5 parameters:

    - x: coordinate on the x axis
    - y: coordinate on the y axis
    - w: width of the visage
    - h: height of the visage
    - an optional confidence score

    :Example:

    >>> c = sppasCoords(143, 17, 150, 98, 0.7)
    >>> c.get_confidence()
    >>> 0.7
    >>> c.get_x()
    >>> 143
    >>> c.get_y()
    >>> 17
    >>> c.get_w()
    >>> 150
    >>> c.get_h()
    >>> 98

    """

    # 4K width multiplied by 4
    MAX_W = 15360

    # 4K height multiplied by 4
    MAX_H = 8640

    # -----------------------------------------------------------------------

    def __init__(self, value_x, value_y, value_w, value_h, confidence=None):
        """Create a new sppasCoords instance.

        :param value_x: (int) Where the image starts on the x-axis.
        :param value_y: (int) Where the image starts on the y-axis.
        :param value_w: (int) The width of the image.
        :param value_h: (int) The height of the image.
        :param confidence: (float) An optional confidence score ranging [0,1]

        """
        self.__x = 0
        self.__set_x(value_x)

        self.__y = 0
        self.__set_y(value_y)

        self.__w = 0
        self.__set_w(value_w)

        self.__h = 0
        self.__set_h(value_h)

        # Save memory by using None instead of float if confidence is not set
        self.__confidence = None
        self.__set_confidence(confidence)

    # -----------------------------------------------------------------------

    def get_confidence(self):
        """Return the confidence value (float)."""
        if self.__confidence is None:
            return 0.
        return self.__confidence

    # -----------------------------------------------------------------------

    def __set_confidence(self, value):
        """Set confidence value.

        :param value: (float) The new confidence value ranging [0, 1].
        :raise: TypeError, ValueError

        """
        if value is None:
            self.__confidence = None
        else:
            value = self.__to_dtype(value, dtype=float)
            if value < 0. or value > 1.:
                raise IntervalRangeException(value, 0, 1)
            self.__confidence = value

    # -----------------------------------------------------------------------

    def get_x(self):
        """Return x-axis value (int)."""
        return self.__x

    # -----------------------------------------------------------------------

    def __set_x(self, value):
        """Set x-axis value.

        :param value: (int) The new x-axis value.
        :raise: TypeError, ValueError

        """
        value = self.__to_dtype(value)
        if value < 0 or value > sppasCoords.MAX_W:
            raise IntervalRangeException(value, 0, sppasCoords.MAX_W)
        self.__x = value

    # -----------------------------------------------------------------------

    def get_y(self):
        """Return y-axis value (int)."""
        return self.__y

    # -----------------------------------------------------------------------

    def __set_y(self, value):
        """Set y-axis value.

        :param value: (int) The new y-axis value.
        :raise: TypeError, ValueError

        """
        value = self.__to_dtype(value)
        if value < 0 or value > sppasCoords.MAX_H:
            raise IntervalRangeException(value, 0, sppasCoords.MAX_H)
        self.__y = value

    # -----------------------------------------------------------------------

    def get_w(self):
        """Return width value (int)."""
        return self.__w

    # -----------------------------------------------------------------------

    def __set_w(self, value):
        """Set width value.

        :param value: (int) The new width value.
        :raise: TypeError, ValueError

        """
        value = self.__to_dtype(value)
        if value < 0 or value > sppasCoords.MAX_W:
            raise IntervalRangeException(value, 0, sppasCoords.MAX_W)
        self.__w = value

    # -----------------------------------------------------------------------

    def get_h(self):
        """Return height value (int)."""
        return self.__h

    # -----------------------------------------------------------------------

    def __set_h(self, value):
        """Set height value.

        :param value: (int) The new height value.
        :raise: TypeError, ValueError

        """
        value = self.__to_dtype(value)
        if value < 0 or value > sppasCoords.MAX_H:
            raise IntervalRangeException(value, 0, sppasCoords.MAX_H)
        self.__h = value

    # -----------------------------------------------------------------------

    def __to_dtype(self, value, dtype=int):
        """Convert a value to int or raise the appropriate exception."""
        try:
            value = dtype(value)
            if isinstance(value, dtype) is False:
                raise sppasTypeError(value, str(dtype))
        except ValueError:
            raise sppasTypeError(value, str(dtype))

        return value

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    x = property(get_x, __set_x)
    y = property(get_y, __set_y)
    w = property(get_w, __set_w)
    h = property(get_h, __set_h)

    # -----------------------------------------------------------------------
    # Methods to manipulate coordinates
    # -----------------------------------------------------------------------

    def scale(self, coeff, image=None):
        """Multiply width and height values with given coefficient value.

        :param coeff: (int) The value to multiply with.
        :param image: (numpy.ndarray or sppasImage) An image to check w, h.
        :returns: Returns the value of the shift to use on the x-axis,
        according to the value of the scale in order to keep the same center.
        :raise: TypeError, ScaleWidthError, ScaleHeightError

        """
        coeff = self.__to_dtype(coeff, dtype=float)
        new_w = int(float(self.__w) * coeff)
        new_h = int(float(self.__h) * coeff)

        # Check new values with the width and height of the given image
        if image is not None:
            (height, width) = image.shape[:2]
            if new_w > width:
                raise ImageWidthError(new_w, width)
            if new_h > height:
                raise ImageHeightError(new_h, height)

        shift_x = int(float(self.__w - new_w) / 2.)
        shift_y = int(float(self.__h - new_h) / 2.)
        self.__w = new_w
        self.__h = new_h
        return shift_x, shift_y

    # -----------------------------------------------------------------------

    def shift(self, x_value, y_value=0, image=None):
        """Multiply width and height value with coeff value.

        :param x_value: (int) The value to add to x-axis value.
        :param y_value: (int) The value to add to y-axis value.
        :param image: (numpy.ndarray or sppasImage) An image to check coords.
        :raise: TypeError

        """
        # Check and convert given values
        x_value = self.__to_dtype(x_value)
        y_value = self.__to_dtype(y_value)

        new_x = self.__x + x_value
        new_y = self.__y + y_value
        if new_x < 0:
            new_x = 0
        elif new_y < 0:
            new_y = 0

        if image is not None:
            # Get the width and height of image
            (max_h, max_w) = image.shape[:2]
            if new_x > max_w:
                raise ImageEastingError(new_x, max_w)
            elif new_x + self.__w > max_w:
                raise ImageBoundError(new_x + self.__w, max_w)
            elif new_y > max_h:
                raise ImageNorthingError(new_y, max_h)
            elif new_y + self.__h > max_h:
                raise ImageBoundError(new_y + self.__h, max_h)

        self.__x = new_x
        self.__y = new_y

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of the current sppasCoords."""
        return sppasCoords(self.__x, self.__y, self.__w, self.__h,
                           self.__confidence)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        return \
               "(" + str(self.__x) + ", " + str(self.__y) + ") " \
               "(" + str(self.__w) + ", " + str(self.__h) + "): " \
               + str(self.get_confidence())

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Return true if self equal other."""
        if isinstance(other, (list, tuple)):
            if len(other) >= 4:
                other = sppasCoords(other[0], other[1], other[2], other[3])
            else:
                return False
        if isinstance(other, sppasCoords) is False:
            return False
        if self.__x != other.x:
            return False
        if self.__y != other.y:
            return False
        if self.__w != other.w:
            return False
        if self.__h != other.h:
            return False
        return True

