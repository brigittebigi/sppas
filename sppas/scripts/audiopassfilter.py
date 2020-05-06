#!/usr/bin/env python
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

    scripts.audiopassfilter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to apply high-pass filter (development version).

"""

import sys
import os.path
from argparse import ArgumentParser
import struct, math

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.audiodata.aio
from sppas.src.audiodata.channel import sppasChannel
from sppas.src.audiodata.audio import sppasAudioPCM

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -o output file [options]" % os.path.basename(PROGRAM),
                        description="... a script to apply high-pass filter (development version).")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Audio Input file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Audio Output file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audioin = sppas.src.audiodata.aio.open(args.i)
SAMPLE_RATE = audioin.get_framerate()

# ----------------------------------------------------------------------------

# IIR filter coefficients
freq = 2000 # Hz
r = 0.98
a1 = -2.0 * r * math.cos(freq / (SAMPLE_RATE / 2.0) * math.pi)
a2 = r * r
filter = [a1, a2]
print(filter)

n = audioin.get_nframes()
original = struct.unpack('%dh' % n, audioin.read_frames(n))
original = [s / 2.0**15 for s in original]

result = [0 for i in range(0, len(filter))]
biggest = 1
for sample in original:
        for cpos in range(0, len(filter)):
            sample -= result[len(result) - 1 - cpos] * filter[cpos]
        result.append(sample)
        biggest = max(abs(sample), biggest)

result = [sample / biggest for sample in result]
result = [int(sample * (2.0**15 - 1)) for sample in result]

# ----------------------------------------------------------------------------

audioout = sppasAudioPCM()
channel = sppasChannel(framerate=SAMPLE_RATE,
                       sampwidth=audioin.get_sampwidth(),
                       frames=struct.pack('%dh' % len(result), *result))
audioout.append_channel(channel)
sppas.src.audiodata.aio.save(args.o, audioout)
