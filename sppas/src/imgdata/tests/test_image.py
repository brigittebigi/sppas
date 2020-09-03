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

from sppas.src.config import paths
from ..coordinates import sppasCoords
from ..image import sppasImage

# ---------------------------------------------------------------------------


class TestImage(unittest.TestCase):

    fn = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")

    def test_init(self):
        img = cv2.imread(TestImage.fn)
        self.assertEqual(len(img), 803)

        i1 = sppasImage(input_array=img)
        self.assertIsInstance(i1, numpy.ndarray)
        self.assertIsInstance(i1, sppasImage)
        self.assertEqual(len(img), len(i1))
        self.assertTrue(i1 == img)

        i2 = sppasImage(filename=TestImage.fn)
        self.assertIsInstance(i2, numpy.ndarray)
        self.assertIsInstance(i2, sppasImage)
        self.assertEqual(len(img), len(i2))
        self.assertTrue(i2 == img)

        with self.assertRaises(IOError):
            sppasImage(filename="toto.jpg")

    # -----------------------------------------------------------------------

    def test_crop(self):
        image = sppasImage(filename=TestImage.fn)
        cropped = image.icrop(sppasCoords(886, 222, 177, 189))
        # The cropped image is 189 rows and 177 columns of pixels
        self.assertEqual(189, len(cropped))
        for row in cropped:
            self.assertEqual(len(row), 177)

        fnc = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016-face.jpg")
        cv2.imwrite(fnc, cropped)
        self.assertTrue(os.path.exists(fnc))
        cropped_read = sppasImage(filename=fnc)
        os.remove(fnc)

        self.assertEqual(189, len(cropped_read))
        for row in cropped_read:
            self.assertEqual(len(row), 177)

        # test if same shape, same elements values
        self.assertTrue(numpy.array_equal(cropped, cropped_read))

        # test if broadcastable shape, same elements values
        self.assertTrue(numpy.array_equiv(cropped, cropped_read))

    # -----------------------------------------------------------------------

    def test_memory_usage(self):
        img = cv2.imread(TestImage.fn)
        i1 = sppasImage(input_array=img)
        self.assertEqual(1488, i1.width)
        self.assertEqual(803, i1.height)
        self.assertEqual(3, i1.channel)

        # Each (r,g,b) is 3 bytes (uint8)
        self.assertEqual(803*1488*3, i1.nbytes)

