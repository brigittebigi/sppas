# -*- coding: UTF-8 -*-
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

    src.structs.tests.test_lang.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest
import os.path

from sppas.src.config import paths

from ..lang import sppasLangResource
from ..structsexc import LangTypeError, LangNameError, LangPathError

# ---------------------------------------------------------------------------


class TestLang(unittest.TestCase):

    def setUp(self):
        self.lr = sppasLangResource()

    def test_constant(self):
        self.assertEqual(2, len(sppasLangResource.RESOURCES_TYPES))

    def test_set(self):
        self.assertEqual(self.lr.get_lang(), "")

        with self.assertRaises(LangPathError):
            self.lr.set("file", "wrongpath")

        with self.assertRaises(LangTypeError):
            self.lr.set("wrongtype", "vocab")

        self.lr.set("file", "vocab")
        langlist = self.lr.get_langlist()
        self.assertEqual(0, len(langlist))

        # Tokenization:
        self.lr.set("file", "vocab", "", ".vocab")
        self.assertEqual(os.path.join(paths.resources, "vocab"), self.lr.get_langresource())
        self.lr.set_lang("fra")
        self.assertEqual("fra", self.lr.get_lang())
        self.assertEqual(os.path.join(paths.resources, "vocab", "fra.vocab"), self.lr.get_langresource())
        with self.assertRaises(LangNameError):
            self.lr.set_lang("wrong")

        # Syllabification:
        self.lr.set("file", "syll", "syllConfig-", ".txt")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(paths.resources, "syll", "syllConfig-fra.txt"), self.lr.get_langresource())
        with self.assertRaises(LangNameError):
            self.lr.set_lang("wrong")

        # Alignment
        self.lr.set("directory", "models", "models-")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(paths.resources, "models", "models-fra"), self.lr.get_langresource())
        with self.assertRaises(LangNameError):
            self.lr.set_lang("wrong")

        # other...
        self.lr.set("directory", "models", "models-", ".txt")
        self.lr.set_lang("fra")
        self.assertEqual(os.path.join(paths.resources, "models", "models-fra"), self.lr.get_langresource())
        with self.assertRaises(LangNameError):
            self.lr.set_lang("wrong")


