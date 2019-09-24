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

    scripts.audioinfo.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to get information about an audio file.

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

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w file [options]" % os.path.basename(PROGRAM),
                        description="... a script to get information about an audio file.")

parser.add_argument(
    "--clip",
    action='store_true',
    help="Print the clipping values of the whole file")

parser.add_argument("-w",
                    metavar="file",
                    required=True,
                    help='Input audio file name')

parser.add_argument("-f",
                    metavar="value",
                    default=0.02,
                    type=float,
                    help='Frame duration to estimate rms values (default: 0.02)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audio = sppas.src.audiodata.aio.open(args.w)
audio.frameduration = args.f

print("Audio file name:     {:s}".format(args.w))
print("Duration (seconds):  {:f}".format(audio.get_duration()))
print("Frame rate (Hz):     {:d}".format(audio.get_framerate()))
print("Sample width (bits): {:d}".format(audio.get_sampwidth()*8))
nc = audio.get_nchannels()
print("Number of channels:  {:d}".format(nc))

if nc == 1:
    if args.clip:
        print("Clipping rate (in %):")
        for i in range(2, 9, 2):
            f = float(i)/10.
            c = audio.clipping_rate(f) * 100.
            print("  - factor={:.1f}:      {:.3f}".format(f, c))

    audiovol = sppasAudioVolume(audio, args.f)
    print("Volume:")
    print("  - min:           {:d}".format(audiovol.min()))
    print("  - max:           {:d}".format(audiovol.max()))
    print("  - mean:          {:.2f}".format(audiovol.mean()))
    print("  - median:        {:.2f}".format(audiovol.median()))
    print("  - stdev:         {:.2f}".format(audiovol.stdev()))
    print("  - coefvariation: {:.2f}".format(audiovol.coefvariation()))
    print("  - std err:       {:.2f}".format(audiovol.stderr()))

else:

    for n in range(nc):
        print("Channel {:d}".format(n))
        cidx = audio.extract_channel(n)
        channel = audio.get_channel(cidx)

        # Values related to amplitude
        frames = channel.get_frames(channel.get_nframes())
        ca = sppasAudioFrames(frames, channel.get_sampwidth(), 1)
        for i in range(2, 9, 2):
            f = float(i)/10.
            c = ca.clipping_rate(f) * 100.
            print("  - factor={:.1f}:      {:.3f}".format(f, c))

        # RMS (=volume)
        cv = sppasChannelVolume(channel)
        print("  Volume:")
        print("  - min:           {:d}".format(cv.min()))
        print("  - max:           {:d}".format(cv.max()))
        print("  - mean:          {:.2f}".format(cv.mean()))
        print("  - median:        {:.2f}".format(cv.median()))
        print("  - stdev:         {:.2f}".format(cv.stdev()))
        print("  - coefvariation: {:.2f}".format(cv.coefvariation()))
