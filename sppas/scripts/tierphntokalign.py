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

    scripts.tierphntokalign.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to append the tier PhnTokAlign in a time-aligned file.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasLabel, sppasTag

# ----------------------------------------------------------------------------
# 0. Verify and extract args:

parser = ArgumentParser(usage="{:s} -i file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to append the tier "
                                    "PhnTokAlign in a time-aligned file.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# 1. Read input data file


parser = sppasRW(args.i)

if args.quiet is False:
    print("Read input: {:s}".format(args.i))
trs_input = parser.read()


tier_phon = trs_input.find('PhonAlign')
if tier_phon is None:
    print("Error: can't find the tier PhonAlign.")
    sys.exit(1)

tier_token = trs_input.find('TokensAlign')
if tier_token is None:
    print("Error: can't find the tier TokensAlign.")
    sys.exit(1)


# ----------------------------------------------------------------------------
# 2. Create the expected data

new_tier = trs_input.create_tier('PhnTokAlign')

for ann_token in tier_token:

    # Create the sequence of phonemes
    beg = ann_token.get_lowest_localization()
    end = ann_token.get_highest_localization()
    ann_phons = tier_phon.find(beg, end)
    content = "-".join(serialize_labels(ann.get_labels()) for ann in ann_phons)

    # Append in the new tier
    loc = ann_token.get_location().copy()
    new_tier.create_annotation(loc, sppasLabel(sppasTag(content)))

trs_input.add_hierarchy_link("TimeAssociation", tier_token, new_tier)

# ----------------------------------------------------------------------------
# 3. Save new version of the file

if args.quiet is False:
    print("Override input file: {:s}".format(args.i))
parser.write(trs_input)
