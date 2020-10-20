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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import unittest

from sppas.src.config.appcfg import sppasAppConfig

# ---------------------------------------------------------------------------


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.__configuration = sppasAppConfig()

    # ---------------------------------------------------------------------------

    def test_cfg_filename(self):
        # Return the name of the config file.
        y = self.__configuration.cfg_filename()
        self.assertIn(".app~", y)

    # ---------------------------------------------------------------------------

    def test_get_set_deps(self):
        self.__configuration.set_feature("first", True)
        y = self.__configuration.get_feature_ids()
        self.assertTrue("first" in y)

        self.__configuration.set_feature("second", True)
        y = self.__configuration.get_feature_ids()
        self.assertTrue("second" in y)

    # ---------------------------------------------------------------------------

    def test_feature_installed(self):
        """Return True if a dependency is installed"""
        self.assertFalse(self.__configuration.feature_installed("aaaa"))
        if os.path.exists(self.__configuration.cfg_filename()) is True:
            self.assertTrue(self.__configuration.feature_installed("wxpython"))
            self.assertTrue(self.__configuration.feature_installed("julius"))
