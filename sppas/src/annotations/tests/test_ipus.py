# -*- coding: UTF-8 -*-
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

    src.annotations.tests.test_ipus.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the SPPAS IPUs Segmentation

"""
import unittest
import struct

from sppas.src.annotations.SearchIPUs.silences import sppasSilences
from sppas.src.audiodata import sppasChannel

# ---------------------------------------------------------------------------


class TestSilences(unittest.TestCase):
    """Test the search of silences.

    """

    def setUp(self):
        # Create the samples.
        # with framerate=8000, our 8000 samples are representing 1 second.
        # 1 sample represents 0.000125 second.
        samples = [0] * 8000

        for i in range(2000, 3000):
            if i % 2:
                samples[i] = i - 2000
            else:
                samples[i] = -i + 2000

        for i in range(3000, 5000):
            if i % 2:
                samples[i] = 1000
            else:
                samples[i] = -1000

        for j, i in enumerate(range(5000, 6000)):
            if i % 2:
                samples[i] = 1000 - j
            else:
                samples[i] = -1000 + j

        # Convert samples into frames (divide the use of memory by 2 --only!)
        converted = b''.join(struct.pack('<h', elem) for elem in samples)

        self.channel = sppasChannel(
            framerate=8000, sampwidth=2, frames=str(converted)
        )

    # -----------------------------------------------------------------------

    def test_convert_frames_samples(self):

        # Create the samples.
        samples = [0] * 8000
        for i in range(2000, 3000):
            if i % 2:
                samples[i] = i - 2000
            else:
                samples[i] = -i + 2000
        for i in range(3000, 5000):
            if i % 2:
                samples[i] = 1000
            else:
                samples[i] = -1000
        for j, i in enumerate(range(5000, 6000)):
            if i % 2:
                samples[i] = 1000 - j
            else:
                samples[i] = -1000 + j

        # Convert samples into frames
        # pack interprets strings as packed binary data:
        #   - < little endian
        #   - h short (integer 2 bytes)
        frames = b''.join(struct.pack('<h', elem) for elem in samples)

        # Convert-back to samples
        data = list(struct.unpack("<{}h".format(len(frames) / 2), frames))

        # data should be the initial samples
        self.assertEqual(len(samples), len(data))
        for s, d in zip(samples, data):
            self.assertEqual(s, d)

    # -----------------------------------------------------------------------

    def test_vagueness(self):
        silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
        self.assertEqual(0.005, silences.get_vagueness())
        silences.set_vagueness(0.01)
        self.assertEqual(0.01, silences.get_vagueness())
        silences.set_vagueness(0.05)
        self.assertEqual(0.02, silences.get_vagueness())
        silences.set_vagueness(0.005)
        self.assertEqual(0.005, silences.get_vagueness())

    # -----------------------------------------------------------------------

    def test_channel(self):
        silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
        self.assertEqual(self.channel, silences._channel)
        cha = sppasChannel()
        silences.set_channel(cha)
        self.assertEqual(cha, silences._channel)

    # -----------------------------------------------------------------------

    def test_vols(self):
        silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
        # there are 160 samples in a window of 20ms.
        # so we'll estimate 8000/160 = 50 rms values
        rms = silences.get_volstats()
        self.assertEqual(50, len(rms))
        # The 2000 first and last samples are 0. so rms is also 0.
        for i in range(12):
            self.assertEqual(0, rms[i])
            self.assertEqual(0, rms[50-i-1])
        # Others are positive values
        for i in range(13, 50-12):
            self.assertGreater(rms[i], 0)

    # -----------------------------------------------------------------------

    def test_fix_threshold_vol(self):
        silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
        threshold = silences.fix_threshold_vol()
        self.assertEqual(201, threshold)

    # -----------------------------------------------------------------------

    def test_search_silences(self):
        silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
        threshold = silences.fix_threshold_vol()
        th = silences.search_silences(threshold)
        self.assertEqual(th, threshold)
        # we have to found 2 silences: at the beginning and at the end
        self.assertEqual(2, len(silences))
        self.assertEqual((0, 2080), silences[0])
        self.assertEqual((5760, 8000), silences[1])

    # -----------------------------------------------------------------------

    def test_extract_tracks(self):
        silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
        silences.search_silences()
        self.assertEqual(2, len(silences))
        tracks = silences.extract_tracks(min_track_dur=0.2,
                                         shift_dur_start=0.,
                                         shift_dur_end=0.)
        self.assertEqual(1, len(tracks))
        self.assertEqual((2080, 5760), tracks[0])

# ---------------------------------------------------------------------------

