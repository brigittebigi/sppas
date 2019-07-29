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

    src.plugins.tests.test_process.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os

from sppas import paths

from ..plugin import sppasPluginParam
from ..process import sppasPluginProcess

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
sample = os.path.join(paths.samples, "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------


class TestPluginProcess(unittest.TestCase):

    def setUp(self):
        param = sppasPluginParam(DATA, "plugin.json")
        self.process = sppasPluginProcess(param)

    def test_run(self):
        self.process.run(sample)
        # time.sleep(0.8)
        # self.process.stop()
        line = self.process.communicate()
        # we'll get the usage of the sox command:
        self.assertGreater(len(line), 10)
