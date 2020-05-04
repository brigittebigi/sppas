#!/usr/bin/env python
# -*- coding : utf-8 -*-
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
    ~~~~~~~~~~~~~~~~

:author:       Laurent Vouriot
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      a script to use workspaces from terminal

Examples:

Create or open a workspace :
>>>  ./sppas/sppas/bin/workspaces.py -w myWorkspace

Adding a file to the workspace :
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace -af ./sppas/samples/samples-fra/BX_track_0451.wav

Checking a file (or a reference):
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace -cf ./sppas/samples/samples-fra/BX_track_0451.wav

if you want to check/uncheck all the files use the argument --check_all /--uncheck_all

An "all-in-one" solution :
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace -af ./sppas/samples/samples-fra/BX_track_0451.wav -cf ./sppas/samples/samples-fra/BX_track_0451.wav

Create a reference in a workspace :
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace -cr reference

you can immediately check this reference with the option --check

Associate each checked files with each checked references
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace  --associate

Create an attribute that is added to each checked references
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace  -att attribute

You can set every parametres of an attribute in one line
>>> ./sppas/sppas/bin/workspaces.py -w myWorkspace  -att attribute -val 123 -type int -desc description...

Import workspace from a file
>>> ./sppas/sppas/bin/workspaces.py -iw path/myImportedWorkspace

