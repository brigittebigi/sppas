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

    src.files.tests.test_filestructures.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import os
import sppas

from sppas import paths
from sppas.src.wkps.filebase import FileBase, States
from sppas.src.wkps.filestructure import FileName
from sppas.src.wkps.filestructure import FileRoot
from sppas.src.wkps.filestructure import FilePath
from sppas.src.wkps.sppasWorkspace import sppasWorkspace
from sppas.src.wkps.wkpexc import FileOSError, PathTypeError

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestFileBase(unittest.TestCase):

    def test_init(self):
        f = FileBase(__file__)
        self.assertEqual(__file__, f.get_id())
        self.assertEqual(__file__, f.id)
        self.assertEqual(States().UNUSED, f.get_state())

    # ----------------------------------------------------------------------------

    def test_overloads(self):
        f = FileBase(__file__)
        self.assertEqual(__file__, str(f))
        self.assertEqual(__file__, "{!s:s}".format(f))
        # TODO: Add real tests of FileBase

# ---------------------------------------------------------------------------


class TestFileName(unittest.TestCase):

    def test_init(self):
        # Attempt to instantiate with an unexisting file. Since SPPAS 2.9 it
        # was raising an exception. From SPPAS 3.0 its state is missing.
        fn = FileName("toto")
        self.assertEqual(fn.get_state(), States().MISSING)

        # Normal situation
        fn = FileName(__file__)
        self.assertEqual(__file__, fn.get_id())
        self.assertFalse(fn.state == States().CHECKED)

    # ----------------------------------------------------------------------------

    def test_extension(self):
        fn = FileName(__file__)
        self.assertEqual(".PY", fn.get_extension())

    # ----------------------------------------------------------------------------

    def test_mime(self):
        fn = FileName(__file__)
        self.assertIn(fn.get_mime(), ["text/x-python", "text/plain"])

    # ----------------------------------------------------------------------------

    def test_set_state(self):
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

    # ----------------------------------------------------------------------------

    def test_update_properties(self):
        # Properties were not changed
        fn = FileName(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))
        self.assertFalse(fn.update_properties())
        fn = FileName("toto")
        self.assertFalse(fn.update_properties())

        # Create a filename of a missing file, then create the file
        test_file = os.path.join(DATA, "testfile.txt")
        if os.path.exists(test_file):
            os.remove(test_file)
        fn = FileName(test_file)
        self.assertEqual(fn.state, States().MISSING)
        with open(test_file, "w") as f:
            f.write("this is a file to test filename update properties.")

        # File is not missing anymore: it exists
        self.assertTrue(fn.update_properties())
        self.assertEqual(fn.state, States().UNUSED)
        os.remove(test_file)

        # File is now missing (again)
        self.assertTrue(fn.update_properties())
        self.assertEqual(fn.state, States().MISSING)

# --------------------------------------------------------------------------------


