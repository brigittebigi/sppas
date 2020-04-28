#!/usr/bin/env python
# -*- coding : UTF-8 -*-
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

        src.config.configuration.py
    ~~~~~~~~~~~~~~~~

:author:       Florian Hocquet
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      the class Feature of SPPAS

"""

import os
import json

from sppas.src.config.sglobal import sppasBaseSettings
from sppas.src.config.sglobal import sppasGlobalSettings
from sppas.src.config.support import sppasPathSettings


# ---------------------------------------------------------------------------


class Configuration(sppasBaseSettings):
    """Creation features.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

    """

    def __init__(self):
        """Create a new Configuration instance.

        """
        super(Configuration, self).__init__()

        with sppasGlobalSettings() as sg:
            name = sg.__name__ + " " + sg.__version__

        self.__dict__ = dict(
            cfg_exist=False,
            file=None,
            file_dict={"deps": {}}
        )
        self.load()

    # -----------------------------------------------------------------------

    def load(self):
        """Load the dictionary of features from a file."""
        with sppasPathSettings() as sp:
            config = os.path.join(sp.basedir, ".deps~")
            self.__dict__["file"] = config

            if os.path.exists(config) is False:
                self.set_cfg_exist(False)
            else:
                self.set_cfg_exist(True)
                with open(config) as cfg:
                    file = json.load(cfg)
                    self.__dict__["file_dict"] = file

    # ---------------------------------------------------------------------------

    def save(self):
        """Save the dictionary of settings in a file.

        To be overridden.

        """
        with open(self.get_file(), "w") as f:
            f.write(json.dumps(self.get_file_dict(), indent=2))

    # ---------------------------------------------------------------------------

    def get_file(self):
        """Return the dictionnary self.__dict__["file_dict"].

        """
        return self.__dict__["file"]

    # ---------------------------------------------------------------------------

    def get_file_dict(self):
        """Return the dictionnary self.__dict__["file_dict"].

        """
        return self.__dict__["file_dict"]

    # ---------------------------------------------------------------------------

    def get_deps(self):
        """Return the dictionnary self.__dict__["file_dict"].

        """
        return self.__dict__["file_dict"]["deps"]

    # ---------------------------------------------------------------------------

    def add_deps(self, key, value):
        """Add a feature in self.__dict__["file_dict"].

        :param key: (str()) The key
        :param value: (str()) The value

        """
        self.__dict__["file_dict"]["deps"][key] = value

    # ---------------------------------------------------------------------------

    def modify_deps(self, key, value):
        """Modify the value of a feature in self.__dict__["file_dict"].

        :param key: (str()) The key
        :param value: (str()) The value

        """
        self.__dict__["file_dict"]["deps"][key] = value

    # ---------------------------------------------------------------------------

    def set_deps(self, dependencies):
        """Set self.__dict__["file_dict"] with another dictionary.

        :param dependencies: (str()) The dictionary you want to replace self.__dict__["deps"].


        """
        if isinstance(dependencies, dict) is False:
            raise NotImplementedError
        else:
            self.__dict__["file_dict"]["deps"] = dependencies

    # ---------------------------------------------------------------------------

    def get_cfg_exist(self):
        """Return if the file exist or not.

        """
        return self.__dict__["cfg_exist"]

    # ---------------------------------------------------------------------------

    def set_cfg_exist(self, value):
        """Set the value of self.__dict__["cfg_exist"]

        :param value: (bool()) The value you want to affect to self.__dict__["cfg_exist"].

        """
        value = bool(value)
        self.__dict__["cfg_exist"] = value

