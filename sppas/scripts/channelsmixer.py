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

    scripts.channelsmixer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to mix channels from mono audio files in one channel

"""

from argparse import ArgumentParser
import os
import sys

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.audiodata.aio
from sppas.src.audiodata.channelsmixer import sppasChannelMixer
from sppas.src.audiodata import sppasAudioPCM

# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w input file -o output file [options]" % os.path.basename(PROGRAM),
                        description="... a script to mix channels from mono audio files in one channel.")

parser.add_argument("-w",
                    metavar="file",
                    nargs='+',
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

mixer = sppasChannelMixer()

for inputFile in args.w:
    audio = sppas.src.audiodata.aio.open(inputFile)
    idx = audio.extract_channel(0)
    mixer.append_channel(audio.get_channel(idx))

new_channel = mixer.mix()

# Save the converted channel
audio_out = sppasAudioPCM()
audio_out.append_channel(new_channel)
sppas.src.audiodata.aio.save(args.o, audio_out)
