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

    wkps.wio.tests.test_wio_readwrite.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import sppas

import unittest
from sppas.src.wkps.wio.wkpreadwrite import sppasWkpRW
from sppas.src.wkps.wio.wjson import sppasWJSON
from sppas.src.wkps.fileref import FileReference, sppasAttribute
from sppas.src.wkps.wio.wannotationpro import sppasWANT

# ---------------------------------------------------------------------------


class testSppasWkpRW(unittest.TestCase):

    def setUp(self):
        self.rw = sppasWkpRW(os.path.join(sppas.paths.sppas, 'src', 'wkps', 'wio', 'tests', 'file.wjson'))
        self.wkp = sppasWJSON()
        self.r1 = FileReference("ref1")
        self.file = os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt')
        self.r1.append(sppasAttribute('initials', 'AB'))
        self.r1.append(sppasAttribute('sex', 'F'))
        self.att = sppasAttribute("att")

        self.rw2 = sppasWkpRW(os.path.join(sppas.paths.wkps, 'AnnotProWkp.antw'))
        self.want = sppasWANT()
    # -------------------------------------------------------------------------

    def test_extensions(self):
        a = self.rw.extensions()
        self.assertEqual(len(a), len(sppasWkpRW.WORKSPACE_TYPES))

    # -------------------------------------------------------------------------

    def test_read(self):
        # WJSON
        self.assertEqual(type(self.rw.read()), type(self.wkp))
        ws = self.rw.read()
        ws.add_ref(self.r1)
        self.wkp.add_ref(self.r1)
        self.assertEqual(ws.get_all_files(), self.wkp.get_all_files())
        self.assertEqual(type(ws), sppasWJSON)

        # WANT
        want = self.rw2.read()
        self.assertEqual(type(want), sppasWANT)

    # -------------------------------------------------------------------------

    def test_create_wkp_from_extension(self):
        self.assertEqual(type(self.rw.create_wkp_from_extension("test.wjson")), sppasWJSON)
        self.assertEqual(type(self.rw.create_wkp_from_extension("test.antw")), sppasWANT)

    # -------------------------------------------------------------------------

    def test_write(self):
        self.assertEqual(type(self.rw.read()), type(self.wkp))










