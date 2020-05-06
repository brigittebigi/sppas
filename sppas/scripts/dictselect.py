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

    scripts.dictselect.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to select words of a dictionary

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import symbols
from sppas import separators
from sppas.src.resources import sppasDictPron
from sppas.src.resources import sppasVocabulary


# ----------------------------------------------------------------------------

parser = ArgumentParser(
    usage="%s -i dictfile -r vocabfile -o file [options]" % os.path.basename(PROGRAM),
    description="... a script to select words of a dictionary.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input dictionary file name')

parser.add_argument("-r",
                    metavar="file",
                    required=True,
                    help='Input vocabulary file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output dictionary file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

pron_dict = sppasDictPron(args.i, nodump=True)
vocab = sppasVocabulary(args.r, nodump=True)
vocab_dict = sppasDictPron()

missing = 0
variants = 0
for entry in vocab:
    prons = pron_dict.get_pron(entry)
    if prons != symbols.unk:
        for pron in prons.split(separators.variants):
            vocab_dict.add_pron(entry, pron)
            variants += 1
    else:
        missing += 1

vocab_dict.save_as_ascii(args.o,
                         with_variant_nb=True,
                         with_filled_brackets=False)

if missing > 0:
    print("{:d} missing words.".format(missing))
print("{:d} pronunciations added.".format(variants))
