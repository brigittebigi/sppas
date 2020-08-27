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

    src.annotations.tests.test_facetracking.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import unittest

from sppas.src.config import paths
from sppas.src.exceptions import sppasError

from ..FaceTracking.facebuffer import sppasFacesVideoBuffer

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MODEL_LBF68 = os.path.join(paths.resources, "faces", "lbfmodel68.yaml")
MODEL_DAT = os.path.join(paths.resources, "faces", "kazemi_landmark.dat")
# --> not efficient: os.path.join(paths.resources, "faces", "aam.xml")

NET = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
HAAR1 = os.path.join(paths.resources, "faces", "haarcascade_profileface.xml")
HAAR2 = os.path.join(paths.resources, "faces", "haarcascade_frontalface_alt.xml")

# ---------------------------------------------------------------------------


class TestFaceBuffer(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    # -----------------------------------------------------------------------

    def test_load_resources(self):
        fvb = sppasFacesVideoBuffer()
        with self.assertRaises(IOError):
            fvb.load_fd_model("toto.txt", "toto")
        with self.assertRaises(IOError):
            fvb.load_fl_model("toto.txt", "toto")

        fvb.load_fd_model(NET, HAAR1, HAAR2)
        fvb.load_fl_model(NET, MODEL_LBF68, MODEL_DAT)

    # -----------------------------------------------------------------------

    def test_nothing(self):
        # Instantiate a video buffer
        fvb = sppasFacesVideoBuffer(size=10, overlap=0)
        with self.assertRaises(ValueError):
            fvb.get_detected_faces(3)
        fvb.detect_buffer()
        with self.assertRaises(ValueError):
            fvb.get_detected_faces(3)

        # Open a video and fill-in the buffer with size-images.
        fvb.open(TestFaceBuffer.VIDEO)
        fvb.next()
        self.assertEqual(10, len(fvb))
        self.assertEqual(10, fvb.tell())
        self.assertEqual((0, 9), fvb.get_range())
        with self.assertRaises(ValueError):
            fvb.get_detected_faces(3)

        # Still no detector was defined... i.e. no model loaded
        with self.assertRaises(sppasError):
            fvb.detect_buffer()

        # Still no detector was defined... i.e. no model loaded
        with self.assertRaises(sppasError):
            fvb.detect_faces_buffer()

    # -----------------------------------------------------------------------

    def test_detect(self):
        fvb = sppasFacesVideoBuffer(video=TestFaceBuffer.VIDEO,
                                    size=10, overlap=0)
        fvb.next()
        self.assertEqual(10, len(fvb))
        self.assertEqual(10, fvb.tell())
        self.assertEqual((0, 9), fvb.get_range())

        # Detect the face in the video
        fvb.load_fd_model(NET, HAAR1, HAAR2)
        fvb.detect_faces_buffer()
        for i in range(10):
            # print("* Image {:d}".format(i))
            faces = fvb.get_detected_faces(i)
            self.assertEqual(1, len(faces))
            # for coord in faces:
            #    print(coord)

        # Detect the landmarks of the face in the video
        with self.assertRaises(sppasError):
            fvb.detect_landmarks_buffer()
        fvb.load_fl_model(NET, MODEL_LBF68, MODEL_DAT)

        fvb.detect_faces_buffer()
        fvb.detect_landmarks_buffer()
        for i in range(10):
            # print("* Image {:d}".format(i))
            faces = fvb.get_detected_faces(i)
            landmarks = fvb.get_detected_landmarks(i)
            self.assertEqual(len(faces), len(landmarks))
            for x in range(len(faces)):
                self.assertEqual(68, len(landmarks[x]))

        fvb.next()
        with self.assertRaises(ValueError):
            fvb.get_detected_faces(3)
