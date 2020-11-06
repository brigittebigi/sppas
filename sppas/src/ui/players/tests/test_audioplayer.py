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

    src.audiodata.tests.test_audioplayer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import os.path

from sppas.src.config import paths

from ..audioplayer import sppasSimpleAudioPlayer

# ---------------------------------------------------------------------------

sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------


class TestMultiPlayer(unittest.TestCase):

    def test_load(self):
        """Test in loading multiple audio files."""
        vp = sppasSimpleAudioPlayer()

        loaded = vp.load("toto.xxx")   # Error 2005 extension not supported
        self.assertTrue(vp.get_filename(), "toto.xxx")
        self.assertFalse(loaded)

        loaded = vp.load(sample_1)
        self.assertTrue(vp.get_filename(), sample_1)
        self.assertTrue(loaded)

    # -----------------------------------------------------------------------

    def test_player_cv(self):
        mp = sppasSimpleAudioPlayer()
        mp.load(sample_1)
        mp.play()
