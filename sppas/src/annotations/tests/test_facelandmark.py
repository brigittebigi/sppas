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

from sppas.src.config import paths
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImageWriter
from sppas.src.imgdata import sppasCoords
from ..FaceDetection import FaceDetection
from ..FaceMark.facelandmark import FaceLandmark

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MODEL_LBF68 = os.path.join(paths.resources, "faces", "lbfmodel68.yaml")
MODEL_DAT = os.path.join(paths.resources, "faces", "kazemi_landmark.dat")
# --> not efficient: os.path.join(paths.resources, "faces", "aam.xml")

NET = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
HAAR1 = os.path.join(paths.resources, "faces", "haarcascade_profileface.xml")
HAAR2 = os.path.join(paths.resources, "faces", "haarcascade_frontalface_alt.xml")

# ---------------------------------------------------------------------------


class TestFaceLandmark(unittest.TestCase):

    def test_load_resources(self):
        fl = FaceLandmark()
        self.assertEqual(0, len(fl))
        with self.assertRaises(IOError):
            fl.load_model("toto.txt", "toto")

        fl.load_model(NET, MODEL_LBF68, MODEL_DAT)
        with self.assertRaises(Exception):
            fl.load_model(MODEL_DAT, MODEL_LBF68)

    # ------------------------------------------------------------------------

    def test_contains(self):
        fd = FaceLandmark()
        # access to the private list of landmarks and append a point
        fd._FaceLandmark__sights.append(sppasCoords(124, 235))
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
        fl.load_model(NET, MODEL_DAT)
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
        fl.load_model(NET, MODEL_LBF68, MODEL_DAT)

        # The image we'll work on
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-portrait.jpg")
        with self.assertRaises(TypeError):
            fl.mark(fn)
        img = sppasImage(filename=fn)
        fl.mark(img)

        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-mark.jpg")
        w = sppasImageWriter()
        w.set_options(tag=True)
        w.write(img, [[c for c in fl]], fn)

    # ------------------------------------------------------------------------

    def test_mark_montage(self):
        fl = FaceLandmark()
        fl.load_model(NET, MODEL_LBF68, MODEL_DAT)

        # The image we'll work on, with 3 faces to be detected
        fn = os.path.join(DATA, "montage.png")
        img = sppasImage(filename=fn)

        fd = FaceDetection()
        fd.load_model(HAAR1, HAAR2, NET)
        fd.detect(img)
        self.assertEqual(len(fd), 3)
        fd.to_portrait(img)

        w = sppasImageWriter()
        w.set_options(tag=True)
        faces = list()       # list of coords
        for i, coord in enumerate(fd):
            fn = os.path.join(DATA, "montage_{:d}-face.jpg".format(i))
            # Create an image of the ROI
            cropped_face = img.icrop(coord)
            cropped_face.write(fn)
            try:
                fn = os.path.join(DATA, "montage_{:d}-mark.jpg".format(i))
                fl.mark(cropped_face)
                face_coords = fl.get_detected_face()
                face_coords.x += coord.x
                face_coords.y += coord.y
                faces.append(face_coords)

                w.write(cropped_face, [[c for c in fl]], fn)

            except Exception as e:
                print("Error for coords {}: {}".format(i, str(e)))

        fn = os.path.join(DATA, "montage-faces.png")
        w.write(img, faces, fn)
