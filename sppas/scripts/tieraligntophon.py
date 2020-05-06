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

    scripts.tieraligntophon.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to a time-aligned phonemes tier to its
phonetization tier.

"""

import sys
import os.path
import logging
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sppasRW
from sppas import sppasLogSetup
from sppas import sppasAppConfig

from sppas.src.anndata import sppasTranscription
from sppas.src.anndata.aio.aioutils import unalign
from sppas.src.annotations import sppasFindTier

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------


parser = ArgumentParser(usage="{:s} -i file -o file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to convert time-aligned "
                                    "phonemes into their phonetization.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output file name')

parser.add_argument("--tok",
                    action='store_true',
                    help="Convert time-aligned tokens into their tokenization.")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# Redirect all messages to logging
# --------------------------------

with sppasAppConfig() as cg:
    if not args.quiet:
        log_level = cg.log_level
    else:
        log_level = cg.quiet_log_level
    lgs = sppasLogSetup(log_level)
    lgs.stream_handler()


# ----------------------------------------------------------------------------
# Read

logging.info("Read input: {:s}".format(args.i))
parser = sppasRW(args.i)
trs_input = parser.read()

trs_out = sppasTranscription()

# ----------------------------------------------------------------------------
# Transform the PhonAlign tier to a Phonetization tier

try:
    align_tier = sppasFindTier.aligned_phones(trs_input)
    logging.info("PhonAlign tier found.")
    phon_tier = unalign(align_tier)
    phon_tier.set_name("Phones")
    trs_out.append(phon_tier)
except IOError:
    logging.error("PhonAlign tier not found.")

# ----------------------------------------------------------------------------
# Transform the TokensAlign tier to a Tokenization tier

if args.tok:
    try:
        align_tier = sppasFindTier.aligned_tokens(trs_input)
        logging.info("TokensAlign tier found.")
        token_tier = unalign(align_tier)
        token_tier.set_name("Tokens")
        trs_out.append(token_tier)
    except IOError:
        logging.error("TokensAlign tier not found.")

# ----------------------------------------------------------------------------
# Write

if len(trs_out) > 0:
    logging.info("Write output: {:s}".format(args.o))
    parser.set_filename(args.o)
    parser.write(trs_out)
else:
    logging.info("No tier converted.")
    sys.exit(1)
