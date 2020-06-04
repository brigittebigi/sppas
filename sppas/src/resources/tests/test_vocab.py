# -*- coding: utf8 -*-
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

    src.resources.tests.test_vocab.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os.path
import shutil

from sppas.src.config import paths
from sppas.src.wkps.fileutils import sppasFileUtils
from sppas.src.utils.makeunicode import u

from ..vocab import sppasVocabulary

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()

VOCAB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vocab.txt")
ITA = os.path.join(paths.resources, "vocab", "ita.vocab")
VOCAB_TEST = os.path.join(TEMP, "vocab.txt")

# ---------------------------------------------------------------------------


class TestVocabulary(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_all(self):
        l = sppasVocabulary(VOCAB, nodump=True)
        self.assertEqual(len(l), 20)
        self.assertTrue(l.is_unk('toto'))
        self.assertFalse(l.is_unk('normale'))
        self.assertFalse(l.is_unk("isn't"))
        self.assertFalse(l.is_unk(u("đ")))
        l.add("être")
        self.assertTrue(l.is_in(u("être")))
        self.assertTrue(u("être") in l)
        #self.assertTrue(l.is_unk("être")) True with Python 2.7 but False with Python 3.

    def test_save(self):
        l = sppasVocabulary(VOCAB, nodump=True)
        l.save(VOCAB_TEST)
        l2 = sppasVocabulary(VOCAB_TEST, nodump=True)
        self.assertEqual(len(l), len(l2))
        for w in l.get_list():
            self.assertTrue(l2.is_in(w))

    def test_ita(self):
        l = sppasVocabulary(ITA, nodump=True)
        self.assertTrue(l.is_unk('toto'))
        self.assertFalse(l.is_unk(u('perché')))
