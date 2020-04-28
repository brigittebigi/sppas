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

    src.config.tests.test_configuration.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest

from sppas.src.config.configuration import Configuration, os, sppasPathSettings

# ---------------------------------------------------------------------------


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__configuration = Configuration()

    # ---------------------------------------------------------------------------

    def test_load(self):
        """Test if the method load from the class Configuration works well.

        """
        with sppasPathSettings() as sp:
            config = os.path.join(sp.basedir, ".deps~")
            self.__dict__["file"] = config

            if os.path.exists(config) is False:
                self.assertEqual(self.__configuration.get_cfg_exist(), False)
            else:
                self.assertEqual(self.__configuration.get_cfg_exist(), True)

    # ---------------------------------------------------------------------------

    def test_save(self):
        """Test if the method save from the class Configuration works well.

        """
        self.__configuration.set_deps({"4": "1", "3": "2", "5": "6"})
        self.__configuration.save()
        y = self.__configuration.get_file_dict()
        self.assertEqual(y, {"deps": {"4": "1", "3": "2", "5": "6"}})

    # ---------------------------------------------------------------------------

    def test_get_add_modify_deps(self):
        """Test if the methods get_deps, add_deps and modify_deps from the class Configuration works well.

        """
        self.__configuration.set_deps({})
        self.__configuration.add_deps("wxpython", False)
        self.__configuration.add_deps("brew", False)
        self.__configuration.add_deps("julius", False)

        y = self.__configuration.get_deps()
        self.assertEqual(y, {"wxpython": False, "brew": False, "julius": False})

        self.__configuration.modify_deps("wxpython", True)

        y = self.__configuration.get_deps()
        self.assertEqual(y, {"wxpython": True, "brew": False, "julius": False})

    # ---------------------------------------------------------------------------

    def test_set_deps(self):
        """Test if the method set_deps from the class Configuration works well.

        """
        self.__configuration.set_deps({"4": "1"})
        y = self.__configuration.get_deps()
        self.assertEqual(y, {"4": "1"})

        self.__configuration.set_deps({"4": "2"})
        y = self.__configuration.get_deps()
        self.assertEqual(y, {"4": "2"})

        with self.assertRaises(NotImplementedError):
            self.__configuration.set_deps("Hello")

    # ---------------------------------------------------------------------------

    def test_get_set_cfg_exist(self):
        """Test if the methods get_cfg_exist and set_cfg_exist from the class Configuration works well.

        """
        self.__configuration.set_cfg_exist({"4": "1"})
        y = self.__configuration.get_cfg_exist()
        self.assertEqual(y, True)

        self.__configuration.set_cfg_exist(True)
        y = self.__configuration.get_cfg_exist()
        self.assertEqual(y, True)

        self.__configuration.set_cfg_exist(0)
        y = self.__configuration.get_cfg_exist()
        self.assertEqual(y, False)

        self.__configuration.set_cfg_exist(False)
        y = self.__configuration.get_cfg_exist()
        self.assertEqual(y, False)

    # ---------------------------------------------------------------------------


test = TestConfiguration()
test.setUp()
test.test_load()
test.test_get_add_modify_deps()
test.test_set_deps()
test.test_get_set_cfg_exist()
test.test_save()
