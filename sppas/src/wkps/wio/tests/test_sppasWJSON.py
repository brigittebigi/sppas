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

    wkps.wio.tests.test_sppasWJSON.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import sppas
import os
import json

from ..sppasWJSON import sppasWJSON
from sppas.src.wkps.sppasWorkspace import sppasWorkspace
from sppas.src.wkps.fileref import FileReference, sppasAttribute
from sppas.src.wkps.filestructure import FilePath

# ---------------------------------------------------------------------------


class TestsppasWJSON(unittest.TestCase):

    def setUp(self):
        self.data = sppasWorkspace()
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        self.r1 = FileReference('SpeakerAB')
        self.r1.set_type('SPEAKER')
        self.r1.append(sppasAttribute('initials', 'AB'))
        self.r1.append(sppasAttribute('sex', 'F'))
        self.att = sppasAttribute("att")

        self.parser = sppasWJSON()
        self.file = os.path.join(sppas.paths.sppas, 'src', 'wkps', 'wio', 'tests', 'file.wjson')

    # -----------------------------------------------------------------------

    def test_init(self):
        self.assertEqual(self.parser.software, "SPPAS")
        self.assertEqual(self.parser.default_extension, "wjson")

    # -----------------------------------------------------------------------

    def test_detect(self):
        self.assertFalse(self.parser.detect(""))
        self.assertTrue(self.parser.detect(self.file))

    # -----------------------------------------------------------------------

    def test_read(self):
        with open(self.file, 'r') as f:
            d = json.load(f)
        self.assertEqual(self.parser.read(self.file), self.parser._parse(d))

    # -----------------------------------------------------------------------

    def test_write(self):
        with open(self.file, 'w') as f:
            d = json.dump(self.parser._serialize(), f, indent=4, separators=(',', ': '))

        self.assertEqual(self.parser.write(self.file), d)

    # -----------------------------------------------------------------------

    def test__serialize(self):
        d = self.parser._serialize()
        jsondata = json.dumps(d, indent=4, separators=(',', ': '))
        jsondict = json.loads(jsondata)
        self.assertEqual(d, jsondict)

    # -----------------------------------------------------------------------

    def test__serialize_ref(self):
        d = self.parser._serialize_ref(self.r1)
        self.assertEqual(self.parser._parse_ref(d), self.r1)

    # -----------------------------------------------------------------------

    def test__serialize_attributes(self):
        d = self.parser._serialize_attributes(self.att)
        self.assertEqual(self.parser._parse_attribute(d), self.att)

    # -----------------------------------------------------------------------

    def test__serialize_path(self):
        for fp in self.data:
            d = self.parser._serialize_path(fp)
            self.assertEqual(self.parser._parse_path(d), fp)

    # -----------------------------------------------------------------------

    def test__serialize_root(self):
        for fp in self.data:
            for fr in fp:
                d = self.parser._serialize_root(fr)
                self.assertEqual(self.parser._parse_root(d, fp.get_id()), fr)

    # -----------------------------------------------------------------------

    def test_serialize_file(self):
        for fp in self.data:
            for fr in fp:
                for fn in fr:
                    d = self.parser._serialize_files(fn)
                    self.assertEqual(self.parser._parse_file(d, fp.get_id()), fn)

    # -----------------------------------------------------------------------

    def test__parse(self):
        d = self.parser._serialize()
        identifier = self.parser._parse(d)
        self.assertEqual(identifier, self.parser.get_id())

    # -----------------------------------------------------------------------

    def test__parse_ref(self):
        d = self.parser._serialize_ref(self.r1)
        self.assertEqual(self.parser._parse_ref(d), self.r1)

    # -----------------------------------------------------------------------

    def test__parse_path(self):
        for fp in self.data:
            d = self.parser._serialize_path(fp)
            self.assertEqual(self.parser._parse_path(d), fp)

    # -----------------------------------------------------------------------

    def test__parse_root(self):
        for fp in self.data:
            for fr in fp:
                d = self.parser._serialize_root(fr)
                self.assertEqual(self.parser._parse_root(d, fp.get_id()), fr)

    # -----------------------------------------------------------------------

    def test__parse_file(self):
        for fp in self.data:
            for fr in fp:
                for fn in fr:
                    print(fn)
                    d = self.parser._serialize_files(fn)
                    self.assertEqual(self.parser._parse_file(d, fp.get_id()), fn)

    # -----------------------------------------------------------------------

    def test__parse_attributes(self):
        d = self.parser._serialize_attributes(self.att)
        self.assertEqual(self.parser._parse_attribute(d), self.att)


