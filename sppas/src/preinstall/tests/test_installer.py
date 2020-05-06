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

    src.config.tests.test_installer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest

from sppas.src.ui.term.textprogress import ProcessProgressTerminal
from sppas.src.preinstall.installer import Installer, Windows
from sppas.src.preinstall.feature import Feature

# ---------------------------------------------------------------------------


class TestInstaller(unittest.TestCase):

    def setUp(self):
        """Initialisation."""
        p = ProcessProgressTerminal()
        # Two installers because the Installer do not have
        # its self._features instantiate.
        self.__installer = Installer(p)
        self.__installer2 = Installer(p)
        self.__feature = Feature("feature")
        self.__feature.set_available(True)
        self.__feature.set_enable(True)
        self.__feature.set_cmd("nil")
        self.__feature.set_packages({"4": "1"})
        self.__feature.set_pypi({"4": "1"})

        self.total_errors = ""
        self.errors = ""

    # ---------------------------------------------------------------------------

    def test_get_feat_ids(self):
        """Return the list of feature identifiers."""
        y = self.__installer.get_feat_ids()
        self.assertEqual(len(y), 3)
        self.assertTrue("wxpython" in y)
        self.assertTrue("brew" in y)
        self.assertTrue("julius" in y)

    # ---------------------------------------------------------------------------

    def test_enable(self):
        """Return True if the feature is enabled and/or set it."""
        y = self.__installer.get_feat_ids()
        self.assertEqual(len(self.__installer.get_feat_ids()), 3)
        self.assertEqual(self.__installer.enable(y[0]), False)

        y = self.__installer.get_feat_ids()
        self.assertEqual(self.__installer.enable(y[1]), False)

        y = self.__installer.get_feat_ids()
        self.assertEqual(self.__installer.enable(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_available(self):
        """Return True if the feature is available and/or set it."""
        y = self.__installer.get_feat_ids()
        self.assertEqual(self.__installer.available(y[0]), True)

        y = self.__installer.get_feat_ids()
        self.assertEqual(self.__installer.available(y[1]), False)

        y = self.__installer.get_feat_ids()
        self.assertEqual(self.__installer.available(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_description(self):
        """Return the description of the feature."""
        y = self.__installer.get_feat_ids()
        self.assertEqual(self.__installer.description(y[0]), "Graphic Interface")

        y = self.__installer.get_feat_ids()
        self.assertEqual(self.__installer.description(y[1]), "Package manager MacOs")

        y = self.__installer.get_feat_ids()
        self.assertEqual(self.__installer.description(y[2]), "Automatic alignment")

    # ---------------------------------------------------------------------------

    def test_get_set_progress(self):
        """Return the progression and/or set it."""
        installer = Installer()
        y = installer._Installer__get_set_progress(0.5)
        self.assertEqual(y, 0.5)

        y = installer._Installer__get_set_progress(10)
        self.assertEqual(y, 1.0)

        y = installer._Installer__get_set_progress(10)
        self.assertEqual(y, 1.0)

        with self.assertRaises(TypeError):
            installer._Installer__get_set_progress("10")

        with self.assertRaises(AssertionError):
            with self.assertRaises(AssertionError):
                installer._Installer__get_set_progress(False)

    # ---------------------------------------------------------------------------

    def test__set_total_errors(self):
        """Add an error message in total errors."""
        def set_total_errors(msg):
            if len(msg) != 0:
                string = str(msg)
                self.total_errors += string

        set_total_errors("An error")
        self.assertEqual(self.total_errors, "An error")

        set_total_errors("A new error")
        self.assertEqual(self.total_errors, "An errorA new error")

    # ---------------------------------------------------------------------------

    def test__set_errors(self):
        """Add an error message in total errors."""
        def set_errors(msg):
            if len(msg) == 0:
                self.errors = ""
            else:
                self.errors += msg

        set_errors("An error")
        self.assertEqual(self.errors, "An error")

        set_errors("A new error")
        self.assertEqual(self.errors, "An errorA new error")

        set_errors("")
        self.assertEqual(self.errors, "")

        set_errors("An error")
        self.assertEqual(self.errors, "An error")

    # ---------------------------------------------------------------------------

    def test_install_pypis(self):
        """Manage the installation of pip packages."""
        self.__installer._Installer__set_errors("")
        self.__installer._Installer__set_errors("An error")

        with self.assertRaises(NotImplementedError):
            self.__installer._Installer__install_pypis(4)

    # ---------------------------------------------------------------------------

    def test_search_pypi(self):
        """Returns True if package is already installed."""
        self.assertTrue(self.__installer._Installer__search_pypi("pip"))
        self.assertFalse(self.__installer._Installer__search_pypi("wxpythonnnnnn"))
        self.assertFalse(self.__installer._Installer__search_pypi(4))

    # ---------------------------------------------------------------------------

    def test_install_pypi(self):
        """Install package."""
        self.assertFalse(self.__installer._Installer__install_pypi("wxpythonnnn"))
        self.assertFalse(self.__installer._Installer__install_pypi(4))

    # ---------------------------------------------------------------------------

    def test_version_pypi(self):
        """Returns True if package is up to date."""
        self.assertTrue(self.__installer._Installer__version_pypi("pip", ">;0.0"))
        self.assertFalse(self.__installer._Installer__version_pypi("numpy", ">;8.0"))

        with self.assertRaises(IndexError):
            self.assertTrue(self.__installer._Installer__version_pypi("pip", "aaaa"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__installer._Installer__version_pypi("pip", "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__installer._Installer__version_pypi("pip", "=;4.2"))

    # ---------------------------------------------------------------------------

    def test_need_update_pypi(self):
        """Return True if the package need to be update."""
        x = "Name: wxPython \n" \
            "Version: 4.0.7.post2 \n" \
            "Summary: Cross platform GUI toolkit \n" \
            "Home-page: http://wxPython.org/ \n" \
            "Author: Robin Dunn \n" \

        y = "Name: numpy \n" \
            "Version: 1.18.3 \n" \
            "Summary: NumPy is the fundamental package for array computing with Python. \n" \
            "Home-page: https://www.numpy.org \n" \
            "Author: Travis E. Oliphant et al. \n"

        with self.assertRaises(IndexError):
            self.__installer._Installer__need_update_pypi("Bonjour", "aaaa")

        with self.assertRaises(IndexError):
            self.__installer._Installer__need_update_pypi(y, "aaaa")

        self.assertTrue(self.__installer._Installer__need_update_pypi(x, ">;4.2"))
        self.assertFalse(self.__installer._Installer__need_update_pypi(x, ">;4.0"))

        self.assertTrue(self.__installer._Installer__need_update_pypi(y, ">;1.2"))
        self.assertFalse(self.__installer._Installer__need_update_pypi(y, ">;1.0"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__installer._Installer__need_update_pypi(x, "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__installer._Installer__need_update_pypi(y, "=;1.2"))

    # ---------------------------------------------------------------------------

    def test_update_pypi(self):
        """Update package."""
        self.assertFalse(self.__installer._Installer__update_pypi("wxpythonnnn"))
        self.assertFalse(self.__installer._Installer__update_pypi(4))

    # ---------------------------------------------------------------------------

    def test_install_packages(self):
        """Manage installation of system packages."""
        self.__installer._Installer____set_errors("")
        self.__installer._Installer____set_errors("An error")

        with self.assertRaises(NotImplementedError):
            self.__installer._Installer__install_packages(4)

    # ---------------------------------------------------------------------------

    def test_search_package(self):
        """Test if the method search_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer2._Installer__search_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        """Test if the method install_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer2._install_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        """Test if the method version_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer2._version_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        """Test if the method need_update_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer2._need_update_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        """Test if the method update_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer2._update_package("aaaa")
