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

    ui.wkps.py
    ~~~~~~~~~~

    Management of the workspaces of the software.

"""

import os
import logging
import shutil

import json

from sppas.src.files.filedata import FileData
from sppas.src.files.fileexc import FileOSError
from sppas import paths
from sppas import sppasIndexError
from sppas import sppasUnicode

# ---------------------------------------------------------------------------


class sppasWorkspaces(object):
    """Manage the set of workspaces.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    A workspace is made of:

        - a file in which data are saved and loaded when needed;
        - a name, matching the filename without path nor extension.

    The extension of a workspace JSON files is: wjson

    TODO: Use SPPAS exceptions and/or define new ones. Use PO for messages.

    """

    ext = ".wjson"

    # -----------------------------------------------------------------------

    def __init__(self):
        """Create a sppasWorkspaces instance.

        Load the list of existing wjson file names of the workspaces folder
        of the software.

        """
        wkp_dir = paths.wkps
        if os.path.exists(wkp_dir) is False:
            os.mkdir(wkp_dir)

        self.__wkps = list()
        self.__wkps.append("Blank")

        self.set_workspaces()

    # -----------------------------------------------------------------------

    def set_workspaces(self):
        """Fix the list of existing workspaces in the software.

        Reset the current list of workspaces.

        """
        for fn in os.listdir(paths.wkps):
            fn_observed, ext_observed = os.path.splitext(fn)
            if ext_observed.lower() == sppasWorkspaces.ext:
                # remove path and extension to set the name of the workspace
                wkp_name = os.path.basename(fn_observed)
                # append in the list
                self.__wkps.append(wkp_name)
                logging.debug('Founded workspace {:s}'.format(wkp_name))

    # -----------------------------------------------------------------------

    @staticmethod
    def verify_path_exist(d):
        """ Verify if a path contained in a dictionary exists on the system

        :param d: (dict) dictionary obtained after reading a workspace
        :returns: (bool) false if the path is not on the system
        """
        if 'id' not in d:
            raise KeyError("Workspace 'id' is missing of the dictionary to parse.")
        return os.path.exists(d['id'])
    # ------------------------------------------------------------------------

    @staticmethod
    def modify_path(d, new_path):
        """ Replace the paths contained in the given dictionary by the new_path

        :param d: (dict) dictionary obtained after reading a workspace
        :param new_path: (str)

        """
        if os.path.exists(new_path) is False:
            raise FileOSError(new_path)
        d['id'] = new_path

    # ------------------------------------------------------------------------

    def import_from_file(self, filename):
        """Import and append an external workspace.

        :param filename: (str)
        :returns: The real name used to save the workspace

        """

        if os.path.exists(filename) is False:
            raise IOError('Invalid filename {:s}'.format(filename))

        name, ext = os.path.splitext(os.path.basename(filename))
        if ext.lower() != sppasWorkspaces.ext:
            raise IOError('{:s} is not a valid extension for workspace files'
                          ''.format(ext))

        # Check if a workspace with the same name is not already existing
        sp = sppasUnicode(name)
        u_name = sp.to_strip()
        if u_name in self:
            raise ValueError('A workspace with name {:s} is already existing.'
                             ''.format(u_name))

        # Copy the file -- modify the filename if any
        try:
            dest = os.path.join(paths.wkps, u_name + sppasWorkspaces.ext)
            shutil.copyfile(filename, dest)

            with open(dest, 'r'):
                pass
        except:
            raise
        # append in the list
        self.__wkps.append(u_name)
        return u_name

    # -----------------------------------------------------------------------

    def new(self, name):
        """Create and append a new empty workspace.

        :param name: (str) Name of the workspace to create.
        :returns: The real name used to save the workspace
        :raises: IOError, ValueError

        """
        # set the name in unicode and with the appropriate extension
        su = sppasUnicode(name)
        u_name = su.to_strip()
        if u_name in self:
            raise ValueError('A workspace with name {:s} is already existing.'
                             ''.format(u_name))

        # create the empty workspace data & save
        fn = os.path.join(paths.wkps, u_name) + sppasWorkspaces.ext
        data = FileData()
        data.save(fn)

        self.__wkps.append(u_name)
        return u_name

    # -----------------------------------------------------------------------

    def export_to_file(self, index, filename):
        """Save the an existing workspace into an external file.

        Override filename if the file already exists.

        :param index: (int) Index of the workspace to save data in
        :param filename: (str)
        :raises: IOError

        """
        if index == 0:
            raise IndexError('It is not allowed to export the Blank workspace.')

        u_name = self[index]
        fn = os.path.join(paths.wkps, u_name) + sppasWorkspaces.ext
        if fn == filename:
            raise IOError("'{!s:s}' and '{!s:s}' are the same file"
                          "".format(fn, filename))
        shutil.copyfile(fn, filename)

    # -----------------------------------------------------------------------

    def delete(self, index):
        """Delete the workspace with the given index.

        :param index: (int) Index of the workspace
        :raises: IndexError

        """
        if index == 0:
            raise IndexError('It is not allowed to delete the Blank workspace.')

        try:
            fn = self.check_filename(index)
            os.remove(fn)
        except OSError:
            # The file was not existing. no need to remove!
            pass

        self.__wkps.pop(index)

    # -----------------------------------------------------------------------

    def index(self, name):
        """Return the index of the workspace with the given name."""
        su = sppasUnicode(name)
        u_name = su.to_strip()
        if u_name not in self:
            raise ValueError("Workspace name '{:s}' not found.".format(name))

        i = 0
        while self.__wkps[i] != u_name:
            i += 1

        return i

    # -----------------------------------------------------------------------

    def rename(self, index, new_name):
        """Set a new name to the workspace at the given index.

        :param index: (int) Index of the workspace
        :param new_name: (str) New name of the workspace
        :returns: (str)
        :raises: IndexError, OSError

        """
        if index == 0:
            raise IndexError('It is not allowed to rename the Blank workspace.')

        su = sppasUnicode(new_name)
        u_name = su.to_strip()

        if u_name in self:
            raise ValueError('A workspace with name {:s} is already existing.'
                             ''.format(u_name))

        cur_name = self[index]
        if cur_name == new_name:
            return

        src = self.check_filename(index)
        dest = os.path.join(paths.wkps, u_name) + sppasWorkspaces.ext
        shutil.move(src, dest)
        self.__wkps[index] = u_name

        return u_name

    # -----------------------------------------------------------------------

    def check_filename(self, index):
        """Get the filename of the workspace at the given index.

        :param index: (int) Index of the workspace
        :returns: (str) name of the file
        :raises: IndexError, OSError


        """
        fn = os.path.join(paths.wkps, self[index]) + sppasWorkspaces.ext
        if os.path.exists(fn) is False:
            raise OSError('The file matching the workspace {:s} is not '
                          'existing'.format(fn[:-4]))

        return fn

    # -----------------------------------------------------------------------

    def load_data(self, index):
        """Return the data of the workspace at the given index.

        :param index: (int) Index of the workspace
        :returns: (str) FileData()
        :raises: IndexError

        """
        if index == 0:
            return FileData()

        try:
            filename = self.check_filename(index)
        except OSError:
            return FileData()

        return FileData().load(filename)

    # -----------------------------------------------------------------------

    def save_data(self, data, index=-1):
        """Save data into a workspace.

        The data can already match an existing workspace or a new workspace
        is created. Raises indexerror if is attempted to save the 'Blank'
        workspace.

        :param data: (FileData) Data of a workspace to save
        :param index: (int) Index of the workspace to save data in
        :returns: The real name used to save the workspace
        :raises: IOError, IndexError

        """
        if index == 0:
            raise IndexError("It is not allowed to save the 'Blank' workspace.")

        if index == -1:
            u_name = self.new("New workspace")
        else:
            u_name = self[index]

        filename = os.path.join(paths.wkps, u_name) + sppasWorkspaces.ext
        data.save(filename)
        return u_name

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of workspaces."""
        return len(self.__wkps)

    def __iter__(self):
        for a in self.__wkps:
            yield a

    def __getitem__(self, i):
        try:
            item = self.__wkps[i]
        except IndexError:
            raise sppasIndexError(i)
        return item

    def __contains__(self, name):
        sp = sppasUnicode(name)
        u_name = sp.to_strip()
        for a in self.__wkps:
            if a.lower() == u_name.lower():
                return True
        return False
