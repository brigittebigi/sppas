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

import cv2

from sppas import error
from sppas.src.imagedata.coordinates import Coordinates

# ----------------------------------------------------------------------------


class ImageError(IndexError):
    """:ERROR 600:.

    Installation failed with error: {error}.

    """

    def __init__(self, error_msg):
        self.parameter = error(600) + \
                         (error(600, "globals")).format(error=error_msg)

    def __str__(self):
        return repr(self.parameter)

# ----------------------------------------------------------------------------


def croppe(image, coordinates):
    """Return a list of cropped images(numpy.ndarray objects).

    :param image: (numpy.ndarray) The image to be cropped.
    :param coordinates: (list) List of sppasCoordinates object.

    """
    list_cropped = list()
    for c in coordinates:
        if isinstance(c, Coordinates) is False:
            raise TypeError
        cropped = image[c.get_y():c.get_y() + c.get_h(), c.get_x():c.get_x() + c.get_w()]
        list_cropped.append(cropped)
    return list_cropped

# ----------------------------------------------------------------------------


def surrond_square(image, coordinates):
    """Surround the elements of "image" with squares.

    :param image: (numpy.ndarray) The image to be processed.
    :param coordinates: (list) List of sppasCoordinates object.
    :returns: An image(numpy.ndarray object).

    """
    for c in coordinates:
        if isinstance(c, Coordinates) is False:
            raise TypeError
        cv2.rectangle(image, (c.get_x(), c.get_y()), (c.get_x() + c.get_w(), c.get_y() + c.get_h()),
                      (0, 0, 255), 2)
    return image

