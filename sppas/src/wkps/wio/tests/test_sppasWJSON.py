# -*- coding: utf-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        use of this software is governed by the gnu public license, version 3.

        sppas is free software: you can redistribute it and/or modify
        it under the terms of the gnu general public license as published by
        the free software foundation, either version 3 of the license, or
        (at your option) any later version.

        sppas is distributed in the hope that it will be useful,
        but without any warranty; without even the implied warranty of
        merchantability or fitness for a particular purpose.  see the
        gnu general public license for more details.

        you should have received a copy of the gnu general public license
        along with sppas. if not, see <http://www.gnu.org/licenses/>.

        this banner notice must not be removed.

        ---------------------------------------------------------------------

    wkps.wio.tests.test_sppasWJSON.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import sppas
import os

from ..sppasWJSON import sppasWJSON
from sppas.src.wkps.sppasWorkspace import sppasWorkspace
from sppas.src.wkps.fileref import FileReference, sppasAttribute

# ---------------------------------------------------------------------------


class TestsppasWJSON(unittest.TestCase):

    def setUp(self):
        self.data = sppasWorkspace()
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        self.r1 = FileReference('SpeakerAB')
        self.r1.set_type('SPEAKER')
        self.r1.append(sppasAttribute('initials', 'AB'))
        self.r1.append(sppasAttribute('sex', 'F'))

        self.parser = sppasWJSON()
        self.file = os.path.join(sppas.paths.sppas, 'src', 'wkps', 'wio', 'tests', 'file.wjson')

    # -----------------------------------------------------------------------

    def test_init(self):
        self.assertEqual(self.parser.software, "SPPAS")
        self.assertEqual(self.parser.default_extension, "wjson")

    # -----------------------------------------------------------------------

    def test_detect(self):
        self.assertFalse(self.parser.detect(""))
        self.assertTrue(self.parser.detect(self.file))

    # -----------------------------------------------------------------------









