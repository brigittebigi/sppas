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
from sppas.src.videodata.manageroutputs import ManagerOutputs, os

# ---------------------------------------------------------------------------


class TestManagerOutputs(unittest.TestCase):

    def setUp(self):
        self.__mOptions = ManagerOptions("-person", usable=True, csv=True, video=True, folder=True)
        self.__mOptions.set_options("portrait", "crop", "circle", 640, 480)
        self.path = "../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4"
        self.__mOutputs = ManagerOutputs(self.path, 25, self.__mOptions)

    # ---------------------------------------------------------------------------

    def test_path(self):
        x, y = self.__mOutputs._ManagerOutputs__path_video(self.path)
        self.assertEqual(x, "C:\\Users\\Floroux\\Documents\\stage\\corpus\\Test_01_Celia_Brigitte\\")
        self.assertEqual(y, "montage_compressed")

    # ---------------------------------------------------------------------------

    def test_cfile_path(self):
        path = self.__mOutputs._ManagerOutputs__cfile_path()
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_*" + self.__mOptions.get_pattern() + ".csv"
        self.assertEqual(path, path2)

        path = self.__mOutputs._ManagerOutputs__cfile_path(1)
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_1" + self.__mOptions.get_pattern() + ".csv"
        self.assertEqual(path, path2)

        path = self.__mOutputs._ManagerOutputs__cfile_path(500)
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_500" + self.__mOptions.get_pattern() + ".csv"
        self.assertEqual(path, path2)

    # ---------------------------------------------------------------------------

    def test_vfile_path(self):
        path = self.__mOutputs._ManagerOutputs__vfile_path()
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_*" + self.__mOptions.get_pattern() + ".avi"
        self.assertEqual(path, path2)

        path = self.__mOutputs._ManagerOutputs__vfile_path(1)
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_1" + self.__mOptions.get_pattern() + ".avi"
        self.assertEqual(path, path2)

        path = self.__mOutputs._ManagerOutputs__vfile_path(500)
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_500" + self.__mOptions.get_pattern() + ".avi"
        self.assertEqual(path, path2)

    # ---------------------------------------------------------------------------

    def test_bfile_path(self):
        path = self.__mOutputs._ManagerOutputs__base_path()
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_*" + self.__mOptions.get_pattern() + "_usable.avi"
        self.assertEqual(path, path2)

        path = self.__mOutputs._ManagerOutputs__base_path(1)
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_1" + self.__mOptions.get_pattern() + "_usable.avi"
        self.assertEqual(path, path2)

        path = self.__mOutputs._ManagerOutputs__base_path(500)
        path2 = self.__mOutputs._ManagerOutputs__path + \
                self.__mOutputs._ManagerOutputs__video_name + "_500" + self.__mOptions.get_pattern() + "_usable.avi"
        self.assertEqual(path, path2)

    # ---------------------------------------------------------------------------

    def test_ffile_path(self):
        path = self.__mOutputs._ManagerOutputs__ffile_path()
        path2 = self.__mOutputs._ManagerOutputs__path + "*" + self.__mOptions.get_pattern() + os.path.sep
        self.assertEqual(path, path2)

        path = self.__mOutputs._ManagerOutputs__ffile_path(1)
        path2 = self.__mOutputs._ManagerOutputs__path + "1" + self.__mOptions.get_pattern() + os.path.sep
        self.assertEqual(path, path2)

        path = self.__mOutputs._ManagerOutputs__ffile_path(500)
        path2 = self.__mOutputs._ManagerOutputs__path + "500" + self.__mOptions.get_pattern() + os.path.sep
        self.assertEqual(path, path2)

    # ---------------------------------------------------------------------------

    def test_out_csv(self):
        with self.assertRaises(TypeError):
            self.__mOutputs._ManagerOutputs__out_csv(["a"])
        with self.assertRaises(ValueError):
            self.__mOutputs._ManagerOutputs__out_csv("a")

    # ---------------------------------------------------------------------------

    def test_out_video(self):
        with self.assertRaises(TypeError):
            self.__mOutputs._ManagerOutputs__out_video(["a"])
        with self.assertRaises(ValueError):
            self.__mOutputs._ManagerOutputs__out_csv("a")

    # ---------------------------------------------------------------------------

    def test_out_folder(self):
        with self.assertRaises(TypeError):
            self.__mOutputs._ManagerOutputs__out_folder(["a"])
        with self.assertRaises(ValueError):
            self.__mOutputs._ManagerOutputs__out_csv("a")

    # ---------------------------------------------------------------------------
