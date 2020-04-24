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

    src.config.tests.tests_installerDeps.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import sys

from sppas.src.config.support import sppasInstallerDeps, Deb, Windows, Dnf, Rpm, CygWin, MacOs

# ---------------------------------------------------------------------------


class TestInstallerDeps(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__installer_deps = sppasInstallerDeps()

    # ---------------------------------------------------------------------------

    def test_get_set_os(self):
        """Test if the methods get_os and set_os from the class sppasInstallerDeps works well.

        """
        self.setUp()

        if sys.platform == "win32":
            self.__installer_deps.set_os()
            y = self.__installer_deps.get_os()
            self.assertEqual(y, Windows)

        elif sys.platform == "linux":
            self.__installer_deps.set_os()
            y = self.__installer_deps.get_os()
            self.assertIn(y, [Deb, Dnf, Rpm])

        elif sys.platform == "darwin":
            self.__installer_deps.set_os()
            y = self.__installer_deps.get_os()
            self.assertEqual(y, MacOs)

        elif sys.platform == "cygwin":
            self.__installer_deps.set_os()
            y = self.__installer_deps.get_os()
            self.assertEqual(y, CygWin)

        else:
            with self.assertRaises(OSError):
                self.__installer_deps.set_os()

    # ---------------------------------------------------------------------------

    def test_get_set_features(self):
        """Test if the methods get_features and set_features from the class sppasInstallerDeps works well.

        """
        self.setUp()

        self.__installer_deps.set_features()
        y = self.__installer_deps.get_features()

        if self.__installer_deps.get_os() == Windows:
            self.assertEqual(y[0].get_id(), "wxpython")
            self.assertEqual(y[0].get_available(), True)
            self.assertEqual(y[0].get_cmd(), "nil")

            self.assertEqual(y[1].get_id(), "brew")
            self.assertEqual(y[1].get_available(), False)
            self.assertEqual(y[1].get_cmd(), "none")

            self.assertEqual(y[2].get_id(), "julius")
            self.assertEqual(y[2].get_available(), False)
            self.assertEqual(y[2].get_cmd(), "none")

        if self.__installer_deps.get_os() == MacOs:
            self.assertEqual(y[0].get_id(), "wxpython")
            self.assertEqual(y[0].get_available(), True)
            self.assertEqual(y[0].get_cmd(), "nil")

            self.assertEqual(y[1].get_id(), "brew")
            self.assertEqual(y[1].get_available(), True)
            self.assertEqual(y[1].get_cmd(), "/bin/bash -c \"$(curl -fsSL "
                                             "https://raw.githubusercontent.com/Homebrew/install/master/install.sh)\"")

            self.assertEqual(y[2].get_id(), "julius")
            self.assertEqual(y[2].get_available(), True)
            self.assertEqual(y[2].get_cmd(), "nil")

    # ---------------------------------------------------------------------------

    def test_get_feature_name(self):
        """Test if the methods get_feature_name from the class sppasInstallerDeps works well.

        """
        self.setUp()

        self.__installer_deps.set_features()
        y = self.__installer_deps.get_features_name()
        self.assertIsInstance(y, list)
        self.assertEqual(y, ["wxpython", "brew", "julius"])

    # ---------------------------------------------------------------------------

    def test_get_set_enable(self):
        """Test if the methods get_enable, set_enable and get_enables from the class sppasInstallerDeps works well.

        """
        self.setUp()

        self.__installer_deps.set_features()
        y = self.__installer_deps.get_features()

        a = self.__installer_deps.get_features()
        if self.__installer_deps.get_os() == Windows:
            for feature in a:
                self.__installer_deps.set_enable(feature)
                c = self.__installer_deps.get_enable(feature)
                self.assertIsInstance(c, bool)

            b = self.__installer_deps.get_enables()
            enables = "\n"
            for f in self.__installer_deps.get_features():
                enables += "(" + f.get_desc() + "," + f.get_id() + ") available = " + str(
                    f.get_available()) + "/ enable " \
                                         "= " + \
                           str(f.get_enable()) + "\n "
            self.assertEqual(b, enables)

            for feature in a:
                self.__installer_deps.unset_enable(feature)
                c = self.__installer_deps.get_enable(feature)
                self.assertIsInstance(c, bool)
                
            b = self.__installer_deps.get_enables()
            enables = "\n"
            for f in self.__installer_deps.get_features():
                enables += "(" + f.get_desc() + "," + f.get_id() + ") available = " + str(
                    f.get_available()) + "/ enable " \
                                         "= " + \
                           str(f.get_enable()) + "\n "
            self.assertEqual(b, enables)

        if self.__installer_deps.get_os() == MacOs:
            for feature in a:
                self.__installer_deps.set_enable(feature)
                c = self.__installer_deps.get_enable(feature)
                self.assertIsInstance(a, bool)
                self.assertEqual(c, True)
            b = self.__installer_deps.get_enables()
            self.assertEqual(b, {"Graphic Interface": True, "Package manager MacOs": True,
                                 "Automatic alignment": True})

            for feature in a:
                self.__installer_deps.unset_enable(feature)
                c = self.__installer_deps.get_enable(feature)
                self.assertIsInstance(a, bool)
                self.assertEqual(a, True)
            b = self.__installer_deps.get_enables()
            self.assertEqual(c, {"Graphic Interface": False, "Package manager MacOs": False,
                                 "Automatic alignment": False})

    # # ---------------------------------------------------------------------------
    #
    # def test_get_cmd_errors(self):
    #     """Test if the methods get_cmd_errors from the class sppasInstallerDeps works well.
    #
    #     """
    #     self.setUp()
    #
    #     y = self.__installer_deps.get_cmd_errors()
    #     self.assertIsInstance(y, str)
    #
    # # ---------------------------------------------------------------------------
    #
    # def test_get_system_errors(self):
    #     """Test if the methods get_system_errors from the class sppasInstallerDeps works well.
    #
    #     """
    #     self.setUp()
    #
    #     y = self.__installer_deps.get_system_errors()
    #     self.assertIsInstance(y, str)
    #
    # # ---------------------------------------------------------------------------
    #
    # def test_get_pypi_errors(self):
    #     """Test if the methods get_pypi_errors from the class sppasInstallerDeps works well.
    #
    #     """
    #     self.setUp()
    #
    #     y = self.__installer_deps.get_pypi_errors()
    #     self.assertIsInstance(y, str)

    # ---------------------------------------------------------------------------


test = TestInstallerDeps()
test.test_get_set_os()
test.test_get_set_features()
test.test_get_feature_name()
test.test_get_set_enable()
# test.test_get_cmd_errors()
# test.test_get_system_errors()
# test.test_get_pypi_errors()

















