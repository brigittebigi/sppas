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

    src.config.tests.test_installer_windows.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
from sppas.src.ui.term.textprogress import ProcessProgressTerminal
from sppas.src.config.installer import Windows, Feature, cp

# ---------------------------------------------------------------------------


class TestInstallerWin(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        p = ProcessProgressTerminal()
        self.__windows = Windows(p)
        self.__feature = Feature()

    # ---------------------------------------------------------------------------

    def test_search_package(self):
        """Test if the method search_package from the class Windows works well.

        """
        self.assertTrue(self.__windows.search_package("aaaa"))

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        """Test if the method install_package from the class Windows works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__windows.install_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        """Test if the method version_package from the class Windows works well.

        """
        self.assertTrue(self.__windows.version_package("aaaa", "aaaa"))

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        """Test if the method need_update_package from the class Windows works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__windows.need_update_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        """Test if the method update_package from the class Windows works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__windows.update_package("aaaa")

    # ---------------------------------------------------------------------------


test = TestInstallerWin()
test.setUp()
test.test_search_package()
test.test_install_package()
test.test_version_package()
test.test_need_update_package()
test.test_update_package()

