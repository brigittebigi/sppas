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

    src.videodata.tests.test_coordswriter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest
import cv2

from sppas.src.videodata.coordswriter import sppasVideoCoordsWriter
from sppas.src.videodata.personsbuffer import PersonsBuffer
from sppas.src.videodata.facetracking import FaceTracking
from sppas.src.videodata.videolandmark import VideoLandmark

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    def setUp(self):
        self.__vLandmark = VideoLandmark()
        self.__fTracker = FaceTracking()
        self.__image = cv2.imread("../../../../../../video_test/image0.jpg")
        self.__path = "../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4"
        self.__pBuffer = PersonsBuffer(self.__path, 100, 0)
        self.__cw = sppasVideoCoordsWriter(self.__path, 25, "person",
                                           csv=True, video=True, folder=True)

    # ---------------------------------------------------------------------------

    def test_process1(self):
        self.__pBuffer.next()
        self.__fTracker.detect(self.__pBuffer)
        self.__fTracker.create_persons(self.__pBuffer)
        self.__vLandmark.process(self.__pBuffer)

        x = len(self.__pBuffer._PersonsBuffer__persons)
        self.assertEqual(x, 2)
        for person in self.__pBuffer._PersonsBuffer__persons:
            self.assertEqual(len(person), self.__pBuffer.get_size())
        y = len(self.__pBuffer._PersonsBuffer__landmarks)
        self.assertEqual(y, 2)
        for landmark in self.__pBuffer._PersonsBuffer__landmarks:
            self.assertEqual(len(landmark), self.__pBuffer.get_size())

    # ---------------------------------------------------------------------------

    def test_process2(self):
        self.__pBuffer.next()
        self.__vLandmark.process(self.__pBuffer)

        x = len(self.__pBuffer._PersonsBuffer__persons)
        self.assertEqual(x, 0)
        y = len(self.__pBuffer._PersonsBuffer__landmarks)
        self.assertEqual(y, 1)
        for landmark in self.__pBuffer._PersonsBuffer__landmarks:
            self.assertEqual(len(landmark), self.__pBuffer.get_size())

    # ---------------------------------------------------------------------------

    def test_landmark_person(self):
        self.__pBuffer.next()
        self.__pBuffer.add_landmarks()
        self.__vLandmark.landmark_person(self.__pBuffer, self.__image)

        y = len(self.__pBuffer._PersonsBuffer__landmarks)
        self.assertEqual(y, 1)
        for landmark in self.__pBuffer._PersonsBuffer__landmarks:
            self.assertEqual(len(landmark), 1)

    # ---------------------------------------------------------------------------

    def test_landmark_persons(self):
        self.__pBuffer.next()
        self.__fTracker.detect(self.__pBuffer)
        self.__fTracker.create_persons(self.__pBuffer)
        self.__pBuffer.add_landmarks(2)
        self.__vLandmark._VideoLandmark__landmark_persons(self.__pBuffer, self.__image, 0)

        y = len(self.__pBuffer._PersonsBuffer__landmarks)
        self.assertEqual(y, 2)
        for landmark in self.__pBuffer._PersonsBuffer__landmarks:
            self.assertEqual(len(landmark), 1)

    # ---------------------------------------------------------------------------

    def test_landmark(self):
        y = self.__vLandmark._VideoLandmark__landmark(self.__image)
        self.assertEqual(len(y), 68)

    # ---------------------------------------------------------------------------

    def test_adjust_points(self):
        y = self.__vLandmark._VideoLandmark__adjust_points([(3, 5), (4, 6), (5, 7)], 10, 10)
        self.assertEqual(y, [(13, 15), (14, 16), (15, 17)])

    # ---------------------------------------------------------------------------

