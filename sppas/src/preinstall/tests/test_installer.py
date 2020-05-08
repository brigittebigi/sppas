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

from sppas import sppasLogSetup
from sppas.src.preinstall.features import Features
from sppas.src.preinstall.installer import Installer
from sppas.src.preinstall.installer import InstallationError

# ---------------------------------------------------------------------------


class InstallerTest(Installer):
    """Manage the installation of external required or optional features. """
    def __init__(self):
        super(InstallerTest, self).__init__()
        self._features = Features(req="", cmdos="")

# ---------------------------------------------------------------------------


class TestInstaller(unittest.TestCase):

    def setUp(self):
        lgs = sppasLogSetup(0)
        lgs.stream_handler()
        self.__installer = InstallerTest()

    # ---------------------------------------------------------------------------

    def test_get_feat_ids(self):
        # Return the list of feature identifiers.
        y = self.__installer.get_fids()
        self.assertEqual(len(y), 3)
        self.assertTrue("wxpython" in y)
        self.assertTrue("brew" in y)
        self.assertTrue("julius" in y)

    # ---------------------------------------------------------------------------

    def test_enable(self):
        """Return True if the feature is enabled and/or set it."""
        y = self.__installer.get_fids()
        self.assertEqual(len(self.__installer.get_fids()), 3)
        self.assertEqual(self.__installer.enable(y[0]), True)

        y = self.__installer.get_fids()
        self.assertEqual(self.__installer.enable(y[1]), False)

        y = self.__installer.get_fids()
        self.assertEqual(self.__installer.enable(y[2]), True)

    # ---------------------------------------------------------------------------

    def test_available(self):
        """Return True if the feature is available and/or set it."""
        y = self.__installer.get_fids()
        self.assertEqual(self.__installer.available(y[0]), True)

        # y = self.__installer.get_fids()
        # self.assertEqual(self.__installer.available(y[1]), False)

        # y = self.__installer.get_fids()
        # self.assertEqual(self.__installer.available(y[2]), False)

    # ---------------------------------------------------------------------------

    def test_get_fids(self):
        y = self.__installer.get_fids()
        self.assertEqual(len(y), 3)

    # ---------------------------------------------------------------------------

    def test_get_set_progress(self):
        # Return the progression and/or add it.
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

    def test_install_pypis(self):
        # Manage the installation of pip packages.
        with self.assertRaises(InstallationError):
            self.__installer._Installer__install_pypi("wxpythonnnn")

        # Wont raise exception and wont return error message
        self.__installer._Installer__install_pypi("pip")

    # ---------------------------------------------------------------------------

    def test_search_pypi(self):
        self.assertTrue(self.__installer._Installer__search_pypi("pip"))
        self.assertFalse(self.__installer._Installer__search_pypi("wxpythonnnnnn"))
        with self.assertRaises(InstallationError):
            self.assertFalse(self.__installer._Installer__search_pypi(4))

    # ---------------------------------------------------------------------------

    def test_version_pypi(self):
        # Bug on MacOS but only in the test file not with the script "preinstall.py"
        # self.assertTrue(self.__installer._Installer__version_pypi("pip", ">;0.0"))
        self.assertFalse(self.__installer._Installer__version_pypi("numpy", ">;8.0"))

        self.assertFalse(self.__installer._Installer__version_pypi("pip", "aaaa"))
        self.assertFalse(self.__installer._Installer__version_pypi("pip", "<;4.2"))
        self.assertFalse(self.__installer._Installer__version_pypi("pip", "=;4.2"))

    # ---------------------------------------------------------------------------

    def test_need_update_pypi(self):
        x = "Name: wxPython \\r\\n" \
            "Version: 4.0.7.post2 \\r\\n" \
            "Summary: Cross platform GUI toolkit \\r\\n" \
            "Home-page: http://wxPython.org/ \\r\\n" \
            "Author: Robin Dunn \\r\\n" \

        y = "Name: numpy \\r\\n" \
            "Version: 1.18.3 \\r\\n" \
            "Summary: NumPy is the fundamental package for array computing with Python. \\r\\n" \
            "Home-page: https://www.numpy.org \\r\\n" \
            "Author: Travis E. Oliphant et al. \\r\\n"

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
        with self.assertRaises(InstallationError):
            self.__installer._Installer__update_pypi("wxpythonnnn")
        with self.assertRaises(InstallationError):
            self.assertFalse(self.__installer._Installer__update_pypi(4))

        self.__installer._Installer__update_pypi("pip")

    # ---------------------------------------------------------------------------

    def test_search_package(self):
        with self.assertRaises(NotImplementedError):
            self.__installer._search_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        with self.assertRaises(NotImplementedError):
            self.__installer._install_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        with self.assertRaises(NotImplementedError):
            self.__installer._version_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        with self.assertRaises(NotImplementedError):
            self.__installer._need_update_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        with self.assertRaises(NotImplementedError):
            self.__installer._update_package("aaaa", "4.0")
