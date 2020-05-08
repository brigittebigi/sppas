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

    bin.preinstall.py
    ~~~~~~~~~~~~~~~~

:author:       Florian Hocquet
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      Launch the installation of external features.

Install these features before launching the SPPAS application to enable them.

"""

import sys
import os
import time
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg, paths
from sppas import sppasLogSetup
from sppas import sppasAppConfig
from sppas import sppasLogFile
from sppas.src.preinstall import sppasInstallerDeps

from sppas.src.ui.term import ProcessProgressTerminal
from sppas.src.ui.term import TerminalController

# ---------------------------------------------------------------------------

EXIT_DELAY = 2
EXIT_STATUS = 1   # Status for an exit with errors.


def exit_error(msg="Unknown."):
    """Exit the program with status 1 and an error message.

    :param msg: (str) Message to print on stdout.

    """
    print("[ ERROR ] {:s}".format(msg))
    time.sleep(EXIT_DELAY)
    sys.exit(EXIT_STATUS)


def check_python():
    """Check if the current python in use is the right one: 3.6+.

    Exit if it's not the case.

    """
    if sys.version_info < (3, 6):
        exit_error("The version of Python is too old: "
                   "This program requires at least version 3.6.")

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    cfg = sppasAppConfig()
    lgs = sppasLogSetup(cfg.log_level)
    log_report = sppasLogFile(pattern="install")
    lgs.file_handler(log_report.get_filename())

    # -----------------------------------------------------------------------
    # Test version of Python
    # -----------------------------------------------------------------------
    check_python()

    # -----------------------------------------------------------------------
    # Fix initial sppasInstallerDeps parameters
    # -----------------------------------------------------------------------

    installer = sppasInstallerDeps()
    cmd_features = list()
    i = 0
    x = 0

    def search_feature(feature_identifier):
        for fid in installer.features_ids():
            if feature_identifier == fid:
                return fid

    def get_enables():
        enables = "\n"
        for fid in installer.features_ids():
            enables += \
                "(" + str(installer.description(fid)) + ", " + fid + ")"\
                "available = " + str(installer.available(fid)) + "/ "\
                "enable = " + str(installer.enable(fid)) + "\n"

        return enables

    # ----------------------------------------------------------------------------
    # Verify and extract args:
    # ----------------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [action]",
        description="PreInstall command interface.\n" +
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

    for fid in installer.features_ids():
        x += 1
        # a = "group_personalize" + str(x)
        a = group_p.add_mutually_exclusive_group()
        cmd_features.append(fid)
        cmd_features.append("no" + fid)
        a.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable feature '{name}': '{desc}'".format(
                name=fid,
                desc=installer.description(fid)))

        a.add_argument(
            "--no" + fid,
            action='store_true',
            help="Disable feature '{name}': '{desc}'".format(
                name=fid,
                desc=installer.description(fid)))

    group_g = parser.add_argument_group("overall action")
    group_ge = group_g.add_mutually_exclusive_group()

    group_ge.add_argument(
        "-a",
        "--all",
        action='store_true',
        help="Install all the available features for this os.")

    group_ge.add_argument(
        "-d",
        "--default",
        action='store_true',
        help="Install all the features that are enabled by default.")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    arguments = vars(args)
    arguments_true = list()
    for a in arguments:
        if arguments[a] is True:
            arguments_true.append(a)

    if args.quiet and len(arguments_true) == 1:
        parser.print_usage()
        exit_error("{:s}: error: argument --quiet: not allowed alone."
                   "".format(os.path.basename(PROGRAM)))

    if not args.quiet:
        p = ProcessProgressTerminal()
        installer.set_progress(p)

    # Fix user communication way
    # -------------------------------

    sep = "-" * 72
    if not args.quiet:
        try:
            term = TerminalController()
            print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
            print(term.render('${RED} {} - Version {}${NORMAL}'
                              '').format(sg.__name__, sg.__version__))
            print(term.render('${BLUE} {} ${NORMAL}').format(sg.__copyright__))
            print(term.render('${BLUE} {} ${NORMAL}').format(sg.__url__))
            print(term.render('${GREEN}{:s}${NORMAL}\n').format(sep))

        except:
            print('{:s}\n'.format(sep))
            print('{}   -  Version {}'.format(sg.__name__, sg.__version__))
            print(sg.__copyright__)
            print(sg.__url__ + '\n')
            print('{:s}\n'.format(sep))

    # enable all available features
    if args.all:
        for fid in installer.features_ids():
            installer.enable(fid, True)

    # Set the values of enable individually for each feature
    for a in arguments_true:
        if a in cmd_features:
            if a.startswith("no") is False:
                fid = search_feature(a)
                if installer.available(fid) is True:
                    installer.enable(fid, True)
            else:
                a = a.replace("no", "")
                fid = search_feature(a)
                if installer.available(fid) is True:
                    installer.enable(fid, False)

    # process the installation
    errors = installer.install()

    msg = "See full installation report in file: {}".format(log_report.get_filename())

    if not args.quiet:
        p.close()
        try:
            term = TerminalController()
            print(term.render('\n${GREEN}{:s}${NORMAL}').format(sep))
            print(term.render('${RED}See {}.').format("..."))
            print(term.render('${GREEN}Thank you for using {}.').format(sg.__name__))
            print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
        except:
            print('\n{:s}\n'.format(sep))
            print(msg)
            print('{:s}\n'.format(sep))

    if len(errors) > 0:
        msg += "\nThe installation process terminated with errors:"
        msg += "\n".join(errors)
        exit_error(msg)

sys.exit(0)