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

    src.imgdata.tests.test_facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest

from sppas.src.imgdata.facedetection import FaceDetection, sppasCoords, cv2


# ---------------------------------------------------------------------------


class TestFaceDetection(unittest.TestCase):

    def setUp(self):
        img = cv2.imread("../../../../../../trump.jpg")
        self.__faceDetection1 = FaceDetection(img)

        img = cv2.imread("../../../../../../iron_chic.jpg")
        self.__faceDetection2 = FaceDetection(img)

        img = cv2.imread("../../../../../../rooster.jpg")
        self.__faceDetection3 = FaceDetection(img)

    # ---------------------------------------------------------------------------

    def test_detect_all(self):
        self.__faceDetection1.detect_all()
        coordinates = self.__faceDetection1.get_all()
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

        self.__faceDetection2.detect_all()
        coordinates = self.__faceDetection2.get_all()
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

        self.__faceDetection3.detect_all()
        coordinates = self.__faceDetection3.get_all()
        x = coordinates[0].get_x()
        self.assertEqual(x, 317)
        y = coordinates[0].get_y()
        self.assertEqual(y, 83)
        w = coordinates[0].get_w()
        self.assertEqual(w, 70)
        h = coordinates[0].get_h()
        self.assertEqual(h, 102)

    # ---------------------------------------------------------------------------

    def test_detect_confidence(self):
        self.__faceDetection1.detect_confidence(0.9)
        coordinates = self.__faceDetection1.get_all()
        self.assertEqual(len(coordinates), 1)
        self.assertEqual(self.__faceDetection1.__len__(), 1)
        x = coordinates[0].get_x()
        self.assertEqual(x, 219)
        y = coordinates[0].get_y()
        self.assertEqual(y, 131)
        w = coordinates[0].get_w()
        self.assertEqual(w, 70)
        h = coordinates[0].get_h()
        self.assertEqual(h, 96)

        self.__faceDetection2.detect_confidence(0.9)
        coordinates = self.__faceDetection2.get_all()
        self.assertEqual(len(coordinates), 3)
        self.assertEqual(self.__faceDetection2.__len__(), 3)
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

        self.__faceDetection3.detect_confidence(0.9)
        coordinates = self.__faceDetection3.get_all()
        self.assertEqual(len(coordinates), 1)
        self.assertEqual(self.__faceDetection3.__len__(), 1)
        x = coordinates[0].get_x()
        self.assertEqual(x, 317)
        y = coordinates[0].get_y()
        self.assertEqual(y, 83)
        w = coordinates[0].get_w()
        self.assertEqual(w, 70)
        h = coordinates[0].get_h()
        self.assertEqual(h, 102)

    # ---------------------------------------------------------------------------

    def test_detect_number(self):
        self.__faceDetection1.detect_number(1)
        coordinates = self.__faceDetection1.get_all()
        self.assertEqual(len(coordinates), 1)
        self.assertEqual(self.__faceDetection1.__len__(), 1)
        x = coordinates[0].get_x()
        self.assertEqual(x, 219)
        y = coordinates[0].get_y()
        self.assertEqual(y, 131)
        w = coordinates[0].get_w()
        self.assertEqual(w, 70)
        h = coordinates[0].get_h()
        self.assertEqual(h, 96)

        self.__faceDetection2.detect_number(2)
        coordinates = self.__faceDetection2.get_all()
        self.assertEqual(len(coordinates), 2)
        self.assertEqual(self.__faceDetection2.__len__(), 2)
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

        self.__faceDetection3.detect_number(0)
        coordinates = self.__faceDetection3.get_all()
        self.assertEqual(len(coordinates), 0)
        self.assertEqual(self.__faceDetection3.__len__(), 0)
        with self.assertRaises(IndexError):
            coordinates[0].get_x()
        with self.assertRaises(IndexError):
            coordinates[0].get_y()
        with self.assertRaises(IndexError):
            coordinates[0].get_w()
        with self.assertRaises(IndexError):
            coordinates[0].get_h()

    # # ---------------------------------------------------------------------------
    #
    # def test_make_square(self):
    #     x, y, w, h = self.__faceDetection1.make_square(50, 50, 120, 200)
    #     self.assertEqual(x, 10)
    #     self.assertEqual(y, 50)
    #     self.assertEqual(w, 200)
    #     self.assertEqual(h, 200)
    #
    #     x, y, w, h = self.__faceDetection1.make_square(20, 50, 120, 200)
    #     self.assertEqual(x, 0)
    #     self.assertEqual(y, 50)
    #     self.assertEqual(w, 200)
    #     self.assertEqual(h, 200)
    #
    #     x, y, w, h = self.__faceDetection1.make_square(60, 60, 300, 200)
    #     self.assertEqual(x, 60)
    #     self.assertEqual(y, 10)
    #     self.assertEqual(w, 300)
    #     self.assertEqual(h, 300)
    #
    #     x, y, w, h = self.__faceDetection1.make_square(60, 50, 300, 200)
    #     self.assertEqual(x, 60)
    #     self.assertEqual(y, 0)
    #     self.assertEqual(w, 300)
    #     self.assertEqual(h, 300)

    # ---------------------------------------------------------------------------

    def test_get_all(self):
        self.__faceDetection1.detect_all()
        coordinates = self.__faceDetection1.get_all()

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

    # ---------------------------------------------------------------------------

    def test_get_best(self):
        self.__faceDetection1.detect_all()
        coordinates = self.__faceDetection1.get_best()
        self.assertIsInstance(coordinates, sppasCoords)

        x = coordinates.get_x()
        self.assertEqual(x, 219)
        y = coordinates.get_y()
        self.assertEqual(y, 131)
        w = coordinates.get_w()
        self.assertEqual(w, 70)
        h = coordinates.get_h()
        self.assertEqual(h, 96)

    # ---------------------------------------------------------------------------

    def test_get_number(self):
        self.__faceDetection1.detect_all()
        coordinates = self.__faceDetection1.get_nbest(2)
        self.assertEqual(len(coordinates), 2)
        self.assertEqual(self.__faceDetection1.__len__(), 2)

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

    # ---------------------------------------------------------------------------

    def test_contains(self):
        self.__faceDetection1.detect_all()
        c1 = sppasCoords(219, 131, 70, 96)
        self.assertTrue(self.__faceDetection1.__contains__(c1))
        c2 = sppasCoords(219, 131, 70, 200)
        self.assertFalse(self.__faceDetection1.__contains__(c2))

        with self.assertRaises(ValueError):
            c3 = 2
            self.assertTrue(self.__faceDetection1.__contains__(c3))

# ---------------------------------------------------------------------------

