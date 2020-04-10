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

:author:       Laurent Vouriot
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      a script to use workspaces from terminal

Examples:

Create or open a workspace :
>>>  ./sppas/sppas/bin/workspaces.py -w myWorkspace

if -w not specified the workspace will be 'blank' by default

Adding a file to the workspace :
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace -a ./sppas/samples/samples-fra/BX_track_0451.wav

Checking a file :
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace -cf ./sppas/samples/samples-fra/BX_track_0451.wav

if you want to check/uncheck all the files use the argument --check_all / unscheck_all

An "all-in-one" solution :
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace -a ./sppas/samples/samples-fra/BX_track_0451.wav -cf ./sppas/samples/samples-fra/BX_track_0451.wav

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
WORKSPACES = SPPAS + "/workspaces"
sys.path.append(SPPAS)

from sppas.src.config import sg
from sppas.src.files import FileData, FilePath
from sppas.src.files import States
from sppas.src.files.fileexc import FileOSError

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

    # Add arguments for input/output files
    # ---------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-w",
        metavar="workspace",
        help="open or create a workspace."
    )

    group_io.add_argument(
        "-r",
        metavar="remove",
        help="remove an existing workspace."
    )

    group_io.add_argument(
        "-a",
        metavar="add",
        help="add a file to a workspace."
    )

    group_io.add_argument(
        "-rf",
        metavar="remove_file",
        help="remove a file of a workspace."
    )

    # Arguments for setting the state of a file
    # -----------------------------------------

    group_state = parser.add_argument_group('State')

    group_state.add_argument(
        "--check_all",
        action="store_true",
        help="check all the files of the workspace you're working on"
    )

    group_state.add_argument(
        "--uncheck_all",
        action="store_true",
        help="uncheck all the files of the workspace you're working on"
    )
    group_state.add_argument(
        "-cf",
        metavar="check_file",
        help="check a file of a workspace."
    )

    group_state.add_argument(
        "-uf",
        metavar="uncheck_file",
        help="uncheck a file of a workspace."
    )

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()
    arguments = vars(args)

    # default workspace : blank
    # -------------------------

    ws = FileData("blank")
    savefile = "{}/blank.wjson".format(WORKSPACES)

    try:
        # open workspace, create one if not exist
        if args.w:
            savefile = "{}/{}.wjson".format(WORKSPACES, args.w)

            # workspace exits, loading it
            if os.path.isfile(savefile):
                ws = ws.load(savefile)

            # else creating a new one
            else:
                print("creating new workspace")
                ws = FileData(args.w)
                ws.save(savefile)
            print("working on : {} in directory {}".format(args.w, WORKSPACES))

        # remove existing workspace
        if args.r:
            os.remove("{}/{}.wjson".format(WORKSPACES, args.r))
            print("remove existing workspace :  {}".format(args.r))

        # adding a file to a workspace
        if args.a:
            ws.add_file(args.a)
            ws.save(savefile)
            print("added the file : {} ".format(args.a))

        # removing a file of a workspace
        if args.rf:
            ws.remove_file(args.rf)
            ws.save(savefile)
            print("removed the file : {} from the workspace : {}".format(args.rf, ws))

        # check a file
        if args.cf:
            if not os.path.isfile(args.cf):
                raise FileNotFoundError("ERROR : {} not found".format(args.cf))
            if args.all:
                ws.set_object_state(States().CHECKED,)
            else:
                ws.set_object_state(States().CHECKED, ws.get_object(args.cf))
            ws.save(savefile)
            print("checked file : {}".format(args.cf))

        # uncheck a file
        if args.uf:
            if not os.path.isfile(args.uf):
                raise FileNotFoundError("ERROR : {} not found".format(args.cf))
            ws.set_object_state(States().UNUSED, ws.get_object(args.cf))
            ws.save(savefile)
            print("unchecked file : {}".format(args.uf))

        if args.check_all:
            ws.set_object_state(States().CHECKED)
            ws.save(savefile)
            print("checked all files")

        if args.uncheck_all:
            ws.set_object_state(States().UNUSED)
            ws.save(savefile)
            print("unchecked all files")

    except FileNotFoundError as e:
        print(e)
    except FileOSError as e:
        print(e)






