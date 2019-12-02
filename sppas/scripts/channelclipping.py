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

    scripts.channelclipping.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to get clipping rates of a channel of an audio file.

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas.src.audiodata.aio
from sppas.src.audiodata.audiovolume import sppasAudioVolume
from sppas.src.audiodata.channelvolume import sppasChannelVolume
from sppas.src.audiodata.audioframes import sppasAudioFrames

# ---------------------------------------------------------------------------
# Verify and extract args:
# ---------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w file [options]" % os.path.basename(PROGRAM),
                        description="... a script to get clipping information "
                                    "about a channel of an audio file.")

parser.add_argument("-w",
                    metavar="file",
                    required=True,
                    help='Input audio file name')

parser.add_argument("-c",
                    metavar="channel",
                    required=False,
                    default=0,
                    type=int,
                    help='Channel number (default=0)')

parser.add_argument("-f",
                    metavar="from",
                    required=False,
                    default=0.,
                    type=float,
                    help='From time (default=0.)')

parser.add_argument("-t",
                    metavar="to",
                    required=False,
                    default=0.,
                    type=float,
                    help='To time (default=channel duration)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ---------------------------------------------------------------------------

print("Open the audio file {:s}".format(args.w))
audio = sppas.src.audiodata.aio.open(args.w)
print("Extract channel number {:d}".format(args.c))
idx = audio.extract_channel(args.c)
channel = audio.get_channel(idx)

# ---------------------------------------------------------------------------

if args.f == 0. and args.t == 0.:
    fragment = channel

else:
    from_frame = int(args.f * float(channel.get_framerate()))
    to_time = args.t
    if args.t == 0.:
        to_time = channel.get_duration()
    to_frame = int(to_time * float(channel.get_framerate()))
    print("Extract the frames of the channel "
          "from {:f} to {:f}".format(args.f, to_time))
    fragment = channel.extract_fragment(begin=from_frame, end=to_frame)

# ---------------------------------------------------------------------------

print("Evaluate clipping rate (in %):")

c = fragment.clipping_rate(0.1) * 100.
if c == 0.:
    # This should be silence
    for i in range(1, 10, 2):
        f = float(i) / 100.
        c = fragment.clipping_rate(f) * 100.
        print("  - factor={:.2f}:    {:.3f}".format(f, c))
        if c == 0.:
            break

else:
    # This should be speech
    for i in range(2, 20, 2):
        f = float(i) / 20.
        c = fragment.clipping_rate(f) * 100.
        print("  - factor={:.1f}:    {:.3f}".format(f, c))
        if c == 0.:
            break

