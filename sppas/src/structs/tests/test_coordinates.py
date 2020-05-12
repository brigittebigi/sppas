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

    src.structs.tests.test_coordinates.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import unittest

from sppas.src.structs.coordinates import sppasCoordinates

# ---------------------------------------------------------------------------


class TestFeature(unittest.TestCase):

    def setUp(self):
        self.__coordinates = sppasCoordinates(0.7, 143, 17, 150, 98)

    # ---------------------------------------------------------------------------

    def test_init(self):
        confidence = self.__coordinates.get_confidence()
        self.assertEqual(confidence, 0.7)
        x = self.__coordinates.get_x()
        self.assertEqual(x, 143)
        y = self.__coordinates.get_y()
        self.assertEqual(y, 17)
        w = self.__coordinates.get_w()
        self.assertEqual(w, 150)
        h = self.__coordinates.get_h()
        self.assertEqual(h, 98)

    # ---------------------------------------------------------------------------

    def test_get_set_confidence(self):
        self.__coordinates._set_confidence(0.5)
        confidence = self.__coordinates.get_confidence()
        self.assertEqual(confidence, 0.5)

        with self.assertRaises(ValueError):
            self.__coordinates._set_confidence("Bonjour")

        with self.assertRaises(ValueError):
            self.__coordinates._set_confidence(-0.7)

        with self.assertRaises(ValueError):
            self.__coordinates._set_confidence(1.1)

    # ---------------------------------------------------------------------------

    def test_get_set_x(self):
        self.__coordinates._set_x(18)
        x = self.__coordinates.get_x()
        self.assertEqual(x, 18)

        with self.assertRaises(ValueError):
            self.__coordinates._set_x("Bonjour")
        x = self.__coordinates.get_x()
        self.assertEqual(x, 18)

        self.__coordinates._set_x(-5)
        x = self.__coordinates.get_x()
        self.assertEqual(x, 0)

        with self.assertRaises(ValueError):
            self.__coordinates._set_x(15361)
        x = self.__coordinates.get_x()
        self.assertEqual(x, 0)

    # ---------------------------------------------------------------------------

    def test_get_set_y(self):
        self.__coordinates._set_y(18)
        y = self.__coordinates.get_y()
        self.assertEqual(y, 18)

        with self.assertRaises(ValueError):
            self.__coordinates._set_y("Bonjour")
        y = self.__coordinates.get_y()
        self.assertEqual(y, 18)

        self.__coordinates._set_y(-5)
        y = self.__coordinates.get_y()
        self.assertEqual(y, 0)

        with self.assertRaises(ValueError):
            self.__coordinates._set_y(8641)
        y = self.__coordinates.get_y()
        self.assertEqual(y, 0)

    # ---------------------------------------------------------------------------

    def test_get_set_w(self):
        self.__coordinates._set_w(18)
        w = self.__coordinates.get_w()
        self.assertEqual(w, 18)

        with self.assertRaises(ValueError):
            self.__coordinates._set_w("Bonjour")
        w = self.__coordinates.get_w()
        self.assertEqual(w, 18)

        with self.assertRaises(ValueError):
            self.__coordinates._set_w(-5)
        w = self.__coordinates.get_w()
        self.assertEqual(w, 18)

        with self.assertRaises(ValueError):
            self.__coordinates._set_w(15361)
        w = self.__coordinates.get_w()
        self.assertEqual(w, 18)

    # ---------------------------------------------------------------------------

    def test_get_set_h(self):
        self.__coordinates._set_h(18)
        h = self.__coordinates.get_h()
        self.assertEqual(h, 18)

        with self.assertRaises(ValueError):
            self.__coordinates._set_h("Bonjour")
        h = self.__coordinates.get_h()
        self.assertEqual(h, 18)

        with self.assertRaises(ValueError):
            self.__coordinates._set_h(-5)
        h = self.__coordinates.get_h()
        self.assertEqual(h, 18)

        with self.assertRaises(ValueError):
            self.__coordinates._set_h(8641)
        h = self.__coordinates.get_h()
        self.assertEqual(h, 18)

    # ---------------------------------------------------------------------------

    def test_guess_portrait(self):
        new_coordinates = self.__coordinates.guess_portrait()
        x = new_coordinates.get_x()
        self.assertEqual(x, 68)
        y = new_coordinates.get_y()
        self.assertEqual(y, 17)
        w = new_coordinates.get_w()
        self.assertEqual(w, 300)
        h = new_coordinates.get_h()
        self.assertEqual(h, 196)

    # ---------------------------------------------------------------------------
