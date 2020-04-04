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

    anndata.annloc.point.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging

from sppas.src.utils.makeunicode import text_type, binary_type

from ...anndataexc import AnnDataTypeError
from ...anndataexc import AnnDataNegValueError

from .localization import sppasBaseLocalization
from .duration import sppasDuration

# ---------------------------------------------------------------------------


class sppasPoint(sppasBaseLocalization):
    """Localization of a point for any numerical representation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Represents a point identified by a midpoint value and a radius value.
    Generally, time is represented in seconds, as a float value ; frames
    are represented by integers like ranks.

    In this class, the 3 relations <, = and > take into account a radius
    value, that represents the uncertainty of the localization. For a point x,
    with a radius value of dx, and a point y with a radius value of dy, these
    relations are defined as:

        - x = y iff |x - y| <= dx + dy
        - x < y iff not(x = y) and x < y
        - x > y iff not(x = y) and x > y

    :Example 1: Strictly equals:

        - x = 1.000, dx=0.
        - y = 1.000, dy=0.
        - x = y is true

        - x = 1.00000000000, dx=0.
        - y = 0.99999999675, dy=0.
        - x = y is false

    :Example 2: Using the radius:

        - x = 1.0000000000, dx=0.0005
        - y = 1.0000987653, dx=0.0005
        - x = y is true  (accept a margin of 1ms between x and y)

        - x = 1.0000000, dx=0.0005
        - y = 1.0011235, dx=0.0005
        - x = y is false

    """

    def __init__(self, midpoint, radius=None):
        """Create a sppasPoint instance.

        :param midpoint: (float, int) midpoint value.
        :param radius: (float, int) represents the vagueness of the point.
        Radius must be of the same type as midpoint.

        """
        super(sppasPoint, self).__init__()

        self.__midpoint = 0
        self.__radius = None

        self.set_midpoint(midpoint)
        self.set_radius(radius)

    # -----------------------------------------------------------------------

    def set(self, other):
        """Set self members from another sppasPoint instance.

        :param other: (sppasPoint)

        """
        if isinstance(other, sppasPoint) is False:
            raise AnnDataTypeError(other, "sppasPoint")

        self.set_midpoint(other.get_midpoint())
        self.set_radius(other.get_radius())

    # -----------------------------------------------------------------------

    def is_point(self):
        """Overrides. Return True, because self represents a point."""
        return True

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of self."""
        return sppasPoint(self.__midpoint, self.__radius)

    # -----------------------------------------------------------------------

    def get_midpoint(self):
        """Return the midpoint value."""
        return self.__midpoint

    # -----------------------------------------------------------------------

    def set_midpoint(self, midpoint):
        """Set the midpoint value.

        In versions < 1.9.8, it was required that midpoint >= 0.
        Negative values are now accepted because some annotations are not
        properly synchronized and then some of them can be negative.

        :param midpoint: (float, int) is the new midpoint value.
        :raise: AnnDataTypeError

        """
        if isinstance(midpoint, (int, float, text_type, binary_type)) is False:
            raise AnnDataTypeError(midpoint, "float, int")

        if isinstance(midpoint, (int, text_type, binary_type)) is True:
            try:
                self.__midpoint = int(midpoint)
                if self.__midpoint < 0:
                    logging.warning('Midpoint is negative: {:d}'
                                    ''.format(midpoint))
                    # self.__midpoint = 0
                    # raise AnnDataNegValueError(midpoint)
                return
            except ValueError:
                pass  # will try with float...

        try:
            self.__midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float, int")

        if self.__midpoint < 0.:
            logging.warning('Midpoint is negative: {:f}'
                            ''.format(midpoint))

            #     self.__midpoint = 0.
        #     raise AnnDataNegValueError(midpoint)

    # -----------------------------------------------------------------------

    def get_radius(self):
        """Return the radius value (float or None)."""
        return self.__radius

    # -----------------------------------------------------------------------

    def set_radius(self, radius=None):
        """Fix the radius value, ie. the vagueness of the point.

        The midpoint value must be set first.

        :param radius: (float, int, None) the radius value
        :raise: AnnDataTypeError, AnnDataNegValueError

        """
        if radius is not None:
            if sppasPoint.check_types(self.__midpoint, radius) is False:
                raise AnnDataTypeError(radius, str(type(self.__midpoint)))

            if isinstance(radius, float):
                try:
                    radius = float(radius)
                    if radius < 0.:
                        raise AnnDataNegValueError(radius)
                except TypeError:
                    raise AnnDataTypeError(radius, "float")

            elif isinstance(radius, int):
                try:
                    radius = int(radius)
                    if radius < 0:
                        raise AnnDataNegValueError(radius)
                except TypeError:
                    raise AnnDataTypeError(radius, "int")

            if self.__midpoint < radius:
                radius = self.__midpoint

        self.__radius = radius

    # -----------------------------------------------------------------------

    def shift(self, delay):
        """Shift the point to a given delay.

        :param delay: (int, float) delay to shift midpoint
        :raise: AnnDataTypeError

        """
        if sppasPoint.check_types(self.__midpoint, delay) is False:
            raise AnnDataTypeError(delay, str(type(self.__midpoint)))

        self.__midpoint += delay

    # -----------------------------------------------------------------------

    def duration(self):
        """Overrides. Return the duration of the point.

        :returns: (sppasDuration) Duration and its vagueness.

        """
        if self.__radius is None:
            return sppasDuration(0., 0.)

        return sppasDuration(0., 2.0*self.get_radius())

    # -----------------------------------------------------------------------

    def is_int(self):
        """Return True if the value of the point is an integer."""
        return isinstance(self.__midpoint, int)

    # -----------------------------------------------------------------------

    def is_float(self):
        """Return True if the value of the point is a float."""
        return isinstance(self.__midpoint, float)

    # -----------------------------------------------------------------------

    @staticmethod
    def check_types(x, y):
        """True only if midpoint and radius are both of the same types.

        :param x: any kind of data
        :param y: any kind of data
        :returns: Boolean

        """
        return isinstance(x, type(y))

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        if self.__radius is None:
            return "sppasPoint: {!s:s}".format(self.__midpoint)
        return "sppasPoint: {!s:s}, {!s:s}".format(self.__midpoint,
                                                   self.__radius)

    # -----------------------------------------------------------------------

    def __str__(self):
        if self.__radius is None:
            return "{!s:s}".format(self.__midpoint)
        return "({!s:s}, {!s:s})".format(self.__midpoint, self.__radius)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Equal is required to use '=='.

        Used between 2 sppasPoint instances or
        between a sppasPoint and an other object representing time.
        This relationship takes into account the radius.

        :param other: (sppasPoint, float, int) the other point to compare

        """
        if isinstance(other, sppasPoint) is True:

            delta = abs(self.__midpoint - other.get_midpoint())
            radius = 0
            if self.__radius is not None:
                radius += self.__radius
            if other.get_radius() is not None:
                radius += other.get_radius()
            return delta <= radius

        if isinstance(other, (int, float)):
            if self.__radius is None:
                return self.__midpoint == other

            delta = abs(self.__midpoint - other)
            radius = self.__radius
            return delta <= radius

        return False

    # -----------------------------------------------------------------------

    def __lt__(self, other):
        """LowerThan is required to use '<'.

        Used between 2 sppasPoint instances
        or between a sppasPoint and an other time object.

        :param other: (sppasPoint, float, int) the other point to compare

        """
        if isinstance(other, sppasPoint) is True:
            return self != other and self.__midpoint < other.get_midpoint()

        return (self != other) and (self.__midpoint < other)

    # -----------------------------------------------------------------------

    def __gt__(self, other):
        """GreaterThan is required to use '>'.

        Used between 2 sppasPoint instances
        or between a sppasPoint and an other time object.

        :param other: (sppasPoint, float, int) the other point to compare

        """
        if isinstance(other, sppasPoint) is True:
            return self != other and self.__midpoint > other.get_midpoint()

        return (self != other) and (self.__midpoint > other)
