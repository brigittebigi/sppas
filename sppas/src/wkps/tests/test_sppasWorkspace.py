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

import sppas


from ..fileref import sppasAttribute, FileReference
from ..sppasWorkspace import sppasWorkspace
from ..filestructure import FileName, FileRoot
from ..filebase import States

# ----------------------------------------------------------------------------


class TestWorkspace(unittest.TestCase):

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

    # ---------------------------------------------------------------------------

    def test_init(self):
        data = sppasWorkspace()
        self.assertEqual(36, len(data.id))
        self.assertEqual(0, len(data))

    # ---------------------------------------------------------------------------

    def test_state(self):
        self.data.set_object_state(States().CHECKED)
        self.assertEqual(States().CHECKED, self.data[0].state)
        self.assertEqual(States().CHECKED, self.data[1].state)
        self.assertEqual(States().CHECKED, self.data[2].state)
        self.assertEqual(States().CHECKED, self.data[3].state)

    # ---------------------------------------------------------------------------

    def test_wrong_way_to_set_state(self):
        """This is exactly what We WILL NEVER DO."""
        wkp = sppasWorkspace()
        wkp.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        for fp in wkp:
            for fr in fp:
                for fn in fr:
                    fn.set_state(States().CHECKED)
                    self.assertEqual(fn.state, States().CHECKED)
                    fn.set_state(States().UNUSED)
                    self.assertEqual(fn.state, States().UNUSED)
                    # but... file is existing
                    fn.set_state(States().MISSING)
                    self.assertNotEqual(fn.state, States().MISSING)
                    fn.set_state(States().CHECKED)
                    self.assertEqual(fn.state, States().CHECKED)
        # ... BUT fp and fr were not updated! So our workspace is CORRUPTED.
        # WE EXPECT STATE OF FR AND FN TO BE **checked** AND THEY ARE NOT:
        for fp in wkp:
            self.assertEqual(fp.state, States().UNUSED)
            for fr in fp:
                self.assertEqual(fr.state, States().UNUSED)

    # ---------------------------------------------------------------------------

    def test_right_way_to_set_state(self):
        # USE THIS INSTEAD:
        wkp = sppasWorkspace()
        wkp.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        fn = wkp.get_object(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        wkp.set_object_state(States().CHECKED, fn)
        for fp in wkp:
            self.assertEqual(fp.state, States().CHECKED)
            for fr in fp:
                self.assertEqual(fr.state, States().CHECKED)

    # ---------------------------------------------------------------------------

    def test_lock_all(self):
        # Lock all files
        self.data.set_object_state(States().LOCKED)
        self.assertEqual(States().LOCKED, self.data[0].state)
        self.assertEqual(States().LOCKED, self.data[1].state)
        self.assertEqual(States().LOCKED, self.data[2].state)
        self.assertEqual(States().LOCKED, self.data[3].state)

        # as soon as a file is locked, the "set_object_state()" does not work anymore
        self.data.set_object_state(States().CHECKED)
        self.assertEqual(States().LOCKED, self.data[0].state)
        self.assertEqual(States().LOCKED, self.data[1].state)
        self.assertEqual(States().LOCKED, self.data[2].state)
        self.assertEqual(States().LOCKED, self.data[3].state)

        # only the unlock method has to be used to unlock files
        self.data.unlock()

    # ---------------------------------------------------------------------------

    def test_lock_filename(self):
        # Lock a single file
        filename = os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier')
        fn = self.data.get_object(filename)
        self.assertIsInstance(fn, FileName)
        self.data.set_object_state(States().LOCKED, fn)
        self.assertEqual(States().LOCKED, fn.state)

        self.assertEqual(States().UNUSED, self.data[0].state)
        self.assertEqual(States().AT_LEAST_ONE_LOCKED, self.data[1].state)

        # unlock a single file
        n = self.data.unlock([fn])
        self.assertEqual(1, n)
        self.assertEqual(States().CHECKED, fn.state)
        self.assertEqual(States().AT_LEAST_ONE_CHECKED, self.data[1].state)

    # ---------------------------------------------------------------------------

    def test_ref(self):
        self.data.add_ref(self.r1)
        self.assertEqual(1, len(self.data.get_refs()))
        self.data.add_ref(self.r2)
        self.assertEqual(2, len(self.data.get_refs()))
        self.r1.set_state(States().CHECKED)
        self.r2.set_state(States().CHECKED)
        self.data.remove_refs(States().CHECKED)
        self.assertEqual(0, len(self.data.get_refs()))

    # ---------------------------------------------------------------------------

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

    # ---------------------------------------------------------------------------

    def test_get_parent(self):
        filename = os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier')
        fr = self.data.get_object(FileRoot.root(filename))
        self.assertIsNotNone(fr)
        fn = self.data.get_object(filename)
        self.assertIsNotNone(fn)
        self.assertEqual(fr, self.data.get_parent(fn))
