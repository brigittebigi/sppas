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

    src.config.tests.test_macos.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
from sppas.src.ui.term.textprogress import ProcessProgressTerminal
from sppas.src.preinstall.installer import MacOsInstaller, InstallationError

# ---------------------------------------------------------------------------


class TestInstallerMacOs(unittest.TestCase):

    def setUp(self):
        """Initialisation."""
        self.__macos = MacOsInstaller()

    # ---------------------------------------------------------------------------

    def test_search_package(self):
        """Returns True if package is already installed."""
        self.assertFalse(self.__macos._search_package("juliuussssss"))
        self.assertFalse(self.__macos._search_package(4))

        # Only if brew is already install on the computer
        # self.assertTrue(self.__macos.search_package("brew"))

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        """Install package."""
        with self.assertRaises(InstallationError):
            self.assertFalse(self.__macos._install_package("juliuussssss"))
        with self.assertRaises(InstallationError):
            self.assertFalse(self.__macos._install_package(4))

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        """Returns True if package is up to date."""
        self.assertTrue(self.__macos._version_package("julius", ">;0.0"))
        self.assertTrue(self.__macos._version_package("flac", ">;0.0"))

        with self.assertRaises(IndexError):
            self.assertTrue(self.__macos._version_package("julius", "aaaa"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos._version_package("julius", "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos._version_package("julius", "=;4.2"))

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        """Return True if the package need to be update."""
        x = "julius: stable 4.5 (bottled) \\r\\n" \
            "Two-pass large vocabulary continuous speech recognition engine \\r\\n" \
            "https://github.com/julius-speech/julius \\r\\n" \
            "/usr/local/Cellar/julius/4.5 (76 files, 3.6MB) * \\r\\n"

        y = "flac: stable 1.3.3 (bottled), HEAD \\r\\n" \
            "Free lossless audio codec \\r\\n" \
            "https://xiph.org/flac/ \\r\\n" \
            "/usr/local/Cellar/flac/1.3.3 (53 files, 2.4MB) * \n" \

        with self.assertRaises(IndexError):
            self.__macos._need_update_package("Bonjour", "aaaa")

        with self.assertRaises(IndexError):
            self.__macos._need_update_package(y, "aaaa")

        self.assertTrue(self.__macos._need_update_package(x, ">;4.6"))
        self.assertFalse(self.__macos._need_update_package(x, ">;4.0"))

        self.assertTrue(self.__macos._need_update_package(y, ">;1.4"))
        self.assertFalse(self.__macos._need_update_package(y, ">;1.0"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos._need_update_package(x, "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos._need_update_package(y, "=;1.2"))

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        """Update package."""
        with self.assertRaises(InstallationError):
            self.assertFalse(self.__macos._update_package("wxpythonnnn", "4.0"))
        with self.assertRaises(InstallationError):
            self.assertFalse(self.__macos._update_package(4, "4.0"))

    # ---------------------------------------------------------------------------

