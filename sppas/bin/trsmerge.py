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

    bin.trsmerge.py
    ~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to merge annotated data files.

"""

import logging
import sys
import os
from argparse import ArgumentParser
import pickle
import time

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas import sppasLogSetup
from sppas import sppasAppConfig

from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasRW
from sppas.src.anndata.aio import sppasXRA

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [files]",
        description="... a program to merge annotated data files.",
        add_help=True,
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__))

    group_verbose = parser.add_mutually_exclusive_group()

    group_verbose.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    group_verbose.add_argument(
        "--debug",
        action='store_true',
        help="Highest level of verbosity")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-i",
        metavar="file",
        action='append',
        required=True,
        help='Input annotated file name (as many as wanted)')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output annotated file name')

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Redirect all messages to logging
    # --------------------------------

    with sppasAppConfig() as cg:
        if not args.quiet:
            if args.debug:
                log_level = 0
            else:
                log_level = cg.log_level
        else:
            log_level = cg.quiet_log_level
        lgs = sppasLogSetup(log_level)
        lgs.stream_handler()

    # -----------------------------------------------------------------------
    # Read
    # -----------------------------------------------------------------------

    trs_output = sppasTranscription("Merged")

    for file_idx, trs_input_file in enumerate(args.i):

        logging.info("Read {:s}".format(args.i))

        start_time = time.time()
        parser = sppasRW(trs_input_file)
        trs_input = parser.read()
        end_time = time.time()

        # General information
        # -------------------
        logging.debug(
            "Elapsed time for reading: {:f} seconds"
            "".format(end_time - start_time))
        pickle_string = pickle.dumps(trs_input)
        logging.debug(
            "Memory usage of the transcription: {:d} bytes"
            "".format(sys.getsizeof(pickle_string)))

        # Copy all media/ctrl vocab
        # -------------------------
        trs_output.set_media_list(trs_input.get_media_list())
        trs_output.set_ctrl_vocab_list(trs_input.get_ctrl_vocab_list())

        # Copy all tiers (keep original ids)
        # ----------------------------------
        for i, tier in enumerate(trs_input):
            logging.info("  - Tier {:d}: {:s}. Selected."
                         "".format(i, tier.get_name()))
            trs_output.append(tier)

        # Metadata
        # --------
        trs_output.set_meta(
            "merge_with_file_{:d}".format(file_idx),
            trs_input_file)

    # -----------------------------------------------------------------------
    # Write
    # -----------------------------------------------------------------------

    if args.o:
        logging.info("Write {:s}".format(args.o))
        parser = sppasRW(args.o)
        start_time = time.time()
        parser.write(trs_output)
        end_time = time.time()

        logging.debug(
            "Elapsed time for writing: {:f} seconds"
            "".format(end_time - start_time))

    else:
        x = sppasXRA()
        x.set(trs_output)
        x.write(sys.stdout)

    logging.info("Done.")
