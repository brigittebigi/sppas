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

    src.imagedata.imageutils.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import numpy as np
import cv2

from sppas.src.imagedata.coordinates import Coordinates


# ----------------------------------------------------------------------------


def crops(image, coordinates):
    """Return a list of cropped images(numpy.ndarray objects).

    :param image: (numpy.ndarray) The image to be cropped.
    :param coordinates: (list) List of Coordinates object.

    """
    list_cropped = list()
    for c in coordinates:
        if isinstance(c, Coordinates) is False:
            raise TypeError
        cropped = image[c.get_y():c.get_y() + c.get_h(), c.get_x():c.get_x() + c.get_w()]
        list_cropped.append(cropped)
    return list_cropped


# ----------------------------------------------------------------------------


def crop(image, coordinate):
    """Return a list of cropped images(numpy.ndarray objects).

    :param image: (numpy.ndarray) The image to be cropped.
    :param coordinate: (Coordinates) Coordinates object.

    """
    if isinstance(coordinate, Coordinates) is False:
        raise TypeError
    x1 = coordinate.x
    x2 = coordinate.x + coordinate.w
    y1 = coordinate.y
    y2 = coordinate.y + coordinate.h
    cropped = image[y1:y2, x1:x2]
    return cropped

# ----------------------------------------------------------------------------


def surrond_square(image, coordinate, number):
    """Surround the elements of "image" with squares.

    :param image: (numpy.ndarray) The image to be processed.
    :param coordinate: (list) Coordinates object.
    :param number: (int) value of R and G (the color of the square).
    :returns: An image(numpy.ndarray object).

    """
    number = int(number)
    if isinstance(number, int) is False:
        raise TypeError
    if isinstance(coordinate, Coordinates) is False:
        raise TypeError
    cv2.rectangle(image, (coordinate.get_x(), coordinate.get_y()), (coordinate.get_x() +
                                                                    coordinate.get_w(),
                                                                    coordinate.get_y() + coordinate.get_h()),
                  (number, number * 2, 200), 2)
    return image

# ----------------------------------------------------------------------------


def resize(image, width, height):
    """Return a list of cropped images(numpy.ndarray objects).

    :param image: (numpy.ndarray) The image to be resized.
    :param width: (int) The width you want to resize to.
    :param height: (int) The width you want to resize to.

    """
    if len(image) == 0:
        return
    if width < 0:
        raise ValueError
    if height < 0:
        raise ValueError
    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return image

# -----------------------------------------------------------------------


def portrait(coords, coeff=2.4):
    """Transform face coordinates to a portrait coordinates.

    :param coords: (Coordinates) The coordinates of the face.
    :param coeff: (float) The coefficient of the scale.

    """
    if isinstance(coords, Coordinates) is False:
        raise TypeError

    # Extend the image with a coeff equal to 2.4
    result = coords.scale(coeff)

    # Reframe the image on the face
    coords.shift(result, -30)

# ----------------------------------------------------------------------------


def draw_points(image, x, y, number, option="circle"):
    """Surround the elements of "image" with squares.

    :param image: (numpy.ndarray) The image to be processed.
    :param x: (list) The x-axis value for the draw.
    :param y: (list) The y-axis value for the draw.
    :param number: (int) value of R and G (the color of the draw).
    :param option: (str) The shape of the draw.

    """
    x = int(x)
    if isinstance(x, int) is False:
        raise TypeError
    y = int(y)
    if isinstance(y, int) is False:
        raise TypeError

    # If option == "circle" draw circle on the coordinate
    if option == "circle":
        cv2.circle(image, (x, y), 4, (number, number * 2, 200), -1)

    elif option == "ellipse":
        cv2.ellipse(image, (x, y), (5, 5), 0, 0, 360, (number, number * 2, 200), 2)

    elif option == "square":
        cv2.rectangle(image, (x-4, y-4), (x+4, y+4), (number, number * 2, 200), 2)

# ----------------------------------------------------------------------------

