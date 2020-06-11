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

from sppas.src.videodata.manageroptions import ManagerOptions

# ---------------------------------------------------------------------------


class TestCoordsWriter(unittest.TestCase):

    def setUp(self):
        self.__mOptions = ManagerOptions("-person", usable=True, csv=True, video=True, folder=True)
        self.__mOptions.set_options(None, None, None, -1, -1)

    # --------------------------------------------------------------------------

    def test_get_set_csv(self):
        y = self.__mOptions.get_csv()
        self.assertEqual(y, True)

        self.__mOptions.set_csv(False)
        y = self.__mOptions.get_csv()
        self.assertEqual(y, False)

        self.__mOptions.set_csv("")
        y = self.__mOptions.get_csv()
        self.assertEqual(y, False)

        self.__mOptions.set_csv(2)
        y = self.__mOptions.get_csv()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_video(self):
        y = self.__mOptions.get_video()
        self.assertEqual(y, True)

        self.__mOptions.set_video(False)
        y = self.__mOptions.get_video()
        self.assertEqual(y, False)

        self.__mOptions.set_video("")
        y = self.__mOptions.get_video()
        self.assertEqual(y, False)

        self.__mOptions.set_video(2)
        y = self.__mOptions.get_video()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_usable(self):
        y = self.__mOptions.get_usable()
        self.assertEqual(y, True)

        self.__mOptions.set_usable(False)
        y = self.__mOptions.get_usable()
        self.assertEqual(y, False)

        self.__mOptions.set_usable("")
        y = self.__mOptions.get_usable()
        self.assertEqual(y, False)

        self.__mOptions.set_usable(2)
        y = self.__mOptions.get_usable()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_folder(self):
        y = self.__mOptions.get_folder()
        self.assertEqual(y, True)

        self.__mOptions.set_folder(False)
        y = self.__mOptions.get_folder()
        self.assertEqual(y, False)

        self.__mOptions.set_folder("")
        y = self.__mOptions.get_folder()
        self.assertEqual(y, False)

        self.__mOptions.set_folder(2)
        y = self.__mOptions.get_folder()
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_framing(self):
        y = self.__mOptions.get_framing()
        self.assertEqual(y, "None")

        self.__mOptions.set_framing("face")
        y = self.__mOptions.get_framing()
        self.assertEqual(y, "face")

        self.__mOptions.set_framing(None)
        y = self.__mOptions.get_framing()
        self.assertEqual(y, "None")

        self.__mOptions.set_framing("portrait")
        y = self.__mOptions.get_framing()
        self.assertEqual(y, "portrait")

        with self.assertRaises(TypeError):
            self.__mOptions.set_framing(2)

        with self.assertRaises(ValueError):
            self.__mOptions.set_framing("aaaaaaaa")

    # ---------------------------------------------------------------------------

    def test_get_set_mode(self):
        y = self.__mOptions.get_mode()
        self.assertEqual(y, "None")

        self.__mOptions.set_mode("full")
        y = self.__mOptions.get_mode()
        self.assertEqual(y, "full")

        self.__mOptions.set_mode(None)
        y = self.__mOptions.get_mode()
        self.assertEqual(y, "None")

        self.__mOptions.set_mode("crop")
        y = self.__mOptions.get_mode()
        self.assertEqual(y, "crop")

        with self.assertRaises(TypeError):
            self.__mOptions.set_mode(2)

        with self.assertRaises(ValueError):
            self.__mOptions.set_mode("aaaaaaaa")

    # ---------------------------------------------------------------------------

    def test_get_set_draw(self):
        y = self.__mOptions.get_draw()
        self.assertEqual(y, "None")

        self.__mOptions.set_draw("circle")
        y = self.__mOptions.get_draw()
        self.assertEqual(y, "circle")

        self.__mOptions.set_draw(None)
        y = self.__mOptions.get_draw()
        self.assertEqual(y, "None")

        self.__mOptions.set_draw("ellipse")
        y = self.__mOptions.get_draw()
        self.assertEqual(y, "ellipse")

        self.__mOptions.set_draw("square")
        y = self.__mOptions.get_draw()
        self.assertEqual(y, "square")

        with self.assertRaises(TypeError):
            self.__mOptions.set_draw(2)

        with self.assertRaises(ValueError):
            self.__mOptions.set_draw("aaaaaaaa")

    # ---------------------------------------------------------------------------

    def test_get_set_width(self):
        y = self.__mOptions.get_width()
        self.assertEqual(y, -1)

        self.__mOptions.set_width(640)
        y = self.__mOptions.get_width()
        self.assertEqual(y, 640)

        self.__mOptions.set_width(500)
        y = self.__mOptions.get_width()
        self.assertEqual(y, 500)

        with self.assertRaises(TypeError):
            self.__mOptions.set_width(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__mOptions.set_width("aaaaaaaa")

        with self.assertRaises(ValueError):
            self.__mOptions.set_width(-2)

        with self.assertRaises(ValueError):
            self.__mOptions.set_width(15361)

    # ---------------------------------------------------------------------------

    def test_get_set_height(self):
        y = self.__mOptions.get_height()
        self.assertEqual(y, -1)

        self.__mOptions.set_height(640)
        y = self.__mOptions.get_height()
        self.assertEqual(y, 640)

        self.__mOptions.set_height(500)
        y = self.__mOptions.get_height()
        self.assertEqual(y, 500)

        with self.assertRaises(TypeError):
            self.__mOptions.set_height(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__mOptions.set_height("aaaaaaaa")

        with self.assertRaises(ValueError):
            self.__mOptions.set_height(-2)

        with self.assertRaises(ValueError):
            self.__mOptions.set_height(8641)

    # ---------------------------------------------------------------------------

    def test_get_set_pattern(self):
        y = self.__mOptions.get_pattern()
        self.assertEqual(y, "-person")

        self.__mOptions.set_pattern("file")
        y = self.__mOptions.get_pattern()
        self.assertEqual(y, "file")

        self.__mOptions.set_pattern("video")
        y = self.__mOptions.get_pattern()
        self.assertEqual(y, "video")

        with self.assertRaises(TypeError):
            self.__mOptions.set_pattern(["a", "b", "c"])

        with self.assertRaises(TypeError):
            self.__mOptions.set_pattern(2)

        with self.assertRaises(TypeError):
            self.__mOptions.set_pattern(-2)

        with self.assertRaises(TypeError):
            self.__mOptions.set_pattern(2.0)

