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

    src.files.tests.test_filedatacompare.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os
from random import randint

from sppas import u
from sppas.src.wkps import FileName, FileRoot, FilePath, sppasCatReference, sppasRefAttribute
from sppas.src.wkps.filedatacompare import sppasFileBaseCompare
from sppas.src.wkps.filedatacompare import sppasFileNameCompare
from sppas.src.wkps.filedatacompare import sppasFileExtCompare
from sppas.src.wkps.filedatacompare import sppasFileRefCompare


class TestFileDataCompare(unittest.TestCase):

    def setUp(self):
        # for FileNameCompare
        self.cmpFileName = sppasFileNameCompare()
        self.filename = u('test_filedatacompare')

        # for FileNameExtensionCompare
        self.cmpFileNameExtension = sppasFileExtCompare()
        self.extenstion = u(os.path.splitext(__file__)[1].upper())

        # for FilePathCompare
        self.cmpPath = sppasFileBaseCompare()

        # for FileRootComapre
        self.cmpRoot = sppasFileBaseCompare()

    def test_exact_fn(self):
        d = __file__
        fp = FileName(d)
        # fp exactly equals d
        self.assertTrue(fp.match([(self.cmpFileName.exact, self.filename, False)]))

    def test_iexact_fn(self):
        d = __file__
        fp = FileName(d)
        # fp matches with upper case d
        self.assertFalse(fp.match([(self.cmpFileName.iexact, self.filename.upper(), True)]))

    def test_startswith_fn(self):
        d = __file__
        fp = FileName(d)
        # fp begins with d's first character
        self.assertTrue(fp.match([(self.cmpFileName.startswith, self.filename[0], False)]))

    def test_istartswith_fn(self):
        d = __file__
        fp = FileName(d)
        # fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmpFileName.istartswith, self.filename[0].upper(), False)]))

    def test_endswith_fn(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmpFileName.endswith, self.filename[-1], True)]))

    def test_iendswith_fn(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmpFileName.iendswith, self.filename[-1].upper(), True)]))

    def test_contains_fn(self):
        d = __file__
        fp = FileName(d)
        # fp contains any d's character
        self.assertTrue(fp.match([(self.cmpFileName.contains, self.filename[randint(0, len(self.filename) - 1)], False)]))

    def test_regexp_fn(self):
        d = __file__
        fp = FileName(d)
        # fp looks like the regex
        self.assertFalse(fp.match([(self.cmpFileName.regexp, "^[a-z]", True)]))

    def test_exact_fe(self):
        d = __file__
        fp = FileName(d)
        # fp exactly equals d
        self.assertTrue(fp.match([(self.cmpFileNameExtension.exact, self.extenstion, False)]))

    def test_iexact_fe(self):
        d = __file__
        fp = FileName(d)
        # fp matches with upper case d
        self.assertFalse(fp.match([(self.cmpFileNameExtension.iexact, self.extenstion.lower(), True)]))

    def test_startswith_fe(self):
        d = __file__
        fp = FileName(d)
        # fp begins with d's first character
        self.assertTrue(fp.match([(self.cmpFileNameExtension.startswith, self.extenstion[0], False)]))

    def test_istartswith_fe(self):
        d = __file__
        fp = FileName(d)
        # fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmpFileNameExtension.istartswith, self.extenstion[0].lower(), False)]))

    def test_endswith_fe(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmpFileNameExtension.endswith, self.extenstion[-1], True)]))

    def test_iendswith_fe(self):
        d = __file__
        fp = FileName(d)
        # fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmpFileNameExtension.iendswith, self.extenstion[-1].lower(), True)]))

    def test_contains_fe(self):
        d = __file__
        fp = FileName(d)
        # fp contains any d's character
        self.assertTrue(fp.match([(self.cmpFileNameExtension.contains, self.extenstion[randint(0, len(self.extenstion) - 1)], False)]))

    def test_regexp_fe(self):
        d = __file__
        fp = FileName(d)
        # fp looks like the regex
        self.assertFalse(fp.match([(self.cmpFileNameExtension.regexp, "^\.", True)]))

    def test_match_fp(self):
        d = u(os.path.dirname(__file__))
        fp = FilePath(d)

        # fp.id is matching dirname
        self.assertTrue(fp.match([(self.cmpPath.exact, d, False)]))

        # fp.id is not matching dirname
        self.assertFalse(fp.match([(self.cmpPath.exact, d, True)]))

        # fp.id is matching dirname and path is checked
        self.assertTrue(fp.match(
            [(self.cmpPath.exact, d, False),
             (self.cmpPath.check, False, False)]))

        # fp is checked
        self.assertFalse(fp.match([(self.cmpPath.check, True, False)]))

        # fp.id ends with 'files' (the name of the package)!
        self.assertTrue(fp.match([(self.cmpPath.endswith, u("tests"), False)]))

    def test_exact_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp exactly equals d
        self.assertTrue(fp.match([(self.cmpRoot.exact, d, False)]))

    def test_iexact_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp matches with upper case d
        self.assertFalse(fp.match([(self.cmpRoot.iexact, d.upper(), True)]))

    def test_startswith_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp begins with d's first character
        self.assertTrue(fp.match([(self.cmpRoot.startswith, d[0], False)]))

    def test_istartswith_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp starts with d's first character in any case
        self.assertTrue(fp.match([(self.cmpRoot.istartswith, d[0].upper(), False)]))

    def test_endswith_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp finishes with d's last character
        self.assertFalse(fp.match([(self.cmpRoot.endswith, d[-1], True)]))

    def test_iendswith_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp finishes with d's last character in any case
        self.assertFalse(fp.match([(self.cmpRoot.iendswith, d[-1].upper(), True)]))

    def test_contains_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp contains any d's character
        self.assertTrue(fp.match([(self.cmpRoot.contains, d[randint(0, len(d) - 1)], False)]))

    def test_regexp_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp looks like the regex
        self.assertFalse(fp.match([(self.cmpRoot.regexp, "[^a-z]", True)]))

    def test_check_fr(self):
        d = u(os.path.splitext(__file__)[0])
        fp = FileRoot(d)
        # fp isn't checked
        self.assertTrue(fp.match([(self.cmpRoot.check, False, False)]))


