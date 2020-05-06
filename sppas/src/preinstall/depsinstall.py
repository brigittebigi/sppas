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

    src.preinstall.depsinstall.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import sys
import os
import logging

from .installer import Deb, Dnf, Rpm, Windows, MacOs

# ---------------------------------------------------------------------------


class sppasInstallerDeps(object):
    """Main class to manage the installation of external features.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    sppasInstallerDeps is a wrapper of Installer Object.
    It only allows :
    - to launch the installation process,
    - to get informations, which are important for the users,
    about the pre-installation.
    - to configure parameters to get a personalized installation.

    For example:

    >>> install = sppasInstallerDeps()

    See what is availabled or not :
    >>> install.get_available("feature_id")

    Personnalize what is enabled or not :
    >>> install.set_enable("feature_id")

    Launch the installation process :
    >>> install.set_enable("feature_id")

    """

    LIST_OS = {
        "linux": {
            "ubuntu": Deb,
            "mint": Deb,
            "debian": Deb,
            "fedora": Dnf,
            "suse": Rpm
        },
        "win32": Windows,
        "darwin": MacOs
    }

    def __init__(self, p=None):
        """Create a new sppasInstallerDeps instance.

        :param p: (ProcessProgressTerminal) The installation progress.

        """
        self.__pbar = p
        self.__os = None
        self.__set_os()
        self.__installer = self.get_os()(p)
        self.__feat_ids = self.__installer.get_feat_ids()

    # ------------------------------------------------------------------------

    def get_feat_ids(self):
        """Return the list of feature identifiers."""
        return self.__feat_ids

    # ------------------------------------------------------------------------

    def get_feat_desc(self, feat_id):
        """Return the description of the feature.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.description(feat_id)

    # ------------------------------------------------------------------------

    def get_available(self, feat_id):
        """Return True if the feature is available.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.available(feat_id)

    # ------------------------------------------------------------------------

    def get_os(self):
        """Return the OS of the computer."""
        return self.__os

    # ------------------------------------------------------------------------

    def __set_os(self):
        """Set the OS of the computer."""
        system = sys.platform
        logging.info("Operating system: {}".format(system))
        if system.startswith("linux") is True:
            linux_distrib = str(os.uname()).split(", ")[3].split("-")[1].split(" ")[0].lower()
            self.__os = self.LIST_OS["linux"][linux_distrib]
        else:
            if system not in list(self.LIST_OS.keys()):
                raise OSError("The OS {} is not supported yet.".format(system))
            else:
                self.__os = self.LIST_OS[system]

    # ------------------------------------------------------------------------

    def get_cfg_exist(self):
        """Return True if the config_file exist."""
        return self.__installer.cfg_file_exists()

    # ------------------------------------------------------------------------

    def get_enable(self, feat_id):
        """Return True if the feature is enabled.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.enable(feat_id)

    # ------------------------------------------------------------------------

    def set_enable(self, feat_id):
        """Make a feature enabled.

        :param feat_id: (str) Identifier of a feature

        """
        self.__installer.enable(feat_id, True)

    # ------------------------------------------------------------------------

    def unset_enable(self, feat_id):
        """Make a feature disabled.

        :param feat_id: (str) Identifier of a feature

        """
        self.__installer.enable(feat_id, False)

    # ------------------------------------------------------------------------

    def install(self):
        """Launch the installation process.

        :return errors: (str) errors happening during installation.

        """
        errors = self.__installer.install()
        return errors

