# -*- coding:utf-8 -*-
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

    src.files.tests.test_sppasWorkspace.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os
import json

import sppas
from sppas import sppasTypeError, u
from ..fileref import sppasAttribute, FileReference
from ..sppasWorkspace import sppasWorkspace
from ..filestructure import FileName
from ..filebase import States

# ---------------------------------------------------------------------------


class TestsppasAttribute(unittest.TestCase):

    def setUp(self):
        self.valint = sppasAttribute('age', '12', 'int', 'speaker\'s age')
        self.valfloat = sppasAttribute('freq', '0.002', 'float', 'word appearance frequency')
        self.valbool = sppasAttribute('adult', 'false', 'bool', 'speaker is minor')
        self.valstr = sppasAttribute('utf', 'Hi everyone !', None, u('первый токен'))

    def testInt(self):
        self.assertTrue(isinstance(self.valint.get_typed_value(), int))
        self.assertEqual('12', self.valint.get_value())

    def testFloat(self):
        self.assertTrue(isinstance(self.valfloat.get_typed_value(), float))
        self.assertNotEqual(0.002, self.valfloat.get_value())

    def testBool(self):
        self.assertFalse(self.valbool.get_typed_value())

    def testStr(self):
        self.assertEqual('Hi everyone !', self.valstr.get_typed_value())
        self.assertEqual('Hi everyone !', self.valstr.get_value())

    def testRepr(self):
        self.assertEqual(u('age, 12, speaker\'s age'), str(self.valint))

    def testSetTypeValue(self):
        with self.assertRaises(sppasTypeError) as error:
            self.valbool.set_value_type('sppasAttribute')

        self.assertTrue(isinstance(error.exception, sppasTypeError))

    def testGetValuetype(self):
        self.assertEqual('str', self.valstr.get_value_type())

# ---------------------------------------------------------------------------


class TestReferences(unittest.TestCase):

    def setUp(self):
        self.micros = FileReference('microphone')
        self.att = sppasAttribute('mic1', 'Bird UM1', None, '最初のインタビューで使えていましたマイク')
        self.micros.append(self.att)
        self.micros.add('mic2', 'AKG D5')

    def testGetItem(self):
        self.assertEqual(u('最初のインタビューで使えていましたマイク'),
                         self.micros.att('mic1').get_description())

    def testsppasAttribute(self):
        self.assertFalse(isinstance(self.micros.att('mic2').get_typed_value(), int))

    def testAddKey(self):
        with self.assertRaises(ValueError) as AsciiError:
            self.micros.add('i', 'Blue Yeti')

        self.assertTrue(isinstance(AsciiError.exception, ValueError))

    def testPopKey(self):
        self.micros.pop('mic1')
        self.assertEqual(1, len(self.micros))
        self.micros.append(self.att)
        self.micros.pop(self.att)
        self.assertEqual(1, len(self.micros))

# ----------------------------------------------------------------------------


