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

    src.annotations.tests.test_facelandmark.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import unittest
import cv2

from sppas.src.config import paths
from sppas.src.imgdata import sppasImage
from ..FaceMark.facelandmark import FaceLandmark

# ---------------------------------------------------------------------------


class TestFaceLandmark(unittest.TestCase):

    def test_load_resources(self):
        fd = FaceLandmark()
        with self.assertRaises(IOError):
            fd.load_model("toto.txt", "toto")

    # ------------------------------------------------------------------------

    def test_detect_default(self):
        fl = FaceLandmark()
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fl))

        # The image we'll work on
        fn = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")
        with self.assertRaises(TypeError):
            fl.mark(fn)
        img = sppasImage(filename=fn)
        fl.mark(img)

        for coord in fl:
            print(coord)
