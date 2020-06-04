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

    An AnnotationPro workspace (antw) is an xml file

    Here is an example of a very simple antw file

    <?xml version="1.0" standalone="yes"?>
    <WorkspaceDataSet xmlns="http://tempuri.org/WorkspaceDataSet.xsd">
      <WorkspaceItem>
        <Id>b1b36c56-652c-4390-81ce-8eabd4b0260f</Id>
        <IdGroup>00000000-0000-0000-0000-000000000000</IdGroup>
        <Name>annprows.ant</Name>
        <OpenCount>0</OpenCount>
        <EditCount>4</EditCount>
        <ListenCount>5</ListenCount>
        <Accepted>false</Accepted>
      </WorkspaceItem>
    </WorkspaceDataSet>

    <WorkspaceItem /> correspond to a file
    <Name /> is the name of the said file

    each filename of the workspace got an id <Id />
    a group id <idGroup />
    and some information about the edition of the file
    how many times it has been opened <OpenCount />,
    how many editions (adding segment, layer, meta...
    each char typed count as an edition) <EditCount />
    how many times it has been listened (played) <ListenCount />
    <Accepted/> ?

"""
import os
import sppas
import xml.etree.cElementTree as ET

from sppas.src.config import sg

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
        """Check whether a file is of antw format or not.

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
        """Read a antw file and fill the sppasWANT instance.

        :param filename: (str)

        """
        if os.path.isfile(filename) is False:
            raise FileOSError(filename)
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            # uri looks like this "http://tempuri.org/WorkspaceDataSet.xsd"
            uri = root.tag[:root.tag.index('}')+1]

            # parsing each file contained in the antw
            for workspaceItem in tree.iter(tag=uri + "WorkspaceItem"):
                self._parse(workspaceItem, uri)
        # TODO RAISE PROPER EXCEPTIONS
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

        # serializing the elements saved in subjoined in the FileName instance
        for fp in self.get_paths():
            for fr in fp:
                for fn in fr:
                    workspace_item = ET.SubElement(root, "WorkspaceItem")
                    self._serialize(fn, workspace_item, uri)

        sppasWANT.indent(root)
        tree = ET.ElementTree(root)
        tree.write(filename,
                   encoding=sg.__encoding__,
                   xml_declaration=True,
                   method="xml")

    # -------------------------------------------------------------------------

    @staticmethod
    def _serialize(fn, workspace_item, uri=""):
        """Convert a FileName into a serializable structure.

        :param fn: (FileName) FileName we want to serialize
        :workspace_item: (ElementTree.Element) Element in which we are going
        to serialize the data
        :param uri: (str)
        :returns: (Element) a tree element that can be serialized

        """
        sub = fn.subjoined

        # we create a sub element in  workspace_item and we add the data
        # kept in subjoined

        # Id
        child_id = ET.SubElement(workspace_item, "Id")
        # IdGroup
        child_id_group = ET.SubElement(workspace_item, "IdGroup")
        # Name
        child_name = ET.SubElement(workspace_item, "Name")
        # OpenCount
        child_open_count = ET.SubElement(workspace_item, "OpenCount")
        # EditCount
        child_edit_count = ET.SubElement(workspace_item, "EditCount")
        # ListenCount
        child_listen_count = ET.SubElement(workspace_item, "ListenCount")
        # Accepted
        child_accepted = ET.SubElement(workspace_item, "Accepted")

        # if sub is not none it means that the file has been edited in
        # AnnotationPro already
        if sub is not None:
            child_id.text = sub[uri + "Id"]
            child_id_group.text = sub[uri + "IdGroup"]
            child_name.text = sub[uri + "Name"]
            child_open_count.text = sub[uri + "OpenCount"]
            child_edit_count.text = sub[uri + "EditCount"]
            child_listen_count.text = sub[uri + "ListenCount"]
            child_accepted.text = sub[uri + "Accepted"]
        else:
            # if we added the file from sppas subjoined will be empty
            # so we add manually the information
            child_id.text = "0"
            child_id_group.text = "0"
            child_name.text = os.path.basename(fn.get_id())
            child_open_count.text = "0"
            child_edit_count.text = "0"
            child_listen_count.text = "0"
            child_accepted.text = "false"

        return workspace_item

    # -------------------------------------------------------------------------

    def _parse(self, tree, uri=""):
        """Fill the data of a sppasWANT reader with a tree.

        :param tree: (ElementTree) tree to parse
        :param uri: (str)
        :returns: (FileName)

        """

        # as the antw file contains only the filename + ext and not the path
        # all the files that are going to be parsed must be contained in  the
        # workspace folder otherwise we can't locate it on the computer

        # the name contained in the .want file is the the filename + ext
        name = tree.find(uri + "Name")
        self.add_file(os.path.abspath(os.path.join(sppas.paths.wkps, name.text)))

        # getting the filename object that we added
        fn = self.get_object(os.path.abspath(os.path.join(sppas.paths.wkps, name.text)))

        # parsing the tree
        # ----------------

        identifier = tree.find(uri + "Id")
        id_group = tree.find(uri + "IdGroup")
        open_count = tree.find(uri + "OpenCount")
        edit_count = tree.find(uri + "EditCount")
        listen_count = tree.find(uri + "ListenCount")
        accepted = tree.find(uri + "Accepted")

        sub = dict()
        # adding the information contained in the tree in a dictionary
        # using their tag as the key
        # a tag looks like this : {http://tempuri.org/WorkspaceDataSet.xsd}Id
        sub[identifier.tag] = identifier.text
        sub[name.tag] = name.text
        sub[id_group.tag] = id_group.text
        sub[open_count.tag] = open_count.text
        sub[edit_count.tag] = edit_count.text
        sub[listen_count.tag] = listen_count.text
        sub[accepted.tag] = accepted.text

        # we add the information of the filename in the subjoined member
        fn.subjoined = sub

        return fn

