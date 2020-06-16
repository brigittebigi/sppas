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

    src.anndata.tests.test_exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
    :summary:      Tests of SPPAS

"""

import unittest
from .exc import *

# ---------------------------------------------------------------------------


class TestExceptions(unittest.TestCase):

    def test_exception(self):
        try:
            raise sppasError("the exception message")
        except Exception as e:
            self.assertTrue(isinstance(e, sppasError))
            self.assertTrue("0000" in str(e))

    # -----------------------------------------------------------------------

    def test_type_errors(self):
        try:
            raise sppasTypeError("wrong", "expected")
        except TypeError as e:
            self.assertTrue(isinstance(e, sppasTypeError))
            self.assertTrue("0100" in str(e))

    # -----------------------------------------------------------------------

    def test_index_errors(self):
        try:
            raise sppasIndexError(0)
        except IndexError as e:
            self.assertTrue(isinstance(e, sppasIndexError))
            self.assertTrue("0200" in str(e))

    # -----------------------------------------------------------------------

    def test_value_errors(self):
        try:
            raise sppasValueError("data name", "value")
        except ValueError as e:
            self.assertTrue(isinstance(e, sppasValueError))
            self.assertTrue("0300" in str(e))

        try:
            raise NegativeValueError(-3)
        except ValueError as e:
            self.assertTrue(isinstance(e, NegativeValueError))
            self.assertTrue("0310" in str(e))

        # to be continued...

    # -----------------------------------------------------------------------

    def test_key_errors(self):
        try:
            raise sppasKeyError("data name", "key")
        except KeyError as e:
            self.assertTrue(isinstance(e, sppasKeyError))
            self.assertTrue("0400" in str(e))

    # -----------------------------------------------------------------------

    def test_os_errors(self):
        try:
            raise sppasInstallationError("msg")
        except OSError as e:
            self.assertTrue(isinstance(e, sppasInstallationError))
            self.assertTrue("0510" in str(e))

        try:
            raise sppasEnableFeatureError("feature name")
        except OSError as e:
            self.assertTrue(isinstance(e, sppasEnableFeatureError))
            self.assertTrue("0520" in str(e))

    # -----------------------------------------------------------------------

    def test_io_errors(self):
        try:
            raise sppasIOError("toto.txt")
        except OSError as e:
            self.assertTrue(isinstance(e, sppasIOError))
            self.assertTrue("0600" in str(e))

        try:
            raise IOExtensionError(".to")
        except OSError as e:
            self.assertTrue(isinstance(e, IOExtensionError))
            self.assertTrue("0610" in str(e))

        try:
            raise NoDirectoryError("folder name")
        except OSError as e:
            self.assertTrue(isinstance(e, NoDirectoryError))
            self.assertTrue("0620" in str(e))
