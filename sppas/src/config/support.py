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

    config.support.py
    ~~~~~~~~~~~~~~~~~

"""

import os
import logging
import sys

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

from sppas.src.config.sglobal import sppasPathSettings
from sppas.src.config.sglobal import sppasGlobalSettings
from sppas.src.config.installer import Deb, Dnf, Rpm, Windows, CygWin, MacOs

# ---------------------------------------------------------------------------


class sppasPostInstall:
    """Check directories, etc.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    @staticmethod
    def sppas_directories():
        """Create the required directories in the SPPAS package."""
        with sppasPathSettings() as paths:

            if os.path.exists(paths.logs) is False:
                os.mkdir(paths.logs)
                logging.info(
                    "The directory {:s} to store logs is created."
                    "".format(paths.logs))

            if os.path.exists(paths.wkps) is False:
                os.mkdir(paths.wkps)
                logging.info(
                    "The directory {:s} to store workspaces is created."
                    "".format(paths.wkps))

            if os.path.exists(paths.trash) is False:
                os.mkdir(paths.trash)
                logging.info(
                    "The Trash directory {:s} is created."
                    "".format(paths.trash))

    # -----------------------------------------------------------------------

    @staticmethod
    def sppas_dependencies():
        """Enable or disable features depending on dependencies."""
        pass


# ---------------------------------------------------------------------------


class sppasUpdate:
    """Check if an update of SPPAS is available.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is not implemented yet.

    """

    @staticmethod
    def check_update():
        with sppasGlobalSettings as sg:
            current = sg.__version__

            # Perhaps I should create a text file with the version number
            url = sg.__url__ + '/download.html'
            response = urlopen(url)
            data = str(response.read())

            # Extract last version from this page

            # Compare to current version

        return False


class sppasInstallerDeps:
    """Manage the installation of features.

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

    See what is enabled or not :
    >>> install.get_enables()

    Personnalize what is enabled or not :
    >>> install.set_enable("feature_id")

    Launch the installation process :
    >>> install.set_enable("feature_id")

    """
    __List_os = {
        "linux": {
            "ubuntu": Deb,
            "mint": Deb,
            "debian": Deb,
            "fedora": Dnf,
            "suse": Rpm
        },
        "win32": Windows,
        "cygwin": CygWin,
        "darwin": MacOs
    }

    def __init__(self, p):
        """Create a new sppasInstallerDeps instance.

        :param p: (ProcessProgressTerminal) The installation progress.

        """
        self.__pbar = p
        self.__Exploit_syst = None
        self.set_os()
        self.__installer = self.get_os()(p)
        self.__feat_ids = self.__installer.get_feat_ids()

    # ---------------------------------------------------------

    def get_feat_ids(self):
        """Return the list of feature identifiers."""
        return self.__feat_ids

    # ---------------------------------------------------------

    def get_feat_desc(self, feat_id):
        """Return the description of the feature.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.description(feat_id)

    # ---------------------------------------------------------

    def get_os(self):
        """Return the OS of the computer."""
        return self.__Exploit_syst

    # ---------------------------------------------------------------------------

    def set_os(self):
        """Set the OS of the computer."""
        system = sys.platform
        if system == "linux":
            linux_distrib = str(os.uname()).split(", ")[3].split("-")[1].split(" ")[0].lower()
            self.__Exploit_syst = self.__List_os["linux"][linux_distrib]
        else:
            if system not in list(self.__List_os.keys()):
                raise OSError("A implémenter")
            else:
                self.__Exploit_syst = self.__List_os[system]

    # ---------------------------------------------------------------------------

    def get_enables(self):
        """Return informations about each feature.

        :return enables: (str)

        """
        features = self.__feat_ids
        enables = "\n"
        for f in features:
            enables += "(" + str(self.__installer.description(f)) + "," + f + ") available = "\
                       + str(self.__installer.available(f)) + "/ enable = " + str(self.__installer.enable(f)) + "\n"
        return enables

    # ---------------------------------------------------------------------------

    def get_enable(self, feat_id):
        """Return True if the feature is enabled.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.enable(feat_id)

    # ---------------------------------------------------------------------------

    def set_enable(self, feat_id):
        """Make a feature enabled.

        :param feat_id: (str) Identifier of a feature

        """
        self.__installer.enable(feat_id, True)

    # ---------------------------------------------------------------------------

    def unset_enable(self, feat_id):
        """Make a feature disabled.

        :param feat_id: (str) Identifier of a feature

        """
        self.__installer.enable(feat_id, False)

    # ---------------------------------------------------------------------------

    def install(self):
        """Launch the installation process.

        :return errors: (str) errors which happend during installation.

        """
        errors = self.__installer.install()
        return errors

    # ---------------------------------------------------------------------------

