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

    src.videodata.tests.test_videobuffer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest

from sppas.src.videodata.personsbuffer import PersonsBuffer
from sppas.src.imagedata.coordinates import Coordinates, ImageError

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    def setUp(self):

        self.__pBuffer = PersonsBuffer("../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4", 100, 10)

    # ---------------------------------------------------------------------------

    def test_get_add_person(self):
        self.__pBuffer.add_person()
        self.__pBuffer.add_person()
        self.__pBuffer.add_person()
        y = self.__pBuffer.get_persons()
        self.assertEqual(y, [[], [], []])

    # ---------------------------------------------------------------------------

    def test_get_add_landmarks(self):
        self.__pBuffer.add_landmarks()
        self.__pBuffer.add_landmarks()
        self.__pBuffer.add_landmarks()
        y = self.__pBuffer.get_landmarks()
        self.assertEqual(y, [[], [], []])

    # ---------------------------------------------------------------------------

    def test_get_add_coordinate(self):
        self.__pBuffer.add_person()
        self.__pBuffer.add_person()
        self.__pBuffer.add_person()

        w = Coordinates(50, 50, 100, 100)
        self.__pBuffer.add_coordinate(0, w)
        x = Coordinates(100, 100, 200, 200)
        self.__pBuffer.add_coordinate(1, x)
        y = Coordinates(150, 150, 300, 300)
        self.__pBuffer.add_coordinate(2, y)

        with self.assertRaises(ValueError):
            self.__pBuffer.add_landmark("aaa", w)

        with self.assertRaises(TypeError):
            self.__pBuffer.add_landmark(["aaa", "aaa", "aaa"], w)

        z = self.__pBuffer.get_persons()
        self.assertEqual(z, [[w], [x], [y]])

    # ---------------------------------------------------------------------------

    def test_get_add_landmark(self):
        self.__pBuffer.add_landmarks()
        self.__pBuffer.add_landmarks()
        self.__pBuffer.add_landmarks()

        w = {"1": (1, 2), "2": (1, 2), "3": (1, 2), "4": (1, 2)}
        self.__pBuffer.add_landmark(0, w)
        x = {"1": (1, 2), "2": (1, 2), "3": (1, 2), "4": (1, 2)}
        self.__pBuffer.add_landmark(1, x)
        y = {"1": (1, 2), "2": (1, 2), "3": (1, 2), "4": (1, 2)}
        self.__pBuffer.add_landmark(2, y)

        with self.assertRaises(ValueError):
            self.__pBuffer.add_landmark("aaa", w)

        with self.assertRaises(TypeError):
            self.__pBuffer.add_landmark(["aaa", "aaa", "aaa"], w)

        z = self.__pBuffer.get_landmarks()
        self.assertEqual(z, [[w], [x], [y]])

    # ---------------------------------------------------------------------------

    def test_clear_len(self):
        self.__pBuffer.add_person()
        self.__pBuffer.add_person()
        self.__pBuffer.add_person()

        w = Coordinates(50, 50, 100, 100)
        self.__pBuffer.add_coordinate(0, w)
        x = Coordinates(100, 100, 200, 200)
        self.__pBuffer.add_coordinate(1, x)
        y = Coordinates(150, 150, 300, 300)
        self.__pBuffer.add_coordinate(2, y)

        self.__pBuffer.add_landmarks()
        self.__pBuffer.add_landmarks()
        self.__pBuffer.add_landmarks()

        w = {"1": (1, 2), "2": (1, 2), "3": (1, 2), "4": (1, 2)}
        self.__pBuffer.add_landmark(0, w)
        x = {"1": (1, 2), "2": (1, 2), "3": (1, 2), "4": (1, 2)}
        self.__pBuffer.add_landmark(1, x)
        y = {"1": (1, 2), "2": (1, 2), "3": (1, 2), "4": (1, 2)}
        self.__pBuffer.add_landmark(2, y)

        len1 = self.__pBuffer.len_persons()
        len2 = self.__pBuffer.len_landmarks()
        self.assertEqual(len1, 3)
        self.assertEqual(len2, 3)

        self.__pBuffer.clear()

        len1 = self.__pBuffer.len_persons()
        len2 = self.__pBuffer.len_landmarks()
        self.assertEqual(len1, 0)
        self.assertEqual(len2, 0)

    # ---------------------------------------------------------------------------

