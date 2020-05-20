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

    scripts.trsbehavior.py
    ~~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to annotate behavior & synchronicity of tiers
               of an annotated file.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata import sppasTag, sppasLabel
from sppas.src.anndata import sppasLocation, sppasInterval, sppasPoint
from sppas.src.anndata import sppasRW

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file -o file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to annotate behavior and "
                                    "synchronicity of tiers of an annotated "
                                    "file.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-t",
                    metavar="value",
                    required=False,
                    action='append',
                    type=int,
                    help='A tier number (use as many -t options as wanted). '
                         'Positive or negative value: '
                         '1=first tier, -1=last tier.')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output file name')

parser.add_argument("-d",
                    metavar="delta",
                    required=False,
                    default=0.04,
                    type=float,
                    help='Frame-rate to create intervals (default:0.04)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Read

parser = sppasRW(args.i)
trs_input = parser.read()

# Take all tiers or specified tiers
tiers_numbers = list()
if not args.t:
    tiers_numbers = range(1, (len(trs_input) + 1))
elif args.t:
    tiers_numbers = args.t

# ----------------------------------------------------------------------------

delta = args.d
start = int(trs_input.get_min_loc().get_midpoint() / delta)
finish = int(trs_input.get_max_loc().get_midpoint() / delta)

behavior_tier = trs_input.create_tier("Behavior")

for i in range(start, finish):
    texts = list()
    b = (i+start)*delta
    e = b+delta

    for t in tiers_numbers:
        tier = trs_input[t-1]
        # get only ONE annotation in our range
        anns = tier.find(b, e, overlaps=True)
        if len(anns) > 1:
            anni = tier.near(b+int(delta/2.), direction=0)
            ann = tier[anni]
        else:
            ann = anns[0]
        texts.append(ann.serialize_labels())

    # Append in new tier
    ti = sppasInterval(
            sppasPoint(b, 0.0001),
            sppasPoint(e, 0.0001))
    if len(texts) > 1:
        missing = False
        for t in texts:
            if len(t.strip()) == 0:
                # missing annotation label...
                missing = True
        if missing is True:
            text = ""
        else:
            text = ";".join(texts)
    else:
        text = str(texts[0])
    behavior_tier.create_annotation(sppasLocation(ti),
                                    sppasLabel(sppasTag(text)))

# ----------------------------------------------------------------------------

synchro_tier = trs_input.create_tier("Synchronicity")
for ann in behavior_tier:
    text = ann.serialize_labels()
    if len(text) > 0:
        values = text.split(';')
        v1 = values[0].strip()
        v2 = values[1].strip()
        if v1 == "0" or v2 == "0":
            if v1 == "0" and v2 == "0":
                v = -1
            else:
                v = 0
        else:
            if v1 != v2:
                v = 1
            else:
                v = 2
        synchro_tier.create_annotation(
            ann.get_location().copy(),
            sppasLabel(sppasTag(v, "int")))

# ----------------------------------------------------------------------------
# Write

parser.set_filename(args.o)
parser.write(trs_input)
