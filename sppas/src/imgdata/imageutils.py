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

    src.imgdata.imageutils.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import cv2
import numpy

from .coordinates import sppasCoords

# ----------------------------------------------------------------------------


def crops(image, coordinates):
    """Return a list of cropped images(numpy.ndarray objects).

    :param image: (numpy.ndarray) The image to be cropped.
    :param coordinates: (list) List of sppasCoords object.

    """
    list_cropped = list()
    for c in coordinates:
        if isinstance(c, sppasCoords) is False:
            raise TypeError
        cropped = image[c.get_y():c.get_y() + c.get_h(), c.get_x():c.get_x() + c.get_w()]
        list_cropped.append(cropped)
    return list_cropped

# ----------------------------------------------------------------------------


def surrond_square(image, coordinate, number):
    """Surround the elements of "image" with squares.

    :param image: (numpy.ndarray) The image to be processed.
    :param coordinate: (list) sppasCoords object.
    :param number: (int) value of R and G (the color of the square).
    :returns: An image(numpy.ndarray object).

    """
    number = int(number)
    if isinstance(number, int) is False:
        raise TypeError
    if isinstance(coordinate, sppasCoords) is False:
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

    :param coords: (sppasCoords) The coordinates of the face.
    :param coeff: (float) The coefficient of the scale.

    """
    if isinstance(coords, sppasCoords) is False:
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
    cos = numpy.abs(matrix[0, 0])
    sin = numpy.abs(matrix[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    matrix[0, 2] += (nW / 2) - cX
    matrix[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, matrix, (nW, nH))

# ----------------------------------------------------------------------------


def overlay(back_image, over_image, x, y, w, h):
    """Overlay an image on another one at given coordinates.

    :param back_image: (numpy.ndarray) The image to be overlaid.
    :param over_image: (numpy.ndarray) The image to tag with.
    :param x: (int)
    :param y: (int)
    :param w: (int)
    :param h: (int)
    :return: the background image tagged with the overlay image

    """
    if isinstance(back_image, sppasImage) is False:
        back_image = sppasImage(input_array=back_image)
    if isinstance(over_image, sppasImage) is False:
        over_image = sppasImage(input_array=over_image)

    # Get the shape of the background image
    h_im, w_im = back_image.shape[:2]

    # Resize the image to overlay to the appropriate size
    over = resize(over_image, w, h)
    cols, rows = over.shape[:2]
    x = int(x - rows * 0.6)

    # Change the values if the overlay image goes out of the bg image
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + rows > w_im:
        rows = w_im - x
    if y + cols > h_im:
        cols = h_im - y
    hand = over.crop(sppasCoords(0, 0, rows, cols))

    # Crop the part of the image where the overlay image takes place
    roi = back_image.crop(sppasCoords(x, y, rows, cols))

    # Now create a mask of overlay image and create its inverse mask also
    # If an error occurs with cv2.cvtColor it's because of the crop of the hand
    img2gray = cv2.cvtColor(hand, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    # Now black-out the area of overlay image in ROI
    img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

    # Take only region of background image from overlay image
    img2_fg = cv2.bitwise_and(hand, hand, mask=mask)

    # Put overlay image in ROI and modify the main image
    combined = cv2.add(img1_bg, img2_fg)
    back_image[y:y+cols, x:x+rows] = combined

    return back_image

