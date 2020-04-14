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

    src.files.filedata.py
    ~~~~~~~~~~~~~~~~~~~~~

    Description:
    ============

    Use instances of these classes to hold data related to filenames and
    references.
    
    Files are structured in a fixed tree-like structure:
        - a FileData contains a list of FilePath,
        - a FilePath contains a list of FileRoot,
        - a FileRoot contains a list of FileName,
        - a FileName is limited to regular file names (no links, etc).

    References are structured as:
        - a FileData contains a list of FileReference,
        - a FileReference contains a list of sppasAttribute.

    Example:
    ========

    The file 'C:\\Users\\MyName\\Desktop\\myfile.pdf' and the file
    'C:\\Users\\MyName\\Desktop\\myfile.txt' will be in the following tree:

        + FileData:
            + FilePath: id='C:\\Users\\MyName\\Desktop'
                + FileRoot: id='C:\\Users\\MyName\\Desktop\\myfile'
                    + FileName: 
                        * id='C:\\Users\\MyName\\Desktop\\myfile.pdf'
                        * name='myfile'
                        * extension='.PDF'
                    + FileName: 
                        * id='C:\\Users\\MyName\\Desktop\\myfile.txt'
                        * name='myfile'
                        * extension='.TXT'
    

    Raised exceptions:
    ==================

        - FileOSError (error 9010)
        - FileTypeError (error 9012)
        - PathTypeError (error 9014)
        - FileRootValueError (error 9030)


    Tests:
    ======

        - python 2.7.15
        - python 3.7.0

