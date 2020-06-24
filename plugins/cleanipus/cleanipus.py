#!/usr/bin/env python
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
# cleanipus.py
# ---------------------------------------------------------------------------
import os
import sys
import logging
import time
import pickle
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

if os.path.exists(SPPAS) is False:
    print("ERROR: SPPAS not found.")
    sys.exit(1)
sys.path.append(SPPAS)

from sppas import sg
from sppas import sppasLogSetup
from sppas import sppasAppConfig
from sppas import symbols
from sppas import sppasRW
from sppas import sppasTag, sppasLabel
from sppas import sppasFindTier

SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# -----------------------------------------------------------------------
# Verify and extract args:
# -----------------------------------------------------------------------

parser = ArgumentParser(
    usage="%(prog)s -i [file]",
    description="... a program to clean IPUs",
    add_help=True,
    epilog="This program is a plugin of {:s}. Contact the "
           "author at: {:s}".format(sg.__name__, sg.__contact__))

group_verbose = parser.add_mutually_exclusive_group()

group_verbose.add_argument(
    "--quiet",
    action='store_true',
    help="Disable the verbosity")

group_verbose.add_argument(
    "--debug",
    action='store_true',
    help="Highest level of verbosity")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name.')

# Force to print help if no argument is given then parse
# ------------------------------------------------------

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# Redirect all messages to logging
# --------------------------------

with sppasAppConfig() as cg:
    if not args.quiet:
        if args.debug:
            log_level = 0
        else:
            log_level = cg.log_level
    else:
        log_level = cg.quiet_log_level
    lgs = sppasLogSetup(log_level)
    lgs.stream_handler()

# -----------------------------------------------------------------------
# Read
# -----------------------------------------------------------------------

logging.info("Read {:s}".format(args.i))

start_time = time.time()
parser = sppasRW(args.i)
trs_input = parser.read()
end_time = time.time()

# General information
# -------------------
logging.debug(
    "Elapsed time for reading: {:f} seconds"
    "".format(end_time - start_time))
pickle_string = pickle.dumps(trs_input)
logging.debug(
    "Memory usage of the transcription: {:d} bytes"
    "".format(sys.getsizeof(pickle_string)))

# -----------------------------------------------------------------------
# Work
# -----------------------------------------------------------------------

tier = sppasFindTier().transcription(trs_input)
if tier is None:
    logging.error('Transcription tier not found.')
    sys.exit(1)

# Replace un-transcribed ipus by silences
# Re-index right-IPUs
ipu = 0
for ann in tier:

    if ann.is_labelled() is False or ann.label_is_string() is False:
        continue
    if ann.get_best_tag().is_silence():
        continue

    old_label = serialize_labels(ann.get_labels(), separator=" ", empty="", alt=True)
    if old_label.startswith("ipu_"):
        try:
            space = old_label.index(' ')
            old_label = old_label[space:].strip()
        except ValueError:
            old_label = ""

    if len(old_label) > 0:
        ipu += 1
        new_labels = list()
        new_labels.append(sppasLabel(sppasTag('ipu_%d' % ipu)))
        new_labels.append(sppasLabel(sppasTag(old_label)))
        ann.set_labels(new_labels)
    else:
        ann.set_labels(sppasLabel(sppasTag(SIL_ORTHO)))


# Merge continuous silences
i = len(tier)-1
while i >= 0:
    # current annotation: label and end of its localization
    label = serialize_labels(tier[i].get_labels())
    end_loc = tier[i].get_location().get_best().get_end().copy()

    # take a look at the previous annotations
    i -= 1
    c = i
    while label == SIL_ORTHO and c >= 0:
        label = serialize_labels(tier[c].get_labels())
        c -= 1
    c += 1
    # c is now pointing to the ipu just before an eventual sequence of silences

    # if several continuous silences were observed
    if c < i:
        # pop the sequence of silences, except the first one
        while c < i:
            tier.pop(i+1)   # i+1 because we already decreased i
            i -= 1
        # set the end of the last silence (we removed) to the remaining one
        tier[i+1].get_location().get_best().set_end(end_loc)

        # annotation of next iteration is the previous of the ipu one
        i = c-1

# -----------------------------------------------------------------------
# Write
# -----------------------------------------------------------------------

f, e = os.path.splitext(args.i)
output = f + "-clean" + e
logging.info("Write {:s}".format(output))
parser = sppasRW(output)
start_time = time.time()
parser.write(trs_input)
end_time = time.time()

logging.debug(
    "Elapsed time for writing: {:f} seconds"
    "".format(end_time - start_time))

logging.info("Done.")
