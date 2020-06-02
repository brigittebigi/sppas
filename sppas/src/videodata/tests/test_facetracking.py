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

from sppas.src.videodata.personsbuffer import PersonsBuffer
from sppas.src.videodata.facetracking import FaceTracking
from sppas.src.imagedata.coordinates import Coordinates

# ---------------------------------------------------------------------------


class TestVideoBuffer(unittest.TestCase):

    def setUp(self):
        self.path = "../../../../../corpus/Test_01_Celia_Brigitte/montage_compressed.mp4"
        self.__pBuffer = PersonsBuffer(self.path, 100, 0)
        self.__fTracker = FaceTracking()

    # ---------------------------------------------------------------------------

    def test_init(self):
        faces = self.__fTracker._FaceTracking__faces
        self.assertEqual(faces, list())

        persons = self.__pBuffer._PersonsBuffer__persons
        self.assertEqual(persons, list())

        size = self.__fTracker._FaceTracking__max_persons
        self.assertEqual(size, 0)

    # ---------------------------------------------------------------------------

    def test_detect(self):
        self.__pBuffer.next()
        self.__fTracker.detect(self.__pBuffer)
        y = len(self.__fTracker._FaceTracking__faces)
        self.assertEqual(y, self.__pBuffer.get_size())
        for face in self.__pBuffer._PersonsBuffer__persons:
            for coord in face:
                self.assertTrue(coord, Coordinates)

    # ---------------------------------------------------------------------------

    def test_all_persons(self):
        self.__pBuffer.next()
        self.__fTracker.detect(self.__pBuffer)
        self.__fTracker.all_persons(self.__pBuffer)
        for face in self.__pBuffer._PersonsBuffer__persons:
            for coord in face:
                try:
                    self.assertIsInstance(coord, Coordinates)
                except:
                    self.assertEqual(coord, None)

    # ---------------------------------------------------------------------------

    def test_several_persons(self):
        self.__pBuffer.next()
        self.__fTracker.detect(self.__pBuffer)
        self.__fTracker.several_persons(self.__pBuffer, nb_person=1)
        for face in self.__pBuffer._PersonsBuffer__persons:
            for coord in face:
                self.assertTrue(coord, Coordinates)
        y = self.__pBuffer.nb_persons()
        self.assertEqual(y, 1)
        for face in self.__pBuffer._PersonsBuffer__persons:
            y = len(face)
            self.assertEqual(y, self.__pBuffer.get_size())

    # ---------------------------------------------------------------------------

