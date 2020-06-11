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
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas import sppasLogSetup
from sppas.src.videodata.manager import Manager

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    lgs = sppasLogSetup(0)
    lgs.stream_handler()

    # -----------------------------------------------------------------------
    # Fix initial Manager parameters
    # -----------------------------------------------------------------------

    csv = False
    video = False
    folder = False
    portrait = False
    square = False
    crop = False
    crop_resize = False

    # ----------------------------------------------------------------------------
    # Verify and extract args:
    # ----------------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [action]",
        description="Manager interface.\n",
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__),
    )

    # Add arguments from the features of features.ini

    # -----------------------------------------------

    group_options = parser.add_argument_group("Options")

    group_options.add_argument(
        "-c",
        "--csv",
        action='store_true',
        help="Export images as csv files")

    group_options.add_argument(
        "-v",
        "--video",
        action='store_true',
        help="Export images as videos")

    group_options.add_argument(
        "-f",
        "--folder",
        action='store_true',
        help="Export images in folders")

    group_options.add_argument(
        "-p",
        "--portrait",
        action='store_true',
        help="Fix coordinates for portraits")

    groupe_mode = group_options.add_mutually_exclusive_group()

    groupe_mode.add_argument(
        "-s",
        "--square",
        action='store_true',
        help="Draw squares around faces")

    groupe_mode.add_argument(
        "-cr",
        "--crop",
        action='store_true',
        help="Crop faces")

    groupe_mode.add_argument(
        "-cr_re",
        "--crop_resize",
        action='store_true',
        help="Crop and resize faces")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Fix user communication way
    # -------------------------------

    if args.csv:
        csv = True

    if args.video:
        video = True

    if args.folder:
        folder = True

    if args.portrait:
        portrait = True

    if args.square:
        square = True

    if args.crop:
        crop = True

    if args.crop_resize:
        crop_resize = True

    manager = Manager("../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4", 20, 0,
                      csv, video, folder, portrait, square, crop, crop_resize)
    manager.launch_process()


