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

import unittest
import sppas
import os
import json

from sppas.src.wkps.wio.wjson import sppasWJSON
from sppas.src.wkps.workspace import sppasWorkspace
from sppas.src.wkps.fileref import sppasCatReference, sppasRefAttribute
from sppas.src.wkps.filestructure import FilePath, FileName
from sppas.src.wkps.filebase import States
from sppas.src.wkps.wkpexc import FilesMatchingValueError

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestsppasWJSON(unittest.TestCase):

    def setUp(self):
        self.data = sppasWorkspace()
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        self.r1 = sppasCatReference('SpeakerAB')
        self.r1.set_type('SPEAKER')
        self.r1.append(sppasRefAttribute('initials', 'AB'))
        self.r1.append(sppasRefAttribute('sex', 'F'))
        self.att = sppasRefAttribute("att")
        self.data.add_ref(self.r1)

        self.wkpjson = sppasWJSON()
        self.file = os.path.join(DATA, 'file.wjson')

    # -----------------------------------------------------------------------

    def test_init(self):
        self.assertEqual(self.wkpjson.software, "SPPAS")
        self.assertEqual(self.wkpjson.default_extension, "wjson")

    # -----------------------------------------------------------------------

    def test_detect(self):
        self.assertFalse(self.wkpjson.detect(""))

    # -----------------------------------------------------------------------

    def test_set(self):
        data = sppasWorkspace()
        data.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        r1 = sppasCatReference('SpeakerAB')
        r1.set_type('SPEAKER')
        r1.append(sppasRefAttribute('initials', 'AB'))
        r1.append(sppasRefAttribute('sex', 'F'))
        data.add_ref(r1)

        wkpjson = sppasWJSON()
        wkpjson.set(data)

        self.assertEqual(data.get_id(), wkpjson.get_id())
        self.assertEqual(data.get_refs(), wkpjson.get_refs())
        self.assertEqual(data.get_paths(), wkpjson.get_paths())

    # -----------------------------------------------------------------------

    def test_serialize(self):
        data = sppasWJSON()
        data.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        r1 = sppasCatReference('SpeakerAB')
        r1.set_type('SPEAKER')
        r1.append(sppasRefAttribute('initials', 'AB'))
        r1.append(sppasRefAttribute('sex', 'F'))
        data.add_ref(r1)

        d = data._serialize()
        jsondata = json.dumps(d, indent=4, separators=(',', ': '))
        jsondict = json.loads(jsondata)
        self.assertEqual(d, jsondict)

    # -----------------------------------------------------------------------

    def test_read_write(self):
        data = sppasWJSON()
        data.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        r1 = sppasCatReference('SpeakerAB')
        r1.set_type('SPEAKER')
        r1.append(sppasRefAttribute('initials', 'AB'))
        r1.append(sppasRefAttribute('sex', 'F'))
        data.add_ref(r1)

        if os.path.exists(self.file):
            os.remove(self.file)
        data.write(self.file)
        self.assertTrue(os.path.exists(self.file))
        self.assertTrue(data.detect(self.file))

        read_data = sppasWJSON()
        read_data.read(self.file)
        os.remove(self.file)

        self.assertEqual(data.id, read_data.id)
        self.assertEqual(data.get_paths(), read_data.get_paths())
        self.assertEqual(data.get_refs(), read_data.get_refs())

    # -----------------------------------------------------------------------

    def test__serialize_ref(self):
        d = self.wkpjson._serialize_ref(self.r1)
        self.assertEqual(self.wkpjson._parse_ref(d), self.r1)

    # -----------------------------------------------------------------------

    def test__serialize_attributes(self):
        d = self.wkpjson._serialize_attributes(self.att)
        self.assertEqual(self.wkpjson._parse_attribute(d), self.att)

    # -----------------------------------------------------------------------

    def test__serialize_path(self):
        fp = FilePath(os.path.dirname(__file__))
        d = self.wkpjson._serialize_path(fp)
        self.assertEqual(self.wkpjson._parse_path(d, version=2), fp)

        # test the absolute path and the relative path
        self.assertEqual(d["id"], fp.get_id())
        self.assertEqual(d["rel"], os.path.relpath(fp.get_id()))

    # -----------------------------------------------------------------------

    def test__serialize_root(self):
        for fp in self.data.get_paths():
            for fr in fp:
                d = self.wkpjson._serialize_root(fr)
                self.assertEqual(self.wkpjson._parse_root(d, fp.get_id(), 2), fr)

    # -----------------------------------------------------------------------

    def test__serialize_file(self):
        for fp in self.data.get_paths():
            for fr in fp:
                for fn in fr:
                    d = self.wkpjson._serialize_files(fn)
                    self.assertEqual(self.wkpjson._parse_file(d, fp.get_id(), 2), fn)

    # -----------------------------------------------------------------------

    def test__parse(self):
        d = self.wkpjson._serialize()
        identifier = self.wkpjson._parse(d)
        self.assertEqual(identifier, self.wkpjson.get_id())

    # -----------------------------------------------------------------------

    def test__parse_path(self):
        p = os.path.join(sppas.paths.samples, 'samples-pol')
        fp = FilePath(p)
        d = self.wkpjson._serialize_path(fp)
        new_path = self.wkpjson._parse_path(d, 2)
        fn = FileName(os.path.join(p, '0001.txt'))
        new_path.append(fn)
        self.assertEqual(new_path, fp)
        self.assertEqual(d["id"], new_path.get_id())
        self.assertEqual(d["rel"], os.path.relpath(new_path.get_id()))
        self.assertEqual(new_path.get_state(), States().UNUSED)

        # wrong absolute and right relative path
        fp = FilePath("/toto/samples-pol")
        d = self.wkpjson._serialize_path(fp)
        # setting the relative path to an existing one
        d["rel"] = os.path.relpath(os.path.dirname(__file__))

        new_path = self.wkpjson._parse_path(d, 2)
        self.assertEqual(new_path.get_id(), os.path.abspath(d["rel"]))

        # path changed so we can't add with the old path name
        fn = FileName(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        with self.assertRaises(FilesMatchingValueError):
            new_path.append(fn)

        self.assertNotEqual(new_path.get_state(), States().MISSING)
        self.assertNotEqual(new_path.get_state(), States().CHECKED)
        self.assertEqual(new_path.get_state(), States().UNUSED)

        # wrong abspath, relpath
        fp = FilePath("/toto/samples-pol")
        d = self.wkpjson._serialize_path(fp)
        new_path = self.wkpjson._parse_path(d, 2)
        self.assertEqual(new_path.get_state(), States().MISSING)

        with self.assertRaises(FilesMatchingValueError):
            fn = FileName(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
            new_path.append(fn)

        self.assertEqual(fp, new_path)
        self.assertEqual(new_path.get_id(), d["id"])
        self.assertEqual(new_path.get_state(), States().MISSING)

    # ---------------------------------------------------------------------

    def test__parse_root(self):
        for fp in self.data.get_paths():
            for fr in fp:
                d = self.wkpjson._serialize_root(fr)
                self.assertEqual(self.wkpjson._parse_root(d, fp.get_id(), 2), fr)

    # -----------------------------------------------------------------------

    def test__parse_file(self):
        for fp in self.data.get_paths():
            for fr in fp:
                for fn in fr:
                    d = self.wkpjson._serialize_files(fn)
                    self.assertEqual(self.wkpjson._parse_file(d, fp.get_id(), 2), fn)

    # -----------------------------------------------------------------------

    def test__parse_ref(self):
        d = self.wkpjson._serialize_ref(self.r1)
        dd = self.wkpjson._parse_ref(d)
        for att1, att2 in zip(self.r1, dd):
            self.assertEqual(att1, att2)
        self.assertEqual(dd, self.r1)

    # -----------------------------------------------------------------------

    def test__parse_attributes(self):
        d = self.wkpjson._serialize_attributes(self.att)
        dd = self.wkpjson._parse_attribute(d)
        self.assertEqual(self.att.get_id(), dd.get_id())
        self.assertEqual(self.att.get_typed_value(), dd.get_typed_value())
        self.assertEqual(self.att.get_description(), dd.get_description())
        self.assertEqual(dd, self.att)


