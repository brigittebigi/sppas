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

    src.config.tests.test_appcfg.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest

from sppas.src.config.appcfg import sppasAppConfig, os, sppasPathSettings

# ---------------------------------------------------------------------------


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__configuration = sppasAppConfig()

    # ---------------------------------------------------------------------------

    def test_cfg_filename(self):
        """Return the name of the config file."""
        y = self.__configuration.cfg_filename()
        self.assertIn(".deps~", y)

    # ---------------------------------------------------------------------------

    def test_cfg_exist(self):
        """Return if the config file exists or not."""
        y = os.path.exists(self.__configuration.cfg_filename())
        self.assertEqual(y, self.__configuration.cfg_file_exists())

    # ---------------------------------------------------------------------------

    def test_load(self):
        """Override. Load the configuration from a file."""
        self.__configuration.load()
        if self.__configuration.cfg_file_exists() is True:
            y = self.__configuration.get_deps()
            self.assertEqual(y, ["wxpython", "brew", "julius"])
        else:
            y = self.__configuration.get_deps()
            self.assertEqual(y, [])

    # ---------------------------------------------------------------------------

    def test_save(self):
        """Override. Save the dictionary in a file."""
        self.__configuration.set_dep("wxpython", True)
        self.__configuration.set_dep("brew", True)
        self.__configuration.set_dep("julius", True)
        self.__configuration.save()
        y = self.__configuration.get_deps()
        self.assertEqual(y, ["wxpython", "brew", "julius"])

    # ---------------------------------------------------------------------------

    def test_hide_unhide(self):
        """Hide or unhide a file"""
        y = self.__configuration.hide_unhide("deps", "-")
        self.assertEqual(y, ".deps~")

        y = self.__configuration.hide_unhide(".deps~", "-")
        self.assertEqual(y, ".deps~")

    # ---------------------------------------------------------------------------

    def test_get_set_deps(self):
        """Return(get_deps), add or modify(set_dep) the dictionnary self.__dict__["file_dict"]."""
        self.__configuration.set_dep("first", True)
        y = self.__configuration.get_deps()
        self.assertEqual(y, ["wxpython", "brew", "julius", "first"])

        self.__configuration.set_dep("second", True)
        y = self.__configuration.get_deps()
        self.assertEqual(y, ["wxpython", "brew", "julius", "first", "second"])

    # ---------------------------------------------------------------------------

    def test_dep_enabled(self):
        """Return True if a dependency is enabled"""
        self.assertFalse(self.__configuration.dep_enabled("aaaa"))

        self.assertEqual(self.__configuration.dep_enabled("wxpython"), True)
        self.assertEqual(self.__configuration.dep_enabled("brew"), True)
        self.assertEqual(self.__configuration.dep_enabled("julius"), True)
        self.assertEqual(self.__configuration.dep_enabled("first"), True)
        self.assertEqual(self.__configuration.dep_enabled("second"), True)

    # ---------------------------------------------------------------------------


test = TestConfiguration()
test.setUp()
test.test_cfg_filename()
test.test_cfg_exist()
test.test_load()
test.test_save()
test.test_hide_unhide()
test.test_get_set_deps()
test.test_dep_enabled()
