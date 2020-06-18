#!/usr/bin/env python
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

    bin.alignment.py
    ~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2019  Brigitte Bigi
:summary:      Run the alignment automatic annotation

"""

import logging
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg, annots
from sppas import sppasLogSetup
from sppas import sppasAppConfig

from sppas.src.anndata import sppasRW
from sppas.src.annotations import sppasAlign
from sppas.src.annotations import sppasParam
from sppas.src.annotations import sppasAnnotationsManager

extensions_out = sppasRW.extensions_out()

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["alignment.json"])
    ann_step_idx = parameters.activate_annotation("alignment")
    ann_options = parameters.get_options(ann_step_idx)

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [files] [options]",
        description=
        parameters.get_step_name(ann_step_idx) + ": " +
        parameters.get_step_descr(ann_step_idx),
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    parser.add_argument(
        "--log",
        metavar="file",
        help="File name for a Procedure Outcome Report (default: None)")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-i",
        metavar="file",
        help='Input wav file name.')

    group_io.add_argument(
        "-p",
        metavar="file",
        help='Input file name with the phonetization.')

    group_io.add_argument(
        "-t",
        metavar="file",
        help='Input file name with the tokenization.')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output file name with estimated alignments.')

    group_io.add_argument(
        "-r",
        metavar="model",
        help='Directory of the acoustic model of the language of the text')

    group_io.add_argument(
        "-R",
        metavar="model",
        help='Directory of the acoustic model of the mother language of the speaker')

    group_io.add_argument(
        "-I",
        metavar="file",
        action='append',
        help='Input file name (append).')

    group_io.add_argument(
        "-l",
        metavar="lang",
        choices=parameters.get_langlist(ann_step_idx),
        help='Language code (iso8859-3). One of: {:s}.'
             ''.format(" ".join(parameters.get_langlist(ann_step_idx))))

    group_io.add_argument(
        "-e",
        metavar=".ext",
        default=annots.extension,
        choices=extensions_out,
        help='Output file extension. One of: {:s}'
             ''.format(" ".join(extensions_out)))

    # Add arguments from the options of the annotation
    # ------------------------------------------------

    group_opt = parser.add_argument_group('Options')

    for opt in ann_options:
        group_opt.add_argument(
            "--" + opt.get_key(),
            type=opt.type_mappings[opt.get_type()],
            default=opt.get_value(),
            help=opt.get_text() + " (default: {:s})"
                                  "".format(opt.get_untypedvalue()))

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Mutual exclusion of inputs
    # --------------------------

    if args.i and args.I:
        parser.print_usage()
        print("{:s}: error: argument -I: not allowed with argument -i"
              "".format(os.path.basename(PROGRAM)))
        sys.exit(1)

    # -----------------------------------------------------------------------
    # The automatic annotation is here:
    # -----------------------------------------------------------------------

    # Redirect all messages to logging
    # --------------------------------

    with sppasAppConfig() as cg:
        if not args.quiet:
            log_level = cg.log_level
        else:
            log_level = cg.quiet_log_level
        lgs = sppasLogSetup(log_level)
        lgs.stream_handler()

    # Get options from arguments
    # --------------------------

    arguments = vars(args)
    for a in arguments:
        if a not in ('i', 'o', 'p', 't', 'r', 'R', 'I', 'l', 'e', 'quiet', 'log'):
            parameters.set_option_value(ann_step_idx, a, str(arguments[a]))

    if args.i or args.p:

        # Perform the annotation on a single file
        # ---------------------------------------

        if not args.p:
            print("argparse.py: error: option -p is required with option -i")
            sys.exit(1)

        ann = sppasAlign(log=None)
        if args.r:
            ann.load_resources(args.r, args.R)
        ann.fix_options(parameters.get_options(ann_step_idx))
        ann.print_options()

        if args.o:
            ann.run([args.p], [args.i, args.t], args.o)

        else:
            trs = ann.run([args.p], [args.i, args.t])
            for tier in trs:
                print(tier.get_name())
                for a in tier:
                    print("{} {} {:s}".format(
                        a.get_location().get_best().get_begin().get_midpoint(),
                        a.get_location().get_best().get_end().get_midpoint(),
                        a.serialize_labels(" ")))

    elif args.I:

        # Perform the annotation on a set of files
        # ----------------------------------------

        if not args.l:
            print("argparse.py: error: option -l is required with option -I")
            sys.exit(1)

        # Fix input files
        for f in args.I:
            parameters.add_to_workspace(os.path.abspath(f))

        # Fix the output file extension and others
        parameters.set_lang(args.l)
        parameters.set_output_format(args.e)
        parameters.set_report_filename(args.log)

        # Perform the annotation
        process = sppasAnnotationsManager()
        process.annotate(parameters)

    else:

        if not args.quiet:
            logging.info("No file was given to be annotated. Nothing to do!")
