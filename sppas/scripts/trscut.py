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

    scripts.trscut.py
    ~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to cut localizations of annotations.

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasInterval, sppasPoint

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file -o file -s start -d delay [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to shift annotations.")

parser.add_argument("-i",
                    metavar="file_in",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-o",
                    metavar="file_out",
                    required=True,
                    help='Output annotated file name')

parser.add_argument("-s",
                    metavar="start",
                    type=float,
                    default=0.,
                    help='Start time value')

parser.add_argument("-d",
                    metavar="delay",
                    required=True,
                    type=float,
                    help='Delay to shift')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if float(args.d) <= 0.:
    print('No delay to apply: nothing to do!')
    sys.exit(0)

# ----------------------------------------------------------------------------
# Read

parser = sppasRW(args.i)

if args.quiet is False:
    print("Read input: {:s}".format(args.i))
trs_input = parser.read()
if len(trs_input) == 0:
    print("No tier in given input file.")
    sys.exit(0)

trs_start_point = trs_input.get_min_loc().copy()
trs_end_point = trs_input.get_max_loc().copy()

# ----------------------------------------------------------------------------
# Remove annotations until start and after start+delay

for tier in trs_input:
    # fix start/end period to keep with appropriate type
    if tier.is_int():
        start = int(args.s)
        end = start + int(args.d)
    else:
        start = float(args.s)
        end = start + float(args.d)

    # remove un-necessary intervals
    tier.remove(trs_start_point, start, overlaps=False)
    tier.remove(end, trs_end_point, overlaps=False)

    if tier.is_point() is False and len(tier) > 0:
        # Adjust start/end localizations
        if float(start) > 0.:
            loc = tier[0].get_location().get_best()
            new_loc = sppasInterval(sppasPoint(start), loc.get_end())
            tier[0].get_location().append(new_loc)
            tier[0].get_location().remove(loc)
        if float(end) < trs_end_point:
            loc = tier[-1].get_location().get_best()
            new_loc = sppasInterval(loc.get_begin(), sppasPoint(end))
            tier[-1].get_location().append(new_loc)
            tier[-1].get_location().remove(loc)

# ----------------------------------------------------------------------------
# Write

parser.set_filename(args.o)

if args.quiet is False:
    print("Write output: {:s}".format(args.o))
parser.write(trs_input)
