#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2018  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# audioseg.py
# ---------------------------------------------------------------------------

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

if os.path.exists(SPPAS) is False:
    print("ERROR: SPPAS not found.")
    sys.exit(1)
sys.path.append(SPPAS)

from sppas.src.utils.makeunicode import sppasUnicode
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasRW
from sppas.src.anndata.aio.aioutils import serialize_labels
import sppas.src.audiodata.aio
from sppas.src.audiodata.audio import sppasAudioPCM
from sppas.src.annotations.searchtier import sppasFindTier

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file".format(os.path.basename(PROGRAM)),
                        description="... a program to "
                                    "segment an audio file into tracks.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input audio file name.')

parser.add_argument("-t",
                    metavar="tier",
                    required=False,
                    help="Name of the tier indicating the tracks.")

parser.add_argument("-e",
                    metavar="ext",
                    required=False,
                    default=".xra",
                    help='File extension for the tracks (default:.xra).')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Load input data

# Open the audio and check it
try:
    audio = sppas.src.audiodata.aio.open(args.i)
except Exception as e:
    print(str(e))
    sys.exit(1)
if audio.get_nchannels() > 1:
    print('AudioSegmenter supports only mono audio files.')
    sys.exit(1)

# fix the annotated data filename
filename = os.path.splitext(args.i)[0]
ann = None
for ext in sppas.src.anndata.aio.extensions:
    ann = filename + ext
    if os.path.exists(ann):
        break
if ann is None:
    print('No annotated data corresponding to the audio file {:s}.'
          ''.format(args.i))
    sys.exit(1)

# Load annotated data
try:
    parser = sppasRW(ann)
    trs_input = parser.read()
except Exception as e:
    print(str(e))
    sys.exit(1)

# ----------------------------------------------------------------------------
# Extract the data we'll work on

# Extract the tier
if args.t:
    tier = trs_input.find(args.t, case_sensitive=False)
    if tier is None:
        print("Tier {:s} not found.".format(args.t))
        sys.exit(1)
else:
    try:
        tier = sppasFindTier.transcription(trs_input)
    except:
        print('A tier with IPUs or a transcription is required to indicate '
              'the tracks. Tier not found.')
        sys.exit(1)

# Extract the channel
audio.extract_channel(0)
channel = audio.get_channel(0)
audio.rewind()
framerate = channel.get_framerate()

# ----------------------------------------------------------------------------
# Prepare output

tier_name = sppasUnicode(tier.get_name()).to_ascii()

# output directory
output_dir = filename + "-" + tier_name
if os.path.exists(output_dir):
    print("A directory with name {:s} is already existing.".format(output_dir))
    sys.exit(1)
os.mkdir(output_dir)
if not args.quiet:
    print("The output directory {:s} was created.".format(output_dir))

# ----------------------------------------------------------------------------
# Split the data into tracks

nb = 0
for i, ann in enumerate(tier):

    # is a track? if yes, extract the text content!
    text = serialize_labels(ann.get_labels(), separator="_", empty="", alt=False)
    if len(text) == 0 or ann.get_best_tag().is_silence():
        continue

    # get localization information
    begin = ann.get_lowest_localization().get_midpoint()
    end = ann.get_highest_localization().get_midpoint()

    # fix base name of autio/trs files
    su = sppasUnicode(text)
    su.clear_whitespace()
    text_ascii = su.to_ascii()
    text_ascii = text_ascii[:29]  # to limit the size of the filename...
    idx = "{:04d}".format(i+1)
    fn = os.path.join(output_dir, idx + "_" + text_ascii)
    if not args.quiet:
        print('* track {:s} from {:f} to {:f}'.format(idx, begin, end))

    # create audio output
    extracter = channel.extract_fragment(int(begin*framerate),
                                         int(end*framerate))
    audio_out = sppasAudioPCM()
    audio_out.append_channel(extracter)
    if not args.quiet:
        print("   - audio: " + fn + ".wav")
    sppas.src.audiodata.aio.save(fn + ".wav", audio_out)

    # create text output (copy original label as it!)
    trs_output = sppasTranscription("TrackSegment")
    tracks_tier = trs_output.create_tier(tier_name + "-" + idx)
    tracks_tier.create_annotation(
        sppasLocation(sppasInterval(
            sppasPoint(0.),
            sppasPoint(float(end-begin))
        )),
        [l.copy() for l in ann.get_labels()]
    )
    parser.set_filename(fn + args.e)
    if not args.quiet:
        print("   - text: " + fn + args.e)
    parser.write(trs_output)

    nb += 1

# just to do things... properly!
if nb == 0:
    os.remove(output_dir)
    print("Done. No track extracted!\n")
else:
    if not args.quiet:
        print("Done. {:d} tracks were extracted.\n".format(nb))
