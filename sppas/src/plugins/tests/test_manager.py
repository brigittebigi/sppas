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

    src.plugins.tests.test_manager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import os

from sppas import paths
from ..manager import sppasPluginsManager

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
soxplugin = os.path.join(DATA, "soxplugintest.zip")
sample = os.path.join(paths.samples, "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------


class TestPluginsManager(unittest.TestCase):

    def setUp(self):
        self.manager = sppasPluginsManager()

    def test_all(self):

        # some plugins are already installed in the package of SPPAS
        plg = 6
        self.assertEqual(plg, len(self.manager.get_plugin_ids()))

        # Install a plugin
        soxid = self.manager.install(soxplugin, "SoX")
        self.assertEqual(plg+1, len(self.manager.get_plugin_ids()))

        # Use it!
        output = sample.replace('.wav', '-converted.wav')
        p = self.manager.get_plugin(soxid)
        message = self.manager.run_plugin(soxid, [sample])

        # Delete it...
        self.manager.delete(soxid)
        self.assertEqual(plg, len(self.manager.get_plugin_ids()))

        # Test result of the run
        self.assertGreater(len(message), 0)
        self.assertTrue(os.path.exists(output))
        os.remove(output)
