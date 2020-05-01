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

    src.config.tests.test_installerDeps.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import sys

from sppas.src.config.support import sppasInstallerDeps, Deb, Windows, Dnf, Rpm, CygWin, MacOs
from sppas.src.ui.term.textprogress import ProcessProgressTerminal

# ---------------------------------------------------------------------------


class TestInstallerDeps(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        p = ProcessProgressTerminal()
        self.__installer_deps = sppasInstallerDeps(p)

    # ---------------------------------------------------------------------------

    def test_get_feat_ids(self):
        """Return the list of feature identifiers."""
        y = self.__installer_deps.get_feat_ids()
        self.assertEqual(y, ["wxpython", "brew", "julius"])

    # ---------------------------------------------------------------------------

    def test_get_feat_desc(self):
        """Return the description of the feature."""
        y = self.__installer_deps.get_feat_ids()
        self.assertEqual(self.__installer_deps.get_feat_desc(y[0]), "Graphic Interface")

        y = self.__installer_deps.get_feat_ids()
        self.assertEqual(self.__installer_deps.get_feat_desc(y[1]), "Package manager MacOs")

        y = self.__installer_deps.get_feat_ids()
        self.assertEqual(self.__installer_deps.get_feat_desc(y[2]), "Automatic alignment")

    # ---------------------------------------------------------------------------

    def test_get__set_os(self):
        """Return(get_os) and set(set_os) the OS of the computer."""
        if sys.platform == "win32":
            y = self.__installer_deps.get_os()
            self.assertEqual(y, Windows)

        elif sys.platform == "linux":
            y = self.__installer_deps.get_os()
            self.assertIn(y, [Deb, Dnf, Rpm])

        elif sys.platform == "darwin":
            y = self.__installer_deps.get_os()
            self.assertEqual(y, MacOs)

        elif sys.platform == "cygwin":
            y = self.__installer_deps.get_os()
            self.assertEqual(y, CygWin)

    # ---------------------------------------------------------------------------

    def test_get_enable(self):
        """Return True if the feature is enabled."""
        if self.__installer_deps.get_cfg_exist() is False:
            y = self.__installer_deps.get_feat_ids()
            self.assertEqual(self.__installer_deps.get_enable(y[0]), False)

            y = self.__installer_deps.get_feat_ids()
            self.assertEqual(self.__installer_deps.get_enable(y[1]), False)

            y = self.__installer_deps.get_feat_ids()
            self.assertEqual(self.__installer_deps.get_enable(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_get_available(self):
        """Return True if the feature is availabled."""
        y = self.__installer_deps.get_feat_ids()
        if sys.platform == "win32":
            self.assertEqual(self.__installer_deps.get_available(y[0]), True)
            self.assertEqual(self.__installer_deps.get_available(y[1]), False)
            self.assertEqual(self.__installer_deps.get_available(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_set_enable(self):
        """Make a feature enabled."""
        y = self.__installer_deps.get_feat_ids()
        self.__installer_deps.set_enable(y[0])
        self.assertEqual(self.__installer_deps.get_enable(y[0]), True)

        self.__installer_deps.set_enable(y[1])
        y = self.__installer_deps.get_feat_ids()
        self.assertEqual(self.__installer_deps.get_enable(y[1]), False)

        self.__installer_deps.set_enable(y[2])
        y = self.__installer_deps.get_feat_ids()
        self.assertEqual(self.__installer_deps.get_enable(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_unset_enable(self):
        """Make a feature disabled."""
        y = self.__installer_deps.get_feat_ids()
        self.__installer_deps.unset_enable(y[0])
        self.assertEqual(self.__installer_deps.get_enable(y[0]), False)

        self.__installer_deps.unset_enable(y[1])
        y = self.__installer_deps.get_feat_ids()
        self.assertEqual(self.__installer_deps.get_enable(y[1]), False)

        self.__installer_deps.unset_enable(y[2])
        y = self.__installer_deps.get_feat_ids()
        self.assertEqual(self.__installer_deps.get_enable(y[2]), False)

    # ---------------------------------------------------------------------------


test = TestInstallerDeps()
test.setUp()
test.test_get_feat_ids()
test.test_get_feat_desc()
test.test_get__set_os()
test.test_get_available()
test.test_get_enable()
test.test_set_enable()
test.test_unset_enable()

















