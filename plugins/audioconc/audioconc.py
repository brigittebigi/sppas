#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2019  Brigitte Bigi
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
# audioconc.py
# ---------------------------------------------------------------------------

import sys
import os
import re
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
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasRW
import sppas.src.audiodata.aio
from sppas.src.audiodata.audio import sppasAudioPCM
from sppas.src.audiodata import sppasChannel
from sppas.src.utils.makeunicode import u


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file".format(os.path.basename(PROGRAM)),
                        description="... a program to "
                                    "concatenate audio chunks containing a word")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input audio file name.')

parser.add_argument("-t",
                    metavar="tier",
                    required=False,
                    default="trans",
                    help="Name of the tier indicating the tracks.")

parser.add_argument("-p",
                    metavar="pattern",
                    required=False,
                    default="-palign",
                    help="Pattern of the annotated input file.")

parser.add_argument("-w",
                    metavar="word",
                    required=True,
                    default="money",
                    help='word to find')

parser.add_argument("-o",
                    metavar="offset",
                    required=True,
                    default="2",
                    help='offset around the sound')

parser.add_argument("-b",
                    metavar="blank",
                    required=True,
                    default="500",
                    help='blank between chuncks')

parser.add_argument("-m",
                    metavar="match",
                    required=True,
                    default="contains",
                    help='contains, exact,  startswith, endswith')


parser.add_argument("-e",
                    metavar="ext",
                    required=False,
                    default=".eaf",
                    help='File extension for the tracks (default:.eaf).')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

if args.m not in (["contains", "exact", "startswith", "endswith"]):
    print("'"+args.m+"' is not allowed, choose from 'contains, exact, startswith, endswith'")
    sys.exit(1)

if not args.i.lower().endswith('wav') is True:
    print('Please, Select an AUDIO file')
    sys.exit(1)

# ----------------------------------------------------------------------------
# Open the audio and check it
audio = sppas.src.audiodata.aio.open(args.i)

if audio.get_nchannels() > 1:
    print('AudioConcatener supports only mono audio files.')
    sys.exit(1)

# the annotated data filename
filename = os.path.splitext(args.i)[0]
ann = None
for ext in sppas.src.anndata.aio.extensions:
    ann = filename + args.p.strip() + ext
    if os.path.exists(ann):
        break
if ann is None:
    print('No annotated data corresponding to the audio file {:s}.'
          ''.format(args.i))
    sys.exit(1)

#type of search for filter not used
if args.m == 'contains':
    search = "f.tag(contains = u(args.w))"
elif args.m == 'exact':
    search = "f.tag(exact = u(args.w))"
    recherche = "args.w == text"
elif args.m == 'startswith':
    search = "f.tag(startswith = u(args.w))"
elif args.m == 'endswith':
    search = "f.tag(endswith = u(args.w))"

#type of search
pattern = ""
if args.m == 'contains':
    pattern = re.compile(u'.*' + u(args.w) + u'.*')
elif args.m == 'exact':
    pattern = re.compile('(^| )' + u(args.w) + '($| )')
elif args.m == 'startswith':
    pattern = re.compile('(^| )' + u(args.w) + u'.*')
elif args.m == 'endswith':
    pattern = re.compile(u'.*' + u(args.w) + '($| )')

# Load annotated data
parser = sppasRW(ann)
trs_input = parser.read()

# Extract the tier
tier = trs_input.find(args.t, case_sensitive=False)
if tier is None:
    print("A tier with name {:s} is required in file {:s}."
          "".format(args.t, ann))
    sys.exit(1)

# Extract the channel
audio.extract_channel(0)
channel = audio.get_channel(0)
audio.rewind()
framerate = channel.get_framerate()
sampwidth = channel.get_sampwidth()

# ----------------------------------------------------------------------------
# output directory
output_dir = filename + "-" + args.t
if os.path.exists(output_dir):
    print("A directory with name {:s} is already existing.".format(output_dir))
    #sys.exit(1)
else:
    os.mkdir(output_dir)
if not args.quiet:
    print("The output directory {:s} was created.".format(output_dir))

mot = args.w.strip().encode('ascii', 'ignore')
fout = os.path.join(output_dir, 'search_' + mot)

offset = float(args.o) / 1000
blank = float(args.b) / 1000
print("offset =" + str(offset))

