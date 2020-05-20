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

    scripts.tierinfo.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to get information about a tier of an annotated file.

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata import sppasRW

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to get information about "
                                    "a tier of an annotated file.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-t",
                    metavar="value",
                    default=1,
                    type=int,
                    help='Tier number (default: 1)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

parser = sppasRW(args.i)
trs_input = parser.read()

if args.t <= 0 or args.t > len(trs_input):
    print('Error: Bad tier number.\n')
    sys.exit(1)
tier = trs_input[args.t-1]

# Get the tier type
tier_type = "Unknown"
if tier.is_point() is True:
    tier_type = "Point"
elif tier.is_interval() is True:
    tier_type = "Interval"
elif tier.is_disjoint() is True:
    tier_type = "DisjointIntervals"

print('Tier number {:d} of file {:s}:'.format(args.t, args.i))
print(" - name: {:s}".format(tier.get_name()))
print(" - type: {:s}".format(tier_type))
print(" - number of annotations: {:d}".format(len(tier)))
if len(tier) > 1:
    print(" - from time: {:.4f}".format(tier.get_first_point().get_midpoint()))
    print(" - to time: {:.4f} ".format(tier.get_last_point().get_midpoint()))

    loc_silences = [a.get_location() for a in tier if a.get_best_tag().is_silence()]
    dur_silence = sum(a.get_best().duration().get_value() for a in loc_silences)
    print(" - number of silences: {:d}".format(len(loc_silences)))
    print(" - total silence duration: {:.3f}".format(dur_silence))
