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

    src.resources.dumpfile.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import codecs
import pickle
import logging

from .resourcesexc import DumpExtensionError

# ---------------------------------------------------------------------------


class sppasDumpFile(object):
    """Class to manage dump files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    A dump file is a binary version of an ASCII file. Its size is greater
    than the original ASCII one but the time to load it is divided by two
    or three.

    """

    DUMP_FILENAME_EXT = ".dump"

    # -----------------------------------------------------------------------

    def __init__(self, filename, dump_extension=""):
        """Create a sppasDumpFile instance.

        :param filename: (str) Name of the ASCII file.
        :param dump_extension: (str) Extension of the dump file.

        """
        self._dump_ext = sppasDumpFile.DUMP_FILENAME_EXT
        self._filename = filename
        self.set_dump_extension(dump_extension)

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_filename(self, filename):
        """Fix the name of the ASCII file.

        :param filename: (str) Name of the ASCII file.

        """
        self._filename = filename

    # -----------------------------------------------------------------------

    def set_dump_extension(self, extension=""):
        """Fix the extension of the dump file.

        Set to the default extension if the given extension is an empty
        string.

        :param extension: (str) Extension of the dump file \
        (starting with or without the dot).
        :raises: DumpExtensionError if extension of the dump file is \
        the same as the ASCII file.

        """
        if extension.startswith('.') is False:
            extension = "." + extension

        if len(extension) == 1:
            extension = sppasDumpFile.DUMP_FILENAME_EXT

        file_name, file_ext = os.path.splitext(self._filename)
        if extension.lower() == file_ext.lower():
            raise DumpExtensionError(extension)

        self._dump_ext = extension

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_dump_extension(self):
        """Return the extension of the dump version of filename."""
        return self._dump_ext

    # -----------------------------------------------------------------------

    def get_dump_filename(self):
        """Return the file name of the dump version of filename.

        :returns: name of the dump file

        """
        file_name, file_ext = os.path.splitext(self._filename)
        return file_name + self._dump_ext

    # ----------------------------------------------------------------------------

    def has_dump(self):
        """Test if a dump file exists for filename and if it is up-to-date.

        :returns: (bool)

        """
        dump_filename = self.get_dump_filename()
        if os.path.isfile(dump_filename):
            tascii = os.path.getmtime(self._filename)
            tdump = os.path.getmtime(dump_filename)
            if tascii < tdump:
                return True

        return False

    # ----------------------------------------------------------------------------
    # proceedReader/Writer
    # ----------------------------------------------------------------------------

    def load_from_dump(self):
        """Load the file from a dumped file.

        :returns: loaded data or None

        """
        if self.has_dump() is False:
            return None

        dump_filename = self.get_dump_filename()

        try:
            with codecs.open(dump_filename, 'rb') as f:
                data = pickle.load(f)
        except Exception as e:
            logging.info('Save a dumped data failed: {:s}'.format(str(e)))
            os.remove(dump_filename)
            return None

        return data

    # ----------------------------------------------------------------------------

    def save_as_dump(self, data):
        """Save the data as a dumped file.

        :param data: The data to save
        :returns: (bool)

        """
        dump_filename = self.get_dump_filename()

        try:
            with codecs.open(dump_filename, 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logging.info('Save a dumped data failed: {:s}'.format(str(e)))
            return False

        return True
