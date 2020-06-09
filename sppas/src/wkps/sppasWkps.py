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

    sppasWkps.py
    ~~~~~~~~~~

    Management of the workspaces of the software.

"""

import os
import logging
import shutil

from sppas.src.config import paths
from sppas.src.exceptions import sppasIndexError

from sppas.src.utils.makeunicode import sppasUnicode

from .wkpexc import FileTypeError
from .wkpexc import WkpExtensionError, WkpIdValueError
from .wkpexc import WkpExportBlankError, WkpDeleteBlankError, WkpRenameBlankError, WkpSaveBlankError
from .wkpexc import WkpExportValueError, WkpNameError, WkpFileError

from .workspace import sppasWorkspace
from .wio.wkpreadwrite import sppasWkpRW

# ---------------------------------------------------------------------------


class sppasWkps(object):
    """Manage the set of workspaces.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A workspace is made of:

        - a file in which data are saved and loaded when needed;
        - a name, matching the filename without path nor extension.

    """

    def __init__(self):
        """Create a sppasWkps instance.

        Load the list of existing wjson file names of the workspaces folder
        of the software.

        """
        wkp_dir = paths.wkps
        if os.path.exists(wkp_dir) is False:
            os.mkdir(wkp_dir)

        self.__wkps = list()
        self.__wkps.append("Blank")
        self.ext = "." + sppasWkpRW.default_extension()

        self.set_workspaces()

    # -----------------------------------------------------------------------

    def set_workspaces(self):
        """Fix the list of existing workspaces in the software.

        Reset the current list of workspaces.

        """
        for fn in os.listdir(paths.wkps):
            fn_observed, ext_observed = os.path.splitext(fn)
            if ext_observed.lower() == self.ext:
                # remove path and extension to set the name of the workspace
                wkp_name = os.path.basename(fn_observed)
                # append in the list
                self.__wkps.append(wkp_name)
                logging.info('Workspace added: {:s}'.format(wkp_name))

    # ------------------------------------------------------------------------

    def import_from_file(self, filename):
        """Import and append an external workspace.

        :param filename: (str)
        :returns: The real name used to save the workspace

        """
        if os.path.exists(filename) is False:
            raise FileTypeError(filename)

        name, ext = os.path.splitext(os.path.basename(filename))
        # remove the "." at the beginning of the extension
        ext = ext[1:]
        # check if the workspace is one of the supported file extensions
        if ext.lower() not in sppasWkpRW.extensions():
            raise WkpExtensionError(ext)

        # Check if a workspace with the same name is not already existing
        u_name = self.__raises_existing(name)

        # Copy the file -- modify the filename if any
        try:
            dest = os.path.join(paths.wkps, u_name + self.ext)
            shutil.copyfile(filename, dest)
        except:
            # We should raise a customized exception.
            raise

        # Test if the wkp can be parsed
        try:
            w = sppasWkpRW(filename).read()
        except:
            # remove of the workspaces directory.
            os.remove(dest)
            raise

        # Append in the list
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
        u_name = self.__raises_existing(name)

        # create the empty workspace data & save
        fn = os.path.join(paths.wkps, u_name) + self.ext

        self.__wkps.append(u_name)
        wkp = sppasWorkspace(u_name)
        sppasWkpRW(fn).write(wkp)

        return u_name

    # -----------------------------------------------------------------------

    def export_to_file(self, index, filename):
        """Save an existing workspace into an external file.

        Override filename if the file already exists.

        :param index: (int) Index of the workspace to save data in
        :param filename: (str)
        :raises: IOError

        """
        if index == 0:
            raise WkpExportBlankError

        u_name = self[index]
        fn = os.path.join(paths.wkps, u_name) + self.ext
        if fn == filename:
            raise WkpExportValueError(filename)

        shutil.copyfile(fn, filename)

    # -----------------------------------------------------------------------

    def delete(self, index):
        """Delete the workspace with the given index.

        :param index: (int) Index of the workspace
        :raises: IndexError

        """
        if index == 0:
            raise WkpDeleteBlankError

        try:
            fn = self.check_filename(index)
            os.remove(fn)
        except OSError:
            # The file was not existing. no need to remove!
            pass

        self.__wkps.pop(index)

    # -----------------------------------------------------------------------

    def index(self, name):
        """Return the index of the workspace with the given name.

        :param name: (str)
        :returns: (int)
        :raises: ValueError

        """
        u_name = self.__raises_not_existing(name)
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
            raise WkpRenameBlankError
        u_name = self.__raises_existing(new_name)

        cur_name = self[index]
        if cur_name == new_name:
            return

        src = self.check_filename(index)
        dest = os.path.join(paths.wkps, u_name) + self.ext
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
        fn = os.path.join(paths.wkps, self[index]) + self.ext
        if os.path.exists(fn) is False:
            raise WkpFileError(fn[:-4])

        return fn

    # -----------------------------------------------------------------------

    def load_data(self, index):
        """Return the data of the workspace at the given index.

        :param index: (int) Index of the workspace
        :returns: (str) sppasWorkspace()
        :raises: IndexError

        """
        if index == 0:
            return sppasWorkspace()

        try:
            filename = self.check_filename(index)
        except OSError as e:
            logging.error("Workspace can't be loaded: {}".format(str(e)))
            return sppasWorkspace()

        return sppasWkpRW(filename).read()

    # -----------------------------------------------------------------------

    def save_data(self, data, index=-1):
        """Save data into a workspace.

        The data can already match an existing workspace or a new workspace
        is created. Raises indexerror if is attempted to save the 'Blank'
        workspace.

        :param data: (sppasWorkspace) Data of a workspace to save
        :param index: (int) Index of the workspace to save data in
        :returns: The real name used to save the workspace
        :raises: IOError, IndexError

        """
        if index == 0:
            raise WkpSaveBlankError

        if index == -1:
            u_name = self.new("New workspace")
        else:
            u_name = self[index]

        filename = os.path.join(paths.wkps, u_name) + self.ext
        parser = sppasWkpRW(filename)
        parser.write(data)

        return u_name

    # -----------------------------------------------------------------------
    # Private useful methods
    # -----------------------------------------------------------------------

    def __raises_not_existing(self, name):
        """Raises WkpNameError if name is not already in self."""
        sp = sppasUnicode(name)
        u_name = sp.to_strip()
        contains = False
        for a in self.__wkps:
            if a.lower() == u_name.lower():
                contains = True
                break
        if contains is False:
            raise WkpNameError(u_name)
        return u_name

    # -----------------------------------------------------------------------

    def __raises_existing(self, name):
        """Raises WkpIdValueError if name is already in self."""
        sp = sppasUnicode(name)
        u_name = sp.to_strip()
        contains = False
        for a in self.__wkps:
            if a.lower() == u_name.lower():
                contains = True
                break
        if contains is True:
            raise WkpIdValueError(u_name)
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
