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
from sppas.src.videodata.videobuffer import VideoBuffer
from sppas.src.videodata.facetracking import FaceTracking

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    def setUp(self):
        self.__fTracker = FaceTracking()
        self.path = "../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4"
        self.__vBuffer = VideoBuffer(self.path, 100, 0)
        self.__cw = sppasVideoCoordsWriter(self.path, 25, "person",
                                           csv=True, video=True, folder=True)

    # ---------------------------------------------------------------------------

    def test_path(self):
        x, y = self.__cw._sppasVideoCoordsWriter__path_video(self.path)
        self.assertEqual(x, "../../../../../corpus/Test_01_Celia_Brigitte/")
        self.assertEqual(y, "montage_compressed")

    # ---------------------------------------------------------------------------

    def test_cfile_path(self):
        path = self.__cw._sppasVideoCoordsWriter__cfile_path()
        path2 = self.__cw._sppasVideoCoordsWriter__path + \
                self.__cw._sppasVideoCoordsWriter__video_name + "_*-" + self.__cw.get_patron() + ".csv"
        self.assertEqual(path, path2)

        path = self.__cw._sppasVideoCoordsWriter__cfile_path(1)
        path2 = self.__cw._sppasVideoCoordsWriter__path + \
                self.__cw._sppasVideoCoordsWriter__video_name + "_1-" + self.__cw.get_patron() + ".csv"
        self.assertEqual(path, path2)

        path = self.__cw._sppasVideoCoordsWriter__cfile_path(500)
        path2 = self.__cw._sppasVideoCoordsWriter__path + \
                self.__cw._sppasVideoCoordsWriter__video_name + "_500-" + self.__cw.get_patron() + ".csv"
        self.assertEqual(path, path2)

    # ---------------------------------------------------------------------------

    def test_vfile_path(self):
        path = self.__cw._sppasVideoCoordsWriter__vfile_path()
        path2 = self.__cw._sppasVideoCoordsWriter__path + \
                self.__cw._sppasVideoCoordsWriter__video_name + "_*-" + self.__cw.get_patron() + ".avi"
        self.assertEqual(path, path2)

        path = self.__cw._sppasVideoCoordsWriter__vfile_path(1)
        path2 = self.__cw._sppasVideoCoordsWriter__path + \
                self.__cw._sppasVideoCoordsWriter__video_name + "_1-" + self.__cw.get_patron() + ".avi"
        self.assertEqual(path, path2)

        path = self.__cw._sppasVideoCoordsWriter__vfile_path(500)
        path2 = self.__cw._sppasVideoCoordsWriter__path + \
                self.__cw._sppasVideoCoordsWriter__video_name + "_500-" + self.__cw.get_patron() + ".avi"
        self.assertEqual(path, path2)

    # ---------------------------------------------------------------------------

    def test_ffile_path(self):
        path = self.__cw._sppasVideoCoordsWriter__ffile_path()
        path2 = self.__cw._sppasVideoCoordsWriter__path + "*-" + self.__cw.get_patron() + "/"
        self.assertEqual(path, path2)

        path = self.__cw._sppasVideoCoordsWriter__ffile_path(1)
        path2 = self.__cw._sppasVideoCoordsWriter__path + "1-" + self.__cw.get_patron() + "/"
        self.assertEqual(path, path2)

        path = self.__cw._sppasVideoCoordsWriter__ffile_path(500)
        path2 = self.__cw._sppasVideoCoordsWriter__path + "500-" + self.__cw.get_patron() + "/"
        self.assertEqual(path, path2)

    # ---------------------------------------------------------------------------

    def test_get_set_csv(self):
        y = self.__cw.get_csv()
        self.assertEqual(y, True)

        self.__cw.set_csv(False)
        y = self.__cw.get_csv()
        self.assertEqual(y, False)

        self.__cw.set_csv("")
        y = self.__cw.get_csv()
        self.assertEqual(y, False)

        self.__cw.set_csv(2)
        y = self.__cw.get_csv()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_video(self):
        y = self.__cw.get_video()
        self.assertEqual(y, True)

        self.__cw.set_video(False)
        y = self.__cw.get_video()
        self.assertEqual(y, False)

        self.__cw.set_video("")
        y = self.__cw.get_video()
        self.assertEqual(y, False)

        self.__cw.set_video(2)
        y = self.__cw.get_video()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_folder(self):
        y = self.__cw.get_folder()
        self.assertEqual(y, True)

        self.__cw.set_folder(False)
        y = self.__cw.get_folder()
        self.assertEqual(y, False)

        self.__cw.set_folder("")
        y = self.__cw.get_folder()
        self.assertEqual(y, False)

        self.__cw.set_folder(2)
        y = self.__cw.get_folder()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_framing(self):
        y = self.__cw.get_framing()
        self.assertEqual(y, None)

        self.__cw.set_framing("face")
        y = self.__cw.get_framing()
        self.assertEqual(y, "face")

        self.__cw.set_framing("portrait")
        y = self.__cw.get_framing()
        self.assertEqual(y, "portrait")

        with self.assertRaises(TypeError):
            self.__cw.set_framing(2)

        with self.assertRaises(ValueError):
            self.__cw.set_framing("aaaaaaaa")

    # ---------------------------------------------------------------------------

    def test_get_set_mode(self):
        y = self.__cw.get_mode()
        self.assertEqual(y, None)

        self.__cw.set_mode("full")
        y = self.__cw.get_mode()
        self.assertEqual(y, "full")

        self.__cw.set_mode("crop")
        y = self.__cw.get_mode()
        self.assertEqual(y, "crop")

        with self.assertRaises(TypeError):
            self.__cw.set_mode(2)

        with self.assertRaises(ValueError):
            self.__cw.set_mode("aaaaaaaa")

    # ---------------------------------------------------------------------------

    def test_get_set_width(self):
        y = self.__cw.get_width()
        self.assertEqual(y, None)

        self.__cw.set_width(640)
        y = self.__cw.get_width()
        self.assertEqual(y, 640)

        self.__cw.set_width(500)
        y = self.__cw.get_width()
        self.assertEqual(y, 500)

        with self.assertRaises(TypeError):
            self.__cw.set_width(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__cw.set_width("aaaaaaaa")

        with self.assertRaises(ValueError):
            self.__cw.set_width(-2)

        with self.assertRaises(ValueError):
            self.__cw.set_width(15361)

    # ---------------------------------------------------------------------------

    def test_get_set_height(self):
        y = self.__cw.get_height()
        self.assertEqual(y, None)

        self.__cw.set_height(640)
        y = self.__cw.get_height()
        self.assertEqual(y, 640)

        self.__cw.set_height(500)
        y = self.__cw.get_height()
        self.assertEqual(y, 500)

        with self.assertRaises(TypeError):
            self.__cw.set_height(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__cw.set_height("aaaaaaaa")

        with self.assertRaises(ValueError):
            self.__cw.set_height(-2)

        with self.assertRaises(ValueError):
            self.__cw.set_height(8641)

    # ---------------------------------------------------------------------------

    def test_get_set_patron(self):
        y = self.__cw.get_patron()
        self.assertEqual(y, "person")

        self.__cw.set_patron("file")
        y = self.__cw.get_patron()
        self.assertEqual(y, "file")

        self.__cw.set_patron("video")
        y = self.__cw.get_patron()
        self.assertEqual(y,"video")

        with self.assertRaises(TypeError):
            self.__cw.set_patron(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__cw.set_patron(2)

        with self.assertRaises(TypeError):
            self.__cw.set_patron(-2)

        with self.assertRaises(TypeError):
            self.__cw.set_patron(2.0)

    # ---------------------------------------------------------------------------

    def test_portrait(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__portrait(2)

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__portrait("Hello")

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__portrait(["a", "b", 1, 2])

    # ---------------------------------------------------------------------------

    def test_mode(self):
        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__process_image(2, "Hello", "a")

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__process_image(2, "Hello", ["a"])

        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__process_image(2, "Hello", 2)

    # ---------------------------------------------------------------------------

    def test_adjust(self):
        self.__cw.set_video(True)
        self.__cw.set_mode("crop")
        self.__cw.set_width(-1)
        self.__cw.set_height(-1)
        self.__cw._sppasVideoCoordsWriter__adjust(np.ndarray, Coordinates)
        y = self.__cw.get_video()
        self.assertEqual(y, False)

    # ---------------------------------------------------------------------------

    def test_adjust_both(self):
        self.__cw.set_width(640)
        self.__cw.set_height(480)
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
        self.__cw.set_framing("face")
        self.__cw.set_height(480)
        self.__cw._sppasVideoCoordsWriter__adjust_width()
        y = self.__cw.get_width()
        self.assertEqual(y, 360)

        self.__cw.set_framing("portrait")
        self.__cw.set_height(480)
        self.__cw._sppasVideoCoordsWriter__adjust_width()
        y = self.__cw.get_width()
        self.assertEqual(y, 640)

    # ---------------------------------------------------------------------------

    def test_adjust_height(self):
        self.__cw.set_framing("face")
        self.__cw.set_width(640)
        self.__cw._sppasVideoCoordsWriter__adjust_height()
        y = self.__cw.get_height()
        self.assertEqual(y, 853)

        self.__cw.set_framing("portrait")
        self.__cw.set_width(640)
        self.__cw._sppasVideoCoordsWriter__adjust_height()
        y = self.__cw.get_height()
        self.assertEqual(y, 480)

    # ---------------------------------------------------------------------------

    def test_out_csv(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__out_csv(["a"])
        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__out_csv("a")

    # ---------------------------------------------------------------------------

    def test_out_video(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__out_video(["a"])
        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__out_csv("a")

    # ---------------------------------------------------------------------------

    def test_out_folder(self):
        with self.assertRaises(TypeError):
            self.__cw._sppasVideoCoordsWriter__out_folder(["a"])
        with self.assertRaises(ValueError):
            self.__cw._sppasVideoCoordsWriter__out_csv("a")

    # ---------------------------------------------------------------------------

