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

    wkps.wio.tests.test_wioWJSON.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os
import unittest
import xml.etree.cElementTree as ET
import sppas

from sppas.src.wkps.wio.wannotationpro import sppasWANT
from sppas.src.wkps.filestructure import FileName

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# All the files contained in data folder must be moved in the workspace folder
# in order to run the tests
# ---------------------------------------------------------------------------


class TestsppasWANT(unittest.TestCase):

    def setUp(self):
        self.antw = sppasWANT("ant")

    # -----------------------------------------------------------------------

    def test_init(self):
        self.assertEqual(self.antw.default_extension, "antw")
        self.assertEqual(self.antw.software, "Annotation Pro")

    # -----------------------------------------------------------------------

    def test_detect(self):
        self.assertFalse(self.antw.detect(os.path.join(DATA, "save.json")))
        self.assertTrue(self.antw.detect(os.path.join(DATA, "AnnotProWkp.antw")))

    # -----------------------------------------------------------------------

    def test_read(self):
        self.antw.read(os.path.join(sppas.paths.wkps, "apWkp.antw"))

        # apWkp.antw contains two files
        fname1 = FileName(os.path.join(sppas.paths.wkps, "annprowkp.ant"))
        fname2 = FileName(os.path.join(sppas.paths.wkps, "annprowkp1.ant"))

        for fp in self.antw.get_all_files():
            for fr in fp:
                for fn in fr:
                    self.assertTrue(fn in [fname1, fname2])
                    # subjoined must contain the 7 nodes of a annotation pro workspace
                    self.assertEqual(len(fn.subjoined), 7)

    # -----------------------------------------------------------------------

    def test_write(self):
        fn = self.antw.read(os.path.join(sppas.paths.wkps, "apWkp.antw"))

        self.antw.add_file(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))
        self.antw.add_file(os.path.join(sppas.paths.samples, "samples-pol", "0001.wav"))

        self.antw.write(os.path.join(sppas.paths.wkps, "testapro.antw"))

        fname = self.antw.read(os.path.join(sppas.paths.wkps, "testapro.antw"))
        self.assertEqual(fn, fname)

    # -----------------------------------------------------------------------

    def test_serialize(self):
        fn = FileName(os.path.join(sppas.paths.wkps, "annprowkp.ant"))

        # dictionary with information that an annotation pro workspace could contain
        sub = {
            "{http://tempuri.org/WorkspaceDataSet.xsd}Id": "b1b36c56-652c-4390-81ce-8eabd4b0260f",
            "{http://tempuri.org/WorkspaceDataSet.xsd}IdGroup": "00000000-0000-0000-0000-000000000000",
            "{http://tempuri.org/WorkspaceDataSet.xsd}Name": "annprowkp.ant",
            "{http://tempuri.org/WorkspaceDataSet.xsd}OpenCount": "0",
            "{http://tempuri.org/WorkspaceDataSet.xsd}EditCount": "4",
            "{http://tempuri.org/WorkspaceDataSet.xsd}ListenCount": "5",
            "{http://tempuri.org/WorkspaceDataSet.xsd}Accepted": "false"
        }

        fn.subjoined = sub

        workspace_item = ET.Element("WorkspaceItem")
        child = self.antw._serialize(fn, workspace_item, "{http://tempuri.org/WorkspaceDataSet.xsd}")
        self.assertEqual(self.antw._parse(child), fn)

        # verifying if the tree contains all the wkp information
        for elem in child:
            self.assertTrue(elem.text in sub.values())

    # -----------------------------------------------------------------------

    def test_parse(self):

        # Creating a tree that could be in a antw file
        root = ET.Element("WorkspaceItem")

        child_id = ET.SubElement(root, "Id")
        child_id.text = "1"

        child_group = ET.SubElement(root, "IdGroup")
        child_group.text = "2"

        # Name
        child_name = ET.SubElement(root, "Name")
        child_name.text = "apWkp.antw"

        # OpenCount
        child_open_count = ET.SubElement(root, "OpenCount")
        child_open_count.text = "35"

        # EditCount
        child_edit_count = ET.SubElement(root, "EditCount")
        child_edit_count.text = "97"

        # ListenCount
        child_listen_count = ET.SubElement(root, "ListenCount")
        child_listen_count.text = "66"

        # Accepted
        child_accepted = ET.SubElement(root, "Accepted")
        child_accepted.text = "false"

        fn = FileName(os.path.join(sppas.paths.wkps, "apWkp.antw"))

        fname = self.antw._parse(root)
        self.assertEqual(fn, fname)

        # verifying if the parsed filename contains all the information
        self.assertEqual(fname.subjoined.get("Id"), child_id.text)
        self.assertEqual(fname.subjoined.get("IdGroup"), child_group.text)
        self.assertEqual(fname.subjoined.get("Name"), child_name.text)
        self.assertEqual(fname.subjoined.get("OpenCount"), child_open_count.text)
        self.assertEqual(fname.subjoined.get("EditCount"), child_edit_count.text)
        self.assertEqual(fname.subjoined.get("ListenCount"), child_listen_count.text)
        self.assertEqual(fname.subjoined.get("Accepted"), child_accepted.text)










