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

    scripts.channelsmixersimulator.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to get the maximum value of a mix between mono audio files.

"""

from argparse import ArgumentParser
import os
import sys

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.audiodata.aio
from sppas.src.audiodata.channelsmixer import sppasChannelMixer

# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w input files" % os.path.basename(PROGRAM),
                        description="... a script to get the minimum and maximum values"
                                    " of a mix between mono audio files.")

parser.add_argument("-w",
                    metavar="file",
                    nargs='+',
                    required=True,
                    help='Audio Input file names')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

mixer = sppasChannelMixer()

for inputFile in args.w:
    audio = sppas.src.audiodata.aio.open(inputFile)
    idx = audio.extract_channel(0)
    mixer.append_channel(audio.get_channel(idx))

print(mixer.get_minmax())
