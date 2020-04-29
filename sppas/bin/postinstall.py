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

    bin.postinstall.py
    ~~~~~~~~~~~~~~~~

:author:       Florian Hocquet
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      Launch the installation of features

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas.src.config.support import sppasInstallerDeps

from sppas import sppasLogSetup
from sppas.src.ui.term.textprogress import ProcessProgressTerminal
from sppas.src.ui.term.terminalcontroller import TerminalController

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial sppasInstallerDeps parameters
    # -----------------------------------------------------------------------

    p = ProcessProgressTerminal()
    installer = sppasInstallerDeps(p)
    feats_ids = installer.get_feat_ids()
    cmd_features = list()
    i = 0

    def search_feature(string):
        for feat_id in feats_ids:
            if string == feat_id:
                return feat_id

    # ----------------------------------------------------------------------------
    # Verify and extract args:
    # ----------------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [action]",
        description="PostInstall commmand interface.\n" +
        installer.get_enables(),
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__),
    )

    # Add arguments from the features of features.ini
    # -----------------------------------------------

    group_act = parser.add_argument_group('Action')

    for feature_id in feats_ids:
        cmd_features.append(feature_id)
        cmd_features.append("no" + feature_id)
        group_act.add_argument(
            "--" + feature_id,
            action='store_true',
            help="Enable the {desc}"
            .format(desc=installer.get_feat_desc(feature_id)))

        group_act.add_argument(
            "--no" + feature_id,
            action='store_true',
            help="Disable the {desc}"
            .format(desc=installer.get_feat_desc(feature_id)))

    group_act.add_argument(
        "-a",
        "--all",
        action='store_true',
        help="Install with all the features enabled")

    group_act.add_argument(
        "-d",
        "--default",
        action='store_true',
        help="Install with all the features with their default enable")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Fix user communication way
    # -------------------------------

    sep = "-" * 72
    try:
        term = TerminalController()
        print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
        print(term.render('${RED} {} - Version {}${NORMAL}'
                          '').format(sg.__name__, sg.__version__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__copyright__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__url__))
        print(term.render('${GREEN}{:s}${NORMAL}\n').format(sep))

        # Redirect all messages to a logging
        # ----------------------------------------
        lgs = sppasLogSetup(0)
        lgs.null_handler()

    except:
        print('{:s}\n'.format(sep))
        print('{}   -  Version {}'.format(sg.__name__, sg.__version__))
        print(sg.__copyright__)
        print(sg.__url__ + '\n')
        print('{:s}\n'.format(sep))

        # Redirect all messages to a logging
        # ----------------------------------
        lgs = sppasLogSetup(0)
        lgs.null_handler()

    # ------------------------------
    # Installation is running here :
    # ------------------------------

    if args.all:
        for feat_id in feats_ids:
            installer.set_enable(feat_id)
        installer.install()

    elif args.default:
        installer.install()

    # Set the values of enable for each feature
    # -----------------------------------------
    else:
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
        installer.install()

    try:
        term = TerminalController()
        print(term.render('\n${GREEN}{:s}${NORMAL}').format(sep))
        print(term.render('${RED}See {}.').format("..."))
        print(term.render('${GREEN}Thank you for using {}.').format(sg.__name__))
        print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
    except:
        print('\n{:s}\n'.format(sep))
        print("See {} for details.\nThank you for using {}."
              "".format("...", sg.__name__))
        print('{:s}\n'.format(sep))

    p.close()
