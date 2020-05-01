# -*- coding: utf-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        use of this software is governed by the gnu public license, version 3.

        sppas is free software: you can redistribute it and/or modify
        it under the terms of the gnu general public license as published by
        the free software foundation, either version 3 of the license, or
        (at your option) any later version.

        sppas is distributed in the hope that it will be useful,
        but without any warranty; without even the implied warranty of
        merchantability or fitness for a particular purpose.  see the
        gnu general public license for more details.

        you should have received a copy of the gnu general public license
        along with sppas. if not, see <http://www.gnu.org/licenses/>.

        this banner notice must not be removed.

        ---------------------------------------------------------------------

    wkps.wio.sppasWJSON.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import json

from sppas.src.config import sg
from .sppasBaseWkpIO import sppasBaseWkpIO
from ..filebase import States
from ..filestructure import FilePath, FileRoot, FileName
from ..fileref import FileReference, sppasAttribute
from ..fileexc import FileOSError

# ---------------------------------------------------------------------------


class sppasWJSON(sppasBaseWkpIO):
    """
    :author:       Laurent Vouriot
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi
    :summary:      Reader/Writer for sppasWorkspace.

    """
    def __init__(self, name=None):
        """Initialize a sppasWJSON instance.

        :param name: (str) The workspace name

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasWJSON, self).__init__(name)

        self.default_extension = "wjson"
        self.software = sg.__name__

        # -----------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        """ Check wether a file is of wjson format or not.

        :param filename: (str) Name of the file to detect
        :returns: (bool)

        """
        try:
            with open(filename, 'r') as f:
                f.readline()
                doctype_line = f.readline().strip()
                f.close()
        except IOError:
            return False
        except UnicodeDecodeError:
            return False

        return "wjson" in doctype_line

    # -----------------------------------------------------------------------

    def read(self, filename):
        """ Read a wjson file and fill the the sppasWSJON.

        :param filename: (str)
        :returns: (sppasWJSON)

        """
        if os.path.exists(filename) is False:
            raise FileOSError(filename)
        with open(filename, 'r') as f:
            d = json.load(f)
            return self._parse(d)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write in the filename.

        :param filename: (str)
        :returns: json file

        """
        with open(filename, 'w') as f:
            return json.dump(self._serialize(), f, indent=4, separators=(',', ': '))

    # -----------------------------------------------------------------------

    def _serialize(self):
        """Convert this sppasWJSON instance into a serializable structure.

        :returns: (dict) a dictionary that can be serialized

        """
        d = dict()

        # Factual information about this file and this sppasWJSON
        d['wjson'] = "2.0"
        d['software'] = self.software
        d['version'] = sg.__version__
        d['id'] = self.id

        # The list of paths/roots/files stored in this sppasWorkspace()

        d['paths'] = list()
        for fp in self.files:
            d['paths'].append(self._serialize_path(fp))

        # The list of references/attributes stored in this sppasWorkspace()
        d['catalogue'] = list()
        for fref in self.refs:
            d['catalogue'].append(self._serialize_ref(fref))

        return d

    # -----------------------------------------------------------------------

    def _serialize_ref(self, fref):
        """Convert a FileReference into a serializable structure.

        :param fref: (FileReference)
        :returns: (dict) a dictionary that can be serialized

        """
        dict_ref = dict()
        dict_ref["id"] = fref.get_id()
        dict_ref["state"] = fref.get_state()
        dict_ref["type"] = fref.get_type()
        dict_ref["subjoin"] = fref.subjoined

        dict_ref["attributes"] = list()
        # serialize the attribtutes in a reference
        for att in fref.get_attributes():
            dict_ref["attributes"].append(self._serialize_attributes(att))

        return dict_ref

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_attributes(att):
        """Convert a sppasAttribute into a serializable structure.

        :param att: (sppasAttribute)
        :returns: (dict) a dictionary that can be serialized

        """
        dict_att = dict()
        dict_att["id"] = att.get_id()
        dict_att["value"] = att.get_value()
        dict_att["type"] = att.get_value_type()
        dict_att["descr"] = att.get_description()

        return dict_att

    # -----------------------------------------------------------------------

    def _serialize_path(self, fp):
        """Convert a FilePath into a serializable structure.

        :param fp: (FilePath)
        :returns: (dict) a dictionary that can be serialize

        """

        dict_path = dict()
        dict_path["id"] = fp.get_id()
        dict_path["rel"] = os.path.relpath(fp.get_id())
        dict_path["roots"] = list()

        # serialize the roots
        for fr in fp:
            dict_path["roots"].append(self._serialize_root(fr))

        return dict_path

    # -----------------------------------------------------------------------

    def _serialize_root(self, fr):
        """Convert a FileRoot into a serializable structure.

        :param fr: (FileRoot)
        :returns: (dict) a dictionary that can be serialize

        """
        dict_root = dict()
        dict_root["id"] = fr.get_id().split(os.sep)[-1]

        # serialize files
        dict_root["files"] = list()
        for fn in fr:
            dict_root["files"].append(self._serialize_files(fn))

        # serialize refids
        dict_root["refids"] = list()
        for ref in fr.get_references():
            dict_root["refids"].append(ref.get_id())

        return dict_root

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_files(fn):
        """Convert a FileName into a serializable structure.

        :param fn: (FileName)
        :returns: (dict) a dictionary that can be serialized

        """

        dict_files = dict()
        dict_files["id"] = fn.get_id().split(os.sep)[-1]
        dict_files["state"] = fn.get_state()

        return dict_files
    # -----------------------------------------------------------------------

    def _parse(self, d):
        """ fill the data of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :returns: the id of the workspace

        """

        if 'id' not in d:
            raise KeyError("Workspace 'id' is missing of the dictionnary to parse. ")
        self.id = self.validate_id(d["id"])

        if 'paths' in d:
            for dict_path in d['paths']:
                self._parse_path(dict_path)

        if 'catalogue' in d:
            for dictref in d['catalogue']:
                self._parse_ref(dictref)

        return self.id

    # -----------------------------------------------------------------------

    def _parse_ref(self, d):
        """Fill the ref of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :returns: (FileReference)

        """
        if "id" not in d:
            raise KeyError("reference 'id' is missing of the dictionary to parse.")
        fr = FileReference(d["id"])

        if 'type' in d:
            fr.set_type(d["type"])

        if 'attributes' in d:
            for att_dict in d["attributes"]:
                fr.append(self._parse_attribute(att_dict))

        # parse the state value
        s = d.get('state', States().UNUSED)
        if s > 0:
            fr.set_state(States().CHECKED)
        else:
            fr.set_state(States().UNUSED)

        self.add(fr)
        return fr

    # -----------------------------------------------------------------------

    def _parse_path(self, d):
        """Fill the paths of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :returns: (FilePath)

        """
        if 'id' not in d:
            raise KeyError("path 'id' is missing of the dictionary to parse.")

        missing = False
        path = d["id"]
        # checking the entry path exists
        if os.path.exists(d["id"]) is False:
            # if not, checking if the relative path exists
            if os.path.exists(d["rel"]) is False:
                # if not setting the state of the file to missing
                fp = FilePath(path)
                fp.set_state(States().MISSING)
                missing = True
            else:
                path = os.path.abspath(d["rel"])
                fp = FilePath(path)
        else:
            fp = FilePath(d["id"])

        # parse roots
        if 'roots' in d:
            for dict_root in d["roots"]:
                fr = self._parse_root(dict_root, path, missing)
                fp.append(fr)

        fp.subjoined = d.get('subjoin', None)

        self.add(fp)
        return fp

    # -----------------------------------------------------------------------

    def _parse_root(self, d, path, missing):
        """Fill the root of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :param path: (str) path of the file used to create the whole path of the file
        as only the name of the file is kept in the wjson file
        :missing: (bool) if true it means that the FilePath is missing on the computer
        :returns: (FileRoot)

        """
        if "id" not in d:
            raise KeyError("root 'id' is missing of the dictionary to parse.")

        fr = FileRoot(path + os.sep + d["id"])

        if "files" in d:
            for dict_file in d["files"]:
                fr.append(self._parse_file(dict_file, path, missing))

        for ref in d["refids"]:
            refe = FileReference(ref)
            fr.add_ref(refe)

        return fr

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_file(d, path, missing):
        """Fill the files of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :param path: (str) path of the file used to create the whole path of the file
        as only the name of the file is kept in the wjson file
        :missing: (bool) if true it means that the filepath is missing on the computer
        :returns: (FileName)

        """
        if 'id' not in d:
            raise KeyError("file 'id' is missing of the dictionary to parse.")

        fn = FileName(path + os.sep + d["id"])

        # parse the state value
        s = d.get('state', States().UNUSED)
        if s > 0:
            fn.set_state(States().CHECKED)
        else:
            fn.set_state(States().UNUSED)
        if missing is True:
            fn.set_state(States().MISSING)

        return fn

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_attribute(d):
        """Fill the attribute of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :returns: (sppasAttribute)

        """
        if 'id' not in d:
            raise KeyError("attribute 'id' is missing of the dictionary to parse.")
        att = sppasAttribute(d['id'])

        att.set_value(d["value"])
        att.set_value_type(d["type"])
        att.set_description(d["descr"])

        return att

