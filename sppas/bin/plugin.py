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

    bin.plugin.py
    ~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2017  Brigitte Bigi
:summary:      Main script to work with SPPAS plugins.

Examples:

Install a plugin:
>>> ./sppas/bin/plugin.py --install -p sppas/src/plugins/tests/data/soxplugin.zip

Use a plugin on a file:
>>> ./sppas/bin/plugin.py --apply -p soxplugin -i samples/samples-eng/oriana1.wav -o resampled.wav

Remove a plugin:
>>> ./sppas/bin/plugin.py --remove -p soxplugin

An "all-in-one" solution:
>>> ./sppas/bin/plugin.py --install --apply --remove -p sppas/src/plugins/tests/data/soxplugin.zip -i samples/samples-eng/oriana1.wav -o resampled.wav

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas.src.ui import TerminalController
from sppas.src.plugins import sppasPluginsManager


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [actions] [files]",
        description="Plugin command line interface.",
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    # Add arguments for actions
    # -------------------------

    group_act = parser.add_argument_group('Actions')

    group_act.add_argument(
        "--install",
        action='store_true',
        help="Install a new plugin from a plugin package.")

    group_act.add_argument(
        "--remove",
        action='store_true',
        help="Remove an existing plugin.")

    group_act.add_argument(
        "--apply",
        action='store_true',
        help="Apply a plugin on a file.")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-p",
        metavar="string",
        required=True,
        help="Plugin (either an identifier, or an archive file).")

    group_io.add_argument(
        "-i",
        metavar="string",
        required=False,
        help="Input file to apply a plugin on it.")

    group_io.add_argument(
        "-o",
        metavar="string",
        required=False,
        help="Output file, ie the result of the plugin.")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Plugins is here:
    # -----------------------------------------------------------------------
    sep = "-"*72

    try:
        term = TerminalController()
        print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
        print(term.render('${RED} {} - Version {}${NORMAL}'
                          '').format(sg.__name__, sg.__version__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__copyright__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__url__))
        print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
    except:
        print('{:s}\n'.format(sep))
        print('{:s}   -  Version {}'.format(sg.__name__, sg.__version__))
        print(sg.__copyright__)
        print(sg.__url__+'\n')
        print('{:s}\n'.format(sep))

    manager = sppasPluginsManager()
    plugin_id = args.p

    if args.install:

        print("Plugin installation")

        # fix a name for the plugin directory
        plugin_folder = os.path.splitext(os.path.basename(args.p))[0]
        plugin_folder.replace(' ', "_")

        # install the plugin.
        plugin_id = manager.install(args.p, plugin_folder)

    if args.apply:
        if args.i:
            # Get the plugin
            p = manager.get_plugin(plugin_id)

            # Set the output file name (if any)
            if args.o:
                options = p.get_options()
                for opt in options.values():
                    if opt.get_key() == "output":
                        opt.set_value(args.o)
                p.set_options(options)

            # Run
            message = manager.run_plugin(plugin_id, [args.i])
            print(message)

        else:
            print("Error: argument -i is required with argument --apply")
            sys.exit(1)

    if args.remove:
        manager.delete(plugin_id)

    print('{:s}\n'.format(sep))
