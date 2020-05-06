#!/usr/bin/env python
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

    bin.pluginbuild.py
    ~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2019 Brigitte Bigi
:summary:      Main script to build a plugin for SPPAS.

In SPPAS, a plugin is a ZIP archive of a directory content.
This directory must contain a configuration file with extension ".json".
This directory should contain an icon, a README.txt file and a license
in PDF format.

"""

import json
import logging
import sys
import os
import zipfile
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas import sppasLogSetup
from sppas import sppasAppConfig
from sppas.src.wkps import sppasDirUtils

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # ----------------------------------------------------------------------------
    # Verify and extract args:
    # ----------------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [actions] [options]",
        description="Build a plugin archive.",
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    parser.add_argument(
        "-i",
        metavar="string",
        help="Directory of the plugin.")

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # ----------------------------------------------------------------------------
    # Check the given directory
    # ----------------------------------------------------------------------------

    if not os.path.isdir(args.i):
        raise OSError("-i argument must point to a directory. "
                      "'{:s}' does not.".format(args.i))

    sd = sppasDirUtils(args.i)

    # Redirect all messages to logging
    # --------------------------------

    with sppasAppConfig() as cg:
        if not args.quiet:
            log_level = cg.log_level
        else:
            log_level = cg.quiet_log_level
        lgs = sppasLogSetup(log_level)
        lgs.stream_handler()

    # Check if there's a README.txt file at the root directory
    # --------------------------------------------------------

    txt_list = sd.get_files(".txt", recurs=False)
    found = False
    for filename in txt_list:
        if "readme" in filename.lower():
            found = True
    if found is False:
        logging.warning("Plugin should contain a README.txt file.")

    # Check if there's an icon file at the root directory
    # ---------------------------------------------------

    png_list = sd.get_files(".png", recurs=False)
    if len(png_list) == 0:
        logging.warning("Plugin should contain a PNG image to be used "
                        "as an icon.")

    # Check if there's a license file at the root directory
    # -----------------------------------------------------

    pdf_list = sd.get_files(".pdf", recurs=False)
    if len(pdf_list) == 0:
        logging.warning("Plugin should contain a license in PDF format.")

    # Check if there's a .ini file at the root directory
    # --------------------------------------------------

    json_list = sd.get_files(".json", recurs=False)
    if len(json_list) != 1:
        logging.critical("A configuration file - and only one, is needed in "
                         "the directory of the plugin.")
        sys.exit(1)

    # ----------------------------------------------------------------------------
    # Check if the .json file can be parsed properly and get identifier
    # ----------------------------------------------------------------------------
    # Read the whole file content
    with open(json_list[0]) as cfg:
        config = json.load(cfg)

    identifier = config['id']
    logging.info("Plugin identifier: {:s}".format(identifier))
    if "version" in config:
        version = config['version']
    else:
        version = "1.0"

    if "icon" not in config:
        logging.warning("Plugin icon is missing.")

    if "name" not in config:
        logging.warning("Plugin name is missing of the configuration file.")

    if "descr" not in config:
        logging.warning("Plugin description is missing of the configuration file.")

    # ----------------------------------------------------------------------------
    # Create the plugin zip file
    # ----------------------------------------------------------------------------

    dest_name = identifier + "-" + version + ".zip"
    plugin_archive = os.path.join(os.path.dirname(args.i), dest_name)
    logging.info("Create the plugin archive: {:s}".format(plugin_archive))

    logging.info("Files appended to the zip:")
    out_file = zipfile.ZipFile(plugin_archive, "w",
                               compression=zipfile.ZIP_DEFLATED)
    for f in sd.dir_entries(args.i, extension="*", subdir=True):
        f_dest = f.replace(args.i, "")
        logging.info("   - {:s}".format(f_dest))
        out_file.write(f, f_dest)

    logging.info("done!")
    out_file.close()
