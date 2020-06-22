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

    bin.annotation.py
    ~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2019  Brigitte Bigi
:summary:      Run any or all the automatic annotations.

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg, annots
from sppas import sppasLogSetup

from sppas.src.annotations import sppasParam
from sppas.src.annotations import sppasAnnotationsManager
from sppas.src.anndata.aio import extensions_out
from sppas.src.ui.term.textprogress import ProcessProgressTerminal
from sppas.src.ui.term.terminalcontroller import TerminalController

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters (parse spasui.json)
    # -----------------------------------------------------------------------

    parameters = sppasParam()
    manager = sppasAnnotationsManager()

    all_langs = list()
    all_langs.append("und")
    for i in range(parameters.get_step_numbers()):
        a = parameters.get_step(i)
        all_langs.extend(a.get_langlist())
    all_langs = list(set(all_langs))

    # ----------------------------------------------------------------------------
    # Verify and extract args:
    # ----------------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s -I file|folder [options]",
        description="Automatic annotations.",
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    parser.add_argument(
        "--log",
        metavar="file",
        help="File name for a Procedure Outcome Report (default: None)")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-I",
        required=True,
        metavar="file|folder",
        action='append',
        help='Input transcription file name (append).')

    group_io.add_argument(
        "-l",
        metavar="lang",
        choices=all_langs,
        default="und",
        help='Language code (iso8859-3). One of: {:s}.'
             ''.format(" ".join(all_langs)))

    group_io.add_argument(
        "-e",
        metavar=".ext",
        default=annots.annot_extension,
        choices=extensions_out,
        help='Output annotation file extension. One of: {:s}'
             ''.format(" ".join(extensions_out)))

    # Add the annotations
    # ------------------------------------------------

    for i in range(parameters.get_step_numbers()):
        parser.add_argument(
            "--" + parameters.get_step_key(i),
            action='store_true',
            help="Activate " + parameters.get_step_name(i))

    parser.add_argument(
        "--merge",
        action='store_true',
        help="Create a merged file with all the annotations")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # ----------------------------------------------------------------------------
    # Automatic annotations configuration
    # ----------------------------------------------------------------------------

    # Fix user communication way
    # -------------------------------

    sep = "-"*72
    try:
        term = TerminalController()
        print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
        print(term.render('${RED} {} - Version {}${NORMAL}'
                          '').format(sg.__name__, sg.__version__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__copyright__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__url__))
        print(term.render('${GREEN}{:s}${NORMAL}\n').format(sep))

        # Redirect all messages to a quiet logging
        # ----------------------------------------
        lgs = sppasLogSetup(50)
        lgs.null_handler()

    except:
        print('{:s}\n'.format(sep))
        print('{}   -  Version {}'.format(sg.__name__, sg.__version__))
        print(sg.__copyright__)
        print(sg.__url__+'\n')
        print('{:s}\n'.format(sep))

        # Redirect all messages to a quiet logging
        # ----------------------------------------
        lgs = sppasLogSetup(50)
        lgs.stream_handler()

    # Get annotations from arguments
    # -------------------------------

    print("Annotations: ")
    x = 0
    arguments = vars(args)
    for a in arguments:
        if arguments[a] is True:
            ann = a.replace('--', '')
            for i in range(parameters.get_step_numbers()):
                key = parameters.get_step_key(i)
                if ann == key:
                    parameters.activate_step(i)
                    print(" - {:s}: enabled.".format(ann))
                    x += 1
    print("")
    if x == 0:
        print('No annotation enabled. Nothing to do.')
        sys.exit(1)

    # Get files from arguments
    # -------------------------------

    print("Files and folders: ")
    for f in args.I:
        parameters.add_to_workspace(os.path.abspath(f))
        print(" - {:s}".format(f))
    print("")

    # Get others from arguments
    # -------------------------------

    parameters.set_lang(args.l)
    parameters.set_output_extension(args.e, "ANNOT")
    parameters.set_report_filename(args.log)

    # ----------------------------------------------------------------------------
    # Annotations are running here
    # ----------------------------------------------------------------------------

    p = ProcessProgressTerminal()
    if args.merge:
        manager.set_do_merge(True)
    manager.annotate(parameters, p)

    try:
        term = TerminalController()
        print(term.render('\n${GREEN}{:s}${NORMAL}').format(sep))
        print(term.render('${RED}See {}.').format(parameters.get_report_filename()))
        print(term.render('${GREEN}Thank you for using {}.').format(sg.__name__))
        print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
    except:
        print('\n{:s}\n'.format(sep))
        print("See {} for details.\nThank you for using {}."
              "".format(parameters.get_report_filename(), sg.__name__))
        print('{:s}\n'.format(sep))

    p.close()


