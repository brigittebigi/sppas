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

from sppas.src.preinstall.features import Features

# ---------------------------------------------------------------------------


class TestFeatures(unittest.TestCase):

    def setUp(self):
        self.__features = Features("req_win", "cmd_win")

    # ---------------------------------------------------------------------------

    def test_type(self):
        self.assertEqual(self.__features.feature_type("video"), "deps")
        self.assertEqual(self.__features.feature_type("julius"), "deps")
        self.assertEqual(self.__features.feature_type("wxpython"), "deps")
        self.assertEqual(self.__features.feature_type("toto"), None)

    # ---------------------------------------------------------------------------

    def test_get_features_filename(self):
        # Return the name of the file with the features descriptions.
        y = self.__features.get_features_filename()
        self.assertIn("features.ini", y)

    # ---------------------------------------------------------------------------

    def test_get_ids(self):
        # Return the list of feature identifiers.
        y = self.__features.get_ids()
        self.assertTrue("wxpython" in y)
        self.assertTrue("brew" in y)
        self.assertTrue("julius" in y)
        self.assertTrue("video" in y)
        self.assertTrue("pol" in y)

    # ---------------------------------------------------------------------------

    def test_enable(self):
        # Return True if the feature is enabled and/or set it.
        self.__features.enable("wxpython", False)
        y = self.__features.enable("wxpython")
        self.assertEqual(y, False)

        self.__features.enable("wxpython", True)
        y = self.__features.enable("wxpython")
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_available(self):
        # Return True if the feature is available and/or set it.
        y = self.__features.available("video")
        self.assertEqual(y, True)

        y = self.__features.available("wxpython")
        self.assertEqual(y, True)

        self.__features.available("wxpython", False)
        y = self.__features.available("wxpython")
        self.assertEqual(y, False)

        y = self.__features.available("brew")
        self.assertEqual(y, False)

    # ---------------------------------------------------------------------------

    def test_description(self):
        # Return the description of the feature
        y = self.__features.description("wxpython")
        self.assertGreater(len(y), 0)

        y = self.__features.description("brew")
        self.assertGreater(len(y), 0)

        y = self.__features.description("julius")
        self.assertGreater(len(y), 0)

    # ---------------------------------------------------------------------------

    def test_packages(self):
        """Return the dictionary of system dependencies of the feature."""
        # For WindowsInstaller
        y = self.__features.packages("wxpython")
        self.assertEqual(y, {})

        y = self.__features.packages("brew")
        self.assertEqual(y, {})

    # ---------------------------------------------------------------------------

    def test_pypi(self):
        # For WindowsInstaller
        """Return the dictionary of pip dependencies of the feature."""
        y = self.__features.pypi("wxpython")
        self.assertEqual(y, {'wxpython': '>;4.0'})

        y = self.__features.pypi("brew")
        self.assertEqual(y, {})

    # ---------------------------------------------------------------------------

    def test_cmd(self):
        # For WindowsInstaller
        """Return the command to execute for the feature."""
        y = self.__features.cmd("wxpython")
        self.assertEqual(y, "")

        y = self.__features.cmd("brew")
        self.assertEqual(y, "")

    # ---------------------------------------------------------------------------

    def test_init_features(self):
        # Return a parsed version of the features.ini file.
        y = self.__features._Features__init_features()

        self.assertGreater(len(y.sections()), 20)
        self.assertTrue("wxpython" in y.sections())

        self.assertEqual(y.get("wxpython", "pip"), "wxpython:>;4.0")

        self.assertTrue("juliusdownload.py" in y.get("julius", "cmd_win"))

    # ---------------------------------------------------------------------------

    def test_set_features(self):
        # Browses the features.ini file and instantiate a Feature().
        self.setUp()

        self.__features.set_features()

        y = self.__features.get_ids()

        self.assertEqual(y[0], "wxpython")
        self.assertEqual(self.__features.packages(y[0]), {})
        self.assertEqual(self.__features.pypi(y[0]), {'wxpython': '>;4.0'})
        self.assertEqual(self.__features.cmd(y[0]), "")

        self.assertEqual(y[1], "brew")
        self.assertEqual(self.__features.packages(y[1]), {})
        self.assertEqual(self.__features.pypi(y[1]), {})
        self.assertEqual(self.__features.cmd(y[1]), "")

        self.assertEqual(y[2], "julius")
        self.assertEqual(self.__features.packages(y[2]), {})
        self.assertEqual(self.__features.pypi(y[2]), {})
        self.assertTrue("juliusdownload.py" in self.__features.cmd(y[2]))

    # ---------------------------------------------------------------------------

    def test_parse_depend(self):
        # Create a dictionary from the string given as an argument.
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
        # Return the number of features.
        y = self.__features.__len__()
        self.assertEqual(y, 23)

    # ---------------------------------------------------------------------------

    def test__contains__(self):
        # Return the number of features.
        y = self.__features.__contains__("wxpython")
        self.assertTrue(y)

        y = self.__features.__contains__("brew")
        self.assertTrue(y)

        y = self.__features.__contains__("julius")
        self.assertTrue(y)

