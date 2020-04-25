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
    """Check directories, etc.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

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
        self.__pbar = p
        self.__Exploit_syst = None
        self.set_os()
        self.__installer = self.get_os()(p)
        self.__features = list()
        self.set_features()

    # ---------------------------------------------------------------------------

    def get_os(self):
        """Return the value of the private attribute __Exploit_syst.

        """
        return self.__Exploit_syst

    # ---------------------------------------------------------------------------

    def get_install(self):
        """Return the value of the private attribute __Exploit_syst.

        """
        return self.__installer.get_cfg_exist()

    # ---------------------------------------------------------------------------

    def set_os(self):
        """Set the value of __Exploit_syst according to the exploitation system of the user.

        """
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

    def get_features(self):
        """Return the list of features __features.

        """
        return self.__features

    # ---------------------------------------------------------------------------

    def set_features(self):
        """Set features in __features with the one in __installer.

        """
        self.__features = self.__installer.get_features()

    # ---------------------------------------------------------------------------

    def get_features_name(self):
        """Return the features names in __features.

        """
        features = self.get_features()
        list_name = list()
        for f in features:
            list_name.append(f.get_id())
        return list_name

    # ---------------------------------------------------------------------------

    def get_enables(self):
        """Return the features enables in __features.

        """
        features = self.get_features()
        enables = "\n"
        for f in features:
            enables += "(" + f.get_desc() + "," + f.get_id() + ") available = "\
                       + str(f.get_available()) + "/ enable = " + str(f.get_enable()) + "\n"
        return enables

    # ---------------------------------------------------------------------------

    def get_enable(self, feature_name):
        """Return the private attribute __enable value of the feature used as an argument.

        :param feature_name: (string) The name of the feature.

        """
        return feature_name.get_enable()

    # ---------------------------------------------------------------------------

    def set_enable(self, feature_name):
        """Set the private attribute __enable value of the feature to True.

        :param feature_name: (string) The name of the feature.

        """
        feature_name.set_enable(True)

    # ---------------------------------------------------------------------------

    def unset_enable(self, feature_name):
        """Set the private attribute __enable value of the feature to False.

        :param feature_name: (string) The name of the feature.

        """
        feature_name.set_enable(False)

    # ---------------------------------------------------------------------------

    def get_states(self):
        """Return the state of the features.

        """
        features = self.get_features()
        dict_enable = dict()
        for f in features:
            dict_enable[f.get_desc()] = f.get_enable()
        return dict_enable

    # ---------------------------------------------------------------------------

    # def get_cmd_errors(self):
    #     """Return the error which appends during the command installation.
    #
    #     """
    #     return self.__installer.get_cmd_errors()
    #
    # # ---------------------------------------------------------------------------
    #
    # def get_system_errors(self):
    #     """Return the error which appends during the system dependencies installation.
    #
    #     """
    #     return self.__installer.get_system_errors()
    #
    # # ---------------------------------------------------------------------------
    #
    # def get_pypi_errors(self):
    #     """Return the error which appends during the pypi dependencies installation.
    #
    #     """
    #     return self.__installer.get_pypi_errors()
    #
    # # ---------------------------------------------------------------------------

    def install(self):
        """Launch the installation procedure of the __installer.

        """
        self.__installer.install()

    # ---------------------------------------------------------------------------