# ----------------------------------------------------------------------------

'''
# filtrage : crée une tier avec seulement les annotations  qui contiennent le mot recherché
f = sppasFilters(tier)
# word = f.tag(contains=u(args.w))
word = eval(search)
# to_tier_phrase et to_tier_mot methodes ajoutées à src\anndata\ann\annset
tier_phrase = word.to_tier_phrase(name="phrase", offset=offset, blank=blank)
if int(offset) > 50:
    tier_mot = word.to_tier_mot(name="mot", offset=offset, blank=blank)
    print(">> {:s} has {:d} occurrences of the word {:s}".format(tier.get_name(), len(tier_phrase), args.w))
'''

tier_phrase = sppasTier("phrase")
nb = False
newend = 0
for i, ann in enumerate(tier):
    text = ann.serialize_labels(separator="_", empty="", alt=False)
    if pattern.match(text):
        nb =True
        start = ann.get_lowest_localization().get_midpoint() - offset
        if start < 0:
            start = 0
        end = ann.get_highest_localization().get_midpoint() + offset
        newstart = newend
        newend = newstart + end - start + blank
        tier_phrase.create_annotation(
            sppasLocation(sppasInterval(
                sppasPoint(float(newstart)),
                sppasPoint(float(newend))
            )),
            [l.copy() for l in ann.get_labels()]
        )

# ------------------------
tier_mot = sppasTier("mot")
if int(args.o) > 50:
    newend = 0
    for i, ann in enumerate(tier):
        text = ann.serialize_labels(separator="_", empty="", alt=False)
        if pattern.match(text):
            start = ann.get_lowest_localization().get_midpoint()
            end = ann.get_highest_localization().get_midpoint()
            tier_mot.create_annotation(
                sppasLocation(sppasInterval(
                    sppasPoint(float(newend)),
                    sppasPoint(float(newend + offset))
                )),
                sppasLabel(sppasTag(str(i) + ' >'))
            )
            newstart = newend + offset
            newend = newstart + end - start
            tier_mot.create_annotation(
                sppasLocation(sppasInterval(
                    sppasPoint(float(newstart)),
                    sppasPoint(float(newend))
                )),
                [l.copy() for l in ann.get_labels()]
            )
            newstart = newend
            newend = newstart + offset + blank
            tier_mot.create_annotation(
                sppasLocation(sppasInterval(
                    sppasPoint(float(newstart)),
                    sppasPoint(float(newend))
                )),
                sppasLabel(sppasTag('< ' + str(i)))
            )

if not tier_phrase.is_empty():
    nb = True
    t = sppasTranscription()
    t.append(tier_phrase)
    if not tier_mot.is_empty():
        t.append(tier_mot)
    parser.set_filename(fout + args.e)
    parser.write(t)
    if not args.quiet:
        print(">>> text: " + fout + args.e + " saved")

    # fichier audio
    audio_out = sppasAudioPCM()
    frames = b''
    blanks = int(blank * framerate * sampwidth)
    frames_blank = b'\x00' * blanks
    for i, Tier in enumerate(tier):
        print("> tier {:d} = {:s}".format(i, tier.get_name()))
        text = Tier.serialize_labels(separator="_", empty="", alt=False)
        if len(text) == 0 or Tier.get_best_tag().is_silence():
            print("> tier {:d} = silence".format(i))
            continue

        # concatenation of sound chunks which contains the word
        if pattern.match(text):
            begin = Tier.get_lowest_localization().get_midpoint() - offset
            if begin < 0:
                begin = 0
            end = Tier.get_highest_localization().get_midpoint() + offset
            chunk_size = int((end - begin) * framerate + offset)
            if not args.quiet:
                print("> chunk_size = " + str(chunk_size))
            # create audio output
            extracter = channel.extract_fragment(int(begin * framerate),
                                                 int(end * framerate))
            frames += extracter.get_frames()
            frames += frames_blank

    data = sppasChannel(framerate, sampwidth, frames)
    audio_out.append_channel(data)
    sppas.src.audiodata.aio.save(fout + ".wav", audio_out)

if not nb:
    print("Done. no {:s} found !\n".format(args.w))
else:
    print("Done. {:d} occurrences of {:s} were concatenated .\n".format(nb, args.w))
