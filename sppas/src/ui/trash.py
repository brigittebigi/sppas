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

    ui.trash.py
    ~~~~~~~~~~

"""

import logging
import os
import time
import shutil

from sppas.src.config import paths

# ---------------------------------------------------------------------------


class sppasTrash(object):
    """Utility manager of the Trash of SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create a sppasTrash instance.

        Create the trash directory if not already existing.

        """
        trash_dir = paths.trash
        if os.path.exists(trash_dir) is False:
            os.mkdir(trash_dir)

    # -----------------------------------------------------------------------

    @staticmethod
    def is_empty():
        """Return True if the trash is empty."""
        return len(os.listdir(paths.trash)) == 0

    # -----------------------------------------------------------------------

    @staticmethod
    def do_empty():
        """Empty the trash, i.e. delete all files."""
        for f in os.listdir(paths.trash):
            full_name = os.path.join(paths.trahs, f)
            if os.path.isdir(full_name):
                logging.debug('Delete folder {!s:s}'.format(full_name))
                shutil.rmtree(full_name)
            if os.path.isfile(full_name):
                logging.debug('Delete file {!s:s}'.format(full_name))
                os.remove(full_name)

    # -----------------------------------------------------------------------

    @staticmethod
    def put_file_into(filename):
        """Put a file into the trash.

        :param filename: (str)
        :return: Full name of the file in the trash

        """
        fn, fe = os.path.splitext(os.path.basename(filename))
        now = time.strftime("-%a-%d-%b-%Y_%H%M%S_0000", time.localtime())
        if os.path.exists(filename):
            trashname = os.path.join(paths.trash, fn+now+fe)
            shutil.move(filename, trashname)
        else:
            return ""

        return trashname


    # -----------------------------------------------------------------------

    @staticmethod
    def put_folder_into(folder):
        """Put all files of a folder into the trash."""
        now = time.strftime("-%a-%d-%b-%Y_%H%M%S_0000", time.localtime())
        shutil.move(folder, os.path.join(paths.trash, now))
