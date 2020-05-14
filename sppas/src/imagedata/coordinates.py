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

    src.imagedata.coordinates.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

# ---------------------------------------------------------------------------


class Coordinates(object):
    """Class to illustrate coordinates.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A sppasCoordinates object represent the coordinate of a face from an image.
    It has 5 parameters:

    - confidence (detection confidence)
    - x (coordinate on the x axis)
    - y (coordinate on the y axis)
    - w (width of the visage)
    - h (height of the visage)

    For example:

    >>> c = Coordinates(0.7, 143, 17, 150, 98)
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

    # 4K width multiply by 4
    MAX_W = 15360

    # 4K height multiply by 4
    MAX_H = 8640

    def __init__(self, x, y, w, h, confidence=0.0):
        """Create a new sppasCoordinates instance.

        :param confidence: (float) The detection confidence of an object from an image.
        :param x: (int) Where the image starts on the x axis.
        :param y: (int) Where the image starts on the y axis.
        :param w: (int) The width of the image.
        :param h: (int) The height of the image.

        """

        # Represent the detection confidence of an object from an image.
        self.__confidence = float
        self._set_confidence(confidence)

        # Represent where the image start on the x axis
        self.__x = 0
        self.x = x

        # Represent where the image start on the y axis
        self.__y = 0
        self.y = y

        # Represent the width of the image.
        self.__w = 0
        self.w = w

        # Represent the height of the image.
        self.__h = 0
        self.h = h

    # -----------------------------------------------------------------------

    def get_confidence(self):
        """Return the confidence value."""
        return self.__confidence

    # -----------------------------------------------------------------------

    def _set_confidence(self, value):
        """Set confidence value.

        :param value: (float) The new confidence value.

        """
        # Because value type is numpy.int32 is that case
        value = float(value)
        if type(value) != float or value < 0 or value > 1.0:
            raise ValueError
        self.__confidence = value

    # -----------------------------------------------------------------------

    def get_x(self):
        """Return x axis value."""
        return self.__x

    # -----------------------------------------------------------------------

    def _set_x(self, value):
        """Set x-axis value.

        :param value: (int) The new x-axis value.

        """
        # Because value type is numpy.int32 is that case
        value = int(value)
        if type(value) != int or value < 0 or value > Coordinates.MAX_W:
            raise ValueError
        else:
            self.__x = value

    # -----------------------------------------------------------------------

    # Allows to use simplified versions of guetter and setter
    x = property(get_x, _set_x)

    # -----------------------------------------------------------------------

    def get_y(self):
        """Return y axis value."""
        return self.__y

    # -----------------------------------------------------------------------

    def _set_y(self, value):
        """Set y-axis value.

        :param value: (int) The new y-axis value.

        """
        # Because value type is numpy.int32 is that case
        value = int(value)
        if type(value) != int or value < 0 or value > Coordinates.MAX_H:
            raise ValueError
        else:
            self.__y = value

    # -----------------------------------------------------------------------

    # Allows to use simplified versions of guetter and setter
    y = property(get_y, _set_y)

    # -----------------------------------------------------------------------

    def get_w(self):
        """Return width value."""
        return self.__w

    # -----------------------------------------------------------------------

    def _set_w(self, value):
        """Set width value.

        :param value: (int) The new width value.

        """
        # Because value type is numpy.int32 is that case
        value = int(value)
        if type(value) != int or value < 0 or value > Coordinates.MAX_W:
            raise ValueError
        self.__w = value

    # -----------------------------------------------------------------------

    # Allows to use simplified versions of guetter and setter
    w = property(get_w, _set_w)

    # -----------------------------------------------------------------------

    def get_h(self):
        """Return height value."""
        return self.__h

    # -----------------------------------------------------------------------

    def _set_h(self, value):
        """Set height value.

        :param value: (int) The new height value.

        """
        # Because value type is numpy.int32 is that case
        value = int(value)
        if type(value) != int or value < 0 or value > Coordinates.MAX_H:
            raise ValueError
        self.__h = value

    # -----------------------------------------------------------------------

    # Allows to use simplified versions of guetter and setter
    h = property(get_h, _set_h)

    # -----------------------------------------------------------------------

    def scale(self, coeff):
        """Multiply width and height value with coeff value."""
        if isinstance(coeff, float) is False:
            raise ValueError
        self.w = int(self.w * coeff)
        self.h = int(self.h * coeff)

    # -----------------------------------------------------------------------

    def __str__(self):
        return "confidence :" + str(self.get_confidence()) + "\n" \
               "x: " + str(self.get_x()) + "\n" \
               "y: " + str(self.get_y()) + "\n" \
               "w: " + str(self.get_w()) + "\n" \
               "h: " + str(self.get_h()) + "\n"

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Return true if self equal other."""
        if isinstance(other, list):
            if len(other) == 4:
                other = Coordinates(other[0], other[1], other[2], other[3])
            else:
                raise TypeError
        if isinstance(other, Coordinates) is False:
            raise TypeError
        if self.get_x() != other.get_x():
            return False
        if self.get_y() != other.get_y():
            return False
        if self.get_w() != other.get_w():
            return False
        if self.get_h() != other.get_h():
            return False
        return True

    # -----------------------------------------------------------------------

