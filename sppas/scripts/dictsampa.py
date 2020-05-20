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

    scripts.dictsampa.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to convert a dictionary with IPA to SAMPA

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import separators
from sppas.src.resources import sppasDictPron


# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to convert a dictionary from IPA to SAMPA.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input dictionary file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output dictionary file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

pron_dict = sppasDictPron(args.i, nodump=True)
sampa_dict = sppasDictPron()
conversion = sppasDictPron.load_sampa_ipa()

for entry in pron_dict:
    prons = pron_dict.get_pron(entry)
    for pron in prons.split(separators.variants):
        p = list()

        for phone in pron.split(separators.phonemes):
            # Convert pron from IPA to SAMPA
            phone_sampa = sppasDictPron.ipa_to_sampa(conversion, phone)
            # Add to the new pronunciation
            p.append(phone_sampa.replace(separators.phonemes, ""))

        # Store result into the new dict
        sampa_dict.add_pron(entry, separators.phonemes.join(p))

sampa_dict.save_as_ascii(args.o, with_variant_nb=True, with_filled_brackets=True)

