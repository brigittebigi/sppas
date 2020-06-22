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

    bin.normalize.py
    ~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2019  Brigitte Bigi
:summary:      Text normalization automatic annotation.

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg, paths, annots
from sppas import sppasLogSetup
from sppas import sppasAppConfig

from sppas.src.anndata.aio import extensions_out
from sppas.src.annotations import sppasTextNorm
from sppas.src.annotations.TextNorm.normalize import TextNormalizer
from sppas.src.annotations import sppasParam
from sppas.src.annotations import sppasAnnotationsManager
from sppas.src.resources import sppasVocabulary
from sppas.src.resources import sppasDictRepl

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["textnorm.json"])
    ann_step_idx = parameters.activate_annotation("textnorm")
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
                                        sg.__copyright__, sg.__contact__))

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
        help='Input transcription file name.')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Annotated file with normalized tokens.')

    group_io.add_argument(
        "-I",
        metavar="file",
        action='append',
        help='Input file name (append).')

    group_io.add_argument(
        "-r",
        metavar="vocab",
        help='Vocabulary file name')

    group_io.add_argument(
        "-l",
        metavar="lang",
        choices=parameters.get_langlist(ann_step_idx),
        help='Language code (iso8859-3). One of: {:s}.'
             ''.format(" ".join(parameters.get_langlist(ann_step_idx))))

    group_io.add_argument(
        "-e",
        metavar=".ext",
        default=annots.annot_extension,
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
        if a not in ('i', 'o', 'I', 'e', 'r', 'l', 'quiet', 'log'):
            parameters.set_option_value(ann_step_idx, a, str(arguments[a]))

    if args.i:

        # Perform the annotation on a single file
        # ---------------------------------------

        if not args.r:
            print("argparse.py: error: option -r is required with option -i")
            sys.exit(1)

        if args.l:
            lang = args.l
        else:
            lang = os.path.basename(args.r)[:3]

        ann = sppasTextNorm(log=None)
        ann.load_resources(args.r, lang=lang)
        ann.fix_options(parameters.get_options(ann_step_idx))

        if args.o:
            ann.run([args.i], output_file=args.o)
        else:
            trs = ann.run([args.i])
            for tier in trs:
                print(tier.get_name())
                for a in tier:
                    if a.location_is_point():
                        print("{}, {:s}".format(
                            a.get_location().get_best().get_midpoint(),
                            a.serialize_labels(" ")))
                    else:
                        print("{}, {}, {:s}".format(
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
        parameters.set_output_extension(args.e, parameters.get_outformat(ann_step_idx))
        parameters.set_report_filename(args.log)

        # Perform the annotation
        manager = sppasAnnotationsManager()
        manager.annotate(parameters)

    else:

        # Perform the annotation on stdin
        # -------------------------------

        if not args.r:
            print("argparse.py: error: option -r is required with option -i")
            sys.exit(1)

        if args.l:
            lang = args.l
        else:
            lang = os.path.basename(args.r)[:3]

        vocab = sppasVocabulary(args.r)
        normalizer = TextNormalizer(vocab, lang)

        replace_file = os.path.join(paths.resources, "repl", lang + ".repl")
        if os.path.exists(replace_file):
            repl = sppasDictRepl(replace_file, nodump=True)
            normalizer.set_repl(repl)

        punct_file = os.path.join(paths.resources, "vocab", "Punctuations.txt")
        if os.path.exists(punct_file):
            punct = sppasVocabulary(punct_file, nodump=True)
            normalizer.set_punct(punct)

        # Number dictionary
        number_filename = os.path.join(paths.resources, 'num', lang.lower() + '_num.repl')
        if os.path.exists(number_filename) is True:
            numbers = sppasDictRepl(number_filename, nodump=True)
            normalizer.set_num(numbers)

        # Will output the faked orthography
        for line in sys.stdin:
            tokens = normalizer.normalize(line)
            for token in tokens:
                print("{!s:s}".format(token))
