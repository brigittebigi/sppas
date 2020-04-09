#!/usr/bin/env python
# -*- coding : UTF-8 -*-
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

    bin.workspaces.py
    ~~~~~~~~~~~~~

:author:    Laurent Vouriot
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      a script to manage workspaces

Exemples:
        TODO
"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
WORKSPACES = SPPAS + "/workspaces"
sys.path.append(SPPAS)

from sppas import sg
from sppas.src.files import FileData

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [actions] [files]",
        description="Workspace command line interface.",
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    # Add arguments for actions
    # -------------------------

    group_act = parser.add_argument_group('Actions')

    # pourquoi pas faire une seule option si le ws n'existe pas on le crée à ce moment
    group_act.add_argument(
        "-c",
        metavar="create",
        help="Create a new workspace."
    )

    group_act.add_argument(
        "-r",
        metavar="remove",
        help="remove an existing workspace."
    )

    group_act.add_argument(
        "-o",
        metavar="open",
        help="open a existing workspace."
    )

    group_act.add_argument(
        "-a",
        metavar="add",
        help="add a file to a workspace."
    )

    # peut-être changer le nom de la commande
    group_act.add_argument(
        "-rf",
        metavar="remove_file",
        help="remove a file of a workspace."
    )

    group_act.add_argument(
        "-cf",
        metavar="check",
        help="check a file of a workspace."
    )

    group_act.add_argument(
        "-uf",
        metavar="uncheck",
        help="uncheck a file of a workspace."
    )


    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    print(args)

    # verify if arguments are with the rights options
    # -----------------------------------------------

    arguments = vars(args)

    if args.c:
        print("created and saved new workspace {} in directory {}".format(args.c, WORKSPACES))
        # TODO : create ws
        ws = FileData(args.c)
        ws.save("{}/{}.wjson".format(WORKSPACES, args.c))
    if args.r:
        print("remove existing workspace {}".format(args.r))
        # bash ?
        # TODO : remove ws
    if args.o:
        print("open existing workspace {}").format(args.o)
        # TODO : load ws
    if args.a:
        print("add a file to the ws {}".format(args.a))
        # TODO : add file to ws
    if args.cf:
        print("check file {}".format(args.cf))
        # TODO : check file
    if args.uf:
        print("uncheck file {}".format(args.uf))
        # TODO : check file



