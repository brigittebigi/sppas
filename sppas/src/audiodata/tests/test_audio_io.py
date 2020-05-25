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

    src.audiodata.tests.test_audio_io.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os.path
import shutil

from sppas.src.config import paths

from ..aio import open as audio_open
from ..aio import save as audio_save
from ..aio import save_fragment as audio_save_fragment

from sppas.src.wkps.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")
sample_2 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav")
sample_3 = os.path.join(paths.samples, "samples-eng", "oriana3.wave")

# ---------------------------------------------------------------------------


class TestInformation(unittest.TestCase):

    def setUp(self):
        self._sample_1 = audio_open(sample_1)
        self._sample_2 = audio_open(sample_2)
        self._sample_3 = audio_open(sample_3)

    def tearDown(self):
        self._sample_1.close()
        self._sample_2.close()
        self._sample_3.close()

    def test_GetSampwidth(self):
        self.assertEqual(self._sample_1.get_sampwidth(), 2)
        self.assertEqual(self._sample_2.get_sampwidth(), 2)
        self.assertEqual(self._sample_3.get_sampwidth(), 2)

    def test_GetChannel(self):
        self.assertEqual(self._sample_1.get_nchannels(), 1)
        self.assertEqual(self._sample_2.get_nchannels(), 1)
        self.assertEqual(self._sample_3.get_nchannels(), 2)

    def test_GetFramerate(self):
        self.assertEqual(self._sample_1.get_framerate(), 16000)
        self.assertEqual(self._sample_2.get_framerate(), 44100)
        self.assertEqual(self._sample_3.get_framerate(), 16000)

# ---------------------------------------------------------------------------


