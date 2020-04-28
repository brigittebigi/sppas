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

    src.config.tests.test_features.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
from sppas.src.config.features import Features, Feature, cp


# ---------------------------------------------------------------------------


class TestFeatures(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__features = Features("req_win", "cmd_win")
        self.__feature = Feature()

    # ---------------------------------------------------------------------------

    def test_read_config(self):
        """Test if the methods read_config from the class Features works well.

        """
        if self.__features.get_configuration().get_cfg_exist() is True:
            self.__features.get_configuration().set_deps({})
            self.__features.get_configuration().set_deps({"wxpython": True, "brew": True, "julius": True})
            self.__features.get_configuration().set_cfg_exist(True)
            self.__features.read_config()
            enables = list()
            for f in self.__features.get_features():
                enables.append(f.get_enable())
            self.assertEqual(enables, [True, False, False])

            self.__features.get_configuration().set_deps({"wxpython": False, "brew": False, "julius": False})
            self.__features.get_configuration().set_cfg_exist(True)
            self.__features.read_config()
            enables = list()
            for f in self.__features.get_features():
                enables.append(f.get_enable())
            self.assertEqual(enables, [False, False, False])

    # ---------------------------------------------------------------------------

    def test_write_config(self):
        """Test if the methods write_config from the class Features works well.

        """
        self.__features.set_cfg_exist(False)
        if self.__features.get_cfg_exist() is False:
            self.__features.get_configuration().set_deps({})
            for f in self.__features.get_features():
                self.__features.get_configuration().add_deps(f.get_id(), f.get_enable())
            y = self.__features.get_configuration().get_deps()
            self.assertEqual(y, {"wxpython": False, "brew": False, "julius": False})

    # ---------------------------------------------------------------------------

    def test_get_set_cfg_exist(self):
        """Test if the methods get_cfg_exist and set_cfg_exist from the class Features works well.

        """
        self.__features.set_cfg_exist(True)
        y = self.__features.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__features.set_cfg_exist(["a", "b", "c"])
        y = self.__features.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__features.set_cfg_exist({"1": "a", "2": "b", "3": "c"})
        y = self.__features.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__features.set_cfg_exist("")
        y = self.__features.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, False)

        self.__features.set_cfg_exist(4)
        y = self.__features.get_cfg_exist()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_config_file(self):
        """Test if the methods get_config_file from the class Features works well.

        """
        y = self.__features.get_configuration().get_deps()
        self.assertIsInstance(y, dict)

    # ---------------------------------------------------------------------------

    def test_init_features(self):
        """Test if the method init_features from the class Features works well.

        """
        y = self.__features.get_features_parser()
        y.read(self.__features.get_feature_file())

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
        """Test if the method set_features from the class Features works well.

        """
        self.setUp()

        self.__features.set_features()

        y = self.__features.get_features()

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
        """Test if the method parse_depend from the class Features works well.

        """
        y = self.__features.parse_depend("aa:aa aa:aa aa:aa aa:aa")
        self.assertEqual(y, {'aa': 'aa'})

        y = self.__features.parse_depend("aa:aa bb:bb cc:cc dd:dd")
        self.assertEqual(y, {'aa': 'aa', 'bb': 'bb', 'cc': 'cc', 'dd': 'dd'})

        with self.assertRaises(IndexError):
            self.__features.parse_depend(4)

        with self.assertRaises(IndexError):
            self.__features.parse_depend("Bonjour")

        with self.assertRaises(IndexError):
            self.__features.parse_depend(4.0)

        with self.assertRaises(IndexError):
            self.__features.parse_depend("aaaa aaaa aaaa aaaa")

        with self.assertRaises(IndexError):
            self.__features.parse_depend(["aa", ":aa", "bb", ":bb", "cc", ":cc", "dd", ":dd"])

    # ---------------------------------------------------------------------------

    def test_get_features(self):
        """Test if the method get_features from the class Features works well.

        """
        self.assertIsInstance(self.__features.get_features(), list)

    # ---------------------------------------------------------------------------

    def test_get_features_parser(self):
        """Test if the method get_features_parser from the class Features works well.

        """
        y = self.__features.get_features_parser()
        self.assertIsInstance(y, cp.ConfigParser)

    # ---------------------------------------------------------------------------


test = TestFeatures()
test.setUp()
test.test_read_config()
test.test_write_config()
test.test_get_set_cfg_exist()
test.test_get_config_file()
test.test_init_features()
test.test_set_features()
test.test_parse_depend()
test.test_get_features()
test.test_get_features_parser()

