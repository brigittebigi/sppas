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

    src.videodata.tests.test_facetracking.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest

from sppas.src.videodata.videobuffer import VideoBuffer
from sppas.src.videodata.facetracking import FaceTracking
from sppas.src.imagedata.coordinates import Coordinates

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    def setUp(self):
        self.__fTracker = FaceTracking()
        self.path = "../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4"
        self.__vBuffer = VideoBuffer(self.path, 100, 0)

    # ---------------------------------------------------------------------------

    def test_init(self):
        nb_person = self.__fTracker._FaceTracking__nb_person
        self.assertEqual(nb_person, 0)

        faces = self.__fTracker._FaceTracking__faces
        self.assertEqual(faces, list())

        persons = self.__fTracker._FaceTracking__persons
        self.assertEqual(persons, list())

        size = self.__fTracker._FaceTracking__size
        self.assertEqual(size, 0)

    # ---------------------------------------------------------------------------

    def test_detect(self):
        self.__vBuffer.next()
        self.__fTracker.detect(self.__vBuffer)
        y = len(self.__fTracker._FaceTracking__faces)
        self.assertEqual(y, self.__vBuffer.get_size())
        for face in self.__fTracker._FaceTracking__faces:
            for coord in face:
                self.assertTrue(coord, Coordinates)

    # ---------------------------------------------------------------------------

    def test_all_persons(self):
        self.__vBuffer.next()
        self.__fTracker.detect(self.__vBuffer)
        self.__fTracker.all_persons()
        for face in self.__fTracker._FaceTracking__persons:
            for coord in face:
                self.assertTrue(coord, Coordinates)

    # ---------------------------------------------------------------------------

    def test_several_persons(self):
        self.__fTracker._FaceTracking__nb_person = 1
        self.__vBuffer.next()
        self.__fTracker.detect(self.__vBuffer)
        self.__fTracker.several_persons()
        for face in self.__fTracker._FaceTracking__persons:
            for coord in face:
                self.assertTrue(coord, Coordinates)
        y = len(self.__fTracker._FaceTracking__persons)
        self.assertEqual(y, self.__fTracker._FaceTracking__nb_person)
        for face in self.__fTracker._FaceTracking__persons:
            y = len(face)
            self.assertEqual(y, self.__vBuffer.get_size())

    # ---------------------------------------------------------------------------

    def test_get_persons(self):
        self.__fTracker._FaceTracking__nb_person = 1
        self.__vBuffer.next()
        self.__fTracker.detect(self.__vBuffer)
        self.__fTracker.all_persons()
        for face in self.__fTracker._FaceTracking__persons:
            for coord in face:
                self.assertTrue(coord, Coordinates)

    # ---------------------------------------------------------------------------

    def test_clear(self):
        self.__fTracker._FaceTracking__faces = ["a", "b"]
        faces = self.__fTracker._FaceTracking__faces
        self.assertEqual(faces, ["a", "b"])

        self.__fTracker._FaceTracking__persons = [1, 2]
        persons = self.__fTracker._FaceTracking__persons
        self.assertEqual(persons, [1, 2])

        self.__fTracker._FaceTracking__size = 200
        size = self.__fTracker._FaceTracking__size
        self.assertEqual(size, 200)

        self.__fTracker.clear()

        faces = self.__fTracker._FaceTracking__faces
        self.assertEqual(faces, [])

        persons = self.__fTracker._FaceTracking__persons
        self.assertEqual(persons, [])

        size = self.__fTracker._FaceTracking__size
        self.assertEqual(size, 0)

    # ---------------------------------------------------------------------------

