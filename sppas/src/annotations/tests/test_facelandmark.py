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
from sppas.src.imgdata import sppasCoords
from ..FaceDetection import FaceDetection
from ..FaceMark.facelandmark import FaceLandmark

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MODEL = os.path.join(paths.resources, "faces", "lbfmodel68.yaml")

NET = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000.caffemodel")
HAAR = os.path.join(paths.resources, "faces", "haarcascade_frontalface_alt2.xml")

# ---------------------------------------------------------------------------


class TestFaceLandmark(unittest.TestCase):

    def test_load_resources(self):
        fl = FaceLandmark()
        self.assertEqual(0, len(fl))
        with self.assertRaises(IOError):
            fl.load_model("toto.txt", "toto")

        fl.load_model(MODEL, NET)

    # ------------------------------------------------------------------------

    def test_contains(self):
        fd = FaceLandmark()
        # access to the private list of landmarks and append a point
        fd._FaceLandmark__landmarks.append(sppasCoords(124, 235))
        # test with coordinates
        self.assertTrue(sppasCoords(124, 235) in fd)
        self.assertFalse(sppasCoords(24, 35) in fd)
        # test with list or tuple
        self.assertTrue((124, 235) in fd)
        self.assertTrue([124, 235, 0, 0] in fd)
        self.assertFalse((24, 35, 0, 0) in fd)

    # ------------------------------------------------------------------------

    def test_mark_nothing(self):
        fl = FaceLandmark()
        fl.load_model(MODEL, NET)
        # Nothing detected... we still didn't asked for

        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            fl.mark(fn)
        img = sppasImage(filename=fn)

        # Nothing should be marked. No face in the image
        with self.assertRaises(Exception):
            fl.mark(img)

    # ------------------------------------------------------------------------

    def test_mark_normal(self):
        fl = FaceLandmark()
        fl.load_model(MODEL, NET)

        # The image we'll work on
        fn = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")
        with self.assertRaises(TypeError):
            fl.mark(fn)
        img = sppasImage(filename=fn)
        fl.mark(img)

        print(fl)

    # ------------------------------------------------------------------------

    def test_mark_montage(self):
        fl = FaceLandmark()
        fl.load_model(MODEL, HAAR)

        # The image we'll work on, with 3 faces to be detected
        fn = os.path.join(DATA, "montage.png")
        img = sppasImage(filename=fn)

        fd = FaceDetection()
        fd.load_model(NET)
        fd.detect(img)
        fd.to_portrait(img)

        landmark_coords = list()
        for i, coord in enumerate(fd):
            # Create an image of the ROI
            cropped_face = img.icrop(coord)
            fn = os.path.join(DATA, "face-{:d}.jpg".format(i))
            cv2.imwrite(fn, i)
            try:
                fl.mark(cropped_face)
                landmark_coords.append(coord)
            except Exception as e:
                print(str(e))

        for coord in landmark_coords:
            print(coord)
