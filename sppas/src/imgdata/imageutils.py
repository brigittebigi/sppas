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
from .image import sppasImage

# ----------------------------------------------------------------------------


class sppasImageCompare(object):
    """Very basic scoring to compare images.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    How to quantify difference between two images?

    - Are images of the same area and dimension?
    - Is lightness/contrast the same? Is color information important?

    """

    def __init__(self, img1, img2):
        # if img1.shape != img2.shape:
        #    raise Exception("Can't compare images: shapes must be identical")
        self.__img1 = img1
        self.__img2 = img2

    # -----------------------------------------------------------------------

    def score(self):
        """Mix various comparison scores to return a single one."""
        # image dimensions
        s1 = self.compare_areas()
        s2 = self.compare_sizes()
        # image lightness and colors
        s3 = self.compare_with_mse()

        return (0.25 * s1) + (0.25 * s2) + (0.5 * s3)

    # -----------------------------------------------------------------------

    def compare_areas(self):
        """Return a score on how image areas are similar.

        :return: (float) value between 0. and 1.

        """
        w1, h1 = self.__img1.size()
        w2, h2 = self.__img2.size()
        area1 = w1 * h1
        area2 = w2 * h2
        min_area = min(area1, area2)
        max_area = max(area1, area2)
        if max_area < 2:
            return 0.

        return float(min_area) / float(max_area)

    # -----------------------------------------------------------------------

    def compare_sizes(self):
        """Return a score on how image sizes are similar.

        :return: (float) value between 0. and 1.

        """
        w1, h1 = self.__img1.size()
        w2, h2 = self.__img2.size()
        w_min = min(w1, w2)
        w_max = max(w1, w2)
        h_min = min(h1, h2)
        h_max = max(h1, h2)

        w_ratio = 0.
        if w_max > 2:
            w_ratio = float(w_min) / float(w_max)

        h_ratio = 0.
        if h_max > 2:
            h_ratio = float(h_min) / float(h_max)

        return (w_ratio + h_ratio) / 2.

    # -----------------------------------------------------------------------

    def compare_with_mse(self):
        r1 = sppasImageCompare(self.__img1, self.__img2.ired()).mse()
        r2 = sppasImageCompare(self.__img1.ired(), self.__img2).mse()
        b1 = sppasImageCompare(self.__img1, self.__img2.iblue()).mse()
        b2 = sppasImageCompare(self.__img1.iblue(), self.__img2).mse()
        g1 = sppasImageCompare(self.__img1, self.__img2.igreen()).mse()
        g2 = sppasImageCompare(self.__img1.igreen(), self.__img2).mse()
        total = r1+r2+b1+b2+g1+g2
        mini = min((r1, r2, b1, b2, g1, g2))
        if round(total, 2) == 0.:
            return 1.

        return min(1., max(0., 1. - (self.mse() / mini)))

    # -----------------------------------------------------------------------

    def mse(self):
        """Return the Mean Squared Error between the two images.

        :return: (float) The lower the error, the more similar the images are

        """
        # convert the images to grayscale
        img1_gray = self.__img1.igray()
        img2_gray = self.__img2.igray()

        # resize to get both images the same size
        w1, h1 = self.__img1.size()
        w2, h2 = self.__img2.size()
        img1 = img1_gray.iresize(width=min(w1, w2), height=min(h1, h2))
        img2 = img2_gray.iresize(width=min(w1, w2), height=min(h1, h2))

        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images
        err = numpy.sum((img1.astype("float") - img2.astype("float")) ** 2)
        err /= float(img1.shape[0] * img2.shape[1])

        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return float(err)

    # -----------------------------------------------------------------------

    def kld(self):
        """Return the Kullback-Leibler Distance between the two images.

        :return: (float) The lower the distance, the more similar the images are

        """
        # convert the images to grayscale
        img1_gray = self.__img1.igray()
        img2_gray = self.__img2.igray()

        # resize to get both images the same size
        w1, h1 = self.__img1.size()
        w2, h2 = self.__img2.size()
        img1 = img1_gray.iresize(width=min(w1, w2), height=min(h1, h2))
        img2 = img2_gray.iresize(width=min(w1, w2), height=min(h1, h2))

        # histograms for the images
        hist1, bin_edges1 = numpy.histogram(img1, bins=range(256))
        hist2, bin_edges2 = numpy.histogram(img2, bins=range(256))


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
    over = over_image.iresize(w, h)
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

