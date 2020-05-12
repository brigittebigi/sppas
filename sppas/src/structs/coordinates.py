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

    structs.coordinates.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

# ---------------------------------------------------------------------------


class sppasCoordinates(object):
    """Class to illustrate coordinates.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    A sppasCoordinates object represent the coordinate of a face from an image.
    It has 5 parameters:

    - confidence (detection confidence)
    - x (coordinate on the x axis)
    - y (coordinate on the y axis)
    - w (width of the visage)
    - h (height of the visage)

    For example:

    >>> c = sppasCoordinates(0.7, 143, 17, 150, 98)
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

    def __init__(self, confidence, x, y, w, h):
        """Create a new sppasCoordinates instance.

        :param confidence: (float) The detection confidence of a visage from an image.
        :param x: (int) Where the image start on the x axis.
        :param y: (int) Where the image start on the y axis.
        :param w: (int) The width of the image.
        :param h: (int) The height of the image.

        """

        # Represent the detection confidence of a visage from an image.
        self.__confidence = float
        self._set_confidence(confidence)

        # Represent where the image start on the x axis
        self.__x = 0
        self._set_x(x)

        # Represent where the image start on the y axis
        self.__y = 0
        self._set_y(y)

        # Represent the width of the image.
        self.__w = 0
        self._set_w(w)

        # Represent the height of the image.
        self.__h = 0
        self._set_h(h)

    # -----------------------------------------------------------------------

    def get_confidence(self):
        """Return the confidence parameter."""
        return self.__confidence

    # -----------------------------------------------------------------------

    def _set_confidence(self, value):
        """Set the value of confidence.

        :param value: (float) The value of confidence.

        """
        # Because value type is numpy.int32 is that case
        value = float(value)
        if type(value) != float or value < 0 or value > 1.0:
            raise ValueError
        self.__confidence = value

    # -----------------------------------------------------------------------

    def get_x(self):
        """Return the x parameter."""
        return self.__x

    # -----------------------------------------------------------------------

    def _set_x(self, value):
        """Set the value of x.

        :param value: (int) The value of x.

        """
        # Because value type is numpy.int32 is that case
        value = int(value)
        if type(value) != int or value > self.MAX_W:
            raise ValueError
        if value < 0:
            self.__x = 0
        else:
            self.__x = value

    # -----------------------------------------------------------------------

    def get_y(self):
        """Return the y parameter."""
        return self.__y

    # -----------------------------------------------------------------------

    def _set_y(self, value):
        """Set the value of y.

        :param value: (int) The value of y.

        """
        # Because value type is numpy.int32 is that case
        value = int(value)
        if type(value) != int or value > self.MAX_H:
            raise ValueError
        if value < 0:
            self.__y = 0
        else:
            self.__y = value

    # -----------------------------------------------------------------------

    def get_w(self):
        """Return the w parameter."""
        return self.__w

    # -----------------------------------------------------------------------

    def _set_w(self, value):
        """Set the value of w.

        :param value: (int) The value of w.

        """
        # Because value type is numpy.int32 is that case
        value = int(value)
        if type(value) != int or value < 0 or value > self.MAX_W:
            raise ValueError
        self.__w = value

    # -----------------------------------------------------------------------

    def get_h(self):
        """Return the h parameter."""
        return self.__h

    # -----------------------------------------------------------------------

    def _set_h(self, value):
        """Set the value of h.

        :param value: (int) The value of h.

        """
        # Because value type is numpy.int32 is that case
        value = int(value)
        if type(value) != int or value < 0 or value > self.MAX_H:
            raise ValueError
        self.__h = value

    # -----------------------------------------------------------------------

    def guess_portrait(self):
        """Return a new sppasCoordinates based on the face coordinates."""
        width = self.get_w() * 2
        height = self.get_h() * 2
        x = self.get_x() - self.get_w()/2
        y = self.get_y()
        coordinates = sppasCoordinates(self.get_confidence(), x, y, width, height)
        return coordinates

    # -----------------------------------------------------------------------

    def __str__(self):
        return "confidence : " + str(self.get_confidence()) + "\n" \
               "x : " + str(self.get_x()) + "\n" \
               "y : " + str(self.get_y()) + "\n" \
               "w : " + str(self.get_w()) + "\n" \
               "h : " + str(self.get_h()) + "\n"

    # -----------------------------------------------------------------------
