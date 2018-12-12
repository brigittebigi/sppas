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

    bin.momel.py
    ~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      Run the momel automatic annotations

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg, annots
from sppas import sppasMomel
from sppas.src.anndata.aio import extensions_out
from sppas.src.annotations.param import sppasParam
from sppas.src.config.ui import sppasAppConfig
from sppas.src.annotations.manager import sppasAnnotationsManager
from sppas.src.utils.fileutils import setup_logging

if __name__ == "__main__":
    
    # ------------------------------------------------------------------------
    # Fix initial annotation parameters
    # ------------------------------------------------------------------------
    
    parameters = sppasParam(["Momel.ini"])
    ann_step_idx = parameters.activate_annotation("momel")
    ann_options = parameters.get_options(ann_step_idx)
    
    # -----------------------------------------------------------------------
    # Verify and extract args:
    # ------------------------------------------------------------------------
    
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

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-i",
        metavar="file",
        help='Input file name (extension: .hz or .PitchTier)')

    group_io.add_argument(
        "-o",
        metavar="file",
        help="Output file name (default: stdout)")

    group_io.add_argument(
        "-I",
        metavar="file",
        action='append',
        help='Input file name with pitch (append).')

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
            help=opt.get_text()+" (default: {:s})".format(opt.get_untypedvalue()))
    
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
        parameters.set_logfilename(cg.log_file)
        if not args.quiet:
            setup_logging(cg.log_level, None)
        else:
            setup_logging(cg.quiet_log_level, None)

    # Get options from arguments
    # --------------------------

    arguments = vars(args)
    for a in arguments:
        if a not in ('i', 'o', 'I', 'e', 'quiet'):
            parameters.set_option_value(ann_step_idx, a, arguments[a])

    if args.i:

        # Perform the annotation on a single file
        # ---------------------------------------

        melodie = sppasMomel(logfile=None)
        melodie.fix_options(parameters.get_options(ann_step_idx))
        if args.o:
            melodie.run(args.i, args.o)
        else:
            trs = melodie.run(args.i, None)
            for a in trs[0]:
                print("{:f} {:f}".format(
                    a.get_location().get_best().get_midpoint(),
                    a.get_best_tag().get_typed_content()))

    elif args.I:

        # Perform the annotation on a set of files
        # ----------------------------------------

        # Fix the output file extension
        parameters.set_output_format(args.e)

        # Fix input files
        files = list()
        for f in args.I:
            parameters.add_sppasinput(os.path.abspath(f))

        # Perform the annotation
        process = sppasAnnotationsManager(parameters)
        process.run_intsint()

    else:

        if not args.quiet:
            print("No file was given to be annotated. Nothing to do!")
