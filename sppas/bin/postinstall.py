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
    ~~~~~~~~~~~~~~~~
:author:       Laurent Vouriot
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      a script to use postInstall from terminal

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas.src.config.support import sppasInstallerDeps
from sppas.src.ui.term.textprogress import ProcessProgressTerminal
from sppas.src.ui.term.terminalcontroller import TerminalController

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    installer = sppasInstallerDeps()
    features = installer.get_features()
    cmd_features = list()

    def search_feature(string):
        for feature in features:
            if string == feature.get_id():
                return feature

    parser = ArgumentParser(
        usage="%(prog)s [action]",
        description="PostInstall commmand interface.",
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    # Add arguments from the features of features.ini
    # -----------------------------------------------

    group_act = parser.add_argument_group('Action')

    group_act.add_argument(
        "--install",
        action='store_true',
        help="Launch the installation procedure of the features for you OS")

    for feature in features:
        cmd_features.append(feature.get_id())
        cmd_features.append("no" + feature.get_id())
        group_act.add_argument(
            "--" + feature.get_id(),
            action='store_true',
            help="Enable the {desc} (Available={available})"
            .format(desc=feature.get_desc(), available=feature.get_available()))

        group_act.add_argument(
            "--no" + feature.get_id(),
            action='store_true',
            help="Disable the {desc}"
            .format(desc=feature.get_desc()))

    # Add arguments from the features of features.ini
    # -----------------------------------------------

    parser.add_argument(
        "-e",
        "--enable",
        action='store_true',
        help="Show for each feature if it is available on your OS and if the installation is enable.")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # The installation process is here:
    # -----------------------------------------------------------------------

    if args.enable:
        print("\nIf an feature has his available = False, even if you set enable to true it wont install the feature. "
              "\nBecause \"available = false\" mean that the installer can't install the feature on your OS.")
        print(installer.get_enables())

    arguments = vars(args)
    arguments_true = list()
    for a in arguments:
        if arguments[a] is True:
            arguments_true.append(a)
    for a in arguments_true:
        if a in cmd_features:
            if "no" not in a:
                cmd = "no" + a
                if cmd in arguments_true:
                    installer.unset_enable(search_feature(a))
                else:
                    installer.set_enable(search_feature(a))
            elif "no" in a:
                a = a.replace("no", "")
                installer.unset_enable(search_feature(a))

    if args.install:
        if installer.get_install() is True:
            print("\nYou already installed the features.\n"
                  "If you want to reinstalled it you have to remove the file \"config.ini\"\n")
        installer.install()

