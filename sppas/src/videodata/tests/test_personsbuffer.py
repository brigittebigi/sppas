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
from sppas.src.imagedata.coordinates import Coordinates

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    def setUp(self):

        self.__pBuffer = PersonsBuffer("../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4", 100, 10)

    # ---------------------------------------------------------------------------

    def test_get_add_person(self):
        self.__pBuffer.add_person(3)
        y = self.__pBuffer._PersonsBuffer__persons
        self.assertEqual(y, [[], [], []])

        self.__pBuffer.add_person()
        y = self.__pBuffer._PersonsBuffer__persons
        self.assertEqual(y, [[], [], [], []])

        self.__pBuffer.clear()

        self.__pBuffer.add_person()
        y = self.__pBuffer._PersonsBuffer__persons
        self.assertEqual(y, [[]])

    # ---------------------------------------------------------------------------

    def test_get_add_landmarks(self):
        self.__pBuffer.add_landmarks(3)
        y = self.__pBuffer._PersonsBuffer__landmarks
        self.assertEqual(y, [[], [], []])

        self.__pBuffer.add_landmarks()
        y = self.__pBuffer._PersonsBuffer__landmarks
        self.assertEqual(y, [[], [], [], []])

        self.__pBuffer.clear()

        self.__pBuffer.add_landmarks()
        y = self.__pBuffer._PersonsBuffer__landmarks
        self.assertEqual(y, [[]])

    # ---------------------------------------------------------------------------

    def test_get_add_coordinate(self):
        self.__pBuffer.add_person()
        self.__pBuffer.add_person()
        self.__pBuffer.add_person()

        x = Coordinates(50, 50, 100, 100)
        self.__pBuffer.add_coordinate(0, x)
        self.__pBuffer.add_coordinate(1, None)
        y = Coordinates(150, 150, 300, 300)
        self.__pBuffer.add_coordinate(2, y)

        with self.assertRaises(ValueError):
            self.__pBuffer.add_landmark("aaa", x)

        with self.assertRaises(TypeError):
            self.__pBuffer.add_landmark(["aaa", "aaa", "aaa"], x)

        z = self.__pBuffer._PersonsBuffer__persons
        self.assertEqual(z, [[x], [None], [y]])

    # ---------------------------------------------------------------------------

    def test_get_add_landmark(self):
        self.__pBuffer.add_landmarks()
        self.__pBuffer.add_landmarks()
        self.__pBuffer.add_landmarks()

        x = [(1, 2), (1, 2), (1, 2), (1, 2)]
        self.__pBuffer.add_landmark(0, x)
        self.__pBuffer.add_landmark(1, None)
        y = [(1, 2), (1, 2), (1, 2), (1, 2)]
        self.__pBuffer.add_landmark(2, y)

        with self.assertRaises(ValueError):
            self.__pBuffer.add_landmark("aaa", x)

        with self.assertRaises(TypeError):
            self.__pBuffer.add_landmark(["aaa", "aaa", "aaa"], x)

        z = self.__pBuffer._PersonsBuffer__landmarks
        self.assertEqual(z, [[x], [None], [y]])

    # ---------------------------------------------------------------------------

    def test_clear_len(self):
        self.__pBuffer.add_person(3)

        x = Coordinates(50, 50, 100, 100)
        self.__pBuffer.add_coordinate(0, x)
        self.__pBuffer.add_coordinate(1, None)
        y = Coordinates(150, 150, 300, 300)
        self.__pBuffer.add_coordinate(2, y)

        len = self.__pBuffer.nb_persons()
        self.assertEqual(len, 3)

        self.assertTrue(self.__pBuffer.is_tracked())

        self.__pBuffer.clear()

        self.__pBuffer.add_landmarks(4)

        x = [(1, 2), (1, 2), (1, 2), (1, 2)]
        self.__pBuffer.add_landmark(0, x)
        self.__pBuffer.add_landmark(1, None)
        y = [(1, 2), (1, 2), (1, 2), (1, 2)]
        self.__pBuffer.add_landmark(2, y)
        self.__pBuffer.add_landmark(3, None)

        len = self.__pBuffer.nb_persons()
        self.assertEqual(len, 4)

        self.assertFalse(self.__pBuffer.is_tracked())

        self.__pBuffer.clear()

        self.assertFalse(self.__pBuffer.is_tracked())

        len = self.__pBuffer.nb_persons()
        self.assertEqual(len, 0)

    # ---------------------------------------------------------------------------

