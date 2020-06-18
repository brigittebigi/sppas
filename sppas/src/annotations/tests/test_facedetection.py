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

    src.imgdata.tests.test_facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import unittest

from sppas.src.config import paths
from sppas.src.imgdata.coordinates import sppasCoords
from sppas.src.imgdata.image import sppasImage
from sppas.src.annotations.FaceDetection.facedetection import FaceDetection

# ---------------------------------------------------------------------------


class TestFaceDetection(unittest.TestCase):

    def test_load_resources(self):
        fd = FaceDetection()
        with self.assertRaises(IOError):
            fd.load_model("toto.txt", "toto")

    # ------------------------------------------------------------------------

    def test_detect_default(self):
        fd = FaceDetection()
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on
        fn = os.path.join(paths, "faces", "BrigitteBigiSlovenie2016.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)

        # only one face should be detected
        self.assertEqual(1, len(fd))

        coords = fd.get_best()
        self.assertTrue(coords == [886, 222, 177, 189])
        self.assertGreater(coords.get_confidence(), 0.99)
        cropped = sppasImage(input_array=img.icrop(coords))
        # The cropped image is 189 rows and 177 columns of pixels
        self.assertEqual(189, len(cropped))
        for row in cropped:
            self.assertEqual(len(row), 177)

        fn_detected = os.path.join(paths, "faces", "BrigitteBigiSlovenie2016-face.jpg")
        face = sppasImage(filename=fn_detected)

        self.assertEqual(len(cropped), len(face))
        for r1, r2 in zip(cropped, face):
            self.assertEqual(len(r1), len(r2))
            for c1, c2 in zip(r1, r2):
                self.assertTrue(len(c1), 3)
                self.assertTrue(len(c2), 3)
                # we can't compare values, they are close but not equals!

    # ------------------------------------------------------------------------

    def test_getters(self):
        fd = FaceDetection()
        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)

        fd.detect(img)
        # two faces should be detected
        self.assertEqual(2, len(fd))
        self.assertTrue(fd[0] == [927, 238, 97, 117])   # me
        self.assertTrue(fd[1] == [519, 198, 109, 109])  # kasia

        # get best
        coords = fd.get_best()
        self.assertTrue(coords == [927, 238, 97, 117])   # me

        coords = fd.get_best(3)
        self.assertTrue(coords[0] == [927, 238, 97, 117])   # me
        self.assertTrue(coords[1] == [519, 198, 109, 109])  # kasia
        self.assertIsNone(coords[2])

        # get confidence
        coords = fd.get_confidence(0.9)
        self.assertEqual(len(coords), 2)
        coords = fd.get_confidence(0.91)
        self.assertEqual(len(coords), 1)
        coords = fd.get_confidence(0.98)
        self.assertEqual(len(coords), 0)

    # ------------------------------------------------------------------------

    def test_contains(self):
        fd = FaceDetection()
        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)
        fd.detect(img)

        self.assertTrue(sppasCoords(927, 238, 97, 117) in fd)
        self.assertTrue((927, 238, 97, 117) in fd)
        self.assertFalse((0, 0, 97, 117) in fd)
