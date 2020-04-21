# -*- coding: UTF-8 -*-
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

    src.ui.tests.test_wkps.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO IMPORTS ISSUES

"""
import unittest

from ..wkps import sppasWorkspaces

#
# /!\ problème avec les imports
#


class TestSppasWorkspaces(unittest.TestCase):

    def setUp(self):
        self.ws = sppasWorkspaces()
        self.dic = {"paths": [{"id": "./", "roots": [{"id": "./", "files": [{"id": "./"}]}]}]}
        self.dic2 = {"paths": [{"id": "", "roots": [{"id": "", "files": [{"id": ""}]}]}]}

    def testVerify_path_exist(self):
        self.assertTrue(self.ws.verify_path_exist(self.dic))
        self.assertFalse(self.ws.verify_path_exist(self.dic2))

    def testmodify_path(self):
        self.ws.modify_path(self.dic, "new_path")
        d = self.dic['path']
        for elem in d['id']:
            self.assertEqual(elem, "new_path")

