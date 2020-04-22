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

        src.config.installer.py
    ~~~~~~~~~~~~~~~~

:author:       Florian Hocquet
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      a script to use workspaces from terminal

"""

import os

from sppas.src.config.features import Feature
from sppas import paths
from subprocess import Popen, PIPE

try:
    import configparser as cp
except ImportError:
    import ConfigParser as cp


# ---------------------------------------------------------------------------


class Installer:
    """Creation Installer.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This class allows you to create an object which will install all the
        dependencies needed for each features you have in your features.ini file.
        To achieve to do that this class have 3 privates attributes :

        - req : the id of the requirements list, that refer to your exploitation
        system, in your feature.ini file
        - features : a list of Feature object, there is one Feature object for
        each section you have in your feature.ini file
        - config_file : the parser which contains your parsed features.ini file

        The initialazation of these privates attributes is done in the constructor
        of the Installer object.

    """

    def __init__(self):
        """Create a new Installer instance.

        """
        self.__req = "req_win"
        self.__cfg_exist = False
        self.__config_file = None
        self.__config_parser = cp.ConfigParser()
        self.__pypi_errors = ""
        self.__system_errors = ""
        self.__features = list()
        self.init_config()
        self.__features_parser = self.init_features()
        self.set_features()

    # ---------------------------------------------------------------------------

    def init_config(self):
        """Check if the config already exist or not.

        """
        config_file = os.path.join(paths.etc, "config.cfg")
        self.__config_file = config_file
        if os.path.exists(self.get_config_file()) is False:
            self.set_cfg_exist(False)
        else:
            self.set_cfg_exist(True)

    # ---------------------------------------------------------------------------

    def get_cfg_exist(self):
        """Return the private attribute __cfg_exist.

        """
        return self.__cfg_exist

    # ---------------------------------------------------------------------------

    def set_cfg_exist(self, value):
        """Set the value of the private attribute __cfg_exist.

        :param value: (boolean) The boolean which represent if the file config_file
        already exist or not in your sppas directory.

        """
        value = bool(value)
        self.__cfg_exist = value

    # ---------------------------------------------------------------------------

    def get_config_file(self):
        """Return the private file __config_file.

        """
        return self.__config_file

    # ---------------------------------------------------------------------------

    def get_config_parser(self):
        """Return the private parser __config_parser.

        """
        return self.__config_parser

    # ---------------------------------------------------------------------------

    @staticmethod
    def init_features():
        """Return a parsed version of your features.ini file.

        """
        feature_file = os.path.join(paths.etc, "features.ini")

        if os.path.exists(feature_file) is False:
            raise IOError('Installation error: the file to configure the '
                          'list of features does not exist.')

        features_parser = cp.ConfigParser()
        try:
            features_parser.read(feature_file)
        except cp.MissingSectionHeaderError:
            print("Votre fichier ne contient pas de sections")
        return features_parser

    # ---------------------------------------------------------------------------

    def set_features(self):
        """Create and initialize each Feature object which compose your private list __feature.

        This method browse your feature.ini file and for each section in it, it
        create a Feature object in your private list __feature with the same content.

        """
        list_features = (self.__features_parser.sections())
        self.__features = list()
        for f in list_features:
            feature = Feature()

            feature.set_id(f)

            available = self.__features_parser.getboolean(f, "available")
            feature.set_available(available)

            enable = self.__features_parser.getboolean(f, "enable")
            feature.set_enable(enable)

            d = self.__features_parser.get(f, self.__req)
            if d == "nil" or d == "":
                feature.set_packages({"nil": "1"})
                feature.set_available(True)
            elif d == "none":
                feature.set_packages({"none": "0"})
                feature.set_available(False)
            else:
                feature.set_available(True)
                depend_packages = self.parse_depend(d)
                feature.set_packages(depend_packages)

            d = self.__features_parser.get(f, "req_pip")
            if d == "nil" or d == "":
                feature.set_pypi({"nil": "1"})
            else:
                depend_pypi = self.parse_depend(d)
                feature.set_pypi(depend_pypi)

            self.__features.append(feature)

    # ---------------------------------------------------------------------------

    def get_features(self):
        """Return the private attribute list __features.

        """
        return self.__features

    # ---------------------------------------------------------------------------

    @staticmethod
    def parse_depend(string_require):
        """Create a dictionary from the string given as an argument.

        :param string_require: (string) The value of one
        of your req_*** key in one of the section of your feature.ini file.

        """
        string_require = str(string_require)
        dependencies = string_require.split(" ")
        depend = dict()
        for line in dependencies:
            tab = line.split(":")
            depend[tab[0]] = tab[1]
        return depend

    # ---------------------------------------------------------------------------

    def get_features_parser(self):
        """Return the private parser __features_parser.

        """
        return self.__features_parser

    # ---------------------------------------------------------------------------

    def show_features(self):
        """Print for each Feature object, in your private list __feature, his privates attributes.

        """
        for f in self.__features:
            print(f.__str__())

    # ---------------------------------------------------------------------------

    def get_pypi_errors(self):
        """Return the private attribute __pypi_errors.

        """
        return self.__pypi_errors

    # ---------------------------------------------------------------------------

    def set_pypi_errors(self, string):
        """Fix the value of the private attribute __pypi_errors.

        :param string: (str) This string is filled with the errors you will encounter during
        the procedure of installation the method install_pypi() and install_feature().

        """
        string = str(string)
        if string == "":
            self.__pypi_errors = ""
        else:
            self.__pypi_errors += string

    # ---------------------------------------------------------------------------

    def get_system_errors(self):
        """Return the private attribute __system_errors.

        """
        return self.__system_errors

    # ---------------------------------------------------------------------------

    def set_system_errors(self, string):
        """Fix the value of the private attribute __system_errors.

        :param string: (str) This string is filled with the errors you will encounter during
        the procedure of installation the method install_packages() and install_feature().

        """
        string = str(string)
        if string == "":
            self.__system_errors = ""
        else:
            self.__system_errors += string

    # ---------------------------------------------------------------------------

    def install(self):
        """Manage the procedure of installation of your pip requirements for each Feature in your private list
        __feature.

        """
        if not self.get_cfg_exist():
            self.get_config_parser().add_section("features")

            for f in self.__features:
                if not f.get_available():
                    print(f.get_id() + " can't be installed by using only command line on your computer because of "
                                       "your OS \n")
                    continue
                if not f.get_enable():
                    continue

                self.install_packages(f)
                self.install_pypis(f)
                f.set_enable(True)

            for f in self.__features:
                self.get_config_parser().set("features", f.get_id(), str(f.get_enable()).lower())
            self.get_config_parser().write(open(self.get_config_file(), 'w'))

    # ---------------------------------------------------------------------------

    def install_pypis(self, feature):
        """Manage the procedure of installation of your pip requirements for each Feature in your private list
        __feature.

        :param feature: (str) The feature you will use to browse the private dictionary __pypi, to install the
        pip packages.

        """
        if not isinstance(feature, Feature):
            raise NotImplementedError

        self.set_pypi_errors("")
        for package, version in feature.get_pypi().items():
            if package == "nil":
                print("You don't need to install pip dependencies to install \"" + feature.get_id() + "\" on your "
                                                                                                      "computer")
            else:
                if not self.search_pypi(package):
                    self.install_pypi(package)
                elif not self.version_pypi(package, version):
                    self.update_pypi(package)
                else:
                    print("The package pip \"" + package + "\" is already installed and up to date on your computer ")
        if not "" == self.get_pypi_errors():
            feature.set_enable(False)
            raise NotImplementedError(self.get_pypi_errors())
        else:
            print("The pip dependencies installation procedure is a success.")

    # ---------------------------------------------------------------------------

    @staticmethod
    def search_pypi(package):
        """Returns True if the pip package given as an argument is installed or not on your computer.

        :param package: (string) The pip package you are searching if it is installed
        or not on your computer.

        """
        package = str(package)
        cmd = Popen(["pip", "show", package], shell=True, stdout=PIPE, stderr=PIPE, text=True)
        cmd.wait()
        error = cmd.stderr.read()
        if "not found" in error:
            return False
        else:
            return True

    # ---------------------------------------------------------------------------

    def install_pypi(self, package):
        """Install the pip package given as an argument on your computer.

        :param package: (string) The pip package you will try to install on your computer.

        """
        package = str(package)
        cmd = Popen(["pip", "install", package, "--no-warn-script-location"], shell=True, stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        error = cmd.stderr.read()
        if not "" == error:
            if "Could not find" in error:
                self.set_pypi_errors("The package \"" + package + "\" isn't a package of pip : " + "\n" + error + "\n")
            else:
                self.set_pypi_errors("An error has occurred during the installation of the package : " + package +
                                     "\n" + error + "\n")
        else:
            print("Successfully installed", package, "\n")

    # ---------------------------------------------------------------------------

    def version_pypi(self, package, req_version):
        """Returns True if the pip package given as an argument has the good version or not on your computer.

        :param package: (string) The pip package you are searching if his version is enough
        recent or not.
        :param req_version: (string) The minimum version you need to have for this pip
        package.

        """
        package = str(package)
        req_version = str(req_version)
        cmd = Popen(["pip", "show", package], shell=True, stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        stdout = cmd.stdout.read()
        if self.need_update_pypi(stdout, req_version):
            return False
        else:
            return True

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_pypi(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout you got with the command "pip show"
        you used on a package in the method "version_pypi"
        :param req_version: (string) The minimum version you need to have for the pip
        package you used has an argument in the "version_pypi" method.

        """
        stdout_show = str(stdout_show)
        req_version = str(req_version)
        version = stdout_show.split("\n")[1].split(":")[1].replace(" ", "")
        v = ""
        i = 0
        for letter in version:
            if not letter.isalpha():
                if letter == ".":
                    i += 1
                if i == 2:
                    break
                v += letter
            else:
                break

        req_version = req_version.split("=", maxsplit=1)

        comparator = req_version[0]
        comparator += "="

        v = float(v)
        version = float(req_version[1])

        if comparator == ">=":
            if v < version:
                return True
            else:
                return False
        else:
            raise ValueError("Your comparator : " + comparator + " does not refer to a valid comparator")

    # ---------------------------------------------------------------------------

    def update_pypi(self, package):
        """Update the pip package given as an argument on your computer.

        :param package: (string) The pip package will try to update on your computer.

        """
        package = str(package)
        cmd = Popen(["pip", "install", "-U", package], shell=True, stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        error = cmd.stderr.read()
        if not "" == error:
            self.__pypi_errors += "An error has occurred during the updating of the package \"" + package + \
                                  "\"\n" + error + "\n"
        else:
            print("Successfully updated", package, "\n")

    # ---------------------------------------------------------------------------

    def install_packages(self, feature):
        """Manage the procedure of installation of your __req requirements for each Feature in your private list
        __feature.

        :param feature: (str) The feature you will use to browse the private dictionary __packages, to install the
        system packages.

        """
        if not isinstance(feature, Feature):
            raise NotImplementedError

        self.set_system_errors("")
        for package, version in feature.get_packages().items():
            if package == "none":
                feature.set_available(False)
                print(feature.get_id() + " can't be installed by using only command line on your computer because of "
                                         "your OS \n")
            elif package == "nil":
                print("For " + feature.get_id() + " you don't need to install system dependencies on your computer "
                                                  "because of your OS")
            else:
                if not self.search_package(package):
                    self.install_package(package)
                elif not self.version_package(package, version):
                    self.update_package(package)
                else:
                    print("The package system : " + package + " is already installed and up to date on your "
                                                              "computer")
        if not "" == self.get_system_errors():
            feature.set_enable(False)
            raise NotImplementedError(self.get_system_errors())
        else:
            print("The system dependencies installation procedure is a success.")

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        package = str(package)
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install the system package given as an argument on your computer.

        :param package: (string) The system package will try to install on your computer.

        """
        package = str(package)
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package you are searching if his version is enough
        recent or not.

        :param req_version: (string) The minimum version you need to have for this system
        package.

        """
        package = str(package)
        req_version = str(req_version)
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout you got with the command associate to
        your OS command which allows you to know if a package is installed or not.

        :param req_version: (string) The minimum version you need to have for the
        package you used has an argument in the "version_package" method.

        """
        stdout_show = str(stdout_show)
        req_version = str(req_version)
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package will try to update on your computer.

        """
        package = str(package)
        raise NotImplementedError

    # ---------------------------------------------------------------------------


class Deb(Installer):
    """Creation Deb(Installer).

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This class allows you to create an object Deb which inherit from the
        super class Installer.
        This Deb(Installer) is made for the Debians distributions of Linux.
        For example :

        - Linux
        - Debian
        - Mint

    """

    def __init__(self):
        """Create a new Deb(Installer) instance.

        """
        super(Deb, self).__init__()
        self.req = "req_deb"

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        raise NotImplementedError

        # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install the system package given as an argument on your computer.

        :param package: (string) The system package will try to install on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package you are searching if his version is enough
        recent or not.

        :param req_version: (string) The minimum version you need to have for this system
        package.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout you got with the command associate to
        your OS command which allows you to know if a package is installed or not.

        :param req_version: (string) The minimum version you need to have for the
        package you used has an argument in the "version_package" method.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package will try to update on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------


class Rpm(Installer):
    """Creation Rpm(Installer).

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This class allows you to create an object Rpm which inherit from the
        super class Installer.
        This Rpm(Installer) is made for the Rpm distributions of Linux.
        For example :

        - Suse

    """

    def __init__(self):
        """Create a new Rpm(Installer) instance.

        """
        super(Rpm, self).__init__()
        self.req = "req_rpm"

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install the system package given as an argument on your computer.

        :param package: (string) The system package will try to install on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package you are searching if his version is enough
        recent or not.

        :param req_version: (string) The minimum version you need to have for this system
        package.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout you got with the command associate to
        your OS command which allows you to know if a package is installed or not.

        :param req_version: (string) The minimum version you need to have for the
        package you used has an argument in the "version_package" method.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package will try to update on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------


class Dnf(Installer):
    """Creation Dnf(Installer).

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This class allows you to create an object Dnf which inherit from the
        super class Installer.
        This Dnf(Installer) is made for Fedora one of the distributions of Linux.

    """

    def __init__(self):
        """Create a new Dnf(Installer) instance.

        """
        super(Dnf, self).__init__()
        self.req = "req_rpm"

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        raise NotImplementedError

        # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install the system package given as an argument on your computer.

        :param package: (string) The system package will try to install on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package you are searching if his version is enough
        recent or not.

        :param req_version: (string) The minimum version you need to have for this system
        package.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout you got with the command associate to
        your OS command which allows you to know if a package is installed or not.

        :param req_version: (string) The minimum version you need to have for the
        package you used has an argument in the "version_package" method.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package will try to update on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------


class Windows(Installer):
    """Creation Windows(Installer).

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This class allows you to create an object Windows which inherit from the
        super class Installer.
        This Windows(Installer) is made for Windows 10.

    """

    def __init__(self):
        """Create a new Windows(Installer) instance.

        """
        super(Windows, self).__init__()
        self.req = "req_win"

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        return True

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install the system package given as an argument on your computer.

        :param package: (string) The system package will try to install on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package you are searching if his version is enough
        recent or not.

        :param req_version: (string) This string is the minimum version you need to have for this system
        package.

        """
        return True

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout you got with the command associate to
        your OS command which allows you to know if a package is installed or not.

        :param req_version: (string) The minimum version you need to have for the
        package you used has an argument in the "version_package" method.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package will try to update on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------


class CygWin(Installer):
    """Creation CygWin(Installer).

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This class allows you to create an object CygWin which inherit from the
        super class Installer.
        This CygWin(Installer) is made for CygWin.

    """

    def __init__(self):
        """Create a new CygWin(Installer) instance.

        """
        super(CygWin, self).__init__()
        self.req = "req_cyg"

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        raise NotImplementedError

        # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install the system package given as an argument on your computer.

        :param package: (string) The system package will try to install on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package you are searching if his version is enough
        recent or not.

        :param req_version: (string) The minimum version you need to have for this system
        package.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout you got with the command associate to
        your OS command which allows you to know if a package is installed or not.

        :param req_version: (string) The minimum version you need to have for the
        package you used has an argument in the "version_package" method.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package will try to update on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------


class MacOs(Installer):
    """Creation MacOs(Installer).

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This class allows you to create an object MacOs which inherit from the
        super class Installer.
        This MacOs(Installer) is made for IOS computers.

    """

    def __init__(self):
        """Create a new MacOs(Installer) instance.

        """
        super(MacOs, self).__init__()
        self.req = "req_ios"

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        raise NotImplementedError

        # ---------------------------------------------------------------------------

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install the system package given as an argument on your computer.

        :param package: (string) The system package will try to install on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package you are searching if his version is enough
        recent or not.

        :param req_version: (string) The minimum version you need to have for this system
        package.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout you got with the command associate to
        your OS command which allows you to know if a package is installed or not.

        :param req_version: (string) The minimum version you need to have for the
        package you used has an argument in the "version_package" method.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package will try to update on your computer.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------


i = Windows()
i.install()
