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

    bin.lpcpreparator.py
    ~~~~~~~~~~~~~~~~

:author:       Florian Hocquet
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      Launch the installation of external features.

Install these features before launching the SPPAS application to enable them.

"""

import os
import sys
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.videodata import Manager

# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [files] [options]",
        description="Preparator for the LPC process",
        epilog="This program is part of "
    )

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    # Add arguments from the creation of the manager
    # -----------------------------------------------

    # Parameters
    # -----------------------------------------------

    group_p = parser.add_argument_group("Parameters")

    group_p.add_argument("-i",
                         required=True,
                         help="Input video filename")

    group_p.add_argument("-s",
                         required=False,
                         type=int,
                         default=100,
                         help="size of the buffer (default: 100)")

    group_p.add_argument("-p",
                         required=False,
                         type=int,
                         default=0,
                         help="overlap of the buffer (default=0)")

    # Configuration
    # -----------------------------------------------

    group_c = parser.add_argument_group("Configuration")

    group_c.add_argument("--track",
                         default=True,
                         type=bool,
                         help="use the tracking process on each person")

    group_c.add_argument("--mark",
                         default=False,
                         type=bool,
                         help="use the landmark process on each person")

    # Options
    # -----------------------------------------------

    group_o = parser.add_argument_group("Options")

    group_o.add_argument("--csv",
                         default=False,
                         type=bool,
                         help="create output csv files")

    group_o.add_argument("--videos",
                         default=False,
                         type=bool,
                         help="create output videos")

    group_o.add_argument("--folders",
                         default=False,
                         type=bool,
                         help="create output folders")

    group_o.add_argument("--framing",
                         default=None,
                         type=str,
                         help="frame the image to portrait")

    group_o.add_argument("--mode",
                         default=None,
                         type=str,
                         help="crop each person")

    group_o.add_argument("--draw",
                         default=None,
                         type=str,
                         help="draw shape on landmark points")

    group_o.add_argument("--nb_person",
                         default=0,
                         type=int,
                         help="frame the image to portrait")

    group_o.add_argument("--pattern",
                         default="-person",
                         type=str,
                         help="crop each person")

    group_o.add_argument("--width",
                         default=640,
                         type=int,
                         help="draw shape on landmark points")

    group_o.add_argument("--height",
                         default=480,
                         type=int,
                         help="draw shape on landmark points")

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Add arguments for input/output files
    # ------------------------------------

    manager = Manager(args.i, args.s, args.p,
                      tracking=args.track, landmark=args.mark,
                      framing=args.framing, mode=args.mode, draw=args.draw,
                      nb_person=args.nb_person,
                      pattern=args.pattern, width=args.width, height=args.height,
                      csv_value=args.csv, v_value=args.videos, f_value=args.folders)

    manager.launch_process()

