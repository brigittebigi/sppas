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

    scripts.tieradjustbounds.py
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
import math
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasPoint
from sppas.src.anndata.anndataexc import IntervalBoundsError

# ----------------------------------------------------------------------------


def round_time(tier, r):
    """Round to r digits all time values of tier."""
    for a in tier:
        loc = a.get_location()
        for l, s in loc:
            b = l.get_begin()
            b.set_midpoint(round(b.get_midpoint(), r))
            e = l.get_end()
            e.set_midpoint(round(e.get_midpoint(), r))
    return tier

# ----------------------------------------------------------------------------


def adjust(time_point, ref):

    i = ref.near(time_point, direction=0)
    a = ref[i]
    l = a.get_location().get_best()

    # which point of 'a' is the closest?
    a_begin = l.get_begin()
    delta_begin = math.fabs(a_begin.get_midpoint() - time_point)
    a_end = l.get_end()
    delta_end = math.fabs(a_end.get_midpoint() - time_point)

    if delta_begin < delta_end:
        return sppasPoint(a_begin.get_midpoint(), delta_begin)
    return sppasPoint(a_end.get_midpoint(), delta_end)

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
                    required=True,
                    metavar="adjust",
                    help='Name of the tier to be adjusted')

parser.add_argument("-T",
                    required=True,
                    metavar="bounds",
                    help='Name of the tier to adjust bounds on')

parser.add_argument("-d",
                    metavar="value",
                    default=0.04,
                    type=float,
                    help='Maximum time diff to adjust a bound (default: 0.04)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# do the job
# ----------------------------------------------------------------------------

parser = sppasRW(args.i)
trs_input = parser.read()

tier_orig = trs_input.find(args.t)
ref = trs_input.find(args.T)

if tier_orig.is_interval() is False:
    print('Only interval tiers are supported.')
    sys.exit(1)
if ref.is_interval() is False:
    print('Only interval tiers are supported.')
    sys.exit(1)

# reformat time values
tier_orig = round_time(tier_orig, 4)
ref = round_time(ref, 4)

# ------------------------

tier = tier_orig.copy()
tier.set_name('TokensAlign-Adjust')

for i in range(1, len(tier)-1):
    ann = tier[i]
    loc = ann.get_location().get_best()

    current = loc.get_end()
    adjusted = adjust(current.get_midpoint(), ref)
    ann_next = tier[i+1]
    loc_next = ann_next.get_location().get_best()

    try:
        loc.set_end(adjusted)
        loc_next.set_begin(adjusted.copy())
    except IntervalBoundsError:
        loc.set_end(current)
        print('Can not adjust {:s} to {:s}.'.format(current, adjusted))

trs_input.append(tier)
parser.write(trs_input)
