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

    src.wkps.filestructure.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import mimetypes
import logging
import os
import glob
from datetime import datetime

from sppas.src.exceptions.exc import sppasTypeError
from sppas.src.exceptions.exc import sppasValueError

from .fileref import sppasCatReference
from .wkpexc import FileRootValueError, FileOSError, PathTypeError, FilesMatchingValueError
from .filebase import FileBase, States

# ---------------------------------------------------------------------------


class FileName(FileBase):
    """Represent the data linked to a filename.

    Use instances of this class to hold data related to a filename.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    FILENAME_STATES = (States().UNUSED, States().CHECKED, States().LOCKED, States().MISSING)

    def __init__(self, identifier):
        """Constructor of a FileName.

        From the identifier, the following properties are extracted:

            1. name (str) The base name of the file, without path nor ext
            2. extension (str) The extension of the file, or the mime type
            3. date (str) Time of the last modification
            4. size (str) Size of the file
            5. state (int) State of the file

        :param identifier: (str) Full name of a file

        """
        super(FileName, self).__init__(identifier)

        # The name (no path, no extension)
        fn, ext = os.path.splitext(self.get_id())
        self.__name = os.path.basename(fn)

        # The extension is forced to be in upper case
        self.__extension = ext.upper()

        # Modified date/time and file size
        self.__date = None
        self.__filesize = 0
        self.update_properties()

        # a free to use member to expend the class
        self.subjoined = None

    # -----------------------------------------------------------------------

    def folder(self):
        """Return the name of the directory of this file (str)."""
        return os.path.dirname(self.id)

    # -----------------------------------------------------------------------

    def get_name(self):
        """Return the short name of the file (str).

        The name is the filename without path nor extension.

        """
        return self.__name

    # -----------------------------------------------------------------------

    def get_extension(self):
        """Return the extension of the file in upper-cases (str)."""
        return self.__extension

    # -----------------------------------------------------------------------

    def get_mime(self):
        """Return the mime type of the file (str)."""
        m = mimetypes.guess_type(self.id)
        if m[0] is not None:
            return m[0]

        return "unknown"

    # -----------------------------------------------------------------------

    def get_date(self):
        """Return a string representing the date of the last modification."""
        if self.__date is None:
            return " -- "
        return "{:d}-{:d}-{:d} {:d}:{:d}:{:d}".format(
            self.__date.year, self.__date.month, self.__date.day,
            self.__date.hour, self.__date.minute, self.__date.second)

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return a string representing the size of the file."""
        unit = " Ko"
        file_size = self.__filesize / 1024
        if file_size > (1024 * 1024):
            file_size /= 1024
            unit = " Mo"

        return str(int(file_size)) + unit

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Override. Set a state value to this filename.

        A LOCKED file can only be unlocked by assigning the CHECKED state.
        No other state than MISSING can be assigned if the file does not exists.

        :param value: (States)
        :returns: (bool) this filename state has changed or not

        """
        # The file is not existing
        if self.__file_exists() is False:
            return self.update_properties()

        # The file is existing:

        # Check given value
        if value not in FileName.FILENAME_STATES:
            raise sppasTypeError(value, str(FileName.FILENAME_STATES))
        # Attempt to set to MISSING but file is existing
        if value == States().MISSING:
            return False

        # Attempt to set to another state than checked but file is locked
        if self._state == States().LOCKED and value != States().CHECKED:
            return False

        # Attempt to set to the same state
        if self._state == value:
            return False

        # The file was previously missing and it exists now...
        if self._state == States().MISSING:
            self.update_properties()

        # Set the requested state.
        self._state = value
        return True

    # -----------------------------------------------------------------------

    def update_properties(self):
        """Update properties of the file (modified date and file size).

        :returns: (bool) true if properties were changed

        """
        cur_state = self._state
        cur_date = self.__date
        cur_size = self.__filesize

        # test if the file is still existing
        if self.__file_exists() is False:
            self.__date = None
            self.__filesize = 0
            self._state = States().MISSING

        else:
            # get time and size
            try:
                self.__date = datetime.fromtimestamp(os.path.getmtime(self.get_id()))
            except ValueError:
                self.__date = None
            self.__filesize = os.path.getsize(self.get_id())
            if self._state == States().MISSING:
                # the file is not missing anymore
                self._state = States().UNUSED

        return cur_state != self._state or cur_date != self.__date or cur_size != self.__filesize

    # -----------------------------------------------------------------------

    def __file_exists(self):
        return os.path.isfile(self.get_id())

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    name = property(get_name, None)
    extension = property(get_extension, None)
    size = property(get_size, None)
    date = property(get_date, None)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__name,
                     self.__date,
                     self.__extension,
                     self.__filesize,
                     self.get_state(),
                     self.id))

# ---------------------------------------------------------------------------


class FileRoot(FileBase):
    """Represent the data linked to the basename of a file.

    We'll use instances of this class to hold data related to the root
    base name of a file. The root of a file is its name without the pattern.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, name):
        """Constructor of a FileRoot.

        :param name: (str) Filename or root name

        """
        if os.path.exists(name):
            root_name = FileRoot.root(name)
        else:
            root_name = name
        super(FileRoot, self).__init__(root_name)

        # A list of FileName instances, i.e. files sharing this root.
        self.__files = list()

        # References
        self.__references = None

        # A free to use member to expand the class
        self.subjoined = None

    # -----------------------------------------------------------------------

    @staticmethod
    def pattern(filename):
        """Return the pattern of the given filename.

        A pattern is the end of the filename, after the '-'.
        It can't contain '_' and must be between 3 and 12 characters
        (not including the '-').

        Notice that the '_' can't be supported (too many side effects).

        :param filename: (str) Name of a file (absolute or relative)
        :returns: (str) Root pattern or an empty string if no pattern is detected

        """
        fn = os.path.basename(filename)
        base = os.path.splitext(fn)[0]

        pos = 0
        if '-' in base:
            pos = base.rindex('-')

            # check if pattern is ok.
            p = base[pos:]
            if '_' in p or len(p) < 4 or len(p) > 13:
                pos = 0

        if pos > 0:
            return base[pos:]
        return ""

    # -----------------------------------------------------------------------

    @staticmethod
    def root(filename):
        """Return the root of the given filename.

        :param filename: (str) Name of a file (absolute or relative)
        :returns: (str) Root

        """
        p = FileRoot.pattern(filename)
        base_file, ext_file = os.path.splitext(filename)
        return filename[:(len(filename)-len(p)-len(ext_file))]

    # -----------------------------------------------------------------------

    def set_object_state(self, value, filename):
        """Set a state value to a filename of this fileroot.

        :param value: (int) A state of FileName.
        :param filename: (FileName) The instance to change state
        :return: (list) Modified instances
        :raises: sppasTypeError

        """
        for fn in self.__files:
            if fn == filename:
                m = fn.set_state(value)
                if m is True:
                    changed = list()
                    changed.append(fn)
                    m = self.update_state()
                    if m is True:
                        changed.append(self)
                    return changed

        return list()

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Set a value to represent the state of this root.

        It is not allowed to manually assign one of the "AT_LEAST" states
        (they are automatically fixed by setting the state of a FileName
        with set_object_state method).

        The state of LOCKED files can't be changed with this method.
        Use set_object_state() instead.

        :param value: (State) A state of FileName.
        :return: (list) Modified instances

        """
        if value not in FileName.FILENAME_STATES:
            raise sppasTypeError(value, str(FileName.FILENAME_STATES))

        modified = list()
        for fn in self.__files:
            if fn.get_state() != States().LOCKED:
                m = fn.set_state(value)
                if m is True:
                    modified.append(fn)

        if len(modified) > 0:
            m = self.update_state()
            if m is True:
                modified.append(self)

        return modified

    # -----------------------------------------------------------------------

    def update_state(self):
        """Update the state depending on the checked and locked filenames.

        The state of a root is assigned as it:
            - locked if all files are locked,
            - at_least_one_locked if at least one of its filenames is locked,
            - checked if all filenames are checked,
            - at_least_one_checked if at least one of its filenames is checked and none of the others are locked,
            - missing if at least one of its filenames is missing and none of the others are locked nor checked,
            - missing if all its filenames are missing,
            - unused if none of its filenames are neither locked nor checked.

        :return: (bool) State is changed or not

        """
        missing = 0
        if len(self.__files) == 0:
            new_state = States().UNUSED
        else:
            checked = 0
            locked = 0
            for fn in self.__files:
                # fn.update_properties()
                if fn.get_state() == States().CHECKED:
                    checked += 1
                elif fn.get_state() == States().LOCKED:
                    locked += 1
                elif fn.get_state() == States().MISSING:
                    missing += 1

            if locked == len(self.__files):
                new_state = States().LOCKED
            elif locked > 0:
                new_state = States().AT_LEAST_ONE_LOCKED
            elif checked == len(self.__files):
                new_state = States().CHECKED
            elif checked > 0:
                new_state = States().AT_LEAST_ONE_CHECKED
            elif missing == len(self.__files):
                new_state = States().MISSING
            else:
                new_state = States().UNUSED

        if self._state != new_state:
            self._state = new_state
            return True

        return False

    # -----------------------------------------------------------------------

    def get_references(self):
        """Return the list of references of the catalog.

        :returns: (list)

        """
        if self.__references is None:
            return list()
        return self.__references

    # -----------------------------------------------------------------------

    def has_ref(self, ref):
        """Return True if the root contains the given reference.

        :param ref: (sppasReference)
        :returns: (bool)

        """
        if isinstance(ref, sppasCatReference) is False:
            raise sppasTypeError(ref, 'sppasCatReference')

        if len(self.get_references()) == 0:
            return False

        for r in self.get_references():
            if r.id == ref.id:
                return True

        return False

    # -----------------------------------------------------------------------

    def add_ref(self, ref):
        """Associate a new reference to the root.

        :param ref: (sppasReference)
        :return: (bool)

        """
        has = self.has_ref(ref)
        if has is True:
            return False

        if self.__references is None:
            self.__references = list()

        self.__references.append(ref)
        return True

    # -----------------------------------------------------------------------

    def remove_ref(self, ref):
        """Remove a reference to unlink it to this root.

        :param ref: (sppasReference)
        :return: (bool)

        """
        for r in self.get_references():
            if r.id == ref.id:
                self.__references.remove(r)
                return True
        return False

    # -----------------------------------------------------------------------

    def set_references(self, list_of_references):
        """Fix the list of references.

        The current list is overridden.

        :param list_of_references: (list)
        :raises: sppasTypeError

        """
        self.__references = list()
        if isinstance(list_of_references, list):
            if len(list_of_references) > 0:
                for reference in list_of_references:
                    if isinstance(reference, sppasCatReference) is False:
                        raise sppasTypeError(reference, 'sppasCatReference')

            self.__references = list_of_references
        else:
            raise sppasTypeError(list_of_references, 'list')

    references = property(get_references, set_references)

    # -----------------------------------------------------------------------

    def get_object(self, filename):
        """Return the instance matching the given filename.

        Return self if filename is matching the id.

        :param filename: Full name of a file
        :returns: (FileName of None)

        """
        fr = FileRoot.root(filename)

        # Does this filename matches this root
        if fr != self.id:
            # TODO: Solve the error with python 2.7: UnicodeWarning:
            # Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
            return None

        # Does it match only the root (no file name)
        if fr == filename:
            return self

        # Check if this file is in the list of known files
        fn = FileName(filename)
        for frn in self.__files:
            if frn.id == fn.id:
                return frn

        return None

    # -----------------------------------------------------------------------

    def append(self, filename, all_root=False, ctime=0.):
        """Append a filename in the list of files.

        'filename' must be the absolute name of a file or an instance
        of FileName.

        :param filename: (str, FileName) Absolute name of a file
        :param all_root: (bool) Add all files sharing the same root
        :param ctime: (float) Add files only if created/modified after time in seconds since the epoch
        :returns: (list of FileName) the appended FileName() instances or None

        """
        if filename is None:
            self.update_state()
            return list()

        fns = list()
        # Get or create the FileName instance
        fn = filename
        if isinstance(filename, FileName) is False:
            fn = FileName(filename)

        # file is not missing
        if fn.get_state() != States().MISSING:
            # Check if root is ok
            if self.id != FileRoot.root(fn.id):
                raise FileRootValueError(fn.id, self.id)

            # This file is not already in the list.
            if all_root is False and fn not in self:
                if os.path.getmtime(fn.get_id()) > ctime:
                    self.__files.append(fn)
                    fns.append(fn)

            if all_root is True:
                # add all files sharing this root on the disk,
                # except if a ctime value is given and file is too old.
                for new_filename in sorted(glob.glob(self.id+"*")):
                    if os.path.isfile(new_filename) is True:
                        fnx = FileName(new_filename)
                        if fnx.get_id() not in self:
                            if os.path.getmtime(fnx.get_id()) > ctime:
                                self.__files.append(fnx)
                                fns.append(fnx)

        # file does not exist. Add it with its 'MISSING' state.
        else:
            self.__files.append(fn)
            fns.append(fn)

        self.update_state()
        return fns

    # -----------------------------------------------------------------------

    def remove(self, filename):
        """Remove a filename of the list of files.

        Given filename must be the absolute name of a file or an instance
        of FileName.

        :param filename: (str, FileName) Absolute name of a file
        :returns: (identifier) Identifier of the removed FileName or None if nothing removed.

        """
        idx = -1
        if isinstance(filename, FileName):
            try:
                idx = self.__files.index(filename)
            except ValueError:
                idx = -1
        else:
            # Search for this filename in the list
            for i, fn in enumerate(self.__files):
                if fn.id == filename:
                    idx = i
                    break

        identifier = None
        if idx != -1:
            identifier = self.__files[idx].get_id()
            self.__files.pop(idx)
            upd = self.update_state()
            if upd is True:
                logging.debug("FileRoot {:s} state changed to {:d}"
                              "".format(self.get_id(), self.get_state()))

        return identifier

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return 'Root: ' + self.id + \
               ' contains ' + str(len(self.__files)) + ' files\n'

    def __iter__(self):
        for a in self.__files:
            yield a

    def __getitem__(self, i):
        return self.__files[i]

    def __len__(self):
        return len(self.__files)

    def __contains__(self, value):
        # The given value is a FileName instance
        if isinstance(value, FileName):
            return value in self.__files

        # The given value is a filename
        for fn in self.__files:
            if fn.id == value:
                return True

        # nothing is matching this value
        return False

# ---------------------------------------------------------------------------


class FilePath(FileBase):
    """Represent the data linked to a folder name.

    We'll use instances of this class to hold data related to the path of
    a filename. Items in the tree will get associated back to the
    corresponding FileName and this FilePath object.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, filepath):
        """Constructor of a FilePath.

        :param filepath: (str) Absolute or relative name of a folder
        :raises: PathTypeError

        """
        super(FilePath, self).__init__(os.path.abspath(filepath))

        if os.path.exists(filepath) is False:
            self._state = States().MISSING
        else:
            # path is existing. Is it a directory?
            if os.path.isdir(filepath) is False:
                raise PathTypeError(filepath)

        # A list of FileRoot instances
        self.__roots = list()

        # a free to use entry to expand the class
        self.subjoined = None

    # -----------------------------------------------------------------------

    def set_object_state(self, value, entry):
        """Set a state value to a filename of this filepath.

        It is not allowed to manually assign one of the "AT_LEAST" states.
        They are automatically fixed here depending on the roots states.

        :param value: (int) A state.
        :param entry: (FileName, FileRoot) The instance to change state
        :raises: sppasTypeError, sppasOSError, sppasValueError

        """
        modified = list()
        # In case (not normal) filename is a string, create a FileName
        if isinstance(entry, (FileName, FileRoot)) is False:
            entry = FileName(entry)

        if isinstance(entry, FileName):
            # Search for the FileRoot matching the given FileName
            root_id = FileRoot.root(entry.id)
            fr = self.get_root(root_id)
            if fr is None:
                raise sppasValueError(root_id, self.id)
            # Ask the FileRoot to set the state of the FileName
            modified = fr.set_object_state(value, entry)

        elif isinstance(entry, FileRoot):
            modified = entry.set_state(value)

        if len(modified) > 0:
            m = self.update_state()
            if m is True:
                modified.append(self)

        return modified

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Set a value to represent the state of the path.

        It is not allowed to manually assign one of the "AT_LEAST" states
        (they are automatically fixed by setting the state of a FileName
        with set_object_state method).

        The state of LOCKED files is not changed.

        :param value: (State) A state of FileName.

        """
        if value not in FileName.FILENAME_STATES:
            raise sppasTypeError(value, str(FileName.FILENAME_STATES))

        modified = list()

        for fr in self.__roots:
            m = fr.set_state(value)
            modified.extend(m)

        if len(modified) > 0:
            m = self.update_state()
            if m is True:
                modified.append(self)

        return modified

    # -----------------------------------------------------------------------

    def get_object(self, filename):
        """Return the instance matching the given entry.

        :param filename: Name of a file or a root (absolute of relative)

        Notice that it returns 'self' if filename is a directory matching
        self.id.

        """
        abs_name = os.path.abspath(filename)
        # if os.path.isdir(abs_name) and abs_name == self.id:
        if abs_name == self.id:
            return self

        for fr in self.__roots:
            if fr.id == abs_name:
                return fr
            fn = fr.get_object(filename)
            if fn is not None:
                return fn

        return None

    # -----------------------------------------------------------------------

    def identifier(self, filename):
        """Return the identifier, i.e. the full name of an existing file.

        :param filename: (str) Absolute or relative name of a file
        :returns: (str) Identifier for this filename
        :raise: FileOSError if filename does not match a regular file

        """
        f = os.path.abspath(filename)
        if os.path.isfile(f) is False:
            f = os.path.join(self.id, filename)
        if os.path.isfile(f) is False:
            raise FileOSError(filename)

        return f

    # -----------------------------------------------------------------------

    def get_root(self, name):
        """Return the FileRoot matching the given id (root or file).

        :param name: (str) Identifier name of a root or a file.
        :returns: FileRoot or None

        """
        for fr in self.__roots:
            # TODO: Solve the error with python 2.7: UnicodeWarning:
            # Unicode equal comparison failed to convert both arguments
            # to Unicode - interpreting them as being unequal
            if fr.id == name:
                return fr

        for fr in self.__roots:
            for fn in fr:
                # TODO: Solve the error with python 2.7: UnicodeWarning:
                # Unicode equal comparison failed to convert both arguments
                # to Unicode - interpreting them as being unequal
                if fn.id == name:
                    return fr

        return None

    # -----------------------------------------------------------------------

    def append(self, entry, all_root=False, ctime=0.):
        """Append a filename in the list of files.

        Given filename can be either an absolute or relative name of a file
        or an instance of FileName. It can also be an instance of FileRoot.

        Only an existing file can be added if the given entry is the name of the file.
        But any FileName() instance can be added, even if the file does not exists
        (of course, its path must match with this fp).

        :param entry: (str, FileName, FileRoot) Absolute or relative name of a file
        :param all_root: (bool) Add also all files sharing the same root as the given one, or all files of the given root
        :param ctime: (float) Add files only if created/modified after time in seconds since the epoch
        :returns: (FileName, FileRoot) the list of appended objects or None
        :raises: FileOSError if entry is a non-existing filename. Exception if given entry does not math the path.

        """
        # list of new objects added to the data
        new_objs = list()
        new_files = list()

        # Given entry is a FileRoot instance
        if isinstance(entry, FileRoot):

            # test if root is matching this path
            abs_name = os.path.dirname(entry.id)
            if abs_name != self.id:
                logging.debug("The root {:s} can't be appended: it is not "
                              "matching the FilePath {:s}".format(entry.id, self.id))
                raise FilesMatchingValueError(entry.id, self.id)

            # test if this root is already inside this path
            obj = self.get_root(entry.id)
            if obj is None:
                self.__roots.append(entry)
                new_objs.append(entry)

            # add all files of this root (if asked)
            if all_root is True:
                new_files = entry.append(None, all_root=all_root, ctime=ctime)

        # Given entry is a filename or a FileName instance
        else:
            if isinstance(entry, FileName):
                file_id = entry.id
            else:
                file_id = self.identifier(entry)
                entry = FileName(file_id)

            # test if root is matching this path
            abs_name = os.path.dirname(file_id)
            if abs_name != self.id:
                logging.debug("The file {:s} can't be appended: its path is "
                              "not matching the FilePath {:s}".format(file_id, self.id))
                raise FilesMatchingValueError(file_id, self.id)

            # Get or create the corresponding FileRoot
            root_id = FileRoot.root(file_id)
            fr = self.get_root(root_id)
            if fr is None:
                fr = FileRoot(root_id)
                self.__roots.append(fr)
                new_objs.append(fr)

            new_files = fr.append(entry, all_root=all_root, ctime=ctime)

        if len(new_files) > 0:
            new_objs.extend(new_files)
        if len(new_objs) > 0:
            self.update_state()
            return new_objs

        return None

    # -----------------------------------------------------------------------

    def remove(self, entry):
        """Remove a root entry of the list of roots.

        Given entry can be either the identifier of a root or an instance
        of FileRoot.

        TODO: REMOVE IF ENTRY is FILENAME

        :param entry:
        :returns: (identifier) Identifier of the removed entry or None

        """
        if isinstance(entry, FileRoot):
            root = entry
        else:
            root = self.get_root(entry)

        try:
            idx = self.__roots.index(root)
            identifier = self.__roots[idx].get_id()
            self.__roots.pop(idx)
        except ValueError:
            identifier = None

        self.update_state()
        return identifier

    # -----------------------------------------------------------------------

    def unlock(self):
        """Unlock all.

        :returns: number of unlocked filenames

        """
        i = 0
        for fr in self.__roots:
            for fn in fr:
                if fn.get_state() == States().LOCKED:
                    fn.set_state(States().CHECKED)
                    i += 1
            if i > 0:
                fr.update_state()
        if i > 0:
            self.update_state()

        return i

    # -----------------------------------------------------------------------

    def update_state(self):
        """Modify state depending on the checked root names.

        The state is missing if the path is not existing on disk.
        Else, the state of a path is assigned as it:
            - locked if all roots are locked,
            - at_least_one_locked if at least one of its roots is locked,
            - checked if all roots are checked,
            - at_least_one_checked if at least one of its roots is checked and none of the others are locked,
            - unused if none of its roots are neither locked, checked nor missing.

        :return: (bool) State was changed or not.

        """
        state = States()
        if os.path.exists(self.get_id()) is False:
            # Path was missing and is still missing
            if self._state == state.MISSING:
                return False
            else:
                # Path was ok and is missing now (was deleted by user during our use)
                self._state = state.MISSING
                return True

        if len(self.__roots) == 0:
            new_state = state.UNUSED
        else:
            at_least_checked = 0
            at_least_locked = 0
            checked = 0
            locked = 0
            for fr in self.__roots:
                if fr.get_state() == state.CHECKED:
                    checked += 1
                elif fr.get_state() == state.AT_LEAST_ONE_CHECKED:
                    at_least_checked += 1
                elif fr.get_state() == state.LOCKED:
                    locked += 1
                elif fr.get_state() == state.AT_LEAST_ONE_LOCKED:
                    at_least_locked += 1

            if locked == len(self.__roots):
                new_state = state.LOCKED
            elif (locked+at_least_locked) > 0:
                new_state = state.AT_LEAST_ONE_LOCKED
            elif checked == len(self.__roots):
                new_state = state.CHECKED
            elif (at_least_checked+checked) > 0:
                new_state = state.AT_LEAST_ONE_CHECKED
            else:
                new_state = state.UNUSED

        if self._state != new_state:
            self._state = new_state
            return True
        return False

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return 'Path: ' + self.get_id() + \
               ' contains ' + str(len(self.__roots)) + ' file roots\n'

    def __iter__(self):
        for a in self.__roots:
            yield a

    def __getitem__(self, i):
        return self.__roots[i]

    def __len__(self):
        return len(self.__roots)

    def __contains__(self, value):
        # The given value is a FileRoot instance
        if isinstance(value, FileRoot):
            return value in self.__roots

        # The given value is a FileName instance or a string
        for fr in self.__roots:
            x = value in fr
            if x is True:
                return True

        # Value could be the name of a root
        root_id = FileRoot.root(value)
        fr = self.get_root(root_id)
        if fr is not None:
            return True

        # nothing is matching this value
        return False
