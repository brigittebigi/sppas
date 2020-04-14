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


from sppas import paths
from sppas.src.config import sg
from sppas.src.ui.wkps import sppasWorkspaces
from sppas.src.files import FileData, FilePath, FileReference
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

    # Arguments for references
    # ------------------------

    group_ref = parser.add_argument_group('References')

    # create reference (set the id)
    group_ref.add_argument(
        "-cr",
        metavar="create_reference",
        help="create a references"
    )

    # set the type of the argument
    group_ref.add_argument(
        "-t",
        metavar="type",
        help="set the type of the created reference"
    )

    group_ref.add_argument(
        "--state",
        action="store_true",
        help="set the state of a reference(CHECKED, UNCHECKED)"
    )

    group_ref.add_argument(
        "-associate",
        metavar="associate",
        help="associate a references to checked files"
    )

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()
    arguments = vars(args)

    # Workspaces
    # -------------------------

    ws = sppasWorkspaces()
    try:
        # open workspace, create one if not exist
        if args.w:
            ws_name = args.w
            # workspace exits, loading it
            fn = os.path.join(paths.wkps, ws_name) + sppasWorkspaces.ext
            if os.path.exists(fn):
                fd = ws.load_data(ws.index(ws_name))
            # else creating a new one
            else:
                print("creating new workspace")
                fd = FileData(ws.new(ws_name))

            print("working on : {}".format(ws_name))

        # remove existing workspace
        if args.r:
            ws.delete(ws.index(args.r))
            print("removing existing workspace :  {}".format(args.r))

        # adding a file to a workspace
        if args.a:
            fd.add_file(args.a)
            ws.save_data(fd, ws.index(ws_name))
            print("added the file : {} ".format(args.a))

        # removing a file of a workspace
        if args.rf:
            print(fd.remove_file(args.rf))
            ws.save_data(fd, ws.index(ws_name))
            print("removed the file : {} from the workspace : {}".format(args.rf, ws_name))

        # check a file
        if args.cf:
            if not os.path.isfile(args.cf):
                raise FileNotFoundError("ERROR : {} not found".format(args.cf))
            fd.set_object_state(States().CHECKED, fd.get_object(args.cf))
            ws.save_data(fd, ws.index(ws_name))
            print("checked file : {}".format(args.cf))

        # uncheck a file
        if args.uf:
            if not os.path.isfile(args.uf):
                raise FileNotFoundError("ERROR : {} not found".format(args.uf))
            fd.set_object_state(States().UNUSED, fd.get_object(args.uf))
            ws.save_data(fd, ws.index(ws_name))
            print("unchecked file : {}".format(args.uf))

        if args.check_all:
            ws.set_object_state(States().CHECKED)
            # ws.save(savefile)
            print("checked all files")

        if args.uncheck_all:
            ws.set_object_state(States().UNUSED)
            # ws.save(savefile)
            print("unchecked all files")

        # References
        # ----------

        # creating a new reference and set its type if specified otherwise set as STANDALONE by default
        if args.cr:
            ref = FileReference(args.cr)
            if args.t:
                ref.set_type(args.t)
            if args.state:
                ref.set_state(States().CHECKED)
            # ws.save(savefile)
            print("reference : {} [{}] created".format(args.cr, ref.get_type()))

        if args.associate:
            print(ws.associtate())
            # ws.save(savefile)

    except FileNotFoundError as e:
        print(e)
    except FileOSError as e:
        print(e)






