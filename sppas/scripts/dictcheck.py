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

    scripts.dictcheck.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to detect pronunciation anomalies into a dictionary.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.config import separators
from sppas.src.resources import sppasDictPron

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to detect pronunciation anomalies into a dictionary.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input dictionary file name (as many as wanted)')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

args = parser.parse_args()

pron_dict = sppasDictPron(args.i, nodump=True)

for entry in pron_dict:

    prons = pron_dict.get_pron(entry)
    nb_chars = float(len(entry))

    for pron in prons.split(separators.variants):

        phonetization = pron.split(separators.phonemes)
        nb_phones = float(len(phonetization))

        if nb_phones < nb_chars * 0.5:
            print("{:s}\t{:s}\tsmall".format(entry.encode('utf8'), pron.encode('utf8')))

        elif nb_phones > nb_chars * 1.8:
            print("{:s}\t{:s}\tlarge".format(entry.encode('utf8'), pron.encode('utf8')))

        elif nb_phones > nb_chars * 1.4:
            print("{:s}\t{:s}\tbig".format(entry.encode('utf8'), pron.encode('utf8')))
