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

    src.ui.players.tests.test_videoplayer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import time
import os.path

from sppas.src.config import paths

from ..audioplayer import sppasSimpleAudioPlayer
from ..mmplayer import sppasMultiMediaPlayer

# ---------------------------------------------------------------------------

sample_video = os.path.join(paths.samples, "faces", "video_sample.mp4")

# ---------------------------------------------------------------------------

sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")
sample_2 = os.path.join(paths.samples, "samples-eng", "oriana2.WAV")
sample_3 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")
sample_4 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav")

# ---------------------------------------------------------------------------


class TestMultiPlayer(unittest.TestCase):

    def test_load(self):
        """Test in loading multiple audio files."""
        mp = sppasMultiMediaPlayer()
        self.assertEqual(0, len(mp))

        loaded = mp.add_audio(sample_1)
        self.assertTrue(loaded)
        self.assertEqual(1, len(mp))
        self.assertTrue(mp.exists(sample_1))
        self.assertFalse(mp.exists(sample_2))

        loaded = mp.add_audio("toto.xxx")   # Error 2005 extension not supported
        self.assertFalse(loaded)
        self.assertEqual(2, len(mp))
        self.assertTrue(mp.is_unknown("toto.xxx"))

        loaded = mp.add_audio("toto.wav")   # Error 2010
        self.assertFalse(loaded)
        self.assertEqual(3, len(mp))
        self.assertTrue(mp.is_unknown("toto.wav"))

        loaded = mp.add_audio(sample_2)
        self.assertTrue(loaded)
        self.assertEqual(4, len(mp))
        self.assertTrue(mp.exists(sample_2))

        loaded = mp.add_video(sample_video)
        self.assertTrue(loaded)
        self.assertEqual(5, len(mp))
        self.assertTrue(mp.exists(sample_video))

    # -----------------------------------------------------------------------

    def test_remove(self):
        mp = sppasMultiMediaPlayer()
        mp.add_audio(sample_1)
        mp.add_audio(sample_2)
        mp.remove(sample_2)

        self.assertEqual(1, len(mp))
        self.assertTrue(mp.exists(sample_1))
        self.assertFalse(mp.exists(sample_2))

    # -----------------------------------------------------------------------

    def test_enable(self):
        mp = sppasMultiMediaPlayer()
        mp.add_audio(sample_1)
        mp.add_audio(sample_2)

        self.assertFalse(mp.is_enabled())
        self.assertFalse(mp.is_enabled(sample_1))
        self.assertFalse(mp.is_enabled(sample_2))
        self.assertFalse(mp.is_enabled(sample_3))

        mp.enable(sample_1, True)
        self.assertTrue(mp.is_enabled(sample_1))
        self.assertTrue(mp.is_enabled())

    # -----------------------------------------------------------------------

    def test_playing(self):
        mp = sppasMultiMediaPlayer()
        mp.add_audio(sample_1)
        mp.add_audio(sample_2)
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

        mp = sppasMultiMediaPlayer()
        self.assertEqual(0., mp.get_duration())
        mp.add_audio(sample_1)
        mp.add_audio(sample_2)
        self.assertEqual(max(d1, d2), mp.get_duration())

    # -----------------------------------------------------------------------

    def test_player_audio(self):
        mp = sppasMultiMediaPlayer()
        mp.add_audio(sample_1)
        mp.add_audio(sample_2)
        mp.add_audio(sample_3)
        mp.add_audio(sample_4)
        mp.enable(sample_1)
        mp.enable(sample_2)
        mp.enable(sample_3)
        mp.enable(sample_4)

        mp.play_interval(10., 13.)
        time.sleep(4)
        mp.stop()
        mp.play()  # will play the same period of time than the previous one
        time.sleep(3)
        mp.stop()

    # -----------------------------------------------------------------------

    def test_player_video(self):
        mp = sppasMultiMediaPlayer()
        mp.add_video(sample_video)
        mp.enable(sample_video)
        mp.play_interval(10., 13.)

