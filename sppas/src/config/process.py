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

    src.plugins.process.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

import shlex
from subprocess import Popen, PIPE


# ----------------------------------------------------------------------------


class Process:
    """Execute and read a subProcess

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
    :summary:      the class Process of SPPAS

    A Process is a wrapper of subprocess.Popen command.
    It can launch a command :

    >>> p = Process()
    >>> p.run_popen("ls -l")

    Return the stdout of a command :

    >>> p.out()

    Return the stderr of a command :

    >>> p.error()

    Stop a command :

    >>> p.stop()

    Return the state of a command :

    >>> p.is_running()

    """

    def __init__(self):
        """Create a new Process instance."""
        self.__process = None

    # ------------------------------------------------------------------------

    def run_popen(self, command):
        """Execute command with subprocess.Popen.

        :param command: (str) The command you want to execute
        :returns: Process error message
        :returns: Process output message

        """
        command = command.strip()
        command_args = shlex.split(command)
        self.__process = Popen(command_args, stdout=PIPE, stderr=PIPE, text=True)
        self.__process.wait()

    # ------------------------------------------------------------------------

    def out(self):
        """Return the stdout of your process.

        :returns: output message

        """
        out = self.__process.stdout.read()
        out = str(out)
        return out

    # ------------------------------------------------------------------------

    def error(self):
        """Return the stderr of your process.

        :returns: error message

        """
        error = self.__process.stderr.read()
        error = str(error)
        return error

    # ------------------------------------------------------------------------

    def stop(self):
        """Terminate the process if it is running."""
        if self.is_running() is True:
            self.__process.terminate()

    # ------------------------------------------------------------------------

    def is_running(self):
        """Return True if the process is running."""
        if self.__process is None:
            return False
        return self.__process.poll() is None