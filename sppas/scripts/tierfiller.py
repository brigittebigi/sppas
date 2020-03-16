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

    scripts.tierfiller.py
    ~~~~~~~~~~~~~~~~~~~~~~

    ... a script to fill in empty labels of a tier of an annotated file.

"""
import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata.aio.aioutils import fill_gaps
from sppas import sppasRW
from sppas import sppasLabel, sppasTag

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(
    usage="%(prog)s [options]",
    description="Fill empty tags and holes of a tier of an annotated file.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-t",
                    metavar="name",
                    required=True,
                    help='Name of the tier to fill in.')

parser.add_argument("-o",
                    metavar="file",
                    help='Output file name')

parser.add_argument("-f",
                    metavar="text",
                    default="#",
                    help='Text to fill in with (default:#)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

parser = sppasRW(args.i)
trs_input = parser.read(args.i)

tier_input = trs_input.find(args.t, case_sensitive=False)
if tier_input is None:
    print('Tier {:s} not found in file {:s}'.format(args.t, args.i))
    sys.exit(1)

if tier_input.is_interval() is False:
    print('Only not empty interval tiers can be filled.')
    sys.exit(1)

if len(tier_input) < 2:
    print('The tier does not contains enough intervals.')
    sys.exit(1)

# ---------------------------------------------------------------------------
# Create the tag to fill empty intervals
# ---------------------------------------------------------------------------

if tier_input.is_int():
    filler = sppasTag(args.f, "int")
elif tier_input.is_float():
    filler = sppasTag(args.f, "float")
elif tier_input.is_bool():
    filler = sppasTag(args.f, "bool")
else:
    filler = sppasTag(args.f)

ctrl_vocab = tier_input.get_ctrl_vocab()
if ctrl_vocab is not None:
    if ctrl_vocab.contains(filler) is False:
        ctrl_vocab.add(filler, description="Filler")

# ----------------------------------------------------------------------------
# Fill in
# ----------------------------------------------------------------------------

# Temporal gaps/holes between annotations are filled with an un-labelled ann.
tier = fill_gaps(tier_input)
if tier is tier_input:
    tier = tier_input.copy()
    tier.gen_id()

tier.set_name(tier.get_name()+"-fill")

# Fill in un-labelled / un-tagged annotations
for ann in tier:
    for label in ann.get_labels():
        if label is not None and len(label) > 0:
            for tag, score in label:
                if tag.is_empty() is True:
                    tag.set(filler)
        else:
            label = sppasLabel(filler)
    if len(ann.get_labels()) == 0:
        ann.append_label(sppasLabel(filler))


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

if args.o:
    trs_input.append(tier)
    parser = sppasRW(args.o)
    parser.write(trs_input)

else:

    for a in tier:
        print("{:f} {:f} {:s}".format(
            a.get_location().get_best().get_begin().get_midpoint(),
            a.get_location().get_best().get_end().get_midpoint(),
            a.get_labels()))
