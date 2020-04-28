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

from sppas.src.config.configuration import Configuration

# ---------------------------------------------------------------------------


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__configuration = Configuration()

    # ---------------------------------------------------------------------------

    def test_get_add_modify_feature(self):
        """Test if the methods get_feature, add_feature and modify_feature from the class Feature works well.

        """
        self.__configuration.add_feature("wxpython", False)
        self.__configuration.add_feature("brew", False)
        self.__configuration.add_feature("julius", False)

        y = self.__configuration.get_features_enable()
        self.assertEqual(y, {"wxpython": False, "brew": False, "julius": False})

        self.__configuration.modify_feature("wxpython", True)

        y = self.__configuration.get_features_enable()
        self.assertEqual(y, {"wxpython": True, "brew": False, "julius": False})

    # ---------------------------------------------------------------------------


test = TestConfiguration()
test.setUp()
test.test_get_add_modify_feature()
