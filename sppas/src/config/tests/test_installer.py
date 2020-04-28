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
from sppas.src.config.installer import Installer, Features, Feature


# ---------------------------------------------------------------------------


class TestInstaller(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        p = ProcessProgressTerminal()
        self.__installer = Installer(p)
        self.__features = Features("req_win", "cmd_win")
        self.__feature = Feature()

        self.__feature.set_available(True)
        self.__feature.set_enable(True)
        self.__feature.set_cmd("nil")
        self.__feature.set_packages({"4": "1"})
        self.__feature.set_pypi({"4": "1"})

        self.__installer.get_actual_feature().set_available(True)
        self.__installer.get_actual_feature().set_enable(True)
        self.__installer.get_actual_feature().set_cmd("nil")
        self.__installer.get_actual_feature().set_packages({"4": "1"})
        self.__installer.get_actual_feature().set_pypi({"4": "1"})

    # ---------------------------------------------------------------------------

    def test_get_set_progress(self):
        """Test if the methods get_set_progress from the class Installer works well.

        """
        y = self.__installer.get_set_progress(0.5)
        self.assertEqual(y, 0.5)

        y = self.__installer.get_set_progress(10)
        self.assertEqual(y, 1)

        y = self.__installer.get_set_progress(10)
        self.assertEqual(y, 1)

        with self.assertRaises(TypeError):
            self.__installer.get_set_progress("10")

        with self.assertRaises(AssertionError):
            with self.assertRaises(AssertionError):
                self.__installer.get_set_progress(False)

    # ---------------------------------------------------------------------------

    def test_get_set_actual_feature(self):
        """Test if the methods get_actual_feature and set_actual_feature from the class Installer works well.

        """
        feature = Feature()
        feature.set_id("Hello")
        feature.set_desc("Goodbye")
        feature.set_enable(False)
        feature.set_available(True)

        self.__installer.set_actual_feature(feature)
        y = self.__installer.get_actual_feature()
        self.assertEqual(y, feature)
        self.assertEqual(y.get_id(), feature.get_id())
        self.assertEqual(y.get_desc(), feature.get_desc())
        self.assertEqual(y.get_enable(), feature.get_enable())
        self.assertEqual(y.get_available(), feature.get_available())

    # ---------------------------------------------------------------------------

    def test_get_set_save_errors(self):
        """Test if the methods get_total_errors, set_total_errors and save_errors from the class Installer works well.

        """
        self.__installer.save_errors("")
        y = self.__installer.get_total_errors()
        self.assertEqual(y, "")

        self.__installer.set_total_errors("aaa")
        y = self.__installer.get_total_errors()
        self.assertEqual(y, "aaa")

        self.__installer.save_errors("")
        y = self.__installer.get_total_errors()
        self.assertEqual(y, "aaa")

        self.__installer.save_errors("bbbb")
        y = self.__installer.get_total_errors()
        self.assertEqual(y, "aaabbbb")

    # ---------------------------------------------------------------------------

    def test_show_save_cmd(self):
        """Test if the methods show_save_cmd from the class Installer works well.

        """
        self.__installer.show_save_cmd("cmd1", "bbb")
        y = self.__installer.get_cmd_errors()
        self.assertEqual(y, "bbb")

        self.__installer.show_save_cmd("cmd2", "ccc")
        y = self.__installer.get_cmd_errors()
        self.assertEqual(y, "ccc")

        self.__installer.show_save_cmd("cmd3", "")
        y = self.__installer.get_cmd_errors()
        self.assertEqual(y, "")

        self.__installer.show_save_cmd("cmd4", "bbb")
        y = self.__installer.get_cmd_errors()
        self.assertEqual(y, "bbb")

    # ---------------------------------------------------------------------------

    def test_show_save_system(self):
        """Test if the methods show_save_system from the class Installer works well.

        """
        self.__installer.show_save_system("system1", "bbb")
        y = self.__installer.get_system_errors()
        self.assertEqual(y, "bbb")

        self.__installer.show_save_system("system2", "ccc")
        y = self.__installer.get_system_errors()
        self.assertEqual(y, "bbbccc")

        self.__installer.show_save_system("system3", "")
        y = self.__installer.get_system_errors()
        self.assertEqual(y, "")

        self.__installer.show_save_system("system4", "bbb")
        y = self.__installer.get_system_errors()
        self.assertEqual(y, "bbb")

    # ---------------------------------------------------------------------------

    def test_show_save_pypi(self):
        """Test if the methods show_save_pypi from the class Installer works well.

        """
        self.__installer.show_save_pypi("pypi1", "bbb")
        y = self.__installer.get_cmd_errors()
        self.assertEqual(y, "bbb")

        self.__installer.show_save_pypi("pypi2", "ccc")
        y = self.__installer.get_pypi_errors()
        self.assertEqual(y, "bbbccc")

        self.__installer.show_save_pypi("pypi3", "")
        y = self.__installer.get_pypi_errors()
        self.assertEqual(y, "")

        self.__installer.show_save_pypi("pypi4", "bbb")
        y = self.__installer.get_pypi_errors()
        self.assertEqual(y, "bbb")

    # ---------------------------------------------------------------------------

    def test_calcul_pourc(self):
        """Test if the methods get_set_progress from the class Installer works well.

        """
        y = self.__installer.calcul_pourc(self.__feature)
        x = round((1 / (1 + len(self.__feature.get_packages()) + len(self.__feature.get_pypi()))), 2)
        self.assertEqual(y, 0.33)
        self.assertEqual(y, x)

    # ---------------------------------------------------------------------------

    def test_get_set_cmd_errors(self):
        """Test if the method get_cmd_errors and set_cmd_errors from the class Installer works well.

        """
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
        self.__installer.set_pypi_errors("")
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
        self.__installer.set_system_errors("")
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
        self.__installer.install_cmds("aaaaaaaaaa", self.__feature)
        y = len(self.__installer.get_cmd_errors()) != 0
        self.assertTrue(y)

        self.__installer.set_cmd_errors("")

        self.__installer.install_cmds("pip freeze", self.__feature)
        y = len(self.__installer.get_cmd_errors()) != 0
        self.assertFalse(y)

        with self.assertRaises(AssertionError):
            y = len(self.__installer.get_cmd_errors()) != 0
            self.assertTrue(y)

    # ---------------------------------------------------------------------------

    def test_install_cmd(self):
        """Test if the method install_cmd from the class Installer works well.

        """
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
        self.assertFalse(self.__installer.search_cmds("wxpythonnnnnn"))

        self.assertTrue(self.__installer.search_cmds("pip"))

    # ---------------------------------------------------------------------------

    def test_install_pypis(self):
        """Test if the method install_pypis from the class Installer works well.

        """
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
        self.assertFalse(self.__installer.search_pypi("wxpythonnnnnn"))
        self.assertFalse(self.__installer.search_pypi(4))

        self.assertTrue(self.__installer.search_pypi("pip"))

    # ---------------------------------------------------------------------------

    def test_install_pypi(self):
        """Test if the method install_pypi from the class Installer works well.

        """
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
        self.assertTrue(y)

    # ---------------------------------------------------------------------------

    def test_version_pypi(self):
        """Test if the method version_pypi from the class Installer works well.

        """
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
        self.assertTrue(y)

    # ---------------------------------------------------------------------------

    def test_install_packages(self):
        """Test if the method install_packages from the class Installer works well.

        """
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
        with self.assertRaises(NotImplementedError):
            self.__installer.search_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        """Test if the method install_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer.install_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        """Test if the method version_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer.version_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        """Test if the method need_update_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer.need_update_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        """Test if the method update_package from the class Installer works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__installer.update_package("aaaa")

    # ---------------------------------------------------------------------------


test = TestInstaller()
test.setUp()
test.test_get_set_progress()
test.test_get_set_actual_feature()
test.test_get_set_save_errors()
test.test_show_save_cmd()
test.test_show_save_system()
test.test_show_save_pypi()
test.test_calcul_pourc()
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