"""

import json
import os
import logging

from sppas import sppasTypeError
from sppas.src.config import sg

from .fileutils import sppasGUID
from .filebase import FileBase, States
from .fileref import FileReference
from .filestructure import FileName, FileRoot, FilePath

# ---------------------------------------------------------------------------


class FileData(FileBase):
    """Represent the data linked to a list of files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    TODO: Rename FileData to sppasWorkspace

    FileData is the container for a  list of files and a catalog.
    It organizes files hierarchically as a collection of FilePath instances,
    each of which is a collection of FileRoot instances, each of which is a 
    collection of FileName. The catalog is a list of FileReference instances
    each of which is a list of key/att-value.

    """

    def __init__(self, identifier=sppasGUID().get()):
        """Constructor of a FileData."""
        super(FileData, self).__init__(identifier)
        self.__data = list()
        self.__refs = list()

    # -----------------------------------------------------------------------
    # Methods to add data
    # -----------------------------------------------------------------------

    def add(self, file_object):
        """Add a file object into the data.

        IMPLEMENTED ONLY FOR FilePath and FileReference.

        :param file_object: (FileBase)
        :raise: sppasTypeError,

        """
        if isinstance(file_object, (FileName, FileRoot, FilePath, FileReference)) is False:
            raise sppasTypeError(file_object.id, "FileBase-subclass")

        test_obj = self.get_object(file_object.id)
        if test_obj is not None:
            raise Exception('Object {:s} is already in the data.'.format(file_object.id))

        if isinstance(file_object, FilePath):
            self.__data.append(file_object)

        elif isinstance(file_object, FileReference):
            self.add_ref(file_object)

        else:
            raise NotImplementedError

    # -----------------------------------------------------------------------

    def add_file(self, filename, brothers=False, ctime=0.):
        """Add file(s) in the list from a file name.

        :param filename: (str) Absolute or relative name of a file
        :param brothers: (bool) Add also all files sharing the same root as the given file
        :param ctime: (float) Add files only if created/modified after time in seconds since the epoch
        :returns: (list of FileBase or None)
        :raises: OSError

        """
        # get or create the corresponding FilePath()
        new_fp = FilePath(os.path.dirname(filename))
        for fp in self.__data:
            if fp.id == new_fp.id:
                new_fp = fp

        # add the file(s) into the FilePath() structure
        added = new_fp.append(filename, brothers, ctime)

        # this is a new path to add into the workspace
        if added is None:
            added = list()
        elif added is not None and new_fp not in self.__data:
            self.__data.append(new_fp)

        return added

    # -----------------------------------------------------------------------

    def remove_file(self, filename):
        """Remove a file in the list from its file name.

        Its root and path are also removed if empties, or their state is
        updated.

        :param filename: (str) Absolute or relative name of a file
        :returns: (list) Identifiers of removed objects
        :raises: OSError

        """
        if isinstance(filename, FileName):
            fn_id = filename.get_id()
        else:
            fn_id = FileName(filename).get_id()

        given_fp = FilePath(os.path.dirname(filename))
        path = None
        root = None
        removed = list()
        for fp in self.__data:
            if fp.get_id() == given_fp.get_id():
                for fr in fp:
                    rem_id = fr.remove(fn_id)
                    if rem_id is not None:
                        removed.append(rem_id)
                        root = fr
                        path = fp
                        break

        # if we removed a file, check if its root/path have to be removed too
        if root is not None:
            # The file was removed. Check to remove (or not) the root.
            if len(root) == 0:
                removed.append(root.get_id())
                path.remove(root)
            else:
                root.update_state()

            if len(path) == 0:
                removed.append(path.get_id())
                self.__data.remove(path)
            else:
                path.update_state()

        return removed

    # -----------------------------------------------------------------------

    def add_ref(self, ref):
        """Add a reference in the list from its file name.

        :param ref: (FileReference) Reference to add

        """
        if isinstance(ref, FileReference) is False:
            raise sppasTypeError(ref, 'FileReference')

        for refe in self.__refs:
            if refe.id == ref.id:
                raise ValueError(
                    "A reference with the identifier '{:s}' is "
                    "already in the data.".format(refe.id))

        self.__refs.append(ref)

    # -----------------------------------------------------------------------

    def remove_refs(self, state=States().CHECKED):
        """Remove all references of the given state.

        :param state: (States)
        :returns: (int) Number of removed refs

        """
        # Fix the list of references to be removed
        removes = list()
        for ref in self.__refs:
            if ref.state == state:
                removes.append(ref)

        # Remove these references of the roots
        for fp in self.__data:
            for fr in fp:
                for fc in removes:
                    fr.remove_ref(fc)

        # Remove these references of the list of existing references
        nb = len(removes)
        for ref in reversed(removes):
            self.__refs.remove(ref)

        return nb

    # -----------------------------------------------------------------------

    def get_refs(self):
        """Return the list of references."""
        return self.__refs

    # -----------------------------------------------------------------------

    def update(self):
        """Update the data: missing files, properties changed.

        Empty FileRoot and FilePath are removed.

        """
        for fp in self.__data:
            for fr in reversed(fp):
                for fn in reversed(fr):
                    if os.path.exists(fn.id):
                        fn.update_properties()
                    else:
                        fr.remove(fn)
                if len(fr) == 0:
                    fp.remove(fr)

        # Remove empty FilePath
        for fp in reversed(self.__data):
            if len(fp) == 0:
                self.__data.remove(fp)

        for fp in self.__data:
            for fr in reversed(fp):
                fr.update_state()
            fp.update_state()

    # -----------------------------------------------------------------------

    def remove_files(self, state=States().CHECKED):
        """Remove all files of the given state.

        Do not update: empty roots or paths are not removed.

        :param state: (States)
        :returns: (int)

        """
        nb = 0
        for fp in self.__data:
            for fr in reversed(fp):
                for fn in reversed(fr):
                    if fn.get_state() == state:
                        fr.remove(fn)
                        nb += 1
                fr.update_state()
            fp.update_state()

        return nb

    # -----------------------------------------------------------------------

    def get_files(self, value=States().CHECKED):
        """Return the list of file names of the given state.

        :param value: (bool) Toggle state
        :returns: (list of str)

        """
        checked = list()
        for fp in self.__data:
            for fr in fp:
                for fn in fr:
                    if fn.get_state() == value:
                        checked.append(fn.id)
        return checked

    # -----------------------------------------------------------------------

    def get_object(self, identifier):
        """Return the file object matching the given identifier.

        :param identifier: (str)
        :returns: (FileData, FilePath, FileRoot, FileName, FileReference)

        """
        if self.id == identifier:
            return self

        for ref in self.get_refs():
            if ref.id == identifier:
                return ref

        for fp in self.__data:
            if fp.id == identifier:
                return fp
            for fr in fp:
                if fr.id == identifier:
                    return fr
                for fn in fr:
                    if fn.id == identifier:
                        return fn

        return None

    # -----------------------------------------------------------------------

    @staticmethod
    def get_object_state(file_obj):
        """Return the state of any FileBase within the FileData.

        :param file_obj: (FileBase) The object which one enquire the state
        :returns: States

        """
        if not isinstance(file_obj, FilePath)\
            and not isinstance(file_obj, FileRoot)\
                and not isinstance(file_obj, FileName):
            raise sppasTypeError(file_obj, 'FilePath or FileRoot or FileName')
        else:
            return file_obj.get_state()

    # -----------------------------------------------------------------------

    def set_object_state(self, state, file_obj=None):
        """Set the state of any FileBase within FileData.

        The default case is to set the state to all FilePath and FileRefence.

        It is not allowed to manually assign one of the "AT_LEAST" states.
        They are automatically fixed depending on the paths states.

        :param state: (States) state to set the file to
        :param file_obj: (FileBase) the specific file to set the state to
        :raises: sppasTypeError, sppasValueError
        :return: list of modified objects

        """
        modified = list()
        if file_obj is None:
            for fp in self.__data:
                m = fp.set_state(state)
                if m is True:
                    modified.append(fp)
            for ref in self.__refs:
                m = ref.set_state(state)
                if m is True:
                    modified.append(ref)

        else:
            if isinstance(file_obj, FileReference):
                file_obj.set_state(state)
                modified.append(file_obj)

            elif isinstance(file_obj, FilePath):
                modified = file_obj.set_state(state)

            elif isinstance(file_obj, (FileRoot, FileName)):
                # search for the FilePath matching with the file_obj
                for fp in self.__data:
                    # test if file_obj is a root or name in this fp
                    cur_obj = fp.get_object(file_obj.id)
                    if cur_obj is not None:
                        # this object is one of this fp
                        m = fp.set_object_state(state, file_obj)
                        if len(m) > 0:
                            modified.extend(m)
                        break
            else:
                logging.error("Wrong type of the object: {:s}"
                              "".format(str(type(file_obj))))
                raise sppasTypeError(file_obj, 'FileBase')

        return modified

    # -----------------------------------------------------------------------

    def set_state(self, value):
        """Set the state of this FileData instance.

        :param value: (States)

        """
        self._state = int(value)

    # -----------------------------------------------------------------------

    def associate(self):
        ref_checked = self.get_reference_from_state(States().CHECKED)
        if len(ref_checked) == 0:
            return 0

        associed = 0
        for fp in self.__data:
            for fr in fp:
                if fr.get_state() in (States().AT_LEAST_ONE_CHECKED, States().CHECKED):
                    associed += 1
                    if fr.get_references() is not None:
                        ref_extended = fr.get_references()
                        ref_extended.extend(ref_checked)
                        #
                        # oskur
                        # fr.set_references(list(set(ref_extended)))
                        #
                        fr.set_references(list(ref_extended))
                    else:
                        fr.set_references(ref_checked)

        return associed

    # -----------------------------------------------------------------------

    def dissociate(self):
        ref_checked = self.get_reference_from_state(States().CHECKED)
        if len(ref_checked) == 0:
            return 0

        dissocied = 0
        for fp in self.__data:
            for fr in fp:
                if fr.get_state() in (States().AT_LEAST_ONE_CHECKED, States().CHECKED):
                    for ref in ref_checked:
                        removed = fr.remove_ref(ref)
                        if removed is True:
                            dissocied += 1
        return dissocied

    # -----------------------------------------------------------------------

    def is_empty(self):
        """Return if the instance contains information."""
        return len(self.__data) + len(self.__refs) == 0

    # -----------------------------------------------------------------------

    def get_filepath_from_state(self, state):
        """Return every FilePath of the given state.

        """
        paths = list()
        for fp in self.__data:
            if fp.get_state() == state:
                paths.append(fp)
        return paths

    # -----------------------------------------------------------------------

    def get_fileroot_from_state(self, state):
        """Return every FileRoot in the given state."""
        roots = list()
        for fp in self.__data:
            for fr in fp:
                if fr.get_state() == state:
                    roots.append(fr)
        return roots

    # -----------------------------------------------------------------------

    def get_fileroot_with_ref(self, ref):
        """Return every FileRoot with the given reference."""
        roots = list()
        for fp in self.__data:
            for fr in fp:
                if fr.has_ref(ref) is True:
                    roots.append(fr)
        return roots

    # -----------------------------------------------------------------------

    def get_filename_from_state(self, state):
        """Return every FileName in the given state.

        """
        if len(self.__data) == 0:
            return list()

        files = list()
        for fp in self.__data:
            for fr in fp:
                for fn in fr:
                    if fn.get_state() == state:
                        files.append(fn)
        return files

    # -----------------------------------------------------------------------

    def get_reference_from_state(self, state):
        """Return every Reference in the given state.

        """
        if len(self.__refs) == 0:
            return list()

        refs = list()
        for r in self.__refs:
            if r.get_state() == state:
                refs.append(r)
        return refs

    # -----------------------------------------------------------------------

    def has_locked_files(self):
        for fp in self.__data:
            if fp.get_state() in (States().AT_LEAST_ONE_LOCKED, States().LOCKED):
                return True
        return False

    # -----------------------------------------------------------------------

    def get_parent(self, filebase):
        """Return the parent of an object.

        :param filebase: (FileName or FileRoot).
        :returns: (FileRoot or FilePath)
        :raises: sppasTypeError

        """
        if isinstance(filebase, FileName):
            fr = FileRoot(filebase.id)
            return self.get_object(fr.id)

        if isinstance(filebase, FileRoot):
            fp = FilePath(os.path.dirname(filebase.id))
            return self.get_object(fp.id)

        raise sppasTypeError(filebase, "FileName, FileRoot")

    # -----------------------------------------------------------------------

    def unlock(self, entries=None):
        """Unlock the given list of files.

        :param entries: (list, None) List of FileName to unlock
        :returns: number of unlocked entries

        """
        i = 0
        if entries is None:
            for fp in self.__data:
                for fr in fp:
                    for fn in fr:
                        if fn.get_state() == States().LOCKED:
                            fn.set_state(States().CHECKED)
                            i += 1
                    if i > 0:
                        fr.update_state()
                if i > 0:
                    fp.update_state()

        elif isinstance(entries, list):
            for fp in self.__data:
                for fr in fp:
                    for fn in fr:
                        if fn in entries and fn.get_state() == States().LOCKED:
                            fn.set_state(States().CHECKED)
                            i += 1
                    if i > 0:
                        fr.update_state()
                if i > 0:
                    fp.update_state()

        return i

    # -----------------------------------------------------------------------
    # Read/Write the data into/from a file
    # -----------------------------------------------------------------------

    def serialize(self):
        """Convert this FileData() into a serializable data structure.

        :returns: (dict) a dictionary that can be serialized (without classes).

        """
        d = dict()

        # Factual information about this file and this FileData()
        d['wjson'] = "1.0"
        d['software'] = sg.__name__
        d['version'] = sg.__version__
        d['id'] = self.id

        # The list of paths/roots/files stored in this FileData()
        d['paths'] = list()
        for fp in self.__data:
            d['paths'].append(fp.serialize())

        # The list of references/attributes stored in this FileData()
        d['catalogue'] = list()
        for ref in self.__refs:
            d['catalogue'].append(ref.serialize())

        return d

    # -----------------------------------------------------------------------

    @staticmethod
    def parse(d):
        wjson_version = d.get("wjson", "1.0")
        soft_name = d.get("software", None)
        soft_version = d.get("version", None)

        if 'id' not in d:
            raise KeyError("Workspace 'id' is missing of the dictionary to parse.")
        data = FileData(d['id'])

        # The list of references/attributes stored in the given dict
        if 'catalogue' in d:
            for dictref in d['catalogue']:
                r = FileReference.parse(dictref)
                data.add_ref(r)

        # The list of paths/roots/files stored in the given dict
        if 'paths' in d:
            for dict_path in d['paths']:
                fp = FilePath.parse(dict_path)
                data.add(fp)

                # append references in roots from the 'refsids" of the dict
                for dict_root in dict_path['roots']:
                    fr = data.get_object(dict_root['id'])
                    if fr is not None and 'refids' in dict_root:
                        for ref_id in dict_root['refids']:
                            ref = data.get_object(ref_id)
                            if ref is not None:
                                fr.add_ref(ref)

        # Fix the state to roots and paths (from the ones of files)
        data.update()
        return data

    # -----------------------------------------------------------------------

    def save(self, filename):
        """Save the current FileData in a serialized file.

        :param filename: (str) the name of the save file.

        """
        with open(filename, 'w') as fd:
            json.dump(self.serialize(), fd, indent=4, separators=(',', ': '))

    # -----------------------------------------------------------------------

    @staticmethod
    def load(filename):
        """Load a saved FileData object from a save file.

        :param filename: (str) the name of the save files.
        :returns: FileData

        """
        with open(filename, "r") as fd:
            d = json.load(fd)
            return FileData.parse(d)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__data:
            yield a

    def __getitem__(self, i):
        return self.__data[i]

    def __len__(self):
        return len(self.__data)
