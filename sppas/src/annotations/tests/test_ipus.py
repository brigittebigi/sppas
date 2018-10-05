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

    src.annotations.tests.test_normalize.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the SPPAS IPUs Segmentation

"""
import unittest
import os.path
import struct
import sys

from sppas.src.config import paths

from sppas.src.anndata import sppasTranscription
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

        for i in range(2000, 2999):
            samples[i] = i - 2000

        for i in range(3000, 4999):
            samples[i] = 1000

        for j, i in enumerate(range(5000, 5999)):
            samples[i] = 1000-j

        # Convert samples into frames (divide the use of memory by 2 --only!)
        frames = ""
        for i in samples:
                frames = frames + struct.pack("<h", samples[i])

        self.channel = sppasChannel(
            framerate=8000, sampwidth=2, frames=frames
        )

    # -----------------------------------------------------------------------

    def test_convert_frames_samples(self):

        # Create the samples.
        samples = [0] * 8000
        for i in range(2000, 2999):
            samples[i] = i - 2000
        for i in range(3000, 4999):
            samples[i] = 1000
        for j, i in enumerate(range(5000, 5999)):
            samples[i] = 1000 - j

        # Convert samples into frames (divide the use of memory by 2 --only!)
        frames = ""
        for i in samples:
            frames = frames + struct.pack("<h", samples[i])

        # Convert-back to samples
        data = list(struct.unpack("<%uh" % (len(frames) / 2), frames))

        # data should be the initial samples
        self.assertEquals(samples, data)

    # -----------------------------------------------------------------------
    #
    # def test_vagueness(self):
    #     silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
    #     self.assertEquals(0.005, silences.get_vagueness())
    #     silences.set_vagueness(0.01)
    #     self.assertEquals(0.01, silences.get_vagueness())
    #     silences.set_vagueness(0.05)
    #     self.assertEquals(0.02, silences.get_vagueness())
    #     silences.set_vagueness(0.005)
    #     self.assertEquals(0.005, silences.get_vagueness())
    #
    # # -----------------------------------------------------------------------
    #
    # def test_channel(self):
    #     silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
    #     self.assertEquals(self.channel, silences._channel)
    #     cha = sppasChannel()
    #     silences.set_channel(cha)
    #     self.assertEquals(cha, silences._channel)
    #
    # # -----------------------------------------------------------------------
    #
    # def test_vols(self):
    #     silences = sppasSilences(self.channel, win_len=0.020, vagueness=0.005)
    #     # there are 160 samples in a window of 20ms.
    #     # so we'll estimate 8000/160 = 50 rms values
    #     rms = silences.get_volstats()
    #     self.assertEquals(50, len(rms))
    #     # PROBLEM: ALL VALUES ARE 0
