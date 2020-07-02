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

from sppas.src.imgdata import HaarCascadeDetector
from sppas.src.imgdata import NeuralNetDetector
from ..FaceDetection.facedetection import FaceDetection

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

NET = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
HAAR1 = os.path.join(paths.resources, "faces", "haarcascade_profileface.xml")
HAAR2 = os.path.join(paths.resources, "faces", "haarcascade_frontalface_alt.xml")

# ---------------------------------------------------------------------------


class TestFaceDetection(unittest.TestCase):

    def test_load_model(self):
        fd = FaceDetection()
        self.assertIsNone(fd._detector)

        with self.assertRaises(IOError):
            fd.load_model("toto.txt")

        fd.load_model(NET)
        self.assertIsNotNone(fd._detector)
        self.assertEqual(len(fd._detector), 1)
        self.assertIsInstance(fd._detector[0], NeuralNetDetector)

        fd.load_model(HAAR1)
        self.assertIsNotNone(fd._detector)
        self.assertEqual(len(fd._detector), 1)
        self.assertIsInstance(fd._detector[0], HaarCascadeDetector)

        fd.load_model(HAAR1, NET, HAAR2)
        self.assertEqual(len(fd._detector), 3)

    # ------------------------------------------------------------------------

    def test_to_portrait(self):
        fd = FaceDetection()
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)   # (w, h) = (1632, 916)

        # normal situation
        fd.invalidate()
        fd._coords.append(sppasCoords(200, 200, 150, 150))
        fd.to_portrait(img)
        self.assertEqual(fd[0], sppasCoords(118, 146, 315, 315))

        # coords at top-left (can't fully shift x and y)
        fd.invalidate()
        fd._coords.append(sppasCoords(10, 10, 100, 100))
        fd.to_portrait(img)
        self.assertEqual(fd[0], [0, 0, 210, 210])

        # coords at bottom-right (can't fully shift x and y)
        fd.invalidate()
        fd._coords.append(sppasCoords(1500, 850, 100, 60))
        fd.to_portrait(img)
        self.assertEqual(fd[0], [1422, 790, 210, 126])

        # the 3rd face in montage.png
        fd.invalidate()
        fd._coords.append(sppasCoords(1546, 253, 276, 276))
        fd.to_portrait(img)
        self.assertEqual(fd[0], [1053, 153, 579, 579])

    # ------------------------------------------------------------------------

    def test_contains(self):
        fd = FaceDetection()
        fd.load_model(NET)
        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)
        fd.detect(img)

        self.assertFalse((0, 0, 97, 117) in fd)
        try:
            # linux, python 3.6, opencv 4.?
            self.assertTrue(sppasCoords(927, 238, 97, 117) in fd)
        except AssertionError:
            # windows10, python 3.8, opencv 4.2.0
            self.assertTrue(sppasCoords(925, 239, 97, 117) in fd)

    # ------------------------------------------------------------------------

    def test_getters(self):
        fd = FaceDetection()
        fd.load_model(NET)
        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)

        fd.detect(img)
        self.assertEqual(2, len(fd))

        try:  # linux
            # two faces should be detected
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

        except AssertionError:   # Windows
            # two faces should be detected
            self.assertTrue(fd[0] == [925, 239, 97, 117])  # me
            self.assertTrue(fd[1] == [509, 204, 94, 99])   # kasia

            # get best
            coords = fd.get_best()
            self.assertTrue(coords == [925, 239, 97, 117])  # me
            # get confidence
            coords = fd.get_confidence(0.9)
            self.assertEqual(len(coords), 1)

    # ------------------------------------------------------------------------

    def test_multi_detect(self):
        fd = FaceDetection()
        fn = os.path.join(DATA, "montage.png")
        img = sppasImage(filename=fn)
        w = sppasImageWriter()
        w.set_options(tag=True)

        fd.load_model(HAAR1, HAAR2, NET)
        fd.detect(img)
        self.assertEqual(3, len(fd))
        coords = [c.copy() for c in fd]
        for c in coords:
            print(c)
        # fn = os.path.join(DATA, "montage-faces.png")
        # w.write(img, coords, fn)

