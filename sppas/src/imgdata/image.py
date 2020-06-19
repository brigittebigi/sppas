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

import os
import cv2
import numpy

from sppas.src.exceptions import sppasIOError, sppasTypeError
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
        >>> img1 = Image(shape=(3,))
        >>> # read the image from a file
        >>> img2 = Image(filename=os.path.join("some image file"))
        >>> # construct from an existing ndarray
        >>> img3 = Image(input_array=img1)

    An image of width=320 and height=200 is represented by len(img)=200;
    each of these 200 rows contains 320 lists of [r,g,b] values.

    """

    def __new__(cls, shape=0, dtype=float, buffer=None, offset=0,
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

        return cropped

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

    def isurround(self, coords, color=(50, 100, 200), thickness=2, text=""):
        """Return a new array with a square surrounding the given coords.

        :param coords: (sppasCoords) Area to surround
        :param color: (int, int, int) Rectangle color or brightness (if grayscale image).
        :param thickness: (int) Thickness of lines that make up the rectangle. Negative values, like CV_FILLED , mean that the function has to draw a filled rectangle.
        :param text: (str) Add text
        :return: (numpy.ndarray)

        """
        if isinstance(coords, sppasCoords) is False:
            if isinstance(coords, list) and len(coords) >= 4:
                try:
                    coords = sppasCoords(coords[0], coords[1], coords[2], coords[3])
                except:
                    pass
        if isinstance(coords, sppasCoords) is False:
            sppasTypeError(coords, "sppasCoords")

        image = sppasImage(input_array=self)
        cv2.rectangle(image,
                      (coords.x, coords.y),
                      (coords.x + coords.w, coords.y + coords.h),
                      color,
                      thickness)
        if len(text) > 0:
            (h, w) = self.shape[:2]
            font_scale = (float(w * h)) / (1920. * 1080.)
            th = thickness//3
            text_size = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                        fontScale=font_scale*2, thickness=th)
            cv2.putText(image, text,
                        (coords.x + thickness, coords.y + thickness + text_size[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, color, th)

        return image

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
