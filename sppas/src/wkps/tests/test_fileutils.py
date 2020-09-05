# -*- coding: UTF-8 -*-
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

    wkps.tests.test_fileutils.py
    ~~~~~~~~~~~~~~~~~~

"""

import os
import unittest

from sppas.src.config import paths
from ..fileutils import sppasDirUtils, sppasFileUtils


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFileUtils(unittest.TestCase):

    def setUp(self):
        self.sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")
        self.sample_2 = os.path.join(paths.samples, "samples-fra", "AG_éàç_0460.TextGrid")

    def test_set_random(self):
        sf = sppasFileUtils()
        f = os.path.basename(sf.set_random())
        self.assertTrue(f.startswith("sppas_tmp_"))
        f = os.path.basename(sf.set_random(add_today=False, add_pid=False))
        self.assertEqual(16, len(f))
        f = os.path.basename(sf.set_random(root="toto", add_today=False, add_pid=False))
        self.assertTrue(f.startswith("toto_"))
        self.assertEqual(11, len(f))

    def test_exists(self):
        sf = sppasFileUtils(self.sample_1)
        self.assertEqual(sf.exists(), self.sample_1)

    def test_format(self):
        sf = sppasFileUtils(" filename with some   whitespace ")
        f = sf.clear_whitespace()
        self.assertEqual("filename_with_some_whitespace", f)
        sf = sppasFileUtils(self.sample_2)
        f = sf.to_ascii()
        self.assertTrue(f.endswith("AG_____0460.TextGrid"))

# ---------------------------------------------------------------------------


class TestDirUtils(unittest.TestCase):

    def test_dir(self):
        # normal situation
        sd = sppasDirUtils(os.path.join(paths.samples, "samples-yue"))
        fl = sd.get_files("wav")
        self.assertEqual(len(fl), 1)

        # directory does not exists
        sd = sppasDirUtils("bad-directory-name")
        with self.assertRaises(IOError):
            sd.get_files("wav")

        # no directory
        sd = sppasDirUtils(None)
        self.assertEqual(sd.get_files("wav"), [])
