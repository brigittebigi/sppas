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

    src.imgdata.image.py
    ~~~~~~~~~~~~~~~~~~~~

"""

import logging
import os
import cv2
import numpy

from sppas.src.exceptions import sppasIOError
from sppas.src.exceptions import sppasTypeError
from sppas.src.exceptions import sppasWriteError
from .coordinates import sppasCoords
from .imgdataexc import ImageReadError

# ----------------------------------------------------------------------------


class sppasImage(numpy.ndarray):
    """Manipulate images.

    :author:       Brigitte Bigi, Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :Example:
        >>> # explicit constructor to create an image
        >>> img1 = sppasImage(shape=(3,))
        >>> # read the image from a file
        >>> img2 = sppasImage(filename=os.path.join("some image file"))
        >>> # construct from an existing ndarray
        >>> img3 = sppasImage(input_array=img1)

    An image of width=320 and height=200 is represented by len(img)=200;
    each of these 200 rows contains 320 lists of [r,g,b] values.

    """

    def __new__(cls, shape=0, dtype=numpy.uint8, buffer=None, offset=0,
                strides=None, order=None, input_array=None, filename=None):
        """Return the instance of this class.

        Image is created either with the given input array, or with the
        given filename or with the given shape in order of priority.

        :param shape: (int)
        :param dtype: (type)
        :param buffer: (any)
        :param offset: (int)
        :param strides:
        :param order:
        :param input_array: (numpy.ndarray) Array representing an image
        :param filename: (str) Name of a file to read the image
        :raise: IOError

        :Example:
            >>> img1 = Image(shape=(3,), input_array=img, filename="name")
            >>> assert(img1 == img)

        """
        # Priority is given to the given already created array
        if input_array is not None:
            if isinstance(input_array, numpy.ndarray) is False:
                raise sppasTypeError(input_array, "sppasImage, numpy.ndarray")

        else:
            if filename is not None:
                if os.path.exists(filename) is False:
                    raise sppasIOError(filename)

                input_array = cv2.imread(filename)
                if input_array is None:
                    raise ImageReadError(filename)
            else:
                # Create the ndarray instance of our type, given the usual
                # ndarray input arguments. This will call the standard
                # ndarray constructor, but return an object of our type.
                input_array = numpy.ndarray.__new__(cls, shape, dtype, buffer, offset, strides, order)

        # Finally, we must return the newly created object.
        # Return a view of it in order to set it to the right type.
        return input_array.view(sppasImage)

    # -----------------------------------------------------------------------

    def icrop(self, coordinate):
        """Return a cropped part of the image to given coordinates.

        :param coordinate: (sppasCoords) crop to these x, y, w, h values.
        :return: (numpy.ndarray)

        """
        if isinstance(coordinate, sppasCoords) is False:
            raise sppasTypeError(coordinate, "sppasCoords")
        x1 = coordinate.x
        x2 = coordinate.x + coordinate.w
        y1 = coordinate.y
        y2 = coordinate.y + coordinate.h
        cropped = self[y1:y2, x1:x2]

        return sppasImage(input_array=cropped)

    # ------------------------------------------------------------------------

    def iresize(self, width=0, height=0):
        """Return a new array with the specified width and height.

        :param width: (int) The width to resize to (0=proportional to height)
        :param height: (int) The width to resize to (0=proportional to width)
        :return: (numpy.ndarray)

        """
        if len(self) == 0:
            return
        width = self.__to_dtype(width)
        height = self.__to_dtype(height)
        if width < 0:
            raise ValueError
        if height < 0:
            raise ValueError
        if width+height == 0:
            return self.copy()

        (h, w) = self.shape[:2]
        prop_width = prop_height = 0
        propw = proph = 1.
        if width != 0:
            prop_width = width
            propw = float(width) / float(w)
        if height != 0:
            prop_height = height
            proph = float(height) / float(h)
        if width == 0:
            prop_width = int(float(w) * proph)
        if height == 0:
            prop_height = int(float(h) * propw)

        image = cv2.resize(self, (prop_width, prop_height),
                           interpolation=cv2.INTER_AREA)
        return image

    # -----------------------------------------------------------------------

    def isurround(self, coords, color=(50, 100, 200), thickness=2, score=False):
        """Return a new array with a square surrounding all the given coords.

        :param coords: (List of sppasCoords) Areas to surround
        :param color: (int, int, int) Rectangle color or brightness (if grayscale image).
        :param thickness: (int) Thickness of lines that make up the rectangle. Negative values, like CV_FILLED , mean that the function has to draw a filled rectangle.
        :param score: (bool) Add the confidence score
        :return: (numpy.ndarray)

        """
        img = self.copy()
        for c in coords:
            if c.w > 0 and c.h > 0:
                # Draw the square and eventually the confidence inside the square
                text = ""
                if score is True and c.get_confidence() > 0.:
                    text = "{:.3f}".format(c.get_confidence())
                img.surround_coord(c, color, thickness, text)
            else:
                img.surround_point(c, color, thickness)
        return img

    # -----------------------------------------------------------------------

    def surround_coord(self, coord, color, thickness, text=""):
        """Add a square surrounding the given coordinates.

        :param coord: (sppasCoords) Area to surround
        :param color: (int, int, int) Rectangle color or brightness (if grayscale image).
        :param thickness: (int) Thickness of lines that make up the rectangle. Negative values, like CV_FILLED , mean that the function has to draw a filled rectangle.
        :param text: (str) Add text

        """
        if isinstance(coord, sppasCoords) is False:
            if isinstance(coord, (tuple, list)) and len(coord) >= 4:
                try:
                    coord = sppasCoords(coord[0], coord[1], coord[2], coord[3])
                except:
                    pass
        if isinstance(coord, sppasCoords) is False:
            sppasTypeError(coord, "sppasCoords")

        cv2.rectangle(self,
                      (coord.x, coord.y),
                      (coord.x + coord.w, coord.y + coord.h),
                      color,
                      thickness)
        if len(text) > 0:
            (h, w) = self.shape[:2]
            font_scale = (float(w * h)) / (1920. * 1080.)
            th = thickness//3
            text_size = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                        fontScale=font_scale*2, thickness=th)
            cv2.putText(self, text,
                        (coord.x + thickness, coord.y + thickness + text_size[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, color, th)

    # ----------------------------------------------------------------------------

    def surround_point(self, point, color, thickness):
        """Add a square surrounding the given point.

        :param point: (sppasCoords, list, tuple) (x,y) values to surround
        :param color: (int, int, int) Rectangle color or brightness (if grayscale image).
        :param thickness: (int) Thickness of lines that make up the rectangle. Negative values, like CV_FILLED , mean that the function has to draw a filled rectangle.

        """
        if isinstance(point, sppasCoords) is False:
            if isinstance(point, (tuple, list)) and len(point) >= 2:
                try:
                    point = sppasCoords(point[0], point[1])
                except:
                    pass
        if isinstance(point, sppasCoords) is False:
            sppasTypeError(point, "sppasCoords, tuple, list")

        x = point.x - (thickness * 2)
        y = point.y - (thickness * 2)
        w = h = thickness * 4

        cv2.rectangle(self, (x, y), (x + w, y + h), color, thickness)

    # ----------------------------------------------------------------------------

    def irotate(self, angle, center=None, scale=1.0):
        """Return a new array with the image rotated to the given angle.

        :param angle: (float) Rotation angle in degrees.
        :param center: (int) Center of the rotation in the source image.
        :param scale: (float) Isotropic scale factor.

        """
        # grab the dimensions of the image
        (h, w) = self.shape[:2]

        # if the center is None, initialize it as the center of the image
        if center is None:
            center = (w // 2, h // 2)

        # perform the rotation
        matrix = cv2.getRotationMatrix2D(center, angle, scale)
        return cv2.warpAffine(self, matrix, (w, h))

    # -----------------------------------------------------------------------

    def size(self):
        (h, w) = self.shape[:2]
        return w, h

    # -----------------------------------------------------------------------

    def write(self, filename):
        try:
            cv2.imwrite(filename, self)
        except cv2.error as e:
            logging.error(str(e))
            sppasWriteError(filename)

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

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for l1, l2 in zip(self, other):
            if len(l1) != len(l2):
                return False
            # the color of the pixel
            for c1, c2 in zip(l1, l2):
                if len(c1) != len(c2):
                    return False
                r1, g1, b1 = c1
                r2, g2, b2 = c2
                if r1 != r2 or g1 != g2 or b1 != b2:
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
