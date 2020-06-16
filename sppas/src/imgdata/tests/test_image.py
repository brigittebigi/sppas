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

    src.imgdata.tests.test_image.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import unittest
import cv2
import numpy

from ..coordinates import sppasCoords
from ..image import sppasImage

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestConfiguration(unittest.TestCase):

    def test_init(self):
        fn = os.path.join(DATA, "BrigitteBigi-Slovenie2016.jpg")
        img = cv2.imread(fn)
        self.assertEqual(len(img), 803)

        i1 = sppasImage(input_array=img)
        self.assertIsInstance(i1, numpy.ndarray)
        self.assertIsInstance(i1, sppasImage)
        self.assertEqual(len(img), len(i1))
        self.assertTrue(i1 == img)

        i2 = sppasImage(filename=fn)
        self.assertIsInstance(i2, numpy.ndarray)
        self.assertIsInstance(i2, sppasImage)
        self.assertEqual(len(img), len(i2))
        self.assertTrue(i2 == img)

        with self.assertRaises(IOError):
            sppasImage(filename="toto.jpg")

    # -----------------------------------------------------------------------

    def test_crop(self):
        fn = os.path.join(DATA, "BrigitteBigi-Slovenie2016.jpg")
        image = sppasImage(filename=fn)
        cropped = image.icrop(sppasCoords(886, 222, 177, 189))
        # The cropped image is 189 rows and 177 columns of pixels
        self.assertEqual(189, len(cropped))
        for row in cropped:
            self.assertEqual(len(row), 177)

        fnc = os.path.join(DATA, "BrigitteBigi-Slovenie2016-face.jpg")
        cv2.imwrite(fnc, cropped)


