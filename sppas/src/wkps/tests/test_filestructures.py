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

from sppas import paths
from sppas.src.wkps.filebase import FileBase, States
from sppas.src.wkps.filestructure import FileName
from sppas.src.wkps.filestructure import FileRoot
from sppas.src.wkps.filestructure import FilePath

from sppas.src.files.fileexc import FileOSError, FileTypeError, PathTypeError, FileLockedError

# ---------------------------------------------------------------------------


class TestFileBase(unittest.TestCase):

    def test_init(self):
        f = FileBase(__file__)
        self.assertEqual(__file__, f.get_id())
        self.assertEqual(__file__, f.id)
        self.assertEqual(States().UNUSED, f.get_state())

    def test_overloads(self):
        f = FileBase(__file__)
        self.assertEqual(__file__, str(f))
        self.assertEqual(__file__, "{!s:s}".format(f))

    def test_serialize(self):
        fn = FileName(__file__)
        d = fn.serialize()
        self.assertEqual(d['id'], fn.id)
        self.assertEqual(0, d['state'])

        fn.set_state(States().CHECKED)
        d = fn.serialize()
        self.assertEqual(1, d['state'])

        fn.set_state(States().LOCKED)
        d = fn.serialize()
        self.assertEqual(2, d['state'])

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

    def test_extension(self):
        fn = FileName(__file__)
        self.assertEqual(".PY", fn.get_extension())

    def test_mime(self):
        fn = FileName(__file__)
        self.assertIn(fn.get_mime(), ["text/x-python", "text/plain"])

    def test_parse(self):
        d = {'id': __file__, 'state': 0}
        fn = FileName.parse(d)
        self.assertEqual(d['id'], fn.id)
        self.assertEqual(0, int(fn.get_state()))

        d = {'id': __file__, 'state': 1}
        fn = FileName.parse(d)
        self.assertEqual(d['id'], fn.id)
        self.assertEqual(1, int(fn.get_state()))

        d = {'id': __file__, 'state': 2}
        fn = FileName.parse(d)
        self.assertEqual(d['id'], fn.id)
        self.assertEqual(1, int(fn.get_state()))

# ---------------------------------------------------------------------------


class TestFileRoot(unittest.TestCase):

    def test_init(self):
        fr = FileRoot(__file__)
        root = __file__.replace('.py', '')
        self.assertEqual(root, fr.id)
        fr = FileRoot("toto")
        self.assertEqual("toto", fr.id)

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

    def test_serialize(self):
        fr = FileRoot(__file__)
        d = fr.serialize()
        self.assertEqual(d['id'], fr.id)
        self.assertEqual(list(), d['files'])
        self.assertEqual(list(), d['refids'])

        fr.append(__file__)
        d = fr.serialize()
        self.assertEqual([FileName(__file__).serialize()], d['files'])


# ---------------------------------------------------------------------------


class TestFilePath(unittest.TestCase):

    def test_init(self):
        # Attempt to instantiate with an unexisting file
        with self.assertRaises(FileOSError):
            FilePath("toto")

        # Attempt to instantiate with a file
        with self.assertRaises(PathTypeError):
            FilePath(__file__)

        # Normal situation
        d = os.path.dirname(__file__)
        fp = FilePath(d)
        self.assertEqual(d, fp.id)
        self.assertFalse(fp.state is States().CHECKED)
        self.assertEqual(fp.id, fp.get_id())

        # Property is only defined for 'get' (set is not implemented).
        with self.assertRaises(AttributeError):
            fp.id = "toto"

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

    def test_serialize(self):
        #print(json.dumps(d, indent=4, separators=(',', ': '), sort_keys=True))
        pass

