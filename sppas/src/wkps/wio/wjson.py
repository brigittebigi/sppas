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

    wkps.wio.wjson.py
    ~~~~~~~~~~~~~~~~~~

"""

import os
import json
from collections import OrderedDict

from sppas.src.config import sg

from ..filebase import FileBase, States
from ..filestructure import FilePath, FileRoot, FileName
from ..fileref import sppasCatReference, sppasRefAttribute
from ..wkpexc import FileOSError

from .basewkpio import sppasBaseWkpIO

# ---------------------------------------------------------------------------


class sppasWJSON(sppasBaseWkpIO):
    """Reader and writer of a workspace in wjson format.

    :author:       Laurent Vouriot
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, name=None):
        """Initialize a sppasWJSON instance.

        :param name: (str) The name of the workspace

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasWJSON, self).__init__(name)

        self.default_extension = "wjson"
        self.software = sg.__name__

    # -----------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        """Check whether a file is of wjson format or not.

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
        """Read a wjson file and fill the the sppasWSJON.

        :param filename: (str)

        """
        if os.path.exists(filename) is False:
            raise FileOSError(filename)
        with open(filename, 'r') as f:
            d = json.load(f)
            self._parse(d)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write in the filename.

        :param filename: (str)

        """
        serialized_dict = self._serialize()
        with open(filename, 'w') as f:
            json.dump(serialized_dict, f, indent=4, separators=(',', ': '))

    # -----------------------------------------------------------------------

    def _serialize(self):
        """Convert this sppasWJSON instance into a serializable structure.

        :returns: (dict) a dictionary that can be serialized

        """
        d = OrderedDict()

        # Factual information about this file and this sppasWJSON
        d['wjson'] = "2.0"
        d['software'] = self.software
        d['version'] = sg.__version__
        d['id'] = self.id

        # The list of paths/roots/files stored in this sppasWorkspace()
        d['paths'] = list()
        for fp in self.get_paths():
            d['paths'].append(self._serialize_path(fp))

        # The list of references/attributes stored in this sppasWorkspace()
        d['catalogue'] = list()
        for fref in self.get_refs():
            d['catalogue'].append(self._serialize_ref(fref))

        return d

    # -----------------------------------------------------------------------

    def _serialize_ref(self, fref):
        """Convert a sppasCatReference into a serializable structure.

        :param fref: (sppasCatReference)
        :returns: (dict) a dictionary that can be serialized

        """
        dict_ref = dict()
        dict_ref["id"] = fref.get_id()
        dict_ref["state"] = fref.get_state()
        dict_ref["type"] = fref.get_type()
        dict_ref["subjoin"] = fref.subjoined

        dict_ref["attributes"] = list()
        # serialize the attributes in a reference
        for att in fref:
            dict_ref["attributes"].append(self._serialize_attributes(att))

        return dict_ref

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_attributes(att):
        """Convert a sppasRefAttribute into a serializable structure.

        :param att: (sppasRefAttribute)
        :returns: (dict) a dictionary that can be serialized

        """
        dict_att = dict()
        dict_att["id"] = att.get_id()
        dict_att["value"] = att.get_typed_value()
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

        if fp.subjoined is not None:
            dict_path['subjoin'] = fp.subjoined

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

        # references identifiers are stored into a list
        dict_root["refids"] = list()
        for ref in fr.get_references():
            dict_root["refids"].append(ref.get_id())

        # subjoined data are simply added as-it
        # (it's risky, the embedded data could be un-serializable by json...)
        if fr.subjoined is not None:
            dict_root['subjoin'] = fr.subjoined

        return dict_root

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_files(fn):
        """Convert a FileName into a serializable structure.

        :param fn: (FileName)
        :returns: (dict) a dictionary that can be serialized

        """
        dict_file = dict()
        dict_file["id"] = fn.get_id().split(os.sep)[-1]
        dict_file["state"] = fn.get_state()

        # subjoined data are simply added as-it
        if fn.subjoined is not None:
            dict_file['subjoin'] = fn.subjoined

        return dict_file

    # -----------------------------------------------------------------------

    def _parse(self, d):
        """Fill the data of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :returns: the id of the workspace

        """
        if 'id' not in d:
            raise KeyError("Workspace 'id' is missing of the dictionary to parse. ")
        try:
            idw = FileBase.validate_id(d['id'])
            self._id = idw
        except ValueError:
            # We keep our current 'id'
            pass

        if 'paths' in d:
            for dict_path in d['paths']:
                self._parse_path(dict_path)

        if 'catalogue' in d:
            for dict_ref in d['catalogue']:
                self._parse_ref(dict_ref)

        return self.id

    # -----------------------------------------------------------------------

    def _parse_ref(self, d):
        """Fill the ref of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :returns: (sppasCatReference)

        """
        if "id" not in d:
            raise KeyError("reference 'id' is missing of the dictionary to parse.")
        fr = sppasCatReference(d["id"])

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

        path = d["id"]
        # check if the entry path exists
        if os.path.exists(d["id"]) is False:
            # check if the relative path exists. "rel" was introduced in v2.0.
            # check if "rel" exists for compatibility with v1.0.
            if "rel" in d:
                if os.path.exists(d["rel"]) is True:
                    path = os.path.abspath(d["rel"])
        # in any case, create the corresponding object
        fp = FilePath(path)

        # parse its roots
        if 'roots' in d:
            for dict_root in d["roots"]:
                fr = self._parse_root(dict_root, path)
                fp.append(fr)

        # append subjoined
        fp.subjoined = d.get('subjoin', None)

        self.add(fp)
        return fp

    # -----------------------------------------------------------------------

    def _parse_root(self, d, path):
        """Fill the root of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :param path: (str) path of the file used to create the whole path of the file
        as only the name of the file is kept in the wjson file
        :returns: (FileRoot)

        """
        if "id" not in d:
            raise KeyError("root 'id' is missing of the dictionary to parse.")

        fr = FileRoot(path + os.sep + d["id"])

        if "files" in d:
            for dict_file in d["files"]:
                fr.append(self._parse_file(dict_file, path))

        for ref in d["refids"]:
            refe = sppasCatReference(ref)
            fr.add_ref(refe)

        # append subjoined dict "as it"
        fr.subjoined = d.get('subjoin', None)

        return fr

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_file(d, path):
        """Fill the files of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :param path: (str) path of the file used to create the whole path of the file
        as only the name of the file is kept in the wjson file
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

        # append subjoined dict "as it"
        fn.subjoined = d.get('subjoin', None)

        return fn

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_attribute(d):
        """Fill the attribute of a sppasWJSON reader with the given dictionary.

        :param d: (dict)
        :returns: (sppasRefAttribute)

        """
        if 'id' not in d:
            raise KeyError("attribute 'id' is missing of the dictionary to parse.")
        att = sppasRefAttribute(d['id'])

        att.set_value(d["value"])
        att.set_value_type(d["type"])
        att.set_description(d["descr"])

        return att

