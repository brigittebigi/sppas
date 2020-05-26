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

    wkps.fileutils.py
    ~~~~~~~~~~~~~~~~~~

    Utility classes to manage file names.

"""

import unittest
import os
import random
import tempfile
from datetime import date

from sppas.src.utils import sppasUnicode
from sppas import NoDirectoryError

# ----------------------------------------------------------------------------


class sppasFileUtils(object):
    """Utility file manager for SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    >>> sf = sppasFileUtils("path/myfile.txt")
    >>> print(sf.exists())

    >>> sf = sppasFileUtils()
    >>> sf.set_random()
    >>> fn = sf.get_filename() + ".txt"

    """

    def __init__(self, filename=None):
        """Create a sppasFileUtils instance.

        :param filename: (str) Name of the current file

        """
        self._filename = filename

    # ------------------------------------------------------------------------

    def get_filename(self):
        """Return the current filename."""

        return self._filename

    # ------------------------------------------------------------------------

    def set_random(self, root="sppas_tmp", add_today=True, add_pid=True):
        """Set randomly a basename, i.e. a filename without extension.

        :param root: (str) String to start the filename
        :param add_today: (bool) Add today's information to the filename
        :param add_pid: (bool) Add the process PID to the filename
        :returns: a random name of a non-existing file or directory

        """
        # get the system temporary directory
        tempdir = tempfile.gettempdir()
        # initial file name
        name = "/"
        while os.path.exists(name) is True:

            filename = root + "_"

            if add_today:
                today = str(date.today())
                filename = filename + today + "_"
            if add_pid:
                pid = str(os.getpid())
                filename = filename + pid + "_"

            # random float value
            filename = filename + '{:06d}' \
                                  ''.format(int(random.random() * 999999))

            # final file name is path/filename
            name = os.path.join(tempdir, filename)

        self._filename = name
        return name

    # ------------------------------------------------------------------------

    def exists(self, directory=None):
        """Check if the file exists, or exists in a given directory.

        Case-insensitive test on all platforms.

        :param directory: (str) Optional directory to test if a file exists.
        :returns: the filename (including directory) or None

        """
        if directory is None:
            directory = os.path.dirname(self._filename)

        for x in os.listdir(directory):
            if os.path.basename(self._filename.lower()) == x.lower():
                return os.path.join(directory, x)

        return None

    # ------------------------------------------------------------------------

    def clear_whitespace(self):
        """Set filename without whitespace.

        :returns: new filename with spaces replaced by underscores.

        """
        sp = sppasUnicode(self._filename)
        self._filename = sp.clear_whitespace()
        return self._filename

    # ------------------------------------------------------------------------

    def to_ascii(self):
        """Set filename with only US-ASCII characters.

        :returns: new filename with non-ASCII chars replaced by underscores.

        """
        sp = sppasUnicode(self._filename)
        self._filename = sp.to_ascii()
        return self._filename

    # ------------------------------------------------------------------------

    def format(self):
        """Set filename without whitespace and with only US-ASCII characters.

        :returns: new filename with non-ASCII characters and spaces\
        replaced by underscores.

        """
        self.clear_whitespace()
        self.to_ascii()
        return self._filename

# ----------------------------------------------------------------------------


class sppasDirUtils(object):
    """Utility directory manager for SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    >>> sd = sppasDirUtils("my-path")
    >>> print(sd.get_files())

    """

    def __init__(self, dirname):
        """Create a sppasDirUtils instance.

        :param dirname: (str) Name of the current directory

        """
        self._dirname = dirname

    # ------------------------------------------------------------------------

    def get_files(self, extension, recurs=True):
        """Return the list of files of the directory.

        :param extension: (str) extension of files to filter the dir content
        :param recurs: (bool) Find files recursively
        :returns: a list of files
        :raises: IOError

        """
        if self._dirname is None:
            return []

        if os.path.exists(self._dirname) is False:
            raise NoDirectoryError(dirname=self._dirname)

        return sppasDirUtils.dir_entries(self._dirname, extension, recurs)

    # ------------------------------------------------------------------------

    @staticmethod
    def dir_entries(dir_name, extension=None, subdir=True):
        """Return a list of file names found in directory 'dir_name'.

        If 'subdir' is True, recursively access subdirectories under
        'dir_name'. Additional argument, if any, is file extension to
        match filenames.

        """
        if extension is None:
            extension = "*"
        if extension.startswith(".") is False and extension != "*":
            extension = "." + extension

        file_list = []
        for dfile in os.listdir(dir_name):
            dirfile = os.path.join(dir_name, dfile)
            if os.path.isfile(dirfile) is True:
                if extension == "*":
                    file_list.append(dirfile)
                else:
                    fname, fext = os.path.splitext(dirfile)
                    if fext.lower() == extension.lower():
                        file_list.append(dirfile)
            # recursively access file names in subdirectories
            elif os.path.isdir(dirfile) is True and subdir is True:
                file_list.extend(
                    sppasDirUtils.dir_entries(dirfile, extension, subdir))

        return file_list
