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

    src.config.tests.test_feature.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest

from sppas.src.preinstall.feature import Feature

# ---------------------------------------------------------------------------


class TestFeature(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__feature = Feature("feature")

    # ---------------------------------------------------------------------------

    def test_get_id(self):
        """Return the id of feature."""
        y = self.__feature.get_id()
        self.assertEqual(y, "feature")

    # ---------------------------------------------------------------------------

    def test_get_set_enable(self):
        """Return(get_enable) or set(set_enable) enable of feature."""
        self.__feature.set_enable(True)
        y = self.__feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__feature.set_available(False)
        self.__feature.set_enable(True)
        y = self.__feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, False)

        self.__feature.set_available(True)
        self.__feature.set_enable(["a", "b", "c"])
        y = self.__feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__feature.set_enable({"1": "a", "2": "b", "3": "c"})
        y = self.__feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__feature.set_enable("")
        y = self.__feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, False)

        self.__feature.set_enable(4)
        y = self.__feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_available(self):
        """Return(get_available) or set(set_available) available of feature."""
        self.__feature.set_available(True)
        y = self.__feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__feature.set_enable(True)
        self.__feature.set_available(False)
        y = self.__feature.get_available()
        x = self.__feature.get_enable()
        self.assertIsInstance(y, bool)
        self.assertIsInstance(x, bool)
        self.assertEqual(y, False)
        self.assertEqual(x, False)

        self.__feature.set_available(["a", "b", "c"])
        y = self.__feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__feature.set_available({"1": "a", "2": "b", "3": "c"})
        y = self.__feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

        self.__feature.set_available("")
        y = self.__feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, False)

        self.__feature.set_available(4)
        y = self.__feature.get_available()
        self.assertIsInstance(y, bool)
        self.assertEqual(y, True)

    # ---------------------------------------------------------------------------

    def test_get_set_desc(self):
        """Return(get_desc) or set(set_desc) the description of feature."""
        self.__feature.set_desc("aaaa")
        y = self.__feature.get_desc()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "aaaa")

        self.__feature.set_desc(True)
        y = self.__feature.get_desc()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "True")

        self.__feature.set_desc(["a", "b", "c"])
        y = self.__feature.get_desc()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "['a', 'b', 'c']")

        self.__feature.set_desc({"1": "a", "2": "b", "3": "c"})
        y = self.__feature.get_desc()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "{'1': 'a', '2': 'b', '3': 'c'}")

        self.__feature.set_desc(4)
        y = self.__feature.get_desc()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "4")

    # ---------------------------------------------------------------------------

    def test_get_set_packages(self):
        """Return(get_packages) or set(set_packages) the dictionary of system dependencies."""
        self.__feature.set_packages(dict())
        y = self.__feature.get_packages()
        self.assertIsInstance(y, dict)
        self.assertEqual(y, {})

        self.__feature.set_packages({'1': 'a', '2': 'b', '3': 'c'})
        y = self.__feature.get_packages()
        self.assertIsInstance(y, dict)
        self.assertEqual(y, {'1': 'a', '2': 'b', '3': 'c'})

        with self.assertRaises(ValueError):
            self.__feature.set_packages(["a", "b", "c"])

        with self.assertRaises(ValueError):
            self.__feature.set_packages("a")

        with self.assertRaises(TypeError):
            self.__feature.set_packages((1, 2, 3))

        with self.assertRaises(TypeError):
            self.__feature.set_packages(4)

        with self.assertRaises(TypeError):
            self.__feature.set_packages(True)

        with self.assertRaises(TypeError):
            self.__feature.set_packages(4.0)

    # ---------------------------------------------------------------------------

    def test_get_set_pypi(self):
        """Return(get_pypi) or set(set_pypi) the dictionary of pip dependencies."""
        self.__feature.set_pypi(dict())
        y = self.__feature.get_pypi()
        self.assertIsInstance(y, dict)
        self.assertEqual(y, {})

        self.__feature.set_pypi({'1': 'a', '2': 'b', '3': 'c'})
        y = self.__feature.get_pypi()
        self.assertIsInstance(y, dict)
        self.assertEqual(y, {'1': 'a', '2': 'b', '3': 'c'})

        with self.assertRaises(ValueError):
            self.__feature.set_pypi(["a", "b", "c"])

        with self.assertRaises(ValueError):
            self.__feature.set_pypi("a")

        with self.assertRaises(TypeError):
            self.__feature.set_pypi((1, 2, 3))

        with self.assertRaises(TypeError):
            self.__feature.set_pypi(4)

        with self.assertRaises(TypeError):
            self.__feature.set_pypi(True)

        with self.assertRaises(TypeError):
            self.__feature.set_pypi(4.0)

    # ---------------------------------------------------------------------------

    def test_get_set_cmd(self):
        """Return(get_cmd) or set(set_cmd) the command to execute"""
        self.__feature.set_cmd("aaaa")
        y = self.__feature.get_cmd()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "aaaa")

        self.__feature.set_cmd(True)
        y = self.__feature.get_cmd()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "True")

        self.__feature.set_cmd(["a", "b", "c"])
        y = self.__feature.get_cmd()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "['a', 'b', 'c']")

        self.__feature.set_cmd({"1": "a", "2": "b", "3": "c"})
        y = self.__feature.get_cmd()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "{'1': 'a', '2': 'b', '3': 'c'}")

        self.__feature.set_cmd(4)
        y = self.__feature.get_cmd()
        self.assertIsInstance(y, str)
        self.assertEqual(y, "4")


test = TestFeature()
test.setUp()
test.test_get_id()
test.test_get_set_enable()
test.test_get_set_available()
test.test_get_set_desc()
test.test_get_set_packages()
test.test_get_set_pypi()
test.test_get_set_cmd()

