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

    src.utils.tests.test_datatype.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi
    :summary:      Test the utility datatype classes.

"""

import unittest

from ..datatype import bidict

# ---------------------------------------------------------------------------


class TestBiDict(unittest.TestCase):
    """Test bidirectional dictionary. """
    def test_create(self):
        d = bidict()
        d = bidict({'a': 1})

    def test_setitem(self):
        """Test setitem in a bidict. """
        d = bidict()
        d['a'] = 1
        self.assertTrue('a' in d)
        self.assertTrue(1 in d)
        self.assertEqual(1, d['a'])
        self.assertEqual(1, d.get('a'))
        self.assertEqual('a', d[1])

        b = bidict({'a': 1})
        self.assertTrue('a' in b)
        self.assertTrue(1 in b)
        self.assertEqual(1, b['a'])
        self.assertEqual('a', b[1])

        with self.assertRaises(KeyError):
            b[2]

    def test_delitem(self):
        """Test delitem in a bidict. """
        d = bidict({'a': 1})
        d['a'] = 2
        self.assertTrue('a' in d)
        self.assertTrue(2 in d)
        self.assertFalse(1 in d)
        self.assertNotEqual(1, d['a'])
        self.assertEqual(2, d['a'])
        self.assertEqual('a', d[2])
        del d[2]
        self.assertFalse(2 in d)
        self.assertFalse('a' in d)