# ---------------------------------------------------------------------------


class TestHaarCascadeFaceDetection(unittest.TestCase):

    def test_detect_nothing(self):
        fd = FaceDetection()
        fd.load_model(HAAR1)
        # Nothing detected... we still didn't asked for
        self.assertIsInstance(fd._detector[0], HaarCascadeDetector)
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
        fd.load_model(HAAR1)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on
        fn = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)

        # No profile face in the image
        self.assertEqual(0, len(fd))

        # Only 1 frontal face in the image but 2 detected
        fd.load_model(HAAR2)
        fd.detect(img)
        self.assertGreaterEqual(1, len(fd))
        print(fd[0])

        # combining both detectors: only the right coords are selected
        fd.load_model(HAAR1, HAAR2)
        fd.set_min_score(0.1)
        fd.detect(img)
        self.assertEqual(1, len(fd))

    # ------------------------------------------------------------------------

    def test_detect_montage(self):
        fd = FaceDetection()
        fn = os.path.join(DATA, "montage.png")   # 3 faces should be found
        img = sppasImage(filename=fn)
        w = sppasImageWriter()
        w.set_options(tag=True)

        # With the profile model
        # ----------------------
        fd.load_model(HAAR1)

        # with the default min score
        fd.detect(img)
        # coords = [c.copy() for c in fd]
        # fn = os.path.join(DATA, "montage-haarprofilefaces.png")
        # w.write(img, coords, fn)
        self.assertEqual(4, len(fd))

        # will detect the same because haar system is normalizing weights
        # with the min score
        fd.set_min_score(0.067)
        fd.detect(img)
        # coords = [c.copy() for c in fd]
        # fn = os.path.join(DATA, "montage-haarprofilefaces.png")
        # w.write(img, coords, fn)
        self.assertEqual(4, len(fd))

        # With the frontal model
        # ----------------------
        fd.set_min_score(FaceDetection.DEFAULT_MIN_SCORE)
        fd.load_model(HAAR2)
        fd.detect(img)
        # coords = [c.copy() for c in fd]
        # fn = os.path.join(DATA, "montage-haarfrontfaces.png")
        # w.write(img, coords, fn)
        self.assertEqual(6, len(fd))

        # With both models
        # ----------------------
        fd.load_model(HAAR1, HAAR2)
        fd.detect(img)
        self.assertEqual(5, len(fd))

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

        # only one face should be detected
        self.assertEqual(1, len(fd))

        coords = fd.get_best()
        self.assertTrue(coords in ([886, 222, 177, 189], [886, 223, 177, 193]))
        self.assertGreater(coords.get_confidence(), 0.99)
        cropped = sppasImage(input_array=img.icrop(coords))
        # The cropped image is 189 rows and 177 columns of pixels
        self.assertTrue(len(cropped) in (189, 193))
        for row in cropped:
            self.assertEqual(len(row), 177)

        """
        # we can't compare values, they are close but not equals!
        fn_detected = os.path.join(DATA, "BrigitteBigiSlovenie2016-face.jpg")
        face = sppasImage(filename=fn_detected)
        self.assertEqual(len(cropped), len(face))
        for r1, r2 in zip(cropped, face):
            self.assertEqual(len(r1), len(r2))
            for c1, c2 in zip(r1, r2):
                self.assertTrue(len(c1), 3)
                self.assertTrue(len(c2), 3)"""

        # Test to-portrait - coords are scaled by 2.1 and shifted.
        # --------------------------------------------------------
        fd.to_portrait(img)
        coords = fd.get_best()
        self.assertTrue(coords in ([789, 153, 371, 405], [789, 154, 371, 396]))
        cropped = sppasImage(input_array=img.icrop(coords))

        fn_detected = os.path.join(DATA, "BrigitteBigiSlovenie2016-portrait.jpg")
        cropped.write(fn_detected)

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
        self.assertEqual(4, len(fd))

        fd.set_min_score(0.067)
        fd.detect(img)
        self.assertEqual(4, len(fd))