class TestsppasWorkspace(unittest.TestCase):

    def setUp(self):
        self.data = sppasWorkspace()
        self.data.add_file(__file__)
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.TextGrid'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-jpn', 'JPA_M16_JPA_T02.TextGrid'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-cat', 'TB-FE1-H1_phrase1.TextGrid'))

        self.r1 = FileReference('SpeakerAB')
        self.r1.set_type('SPEAKER')
        self.r1.append(sppasAttribute('initials', 'AB'))
        self.r1.append(sppasAttribute('sex', 'F'))
        self.r2 = FileReference('SpeakerCM')
        self.r2.set_type('SPEAKER')
        self.r2.append(sppasAttribute('initials', 'CM'))
        self.r2.append(sppasAttribute('sex', 'F'))
        self.r3 = FileReference('Dialog1')
        self.r3.set_type('INTERACTION')
        self.r3.append(sppasAttribute('when', '2003', 'int', 'Year of recording'))
        self.r3.append(sppasAttribute('where', 'Aix-en-Provence', descr='Place of recording'))

    def test_init(self):
        data = sppasWorkspace()
        self.assertEqual(36, len(data.id))
        self.assertEqual(0, len(data))

    # outdated
    def test_save(self):
        self.data.add_ref(self.r1)
        self.data.add_ref(self.r2)
        self.data.add_ref(self.r3)
        current_file_list = list()
        saved_file_list = list()
        self.data.save(os.path.join(sppas.paths.sppas, 'src', 'wkps', 'tests', 'save.json'))
        for fp in self.data:
            for fr in fp:
                for fn in fr:
                    current_file_list.append(fn)

        data = sppasWorkspace.load(os.path.join(sppas.paths.sppas, 'src', 'wkps', 'tests', 'save.json'))
        for fp in data:
            for fr in fp:
                for fn in fr:
                    saved_file_list.append(fn)
        self.assertEqual(len(current_file_list), len(saved_file_list))
        for f1, f2 in zip(current_file_list, saved_file_list):
            self.assertEqual(f1, f2)

    def test_state(self):
        self.data.set_object_state(States().CHECKED)
        self.assertEqual(States().CHECKED, self.data.get_object_state(self.data[0]))
        self.assertEqual(States().CHECKED, self.data.get_object_state(self.data[1]))
        self.assertEqual(States().CHECKED, self.data.get_object_state(self.data[2]))
        self.assertEqual(States().CHECKED, self.data.get_object_state(self.data[3]))

    def test_lock_all(self):
        # Lock all files
        self.data.set_object_state(States().LOCKED)
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[0]))
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[1]))
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[2]))
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[3]))

        # as soon as a file is locked, the "set_object_state()" does not work anymore
        self.data.set_object_state(States().CHECKED)
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[0]))
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[1]))
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[2]))
        self.assertEqual(States().LOCKED, self.data.get_object_state(self.data[3]))

        # only the unlock method has to be used to unlock files
        self.data.unlock()

    def test_lock_filename(self):

        # Lock a single file
        filename = os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier')
        fn = self.data.get_object(filename)
        self.assertIsInstance(fn, FileName)
        self.data.set_object_state(States().LOCKED, fn)
        self.assertEqual(States().LOCKED, self.data.get_object_state(fn))

        self.assertEqual(States().UNUSED, self.data.get_object_state(self.data[0]))
        self.assertEqual(States().AT_LEAST_ONE_LOCKED, self.data.get_object_state(self.data[1]))

        # unlock a single file
        n = self.data.unlock([fn])
        self.assertEqual(1, n)
        self.assertEqual(States().CHECKED, self.data.get_object_state(fn))
        self.assertEqual(States().AT_LEAST_ONE_CHECKED, self.data.get_object_state(self.data[1]))

    def test_ref(self):
        self.data.add_ref(self.r1)
        self.assertEqual(1, len(self.data.get_refs()))
        self.data.add_ref(self.r2)
        self.assertEqual(2, len(self.data.get_refs()))
        self.r1.set_state(States().CHECKED)
        self.r2.set_state(States().CHECKED)
        self.data.remove_refs(States().CHECKED)
        self.assertEqual(0, len(self.data.get_refs()))

    def test_assocations(self):
        self.data.add_ref(self.r1)
        self.data.set_object_state(States().CHECKED)

        for ref in self.data.get_refs():
            self.data.set_object_state(States().CHECKED, ref)

        self.data.associate()

        for fp in self.data:
            for fr in fp:
                self.assertTrue(self.r1 in fr.get_references())

        self.data.dissociate()

        for fp in self.data:
            for fr in fp:
                self.assertEqual(0, len(fr.get_references()))

    def test_serialize(self):
        d = self.data.serialize()
        jsondata = json.dumps(d, indent=4, separators=(',', ': '))
        jsondict = json.loads(jsondata)
        self.assertEqual(d, jsondict)

    def test_parse(self):
        self.data.add_ref(self.r1)
        self.data.add_ref(self.r2)
        self.data.add_ref(self.r3)
        d = self.data.serialize()
        data = self.data.parse(d)
        self.assertEqual(len(data), len(self.data))
        self.assertEqual(len(data.get_refs()), len(self.data.get_refs()))
        dd = data.serialize()
        self.assertEqual(d, dd)
