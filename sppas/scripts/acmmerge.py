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

    scripts.acmmerge.py
    ~~~~~~~~~~~~~~~~~~~

    ... a script to merge 2 hmmdefs files.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.models.acm.acmodelhtkio import sppasHtkIO


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file1/dir1 -I file2/dir2 -g gamma -o file" % os.path.basename(PROGRAM), 
                        description="... a script to merge 2 hmmdefs files.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input file/directory name')

parser.add_argument("-I",
                    metavar="file",
                    required=False,
                    help='Input file/directory name')

parser.add_argument("-g",
                    metavar="value",
                    type=float,
                    default=0.5,
                    help='Gamma coefficient, for the file of -i option')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

mxg = parser.add_mutually_exclusive_group(required=True)
mxg.add_argument("-o",
                 metavar="file",
                 required=False,
                 help='Output file name')
mxg.add_argument("-O",
                 metavar="file",
                 required=False,
                 help='Output directory name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if args.quiet is False:
    print("Loading AC 1:")
acmodel1 = sppasHtkIO()
if os.path.isfile(args.i):
    acmodel1.read(os.path.dirname(args.i), os.path.basename(args.i))
else:
    acmodel1.read(folder=args.i)
if args.quiet is False:
    print("... done")

if args.I:
    if args.quiet is False:
        print("Loading AC 2:")
    acmodel2 = sppasHtkIO()
    if os.path.isfile(args.I):
        acmodel2.read(os.path.dirname(args.I), os.path.basename(args.I))
    else:
        acmodel2.read(folder=args.I)
    if args.quiet is False:
        print("... done")

    (appended, interpolated, keeped, changed) = acmodel1.merge_model(acmodel2, gamma=args.g)
    if args.quiet is False:
        print("Number of appended HMMs:     {:d}".format(appended))
        print("Number of interpolated HMMs: {:d}".format(interpolated))
        print("Number of keeped HMMs:       {:d}".format(keeped))
        print("Number of changed HMMs:      {:d}".format(changed))

parser = sppasHtkIO()
parser.set(acmodel1)

if args.o:
    parser.write(os.path.dirname(args.o), os.path.basename(args.o))
if args.O:
    parser.write(args.O)
