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

    scripts.trsshift.py
    ~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to shift localizations of annotations.

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation
from sppas.src.anndata.anndataexc import AnnDataTypeError

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file -o file -d delay [options]"
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

parser.add_argument("-d",
                    metavar="delay",
                    required=True,
                    type=float,
                    help='Delay to shift')

parser.add_argument("--nofill",
                    action='store_true',
                    help="Disable the creation of an interval in the delay")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if float(args.d) == 0.:
    print('No shift to apply: nothing to do!')
    sys.exit()

# ----------------------------------------------------------------------------
# Read

parser = sppasRW(args.i)

if args.quiet is False:
    print("Read input: {:s}".format(args.i))
trs_input = parser.read()
trs_start_point = trs_input.get_min_loc().copy()
trs_end_point = trs_input.get_max_loc().copy()

# ----------------------------------------------------------------------------
# Shift

try:
    trs_input.shift(args.d)
except AnnDataTypeError:
    trs_input.shift(int(args.d))

shifted_trs_start_point = trs_input.get_min_loc().copy()
shifted_trs_end_point = trs_input.get_max_loc().copy()

# ----------------------------------------------------------------------------
# Write

parser.set_filename(args.o)
if sppasRW.create_trs_from_extension(args.o).gaps_support() is False and \
   args.nofill is False:
    for tier in trs_input:
        if tier.is_point():
            continue
        else:
            if args.d > 0:
                tier.create_annotation(
                    sppasLocation(sppasInterval(trs_start_point,
                                  shifted_trs_start_point)))
            elif args.d < 0:
                tier.create_annotation(
                    sppasLocation(sppasInterval(shifted_trs_end_point,
                                                trs_end_point)))

if args.quiet is False:
    print("Write output: {:s}".format(args.o))
parser.write(trs_input)
