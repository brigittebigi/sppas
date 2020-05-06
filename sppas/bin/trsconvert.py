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

    bin.trsconvert.py
    ~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2019  Brigitte Bigi
:summary:      a program to export annotation files based on anndata API.

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

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata.aio import sppasXRA

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [files] [options]",
        description="... a program to export annotated files.",
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
        required=True,
        help='Input annotated file name.')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output annotated file name.')

    # Add arguments for the options
    # -----------------------------

    group_opt = parser.add_argument_group('Options')

    group_opt.add_argument(
        "-n",
        metavar="value",
        required=False,
        action='append',
        type=int,
        help='Number of a tier (use as many -n options as wanted). '
             'Positive or negative value: '
             '1=first tier, -1=last tier.')

    group_opt.add_argument(
        "-t",
        metavar="tiername",
        required=False,
        action='append',
        type=str,
        help='Name of a tier (use as many -t options as wanted).')

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

    logging.info("Read {:s}".format(args.i))

    start_time = time.time()
    parser = sppasRW(args.i)
    trs_input = parser.read()
    end_time = time.time()

    # General information
    # -------------------
    logging.info(
        "Elapsed time for reading: {:f} seconds"
        "".format(end_time - start_time))
    pickle_string = pickle.dumps(trs_input)
    logging.info(
        "Memory usage of the transcription: {:d} bytes"
        "".format(sys.getsizeof(pickle_string)))

    # -----------------------------------------------------------------------
    # Select tiers
    # -----------------------------------------------------------------------

    # Take all tiers or specified tiers
    tier_numbers = []
    if not args.t and not args.n:
        tier_numbers = range(1, (len(trs_input) + 1))
    elif args.n:
        tier_numbers = args.n

    # Select tiers to create output
    trs_output = sppasTranscription("Converted")

    # Add selected tiers into output
    for i in tier_numbers:
        if i > 0:
            idx = i-1
        elif i < 0:
            idx = i
        else:
            idx = len(trs_input)
        if idx < len(trs_input):
            trs_output.append(trs_input[idx])
            logging.info("  - Tier {:d}: {:s}. Selected."
                         "".format(i, trs_input[idx].get_name()))
        else:
            logging.error("  - Tier {:d}: Wrong tier number. Ignored"
                          "".format(i))

    if args.t:
        for n in args.t:
            t = trs_input.find(n, case_sensitive=False)
            if t is not None:
                trs_output.append(t)
            else:
                logging.error("  - Tier {:s}: Wrong tier name. Ignored"
                              "".format(n))

    # Set the other members
    for key in trs_input.get_meta_keys():
        trs_output.set_meta(key, trs_input.get_meta(key))

    # Copy relevant hierarchy links
    for child_tier in trs_input:
        parent_tier = trs_input.get_hierarchy().get_parent(child_tier)
        if parent_tier is not None:
            output_child_tier = trs_output.find(child_tier.get_name())
            output_parent_tier = trs_output.find(parent_tier.get_name())
            if output_child_tier is not None and output_parent_tier is not None:
                link_type = trs_input.get_hierarchy().get_hierarchy_type(child_tier)
                trs_output.add_hierarchy_link(link_type,
                                              output_parent_tier,
                                              output_child_tier)

    # Copy all media
    trs_output.set_media_list(trs_input.get_media_list())

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

        logging.info("Done.")

    else:
        x = sppasXRA()
        x.set(trs_output)
        x.write(sys.stdout)
