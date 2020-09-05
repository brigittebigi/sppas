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

    bin.otherrepetition.py
    ~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2019  Brigitte Bigi
:summary:      Other-Repetitions automatic annotation.

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas import sppasLogSetup
from sppas import sppasAppConfig
from sppas.src.config import cfg

from sppas.src.annotations import sppasAnnotationsManager
from sppas.src.annotations import sppasLexRep
from sppas.src.annotations import sppasParam
from sppas.src.wkps import sppasWkpRW

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["lexrep.json"])
    ann_step_idx = parameters.activate_annotation("spklexrep")
    ann_options = parameters.get_options(ann_step_idx)
    extensions_out = parameters.get_output_extensions(ann_step_idx)

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
                                        sg.__copyright__, sg.__contact__))

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    # Add arguments for input/output files
    # ------------------------------------

    group_wkp = parser.add_argument_group('Files (auto)')
    group_wkp.add_argument(
        "-w",
        metavar="wkp",
        help='Workspace.')
    group_wkp.add_argument(
        "-l",
        metavar="lang",
        choices=parameters.get_langlist(ann_step_idx),
        help='Language code (iso8859-3). One of: {:s}.'
             ''.format(" ".join(parameters.get_langlist(ann_step_idx))))
    group_wkp.add_argument(
        "-e",
        metavar=".ext",
        default=parameters.get_output_extension(ann_step_idx),
        choices=extensions_out,
        help='Output file extension. One of: {:s}'
             ''.format(" ".join(extensions_out)))
    group_wkp.add_argument(
        "--log",
        metavar="file",
        help="File name for a Procedure Outcome Report (default: None)")

    group_io = parser.add_argument_group('Files (manual)')
    group_io.add_argument(
        "-i",
        metavar="file",
        help='Input file name with time-aligned tokens of speaker 1.')
    group_io.add_argument(
        "-s",
        metavar="file",
        help='Input file name with time-aligned tokens of speaker 2.')
    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output file name with other-repetitions.')
    group_io.add_argument(
        "-r",
        help='List of stop-words')

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
    if args.w and args.i:
        print("argparse.py: error: choose either -w or -i input options, not both.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # The automatic annotation is here:
    # -----------------------------------------------------------------------

    # Redirect all messages to logging
    # --------------------------------

    # parameters.set_report_filename(cfg.log_file)
    if not args.quiet:
        log_level = cfg.log_level
    else:
        log_level = cfg.quiet_log_level
    lgs = sppasLogSetup(log_level)
    lgs.stream_handler()

    # Get options from arguments
    # --------------------------

    arguments = vars(args)
    for a in arguments:
        if a not in ('i', 'o', 's', 'r', 'w', 'l', 'e', 'log', 'quiet'):
            parameters.set_option_value(ann_step_idx, a, str(arguments[a]))
            o = parameters.get_step(ann_step_idx).get_option_by_key(a)

    if args.i:

        if not args.s:
            print("argparse.py: error: option -s is required with option -i")
            sys.exit(1)

        # Perform the annotation on a single file
        # ---------------------------------------

        ann = sppasLexRep()
        ann.load_resources(args.r)
        ann.fix_options(parameters.get_options(ann_step_idx))
        if args.o:
            ann.run([args.i, args.s], output_file=args.o)
        else:
            trs = ann.run([args.i, args.s])

            for tier in trs:
                for a in tier:
                    print("{} {} {:s}".format(
                        a.get_location().get_best().get_begin().get_midpoint(),
                        a.get_location().get_best().get_end().get_midpoint(),
                        a.get_best_tag().get_content()))

    elif args.w:

        if not args.l:
            print("argparse.py: error: option -l is required with option -w")
            sys.exit(1)

        parser = sppasWkpRW(args.w)
        wkp = parser.read()
        parameters.set_workspace(wkp)

        # Fix the output file extension and others
        parameters.set_lang(args.l)
        parameters.set_output_extension(args.e, parameters.get_outformat(ann_step_idx))
        parameters.set_report_filename(args.log)

        # Perform the annotation
        process = sppasAnnotationsManager()
        process.annotate(parameters)


    else:

        if not args.quiet:
            print("No file was given to be annotated. Nothing to do!")