class TestFileRoot(unittest.TestCase):

    def test_init(self):
        fr = FileRoot(__file__)
        root = __file__.replace('.py', '')
        self.assertEqual(root, fr.id)
        fr = FileRoot("toto")
        self.assertEqual("toto", fr.id)

    # ----------------------------------------------------------------------------

    def test_pattern(self):
        # Primary file
        self.assertEqual('', FileRoot.pattern('filename.wav'))

        # Annotated file (sppas or other...)
        self.assertEqual('-phon', FileRoot.pattern('filename-phon.xra'))
        self.assertEqual('-unk', FileRoot.pattern('filename-unk.xra'))

        # pattern is too short
        self.assertEqual("", FileRoot.pattern('F_F_B003-P8.xra'))

        # pattern is too long
        self.assertEqual("", FileRoot.pattern('F_F_B003-P1234567890123.xra'))

    # ----------------------------------------------------------------------------

    def test_root(self):
        self.assertEqual('filename', FileRoot.root('filename.wav'))
        self.assertEqual('filename', FileRoot.root('filename-phon.xra'))
        self.assertEqual('filename', FileRoot.root('filename-unk.xra'))
        self.assertEqual('filename_unk', FileRoot.root('filename_unk.xra'))
        self.assertEqual('filename-unk', FileRoot.root('filename-unk-unk.xra'))
        self.assertEqual('filename-unk_unk', FileRoot.root('filename-unk_unk.xra'))
        self.assertEqual('filename.unk', FileRoot.root('filename.unk-unk.xra'))
        self.assertEqual(
            'e:\\bigi\\__pycache__\\filedata.cpython-37',
            FileRoot.root('e:\\bigi\\__pycache__\\filedata.cpython-37.pyc'))

    # ----------------------------------------------------------------------------

    def test_set_state(self):
        root = __file__.replace('.py', '')
        fr = FileRoot(root)
        modified = fr.set_state(States().CHECKED)
        self.assertEqual(len(modified), 0)

        # testing with a FileRoot with files
        wkp = sppasWorkspace()
        wkp.add_file(__file__)

        for fp in wkp:
            for fr in fp:
                modified = fr.set_state(States().CHECKED)
                for fn in fp:
                    self.assertEqual(fn.state, States().CHECKED)
        self.assertGreater(len(modified), 0)

        for fp in wkp:
            for fr in fp:
                modified = fr.set_state(States().UNUSED)
                for fn in fp:
                    self.assertEqual(fn.state, States().UNUSED)
        self.assertGreater(len(modified), 0)

        for fp in wkp:
            for fr in fp:
                modified = fr.set_state(States().MISSING)
                for fn in fr:
                    self.assertNotEqual(fn.state, States().MISSING)
        self.assertEqual(len(modified), 0)

    # ----------------------------------------------------------------------------

    def test_update_state_with_missing(self):
        fr = FileRoot(os.path.join(sppas.paths.samples, "samples-pol", "0001"))
        fr.append(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))
        self.assertEqual(fr.state, States().UNUSED)
        self.assertFalse(fr.update_state())

        fr.append(os.path.join(sppas.paths.samples, "samples-pol", "0001missing.txt"))
        self.assertEqual(fr.state, States().UNUSED)

        fr.set_state(States().CHECKED)
        self.assertEqual(fr.state, States().AT_LEAST_ONE_CHECKED)

    # ----------------------------------------------------------------------------

    def test_update_state(self):
        fr = FileRoot(os.path.join(sppas.paths.samples, "samples-pol", "0001"))
        fr.append(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))
        self.assertEqual(fr.state, States().UNUSED)
        self.assertFalse(fr.update_state())

        fr.set_state(States().CHECKED)
        self.assertEqual(fr.get_state(), States().CHECKED)
        self.assertFalse(fr.update_state())
        self.assertEqual(fr.get_state(), States().CHECKED)

        for fn in fr:
            fn.set_state(States().UNUSED)
            self.assertTrue(fr.update_state())
            self.assertEqual(fr.get_state(), States().UNUSED)

            fn.set_state(States().MISSING)
            self.assertFalse(fr.update_state())
            self.assertEqual(fr.state, States().UNUSED)

    # -----------------------------------------------------------------------

    def test_append(self):
        fr = FileRoot(os.path.join(sppas.paths.samples, "samples-pol", "0001"))
        fn = FileName(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))

        # adding existing file
        fns = fr.append(fn)
        self.assertEqual(len(fns), 1)
        for f in fr:
            self.assertEqual(f, fn)

        # if file already in the list
        fns = fr.append(fn)
        self.assertEqual(len(fns), 0)

        fr.remove(fn)

        # unexisting file
        fn = FileName("toto")
        fns = fr.append(fn)
        self.assertEqual(len(fns), 1)
        for f in fr:
            self.assertEqual(f, fn)

# ---------------------------------------------------------------------------


