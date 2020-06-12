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

import cv2
import numpy as np

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


def draw_points(image, x, y, number):
    """Surround the elements of "image" with squares.

    :param image: (numpy.ndarray) The image to be processed.
    :param x: (list) The x-axis value for the draw.
    :param y: (list) The y-axis value for the draw.
    :param number: (int) value of R and G (the color of the draw).

    """
    x = int(x)
    if isinstance(x, int) is False:
        raise TypeError
    y = int(y)
    if isinstance(y, int) is False:
        raise TypeError

    # Draw circle on the coordinate
    cv2.circle(image, (x, y), 3, (number, number * 2, 200), -1)

# ----------------------------------------------------------------------------


def rotate(image, angle, center=None, scale=1.0):
    # grab the dimensions of the image
    (h, w) = image.shape[:2]

    # if the center is None, initialize it as the center of
    # the image
    if center is None:
        center = (w // 2, h // 2)

    # perform the rotation
    matrix = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, matrix, (w, h))

    # return the rotated image
    return rotated

# ----------------------------------------------------------------------------


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    matrix = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(matrix[0, 0])
    sin = np.abs(matrix[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    matrix[0, 2] += (nW / 2) - cX
    matrix[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, matrix, (nW, nH))

# ----------------------------------------------------------------------------


def add_image(image, hand, x, y, w, h):
    """Rotate the image.

    :param image: (numpy.ndarray) The image to be processed.
    :param hand: (numpy.ndarray) The image to be added.

    """
    # Get the shape of the background image
    h_im, w_im = image.shape[:2]

    # Resize the hand to the right size
    hand = resize(hand, w, h)
    cols, rows = hand.shape[:2]
    x = int(x - rows * 0.6)

    # If the hand will go out of the image
    # change the values
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + rows > w_im:
        rows = w_im - x
    if y + cols > h_im:
        cols = h_im - y
    hand = crop(hand, Coordinates(0, 0, rows, cols))

    # Crop the part of the image where the hand will take place
    roi = crop(image, Coordinates(x, y, rows, cols))

    # Now create a mask of hand and create its inverse mask also
    # If an error occure with cv2.cvtColor
    # it's because of the crop of the hand
    img2gray = cv2.cvtColor(hand, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    # Now black-out the area of logo in ROI
    img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

    # Take only region of logo from logo image.
    img2_fg = cv2.bitwise_and(hand, hand, mask=mask)

    # Put logo in ROI and modify the main image
    combined = cv2.add(img1_bg, img2_fg)
    image[y:y+cols, x:x+rows] = combined

    return image

# ----------------------------------------------------------------------------

