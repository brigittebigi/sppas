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

    src.imgdata.tests.test_imgexc
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
    :summary:      Tests of exceptions of imgdata package of SPPAS

"""

import unittest
from ..imgdataexc import *

# ---------------------------------------------------------------------------


class TestImagesExceptions(unittest.TestCase):

    def test_io_error(self):
        try:
            raise ImageReadError("the filename")
        except Exception as e:
            self.assertTrue(isinstance(e, IOError))
            self.assertTrue("2610" in str(e))

        try:
            raise ImageWriteError("the filename")
        except Exception as e:
            self.assertTrue(isinstance(e, IOError))
            self.assertTrue("2620" in str(e))

    def test_value_error(self):
        try:
            raise ImageBoundError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2330" in str(e))

        try:
            raise ImageWidthError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2332" in str(e))

        try:
            raise ImageHeightError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2334" in str(e))

        try:
            raise ImageEastingError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2336" in str(e))

        try:
            raise ImageNorthingError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2338" in str(e))




