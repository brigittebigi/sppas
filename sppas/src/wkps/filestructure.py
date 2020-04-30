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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import mimetypes
import logging
import os
import glob
from datetime import datetime

from sppas import sppasTypeError
from sppas import sppasValueError

from .fileref import FileReference
from .fileexc import FileRootValueError, FileOSError, FileTypeError
from .filebase import FileBase, States

# ---------------------------------------------------------------------------


class FileName(FileBase):
    """Represent the data linked to a filename.

    Use instances of this class to hold data related to a filename.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    FILENAME_STATES = (States().UNUSED, States().CHECKED, States().LOCKED, States().MISSING)

    def __init__(self, identifier):
        """Constructor of a FileName.

        From the identifier, the following properties are extracted:

            1. name (str) The base name of the file, without path nor ext
            2. extension (str) The extension of the file, or the mime type
            3. date (str) Time of the last modification
            4. size (str) Size of the file

        :param identifier: (str) Full name of a file
        :raise: FileOSError if identifier does not match an existing file,
        FileTypeError if the filename does not match a file (like links
        or folder).

        """
        super(FileName, self).__init__(identifier)
        if os.path.exists(self.id) is False:
            raise FileOSError(self.id)
        if os.path.isfile(self.id) is False:
            raise FileTypeError(self.id)

        # Properties of the file (protected)
        # ----------------------------------

        # The name (no path, no extension)
        fn, ext = os.path.splitext(self.get_id())
        self.__name = os.path.basename(fn)

        # The extension is forced to be in upper case
        self.__extension = ext.upper()

        # Modified date/time and file size
        self.__date = None
        self.__filesize = 0
        self.update_properties()

    # -----------------------------------------------------------------------

    def folder(self):
        """Return the name of the directory of this file."""
        return os.path.dirname(self.id)

    # -----------------------------------------------------------------------

    def get_name(self):
        """Return the short name of the file., i.e. without path nor extension."""
        return self.__name

    # -----------------------------------------------------------------------

    def get_extension(self):
        """Return the extension of the file."""
        return self.__extension

    # -----------------------------------------------------------------------

    def get_mime(self):
        """Return the mime type of the file."""
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
        filesize = self.__filesize / 1024
        if filesize > (1024 * 1024):
            filesize /= 1024
            unit = " Mo"

        return str(int(filesize)) + unit

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Override. Set a state value to this filename.

        Notice that a locked file can only be unlocked by assigning the
        UNUSED state.

        :param value: (States)
        :returns: (bool) this filename state has changed or not
        :raise: sppasTypeError

        """
        if value not in FileName.FILENAME_STATES:
            raise sppasTypeError(value, str(FileName.FILENAME_STATES))

        if self._state == States().LOCKED and value != States().CHECKED:
            return False
        if self._state == value:
            return False

        self._state = value
        return True

    # -----------------------------------------------------------------------

    def update_properties(self):
        """Update properties of the file (modified date and filesize).

        :raise: FileTypeError if the file is not existing

        """
        # test if the file is still existing
        if os.path.isfile(self.get_id()) is False:
            raise FileTypeError(self.get_id())
        # get time and size
        try:
            self.__date = datetime.fromtimestamp(
                os.path.getmtime(self.get_id()))
        except ValueError:
            self.__date = None
        self.__filesize = os.path.getsize(self.get_id())

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
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    def __init__(self, name):
        """Constructor of a FileRoot.

        :param name: (str) Filename or root name
        :raise: OSError if filepath does not match a directory (not file/link)

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
        changed = list()
        for fn in self.__files:
            if fn == filename:
                m = fn.set_state(value)
                if m is True:
                    changed.append(fn)
                    m = self.update_state()
                    if m is True:
                        changed.append(self)
                    return changed

        return changed

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Set a value to represent the state of the root.

        It is not allowed to manually assign one of the "AT_LEAST" states
        (they are automatically fixed by setting the state of a FileName
        with set_object_state method).

        The state of locked files is not changed.

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

    statefr = property(FileBase.get_state, set_state)

    # -----------------------------------------------------------------------

    def update_state(self):
        """Update the state depending on the checked and locked filenames.

        :return: (bool) State is changed or not

        """
        if len(self.__files) == 0:
            new_state = States().UNUSED
        else:
            checked = 0
            locked = 0
            missing = 0
            for fn in self.__files:
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
            elif missing > 0:
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
        """Return True if the root as the given reference.

        :returns: (bool)

        """
        if isinstance(ref, FileReference) is False:
            raise sppasTypeError(ref, 'FileReference')

        if len(self.get_references()) == 0:
            return False

        for r in self.get_references():
            if r.id == ref.id:
                return True

        return False

    # -----------------------------------------------------------------------

    def add_ref(self, ref):
        has = self.has_ref(ref)
        if has is True:
            return False

        if self.__references is None:
            self.__references = list()

        self.__references.append(ref)
        return True

    # -----------------------------------------------------------------------

    def remove_ref(self, ref):
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
                    if isinstance(reference, FileReference) is False:
                        raise sppasTypeError(reference, 'FileReference')

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
        for fn in self.__files:
            if fn.id == filename:
                return fn

        return None

    # -----------------------------------------------------------------------

    def append(self, filename, all_root=False, ctime=0.):
        """Append a filename in the list of files.

        Given filename must be the absolute name of a file or an instance
        of FileName.

        :param filename: (str, FileName) Absolute name of a file
        :param all_root: (bool) Add all files sharing the same root
        :param ctime: (float) Add files only if created/modified after time in seconds since the epoch
        :returns: (list of FileName) the appended FileName() instances or None

        """
        fns = list()
        # Get or create the FileName instance
        if filename is not None:
            fn = filename
            if isinstance(filename, FileName) is False:
                fn = FileName(filename)

        # Check if root is ok
        if self.id != FileRoot.root(fn.id):
            raise FileRootValueError(fn.id, self.id)

        # Check if this filename is not already in the list
        if all_root is False and fn not in self:
            if os.path.getmtime(fn.get_id()) > ctime:
                self.__files.append(fn)
                fns.append(fn)

        if all_root is True:
            # add all files sharing this root on the disk,
            # except if a ctime value is given and file is too old.
            for new_filename in sorted(glob.glob(self.id+"*")):
                if os.path.isfile(new_filename) is True:
                    fn = FileName(new_filename)
                    if fn.get_id() not in self:
                        if os.path.getmtime(fn.get_id()) > ctime:
                            self.__files.append(fn)
                            fns.append(fn)
        if len(fns) > 0:
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
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    def __init__(self, filepath):
        """Constructor of a FilePath.

        :param filepath: (str) Absolute or relative name of a folder
        :raise: OSError if filepath does not match a directory (not file/link)

        """
        super(FilePath, self).__init__(os.path.abspath(filepath))

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
            file_id = self.identifier(entry)
            entry = FileName(file_id)

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

        The state of locked files is not changed.

        :param value: (State) A state of FileName.

        """
        if value not in FileName.FILENAME_STATES:
            raise sppasTypeError(value, str(FileName.FILENAME_STATES))

        modified = list()

        self._state = value

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
        if os.path.isdir(abs_name) and abs_name == self.id:
            return self

        elif os.path.isfile(filename):
            idt = self.identifier(filename)
            for fr in self.__roots:
                fn = fr.get_object(idt)
                if fn is not None:
                    return fn
        else:
            for fr in self.__roots:
                if fr.id == abs_name:
                    return fr

        return None

    # -----------------------------------------------------------------------

    def identifier(self, filename):
        """Return the identifier, i.e. the full name of the file.

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

        :param entry: (str, FileName, FileRoot) Absolute or relative name of a file
        :param all_root: (bool) Add also all files sharing the same root as the given one, or all files of the given root
        :param ctime: (float) Add files only if created/modified after time in seconds since the epoch
        :returns: (FileName, FileRoot) the list of appended objects or None

        """
        # list of new objects added to the data
        new_objs = list()
        new_files = list()

        if isinstance(entry, FileRoot):
            # Given entry is a FileRoot instance

            # test if root is matching this path
            abs_name = os.path.dirname(entry.id)
            if abs_name != self.id:
                raise Exception('The root {:s} is not matching the path {:s}'.format(entry.id, self.id))

            # test if this root is already inside this path
            obj = self.get_root(entry.id)
            if obj is None:
                self.__roots.append(entry)
                new_objs.append(entry)

            # add all files of this root (if asked)
            if all_root is True:
                new_files = entry.append(None, all_root=all_root, ctime=ctime)

        else:
            # Given entry is a filename or FileName instance
            if isinstance(entry, FileName):
                file_id = entry.id
            else:
                file_id = self.identifier(entry)
                entry = FileName(file_id)
            root_id = FileRoot.root(file_id)

            # Get or create the corresponding FileRoot
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
        """Remove an entry of the list of roots.

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

    def update_state(self):
        """Modify state depending on the checked root names."""
        if len(self.__roots) == 0:
            new_state = States().UNUSED

        else:
            at_least_checked = 0
            at_least_locked = 0
            checked = 0
            locked = 0
            missing = 0
            for fr in self.__roots:
                if fr.get_state() == States().CHECKED:
                    checked += 1
                elif fr.get_state() == States().AT_LEAST_ONE_CHECKED:
                    at_least_checked += 1
                elif fr.get_state() == States().LOCKED:
                    locked += 1
                elif fr.get_state() == States().MISSING:
                    missing += 1
                elif fr.get_state() == States().AT_LEAST_ONE_LOCKED:
                    at_least_locked += 1

            if locked == len(self.__roots):
                new_state = States().LOCKED
            elif (locked+at_least_locked) > 0:
                new_state = States().AT_LEAST_ONE_LOCKED
            elif checked == len(self.__roots):
                new_state = States().CHECKED
            elif (at_least_checked+checked) > 0:
                new_state = States().AT_LEAST_ONE_CHECKED
            elif missing > 0:
                new_state = States().MISSING
            else:
                new_state = States().UNUSED

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
