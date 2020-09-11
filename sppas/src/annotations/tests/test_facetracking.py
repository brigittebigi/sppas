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
from sppas.src.annotations.param import sppasParam
from sppas.src.videodata import sppasVideoReaderBuffer

from ..FaceTracking.videotrackwriter import sppasVideoCoordsWriter
from ..FaceTracking.facebuffer import sppasFacesVideoBuffer
from ..FaceTracking.sppasfacetrack import sppasFaceTrack

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

    def test_subclassing(self):

        class subclassVideoBuffer(sppasVideoReaderBuffer):
            def __init__(self, video=None,
                         size=sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE):
                super(subclassVideoBuffer, self).__init__(video, size, overlap=0)

        bv = subclassVideoBuffer()
        self.assertEqual(bv.get_buffer_size(), sppasVideoReaderBuffer.DEFAULT_BUFFER_SIZE)
        self.assertEqual(bv.get_buffer_overlap(), sppasVideoReaderBuffer.DEFAULT_BUFFER_OVERLAP)
        self.assertFalse(bv.is_opened())
        self.assertEqual(0, bv.get_framerate())
        self.assertEqual(0, bv.tell())

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
        fvb = sppasFacesVideoBuffer(size=10)
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
        self.assertEqual((0, 9), fvb.get_buffer_range())
        with self.assertRaises(ValueError):
            fvb.get_detected_faces(3)

        # Still no detector was defined... i.e. no model loaded
        with self.assertRaises(sppasError):
            fvb.detect_buffer()

        # Still no detector was defined... i.e. no model loaded
        with self.assertRaises(sppasError):
            fvb.detect_faces_buffer()

    # -----------------------------------------------------------------------

    def test_getters_setters(self):
        vb = sppasFacesVideoBuffer(video=None, size=10)
        self.assertEqual(0, vb.get_filter_best())
        self.assertEqual(0.18, vb.get_filter_confidence())

    # -----------------------------------------------------------------------

    def test_detect(self):
        fvb = sppasFacesVideoBuffer(video=TestFaceBuffer.VIDEO, size=10)
        fvb.next()
        self.assertEqual(10, len(fvb))
        self.assertEqual(10, fvb.tell())
        self.assertEqual((0, 9), fvb.get_buffer_range())

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
            persons = fvb.get_detected_persons(i)
            self.assertEqual(len(faces), len(landmarks))
            self.assertEqual(len(faces), len(persons))
            for x in range(len(faces)):
                self.assertEqual(68, len(landmarks[x]))
                self.assertIsNone(persons[x])

        fvb.set_default_detected_persons()
        for i in range(10):
            all_persons = fvb.get_detected_persons(i)
            self.assertIsInstance(all_persons, list)
            self.assertEqual(len(fvb.get_detected_faces(i)), len(all_persons))
            for j in range(len(all_persons)):
                self.assertEqual(all_persons[j][1], j)

        fvb.next()
        with self.assertRaises(ValueError):
            fvb.get_detected_faces(3)

# ---------------------------------------------------------------------------


class TestSPPASFaceTracking(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    # -----------------------------------------------------------------------

    def test_ann_options(self):
        parameters = sppasParam(["facetrack.json"])
        ann_step_idx = parameters.activate_annotation("facetrack")
        ann_options = parameters.get_options(ann_step_idx)

        for opt in ann_options:
            key = opt.get_key()
            if key in ("nbest", "width", "height"):
                self.assertEqual(0, opt.get_value())
            elif key == "score":
                self.assertEqual(0.2, opt.get_value())
            elif key in ("csv", "video", "folder", "tag", "crop"):
                self.assertFalse(opt.get_value())

    # -----------------------------------------------------------------------

    def test_init(self):
        ann = sppasFaceTrack(log=None)
        self.assertFalse(ann.get_option("csv"))
        self.assertFalse(ann.get_option("video"))
        self.assertFalse(ann.get_option("folder"))
        self.assertFalse(ann.get_option("tag"))
        self.assertFalse(ann.get_option("crop"))
        self.assertEqual(0, ann.get_option("nbest"))
        self.assertEqual(0, ann.get_option("width"))
        self.assertEqual(0, ann.get_option("height"))

        with self.assertRaises(KeyError):
            ann.get_option("toto")

    # -----------------------------------------------------------------------

    def test_getters_setters(self):
        ann = sppasFaceTrack(log=None)
        ann.set_max_faces(3)
        self.assertEqual(3, ann.get_option("nbest"))
        ann.set_min_score(0.5)
        self.assertEqual(0.5, ann.get_option("score"))
        ann.set_out_csv(True)
        self.assertTrue(ann.get_option("csv"))
        ann.set_out_video(True)
        self.assertTrue(ann.get_option("video"))
        ann.set_out_images(True)
        self.assertTrue(ann.get_option("folder"))
        ann.set_img_width(540)
        self.assertEqual(540, ann.get_option("width"))
        ann.set_img_height(760)
        self.assertEqual(760, ann.get_option("height"))

        # Set our custom video buffer and writer and configure them
        # with our options
        vb = sppasFacesVideoBuffer(video=None, size=10)
        vw = sppasVideoCoordsWriter()
        ann.set_videos(vb, vw, options=True)
        self.assertEqual(3, ann.get_option("nbest"))
        self.assertEqual(0.5, ann.get_option("score"))
        self.assertTrue(ann.get_option("csv"))
        self.assertTrue(ann.get_option("video"))
        self.assertTrue(ann.get_option("folder"))
        self.assertEqual(540, ann.get_option("width"))
        self.assertEqual(760, ann.get_option("height"))

        # Set our custom video buffer and writer and set options
        # with their configuration
        vb = sppasFacesVideoBuffer(video=None, size=10)
        self.assertEqual(0.18, vb.get_filter_confidence())
        vw = sppasVideoCoordsWriter()
        ann.set_videos(vb, vw, options=False)
        self.assertEqual(0, ann.get_option("nbest"))
        self.assertEqual(0.18, ann.get_option("score"))
        self.assertFalse(ann.get_option("csv"))
        self.assertFalse(ann.get_option("video"))
        self.assertFalse(ann.get_option("folder"))
        self.assertEqual(0, ann.get_option("width"))
        self.assertEqual(0, ann.get_option("height"))

    # -----------------------------------------------------------------------

    def test_detect(self):
        """No test is done... to do."""
        ann = sppasFaceTrack(log=None)

    # -----------------------------------------------------------------------

    def test_run(self):
        """No test is done... to do."""
        ann = sppasFaceTrack(log=None)
