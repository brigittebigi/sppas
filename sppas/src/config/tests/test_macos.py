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

    src.config.tests.test_installer_macos.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
from sppas.src.ui.term.textprogress import ProcessProgressTerminal
from sppas.src.config.installer import MacOs, Feature

# ---------------------------------------------------------------------------


class TestInstallerMacOs(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        p = ProcessProgressTerminal()
        self.__macos = MacOs(p)
        self.__feature = Feature()

    # ---------------------------------------------------------------------------

    def test_search_package(self):
        """Test if the method search_package from the class MacOs works well.

        """
        self.assertFalse(self.__macos.search_package("aaaa"))
        self.assertTrue(self.__macos.search_package("julius"))

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        """Test if the method install_package from the class MacOs works well.

        """
        self.__macos.install_package("aaaa")
        y = len(self.__macos.get_system_errors()) != 0
        self.assertTrue(y)

        self.__macos.install_package("julius")
        y = len(self.__macos.get_system_errors()) != 0
        self.assertTrue(y)

        with self.assertRaises(AssertionError):
            y = len(self.__macos.get_system_errors()) != 0
            self.assertFalse(y)

        self.__macos.set_system_errors("")

        self.__macos.install_package("julius")
        y = len(self.__macos.get_system_errors()) != 0
        self.assertTrue(y)

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        """Test if the method version_package from the class MacOs works well.

        """
        self.assertTrue(self.__macos.version_package("julius", ">;0.0"))
        self.assertTrue(self.__macos.version_package("flac", ">;0.0"))

        with self.assertRaises(IndexError):
            self.assertTrue(self.__macos.version_package("julius", "aaaa"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos.version_package("julius", "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos.version_package("julius", "=;4.2"))

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        """Test if the method need_update_package from the class MacOs works well.

        """
        x = "julius: stable 4.5 (bottled) \n" \
            "Two-pass large vocabulary continuous speech recognition engine \n" \
            "https://github.com/julius-speech/julius \n" \
            "/usr/local/Cellar/julius/4.5 (76 files, 3.6MB) * \n"

        y = "flac: stable 1.3.3 (bottled), HEAD \n" \
            "Free lossless audio codec \n" \
            "https://xiph.org/flac/ \n" \
            "/usr/local/Cellar/flac/1.3.3 (53 files, 2.4MB) * \n" \

        with self.assertRaises(IndexError):
            self.__macos.need_update_package("Bonjour", "aaaa")

        with self.assertRaises(IndexError):
            self.__macos.need_update_package(y, "aaaa")

        self.assertTrue(self.__macos.need_update_package(x, ">;4.6"))
        self.assertFalse(self.__macos.need_update_package(x, ">;4.0"))

        self.assertTrue(self.__macos.need_update_package(y, ">;1.4"))
        self.assertFalse(self.__macos.need_update_package(y, ">;1.0"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos.need_update_package(x, "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos.need_update_package(y, "=;1.2"))

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        """Test if the method update_package from the class MacOs works well.

        """
        self.__macos.update_package("aaaa")
        y = len(self.__macos.get_system_errors()) != 0
        self.assertTrue(y)

        self.__macos.update_package("julius")
        y = len(self.__macos.get_system_errors()) != 0
        self.assertTrue(y)

        with self.assertRaises(AssertionError):
            y = len(self.__macos.get_system_errors()) != 0
            self.assertFalse(y)

        self.__macos.set_system_errors("")

        self.__macos.update_package("julius")
        y = len(self.__macos.get_system_errors()) != 0
        self.assertFalse(y)

    # ---------------------------------------------------------------------------


test = TestInstallerMacOs()
test.setUp()
test.test_search_package()
test.test_install_package()
test.test_version_package()
test.test_need_update_package()
test.test_update_package()

