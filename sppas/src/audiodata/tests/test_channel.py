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

    src.audiodata.tests.test_channel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os.path
import shutil

from sppas.src.config import paths
from sppas.src.wkps.fileutils import sppasFileUtils
from ..aio import open as audio_open
from ..aio import save as audio_save
from ..audio import sppasAudioPCM

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")   # mono
sample_2 = os.path.join(paths.samples, "samples-eng", "oriana3.wave")  # stereo
sample_3 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav")

# ---------------------------------------------------------------------------


class TestChannel(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)
        self._sample_1 = audio_open(sample_1)
        self._sample_2 = audio_open(sample_2)
        self._sample_3 = audio_open(sample_3)

    def tearDown(self):
        self._sample_1.close()
        shutil.rmtree(TEMP)

    def test_Extract(self):
        frames = self._sample_1.read_frames(self._sample_1.get_nframes())
        self._sample_1.rewind()
        cidx = self._sample_1.extract_channel(0)
        channel = self._sample_1.get_channel(cidx)
        self.assertEqual(len(frames)/self._sample_1.get_sampwidth(),
                         channel.get_nframes())
        self.assertEqual(frames, channel.get_frames())
        self.assertEqual(frames, channel.get_frames(channel.get_nframes()))

        frames = self._sample_2.read_frames(self._sample_2.get_nframes())
        frames_channel = b""
        sw = self._sample_2.get_sampwidth()
        # we are going to extract the channel number 2,
        # so we have to skip all frames which belong to the channel number 1
        for i in range(sw, len(frames),
                       sw * self._sample_2.get_nchannels()):
            frames_channel += frames[i:i+sw]
        self._sample_2.rewind()
        # Channel number 2 has index 1
        cidx = self._sample_2.extract_channel(1)
        channel = self._sample_2.get_channel(cidx)
        self.assertEqual(len(frames_channel)/self._sample_2.get_sampwidth(), channel.get_nframes())
        self.assertEqual(frames_channel, channel.get_frames())
        self.assertEqual(frames_channel, channel.get_frames(channel.get_nframes()))

    def test_GetFrames(self):
        self._sample_1.seek(1000)
        frames = self._sample_1.read_frames(500)
        self._sample_1.rewind()
        cidx = self._sample_1.extract_channel(0)
        channel = self._sample_1.get_channel(cidx)
        self.assertEqual(len(frames)/self._sample_1.get_sampwidth(), 500)
        channel.seek(1000)
        self.assertEqual(channel.tell(), 1000)
        self.assertEqual(frames, channel.get_frames(500))

    def test_Save(self):
        cidx = self._sample_1.extract_channel(0)
        channel = self._sample_1.get_channel(cidx)
        audio = sppasAudioPCM()
        audio.append_channel(channel)
        sample_new = os.path.join(TEMP, "converted.wav")
        audio_save(sample_new, audio)
        savedaudio = audio_open(sample_new)

        self._sample_1.rewind()
        frames = self._sample_1.read_frames(self._sample_1.get_nframes())
        saved_frames = savedaudio.read_frames(self._sample_1.get_nframes())
        self.assertEqual(len(frames), len(saved_frames))
        self.assertEqual(frames, saved_frames)

        savedaudio.close()
        os.remove(sample_new)

    def test_ExtractFragment(self):
        self._sample_1.extract_channel(0)
        self._sample_3.extract_channel(0)

        channel = self._sample_1.get_channel(0)
        newchannel = channel.extract_fragment(1*channel.get_framerate(), 2*channel.get_framerate())
        self.assertEqual(newchannel.get_nframes()/newchannel.get_framerate(), 1)
