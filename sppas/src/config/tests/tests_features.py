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

    src.config.tests.tests_features.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest

from sppas.src.config.features import Feature

# ---------------------------------------------------------------------------


class TestFeatures(unittest.TestCase):

    feature = Feature()

    def test_get_set_enable(self):
        """Test if the methods get_enable and set_enable works well."""
        self.feature.set_enable(True)
        y = self.feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.feature.set_enable(["a", "b", "c"])
        y = self.feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.feature.set_enable({"1": "a", "2": "b", "3": "c"})
        y = self.feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.feature.set_enable("")
        y = self.feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, False)

        self.feature.set_enable(4)
        y = self.feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_available(self):
        """Test if the methods get_available and set_available works well."""
        self.feature.set_available(True)
        y = self.feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.feature.set_available(["a", "b", "c"])
        y = self.feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.feature.set_available({"1": "a", "2": "b", "3": "c"})
        y = self.feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.feature.set_available("")
        y = self.feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, False)

        self.feature.set_available(4)
        y = self.feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_id(self):
        """Test if the methods get_id and set_id works well."""
        self.feature.set_id("aaaa")
        y = self.feature.get_id()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "aaaa")

        self.feature.set_id(True)
        y = self.feature.get_id()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "True")

        self.feature.set_id(["a", "b", "c"])
        y = self.feature.get_id()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "['a', 'b', 'c']")

        self.feature.set_id({"1": "a", "2": "b", "3": "c"})
        y = self.feature.get_id()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "{'1': 'a', '2': 'b', '3': 'c'}")

        self.feature.set_id(4)
        y = self.feature.get_id()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "4")

    # ---------------------------------------------------------------------------

    def test_get_set_dict_packages(self):
        """Test if the methods get_dict_packages and set_dict_packages works well."""
        self.feature.set_dict_packages(dict())
        y = self.feature.get_dict_packages()
        self.assertIsInstance(y, dict)
        self.assertEqual(y, {})

        self.feature.set_dict_packages({'1': 'a', '2': 'b', '3': 'c'})
        y = self.feature.get_dict_packages()
        self.assertIsInstance(y, dict)
        self.assertEqual(y, {'1': 'a', '2': 'b', '3': 'c'})

        with self.assertRaises(ValueError):
            self.feature.set_dict_packages(["a", "b", "c"])

        with self.assertRaises(ValueError):
            self.feature.set_dict_packages("a")

        with self.assertRaises(TypeError):
            self.feature.set_dict_packages((1, 2, 3))

        with self.assertRaises(TypeError):
            self.feature.set_dict_packages(4)

        with self.assertRaises(TypeError):
            self.feature.set_dict_packages(True)

        with self.assertRaises(TypeError):
            self.feature.set_dict_packages(4.0)

    # ---------------------------------------------------------------------------

    def test_get_set_dict_pypi(self):
        """Test if the methods get_dict_pypi and set_dict_pypi works well."""
        self.feature.set_dict_pypi(dict())
        y = self.feature.get_dict_pypi()
        self.assertIsInstance(y, dict)
        self.assertEqual(y, {})

        self.feature.set_dict_pypi({'1': 'a', '2': 'b', '3': 'c'})
        y = self.feature.get_dict_pypi()
        self.assertIsInstance(y, dict)
        self.assertEqual(y, {'1': 'a', '2': 'b', '3': 'c'})

        with self.assertRaises(ValueError):
            self.feature.set_dict_pypi(["a", "b", "c"])

        with self.assertRaises(ValueError):
            self.feature.set_dict_pypi("a")

        with self.assertRaises(TypeError):
            self.feature.set_dict_pypi((1, 2, 3))

        with self.assertRaises(TypeError):
            self.feature.set_dict_pypi(4)

        with self.assertRaises(TypeError):
            self.feature.set_dict_pypi(True)

        with self.assertRaises(TypeError):
            self.feature.set_dict_pypi(4.0)
