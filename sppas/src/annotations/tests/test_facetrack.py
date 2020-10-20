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

    src.annotations.tests.test_facetrack.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import unittest

from sppas.src.config import paths
from sppas.src.exceptions import sppasError
from sppas.src.annotations.param import sppasParam
from sppas.src.videodata import sppasVideoReaderBuffer
from sppas.src.imgdata import sppasImageCoordsWriter, sppasImage

from ..FaceTracking.videotrackwriter import sppasVideoCoordsWriter
from ..FaceTracking.facebuffer import sppasFacesVideoBuffer
from ..FaceTracking.sppasfacetrack import sppasFaceTrack
from ..FaceTracking.facetrack import FaceRecognition
from ..FaceTracking.facetrack import FaceTracking
from ..FaceDetection.facedetection import FaceDetection

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
        with self.assertRaises(ValueError):
            vb.set_detected_persons(0, list())
        with self.assertRaises(ValueError):
            vb.set_person_coords(0, "X000", list())

    # -----------------------------------------------------------------------

    def test_detect_getters(self):
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

        fvb.close()

    # -----------------------------------------------------------------------

    def test_detect_setters(self):
        fvb = sppasFacesVideoBuffer(video=TestFaceBuffer.VIDEO, size=10)
        fvb.load_fd_model(NET, HAAR1, HAAR2)
        fvb.next()
        fvb.detect_faces_buffer()

        # wrong buffer index
        with self.assertRaises(ValueError):
            fvb.set_person_coords(20, "X000", list())

        # wrong sppasCoords type
        with self.assertRaises(TypeError):
            fvb.set_person_coords(5, "X000", 'bla bla')

        # detect faces of the buffer
        all_faces = fvb.get_detected_faces(5)
        all_persons = fvb.get_detected_persons(5)
        self.assertEqual(len(all_faces), 1)  # 1 face is detected
        self.assertEqual(345, all_faces[0].x)
        self.assertEqual(50, all_faces[0].y)
        self.assertEqual(262, all_faces[0].w)
        self.assertEqual(262, all_faces[0].h)
        self.assertIsNone(all_persons[0])    # no person is assigned to the face

        # set a person_id to each detected face
        fvb.set_default_detected_persons()
        all_persons = fvb.get_detected_persons(5)
        self.assertEqual(("X000", 0), all_persons[0])

        # something normal... change coords of the detected person
        fvb.set_person_coords(5, "X000", (150, 160, 200, 210, 0.4))
        self.assertEqual(150, all_faces[0].x)
        self.assertEqual(160, all_faces[0].y)
        self.assertEqual(200, all_faces[0].w)
        self.assertEqual(210, all_faces[0].h)

        # something normal... add coords for a non-detected person
        fvb.set_person_coords(5, "toto", (400, 410, 200, 210, 0.2))
        all_faces = fvb.get_detected_faces(5)
        self.assertEqual(len(all_faces), 2)  # 1 face is detected + added one
        self.assertEqual(150, all_faces[0].x)
        self.assertEqual(160, all_faces[0].y)
        self.assertEqual(200, all_faces[0].w)
        self.assertEqual(210, all_faces[0].h)
        self.assertEqual(400, all_faces[1].x)
        self.assertEqual(410, all_faces[1].y)
        self.assertEqual(200, all_faces[1].w)
        self.assertEqual(210, all_faces[1].h)
        all_persons = fvb.get_detected_persons(5)
        self.assertEqual(len(all_persons), 2)  # 1 person is detected + added one

        fvb.close()

    # -----------------------------------------------------------------------

    def test_detect_set_persons(self):
        fvb = sppasFacesVideoBuffer(video=TestFaceBuffer.VIDEO, size=10)
        fvb.load_fd_model(NET, HAAR1, HAAR2)
        fvb.next()
        fvb.detect_faces_buffer()
        fvb.set_default_detected_persons()

        person_coords = fvb.coords_by_person()
        self.assertEqual(1, len(person_coords))
        self.assertTrue("X000" in person_coords)
        self.assertEqual(10, len(person_coords["X000"]))
        self.assertTrue(person_coords["X000"][4].x in range(340, 350))
        self.assertTrue(person_coords["X000"][4].y in range(49, 51))
        self.assertTrue(person_coords["X000"][4].w in range(260, 270))
        self.assertTrue(person_coords["X000"][4].h in range(260, 270))

        fvb.set_person_coords(4, "toto", (400, 410, 200, 210, 0.2))
        person_coords = fvb.coords_by_person()
        self.assertEqual(2, len(person_coords))
        self.assertTrue("X000" in person_coords)
        self.assertTrue("toto" in person_coords)
        self.assertEqual(10, len(person_coords["X000"]))
        self.assertEqual(10, len(person_coords["toto"]))

        for i in range(0, 4):
            self.assertIsNone(person_coords["toto"][i])
        for i in range(5, 10):
            self.assertIsNone(person_coords["toto"][i])
        self.assertEqual(400, person_coords["toto"][4].x)
        self.assertEqual(410, person_coords["toto"][4].y)

        fvb.close()

