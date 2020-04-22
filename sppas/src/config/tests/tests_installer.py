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

try:
    import configparser as cp
except ImportError:
    import ConfigParser as cp

from sppas.src.config.installer import Installer, Deb, Dnf, Rpm, Windows, CygWin, MacOs, Feature, paths


# ---------------------------------------------------------------------------


class TestInstaller(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__installer = Installer()
        self.__feature = Feature()

    # ---------------------------------------------------------------------------

    def tests_get_set_cfg_exist(self):
        """Test if the methods get_cfg_exist and set_cfg_exist from the class Installer works well.

        """
        self.setUp()

        self.__installer.set_cfg_exist(True)
        y = self.__installer.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__installer.set_cfg_exist(["a", "b", "c"])
        y = self.__installer.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__installer.set_cfg_exist({"1": "a", "2": "b", "3": "c"})
        y = self.__installer.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__installer.set_cfg_exist("")
        y = self.__installer.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, False)

        self.__installer.set_cfg_exist(4)
        y = self.__installer.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def tests_get_config_parser(self):
        """Test if the methods get_config_file from the class Installer works well.

        """
        self.setUp()

        y = self.__installer.get_config_parser()
        self.assertIsInstance(y, cp.ConfigParser)

    # ---------------------------------------------------------------------------

    def test_init_features(self):
        """Test if the method init_features from the class Installer works well.

        """

    # ---------------------------------------------------------------------------

    def test_set_features(self):
        """Test if the method init_features from the class Installer works well.

        """

    # ---------------------------------------------------------------------------

    def test_get_features_parser(self):
        """Test if the method get_features_parser from the class Installer works well.

        """
        y = self.__installer.get_features_parser()
        self.assertIsInstance(y, cp.ConfigParser)

    # ---------------------------------------------------------------------------

    def test_parse_depend(self):
        """Test if the method parse_depend from the class Installer works well.

        """
        y = self.__installer.parse_depend("aa:aa aa:aa aa:aa aa:aa")
        self.assertEqual(y, {'aa': 'aa'})

        y = self.__installer.parse_depend("aa:aa bb:bb cc:cc dd:dd")
        self.assertEqual(y, {'aa': 'aa', 'bb': 'bb', 'cc': 'cc', 'dd': 'dd'})

        with self.assertRaises(IndexError):
            self.__installer.parse_depend(4)

        with self.assertRaises(IndexError):
            self.__installer.parse_depend("Bonjour")

        with self.assertRaises(IndexError):
            self.__installer.parse_depend(4.0)

        with self.assertRaises(IndexError):
            self.__installer.parse_depend("aaaa aaaa aaaa aaaa")

        with self.assertRaises(IndexError):
            self.__installer.parse_depend(["aa", ":aa", "bb", ":bb", "cc", ":cc", "dd", ":dd"])

    # ---------------------------------------------------------------------------

    def test_get_set_pypi_errors(self):
        """Test if the method get_pypi_errors and set_pypi_errors from the class Installer works well.

        """
        self.__installer.set_pypi_errors("msg1")
        y = self.__installer.get_pypi_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "msg1")

        self.__installer.set_pypi_errors("2")
        y = self.__installer.get_pypi_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "msg12")

        self.__installer.set_pypi_errors("")
        y = self.__installer.get_pypi_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "")

        self.__installer.set_pypi_errors("nouveau msg")
        y = self.__installer.get_pypi_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "nouveau msg")

    # ---------------------------------------------------------------------------

    def test_get_set_system_errors(self):
        """Test if the method get_system_errors and Set_system_errors from the class Installer works well.

        """
        self.__installer.set_system_errors("msg1")
        y = self.__installer.get_system_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "msg1")

        self.__installer.set_system_errors("2")
        y = self.__installer.get_system_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "msg12")

        self.__installer.set_system_errors("")
        y = self.__installer.get_system_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "")

        self.__installer.set_system_errors("nouveau msg")
        y = self.__installer.get_system_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "nouveau msg")

    # ---------------------------------------------------------------------------

    def test_install_pypis(self):
        """Test if the method install_pypis from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__installer.install_pypis(4)

        with self.assertRaises(NotImplementedError):
            self.__installer.install_pypis("Hello")

        self.__feature.set_pypi({"azfegsdfgsdg": ">=0.0"})
        with self.assertRaises(NotImplementedError):
            self.__installer.install_pypis(self.__feature)

        self.__feature.set_pypi({"none": ">=0.0"})
        y = self.__feature.get_available()
        self.assertEqual(y, False)

    # ---------------------------------------------------------------------------

    def test_search_pypi(self):
        """Test if the method search_pypi from the class Installer works well.

        """
        self.setUp()

        self.assertFalse(self.__installer.search_pypi("wxpythonnnnnn"))
        self.assertFalse(self.__installer.search_pypi(4))

        self.assertTrue(self.__installer.search_pypi("wxpython"))

    # ---------------------------------------------------------------------------

    def test_install_pypi(self):
        """Test if the method install_pypi from the class Installer works well.

        """

    # ---------------------------------------------------------------------------

    def test_version_pypi(self):
        """Test if the method version_pypi from the class Installer works well.

        """
        self.setUp()

        self.assertTrue(self.__installer.version_pypi("pip",  ">=4.0"))
        self.assertTrue(self.__installer.version_pypi("wxpythonnnnnn", ">=4.0"))

    # ---------------------------------------------------------------------------

    def test_need_update_pypi(self):
        """Test if the method need_update_pypi from the class Installer works well.

        """

    # ---------------------------------------------------------------------------

    def test_update_pypi(self):
        """Test if the method update_pypi from the class Installer works well.

        """

    # ---------------------------------------------------------------------------

    def test_install_packages(self):
        """Test if the method install_packages from the class Installer works well.

        """
        self.setUp()

        self.__feature.set_packages({"azfegsdfgsdg": ">=0.0"})
        with self.assertRaises(NotImplementedError):
            self.__installer.install_packages(self.__feature)

        with self.assertRaises(NotImplementedError):
            self.__installer.install_packages(4)

        with self.assertRaises(NotImplementedError):
            self.__installer.install_packages("Hello")

        self.__feature.set_packages({"none": ">=0.0"})
        y = self.__feature.get_available()
        self.assertEqual(y, False)

