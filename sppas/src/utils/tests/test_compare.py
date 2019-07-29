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

    src.utils.tests.test_compare.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi
    :summary:      Test the utility comparison class.

"""

import unittest

from ..compare import sppasCompare

# ---------------------------------------------------------------------------


class TestCompare(unittest.TestCase):

    def setUp(self):
        self.cmp = sppasCompare(verbose=False, case_sensitive=False)

    def test_equals_items(self):
        # Compare numeric values
        self.assertTrue(self.cmp.equals_items(5, 5))
        self.assertTrue(self.cmp.equals_items(5, 5.0))
        self.assertFalse(self.cmp.equals_items(4, 4.1))
        self.assertTrue(self.cmp.equals_items(4.00001, 4.00002))

        # Compare strings
        self.assertTrue(self.cmp.equals_items("aéè", "aéè"))
        self.assertTrue(self.cmp.equals_items("Aéè", "aéè"))
        self.cmp.set_case_sensitive(True)
        self.assertFalse(self.cmp.equals_items("Aéè", "aéè"))
        self.assertFalse(self.cmp.equals_items(u"Aéè", u"aéè"))
        self.cmp.set_case_sensitive(False)
        self.assertTrue(self.cmp.equals_items(u"Aéè", u"aéè"))
        #self.assertTrue(self.cmp.equals_items("Aéè", u"aéè"))

    def test_equals_lists(self):
        l1 = [1, 2, 3, 4]
        l2 = [1, 3, 4, 2]
        self.assertTrue(self.cmp.equals_lists(l1, l1))
        self.assertTrue(self.cmp.equals_lists(l2, l2))
        self.assertFalse(self.cmp.equals_lists(l1, l2))

    def test_equals_dicts(self):
        d1 = {1: "one", 2: "two"}
        d2 = {2: "TWO", 1: "ONE"}
        self.assertTrue(self.cmp.equals(d1, d2))
