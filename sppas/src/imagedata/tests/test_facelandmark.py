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

    src.imagedata.tests.test_coordinates.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import cv2

from sppas.src.imagedata.facelandmark import FaceLandmark

# ---------------------------------------------------------------------------


class TestCoordinates(unittest.TestCase):

    def setUp(self):
        self.__fLandmark = FaceLandmark()
        self.__image = cv2.imread("../../../../../../video_test/image0.jpg")

    # ---------------------------------------------------------------------------

    def test_get_landmarks(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_landmarks()
        self.assertEqual(len(y), 68)
        self.assertEqual(len(self.__fLandmark), 68)

        self.assertEqual((119, 122), y[0])
        self.assertEqual((119, 141), y[1])
        self.assertEqual((121, 161), y[2])
        self.assertEqual((124, 181), y[3])
        self.assertEqual((131, 201), y[4])
        self.assertEqual((143, 216), y[5])
        self.assertEqual((161, 228), y[6])
        self.assertEqual((179, 238), y[7])
        self.assertEqual((201, 242), y[8])
        self.assertEqual((223, 240), y[9])
        self.assertEqual((243, 233), y[10])

    # ---------------------------------------------------------------------------

    def test_get_landmark(self):
        self.__fLandmark.landmarks(self.__image)

        y = self.__fLandmark.get_landmark(0)
        self.assertEqual((119, 122), y)

        y = self.__fLandmark.get_landmark(1)
        self.assertEqual((119, 141), y)

        y = self.__fLandmark.get_landmark(2)
        self.assertEqual((121, 161), y)

        y = self.__fLandmark.get_landmark(3)
        self.assertEqual((124, 181), y)

        y = self.__fLandmark.get_landmark(4)
        self.assertEqual((131, 201), y)

        y = self.__fLandmark.get_landmark(5)
        self.assertEqual((143, 216), y)

        y = self.__fLandmark.get_landmark(6)
        self.assertEqual((161, 228), y)

        y = self.__fLandmark.get_landmark(7)
        self.assertEqual((179, 238), y)

        y = self.__fLandmark.get_landmark(8)
        self.assertEqual((201, 242), y)

        y = self.__fLandmark.get_landmark(9)
        self.assertEqual((223, 240), y)

        y = self.__fLandmark.get_landmark(10)
        self.assertEqual((243, 233), y)

    # -----------------------------------------------------------------------

    def test_get_left_face(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_left_face()
        self.assertEqual(len(y), 8)

        self.assertEqual([(119, 122), (119, 141), (121, 161), (124, 181),
                          (131, 201), (143, 216), (161, 228), (179, 238)], y)

    # -----------------------------------------------------------------------

    def test_get_right_face(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_right_face()
        self.assertEqual(len(y), 9)

        self.assertEqual([(201, 242), (223, 240), (243, 233), (263, 223),
                          (277, 208), (286, 190), (291, 169), (294, 149), (295, 129)], y)

    # -----------------------------------------------------------------------

    def test_get_left_brow(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_left_brow()
        self.assertEqual(len(y), 5)

        self.assertEqual([(137, 94), (147, 82), (163, 76), (180, 78), (195, 86)], y)

    # -----------------------------------------------------------------------

    def test_get_right_brow(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_right_brow()
        self.assertEqual(len(y), 5)

        self.assertEqual([(222, 85), (238, 78), (257, 78), (272, 86), (279, 100)], y)

    # -----------------------------------------------------------------------

    def test_get_nose(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_nose()
        self.assertEqual(len(y), 9)

        self.assertEqual([(208, 105), (207, 116), (206, 128), (205, 141),
                          (187, 154), (195, 157), (205, 160), (214, 158), (223, 156)], y)

    # -----------------------------------------------------------------------

    def test_get_left_eyes(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_left_eyes()
        self.assertEqual(len(y), 6)

        self.assertEqual([(156, 111), (166, 106), (176, 106), (186, 111), (175, 112), (165, 113)], y)

    # -----------------------------------------------------------------------

    def test_get_right_eyes(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_right_eyes()
        self.assertEqual(len(y), 6)

        self.assertEqual([(229, 112), (240, 108), (250, 108), (258, 114), (250, 115), (240, 114)], y)

    # -----------------------------------------------------------------------

    def test_get_mouth(self):
        self.__fLandmark.landmarks(self.__image)
        y = self.__fLandmark.get_mouth()
        self.assertEqual(len(y), 20)

        self.assertEqual([(171, 186), (185, 182), (197, 178), (204, 181), (211, 179),
                          (223, 184), (237, 189), (222, 195), (210, 196), (202, 196),
                          (195, 195), (183, 194), (176, 186), (197, 186), (203, 187),
                          (211, 186), (232, 189), (210, 186), (203, 186), (196, 186)], y)

    # -----------------------------------------------------------------------

    def test_reset(self):
        self.__fLandmark.landmarks(self.__image)
        self.assertEqual(len(self.__fLandmark), 68)
        self.__fLandmark.reset()
        self.assertEqual(len(self.__fLandmark), 0)

    # -----------------------------------------------------------------------

    def test_contains(self):
        self.__fLandmark.landmarks(self.__image)
        self.assertEqual(len(self.__fLandmark), 68)
        self.assertTrue(self.__fLandmark.__contains__(171, 186))
        self.assertFalse(self.__fLandmark.__contains__(171, 200))

    # ---------------------------------------------------------------------------

