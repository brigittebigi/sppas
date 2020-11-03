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

    src.audiodata.tests.test_player.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import os.path
import time

from sppas.src.config import paths
from ..audioplayer import sppasSimpleAudioPlayer, sppasMultiAudioPlayer

# ---------------------------------------------------------------------------

sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")
sample_2 = os.path.join(paths.samples, "samples-eng", "oriana2.wav")
sample_3 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")
sample_4 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav")

# ---------------------------------------------------------------------------


class TestMultiPlayer(unittest.TestCase):

    def test_load(self):
        """Test in loading multiple audio files."""
        mp = sppasMultiAudioPlayer()
        self.assertEqual(0, len(mp))

        loaded = mp.load(sample_1)
        self.assertTrue(loaded)
        self.assertEqual(1, len(mp))
        self.assertTrue(mp.exists(sample_1))
        self.assertFalse(mp.exists(sample_2))

        loaded = mp.load("toto.xxx")   # Error 2005 extension not supported
        self.assertFalse(loaded)
        self.assertEqual(1, len(mp))

        loaded = mp.load("toto.wav")   # Error 2010
        self.assertFalse(loaded)
        self.assertEqual(1, len(mp))

        loaded = mp.load(sample_2)
        self.assertTrue(loaded)
        self.assertEqual(2, len(mp))
        self.assertTrue(mp.exists(sample_2))

    # -----------------------------------------------------------------------

    def test_remove(self):
        mp = sppasMultiAudioPlayer()
        mp.load(sample_1)
        mp.load(sample_2)
        mp.remove(sample_2)

        self.assertEqual(1, len(mp))
        self.assertTrue(mp.exists(sample_1))
        self.assertFalse(mp.exists(sample_2))

    # -----------------------------------------------------------------------

    def test_enable(self):
        mp = sppasMultiAudioPlayer()
        mp.load(sample_1)
        mp.load(sample_2)

        self.assertFalse(mp.is_enabled())
        self.assertFalse(mp.is_enabled(sample_1))
        self.assertFalse(mp.is_enabled(sample_2))
        self.assertFalse(mp.is_enabled(sample_3))

        mp.enable(sample_1, True)
        self.assertTrue(mp.is_enabled(sample_1))
        self.assertTrue(mp.is_enabled())

    # -----------------------------------------------------------------------

    def test_playing(self):
        mp = sppasMultiAudioPlayer()
        mp.load(sample_1)
        mp.load(sample_2)
        self.assertFalse(mp.are_playing())
        self.assertFalse(mp.is_playing())
        self.assertFalse(mp.is_playing(sample_1))

    # -----------------------------------------------------------------------

    def test_duration(self):
        sp1 = sppasSimpleAudioPlayer()
        sp1.load(sample_1)
        d1 = sp1.get_duration()
        del sp1
        sp2 = sppasSimpleAudioPlayer()
        sp2.load(sample_2)
        d2 = sp2.get_duration()
        del sp2

        mp = sppasMultiAudioPlayer()
        self.assertEqual(0., mp.get_duration())
        mp.load(sample_1)
        mp.load(sample_2)
        self.assertEqual(max(d1, d2), mp.get_duration())

    # -----------------------------------------------------------------------

    def test_player(self):
        mp = sppasMultiAudioPlayer()
        mp.load(sample_1)
        mp.load(sample_2)
        mp.load(sample_3)
        mp.load(sample_4)
        mp.enable(sample_1)
        mp.enable(sample_2)
        mp.enable(sample_3)
        mp.enable(sample_4)
        mp.play()
        time.sleep(3)
        mp.pause()
        mp.play()
        time.sleep(3)
        mp.stop()
