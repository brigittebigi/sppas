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

from sppas.src.config.installer import Installer, Deb, Dnf, Rpm, Windows, CygWin, MacOs, Feature, cp


# ---------------------------------------------------------------------------


class TestInstaller(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__installer = Installer()
        self.__windows = Windows()
        self.__feature = Feature()

    # ---------------------------------------------------------------------------

    def test_get_set_req(self):
        """Test if the methods get_req and set_req from the class Installer works well.

        """
        self.setUp()

        self.__installer.set_req("aaaa")
        y = self.__installer.get_req()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "aaaa")

        self.__installer.set_req(True)
        y = self.__installer.get_req()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "True")

        self.__installer.set_req(["a", "b", "c"])
        y = self.__installer.get_req()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "['a', 'b', 'c']")

        self.__installer.set_req({"1": "a", "2": "b", "3": "c"})
        y = self.__installer.get_req()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "{'1': 'a', '2': 'b', '3': 'c'}")

        self.__installer.set_req(4)
        y = self.__installer.get_req()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "4")

    # ---------------------------------------------------------------------------

    def test_get_set_cmdos(self):
        """Test if the methods get_cmd and set_cmd from the class Installer works well.

        """
        self.setUp()

        self.__installer.set_cmdos("aaaa")
        y = self.__installer.get_cmdos()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "aaaa")

        self.__installer.set_cmdos(True)
        y = self.__installer.get_cmdos()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "True")

        self.__installer.set_cmdos(["a", "b", "c"])
        y = self.__installer.get_cmdos()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "['a', 'b', 'c']")

        self.__installer.set_cmdos({"1": "a", "2": "b", "3": "c"})
        y = self.__installer.get_cmdos()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "{'1': 'a', '2': 'b', '3': 'c'}")

        self.__installer.set_cmdos(4)
        y = self.__installer.get_cmdos()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "4")

    # ---------------------------------------------------------------------------

    def test_get_set_cfg_exist(self):
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

    def test_get_config_parser(self):
        """Test if the methods get_config_file from the class Installer works well.

        """
        self.setUp()

        y = self.__installer.get_config_parser()
        self.assertIsInstance(y, cp.ConfigParser)

    # ---------------------------------------------------------------------------

    def test_init_features(self):
        """Test if the method init_features from the class Installer works well.

        """
        self.setUp()

        y = self.__installer.get_config_parser()
        y.read(self.__installer.get_feature_file())

        self.assertEqual(y.sections(), ["wxpython", "brew", "julius"])
        self.assertEqual(len(y.sections()), 3)

        self.assertEqual(y.get("wxpython", "desc"), "Graphic Interface")
        self.assertEqual(y.get("wxpython", "req_win"), "nil")
        self.assertEqual(y.get("wxpython", "req_pip"), "wxpython:>;4.0")
        self.assertEqual(y.get("wxpython", "cmd_win"), "nil")

        self.assertEqual(y.get("brew", "desc"), "Package manager MacOs")
        self.assertEqual(y.get("brew", "req_win"), "nil")
        self.assertEqual(y.get("brew", "req_pip"), "nil")
        self.assertEqual(y.get("brew", "cmd_win"), "none")

        self.assertEqual(y.get("julius", "desc"), "Automatic alignment")
        self.assertEqual(y.get("julius", "req_win"), "nil")
        self.assertEqual(y.get("julius", "req_pip"), "nil")
        self.assertEqual(y.get("julius", "cmd_win"), "none")

    # ---------------------------------------------------------------------------

    def test_set_features(self):
        """Test if the method set_features from the class Installer works well.

        """
        self.setUp()

        self.__installer.set_features()

        y = self.__installer.get_features()

        self.assertEqual(y[0].get_id(), "wxpython")
        self.assertEqual(y[0].get_desc(), "Graphic Interface")
        self.assertEqual(y[0].get_packages(), {'nil': '1'})
        self.assertEqual(y[0].get_pypi(), {'wxpython': '>;4.0'})
        self.assertEqual(y[0].get_cmd(), "nil")

        self.assertEqual(y[1].get_id(), "brew")
        self.assertEqual(y[1].get_desc(), "Package manager MacOs")
        self.assertEqual(y[1].get_packages(), {'nil': '1'})
        self.assertEqual(y[1].get_pypi(), {'nil': '1'})
        self.assertEqual(y[1].get_cmd(), "none")

        self.assertEqual(y[2].get_id(), "julius")
        self.assertEqual(y[2].get_desc(), "Automatic alignment")
        self.assertEqual(y[2].get_packages(), {'nil': '1'})
        self.assertEqual(y[2].get_pypi(), {'nil': '1'})
        self.assertEqual(y[2].get_cmd(), "none")

    # ---------------------------------------------------------------------------

    def test_parse_depend(self):
        """Test if the method parse_depend from the class Installer works well.

        """
        self.setUp()

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

    def test_get_features(self):
        """Test if the method get_features from the class Installer works well.

        """
        self.setUp()

        self.assertIsInstance(self.__installer.get_features(), list)

    # ---------------------------------------------------------------------------

    def test_get_features_parser(self):
        """Test if the method get_features_parser from the class Installer works well.

        """
        self.setUp()

        y = self.__installer.get_features_parser()
        self.assertIsInstance(y, cp.ConfigParser)

    # ---------------------------------------------------------------------------

    def test_get_set_cmd_errors(self):
        """Test if the method get_cmd_errors and set_cmd_errors from the class Installer works well.

        """
        self.setUp()

        self.__installer.set_cmd_errors("aaaa")
        y = self.__installer.get_cmd_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "aaaa")

        self.__installer.set_cmd_errors(True)
        y = self.__installer.get_cmd_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "True")

        self.__installer.set_cmd_errors(["a", "b", "c"])
        y = self.__installer.get_cmd_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "['a', 'b', 'c']")

        self.__installer.set_cmd_errors({"1": "a", "2": "b", "3": "c"})
        y = self.__installer.get_cmd_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "{'1': 'a', '2': 'b', '3': 'c'}")

        self.__installer.set_cmd_errors(4)
        y = self.__installer.get_cmd_errors()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "4")

    # ---------------------------------------------------------------------------

    def test_get_set_pypi_errors(self):
        """Test if the method get_pypi_errors and set_pypi_errors from the class Installer works well.

        """
        self.setUp()

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
        self.setUp()

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

    def test_install_cmds(self):
        """Test if the method install_cmds from the class Installer works well.

        """
        self.setUp()

        self.__installer.install_cmds("aaaaaaaaaa", self.__feature.get_id())
        y = len(self.__installer.get_cmd_errors()) != 0
        self.assertTrue(y)

        self.__installer.set_cmd_errors("")

        self.__installer.install_cmds("pip freeze", self.__feature.get_id())
        y = len(self.__installer.get_cmd_errors()) != 0
        self.assertFalse(y)

        with self.assertRaises(AssertionError):
            y = len(self.__installer.get_cmd_errors()) != 0
            self.assertTrue(y)

    # ---------------------------------------------------------------------------

    def test_install_cmd(self):
        """Test if the method install_cmd from the class Installer works well.

        """
        self.setUp()

        self.__feature.set_cmd("cmd_windows")

        with self.assertRaises(NotImplementedError):
            self.__installer.install_cmd(4)

        self.__feature.set_cmd("azfegsdfgsdg")
        with self.assertRaises(NotImplementedError):
            self.__installer.install_cmd(4)

    # ---------------------------------------------------------------------------

    def test_search_cmds(self):
        """Test if the method search_cmds from the class Installer works well.

        """
        self.setUp()

        self.assertFalse(self.__installer.search_cmds("wxpythonnnnnn"))
        self.assertFalse(self.__installer.search_cmds(4))

        self.assertTrue(self.__installer.search_cmds("pip"))

    # ---------------------------------------------------------------------------

    def test_install_pypis(self):
        """Test if the method install_pypis from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__installer.install_pypis(4)

        with self.assertRaises(NotImplementedError):
            self.__installer.install_pypis("Hello")

        self.__feature.set_pypi({"azfegsdfgsdg": ">;0.0"})
        with self.assertRaises(NotImplementedError):
            self.__installer.install_pypis(self.__feature)
        self.assertEqual(self.__feature.get_enable(), False)

    # ---------------------------------------------------------------------------

    def test_search_pypi(self):
        """Test if the method search_pypi from the class Installer works well.

        """
        self.setUp()

        self.assertFalse(self.__installer.search_pypi("wxpythonnnnnn"))
        self.assertFalse(self.__installer.search_pypi(4))

        self.assertTrue(self.__installer.search_pypi("pip"))

    # ---------------------------------------------------------------------------

    def test_install_pypi(self):
        """Test if the method install_pypi from the class Installer works well.

        """
        self.setUp()

        self.__installer.install_pypi("wxpythonnnn")
        y = len(self.__installer.get_pypi_errors()) != 0
        self.assertTrue(y)

        self.__installer.install_pypi("wxpython")
        y = len(self.__installer.get_pypi_errors()) != 0
        self.assertTrue(y)

        with self.assertRaises(AssertionError):
            y = len(self.__installer.get_pypi_errors()) != 0
            self.assertFalse(y)

        self.__installer.set_pypi_errors("")

        self.__installer.install_pypi("wxpython")
        y = len(self.__installer.get_pypi_errors()) != 0
        self.assertFalse(y)

    # ---------------------------------------------------------------------------

    def test_version_pypi(self):
        """Test if the method version_pypi from the class Installer works well.

        """
        self.setUp()

        self.assertTrue(self.__installer.version_pypi("pip", ">;0.0"))
        self.assertTrue(self.__installer.version_pypi("wxpythonnnnnn", ">;4.0"))
        self.assertFalse(self.__installer.version_pypi("numpy", ">;8.0"))

        with self.assertRaises(IndexError):
            self.assertTrue(self.__installer.version_pypi("pip", "aaaa"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__installer.version_pypi("pip", "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__installer.version_pypi("pip", "=;4.2"))

    # ---------------------------------------------------------------------------

    def test_need_update_pypi(self):
        """Test if the method need_update_pypi from the class Installer works well.

        """
        self.setUp()

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
            self.__installer.need_update_pypi("Bonjour", "aaaa")

        with self.assertRaises(IndexError):
            self.__installer.need_update_pypi(y, "aaaa")

        self.assertTrue(self.__installer.need_update_pypi(x, ">;4.2"))
        self.assertFalse(self.__installer.need_update_pypi(x, ">;4.0"))

        self.assertTrue(self.__installer.need_update_pypi(y, ">;1.2"))
        self.assertFalse(self.__installer.need_update_pypi(y, ">;1.0"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__installer.need_update_pypi(x, "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__installer.need_update_pypi(y, "=;1.2"))

    # ---------------------------------------------------------------------------

    def test_update_pypi(self):
        """Test if the method update_pypi from the class Installer works well.

        """
        self.setUp()

        self.__installer.update_pypi("wxpythonnnn")
        y = len(self.__installer.get_pypi_errors()) != 0
        self.assertTrue(y)

        self.__installer.update_pypi("wxpython")
        y = len(self.__installer.get_pypi_errors()) != 0
        self.assertTrue(y)

        with self.assertRaises(AssertionError):
            y = len(self.__installer.get_pypi_errors()) != 0
            self.assertFalse(y)

        self.__installer.set_pypi_errors("")

        self.__installer.update_pypi("wxpython")
        y = len(self.__installer.get_pypi_errors()) != 0
        self.assertFalse(y)

    # ---------------------------------------------------------------------------

    def test_install_packages(self):
        """Test if the method install_packages from the class Installer works well.

        """
        self.setUp()

        self.__feature.set_packages({"azfegsdfgsdg": ">;0.0"})
        with self.assertRaises(NotImplementedError):
            self.__installer.install_packages(self.__feature)

        with self.assertRaises(NotImplementedError):
            self.__installer.install_packages(4)

        with self.assertRaises(NotImplementedError):
            self.__installer.install_packages("Hello")

        self.__feature.set_packages({"none": ">;0.0"})
        y = self.__feature.get_available()
        self.assertEqual(y, False)

    # ---------------------------------------------------------------------------

    def test_search_package(self):
        """Test if the method search_package from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__installer.search_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        """Test if the method install_package from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__installer.install_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        """Test if the method version_package from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__installer.version_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        """Test if the method need_update_package from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__installer.need_update_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        """Test if the method update_package from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__installer.update_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_configurate_enable(self):
        """Test if the method configurate_enable from the class Installer works well.

        """
        self.setUp()

        if self.__installer.get_cfg_exist() is True:
            with self.assertRaises(NotImplementedError):
                self.__installer.configurate_enable("aaaa")

            with self.assertRaises(NotImplementedError):
                self.__installer.configurate_enable("aaaa")

            x = self.__installer.get_config_parser()
            x.read(self.__installer.get_config_file())

            list_options = x.options("features")
            i = 0

            for option in list_options:
                x.set("features", option, "true")
                x.write(open(self.__installer.get_config_file(), 'w'))
                self.__installer.configurate_enable(x)

                if self.__installer.get_features()[i].get_available() is True:
                    self.assertEqual(self.__installer.get_features()[i].get_enable(), True)
                    self.assertEqual(x.getboolean("features", option), True)
                else:
                    self.assertEqual(self.__installer.get_features()[i].get_enable(), False)
                    self.assertEqual(x.getboolean("features", option), False)

                self.assertEqual(self.__installer.get_features()[i].get_enable(), x.getboolean("features", option))

                x.set("features", option, "false")
                x.write(open(self.__installer.get_config_file(), 'w'))
                self.__installer.configurate_enable(x)

                self.assertEqual(self.__installer.get_features()[i].get_enable(), False)
                # self.assertEqual(y.getboolean(option, "enable"), False)
                self.assertEqual(x.getboolean("features", option), False)

                self.assertEqual(self.__installer.get_features()[i].get_enable(), x.getboolean("features", option))
                # self.assertEqual(y.getboolean(option, "enable"), x.getboolean("features", option))

                i += 1

    # ---------------------------------------------------------------------------

    def Win_test_search_package(self):
        """Test if the method search_package from the class Installer works well.

        """
        self.setUp()

        self.assertTrue(self.__windows.search_package("aaaa"))

    # ---------------------------------------------------------------------------

    def Win_test_install_package(self):
        """Test if the method install_package from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__windows.install_package("aaaa")

    # ---------------------------------------------------------------------------

    def Win_test_version_package(self):
        """Test if the method version_package from the class Installer works well.

        """
        self.setUp()

        self.assertTrue(self.__windows.version_package("aaaa", "aaaa"))

    # ---------------------------------------------------------------------------

    def Win_test_need_update_package(self):
        """Test if the method need_update_package from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__windows.need_update_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def Win_test_update_package(self):
        """Test if the method update_package from the class Installer works well.

        """
        self.setUp()

        with self.assertRaises(NotImplementedError):
            self.__windows.update_package("aaaa")

    # ---------------------------------------------------------------------------


test = TestInstaller()
test.test_get_set_req()
test.test_get_set_cmdos()
test.test_get_set_cfg_exist()
test.test_get_config_parser()
test.test_init_features()
test.test_set_features()
test.test_parse_depend()
test.test_get_features()
test.test_get_features_parser()
test.test_get_set_cmd_errors()
test.test_get_set_pypi_errors()
test.test_get_set_system_errors()
test.test_install_cmd()
test.test_search_cmds()
test.test_install_cmds()
test.test_install_pypis()
test.test_search_pypi()
test.test_install_pypi()
test.test_version_pypi()
test.test_need_update_pypi()
test.test_update_pypi()
test.test_search_package()
test.test_install_package()
test.test_version_package()
test.test_need_update_package()
test.test_update_package()
test.test_configurate_enable()
test.Win_test_search_package()
test.Win_test_install_package()
test.Win_test_version_package()
test.Win_test_need_update_package()
test.Win_test_update_package()

