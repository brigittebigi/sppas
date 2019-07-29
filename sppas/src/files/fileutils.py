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

    files.fileutils.py
    ~~~~~~~~~~~~~~~~~~

    Utility classes to manage file names.

"""

import unittest
import uuid
import os
import random
import tempfile
from datetime import date

from sppas.src.config import paths
from sppas.src.utils import sppasUnicode
from sppas import NoDirectoryError


# ----------------------------------------------------------------------------


class sppasGUID(object):
    """Utility tool to generate an id.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This class is a manager for GUID - globally unique identifier.

    GUIDs are usually stored as 128-bit values, and are commonly
    displayed as 32 hexadecimal digits with groups separated by hyphens,
    such as {21EC2020-3AEA-4069-A2DD-08002B30309D}.

    """
    def __init__(self):
        self.__guid = uuid.uuid4()

    # ---------------------------------------------------------------------------

    def get(self):
        return str(self.__guid)

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

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFileUtils(unittest.TestCase):

    def setUp(self):
        self.sample_1 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")
        self.sample_2 = os.path.join(paths.samples, "samples-fra", "AG_éàç_0460.TextGrid")

    def test_set_random(self):
        sf = sppasFileUtils()
        f = os.path.basename(sf.set_random())
        self.assertTrue(f.startswith("sppas_tmp_"))
        f = os.path.basename(sf.set_random(add_today=False, add_pid=False))
        self.assertEqual(16, len(f))
        f = os.path.basename(sf.set_random(root="toto", add_today=False, add_pid=False))
        self.assertTrue(f.startswith("toto_"))
        self.assertEqual(11, len(f))

    def test_exists(self):
        sf = sppasFileUtils(self.sample_1)
        self.assertEqual(sf.exists(), self.sample_1)

    def test_format(self):
        sf = sppasFileUtils(" filename with some   whitespace ")
        f = sf.clear_whitespace()
        self.assertEqual("filename_with_some_whitespace", f)
        sf = sppasFileUtils(self.sample_2)
        f = sf.to_ascii()
        self.assertTrue(f.endswith("AG_____0460.TextGrid"))

# ---------------------------------------------------------------------------


class TestDirUtils(unittest.TestCase):

    def test_dir(self):
        # normal situation
        sd = sppasDirUtils(os.path.join(paths.samples, "samples-yue"))
        fl = sd.get_files("wav")
        self.assertEqual(len(fl), 1)

        # directory does not exists
        sd = sppasDirUtils("bad-directory-name")
        with self.assertRaises(IOError):
            sd.get_files("wav")

        # no directory
        sd = sppasDirUtils(None)
        self.assertEqual(sd.get_files("wav"), [])
