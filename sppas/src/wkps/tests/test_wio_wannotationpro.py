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

from sppas.src.wkps.wio.wannotationpro import sppasWANT
from sppas.src.wkps.filestructure import FilePath

# ---------------------------------------------------------------------------


class TestsppasWANT(unittest.TestCase):

    def setUp(self):
        self.antw = sppasWANT("jul")

    # -----------------------------------------------------------------------

    def test_init(self):
        self.assertEqual(self.antw.default_extension, "antw")
        self.assertEqual(self.antw.software, "Annotation Pro")

    # -----------------------------------------------------------------------

    def test_detect(self):
        self.assertFalse(self.antw.detect("./save.json"))
        self.assertTrue(self.antw.detect("./AnnotProWkp.antw"))

    # -----------------------------------------------------------------------

    def test_serialize(self):
        jul = sppasWANT()
        fp = FilePath("annotpro.ws")

        sub = dict()
        id_group = "IdGroup"
        open_count = "OpenCount"
        edit_count = "EditCount"
        listen_count = "ListenCount"
        accepted = "Accepted"

        sub["id_group"] = id_group
        sub["open_count"] = open_count
        sub["listen_count"] = listen_count
        sub["edit_count"] = edit_count
        sub["accepted"] = accepted

        fp.subjoined = sub
        jul.add(fp)

        root = ET.Element("WorkspaceDataSet")
        root.set("xmlns", "http://tempuri.org/WorkspaceDataSet.xsd")

        test = jul._serialize(root)

        for elem in test.iter():
            print(elem)

    # -----------------------------------------------------------------------

    def test_read(self):
        fp = FilePath(os.path.dirname("annprowkpa.ant"))
        fpath = self.antw.read("./AnnotProWkp.antw")

        sub = ["b1b36c56-652c-4390-81ce-8eabd4b0260f", "00000000-0000-0000-0000-000000000000",
               "0", "4", "5", "false"]

        # read return the right FilePath
        self.assertEqual(fp, fpath)

        # read fill the sppasWANT instance with the filepath
        self.assertTrue(fp in self.antw.get_all_files())

        for fp in self.antw.get_all_files():
            self.assertTrue(type(fp.subjoined) is dict)
            for value in fp.subjoined.values():
                self.assertTrue(value in sub)

    # -----------------------------------------------------------------------

    def test_write(self):
        fp = self.antw.read("./AnnotProWkp.antw")
        self.antw.write("./testapro.antw")
        fpath = self.antw.read("./testapro.antw")
        self.assertEqual(fp, fpath)

    # -----------------------------------------------------------------------







