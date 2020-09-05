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

from .installer import DebianInstaller
from .installer import DnfInstaller
from .installer import RpmInstaller
from .installer import WindowsInstaller
from .installer import MacOsInstaller

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
    - to get information, which are important for the users,
    about the pre-installation.
    - to configure parameters to get a personalized installation.

    For example:

    >>> installer = sppasInstallerDeps()

    See if a feature is available or not:
    >>> installer.available("feature_id")
    >>> True

    Customize what is enabled or not:
    >>> installer.enable("feature_id")
    >>> False
    >>> installer.enable("feature_id", True)
    >>> True

    Launch the installation process:
    >>> errors = installer.install("feature_id")
    >>> assert len(errors) == 0
    >>> assert installer.available("feature_id") is True

    """

    LIST_OS = {
        "linux": {
            "ubuntu": DebianInstaller,
            "mint": DebianInstaller,
            "debian": DebianInstaller,
            "fedora": DnfInstaller,
            "suse": RpmInstaller
        },
        "win32": WindowsInstaller,
        "darwin": MacOsInstaller
    }

    def __init__(self, progress=None):
        """Create a new sppasInstallerDeps instance.

        Instantiate the appropriate installer depending on the OS.

        :param progress: (ProcessProgressTerminal) The installation progress.

        """
        self.__os = None
        self.__set_os()
        self.__installer = self.os()()
        logging.debug("InstallerDeps .......")
        logging.info("System installer: {}"
                     "".format(self.__installer.__class__.__name__))
        logging.debug("InstallerDeps ok ****** 1")
        if progress is not None:
            logging.debug("set progress")
            self.__installer.set_progress(progress)
            logging.debug("set progress done")
        logging.debug("InstallerDeps ok OK ok")

    # ------------------------------------------------------------------------

    def set_progress(self, progress=None):
        self.__installer.set_progress(progress)

    # ------------------------------------------------------------------------

    def features_ids(self, feat_type=None):
        """Return the list of feature identifiers.

        :param feat_type: (str) Only return features of the given type.
        :returns: (list)

        """
        return self.__installer.get_fids(feat_type)

    # ------------------------------------------------------------------------

    def feature_type(self, feat_id):
        """Return the feature type: deps, lang, annot.

        :param feat_id: (str) Identifier of a feature
        :return: (str) or None

        """
        return self.__installer.feature_type(feat_id)

    # ------------------------------------------------------------------------

    def brief(self, feat_id):
        """Return the brief description of the feature.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.brief(feat_id)

    # ------------------------------------------------------------------------

    def description(self, feat_id):
        """Return the description of the feature.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.description(feat_id)

    # ------------------------------------------------------------------------

    def available(self, feat_id):
        """Return True if the feature is available.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.available(feat_id)

    # ------------------------------------------------------------------------

    def os(self):
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

    def enable(self, fid, value=None):
        """Return True if the feature is enabled and/or set it.

        :param fid: (str) Identifier of a feature
        :param value: (bool or None) Enable of disable the feature.

        """
        if value is None:
            return self.__installer.enable(fid)

        return self.__installer.enable(fid, value)

    # ------------------------------------------------------------------------

    def install(self):
        """Launch the installation process.

        :return errors: (str) errors happening during installation.

        """
        errors = self.__installer.install()
        return errors