class TestData(unittest.TestCase):

    def setUp(self):
        self._sample_1 = audio_open(sample_1)
        self._sample_2 = audio_open(sample_2)
        self._sample_3 = audio_open(sample_3)
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        self._sample_1.close()
        self._sample_2.close()
        self._sample_3.close()
        shutil.rmtree(TEMP)

    def test_ReadFrames(self):
        self.assertEqual(len(self._sample_1.read_frames(self._sample_1.get_nframes())), 
                         self._sample_1.get_nframes()*self._sample_1.get_sampwidth()*self._sample_1.get_nchannels())
        self.assertEqual(len(self._sample_2.read_frames(self._sample_2.get_nframes())), 
                         self._sample_2.get_nframes()*self._sample_2.get_sampwidth()*self._sample_2.get_nchannels())
        self.assertEqual(len(self._sample_3.read_frames(self._sample_3.get_nframes())), 
                         self._sample_3.get_nframes()*self._sample_3.get_sampwidth()*self._sample_3.get_nchannels())
        # self.assertEqual(len(self._sample_4.read_frames(self._sample_4.get_nframes())),(self._sample_4.get_nframes()*self._sample_4.get_sampwidth()*self._sample_4.get_nchannels()))

    def test_ReadSamples(self):
        samples = self._sample_1.read_samples(self._sample_1.get_nframes())
        self.assertEqual(len(samples), 1)
        self.assertEqual(len(samples[0]), self._sample_1.get_nframes())

        samples = self._sample_2.read_samples(self._sample_2.get_nframes())
        self.assertEqual(len(samples), 1)
        self.assertEqual(len(samples[0]), self._sample_2.get_nframes())

        samples = self._sample_3.read_samples(self._sample_3.get_nframes())
        self.assertEqual(len(samples), 2)
        self.assertEqual(len(samples[0]), self._sample_3.get_nframes())
        self.assertEqual(len(samples[1]), self._sample_3.get_nframes())

    def test_WriteFrames(self):
        _sample_new = os.path.join(TEMP, "new_file.wav")

        # save first
        audio_save(_sample_new, self._sample_1)
        # read the saved file and compare Audio() instances
        new_file = audio_open(_sample_new)
        self.assertEqual(new_file.get_framerate(), self._sample_1.get_framerate())
        self.assertEqual(new_file.get_sampwidth(), self._sample_1.get_sampwidth())
        self.assertEqual(new_file.get_nchannels(), self._sample_1.get_nchannels())
        self.assertEqual(new_file.get_nframes(), self._sample_1.get_nframes())
        new_file.close()
        os.remove(_sample_new)
        self._sample_1.rewind()

        audio_save_fragment(_sample_new, self._sample_1, self._sample_1.read_frames(self._sample_1.get_nframes()))
        new_file = audio_open(_sample_new)
        self.assertEqual(new_file.get_framerate(), self._sample_1.get_framerate())
        self.assertEqual(new_file.get_sampwidth(), self._sample_1.get_sampwidth())
        self.assertEqual(new_file.get_nchannels(), self._sample_1.get_nchannels())
        self.assertEqual(new_file.get_nframes(), self._sample_1.get_nframes())
        new_file.close()
        os.remove(_sample_new)

        _sample_new = os.path.join(TEMP, "new_file.wav")
        # save first
        audio_save(_sample_new, self._sample_3)
        # read the saved file and compare Audio() instances
        new_file = audio_open(_sample_new)
        self.assertEqual(new_file.get_framerate(), self._sample_3.get_framerate())
        self.assertEqual(new_file.get_sampwidth(), self._sample_3.get_sampwidth())
        self.assertEqual(new_file.get_nchannels(), self._sample_3.get_nchannels())
        self.assertEqual(new_file.get_nframes(), self._sample_3.get_nframes())
        new_file.close()
        os.remove(_sample_new)
        self._sample_3.rewind()

        audio_save_fragment(_sample_new, self._sample_3, self._sample_3.read_frames(self._sample_3.get_nframes()))
        new_file = audio_open(_sample_new)
        self.assertEqual(new_file.get_framerate(), self._sample_3.get_framerate())
        self.assertEqual(new_file.get_sampwidth(), self._sample_3.get_sampwidth())
        self.assertEqual(new_file.get_nchannels(), self._sample_3.get_nchannels())
        self.assertEqual(new_file.get_nframes(), self._sample_3.get_nframes())
        new_file.close()
        os.remove(_sample_new)

    def test_not_read(self):
        with self.assertRaises(TypeError):
            audio_open(os.path.join(TEMP, "new_file.toto"))
        with self.assertRaises(IOError):
            audio_open(os.path.join(TEMP, "nofile.wav"))
        try:
            audio_open(os.path.join(TEMP, "new_file.toto"))
        except TypeError as e:
            self.assertTrue(":ERROR 2005:" in str(e))
        try:
            audio_open(os.path.join(TEMP, "nofile.wav"))
        except IOError as e:
            self.assertTrue(":ERROR 2010:" in str(e))

    def test_save_wav(self):
        self._sample_1.rewind()
        self._sample_1.extract_channel(0)
        channel_ref = self._sample_1.get_channel(0)
        frames_ref = self._sample_1.read_frames(100)
        samples_ref = self._sample_1.read_samples(100)

        # save/read the file and compare samples
        audio_save(os.path.join(TEMP, "new_file.wav"), self._sample_1)
        new_audio = audio_open(os.path.join(TEMP, "new_file.wav"))
        self.assertEqual(new_audio.get_framerate(), self._sample_1.get_framerate())
        self.assertEqual(new_audio.get_sampwidth(), self._sample_1.get_sampwidth())
        self.assertEqual(new_audio.get_nchannels(), self._sample_1.get_nchannels())
        self.assertEqual(new_audio.get_nframes(), self._sample_1.get_nframes())

        new_audio.extract_channel(0)
        channel_read = new_audio.get_channel(0)
        frames_read = new_audio.read_frames(100)
        samples_read = new_audio.read_samples(100)

        self.assertEqual(channel_ref.get_nframes(), channel_read.get_nframes())
        self.assertEqual(samples_ref, samples_read)
        self.assertEqual(frames_ref, frames_read)
