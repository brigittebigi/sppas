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
import numpy as np

from sppas.src.videodata.videobuffer import VideoBuffer, ImageError

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    def setUp(self):

        self.__vBuffer = VideoBuffer("../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4", 100, 10)

    # ---------------------------------------------------------------------------

    def test_get_overalp(self):
        y = self.__vBuffer.get_overlap()
        self.assertEqual(y, 10)

    # ---------------------------------------------------------------------------

    def test_get_set_size(self):
        y = self.__vBuffer.get_size()
        self.assertEqual(y, 100)

        self.__vBuffer.set_size(1000)
        y = self.__vBuffer.get_size()
        self.assertEqual(y, 1000)

        self.__vBuffer.set_size(50)
        y = self.__vBuffer.get_size()
        self.assertEqual(y, 50)

        with self.assertRaises(TypeError):
            self.__vBuffer.set_size(["a"])

        with self.assertRaises(ValueError):
            self.__vBuffer.set_size("a")

        with self.assertRaises(ValueError):
            self.__vBuffer.set_size(1100)

    # ---------------------------------------------------------------------------

    def test_next_append(self):
        with self.assertRaises(ImageError):
            self.__vBuffer._VideoBuffer__next_append(["4", "3", "2", "1"])
        self.assertEqual(self.__vBuffer.__len__(), 0)

        self.__vBuffer.next()
        self.assertEqual(self.__vBuffer.__len__(), 100)

    # ---------------------------------------------------------------------------

    def test_prev_append(self):
        with self.assertRaises(ImageError):
            self.__vBuffer._VideoBuffer__prev_append(["4", "3", "2", "1"])

        self.assertEqual(self.__vBuffer.__len__(), 0)

        with self.assertRaises(ImageError):
            self.__vBuffer.previous()

        self.__vBuffer.next()
        self.__vBuffer.next()
        self.__vBuffer.previous()
        self.assertEqual(self.__vBuffer.__len__(), 100)

    # ---------------------------------------------------------------------------

    def test_previous(self):
        with self.assertRaises(ImageError):
            self.__vBuffer.previous()

    # ---------------------------------------------------------------------------

    def test_load_frames(self):
        with self.assertRaises(TypeError):
            self.__vBuffer._VideoBuffer__load_frames(["a"])

        with self.assertRaises(ValueError):
            self.__vBuffer._VideoBuffer__load_frames("a")

    # ---------------------------------------------------------------------------

    def test_read(self):
        with self.assertRaises(TypeError):
            self.__vBuffer.read(begining=[1, 2, 3, 4])

        with self.assertRaises(ValueError):
            self.__vBuffer.read(begining="aaaaa")

        with self.assertRaises(ValueError):
            self.__vBuffer.read(begining=-3)

        with self.assertRaises(ValueError):
            self.__vBuffer.read(begining=-3.0)

        with self.assertRaises(TypeError):
            self.__vBuffer.read(end=[1, 2, 3, 4])

        with self.assertRaises(ValueError):
            self.__vBuffer.read(end="aaaaa")

        with self.assertRaises(ValueError):
            self.__vBuffer.read(end=-3)

        with self.assertRaises(ValueError):
            self.__vBuffer.read(end=-3.0)

    # ---------------------------------------------------------------------------

    def test_len(self):
        self.__vBuffer.next()
        self.assertEqual(self.__vBuffer.__len__(), 100)

    # ---------------------------------------------------------------------------

    def test_str(self):
        self.__vBuffer.next()
        y = self.__vBuffer.__str__()
        print(y)
        self.assertEqual(len(y), 100)

    # ---------------------------------------------------------------------------