# ---------------------------------------------------------------------------


class TestFaceRecognition(unittest.TestCase):

    PHOTO1 = "/E/Photos/BientotQuadra1.jpg"
    PHOTO2 = "/E/Photos/BientotQuadra2.jpg"

    def setUp(self):
        # Detect persons of photo 1
        self.img1 = sppasImage(filename=TestFaceRecognition.PHOTO1)
        fd = FaceDetection()
        fd.load_model(NET, HAAR1, HAAR2)
        fd.detect(self.img1)
        fd.to_portrait(self.img1)
        self.coords1 = [x.copy() for x in fd]
        self.assertEqual(7, len(self.coords1))

        fn = os.path.join(DATA, "BientotQuadra1-face.png")
        w = sppasImageCoordsWriter()
        w.set_options(tag=True)
        w.write(self.img1, self.coords1, fn)
        self.persons = dict()
        self.persons["lea"] = self.img1.icrop(fd[0])
        self.persons["beatrice"] = self.img1.icrop(fd[1])
        self.persons["gael"] = self.img1.icrop(fd[2])
        self.persons["myriam"] = self.img1.icrop(fd[3])
        self.persons["roselyne"] = self.img1.icrop(fd[4])
        self.persons["brigitte"] = self.img1.icrop(fd[5])
        self.persons["franck"] = self.img1.icrop(fd[6])

        # Detect persons of photo 2
        self.img2 = sppasImage(filename=TestFaceRecognition.PHOTO2)
        fd = FaceDetection()
        fd.load_model(NET, HAAR1, HAAR2)
        fd.detect(self.img2)
        fd.to_portrait(self.img2)
        self.coords2 = [x.copy() for x in fd]
        self.assertEqual(7, len(self.coords2))

        fn = os.path.join(DATA, "BientotQuadra2-face.png")
        w = sppasImageCoordsWriter()
        w.set_options(tag=True)
        w.write(self.img2, self.coords2, fn)

    def test_score_img_similarity_fr(self):
        img_faces = [self.img2.icrop(c) for c in self.coords2]

        # So, now we have portraits of the known persons and
        # their portrait in a new image. Can we match the persons?
        fr = FaceRecognition(self.persons)

        # in img_faces, beatrice is at index 0.
        d = fr.scores_img_similarity(img_faces[0])
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("beatrice", ds[0][0])

        d = fr.scores_img_similarity(img_faces[1])
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("myriam", ds[0][0])

        d = fr.scores_img_similarity(img_faces[2])
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("roselyne", ds[0][0])

        # Recognition error ********************** : brigitte expected
        # brigitte detected at index 5 in image1 and at index 3 in image2
        d = fr.scores_img_similarity(img_faces[3])
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("beatrice", ds[0][0])
        self.assertEqual("brigitte", ds[1][0])

        d = fr.scores_img_similarity(img_faces[4])
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("franck", ds[0][0])

        d = fr.scores_img_similarity(img_faces[5])
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("gael", ds[0][0])

        d = fr.scores_img_similarity(img_faces[6])
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("lea", ds[0][0])

    # -----------------------------------------------------------------------

    def test_score_img_similarity_ft(self):
        img2_faces = [self.img2.icrop(c) for c in self.coords2]

        ft = FaceTracking()
        # in img2_faces, beatrice is at index 0.
        scores = ft._scores_img_similarity(
            img2_faces[0],           # detected portrait of beatrice in image2
            self.persons.values(),   # all detected portraits in image1
            ref_coords=self.coords2[0],      # coords of beatrice in image2
            compare_coords=self.coords1)     # all detected coords in image1
        d = dict()
        for p, s in zip(self.persons, scores):
            d[p] = s
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("beatrice", ds[0][0])

        # in img2_faces, brigitte is at index 3. BUT NOT RECOGNIZED
        scores = ft._scores_img_similarity(
            img2_faces[3],  # detected portrait of brigitte in image2
            self.persons.values(),  # all detected portraits in image1
            ref_coords=self.coords2[3],  # coords of brigitte in image2
            compare_coords=self.coords1)  # all detected coords in image1
        d = dict()
        for p, s in zip(self.persons, scores):
            d[p] = s
        ds = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.assertEqual("beatrice", ds[0][0])
        self.assertEqual("brigitte", ds[1][0])

    # -----------------------------------------------------------------------

    def test_get_best_scores(self):
        img2_faces = [self.img2.icrop(c) for c in self.coords2]

        ft = FaceTracking()

        # if we detected several persons in image 1 but only one in image 2
        scores = ft._scores_img_similarity(
            img2_faces[0],  # i-th detected portrait in image2
            self.persons.values(),  # all detected portraits in image1
            ref_coords=self.coords2[0],  # i-th coords in image2
            compare_coords=self.coords1)  # all detected coords in image1
        best_scores = ft._get_best_scores([scores])
        self.assertEqual([1], best_scores)

        all_scores = list()
        for i in range(len(img2_faces)):
            scores_i = ft._scores_img_similarity(
                img2_faces[i],           # i-th detected portrait in image2
                self.persons.values(),   # all detected portraits in image1
                ref_coords=self.coords2[i],    # i-th coords in image2
                compare_coords=self.coords1)   # all detected coords in image1
            all_scores.append(scores_i)

        best_scores = ft._get_best_scores(all_scores)
        self.assertEqual([1, 3, 4, 5, 6, 2, 0], best_scores)

# ---------------------------------------------------------------------------


class TestFaceTracking(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    # -----------------------------------------------------------------------

    def test_create_initial_image_data(self):
        fvb = sppasFacesVideoBuffer(video=TestFaceBuffer.VIDEO, size=20)
        fvb.load_fd_model(NET, HAAR1, HAAR2)
        fvb.next()
        fvb.detect_faces_buffer()
        # 1 face is detected in the 1st image (344, 49) (264, 264): 0.504026
        self.assertEqual(1, len(fvb.get_detected_faces(0)))
        self.assertEqual(1, len(fvb.get_detected_persons(0)))
        # but no person is defined.
        self.assertIsNone(fvb.get_detected_persons(0)[0])

        ft = FaceTracking()
        ft._create_initial_image_data(fvb)
        # now we expect that the 1st image has 1 associated person
        persons = fvb.get_detected_persons(0)
        self.assertEqual(1, len(persons))
        self.assertEqual("X000", persons[0][0])
        self.assertEqual(0, persons[0][1])

        ft.invalidate()
        ft._track_persons(fvb)

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
