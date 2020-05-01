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
from sppas.src.wkps.fileexc import FileOSError, FileTypeError, PathTypeError

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


# ---------------------------------------------------------------------------


class TestFileName(unittest.TestCase):

    def test_init(self):
        # Attempt to instantiate with an unexisting file
        with self.assertRaises(FileOSError):
            FileName("toto")

        # Attempt to instantiate with a directory
        with self.assertRaises(FileTypeError):
            FileName(os.path.dirname(__file__))

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
                    self.assertTrue(fn.get_state() is States().CHECKED)
                    fn.set_state(States().UNUSED)
                    self.assertTrue(fn.get_state() is States().UNUSED)
                    fn.set_state(States().MISSING)
                    self.assertTrue(fn.get_state() is States().MISSING)

    # ----------------------------------------------------------------------------

    def test_update_proprieties(self):
        fn = FileName(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))
        self.assertTrue(fn.update_properties())
        fn = FileName("toto")
        self.assertFalse(fn.update_properties())

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
                    self.assertTrue(fn.get_state() is States().CHECKED)
        self.assertTrue(len(modified) > 0)

        for fp in wkp:
            for fr in fp:
                modified = fr.set_state(States().UNUSED)
                for fn in fp:
                    self.assertTrue(fn.get_state() is States().UNUSED)
        self.assertTrue(len(modified) > 0)

        for fp in wkp:
            for fr in fp:
                modified = fr.set_state(States().MISSING)
                for fn in fr:
                    self.assertTrue(fn.get_state() is States().MISSING)
        self.assertTrue(len(modified) > 0)

    # ----------------------------------------------------------------------------

    def test_update_state(self):

        fr = FileRoot(os.path.join(sppas.paths.samples, "samples-pol", "0001"))
        fr.append(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))

        self.assertTrue(fr.get_state() is States().UNUSED)
        self.assertFalse(fr.update_state())

        self.assertEqual(fr.get_state(), States().UNUSED)
        fr.set_state(States().CHECKED)
        self.assertEqual(fr.get_state(), States().CHECKED)
        self.assertFalse(fr.update_state())
        self.assertEqual(fr.get_state(), States().CHECKED)

        for fn in fr:
            fn.set_state(States().UNUSED)
            self.assertTrue(fr.update_state())
            self.assertEqual(fr.get_state(), States().UNUSED)
            fn.set_state(States().MISSING)
            self.assertTrue(fr.update_state())
            self.assertEqual(fr.get_state(), States().MISSING)

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
        # Attempt to instantiate with an unexisting file
        with self.assertRaises(FileOSError):
            FilePath("toto")

        fp = FilePath("/toto")
        self.assertTrue(fp.state is States().MISSING)

        # Attempt to instantiate with a file
        with self.assertRaises(PathTypeError):
            FilePath(__file__)

        # Normal situation
        d = os.path.dirname(__file__)
        fp = FilePath(d)
        self.assertEqual(d, fp.id)
        self.assertFalse(fp.state is States().CHECKED)
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

        # Remove the file from its instance
        i = fp.remove(fp.get_root(fn.id))
        self.assertEqual(0, len(fp))
        self.assertEqual(i, 0)

        # Remove an un-existing file
        self.assertEqual(-1, fp.remove("toto"))

        # Remove a file not in the list!
        i = fp.remove(FileName(__file__))
        self.assertEqual(-1, i)

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
        fp = FilePath(d)
        fns = fp.append(os.path.join(paths.samples, "samples-eng", "ENG_M15_ENG_T02.PitchTier"), all_root=True)
        self.assertIsNotNone(fns)
        self.assertEqual(1, len(fp))   # 1 root
        self.assertEqual(3, len(fns))   # root + .wav + .pitchter
        self.assertIsInstance(fns[0], FileRoot)
        self.assertIsInstance(fns[1], FileName)
        self.assertIsInstance(fns[2], FileName)

    # ----------------------------------------------------------------------------

    def test_set_state(self):
        fp = FilePath(os.path.abspath(__file__))
        fp.append(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))

        modified = fp.set_state(States().CHECKED)
        self.assertTrue(len(modified) > 0)
        self.assertTrue(fp.get_state() is States().CHECKED)
        for fr in fp:
            self.assertTrue(fr.get_state() is States().CHECKED)
            self.assertFalse(fr.get_state() is States().UNUSED)
            for fn in fr:
                self.assertTrue(fn.get_state() is States().CHECKED)

        fp.set_state(States().UNUSED)
        self.assertTrue(fp.get_state() is States().UNUSED)
        for fr in fp:
            self.assertTrue(fr.get_state() is States().UNUSED)
            for fn in fr:
                self.assertTrue(fn.get_state() is States().UNUSED)

        fp.set_state(States().MISSING)
        self.assertTrue(fp.get_state() is States().MISSING)
        for fr in fp:
            self.assertTrue(fr.get_state() is States().MISSING)
            for fn in fr:
                self.assertTrue(fn.get_state() is States().MISSING)

    # ----------------------------------------------------------------------------

    def test_update_state(self):
        fp = FilePath(os.path.join(sppas.paths.samples, "samples-pol"))
        fn = FileName(os.path.join(sppas.paths.samples, "samples-pol", "0001.txt"))
        self.assertTrue(fp.get_state() is States().UNUSED)
        self.assertTrue(fn.get_state() is States().UNUSED)

        # append calls update_state()
        fp.append(fn)
        self.assertTrue(fp.get_state() is States().UNUSED)

        # if the state of its roots is  changed
        for fr in fp:
            fr.set_state(States().CHECKED)

        self.assertTrue(fp.update_state())
        self.assertTrue(fp.get_state() is States().CHECKED)

        fp.set_state(States().UNUSED)
        self.assertTrue(fp.get_state() is States().UNUSED)

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







