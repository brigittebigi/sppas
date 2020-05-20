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

    src.videodata.tests.test_coordswriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import numpy as np

from sppas.src.videodata.coordswriter import sppasImgCoordsWriter
from sppas.src.videodata.videobuffer import VideoBuffer
from sppas.src.videodata.facetracking import FaceTraking

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    def setUp(self):
        self.__fTracker = FaceTraking()
        self.__vBuffer = VideoBuffer("../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4", 20, 0)
        self.__cw = sppasImgCoordsWriter(csv=True, video=True, folder=True)

    # ---------------------------------------------------------------------------

    def test_get_csv(self):
        y = self.__cw.get_csv()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_video(self):
        y = self.__cw.get_video()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_folder(self):
        y = self.__cw.get_folder()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_portrait(self):
        y = self.__cw.get_portrait()
        self.assertEqual(y, False)

        self.__cw.set_portrait(True)
        y = self.__cw.get_portrait()
        self.assertEqual(y, True)

        self.__cw.set_portrait("")
        y = self.__cw.get_portrait()
        self.assertEqual(y, False)

        self.__cw.set_portrait(2)
        y = self.__cw.get_portrait()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_square(self):
        y = self.__cw.get_square()
        self.assertEqual(y, False)

        self.__cw.set_square(True)
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(x, True)
        self.assertEqual(y, False)
        self.assertEqual(z, False)

        self.__cw.set_square("")
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(x, False)
        self.assertEqual(y, False)
        self.assertEqual(z, False)

        self.__cw.set_square(2)
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(x, True)
        self.assertEqual(y, False)
        self.assertEqual(z, False)

    # ---------------------------------------------------------------------------

    def test_get_set_crop(self):
        y = self.__cw.get_crop()
        self.assertEqual(y, False)

        self.__cw.set_crop(True)
        w = self.__cw.get_video()
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(w, False)
        self.assertEqual(x, False)
        self.assertEqual(y, True)
        self.assertEqual(z, False)

        self.__cw.set_crop("")
        w = self.__cw.get_video()
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(w, False)
        self.assertEqual(x, False)
        self.assertEqual(y, False)
        self.assertEqual(z, False)

        self.__cw.set_crop(2)
        w = self.__cw.get_video()
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(w, False)
        self.assertEqual(x, False)
        self.assertEqual(y, True)
        self.assertEqual(z, False)

    # ---------------------------------------------------------------------------

    def test_get_set_crop_resize(self):
        y = self.__cw.get_crop_resize()
        self.assertEqual(y, False)

        self.__cw.set_crop_resize(True)
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(x, False)
        self.assertEqual(y, False)
        self.assertEqual(z, True)

        self.__cw.set_crop_resize("")
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(x, False)
        self.assertEqual(y, False)
        self.assertEqual(z, False)

        self.__cw.set_crop_resize(2)
        x = self.__cw.get_square()
        y = self.__cw.get_crop()
        z = self.__cw.get_crop_resize()
        self.assertEqual(x, False)
        self.assertEqual(y, False)
        self.assertEqual(z, True)

    # ---------------------------------------------------------------------------

    def test_browse_faces(self):
        self.__cw.set_square(True)
        self.__vBuffer.next()
        iterator = self.__vBuffer.__iter__()
        for i in range(0, self.__vBuffer.__len__()):
            self.__fTracker.append(next(iterator))
        self.__fTracker.apply()
        self.__cw.browse_faces(self.__vBuffer.get_overlap(), self.__fTracker.get_faces())

    # ---------------------------------------------------------------------------

    def test_portrait(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasImgCoordsWriter__portrait(2)

        with self.assertRaises(TypeError):
            self.__cw._sppasImgCoordsWriter__portrait("Hello")

        with self.assertRaises(TypeError):
            self.__cw._sppasImgCoordsWriter__portrait(["a", "b", 1, 2])

    # ---------------------------------------------------------------------------

    def test_mode(self):
        with self.assertRaises(ValueError):
            self.__cw._sppasImgCoordsWriter__mode(2, "Hello", "a")

        with self.assertRaises(TypeError):
            self.__cw._sppasImgCoordsWriter__out_csv(2, "Hello", ["a"])

        with self.assertRaises(TypeError):
            self.__cw._sppasImgCoordsWriter__mode(2, "Hello", 2)

    # ---------------------------------------------------------------------------

    def test_out_csv(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasImgCoordsWriter__out_csv(["a"])
        with self.assertRaises(ValueError):
            self.__cw._sppasImgCoordsWriter__out_csv("a")

    # ---------------------------------------------------------------------------

    def test_out_video(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasImgCoordsWriter__out_video(["a"])
        with self.assertRaises(ValueError):
            self.__cw._sppasImgCoordsWriter__out_csv("a")

    # ---------------------------------------------------------------------------

    def test_out_folder(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasImgCoordsWriter__out_folder(["a"])
        with self.assertRaises(ValueError):
            self.__cw._sppasImgCoordsWriter__out_csv("a")

    # ---------------------------------------------------------------------------

