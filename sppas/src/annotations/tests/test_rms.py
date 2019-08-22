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


"""

import unittest
import os

import sppas.src.audiodata.aio
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasTier

from ..RMS.irms import IntervalsRMS
from ..RMS.sppasrms import sppasRMS

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestIntervalsRMS(unittest.TestCase):
    """Test of the rms estimator on intervals.

    """

    def setUp(self):
        audio_speech = sppas.src.audiodata.aio.open(
            os.path.join(DATA, "oriana1.wav")
        )
        n = audio_speech.get_nchannels()
        if n != 1:
            raise IOError("An audio file with only one channel is expected. "
                          "Got {:d} channels.".format(n))

        # Extract the channel and set it to the RMS estimator
        idx = audio_speech.extract_channel(0)
        self.channel = audio_speech.get_channel(idx)

    def test_estimator(self):
        estimator = IntervalsRMS()
        self.assertEqual(0, estimator.get_rms())
        self.assertEqual(list(), estimator.get_values())

        estimator.set_channel(self.channel)
        self.assertEqual(0, estimator.get_rms())
        self.assertEqual(list(), estimator.get_values())

        estimator.estimate(0., self.channel.get_duration())
        self.assertEqual(359.631, round(estimator.get_fmean(), 3))
        self.assertEqual(696, round(estimator.get_rms(), 3))

        # only on silence (at the beginning)
        estimator.estimate(0., 0.7)
        self.assertEqual(2, estimator.get_rms())
        self.assertEqual(1.757, round(estimator.get_fmean(), 3))
        estimator.estimate(0., 1.4)
        self.assertEqual(2, estimator.get_rms())
        self.assertEqual(1.757, round(estimator.get_fmean(), 3))

        # only speech
        estimator.estimate(1.4, 2.4)
        self.assertEqual(1069, estimator.get_rms())
        self.assertEqual(633.21, round(estimator.get_fmean(), 3))
        estimator.estimate(2.4, 3.4)
        self.assertEqual(1228, estimator.get_rms())
        self.assertEqual(953.83, round(estimator.get_fmean(), 3))

    def test_sppasrms(self):
        rms = sppasRMS()
        rms.set_tiername("Tokens")
        audio_file = os.path.join(DATA, "oriana1.wav")
        trs_file = os.path.join(DATA, "oriana1-token.xra")
        out = rms.run([audio_file, trs_file], None, None)
