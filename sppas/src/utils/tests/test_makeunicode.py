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

    src.utils.tests.test_makeunicode.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi
    :summary:      Test the "unicode maker" of SPPAS.

"""

import unittest
import sys

from ..makeunicode import sppasUnicode
from ..makeunicode import u, b, basestring

# ---------------------------------------------------------------------------


LowerDict = dict()
LowerDict['A'] = u('a')
LowerDict['B'] = u('b')
LowerDict['C'] = u('c')
LowerDict['D'] = u('d')
LowerDict['E'] = u('e')
LowerDict['F'] = u('f')
LowerDict['G'] = u('g')
LowerDict['H'] = u('h')
LowerDict['I'] = u('i')
LowerDict['J'] = u('j')
LowerDict['K'] = u('k')
LowerDict['L'] = u('l')
LowerDict['M'] = u('m')
LowerDict['N'] = u('n')
LowerDict['O'] = u('o')
LowerDict['P'] = u('p')
LowerDict['Q'] = u('q')
LowerDict['R'] = u('r')
LowerDict['S'] = u('s')
LowerDict['T'] = u('t')
LowerDict['U'] = u('u')
LowerDict['V'] = u('v')
LowerDict['W'] = u('w')
LowerDict['X'] = u('x')
LowerDict['Y'] = u('y')
LowerDict['Z'] = u('z')
LowerDict['À'] = u('à')
LowerDict['Á'] = u('a')
LowerDict['Á'] = u('á')
LowerDict['Â'] = u('â')
LowerDict['Ã'] = u('a')
LowerDict['Ã'] = u('ã')
LowerDict['Ä'] = u('ä')
#LowerDict['Æ'] = u('ae')
LowerDict['Ç'] = u('ç')
LowerDict['È'] = u('è')
LowerDict['É'] = u('é')
LowerDict['Ê'] = u('ê')
LowerDict['Ë'] = u('ë')
LowerDict['Ì'] = u('ì')
LowerDict['Í'] = u('í')
LowerDict['Î'] = u('î')
LowerDict['Ï'] = u('ï')
# LowerDict['Ñ'] = u('n')
LowerDict['Ò'] = u('ò')
LowerDict['Ó'] = u('ó')
LowerDict['Ô'] = u('ô')
LowerDict['Õ'] = u('_')
LowerDict['Õ'] = u('õ')
LowerDict['Ö'] = u('ö')
LowerDict['Ù'] = u('ù')
LowerDict['Ú'] = u('u')
LowerDict['Ú'] = u('ú')
LowerDict['Û'] = u('û')
LowerDict['Ü'] = u('ü')
LowerDict['Ý'] = u('ý')
LowerDict['Ă'] = u('ă')
LowerDict['Đ'] = u('đ')
LowerDict['Ĩ'] = u('ĩ')
LowerDict['Ũ'] = u('ũ')
LowerDict['Ơ'] = u('ơ')
LowerDict['Ư'] = u('ư')
LowerDict['Ạ'] = u('ạ')
LowerDict['Ả'] = u('ả')
LowerDict['Ấ'] = u('ấ')
LowerDict['Ầ'] = u('ầ')
LowerDict['Ẩ'] = u('ẩ')
LowerDict['Ẫ'] = u('ẫ')
LowerDict['Ậ'] = u('ậ')
LowerDict['Ắ'] = u('ắ')
LowerDict['Ằ'] = u('ằ')
LowerDict['Ẳ'] = u('ẳ')
LowerDict['Ẵ'] = u('ẵ')
LowerDict['Ặ'] = u('ặ')
LowerDict['Ẹ'] = u('ẹ')
LowerDict['Ẻ'] = u('ẻ')
LowerDict['Ẽ'] = u('ẽ')
LowerDict['Ế'] = u('ế')
LowerDict['Ề'] = u('ề')
LowerDict['Ể'] = u('ể')
LowerDict['Ễ'] = u('ễ')
LowerDict['Ệ'] = u('ệ')
LowerDict['Ỉ'] = u('ỉ')
LowerDict['Ị'] = u('ị')
LowerDict['Ọ'] = u('ọ')
LowerDict['Ỏ'] = u('ỏ')
LowerDict['Ố'] = u('ố')
LowerDict['Ồ'] = u('ồ')
LowerDict['Ổ'] = u('ổ')
LowerDict['Ỗ'] = u('ỗ')
LowerDict['Ộ'] = u('ộ')
LowerDict['Ớ'] = u('ớ')
LowerDict['Ờ'] = u('ờ')
LowerDict['Ở'] = u('ở')
LowerDict['Ỡ'] = u('ỡ')
LowerDict['Ợ'] = u('ợ')
LowerDict['Ụ'] = u('ụ')
LowerDict['Ủ'] = u('ủ')
LowerDict['Ứ'] = u('ứ')
LowerDict['Ừ'] = u('ừ')
LowerDict['Ử'] = u('ử')
LowerDict['Ữ'] = u('ữ')
LowerDict['Ự'] = u('ự')
LowerDict['Ỳ'] = u('ỳ')
LowerDict['Ỵ'] = u('ỵ')
LowerDict['Ỷ'] = u('ỷ')
LowerDict['Ỹ'] = u('ỹ')

# ---------------------------------------------------------------------------


class TestMethods(unittest.TestCase):
    """Test u and b methods."""

    def test_u(self):
        if sys.version_info < (3,):
            self.assertEqual(u("a string"), u"a string")
            self.assertEqual(u(3), u"3")
        else:
            self.assertEqual(u("a string"), "a string")
            self.assertEqual(u(3), str(3))

    def test_b(self):
        if sys.version_info < (3,):
            self.assertEqual(b("a string"), "a string")
            self.assertEqual(b(3), "3")
        else:
            self.assertEqual(b("a string"), b"a string")
            self.assertEqual(b(3), b"3")

    # -----------------------------------------------------------------------

    def test_basestring(self):
        if sys.version_info < (3,):
            self.assertTrue(isinstance('toto', basestring))
            self.assertTrue(isinstance(u('toto'), basestring))
            self.assertTrue(isinstance(b('toto'), basestring))
            self.assertFalse(isinstance(True, basestring))
            self.assertFalse(isinstance(5, basestring))
        else:
            self.assertTrue(isinstance('toto', str))
            self.assertTrue(isinstance(u('toto'), str))
            self.assertTrue(isinstance(b('toto'), bytes))
            self.assertFalse(isinstance(True, str))
            self.assertFalse(isinstance(5, str))

# ---------------------------------------------------------------------------


class TestMakeUnicode(unittest.TestCase):
    """Make a string as unicode and operates on it."""

    def test_init(self):
        sppasUnicode("")
        sppasUnicode("é")
        with self.assertRaises(TypeError):
            sppasUnicode(1)
        with self.assertRaises(TypeError):
            sppasUnicode(True)

    # -----------------------------------------------------------------------

    def test_clear_whitespace(self):
        s = "  ée  àa  çc  "
        self.assertEqual(sppasUnicode(s).clear_whitespace(), u("ée_àa_çc"))

    # -----------------------------------------------------------------------

    def test_to_ascii(self):
        s = "  ée  àa  çc  "
        self.assertEqual(sppasUnicode(s).to_ascii(), u("  _e  _a  _c  "))

    # -----------------------------------------------------------------------

    def test_lower(self):
        for key, value in LowerDict.items():
            self.assertEqual(value, sppasUnicode(key).to_lower())

    # -----------------------------------------------------------------------

    def test_strip(self):
        self.assertEqual(sppasUnicode('  \n Ỹ  \t\r   ỏ  ').to_strip(), u('Ỹ ỏ'))
        self.assertEqual(sppasUnicode('\t \t').to_strip(), u(''))
