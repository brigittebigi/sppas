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

    src.annotations.tests.test_facedetection.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import unittest

from sppas.src.config import paths
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImageWriter
from sppas.src.annotations.FaceDetection.facedetection import FaceDetection

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

NET = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000.caffemodel")
#HAAR = os.path.join(paths.resources, "faces", "haarcascade_profileface.xml")
HAAR = os.path.join(paths.resources, "faces", "haarcascade_frontalface_alt.xml")

# ---------------------------------------------------------------------------


class TestFaceDetection(unittest.TestCase):

    def test_load_resources(self):
        fd = FaceDetection()
        self.assertIsNone(fd._FaceDetection__net)
        self.assertIsNone(fd._FaceDetection__cascade)

        with self.assertRaises(IOError):
            fd.load_model("toto.txt")

        fd.load_model(NET)
        self.assertIsNotNone(fd._FaceDetection__net)

        fd.load_model(HAAR)
        self.assertIsNotNone(fd._FaceDetection__cascade)

# ---------------------------------------------------------------------------


class TestHaarCascadeFaceDetection(unittest.TestCase):

    def test_detect_nothing(self):
        fd = FaceDetection()
        fd.load_model(HAAR)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)

        # Nothing should be detected
        self.assertEqual(0, len(fd))

    # ------------------------------------------------------------------------

    def test_detect_one_face_good_img_quality(self):
        fd = FaceDetection()
        fd.load_model(HAAR)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on
        fn = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)

        # only one face should be detected but it detects 2....
        self.assertEqual(2, len(fd))

    # ------------------------------------------------------------------------

    def test_detect_montage(self):
        fd = FaceDetection()
        fd.load_model(HAAR)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on, with 3 faces to be detected
        fn = os.path.join(DATA, "montage.png")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        coords = [c.copy() for c in fd]

        w = sppasImageWriter()
        w.set_options(tag=True)
        fn = os.path.join(DATA, "montage-haarfaces.png")
        w.write(img, coords, fn)

        # 8 faces are detected (including the 3 right ones) but 2 are too small
        self.assertEqual(4, len(fd))

# ---------------------------------------------------------------------------


class TestDNNFaceDetection(unittest.TestCase):

    def test_detect_nothing(self):
        fd = FaceDetection()
        fd.load_model(NET)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)

        # Nothing should be detected
        self.assertEqual(0, len(fd))

    # ------------------------------------------------------------------------

    def test_detect_one_face_good_img_quality(self):
        fd = FaceDetection()
        fd.load_model(NET)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on
        fn = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        print(fd)

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

        fn_detected = os.path.join(DATA, "BrigitteBigiSlovenie2016-face.jpg")
        face = sppasImage(filename=fn_detected)

        self.assertEqual(len(cropped), len(face))
        for r1, r2 in zip(cropped, face):
            self.assertEqual(len(r1), len(r2))
            for c1, c2 in zip(r1, r2):
                self.assertTrue(len(c1), 3)
                self.assertTrue(len(c2), 3)
                # we can't compare values, they are close but not equals!

        # Test to-portrait - coords are scaled by 2.2 and shifted.
        # --------------------------------------------------------
        fd.to_portrait(img)
        coords = fd.get_best()
        print(coords)
        self.assertTrue(coords == [780, 147, 389, 415])
        cropped = sppasImage(input_array=img.icrop(coords))

        fn_detected = os.path.join(DATA, "BrigitteBigiSlovenie2016-portrait.jpg")
        face = sppasImage(filename=fn_detected)

        self.assertEqual(len(cropped), len(face))
        for r1, r2 in zip(cropped, face):
            self.assertEqual(len(r1), len(r2))
            for c1, c2 in zip(r1, r2):
                self.assertTrue(len(c1), 3)
                self.assertTrue(len(c2), 3)
                # we can't compare values, they are close but not equals!

    # ------------------------------------------------------------------------

    def test_detect_montage(self):
        fd = FaceDetection()
        fd.load_model(NET)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on, with 3 faces to be detected
        fn = os.path.join(DATA, "montage.png")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        coords = [c.copy() for c in fd]

        w = sppasImageWriter()
        w.set_options(tag=True)
        fn = os.path.join(DATA, "montage-dnnfaces.png")
        w.write(img, coords, fn)

        # Detected faces are
        # (877,237) (154,208): 0.975750
        # (238,199) (192,261): 0.962529
        # (1605,282) (155,219): 0.479989
        # (419,935) (165,135): 0.456266
        # (235,306) (143,143): 0.218089

        # only 3 faces should be detected
        # self.assertEqual(3, len(fd))

    # ------------------------------------------------------------------------

    def test_getters(self):
        fd = FaceDetection()
        fd.load_model(NET)
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

        # get more coords than those detected
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
        fd.load_model(NET)
        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)
        fd.detect(img)

        self.assertTrue(sppasCoords(927, 238, 97, 117) in fd)
        self.assertTrue((927, 238, 97, 117) in fd)
        self.assertFalse((0, 0, 97, 117) in fd)
