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

    src.imagedata.tests.test_facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import os

from sppas.src.imagedata.facedetection import faceDetection, cv2
from sppas.src.config import sppasPathSettings


# ---------------------------------------------------------------------------


class TestFeature(unittest.TestCase):

    def setUp(self):
        self.__faceDetection = faceDetection()
        self.__proto = os.path.join(sppasPathSettings().resources, "video", "deploy.prototxt.txt")
        self.__model = os.path.join(sppasPathSettings().resources, "video",
                                    "res10_300x300_ssd_iter_140000.caffemodel")
        self.__net = cv2.dnn.readNetFromCaffe(self.__proto, self.__model)

    # ---------------------------------------------------------------------------

    def test_detect_faces(self):
        img = cv2.imread("../../../../../../trump.jpg")
        coordinates = self.__faceDetection.detect_faces(img, self.__net, 2)
        x = coordinates[0].get_x()
        self.assertEqual(x, 219)
        y = coordinates[0].get_y()
        self.assertEqual(y, 131)
        w = coordinates[0].get_w()
        self.assertEqual(w, 70)
        h = coordinates[0].get_h()
        self.assertEqual(h, 96)

        x = coordinates[1].get_x()
        self.assertEqual(x, 631)
        y = coordinates[1].get_y()
        self.assertEqual(y, 129)
        w = coordinates[1].get_w()
        self.assertEqual(w, 68)
        h = coordinates[1].get_h()
        self.assertEqual(h, 91)

        img = cv2.imread("../../../../../../iron_chic.jpg")
        coordinates = self.__faceDetection.detect_faces(img, self.__net, 3)
        x = coordinates[0].get_x()
        self.assertEqual(x, 260)
        y = coordinates[0].get_y()
        self.assertEqual(y, 59)
        w = coordinates[0].get_w()
        self.assertEqual(w, 173)
        h = coordinates[0].get_h()
        self.assertEqual(h, 220)

        x = coordinates[1].get_x()
        self.assertEqual(x, 135)
        y = coordinates[1].get_y()
        self.assertEqual(y, 127)
        w = coordinates[1].get_w()
        self.assertEqual(w, 126)
        h = coordinates[1].get_h()
        self.assertEqual(h, 196)

        x = coordinates[2].get_x()
        self.assertEqual(x, 6)
        y = coordinates[2].get_y()
        self.assertEqual(y, 154)
        w = coordinates[2].get_w()
        self.assertEqual(w, 133)
        h = coordinates[2].get_h()
        self.assertEqual(h, 197)

        img = cv2.imread("../../../../../../rooster.jpg")
        coordinates = self.__faceDetection.detect_faces(img, self.__net, 1)
        x = coordinates[0].get_x()
        self.assertEqual(x, 317)
        y = coordinates[0].get_y()
        self.assertEqual(y, 83)
        w = coordinates[0].get_w()
        self.assertEqual(w, 70)
        h = coordinates[0].get_h()
        self.assertEqual(h, 102)

        # ---------------------------------------------------------------------------