class TestFilePath(unittest.TestCase):

    def test_init(self):
        # Attempt to instantiate with an unexisting file. Since SPPAS 2.9
        # it was raising FileOSError. Since SPPAS 3.0 its state is Missing.
        fp = FilePath("toto")
        self.assertEqual(fp.get_state(), States().MISSING)

        fp = FilePath("/toto")
        self.assertEqual(fp.state, States().MISSING)

        # Attempt to instantiate with a file.
        with self.assertRaises(PathTypeError):
            FilePath(__file__)

        # Normal situation
        d = os.path.dirname(__file__)
        fp = FilePath(d)
        self.assertEqual(d, fp.id)
        self.assertEqual(fp.state, States().UNUSED)
        self.assertEqual(fp.id, fp.get_id())

    # ----------------------------------------------------------------------------

    def test_append_remove(self):
        d = os.path.dirname(__file__)
        fp = FilePath(d)

        # Attempt to append an unexisting file
        with self.assertRaises(FileOSError):
            fp.append("toto")

        # Normal situation
        fns = fp.append(__file__)
        self.assertIsNotNone(fns)
        self.assertEqual(len(fns), 2)
        fr = fns[0]
        fn = fns[1]
        self.assertIsInstance(fr, FileRoot)
        self.assertIsInstance(fn, FileName)
        self.assertEqual(__file__, fn.id)

        fr = fp.get_root(FileRoot.root(fn.id))
        self.assertIsNotNone(fr)
        self.assertIsInstance(fr, FileRoot)
        self.assertEqual(FileRoot.root(__file__), fr.id)

        self.assertEqual(1, len(fp))
        self.assertEqual(1, len(fr))

        # Attempt to add again the same file
        fns2 = fp.append(__file__)
        self.assertIsNone(fns2)
        self.assertEqual(1, len(fp))

        fns3 = fp.append(FileName(__file__))
        self.assertIsNone(fns3)
        self.assertEqual(1, len(fp))

        # Remove the file from its name
        fp.remove(fp.get_root(FileRoot.root(__file__)))
        self.assertEqual(0, len(fp))

        # Append an instance of FileName
        fp = FilePath(d)

        fn = FileName(__file__)
        rfns = fp.append(fn)
        self.assertIsNotNone(rfns)
        self.assertEqual(fn, rfns[1])
        self.assertEqual(1, len(fp))

        # Attempt to add again the same file
        fp.append(FileName(__file__))
        self.assertEqual(1, len(fp))

        # Tests of remove (return an id or None)

        # Remove the whole root from a file
        root_to_remove = fp.get_root(fn.id).get_id()
        idr = fp.remove(fp.get_root(fn.id))
        self.assertEqual(0, len(fp))
        self.assertEqual(idr, root_to_remove)

        # Remove an un-existing file
        self.assertEqual(None, fp.remove("toto"))

        # Remove a file not in the list!
        i = fp.remove(FileName(__file__))
        self.assertEqual(None, i)

    # ----------------------------------------------------------------------------

    def test_append_with_brothers(self):
        d = os.path.dirname(__file__)

        # Normal situation (1)
        fp = FilePath(d)
        fns = fp.append(__file__, all_root=False)
        self.assertIsNotNone(fns)
        self.assertEqual(2, len(fns))
        self.assertEqual(FileRoot.root(__file__), fns[0].id)
        self.assertIsInstance(fns[0], FileRoot)
        self.assertIsInstance(fns[1], FileName)

        # Normal situation (2)
        fp = FilePath(d)
        fns = fp.append(__file__, all_root=True)
        self.assertIsNotNone(fns)
        self.assertEqual(2, len(fns))
        self.assertEqual(FileRoot.root(__file__), fns[0].id)
        self.assertIsInstance(fns[0], FileRoot)
        self.assertIsInstance(fns[1], FileName)

        # with brothers
        d = os.path.join(paths.samples, "samples-eng")
        fp = FilePath(d)
        fns = fp.append(os.path.join(d, "ENG_M15_ENG_T02.PitchTier"), all_root=True)
        self.assertIsNotNone(fns)
        self.assertEqual(1, len(fp))   # 1 root
        self.assertEqual(3, len(fns))   # root + .wav + .pitchtier
        self.assertIsInstance(fns[0], FileRoot)
        self.assertIsInstance(fns[1], FileName)
        self.assertIsInstance(fns[2], FileName)

    # ----------------------------------------------------------------------------

    def test_set_state(self):
        d = os.path.join(sppas.paths.samples, 'samples-pol')
        fp = FilePath(d)
        fp.append(os.path.join(d, '0001.txt'))
        s = States()

        modified = fp.set_state(States().CHECKED)
        self.assertGreater(len(modified), 0)
        self.assertEqual(fp.get_state(), s.CHECKED)
        for fr in fp:
            self.assertEqual(fr.state, s.CHECKED)
            for fn in fr:
                self.assertEqual(fn.get_state(), s.CHECKED)

        fp.set_state(States().UNUSED)
        self.assertEqual(s.UNUSED, fp.get_state())
        for fr in fp:
            self.assertEqual(s.UNUSED, fr.get_state())
            for fn in fr:
                self.assertEqual(s.UNUSED, fn.get_state())

        # Test of LOCKED state
        fp.set_state(States().LOCKED)
        self.assertEqual(s.LOCKED, fp.state)
        for fr in fp:
            self.assertEqual(fr.state, s.LOCKED)
            for fn in fr:
                self.assertEqual(fn.get_state(), s.LOCKED)

        fp.set_state(States().UNUSED)
        self.assertEqual(s.LOCKED, fp.state)
        # All unlocked files are checked
        fp.unlock()

        # Attempt to set to MISSING state but path is existing
        fp.set_state(States().MISSING)
        self.assertEqual(s.CHECKED, fp.state)

        f = FileName(os.path.join(d, 'missing.txt'))
        fp.append(f)
        self.assertEqual(s.MISSING, f.state)

    # ----------------------------------------------------------------------------

    def test_missing(self):
        missing_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "missing_dir")
        os.mkdir(missing_directory)
        fp = FilePath(missing_directory)
        self.assertEqual(States().UNUSED, fp.state)
        os.rmdir(missing_directory)
        fp.update_state()
        self.assertEqual(States().MISSING, fp.state)

        # Add files in the missing_dir...

        # Can't add an un-existing file name
        with self.assertRaises(FileOSError):
            fp.append("toto.wav")

        # Can add any FileName instance. It's state is MISSING.
        fn = FileName(os.path.join(missing_directory, "toto.wav"))
        fp.append(fn)

        print(fn.id)
        print(fp.id)

        for fr in fp:
            self.assertEqual(States().MISSING, fr.get_state())
            for fn in fr:
                self.assertEqual(States().MISSING, fn.get_state())

    # ----------------------------------------------------------------------------

    def test_update_state(self):
        fp = FilePath(os.path.join(sppas.paths.samples, "samples-pol"))
        fn = FileName(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))
        self.assertEqual(fp.get_state(), States().UNUSED)
        self.assertEqual(fn.get_state(), States().UNUSED)

        # append calls update_state()
        fp.append(fn)
        self.assertEqual(fp.get_state(), States().UNUSED)

        # if the state of its roots is  changed
        for fr in fp:
            fr.set_state(States().CHECKED)

        self.assertTrue(fp.update_state())
        self.assertEqual(fp.get_state(), States().CHECKED)

        fp.set_state(States().UNUSED)
        self.assertEqual(fp.get_state(), States().UNUSED)

        # nothing has changed
        self.assertFalse(fp.update_state())

        fp.set_state(States().CHECKED)
        self.assertEqual(fp.get_state(), States().CHECKED)

        for fr in fp:
            fr.set_state(States().UNUSED)
            self.assertTrue(fp.update_state())
            self.assertEqual(fr.get_state(), States().UNUSED)

        # if the filepath is missing updating has no effect
        fp.set_state(States().MISSING)
        self.assertFalse(fp.update_state())
        for fr in fp:
            fr.set_state(States().UNUSED)
        self.assertFalse(fp.update_state())







