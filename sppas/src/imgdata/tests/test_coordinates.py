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

    src.imgdata.tests.test_coordinates.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest

from ..coordinates import sppasCoords

# ---------------------------------------------------------------------------


class TestCoordinates(unittest.TestCase):

    def setUp(self):
        self.__coordinates = sppasCoords(143, 17, 150, 98, 0.7)

    # ---------------------------------------------------------------------------

    def test_init(self):
        confidence = self.__coordinates.get_confidence()
        self.assertEqual(confidence, 0.7)
        x = self.__coordinates.x
        self.assertEqual(x, 143)
        y = self.__coordinates.y
        self.assertEqual(y, 17)
        w = self.__coordinates.w
        self.assertEqual(w, 150)
        h = self.__coordinates.h
        self.assertEqual(h, 98)

    # ---------------------------------------------------------------------------

    def test_get_set_confidence(self):
        self.__coordinates._sppasCoords__set_confidence(0.5)
        confidence = self.__coordinates.get_confidence()
        self.assertEqual(confidence, 0.5)

        with self.assertRaises(TypeError):
            self.__coordinates._sppasCoords__set_confidence("Bonjour")

        with self.assertRaises(ValueError):
            self.__coordinates._sppasCoords__set_confidence(-0.7)

        with self.assertRaises(ValueError):
            self.__coordinates._sppasCoords__set_confidence(1.1)

    # ---------------------------------------------------------------------------

    def test_get_set_x(self):
        self.__coordinates.x = 18
        x = self.__coordinates.x
        self.assertEqual(x, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.x = "Bonjour"
        x = self.__coordinates.x
        self.assertEqual(x, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.x = -5
        x = self.__coordinates.x
        self.assertEqual(x, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.x = 15361
        x = self.__coordinates.x
        self.assertEqual(x, 18)

    # ---------------------------------------------------------------------------

    def test_get_set_y(self):
        self.__coordinates.y = 18
        y = self.__coordinates.y
        self.assertEqual(y, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.y = "Bonjour"
        y = self.__coordinates.y
        self.assertEqual(y, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.y = -5
            y = self.__coordinates.y
            self.assertEqual(y, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.y = 8641
        y = self.__coordinates.y
        self.assertEqual(y, 18)

    # ---------------------------------------------------------------------------

    def test_get_set_w(self):
        self.__coordinates.w = 18
        w = self.__coordinates.w
        self.assertEqual(w, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.w = "Bonjour"
        w = self.__coordinates.w
        self.assertEqual(w, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.w = -5
        w = self.__coordinates.w
        self.assertEqual(w, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.w = 15361
        w = self.__coordinates.w
        self.assertEqual(w, 18)

    # ---------------------------------------------------------------------------

    def test_get_set_h(self):
        self.__coordinates.h = 18
        h = self.__coordinates.h
        self.assertEqual(h, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.h = "Bonjour"
        h = self.__coordinates.h
        self.assertEqual(h, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.h = -5
        h = self.__coordinates.h
        self.assertEqual(h, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.h = 8641
        h = self.__coordinates.h
        self.assertEqual(h, 18)

    # ---------------------------------------------------------------------------

    def test_scale(self):
        coordinates = sppasCoords(143, 17, 150, 98)
        shift_x, shift_y = coordinates.scale(2.)
        self.assertEqual(coordinates.w, 300)
        self.assertEqual(coordinates.h, 196)
        self.assertEqual(shift_x, -75)
        self.assertEqual(shift_y, -49)

        coordinates = sppasCoords(143, 17, 150, 98)
        shift_x, shift_y = coordinates.scale(3)
        self.assertEqual(coordinates.w, 450)
        self.assertEqual(coordinates.h, 294)
        self.assertEqual(shift_x, -150)

        coordinates = sppasCoords(143, 17, 150, 98)
        shift_x, shift_y = coordinates.scale("0.5")
        self.assertEqual(coordinates.w, 75)
        self.assertEqual(coordinates.h, 49)
        self.assertEqual(shift_x, 37)  # it's 37.5... rounded to 37.

        with self.assertRaises(TypeError):
            self.__coordinates.scale("a")

    # ---------------------------------------------------------------------------

    def test_shift(self):
        self.__coordinates.shift(20)
        x = self.__coordinates.x
        self.assertEqual(x, 163)

        self.__coordinates.shift(-20)
        x = self.__coordinates.x
        self.assertEqual(x, 143)

        self.__coordinates.shift(20, 10)
        x = self.__coordinates.x
        y = self.__coordinates.y
        self.assertEqual(x, 163)
        self.assertEqual(y, 27)

        self.__coordinates.shift(-20, -10)
        x = self.__coordinates.x
        y = self.__coordinates.y
        self.assertEqual(x, 143)
        self.assertEqual(y, 17)

        with self.assertRaises(TypeError):
            self.__coordinates.shift("a", "a")

        self.__coordinates.shift(20, -20)
        y = self.__coordinates.y
        self.assertEqual(y, 0)

    # ---------------------------------------------------------------------------

    def test_equal(self):
        self.assertTrue(self.__coordinates == ([143, 17, 150, 98, 0.2]))
        self.assertFalse(self.__coordinates != ([143, 17, 150, 98, 0.2]))
        self.assertTrue(self.__coordinates != ([14, 1, 150, 98]))

        c = sppasCoords(143, 17, 150, 98)
        self.assertTrue(self.__coordinates.__eq__(c))

        c = sppasCoords(143, 17, 150, 200)
        self.assertFalse(self.__coordinates.__eq__(c))

    # ---------------------------------------------------------------------------

    def test_copy(self):
        c = self.__coordinates.copy()
        self.assertEqual(c, sppasCoords(143, 17, 150, 98))
        self.assertTrue(self.__coordinates.__eq__(c))

    # ---------------------------------------------------------------------------

    def test_print(self):
        c = sppasCoords(143, 17, 150, 98)
        self.assertEqual(str(c), "(143, 17) (150, 98): 0.0")


