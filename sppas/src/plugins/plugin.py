#!/usr/bin/env python
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

    src.plugins.plugin.py
    ~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import json
import os
import platform
import shlex
import signal
from subprocess import Popen

from sppas.src.structs import sppasOption
from sppas import IOExtensionError

from .pluginsexc import PluginConfigFileError
from .pluginsexc import CommandExecError
from .pluginsexc import CommandSystemError
from .pluginsexc import OptionKeyError

# ----------------------------------------------------------------------------


class sppasPluginParam(object):
    """Class to represent the set of parameters of a plugin.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The set of parameters of a plugin is made of a directory name, a
    configuration file name and a sppasPluginParser. This latter allows to
    get all information related to the plugin from the configuration file
    name:

        - the plugin configuration: identifier, name, description and icon;
        - the commands for windows, macos and linux;
        - a set of options, each one containing at least an identifier,
        and optionally a type, a value and a description text.

    """

    def __init__(self, directory, config_file):
        """Create a new sppasPluginParam instance.

        :param directory: (str) the directory where to find the plugin
        :param config_file: (str) the file name of the plugin configuration

        """
        # The path where to find the plugin and its config
        self._directory = directory
        self._cfgfile = config_file

        # Declare members and initialize:

        # An identifier to represent this plugin
        self._key = None
        # The name of the plugin
        self._name = ""
        # The description of the plugin do
        self._descr = ""
        # The icon of the plugin application
        self._icon = ""

        # The command to be executed and its options
        self._command = ""
        self._options = list()
        # OK... fill members from the given file
        self.parse()

    # ------------------------------------------------------------------------

    def reset(self):
        """Reset all members to their default value."""
        self._key = None
        self._name = ""
        self._descr = ""
        self._icon = ""

        self._command = ""
        self._options = list()

    # ------------------------------------------------------------------------

    def parse(self):
        """Parse the configuration file of the plugin."""
        self.reset()
        filename = os.path.join(self._directory, self._cfgfile)
        if filename.endswith('json'):

            if os.path.exists(filename) is False:
                raise PluginConfigFileError

            # Read the whole file content
            with open(filename) as cfg:
                conf = json.load(cfg)

            self._key = conf['id']
            self._name = conf.get("name", "")
            self._descr = conf.get("descr", "")
            self._icon = conf.get("icon", "")

            # get the command
            command = self.__get_command(conf['commands'])
            if self.__check_command(command) is False:
                raise CommandExecError(command)
            self._command = command

            for new_option in conf['options']:
                opt = sppasOption(new_option['id'])
                opt.set_type(new_option['type'])
                opt.set_value(str(new_option['value']))  # dangerous cast
                opt.set_text(new_option.get('text', ""))
                self._options.append(opt)

        else:
            raise IOExtensionError(filename)

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_directory(self):
        """Get the directory name of the plugin."""
        return self._directory

    # ------------------------------------------------------------------------

    def get_key(self):
        """Get the identifier of the plugin."""
        return self._key

    def get_name(self):
        """Get the name of the plugin."""
        return self._name

    def get_descr(self):
        """Get the short description of the plugin."""
        return self._descr

    def get_icon(self):
        """Get the icon file name of the plugin."""
        return self._icon

    # ------------------------------------------------------------------------

    def get_command(self):
        """Get the appropriate command to execute the plugin."""
        return self._command

    # ------------------------------------------------------------------------

    def get_option_from_key(self, key):
        """Get an option from its key."""
        for option in self._options:
            if option.get_key() == key:
                return option
        raise OptionKeyError(key)

    def get_options(self):
        """Get all the options."""
        return self._options

    def set_options(self, options_dict):
        """Fix the options."""
        self._options = options_dict

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    @staticmethod
    def __get_command(commands):
        """Return the appropriate command from a list of available ones."""
        _system = platform.system().lower()

        if ('windows' in _system or 'cygwin' in _system) and \
                'windows' in commands.keys():
            return commands['windows']

        if 'darwin' in _system and 'macos' in commands.keys():
            return commands['macos']

        if 'linux' in _system and 'linux' in commands.keys():
            return commands['linux']

        raise CommandSystemError(_system, commands.keys())

    # ------------------------------------------------------------------------

    @staticmethod
    def __check_command(command):
        """Return True if command exists.

        Test only the main command (i.e. the first string, without args).

        """
        logging.debug("Test of the command: {:s}".format(command))
        command_args = shlex.split(command)
        test_command = command_args[0]

        NULL = open(os.path.devnull, 'w')
        try:
            p = Popen([test_command], shell=False, stdout=NULL, stderr=NULL)
        except OSError:
            NULL.close()
            return False

        # Get the process id & try to terminate it gracefully
        pid = p.pid
        p.terminate()

        # Check if the process has really terminated & force kill if not.
        try:
            os.kill(pid, signal.SIGINT)
            p.kill()
            # print("Forced kill")
        except OSError:
            # print("Terminated gracefully")
            pass
        NULL.close()
        return True