Export workspace to a file
>>> ./sppas/sppas/bin/workspaces.py -ew myWorkspace
"""

import sys
import os
from argparse import ArgumentParser
import json

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import paths
from sppas.src.config import sg
from sppas.src.wkps import sppasWkps
from sppas.src.wkps import FileReference, States, sppasAttribute
from sppas.src.wkps.wkpexc import FileOSError
from sppas.src.exc import sppasTypeError

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
        "-af",
        metavar="add",
        help="add a file to a workspace."
    )

    group_io.add_argument(
        "-rf",
        metavar="remove_file",
        help="remove a file of a workspace."
    )

    # Arguments for setting the state of a file/reference
    # ---------------------------------------------------

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
        help="check a file (or a reference) of a workspace."
    )

    group_state.add_argument(
        "-uf",
        metavar="uncheck_file",
        help="uncheck a file (or a reference) of a workspace."
    )

    group_state.add_argument(
        "--check",
        action="store_true",
        help="check a file or a reference when created."
    )

    # Arguments for references
    # ------------------------

    group_ref = parser.add_argument_group('References')

    group_ref.add_argument(
        "-ar",
        metavar="add_reference",
        help="add a reference."
    )

    group_ref.add_argument(
        "-tr",
        metavar="type",
        help="set the type of the created reference."
    )

    group_ref.add_argument(
        "--remove_refs",
        action="store_true",
        help="remove checked reference(s)."
    )

    group_ref.add_argument(
        "--associate",
        action="store_true",
        help="associate reference(s) to file(s)."
    )

    group_ref.add_argument(
        "--dissociate",
        action="store_true",
        help="dissociate reference(s) to file(s)."
    )

    # Arguments for sppasAttributes
    # ------------------------------

    group_att = parser.add_argument_group('sppasAttributes')

    group_att.add_argument(
        "-att",
        metavar="create_attribute",
        help="create a new sppasAttribute."
    )

    group_att.add_argument(
        "-val",
        metavar="value_attribute",
        help="set the value of the attribute."
    )

    group_att.add_argument(
        "-type",
        metavar="type_attribute",
        help="set the type value of an attribute."
    )
    group_att.add_argument(
        "-desc",
        metavar="description_attribute",
        help="set the description of an attribute."
    )

    group_att.add_argument(
        "-ratt",
        metavar="remove_attribute",
        help="remove an attribute from a reference."
    )

    group_att.add_argument(
        "-setattr",
        metavar="set_attribute",
        help="set a an existing attribute."

    )

    #  Verbose mode
    # -------------

    group_verbose = parser.add_argument_group('verbose')

    group_verbose.add_argument(
        "--quiet",
        action="store_true",
        help="verbose mode."
    )

    # import/export files
    # --------------------

    group_io = parser.add_argument_group('io')

    group_io.add_argument(
        "-iw",
        metavar="import_workspace",
        help="import an external workspace"
    )

    group_io.add_argument(
        "-ew",
        metavar="export_workspace",
        help="export a workspace"
    )

    # TESTS
    # -----

    group_tests = parser.add_argument_group('tests')

    group_tests.add_argument(
        "-test",
        metavar="tests",
        help="tests"
    )

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()
    arguments = vars(args)

    try:

        # Workspaces
        # ----------

        ws = sppasWkps()
        # fd = sppasWorkspace()
        ws_name = None
        # open workspace, create one if not exist
        if args.w:
            ws_name = args.w
            # workspace exits, loading it
            fn = os.path.join(paths.wkps, ws_name) + sppasWkps.ext
            if os.path.exists(fn):
                fd = ws.load_data(ws.index(ws_name))
            # else creating a new one
            else:
                if not args.quiet:
                    print("creating new workspace")
                fd = ws.new(ws_name)

            refs = fd.get_refs()

            if not args.quiet:
                print("working on : {}".format(ws_name))

        # remove existing workspace
        if args.r:
            ws.delete(ws.index(args.r))
            if not args.quiet:
                print("removing existing workspace :  {}".format(args.r))

        # adding a file to a workspace
        if args.af:
            fd.add_file(args.af)
            if args.check:
                fd.set_object_state(States().CHECKED, fd.get_object(args.af))
            if not args.quiet:
                print("added the file : {} ".format(args.af))

        # removing a file of a workspace
        if args.rf:
            fd.remove_file(args.rf)
            if not args.quiet:
                print("removed the file : {} from the workspace : {}".format(args.rf, ws_name))

        # check a file
        if args.cf:
            # we need to test if the file exist because if not
            # all the files would be checked (files and references)
            found = False
            if fd.get_object(args.cf):
                found = True
                fd.set_object_state(States().CHECKED, fd.get_object(args.cf))
            for ref in fd.get_refs():
                if ref.id == args.cf:
                    found = True
                    fd.set_object_state(States().CHECKED, fd.get_object(args.cf))
            if not found:
                raise FileNotFoundError("ERROR : {} not found".format(args.cf))
            if not args.quiet:
                print("{} : checked".format(args.cf))

        # uncheck a file
        if args.uf:
            found = False
            if fd.get_object(args.uf):
                found = True
                fd.set_object_state(States().UNUSED, fd.get_object(args.uf))
                # ws.save_data(fd, ws.index(ws_name))
            for ref in fd.get_refs():
                if ref.id == args.uf:
                    found = True
                    fd.set_object_state(States().UNUSED, fd.get_object(args.uf))
            if not found:
                raise FileNotFoundError("ERROR : {} not found".format(args.uf))
            if not args.quiet:
                print("{} : unchecked".format(args.uf))

        # check all the file(s) and reference(s)
        if args.check_all:
            fd.set_object_state(States().CHECKED)
            # ws.save_data(fd, ws.index(ws_name))
            if not args.quiet:
                print("checked all files")

        # uncheck
        if args.uncheck_all:
            fd.set_object_state(States().UNUSED)
            # ws.save_data(fd, ws.index(ws_name))
            if not args.quiet:
                print("unchecked all files")

        # References
        # ----------

        # creating a new reference and setting its type if specified
        # otherwise set as STANDALONE by default
        if args.ar:
            ref = FileReference(args.ar)
            if args.tr:
                ref.set_type(args.tr)
            if args.check:
                ref.set_state(States().CHECKED)
            fd.add_ref(ref)
            if not args.quiet:
                print("reference : {} [{}] created".format(args.ar, ref.get_type()))

        # remove a reference
        if args.remove_refs:
            nb = fd.remove_refs()
            if not args.quiet:
                print("removed {} reference(s)".format(nb))

        # associate file(s) and reference(s)
        if args.associate:
            fd.associate()
            if not args.quiet:
                for file in fd.get_files():
                    print(file)
                    for ref in fd.get_refs():
                        if ref.get_state() == States().CHECKED:
                            print("{} associated with {} ".format(file, ref))

        # dissociate
        if args.dissociate:
            fd.dissociate()
            if not args.quiet:
                for file in fd.get_files():
                    for ref in fd.get_refs():
                        if ref.get_state() == States().CHECKED:
                            print("{} dissociated with {} ".format(file, ref))

        # sppasAttribute
        # --------------

        # create a new attribute that we add to every checked references
        if args.att:
            att = sppasAttribute(args.att)
            for ref in refs:
                if ref.get_state() == States().CHECKED:
                    ref.append(att)
            if not args.quiet:
                print("attribute : {} created".format(args.att))

        # if we want to modify an existing attribute
        if args.setattr:
            # check if the attribute exist in the references
            for ref in refs:
                if ref.att(args.setattr):
                    att = ref.att(args.setattr)
                else:
                    raise FileNotFoundError("ERROR : {} not found".format(args.setattr))

        # set the type value
        if args.type:
            if args.type not in sppasAttribute.VALUE_TYPES:
                raise ValueError("ERROR : {} is not a supported type ('str', 'int', 'float', 'bool')"
                                 .format(args.type))
            att.set_value_type(args.type)

        # set attribute value
        if args.val:
            att.set_value(args.val)

        # set the description
        if args.desc:
            att.set_description(args.desc)

        # remove an attribute
        if args.ratt:
            for ref in refs:
                if ref.get_state() == States().CHECKED:
                    ref.pop(args.ratt)
            if not args.quiet:
                print("removing : {}".format(args.ratt))

        # checking if we work on a workspace
        if ws_name is not None:
            fd.update()
            ws.save_data(fd, ws.index(ws_name))

        # Import workspace
        # ----------------

        if args.iw:
            if os.path.exists(args.iw) is False:
                raise FileOSError(args.iw)
            ws.import_from_file(args.iw)
            if not args.quiet:
                print("{} imported".format(args.iw))

        # Export workspace
        # ----------------

        if args.ew:
            print("enter the path you want to save this workspace")
            filename = input()
            path = filename.split(os.sep)
            path.remove(path[-1])
            if os.path.exists(os.sep.join(path)) is False:
                raise FileOSError(path)
            ws.export_to_file(ws.index(args.ew), filename)

            if not args.quiet:
                print("{} exported to {}".format(args.ew, filename))

        # TESTS
        # -----

        # argument used for debug
        if args.test:
            pass

    except FileOSError as e:
        print(e)
    except ValueError as e:
        print(e)
    except sppasTypeError as e:
        print(e)
    except KeyError as e:
        print(e)
    except OSError as e:
        print(e)







