# -*- coding:utf-8 -*-
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

    src.audiodata.tests.test_audio.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os.path

from sppas.src.config import paths

from ..aio import open as audio_open
from ..audio import sppasAudioPCM
from ..audiodataexc import ChannelIndexError, AudioError

sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")
sample_3 = os.path.join(paths.samples, "samples-eng", "oriana3.wave")

# ---------------------------------------------------------------------------


class TestAudioPCM(unittest.TestCase):

    def test_set_get(self):
        """Test open/close get_channels/get_audiofp."""

        a1 = audio_open(sample_1)
        a3 = sppasAudioPCM()
        a3.set(a1)
        x = a1.get_channels()
        y = a1.get_audiofp()
        self.assertEqual(x, a3.get_channels())
        self.assertEqual(y, a3.get_audiofp())
        a1.close()
        self.assertIsNone(a1.get_audiofp())
        self.assertEqual(x, a3.get_channels())
        self.assertEqual(y, a3.get_audiofp())
        a3.close()
        self.assertIsNone(a3.get_audiofp())

    # -----------------------------------------------------------------------

    def test_channels(self):
        """Test extract_channel/get_channel/append_channel/verify_channels/pop_channel/remove_channel."""
        a1 = audio_open(sample_1)
        a2 = sppasAudioPCM()
        a3 = audio_open(sample_3)

        with self.assertRaises(AudioError):
            a2.extract_channel(0)
        with self.assertRaises(ChannelIndexError):
            a1.extract_channel(2)
        cidx1 = a3.extract_channel()
        cidx2 = a3.extract_channel(1)
        c1 = a3.get_channel(cidx1)
        c2 = a3.get_channel(cidx2)
        self.assertEqual(0, a2.append_channel(c1))
        self.assertEqual(1, a2.append_channel(c2))
        a2.insert_channel(0, c1)
        self.assertTrue(a2.verify_channels())
        a2.pop_channel(2)
        self.assertEqual(2, a2.get_nchannels())
        a2.remove_channel(c1)
        self.assertEqual(1, a2.get_nchannels())

    def test_getters(self):
        """Test get_nchannels/get_sampwidth/get_framerate/get_nframes/get_duration."""
        a1 = audio_open(sample_1)
        self.assertEqual(1, a1.get_nchannels())
        self.assertEqual(2, a1.get_sampwidth())
        self.assertEqual(16000, a1.get_framerate())
        self.assertEqual(284672, a1.get_nframes())
        self.assertEqual(17.792, round(a1.get_duration(), 3))
        a1.extract_channels()
        a1.close()
        self.assertEqual(1, a1.get_nchannels())
        self.assertEqual(2, a1.get_sampwidth())
        self.assertEqual(16000, a1.get_framerate())
        self.assertEqual(284672, a1.get_nframes())
        self.assertEqual(17.792, round(a1.get_duration(), 3))

    def test_audio_estimators(self):
        """Test rms/clipping_rate."""
        a1 = audio_open(sample_1)
        a1.extract_channels()
        self.assertEqual(696, a1.rms())
        self.assertEqual(0.01, round(a1.clipping_rate(0.1), 2))
        a1.close()

    def test_incoming(self):
        """Test seek/tell/rewind / read/read_samples/read_frames."""
        a1 = audio_open(sample_1)

        frames = a1.read()
        self.assertEqual(284672 * 2, len(frames))
        self.assertEqual(284672, a1.tell())
        reframes = a1.read()
        self.assertEqual(0, len(reframes))
        a1.rewind()
        self.assertEqual(0, a1.tell())
        frames = a1.read_frames(100)
        self.assertEqual(100 * 2, len(frames))
        self.assertEqual(100, a1.tell())

        samples1 = a1.read_samples(100)
        self.assertEqual(100, len(samples1[0]))  # samples is a list of list of data
        self.assertEqual(200, a1.tell())
        a1.seek(100)
        samples2 = a1.read_samples(100)
        self.assertEqual(samples1, samples2)

        a1.close()
