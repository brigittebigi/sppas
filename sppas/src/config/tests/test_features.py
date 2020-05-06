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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
from sppas.src.preinstall.features import Features, Feature


# ---------------------------------------------------------------------------


class TestFeatures(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__features = Features("req_win", "cmd_win")
        self.__feature = Feature("feature")

    # ---------------------------------------------------------------------------

    def test_get_features_filename(self):
        """Return the name of the file with the features descriptions."""
        y = self.__features.get_features_filename()
        self.assertIn("features.ini", y)

    # ---------------------------------------------------------------------------

    def test_get_ids(self):
        """Return the list of feature identifiers."""
        y = self.__features.get_ids()
        self.assertEqual(y, ["wxpython", "brew", "julius"])

    # ---------------------------------------------------------------------------

    def test_enable(self):
        """Return True if the feature is enabled and/or set it."""
        if self.__features.get_cfg_exist() is False:
            y = self.__features.enable("wxpython")
            self.assertEqual(y, False)
        else:
            self.__features.enable("wxpython", False)
            y = self.__features.enable("wxpython")
            self.assertEqual(y, False)

        self.__features.enable("wxpython", True)
        y = self.__features.enable("wxpython")
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_available(self):
        """Return True if the feature is available and/or set it."""
        y = self.__features.available("wxpython")
        self.assertEqual(y, True)

        self.__features.available("wxpython", False)
        y = self.__features.available("wxpython")
        self.assertEqual(y, False)

    # ---------------------------------------------------------------------------

    def test_description(self):
        """Return the description of the feature"""
        y = self.__features.description("wxpython")
        self.assertEqual(y, "Graphic Interface")

        y = self.__features.description("brew")
        self.assertEqual(y, "Package manager MacOs")

        y = self.__features.description("julius")
        self.assertEqual(y, "Automatic alignment")

    # ---------------------------------------------------------------------------

    def test_packages(self):
        """Return the dictionary of system dependencies of the feature."""
        # For Windows
        y = self.__features.packages("wxpython")
        self.assertEqual(y, {'nil': '1'})

        y = self.__features.packages("brew")
        self.assertEqual(y, {'nil': '1'})

    # ---------------------------------------------------------------------------

    def test_pypi(self):
        # For Windows
        """Return the dictionary of pip dependencies of the feature."""
        y = self.__features.pypi("wxpython")
        self.assertEqual(y, {'wxpython': '>;4.0'})

        y = self.__features.pypi("brew")
        self.assertEqual(y, {'nil': '1'})

    # ---------------------------------------------------------------------------

    def test_cmd(self):
        # For Windows
        """Return the command to execute for the feature."""
        y = self.__features.cmd("wxpython")
        self.assertEqual(y, "nil")

        y = self.__features.cmd("brew")
        self.assertEqual(y, "none")

    # ---------------------------------------------------------------------------

    def test_init_features(self):
        """Return a parsed version of your features.ini file."""
        y = self.__features.init_features()

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
        """Browses the features.ini file and instantiate a Feature()."""
        self.setUp()

        self.__features.set_features()

        y = self.__features.get_ids()

        self.assertEqual(y[0], "wxpython")
        self.assertEqual(self.__features.description(y[0]), "Graphic Interface")
        self.assertEqual(self.__features.packages(y[0]), {'nil': '1'})
        self.assertEqual(self.__features.pypi(y[0]), {'wxpython': '>;4.0'})
        self.assertEqual(self.__features.cmd(y[0]), "nil")

        self.assertEqual(y[1], "brew")
        self.assertEqual(self.__features.description(y[1]), "Package manager MacOs")
        self.assertEqual(self.__features.packages(y[1]), {'nil': '1'})
        self.assertEqual(self.__features.pypi(y[1]), {'nil': '1'})
        self.assertEqual(self.__features.cmd(y[1]), "none")

        self.assertEqual(y[2], "julius")
        self.assertEqual(self.__features.description(y[2]), "Automatic alignment")
        self.assertEqual(self.__features.packages(y[2]), {'nil': '1'})
        self.assertEqual(self.__features.pypi(y[2]), {'nil': '1'})
        self.assertEqual(self.__features.cmd(y[2]), "none")

    # ---------------------------------------------------------------------------

    def test_parse_depend(self):
        """Create a dictionary from the string given as an argument."""
        def parse(string_require):
            string_require = str(string_require)
            dependencies = string_require.split(" ")
            depend = dict()
            for line in dependencies:
                tab = line.split(":")
                depend[tab[0]] = tab[1]
            return depend

        y = parse("aa:aa aa:aa aa:aa aa:aa")
        self.assertEqual(y, {'aa': 'aa'})
        y = parse("aa:aa bb:bb cc:cc dd:dd")
        self.assertEqual(y, {'aa': 'aa', 'bb': 'bb', 'cc': 'cc', 'dd': 'dd'})

        with self.assertRaises(IndexError):
            parse(4)

        with self.assertRaises(IndexError):
            parse("Bonjour")

        with self.assertRaises(IndexError):
            parse(4.0)

        with self.assertRaises(IndexError):
            parse("aaaa aaaa aaaa aaaa")

        with self.assertRaises(IndexError):
            parse(["aa", ":aa", "bb", ":bb", "cc", ":cc", "dd", ":dd"])

    # ---------------------------------------------------------------------------

    def test__len__(self):
        """Return the number of features."""
        y = self.__features.__len__()
        self.assertEqual(y, 3)

    # ---------------------------------------------------------------------------

    def test__contains__(self):
        """Return the number of features."""
        y = self.__features.__contains__("wxpython")
        self.assertTrue(y)

        y = self.__features.__contains__("brew")
        self.assertTrue(y)

        y = self.__features.__contains__("julius")
        self.assertTrue(y)

    # ---------------------------------------------------------------------------


test = TestFeatures()
test.setUp()
test.test_get_features_filename()
test.test_get_ids()
test.test_enable()
test.test_available()
test.test_description()
test.test_packages()
test.test_pypi()
test.test_cmd()
test.test_init_features()
test.test_set_features()
test.test_parse_depend()
test.test__len__()
test.test__contains__()

