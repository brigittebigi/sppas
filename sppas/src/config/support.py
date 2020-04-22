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
# import sys

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

from sppas.src.config.sglobal import sppasPathSettings
from sppas.src.config.sglobal import sppasGlobalSettings
# from sppas.src.config.installer import Installer, Deb, Rpm, Windows, CygWin, MacOs

try:
    # For Python 3.0 and later
    import configparser as cp
except ImportError:
    # Fall back to Python 2
    import ConfigParser as cp


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


# ---------------------------------------------------------------------------


# class sppasInstallerDeps:
#     """Check directories, etc.
#
#     :author:       Florian Hocquet
#     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
#     :contact:      develop@sppas.org
#     :license:      GPL, v3
#     :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
#
#     """
#     __List_os = {
#         "linux": {
#             "ubuntu": Deb,
#             "mint": Deb,
#             "debian": Deb,
#             "fedora": Rpm,
#             "suse": Rpm
#         },
#         "win32": Windows,
#         "cygwin": CygWin,
#         "darwin": MacOs
#     }
#
#     def __init__(self):
#         self.__Exploit_syst = None
#         self.set_os()
#         self.__Instance_Install = None
#
#     # ---------------------------------------------------------------------------
#
#     def get_os(self):
#         return self.__Exploit_syst
#
#     # ---------------------------------------------------------------------------
#
#     def set_os(self):
#         system = sys.platform
#         if system == "linux":
#             linux_distrib = str(os.uname()).split(", ")[3].split("-")[1].split(" ")[0].lower()
#             self.__Exploit_syst = self.__List_os["linux"][linux_distrib]
#         else:
#             if system not in list(self.__List_os.keys()):
#                 raise OSError("A implémenter")
#             else:
#                 self.__List_os[sys]
#
#     # ---------------------------------------------------------------------------
#
#     def get_sections(self):
#         list_options = (self.__config_file.sections())
#         return list_options
#
#     # ---------------------------------------------------------------------------
#
#     def get_desc(self, section):
#         try:
#             return self.__config_file.get(section, 'desc')
#         except cp.NoSectionError:
#             return "Vous devez saisir une des sections disponibles"
#
#     # ---------------------------------------------------------------------------
#
#     def get_enable(self, section):
#         try:
#             enable = self.__config_file.getboolean(section, "enable")
#             return enable
#         except cp.NoSectionError:
#             return "Vous devez saisir une des sections disponibles"
#
#     # ---------------------------------------------------------------------------
#
#     def set_enable(self, section, boolean):
#         if type(boolean) is bool and boolean:
#             self.__config_file.set(section, "enable", "true")
#         elif type(boolean) is bool and boolean is False:
#             self.__config_file.set(section, "enable", "false")
#         with open('test.ini', 'w') as configfile:
#             self.__config_file.write(configfile)
#
#     # ---------------------------------------------------------------------------
#
#     def get_dependencies(self, section):
#         requirements = self.__List_require.get(self.get_os())
#
#         dependencies = self.__config_file.get(section, requirements).split(" ")
#         depend_version = dict()
#         for line in dependencies:
#             tab = line.split("=", maxsplit=1)
#             depend_version[tab[0]] = tab[1]
#
#         dependencies2 = self.__config_file.get(section, "req_pip").split(" ")
#         depend_version2 = dict()
#         for line2 in dependencies2:
#             tab2 = line2.split("=", maxsplit=1)
#             depend_version2[tab2[0]] = tab2[1]
#         return depend_version, depend_version2
#
#     # ---------------------------------------------------------------------------
#
#     def install_all(self):
#         raise NotImplementedError('Not implemented yet')
#     # ---------------------------------------------------------------------------

