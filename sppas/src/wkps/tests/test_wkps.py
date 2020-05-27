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

    src.ui.tests.test_wkps.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

import os
import unittest

from sppas.src.config import paths
from sppas.src.wkps.sppasWkps import sppasWkps


class TestSppasWorkspaces(unittest.TestCase):

    def setUp(self):
        return

    # -----------------------------------------------------------------------

    def test_init(self):
        wkps = sppasWkps()

        # At least the Blank workspace is stored into the list,
        # and the existing workspaces on the disk.
        self.assertGreaterEqual(len(wkps), 1)
        self.assertEqual(wkps.index("Blank"), 0)

    # -----------------------------------------------------------------------

    def test_new(self):
        """Create a workspace and append it to the SPPAS workspaces."""
        wkps = sppasWkps()

        # Attempt to create a workspace with the Blank name
        with self.assertRaises(ValueError):  # WkpIdValueError
            wkps.new("Blank")

        # Really create a new workspace
        wlen = len(wkps)
        n = wkps.new("test")
        self.assertEqual(len(wkps), wlen + 1)
        fn = os.path.join(paths.wkps, n + ".wjson")
        self.assertTrue(os.path.exists(fn))

        # Attempt to create a workspace with the same name
        with self.assertRaises(ValueError):  # WkpIdValueError
            wkps.new(n)

        os.remove(fn)

    # -----------------------------------------------------------------------

    def test_delete(self):
        wkps = sppasWkps()
        wlen = len(wkps)

        # Delete a workspace
        fn = os.path.join(paths.wkps, "test.wjson")
        n = wkps.new("test")
        i = wkps.index(n)
        wkps.delete(i)
        self.assertFalse(os.path.exists(fn))

        self.assertEqual(len(wkps), wlen)

    # -----------------------------------------------------------------------

    def test_rename(self):
        """Create, rename and delete a workspace in wkps folder."""
        wkps = sppasWkps()

        with self.assertRaises(IndexError):  # WkpRenameBlankError
            wkps.rename(0, "renamed")

        n = wkps.new("test")

        # Rename the workspace
        i = wkps.index(n)
        wkps.rename(i, "renamed")
        fn = os.path.join(paths.wkps, "renamed.wjson")
        self.assertTrue(os.path.exists(fn))

        # Delete a workspace
        wkps.delete(i)
        self.assertFalse(os.path.exists(fn))


