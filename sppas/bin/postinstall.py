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

from sppas.src.config.installer import sppasInstallerDeps
from sppas import sg

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    installer = sppasInstallerDeps()
    features = installer.get_features()

    parser = ArgumentParser(
        usage="%(prog)s [action] [option]",
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
        group_act.add_argument(
            "--" + feature.get_id(),
            #default=feature.set_enable(),
            desc="a",
            help="{id}: {desc}, set the value enable to True.".format(id=feature.get_id(), desc=feature.get_desc()))

    # Add arguments for options
    # -------------------------

    group_opt = parser.add_argument_group('Option')

    group_opt.add_argument(
        "-e",
        #default=installer.get_enables(),
        help="Display the enable value associate with the id for each feature you have.")

    group_opt.add_argument(
        "-e",
        #default=installer.get_enables(),
        help="Display the enable value associate with the id for each feature you have.")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()










