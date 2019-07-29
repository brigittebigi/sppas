#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2017-2018 Brigitte Bigi
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
# ipamapping.py
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

from sppas.src.presenters import sppasMappingTier
from sppas.src.anndata import sppasTranscription, sppasRW

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a program to map tags of labels.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name.')

parser.add_argument("-n",
                    metavar="tiername",
                    required=True,
                    type=str,
                    help='One or several tier name separated by commas.')

parser.add_argument("--reverse",
                    action='store_true',
                    help='Reverse the conversion (ipa to sampa).')

parser.add_argument("--nopraat",
                    action='store_true',
                    help='Use the standard table even if textgrid file.')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Load input data

# read content
parser = sppasRW(args.i)
trs_input = parser.read()

# fix table
if args.nopraat:
    print('Converted with standard-IPA mapping table.')
    table = os.path.join(os.path.dirname(PROGRAM), 'sampa2ipa.repl')
else:
    if args.i.lower().endswith('textgrid') is True:
        print('Converted with Praat-IPA mapping table.')
        table = os.path.join(os.path.dirname(PROGRAM), "sampa2praat.repl")
    else:
        print('Converted with standard-IPA mapping table.')
        table = os.path.join(os.path.dirname(PROGRAM), 'sampa2ipa.repl')

# load table
mapping = sppasMappingTier(table)
if args.reverse:
    mapping.set_reverse(True)    # from ipa to sampa direction
    print("Convert from IPA to SAMPA (reverse option enabled)")
else:
    mapping.set_reverse(False)    # from sampa to ipa direction

mapping.set_keep_miss(True)   # keep unknown entries as given
mapping.set_miss_symbol("")   # not used!
mapping.set_delimiters([])    # will use longest matching

# ----------------------------------------------------------------------------
# Convert input file

trs = sppasTranscription(name=trs_input.get_name()+"-IPA")

for n in args.n.split(','):
    print(" -> Tier {:s}:".format(n))
    tier = trs_input.find(n, case_sensitive=False)
    if tier is not None:
        new_tier = mapping.map_tier(tier)
        if args.reverse:
            new_tier.set_name(n+"-SAMPA")
        else:
            new_tier.set_name(n+"-IPA")
        trs.append(new_tier)
    else:
        print(" [IGNORED] Wrong tier name.")

# ----------------------------------------------------------------------------
# Write converted tiers

if len(trs) == 0:
    print("No tier converted. No file created.")
    sys.exit(1)

infile, inext = os.path.splitext(args.i)
if args.reverse:
    filename = infile + "-sampa" + inext
else:
    filename = infile + "-ipa" + inext
parser.set_filename(filename)
parser.write(trs)
print("File {:s} created.".format(filename))
