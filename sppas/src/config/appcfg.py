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

    src.config.appcfg.py
    ~~~~~~~~~~~~~~~~~~~~~

"""

import os
import sys
import json

from .settings import sppasBaseSettings
from .settings import sppasGlobalSettings
from .settings import sppasPathSettings

# ---------------------------------------------------------------------------


class sppasAppConfig(sppasBaseSettings):
    """Configuration for any SPPAS Application.

        :author:       Florian Hocquet, Brigitte Bigi
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new sppasAppConfig instance.

            The configuration is set to its default values and updated
            with the content of a configuration file (if existing).
            The configuration is saved when this instance is deleted.

        """
        super(sppasAppConfig, self).__init__()

        with sppasGlobalSettings() as sg:
            name = sg.__name__ + " " + sg.__version__

        # Create a default configuration
        self.__dict__ = dict(
            name=name,
            log_level=0,  # 15,
            quiet_log_level=30,
            log_file=None,
            splash_delay=3,
            deps=dict()
        )

        # Load the existing configuration file (if any)
        self.load()

    # -----------------------------------------------------------------------

    def set(self, key, value):
        """Set any member of this config.

        :param key: (str)
        :param value: (any type)

        """
        setattr(self, key, value)

    # -----------------------------------------------------------------------

    @staticmethod
    def cfg_filename():
        """Return the name of the config file."""
        with sppasPathSettings() as paths:
            cfg_filename = os.path.join(paths.basedir, ".deps~")
        return cfg_filename

    # -----------------------------------------------------------------------

    def cfg_file_exists(self):
        """Return if the config file exists or not."""
        cfg = self.cfg_filename()
        if cfg is None:
            return False

        return os.path.exists(cfg)

    # ------------------------------------------------------------------------

    def load(self):
        """Override. Load the configuration from a file."""
        if self.cfg_file_exists() is True:
            with open(self.cfg_filename()) as cfg:
                self.__dict__["deps"] = json.load(cfg)

    # ------------------------------------------------------------------------

    def save(self):
        """Override. Save the dictionary in a file."""
        # Admin rights are needed to write in an hidden file.
        # So it's needed to switch the file in a normal mode
        # to modify it and then to hide back the file.
        self.hide_unhide(".deps~", "-")
        with open(self.cfg_filename(), "w") as f:
            f.write(json.dumps(self.__dict__["deps"], indent=2))
        self.hide_unhide(".deps~", "+")

    # ------------------------------------------------------------------------

    def hide_unhide(self, filename, operator):
        """Hide or un-hide a file.

        :param filename: (str)
        :param operator: ()

        """
        if filename.startswith(".") is False:
            filename = "." + filename

        if filename.endswith("~") is False:
            filename = filename + "~"

        system = sys.platform
        with sppasPathSettings() as sp:
            config = os.path.join(sp.basedir, filename)
        if system == "win32":
            p = os.popen('attrib ' + operator + 'h ' + config)
            p.close()
        return filename

    # ------------------------------------------------------------------------
    # Methods related to the list of dependencies for the features.
    # ------------------------------------------------------------------------

    def get_deps(self):
        """Return the list of dependency features."""
        return list(self.__dict__["deps"].keys())

    # ------------------------------------------------------------------------

    def dep_enabled(self, key):
        """Return True if a dependency is enabled.

        :param key: (str) Identifier of a feature.

        """
        if key not in self.__dict__["deps"]:
            return False
        return self.__dict__["deps"][key]

    # ------------------------------------------------------------------------

    def set_dep(self, key, value):
        """Add or update a dependency feature.

        This change is set to the current dict but is not saved in the
        configuration file.

        :param key: (str) Identifier of a feature
        :param value: (bool) Enabled or disabled

        """
        self.__dict__["deps"][key] = value

