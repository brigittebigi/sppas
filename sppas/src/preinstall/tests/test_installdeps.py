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

    src.config.tests.test_installdeps.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import sys

from sppas.src.preinstall.depsinstall import sppasInstallerDeps
from sppas.src.preinstall.installer import DebInstaller, WindowsInstaller, DnfInstaller, RpmInstaller, MacOsInstaller

# ---------------------------------------------------------------------------


class TestInstallerDeps(unittest.TestCase):

    def setUp(self):
        self.__installer_deps = sppasInstallerDeps()

    # ---------------------------------------------------------------------------

    def test_features_ids(self):
        """Return the list of feature identifiers."""
        y = self.__installer_deps.features_ids()
        self.assertGreaterEqual(len(y), 3)
        self.assertIn("wxpython", y)
        self.assertIn("brew", y)
        self.assertIn("julius", y)

    # ---------------------------------------------------------------------------

    def test_get_feat_desc(self):
        """Return the description of the feature."""
        y = self.__installer_deps.features_ids()
        self.assertGreaterEqual(len(y), 3)
        self.assertGreaterEqual(len(self.__installer_deps.description(y[0])), 14)
        self.assertGreaterEqual(len(self.__installer_deps.description(y[1])), 14)
        self.assertGreaterEqual(len(self.__installer_deps.description(y[2])), 14)

    # ---------------------------------------------------------------------------

    def test_get__set_os(self):
        """Return(get_os) and set(set_os) the OS of the computer."""
        if sys.platform == "win32":
            y = self.__installer_deps.os()
            self.assertEqual(y, WindowsInstaller)

        elif sys.platform == "linux":
            y = self.__installer_deps.os()
            self.assertIn(y, [DebInstaller, DnfInstaller, RpmInstaller])

        elif sys.platform == "darwin":
            y = self.__installer_deps.os()
            self.assertEqual(y, MacOsInstaller)

    # ---------------------------------------------------------------------------

    def test_enable(self):
        """Return True if the feature is enabled."""
        y = self.__installer_deps.features_ids()
        self.assertEqual(self.__installer_deps.enable(y[0]), False)

        y = self.__installer_deps.features_ids()
        self.assertEqual(self.__installer_deps.enable(y[1]), False)

        y = self.__installer_deps.features_ids()
        self.assertEqual(self.__installer_deps.enable(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_get_available(self):
        """Return True if the feature is available."""
        y = self.__installer_deps.features_ids()
        if sys.platform == "win32":
            self.assertEqual(self.__installer_deps.available(y[0]), True)
            self.assertEqual(self.__installer_deps.available(y[1]), False)
            self.assertEqual(self.__installer_deps.available(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_set_enable(self):
        """Make a feature enabled."""
        y = self.__installer_deps.features_ids()
        self.__installer_deps.enable(y[0], True)
        self.assertEqual(self.__installer_deps.enable(y[0]), True)

        if sys.platform != "darwin":
            self.__installer_deps.enable(y[1], True)
            y = self.__installer_deps.features_ids()
            self.assertEqual(self.__installer_deps.enable(y[1]), False)

        # self.__installer_deps.enable(y[2], True)
        # y = self.__installer_deps.features_ids()
        # self.assertEqual(self.__installer_deps.enable(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_unset_enable(self):
        """Make a feature disabled."""
        y = self.__installer_deps.features_ids()
        self.__installer_deps.enable(y[0], False)
        self.assertEqual(self.__installer_deps.enable(y[0]), False)

        self.__installer_deps.enable(y[1], False)
        y = self.__installer_deps.features_ids()
        self.assertEqual(self.__installer_deps.enable(y[1]), False)

        self.__installer_deps.enable(y[2], False)
        y = self.__installer_deps.features_ids()
        self.assertEqual(self.__installer_deps.enable(y[2]), False)


















