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

    scripts.stats.py
    ~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to estimate stats of annotated files.

"""

import logging
import sys
import os.path
from argparse import ArgumentParser
import codecs
import pickle
import time

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas import sppasLogSetup
from sppas import sppasAppConfig

from sppas.src.anndata import sppasRW
from sppas.src.analysis.tierstats import sppasTierStats

# ----------------------------------------------------------------------------


modes_help = "Stat to estimate, in:\n"
modes_help += "  0 = Summary of all files (default),\n"
modes_help += "  1 = Occurrences in each file,\n"
modes_help += '  2 = Total duration in each file,\n'
modes_help += '  3 = Average duration in each file,\n'
modes_help += '  4 = Median duration in each file,\n'
modes_help += '  5 = Standard deviation duration in each file.'

# ----------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [files] [options]",
        description="... a program to estimate distributions of annotations.",
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

    # Add arguments for the options
    # -----------------------------

    group_opt = parser.add_argument_group('Options')

    group_opt.add_argument(
        "-t",
        metavar="tiername",
        required=True,
        type=str,
        help='Name of the tier to estimate distributions.')

    group_opt.add_argument(
        "-s",
        metavar="stat",
        type=int,
        default=0,
        help=modes_help)

    group_opt.add_argument(
        "-n",
        metavar="ngram",
        default=1,
        type=int,
        help='Value of N of the Ngram sequences (default: 1; Max: 5)')

    group_opt.add_argument(
        "--addradius",
        action='store_true',
        help="Add the Radius to the estimation of the duration (default is to use midpoint)")

    group_opt.add_argument(
        "--deductradius",
        action='store_true',
        help="Deduct the Radius to the estimation of the duration (default is to use midpoint)")

    group_opt.add_argument(
        "--withalt",
        action='store_true',
        help="Include also alternative tags (default is to ignore them)")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Mutual exclusion of radius
    # --------------------------

    if args.addradius and args.deductradius:
        parser.print_usage()
        print("{:s}: error: argument --addradius: "
              "not allowed with argument --deductradius"
              "".format(os.path.basename(PROGRAM)))
        sys.exit(1)

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
    # Check args.
    # Set variables: modes, ngram, tier_name, with_alt, with_radius
    # -----------------------------------------------------------------------

    mode = args.s
    if mode not in range(6):
        logging.error("Unknown stats mode: {}".format(mode))
        sys.exit(1)

    ngram = 1
    if args.n:
        if args.n < 6:
            ngram = args.n
        else:
            logging.warning("Invalid ngram value {:d}. Max is 5."
                            "".format(args.n))

    tier_name = args.t
    tier_name = tier_name.replace(' ', '_')

    with_alt = False
    if args.withalt:
        with_alt = True

    with_radius = 0
    if args.addradius:
        with_radius = 1
    if args.deductradius:
        with_radius = -1

    # -----------------------------------------------------------------------
    # Read data
    # -----------------------------------------------------------------------

    tiers = dict()
    for file_input in args.i:

        logging.info("Read {:s}".format(file_input))
        start_time = time.time()
        parser = sppasRW(file_input)
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

        # Get expected tier
        # -----------------
        tier = trs_input.find(args.t, case_sensitive=False)
        if tier is not None:
            tiers[tier] = file_input
            logging.info("  - Tier {:s}. Selected."
                         "".format(tier.get_name()))
        else:
            logging.error("  - Tier {:s}: Not found."
                          "".format(args.t))
            continue

    # ----------------------------------------------------------------------------
    # Estimates statistical distributions
    # ----------------------------------------------------------------------------

    row_data = list()

    # Summary (=> sum stats of all files and print all estimated values)
    if mode == 0:

        ts = sppasTierStats(list(tiers), ngram, with_radius, with_alt)
        ds = ts.ds()

        occurrences = ds.len()
        total = ds.total()
        mean = ds.mean()
        median = ds.median()
        stdev = ds.stdev()

        row_data.append(["Tag", "Occurrences", "Total durations",
                         "Mean durations", "Median durations",
                         "Std dev. durations"])
        for key in occurrences:
            row_data.append([key,
                             "{:d}".format(occurrences[key]),
                             "{:.4f}".format(total[key]),
                             "{:.4f}".format(mean[key]),
                             "{:.4f}".format(median[key]),
                             "{:.4f}".format(stdev[key])])

    # One value (mean, occ, ...) separately for each files
    else:
        data = list()
        for tier in tiers:
            ts = sppasTierStats(tier, ngram, with_radius, with_alt)
            ds = ts.ds()
            data.append(ds)

        title = ["Tag"]
        title.extend([tiers[t] for t in tiers])
        row_data.append(title)

        # estimates descriptive statistics
        stat_values = list()
        items = list()  # the list of labels
        for ds in data:
            if mode == 1:
                stat_values.append(ds.len())

            elif mode == 2:
                stat_values.append(ds.total())

            elif mode == 3:
                stat_values.append(ds.mean())

            elif mode == 4:
                stat_values.append(ds.median())

            elif mode == 5:
                stat_values.append(ds.stdev())

            items.extend(ds.len().keys())

        if mode == 1:
            for i, item in enumerate(sorted(set(items))):
                row = [item] + ["{:d}".format(stat.get(item, 0)) for stat in stat_values]
                row_data.append(row)
        else:
            for i, item in enumerate(sorted(set(items))):
                row = [item] + ["{:.4f}".format(stat.get(item, 0)) for stat in stat_values]
                row_data.append(row)

    # -----------------------------------------------------------------------
    # Save stats
    # -----------------------------------------------------------------------

    if args.o:
        file_output = args.o
        with codecs.open(file_output, 'w', sg.__encoding__) as fp:
            for row in row_data:
                fp.write(','.join(row))
                fp.write('\n')

    else:
        for row in row_data:
            print(','.join(row))
