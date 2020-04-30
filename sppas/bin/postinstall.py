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
from sppas.src.config.configuration import Configuration

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial sppasInstallerDeps parameters
    # -----------------------------------------------------------------------

    p = ProcessProgressTerminal()
    cfg = Configuration()
    installer = sppasInstallerDeps(p)
    feats_ids = installer.get_feat_ids()
    cmd_features = list()
    i = 0
    x = 0

    def search_feature(string):
        for feat_id in feats_ids:
            if string == feat_id:
                return feat_id

    def get_enables():
        enables = "\n"
        for feat in feats_ids:
            enables += "(" + str(installer.get_feat_desc(feat)) + "," + feat + ") available = "\
                       + str(installer.get_available(feat)) + "/ enable = " + str(installer.get_enable(feat)) + "\n"
        return enables

    # ----------------------------------------------------------------------------
    # Verify and extract args:
    # ----------------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [action]",
        description="PostInstall commmand interface.\n" +
        get_enables(),
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__),
    )

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    # Add arguments from the features of features.ini

    # -----------------------------------------------

    group_p = parser.add_argument_group("personalize action")

    for feature_id in feats_ids:
        x += 1
        a = "group_personalize" + str(x)
        a = group_p.add_mutually_exclusive_group()
        cmd_features.append(feature_id)
        cmd_features.append("no" + feature_id)
        a.add_argument(
            "--" + feature_id,
            action='store_true',
            help="Enable the {desc}"
            .format(desc=installer.get_feat_desc(feature_id)))

        a.add_argument(
            "--no" + feature_id,
            action='store_true',
            help="Disable the {desc}"
            .format(desc=installer.get_feat_desc(feature_id)))

    group_g = parser.add_argument_group("overall action")
    group_ge = group_g.add_mutually_exclusive_group()

    group_ge.add_argument(
        "-a",
        "--all",
        action='store_true',
        help="Install with all the features enabled")

    group_ge.add_argument(
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
        lgs = sppasLogSetup(50)
        lgs.null_handler()

    except:
        print('{:s}\n'.format(sep))
        print('{}   -  Version {}'.format(sg.__name__, sg.__version__))
        print(sg.__copyright__)
        print(sg.__url__ + '\n')
        print('{:s}\n'.format(sep))

        # Redirect all messages to a logging
        # ----------------------------------
        lgs = sppasLogSetup(50)
        lgs.null_handler()

    # ------------------------------
    # Installation is running here :
    # ------------------------------

    arguments = vars(args)
    arguments_true = list()
    for a in arguments:
        if arguments[a] is True:
            arguments_true.append(a)

    if args.quiet and len(arguments_true) == 1:
        parser.print_usage()
        print("{:s}: error: argument --quiet: not allowed alone"
              "".format(os.path.basename(PROGRAM)))
        sys.exit(1)

    if not args.quiet:
        log_level = cfg.log_level
    else:
        log_level = cfg.quiet_log_level
    lgs = sppasLogSetup(log_level)
    lgs.stream_handler()

    if args.all:
        # Because when the verification of the config file
        # is done during the instantiation of the Installer
        # but the modification by the user and the update
        # of the config file is done after the instantiation
        # of the Installer so the modification of the enable
        # with -a etc... will modify the Features object
        # and then the config file.
        if installer.get_cfg_exist() is False:
            for feat_id in feats_ids:
                installer.set_enable(feat_id)
        installer.install()

    elif args.default:
        installer.install()

    # Set the values of enable for each feature
    # -----------------------------------------
    else:
        for a in arguments_true:
            if a in cmd_features:
                if "no" not in a:
                    if installer.get_cfg_exist() is False:
                        installer.set_enable(search_feature(a))
                elif "no" in a:
                    a = a.replace("no", "")
                    if installer.get_cfg_exist() is False:
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
