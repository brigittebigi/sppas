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

import logging
import os
import shlex
from subprocess import Popen, PIPE, STDOUT

# ----------------------------------------------------------------------------


class sppasPluginProcess(object):
    """Process one plugin (and only one).

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, plugin_param):
        """Create a new sppasPluginProcess instance.

        :param plugin_param: (sppasPluginParam)

        """
        self._plugin = plugin_param
        self._process = None

    # ------------------------------------------------------------------------

    def run(self, filename):
        """Execute the plugin in batch mode (ie don't wait it to be finished).

        :param filename: (str) The file name of the file on which to apply
        the plugin
        :returns: Process output message

        """
        # the command
        command = self._plugin.get_command()

        # append the options (sorted like in the configuration file)
        for opt in self._plugin.get_options():
            opt_id = opt.get_key()

            if opt_id == "input":
                command += " \'" + filename + "\' "

            elif opt_id == "options":
                value = opt.get_untypedvalue()
                if len(value) > 0:
                    command += " " + value

            elif opt_id == "output":
                value = opt.get_untypedvalue()
                if len(value) > 0:
                    fname = os.path.splitext(filename)[0]
                    command += " \'" + fname + value + "\' "

            elif opt.get_type() == "bool":
                value = opt.get_value()
                if value is True:
                    command += " " + opt.get_key()

            else:
                value = opt.get_untypedvalue()
                if len(value) > 0:
                    command += " " + opt.get_key()
                    if value == "input":
                        command += " \'" + filename + "\' "
                    elif "file" in opt.get_type():
                        command += " \'" + value + "\' "
                    else:
                        command += " " + value

        logging.debug("Execute the command: {:s}".format(command))
        args = shlex.split(command)
        for i, argument in enumerate(args):
            if "PLUGIN_PATH/" in argument:
                newarg = argument.replace("PLUGIN_PATH/", "")
                args[i] = os.path.join(self._plugin.get_directory(), newarg)

        self._process = Popen(args, shell=False,
                              stdout=PIPE,
                              stderr=STDOUT,
                              universal_newlines=True)

    # ------------------------------------------------------------------------

    def communicate(self):
        """Wait for the process and get output messages (if any).

        :returns: output message

        """
        out, err = self._process.communicate()
        return "".join(out)

    # ------------------------------------------------------------------------

    def stop(self):
        """Terminate the process if it is running."""
        if self.is_running() is True:
            self._process.terminate()

    # ------------------------------------------------------------------------

    def is_running(self):
        """Return True if the process is running."""
        if self._process is None:
            return False
        # A None value indicates that the process hasn't terminated yet.
        return self._process.poll() is None
