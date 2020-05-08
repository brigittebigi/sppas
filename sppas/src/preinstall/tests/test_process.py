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

    src.config.tests.test_process.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import unittest

from sppas.src.config.process import Process, Popen, PIPE

# ---------------------------------------------------------------------------


class TestProcess(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        self.__process = Process()

    # ---------------------------------------------------------------------------

    def test_run_popen_out_error(self):
        """Test if the method run_popen, out and error from the class WindowsInstaller works well.

        """
        self.__process.run_popen("pip show wxpython")
        y = str(self.__process.out())
        y = y.split("\\r\\n")[0]
        x = str(self.__process.error())
        self.assertEqual(y, "b'Name: wxPython")
        self.assertEqual(x, "b''")

        self.__process.run_popen("pip show wxpythonnnn")
        y = self.__process.out()
        x = self.__process.error()
        self.assertEqual(y, "b''")
        self.assertEqual(x, "b'WARNING: Package(s) not found: wxpythonnnn\\r\\n'")

    # ---------------------------------------------------------------------------


test = TestProcess()
test.setUp()
test.test_run_popen_out_error()

