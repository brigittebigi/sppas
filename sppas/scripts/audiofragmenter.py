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

    scripts.audiofragmenter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to extract a fragment of an audio file.

"""

from argparse import ArgumentParser
import os
import sys

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.audiodata.aio
from sppas.src.audiodata.audio import sppasAudioPCM

# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w input file -o output file [OPTIONS]" % os.path.basename(PROGRAM),
                        description="... a script to extract a fragment of an audio file.")

parser.add_argument("-w",
                    metavar="file",
                    required=True,
                    help='Audio Input file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Audio Output file name')

parser.add_argument("-bs",
                    default=0,
                    metavar="value",
                    type=float,
                    help='The position (in seconds) when begins the mix, don\'t use with -bf')

parser.add_argument("-es",
                    default=0,
                    metavar="value",
                    type=float,
                    help='The position (in seconds) when ends the mix, don\'t use with -ef')

parser.add_argument("-bf",
                    default=0,
                    metavar="value",
                    type=float,
                    help='The position (in number of frames) when begins the mix, don\'t use with -bs')

parser.add_argument("-ef",
                    default=0,
                    metavar="value",
                    type=float,
                    help='The position (in number of frames) when ends the mix, don\'t use with -es')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audio_out = sppasAudioPCM()
audio = sppas.src.audiodata.aio.open(args.w)

if args.bf and args.bs:
    print("bf option and bs option can't be used at the same time!")
    sys.exit(1)

if args.ef and args.es:
    print("ef option and es option can't be used at the same time!")
    sys.exit(1)

if args.bf:
    begin = args.bf
elif args.bs:
    begin = args.bs*audio.get_framerate()
else:
    begin = 0
if args.ef:
    end = args.ef
elif args.es:
    end = args.es*audio.get_framerate()
else:
    end = 0

for i in range(audio.get_nchannels()):
    idx = audio.extract_channel(i)
    audio.rewind()
    channel = audio.get_channel(idx)
    extracter = channel.extract_fragment(begin, end)
    audio_out.append_channel(extracter)

sppas.src.audiodata.aio.save(args.o, audio_out)
