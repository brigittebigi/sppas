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

from sppas.src.imagedata.coordinates import Coordinates
from sppas.src.videodata.coordswriter import sppasVideoCoordsWriter
from sppas.src.videodata.personsbuffer import PersonsBuffer
from sppas.src.videodata.facetracking import FaceTracking

# ---------------------------------------------------------------------------


class TestCoordsWriter(unittest.TestCase):

    def setUp(self):
        self.__fTracker = FaceTracking()
        self.path = "../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4"
        self.__pBuffer = PersonsBuffer(self.path, 100, 0)
        self.__cw = sppasVideoCoordsWriter(self.path, 25, "person",
                                           usable=True, csv=True, video=True, folder=True)

    # ---------------------------------------------------------------------------

    def test_get_set_csv(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_csv()
        self.assertEqual(y, True)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_csv(False)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_csv()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_csv("")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_csv()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_csv(2)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_csv()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_video(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_video()
        self.assertEqual(y, True)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_video(False)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_video()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_video("")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_video()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_video(2)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_video()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_usable(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_usable()
        self.assertEqual(y, True)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_usable(False)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_usable()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_usable("")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_usable()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_usable(2)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_usable()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_folder(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_folder()
        self.assertEqual(y, True)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_folder(False)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_folder()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_folder("")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_folder()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_folder(2)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_folder()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_framing(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_framing()
        self.assertEqual(y, "None")

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("face")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_framing()
        self.assertEqual(y, "face")

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing(None)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_framing()
        self.assertEqual(y, "None")

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("portrait")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_framing()
        self.assertEqual(y, "portrait")

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_framing(2)

        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("aaaaaaaa")

    # ---------------------------------------------------------------------------

    def test_get_set_mode(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_mode()
        self.assertEqual(y, "None")

        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode("full")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_mode()
        self.assertEqual(y, "full")

        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode(None)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_mode()
        self.assertEqual(y, "None")

        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode("crop")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_mode()
        self.assertEqual(y, "crop")

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_mode(2)

        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_mode("aaaaaaaa")

    # ---------------------------------------------------------------------------

    def test_get_set_draw(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_draw()
        self.assertEqual(y, False)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_draw(False)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_draw()
        self.assertEqual(y, False)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_draw(True)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_draw()
        self.assertEqual(y, True)

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_draw(2)

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_draw("aaaaaaaa")

    # ---------------------------------------------------------------------------

    def test_get_set_width(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_width()
        self.assertEqual(y, -1)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_width(640)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_width()
        self.assertEqual(y, 640)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_width(500)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_width()
        self.assertEqual(y, 500)

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_width(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_width("aaaaaaaa")

        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_width(-2)

        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_width(15361)

    # ---------------------------------------------------------------------------

    def test_get_set_height(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_height()
        self.assertEqual(y, -1)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_height(640)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_height()
        self.assertEqual(y, 640)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_height(500)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_height()
        self.assertEqual(y, 500)

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_height(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_height("aaaaaaaa")

        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_height(-2)

        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_height(8641)

    # ---------------------------------------------------------------------------

    def test_get_set_pattern(self):
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_pattern()
        self.assertEqual(y, "person")

        self.__cw._sppasVideoCoordsWriter__mOptions.set_pattern("file")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_pattern()
        self.assertEqual(y, "file")

        self.__cw._sppasVideoCoordsWriter__mOptions.set_pattern("video")
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_pattern()
        self.assertEqual(y,"video")

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_pattern(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_pattern(2)

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_pattern(-2)

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__mOptions.set_pattern(2.0)

    # ---------------------------------------------------------------------------

    def test_write(self):
        self.__cw._sppasVideoCoordsWriter__mOptions.set_video(True)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_folder(True)

        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_video(), True)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_folder(), True)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing(None)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode(None)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_draw(False)

        if self.__cw._sppasVideoCoordsWriter__mOptions.get_framing() == "None" \
                and self.__cw._sppasVideoCoordsWriter__mOptions.get_mode() == "None" \
                and self.__cw._sppasVideoCoordsWriter__mOptions.get_draw() is False:
            self.__cw._sppasVideoCoordsWriter__mOptions.set_video(False)
            self.__cw._sppasVideoCoordsWriter__mOptions.set_folder(False)

        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_video(), False)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_folder(), False)

    # ---------------------------------------------------------------------------

    def test_verify_option(self):
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode("full")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "full")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "None")
        self.__cw._sppasVideoCoordsWriter__verify_options(self.__pBuffer)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "full")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "None")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode(None)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing(None)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("face")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "None")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "face")
        self.__cw._sppasVideoCoordsWriter__verify_options(self.__pBuffer)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "None")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "face")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode(None)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing(None)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode("crop")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "crop")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "None")
        self.__cw._sppasVideoCoordsWriter__verify_options(self.__pBuffer)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "crop")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "None")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode(None)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing(None)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("portrait")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "None")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "portrait")
        self.__cw._sppasVideoCoordsWriter__verify_options(self.__pBuffer)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "None")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "portrait")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode(None)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing(None)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("portrait")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode("crop")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "crop")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "portrait")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_draw(), False)
        self.__cw._sppasVideoCoordsWriter__verify_options(self.__pBuffer)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_video(), False)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode(None)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing(None)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("portrait")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode("crop")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_draw(True)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_mode(), "crop")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_framing(), "portrait")
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_draw(), True)
        self.assertEqual(self.__pBuffer.is_landmarked(), False)
        self.__cw._sppasVideoCoordsWriter__verify_options(self.__pBuffer)
        self.assertEqual(self.__cw._sppasVideoCoordsWriter__mOptions.get_video(), False)

    # ---------------------------------------------------------------------------

    def test_mode(self):
        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__process_image(2, "Hello", "a")

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__process_image(2, "Hello", ["a"])

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__process_image(2, "Hello", 2)

    # ---------------------------------------------------------------------------

    def test_draw_points(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__draw_points(2, "Hello", 2)

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__draw_points(2, "Hello", {"test": 1})

    # ---------------------------------------------------------------------------

    def test_adjust(self):
        self.__cw._sppasVideoCoordsWriter__mOptions.set_video(True)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_mode("crop")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_width(-1)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_height(-1)
        self.__cw._sppasVideoCoordsWriter__adjust(np.ndarray, Coordinates)
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_video()
        self.assertEqual(y, False)

    # ---------------------------------------------------------------------------

    def test_adjust_both(self):
        self.__cw._sppasVideoCoordsWriter__mOptions.set_width(640)
        self.__cw._sppasVideoCoordsWriter__mOptions.set_height(480)
        coord = Coordinates(120, 200, 400, 300)
        self.__cw._sppasVideoCoordsWriter__adjust_both(coord)
        x = coord.x
        self.assertEqual(x, 120)
        y = coord.y
        self.assertEqual(y, 200)
        w = coord.w
        self.assertEqual(w, 400)
        h = coord.h
        self.assertEqual(h, 300)

        coord = Coordinates(120, 200, 400, 350)
        self.__cw._sppasVideoCoordsWriter__adjust_both(coord)
        x = coord.x
        self.assertEqual(x, 87)
        y = coord.y
        self.assertEqual(y, 200)
        w = coord.w
        self.assertEqual(w, 466)
        h = coord.h
        self.assertEqual(h, 350)

    # ---------------------------------------------------------------------------

    def test_adjust_width(self):
        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("face")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_height(480)
        self.__cw._sppasVideoCoordsWriter__adjust_width()
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_width()
        self.assertEqual(y, 360)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("portrait")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_height(480)
        self.__cw._sppasVideoCoordsWriter__adjust_width()
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_width()
        self.assertEqual(y, 640)

    # ---------------------------------------------------------------------------

    def test_adjust_height(self):
        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("face")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_width(640)
        self.__cw._sppasVideoCoordsWriter__adjust_height()
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_height()
        self.assertEqual(y, 853)

        self.__cw._sppasVideoCoordsWriter__mOptions.set_framing("portrait")
        self.__cw._sppasVideoCoordsWriter__mOptions.set_width(640)
        self.__cw._sppasVideoCoordsWriter__adjust_height()
        y = self.__cw._sppasVideoCoordsWriter__mOptions.get_height()
        self.assertEqual(y, 480)

    # ---------------------------------------------------------------------------

