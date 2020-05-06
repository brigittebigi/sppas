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

    wkps.wio.wkpannpro.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import xml.etree.cElementTree as ET

from sppas.src.config import sg

from sppas.src.wkps.filebase import FileBase
from sppas.src.wkps.filestructure import FilePath, FileRoot
from sppas.src.wkps.wio.basewkpio import sppasBaseWkpIO
from sppas.src.wkps.wkpexc import FileOSError

# ----------------------------------------------------------------------------


class sppasWANT(sppasBaseWkpIO):
    """Reader and writer to import/export a workspace from/to annotationpro.

        :author:       Laurent Vouriot
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """
    def __init__(self, name=None):
        """Initialize aa sppasWANT instance.

        :param name: (str) The name of the workspace

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasWANT, self).__init__(name)

        self.default_extension = "antw"
        self.software = "Annotation Pro"

    # -------------------------------------------------------------------------

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

        return "WorkspaceDataSet" in doctype_line

    # -----------------------------------------------------------------------

    @staticmethod
    def indent(elem, level=0):
        """Pretty indent of an ElementTree.

        http://effbot.org/zone/element-lib.htm#prettyprint

        """
        i = "\n" + level * "\t"
        if len(elem) > 0:
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                if level < 2:
                    elem.tail = "\n" + i
                else:
                    elem.tail = i
            for elem in elem:
                sppasWANT.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    # -------------------------------------------------------------------------

    def read(self, filename):
        """Read a antw file and fill the sppasWANT.

        :param filename: (str)

        """
        if os.path.exists(filename) is False:
            raise FileOSError(filename)
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            uri = root.tag[:root.tag.index('}')+1]

            for child in tree.iter(tag=uri + "WorkspaceItem"):
                return self._parse(child, uri)
        except Exception:
            raise

    # -------------------------------------------------------------------------

    def write(self, filename):
        """Write in the filename.

        :param filename: (str)
        :returns: xml file

        """
        root = ET.Element("WorkspaceDataSet")
        root.set("xmlns", "http://tempuri.org/WorkspaceDataSet.xsd")
        uri = "{http://tempuri.org/WorkspaceDataSet.xsd}"

        tree = ET.SubElement(root, "workspaceItem")

        self._serialize(tree, uri)

        sppasWANT.indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename,
                   encoding=sg.__encoding__,
                   xml_declaration=True,
                   method="xml")

    # -------------------------------------------------------------------------

    def _serialize(self, root, uri=""):
        """Convert this sppasWANT instance into a serializable structure.

        :param root: (ET.Element) root of the tree in which we want to serialize
        :param uri: (str)
        :returns: (tree) a tree that can be serialized

        """
        for fp in self.get_all_files():
            sub = fp.subjoined

        child_id = ET.SubElement(root, "Id")
        child_id.text = self._id

        child_id_group = ET.SubElement(root, "IdGroup")
        child_id_group.text = sub[uri + "IdGroup"]

        child_name = ET.SubElement(root, "Name")
        child_name.text = sub[uri + "Name"]

        child_open_count = ET.SubElement(root, "OpenCount")
        child_open_count.text = sub[uri + "OpenCount"]

        child_edit_count = ET.SubElement(root, "EditCount")
        child_edit_count.text = sub[uri + "EditCount"]

        child_listen_count = ET.SubElement(root, "ListenCount")
        child_listen_count.text = sub[uri + "ListenCount"]

        child_accepted = ET.SubElement(root, "Accepted")
        child_accepted.text = sub[uri + "Accepted"]

        return root

    # -------------------------------------------------------------------------

    def _parse(self, tree, uri=""):
        """Fill the data of a sppasWANT reader with a tree.

        :param tree: (ElementTree) tree to parse
        :param uri: (str)
        :returns: the id of the workspace

        """
        identifier = tree.find(uri + "Id")
        if identifier is None:
            raise KeyError("Workspace id is missing of the tree to parse")
        try:
            idw = FileBase.validate_id(identifier.text)
            self._id = idw
        except ValueError:
            # we keep our current 'id'
            pass

        sub = dict()

        name = tree.find(uri + "Name")
        fp = FilePath(os.path.dirname(name.text))

        id_group = tree.find(uri + "IdGroup")
        open_count = tree.find(uri + "OpenCount")
        edit_count = tree.find(uri + "EditCount")
        listen_count = tree.find(uri + "ListenCount")
        accepted = tree.find(uri + "Accepted")

        sub[name.tag] = name.text
        sub[id_group.tag] = id_group.text
        sub[open_count.tag] = open_count.text
        sub[edit_count.tag] = edit_count.text
        sub[listen_count.tag] = listen_count.text
        sub[accepted.tag] = accepted.text

        fp.subjoined = sub
        self.add(fp)

