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

    src.plugins.tests.test_plugin.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import os

from sppas import u
from ..plugin import sppasPluginParam

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestPluginParam(unittest.TestCase):

    def setUp(self):
        self.param = sppasPluginParam(DATA, "plugin.json")

    def test_getters(self):
        self.assertEqual(self.param.get_key(), "pluginid")
        self.assertEqual(self.param.get_name(), "The Plugin Name")
        self.assertEqual(self.param.get_descr(), "Performs something on some files.")
        self.assertEqual(self.param.get_icon(), "")

        opt = self.param.get_options()
        self.assertEqual(len(opt), 3)

        self.assertEqual(opt[0].get_key(), "-b")
        self.assertEqual(opt[1].get_key(), "--show-progress")
        self.assertEqual(opt[2].get_key(), "-i")
        self.assertEqual(opt[2].get_value(), u('C:\Windows'))
