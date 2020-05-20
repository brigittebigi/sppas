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

    scripts.slmtrain.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to train a statistical language model.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.models import sppasNgramsModel
from sppas.src.models import sppasArpaIO


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file " % os.path.basename(PROGRAM),
                        description="... a script to train a statistical language model.")

parser.add_argument("-i",
                    metavar="input",
                    required=True,
                    action='append',
                    help='Input file name of the training corpus.')

parser.add_argument("-r",
                    metavar="vocab",
                    required=False,
                    help='List of known words.')

parser.add_argument("-n",
                    metavar="order",
                    required=False,
                    default=3,
                    type=int,
                    help='N-gram order value (default=1).')

parser.add_argument("-m",
                    metavar="method",
                    required=False,
                    default="logml",
                    type=str,
                    help='Method to estimates probabilities (one of: raw, lograw, ml, logml).')

parser.add_argument("-o",
                    metavar="output",
                    required=True,
                    help='Output file name.')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------

# ---------------------------------
# 1. Create a sppasNgramsModel

model = sppasNgramsModel(args.n)
if args.r:
    model.set_vocab(args.r)

# ---------------------------------
# 2. Estimate counts of each n-gram

model.count(*(args.i))

# ---------------------------------
# 3. Estimate probabilities

probas = model.probabilities(args.m)

# ---------------------------------
# 4. Write in an ARPA file

arpaio = sppasArpaIO()
arpaio.set(probas)
arpaio.save(args.o)