class TestFileDataReferencesCompare(unittest.TestCase):

    def setUp(self):
        self.micros = sppasCatReference('microphone')
        self.micros.append(sppasRefAttribute('mic1', 'Bird UM1', None, '最初のインタビューで使えていましたマイク'))
        self.micros.add('mic2', 'AKG D5')
        self.id_cmp = sppasFileRefCompare()

    def test_exact_id(self):
        self.assertTrue(self.micros.match([(self.id_cmp.exact, u('microphone'), False)]))

    def test_iexact_id(self):
        name = u('microphone')
        self.assertFalse(self.micros.match([(self.id_cmp.iexact, name.upper(), True)]))

    def test_startswith_id(self):
        name = u('microphone')
        self.assertTrue(self.micros.match([(self.id_cmp.startswith, name[0], False)]))

    def test_istartswith_id(self):
        name = u('microphone')
        self.assertFalse(self.micros.match([(self.id_cmp.istartswith, name[0].upper(), True)]))

    def test_endswith_id(self):
        name = u('microphone')
        self.assertTrue(self.micros.match([(self.id_cmp.endswith, name[-1], False)]))

    def test_iendswith_id(self):
        name = u('microphone')
        self.assertFalse(self.micros.match([(self.id_cmp.iendswith, name[-1].upper(), True)]))

    def test_contains_id(self):
        name = u('microphone')
        self.assertTrue(self.micros.match([(self.id_cmp.contains, name[randint(0, len(name) - 1)], False)]))

    def test_regexp_id(self):
        regexp = '[^*_ç]'
        self.assertTrue(self.micros.match([(self.id_cmp.regexp, regexp, False)]))
