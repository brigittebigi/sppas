# !/usr/bin/env python
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
:summary:      the class Installer of SPPAS

"""

import os
import sys
from subprocess import Popen, PIPE, call, STDOUT
import logging

try:
    import configparser as cp
except ImportError:
    import ConfigParser as cp

from sppas.src.config.features import Feature
from sppas.src.config.support import sppasPathSettings


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

    def __init__(self, p):
        """Create a new Installer instance.

        """
        logging.basicConfig(level=logging.DEBUG)
        self.__pbar = p
        self.__progression = 0
        self.__req = "req_win"
        self.__cmdos = "cmd_win"
        self.__cfg_exist = False
        self.__config_file = None
        self.__config_parser = cp.ConfigParser()
        self.__feature_file = self.set_features_file()
        self.__features_parser = cp.ConfigParser()
        self.__cmd_errors = ""
        self.__system_errors = ""
        self.__pypi_errors = ""
        self.__features = list()
        self.init_config()
        self.__features_parser = self.init_features()
        self.set_features()

    # ---------------------------------------------------------------------------

    def get_set_progress(self, value):
        """Return and Set the private attribute __progression.

        :param value: (int) The value you want to add.

        """
        self.__progression += value
        if self.__progression >= 0.99:
            self.__progression = 1
        return self.__progression

    # ---------------------------------------------------------------------------

    def get_req(self):
        """Return the private attribute __req.

        """
        return self.__req

    # ---------------------------------------------------------------------------

    def set_req(self, value):
        """Set the value of the private attribute __req.

        :param value: (string) The requirements list for your OS.

        """
        value = str(value)
        self.__req = value

    # ---------------------------------------------------------------------------

    def get_cmdos(self):
        """Return the private attribute __cmd.

        """
        return self.__cmdos

    # ---------------------------------------------------------------------------

    def set_cmdos(self, value):
        """Set the value of the private attribute __cmd.

        :param value: (string) The cmd command for your OS.

        """
        value = str(value)
        self.__cmdos = value

    # ---------------------------------------------------------------------------

    def init_config(self):
        """Check if the config already exist or not.

        """
        paths = sppasPathSettings()
        config_file = os.path.join(paths.basedir, "config.ini")
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

    def set_features_file(self):
        """Return a the your features.ini file.

        """
        paths = sppasPathSettings()
        feature_file = os.path.join(paths.etc, "features.ini")
        self.__feature_file = feature_file

        if os.path.exists(feature_file) is False:
            raise IOError('Installation error: the file to configure the '
                          'list of features does not exist.')
        return feature_file

    # ---------------------------------------------------------------------------

    def init_features(self):
        """Return a parsed version of your features.ini file.

        """
        features_parser = cp.ConfigParser()
        try:
            features_parser.read(self.get_feature_file())
        except cp.MissingSectionHeaderError:
            raise IOError("Votre fichier ne contient pas de sections")
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

            desc = self.__features_parser.get(f, "desc")
            feature.set_desc(desc)

            feature.set_enable(self.__features_parser.getboolean(f, "enable"))

            d = self.__features_parser.get(f, self.__req)
            if d == "nil" or d == "":
                feature.set_packages({"nil": "1"})
                feature.set_available(True)
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

            cmd = self.__features_parser.get(f, self.__cmdos)
            if cmd == "none":
                feature.set_available(False)
            feature.set_cmd(cmd)

            self.__features.append(feature)

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

    def get_features(self):
        """Return the private attribute list __features.

        """
        return self.__features

    # ---------------------------------------------------------------------------

    def calcul_pourc(self):
        """Return pourcentage of progression.

        :param feature: (Feature) The feature you use.

        """
        pourc = round((1 / len(self.get_features()) / 3), 3)
        return pourc

    # ---------------------------------------------------------------------------

    def get_feature_file(self):
        """Return the private file __feature_file.

        """
        return self.__feature_file

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

    def get_cmd_errors(self):
        """Return the private attribute __cmd_errors.

        """
        return self.__cmd_errors

    # ---------------------------------------------------------------------------

    def set_cmd_errors(self, string):
        """Fix the value of the private attribute __cmd_errors.

        :param string: (str) This string is filled with the errors you will encounter during
        the installation procedure of the method install_cmd.

        """
        string = str(string)
        self.__cmd_errors = string

    # ---------------------------------------------------------------------------

    def get_pypi_errors(self):
        """Return the private attribute __pypi_errors.

        """
        return self.__pypi_errors

    # ---------------------------------------------------------------------------

    def set_pypi_errors(self, string):
        """Fix the value of the private attribute __pypi_errors.

        :param string: (str) This string is filled with the errors you will encounter during
        the procedure of installation the method install_pypi().

        """
        string = str(string)
        if len(string) == 0:
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
        the procedure of installation the method install_packages().

        """
        string = str(string)
        if len(string) == 0:
            self.__system_errors = ""
        else:
            self.__system_errors += string

    # ---------------------------------------------------------------------------

    def install(self):
        """Manage the procedure of installation of your features.

        """
        if self.get_cfg_exist() is False:
            self.get_config_parser().add_section("features")

            if self.__pbar is not None:
                self.__pbar.set_header("Begining of the installation")

            for f in self.__features:
                self.__pbar.set_header("Begining of the installation for the feature \"" + f.get_desc() + "\"")
                if f.get_available() is False:
                    self.__pbar.update(
                        self.get_set_progress(round(1 / len(self.get_features()), 2)),
                        "{name} can't be installed by using only command line on your computer because "
                        "of your OS. \n".format(name=f.get_id()))
                    continue
                if f.get_enable() is False:
                    self.__pbar.update(
                        self.get_set_progress(round(1 / len(self.get_features()), 2)),
                        "You choose to don't install the feature \"{name}\" \n".format(name=f.get_id()))
                    continue

                try:
                    self.install_cmd(f)
                    self.install_packages(f)
                    self.install_pypis(f)
                    f.set_enable(True)
                except NotImplementedError:
                    if len(self.get_cmd_errors()) != 0:
                        logging.error(self.get_cmd_errors())
                    if len(self.get_system_errors()) != 0:
                        logging.error(self.get_system_errors())
                    if len(self.get_pypi_errors()) != 0:
                        logging.error(self.get_pypi_errors())

            self.__pbar.set_header("The installation process is finished")

            for f in self.__features:
                self.get_config_parser().set("features", f.get_id(), str(f.get_enable()).lower())
            self.get_config_parser().write(open(self.get_config_file(), 'w'))
        else:
            self.configurate_enable(self.get_config_parser())

    # ---------------------------------------------------------------------------

    def install_cmd(self, feature):
        """Use the command which is in your feature.

        :param feature: (string) The pip package you will try to install on your computer.

        """
        if not isinstance(feature, Feature):
            raise NotImplementedError

        feature_command = feature.get_cmd()

        if feature_command == "none":
            feature.set_available(False)
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc()),
                "{name} does not exist on your OS computer. \n".format(name=feature.get_id()))
        elif feature_command == "nil":
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc()),
                "You don't have any command to use because of your OS")
        else:
            if self.search_cmds(feature.get_id()) is False:
                self.install_cmds(feature_command, feature)
            else:
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc()),
                    "The command \"{name}\" is already installed on your computer ".format(name=feature.get_id()))

        if len(self.get_cmd_errors()) != 0:
            feature.set_enable(False)
            raise NotImplementedError()

    # ---------------------------------------------------------------------------

    def search_cmds(self, command):
        """Return True if the command is installed on your PC.

        :param command: (string) The command you will try to install on your computer.

        """
        command = str(command)
        command = command.strip()
        NULL = open(os.path.devnull, "w")
        try:
            call(command, stdout=NULL, stderr=STDOUT)
        except OSError:
            NULL.close()
            return False

        NULL.close()
        return True

        # command = str(command)
        # try:
        #     cmd = Popen(command, stdout=PIPE, stderr=PIPE, text=True)
        #     cmd.wait()
        #     return True
        # except FileNotFoundError:
        #     return False

    # ---------------------------------------------------------------------------

    def install_cmds(self, command, feature):
        """Install the pip package given as an argument on your computer.

        :param command: (string) The command you will try to install on your computer.
        :param id: (string) name of the command.

        """
        if not isinstance(feature, Feature):
            raise NotImplementedError

        self.set_cmd_errors("")
        command = str(command)
        command = command.strip()

        try:
            command = str(command)
            cmd = Popen(command.split(" "), stdout=PIPE, stderr=PIPE, text=True)
            cmd.wait()
            error = cmd.stderr.read()
            error = str(error)
            if len(error) != 0:
                self.set_cmd_errors("An error has occurred during the installation of : {name} "
                                    "\n {error} \n".format(name=id, error=error))
            else:
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc()),
                    "The installation of \"{name}\" is a success.".format(name=feature.get_id()))
        except FileNotFoundError:
            self.set_cmd_errors("An error has occurred during the installation of : {name} "
                                "\n {error} \n".format(name=id, error=feature.get_id() + " is not a command"))

    # ---------------------------------------------------------------------------

    def install_pypis(self, feature):
        """Manage the procedure of installation of your pip requirements.

        :param feature: (str) The feature you will use to browse the private dictionary __pypi, to install the
        pip packages.

        """
        if not isinstance(feature, Feature):
            raise NotImplementedError

        self.set_pypi_errors("")
        for package, version in feature.get_pypi().items():
            if package == "nil":
                logging.info("You don't need to install pip dependencies to install \"{name}\" on your computer"
                             .format(name=feature.get_id()))
            else:
                if self.search_pypi(package) is False:
                    self.install_pypi(package)
                elif self.version_pypi(package, version) is False:
                    self.update_pypi(package)
                else:
                    logging.info("The package pip \"{name}\" is already installed and up to date on your "
                                 "computer ".format(name=package))

        if len(self.get_pypi_errors()) != 0:
            feature.set_enable(False)
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc()),
                "The pip installation procedure have failed. Here is the errors :")
            raise NotImplementedError()
        else:
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc()),
                "The pip dependencies installation procedure is a success. \n")

    # ---------------------------------------------------------------------------

    @staticmethod
    def search_pypi(package):
        """Returns True if the pip package given as an argument is installed or not on your computer.

        :param package: (string) The pip package you are searching if it is installed
        or not on your computer.

        """
        package = str(package)
        cmd = Popen(["pip3", "show", package], stdout=PIPE, stderr=PIPE, text=True)
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
        cmd = Popen(["pip3", "install", package, "--no-warn-script-location"], stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        error = cmd.stderr.read()
        error = str(error)
        if len(error) != 0:
            if "Could not find" in error:
                self.set_pypi_errors("\n The package \"{name}\" isn't a package of pip : "
                                     "\n {error} \n".format(name=package, error=error))
            else:
                self.set_pypi_errors("An error has occurred during the installation of the package : {name} "
                                     "\n {error} \n".format(name=package, error=error))
        else:
            logging.info("The installation of \"{name}\" is a success.".format(name=package))

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
        cmd = Popen(["pip3", "show", package], stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        stdout = cmd.stdout.read()
        error = cmd.stderr.read()
        if "not found" in error:
            logging.info("\"{name}\" is not installed yet.".format(name=package))
            return True
        else:
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
            if letter.isalpha() is False:
                if letter == ".":
                    i += 1
                if i == 2 or letter == " ":
                    break
                v += letter
            else:
                break

        req_version = req_version.split(";", maxsplit=1)

        comparator = req_version[0]
        comparator += "="

        v = v.strip()
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
        cmd = Popen(["pip3", "install", "-U", package], stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        error = cmd.stderr.read()
        error = str(error)
        if len(error) != 0:
            if "Could not find" in error:
                self.set_pypi_errors("\n The package \"{name}\" isn't a package of pip : "
                                     "\n {error} \n".format(name=package, error=error))
            else:
                self.set_pypi_errors("An error has occurred during the updating of the package : {name} "
                                     "\n {error} \n".format(name=package, error=error))
        else:
            logging.info("The update of {name} is a success.".format(name=package))

    # ---------------------------------------------------------------------------

    def install_packages(self, feature):
        """Manage the procedure of installation of your __req requirements.

        :param feature: (str) The feature you will use to browse the private dictionary __packages, to install the
        system packages.

        """
        if not isinstance(feature, Feature):
            raise NotImplementedError

        self.set_system_errors("")
        for package, version in feature.get_packages().items():
            if package == "nil":
                logging.info("For {name} you don't need to install system dependencies on your "
                             "computer because of your OS".format(name=feature.get_id()))
            else:
                if self.search_package(package) is False:
                    self.install_package(package)
                elif self.version_package(package, version) is False:
                    self.update_package(package)
                else:
                    logging.info("The package system \"{name}\" is already installed and up to date on your "
                                 "computer".format(name=package))
        if len(self.get_system_errors()) != 0:
            feature.set_enable(False)
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc()),
                "The pip dependencies installation procedure is a success. \n")
            raise NotImplementedError()
        else:
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc()),
                "The system dependencies installation procedure is a success.")

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

    def configurate_enable(self, config_parser):

        if isinstance(config_parser, cp.ConfigParser) is False:
            raise NotImplementedError

        config_parser.read(self.get_config_file())
        options = config_parser.options("features")

        for option in options:
            for f in self.get_features():
                if f.get_id() == option and f.get_available() is True:
                    f.set_enable(config_parser.getboolean("features", option))
                elif f.get_id() == option and f.get_available() is False:
                    config_parser.set("features", f.get_id(), str(False).lower())

        config_parser.write(open(self.get_config_file(), 'w'))

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

    def __init__(self, p):
        """Create a new Deb(Installer) instance.

        """
        super(Deb, self).__init__(p)
        self.set_req("req_deb")
        self.set_cmdos("cmd_deb")
        self.set_features()

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

        :param req_version: (string) The minimum version you need to have for this system
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

    def __init__(self, p):
        """Create a new Rpm(Installer) instance.

        """
        super(Rpm, self).__init__(p)
        self.set_req("req_rpm")
        self.set_cmdos("cmd_rpm")
        self.set_features()

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

        :param req_version: (string) The minimum version you need to have for this system
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

    def __init__(self, p):
        """Create a new Dnf(Installer) instance.

        """
        super(Dnf, self).__init__(p)
        self.set_req("req_rpm")
        self.set_cmdos("cmd_rpm")
        self.set_features()

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

        :param req_version: (string) The minimum version you need to have for this system
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

    def __init__(self, p):
        """Create a new Windows(Installer) instance.

        """
        super(Windows, self).__init__(p)
        self.set_req("req_win")
        self.set_cmdos("cmd_win")
        self.set_features()

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

    def __init__(self, p):
        """Create a new CygWin(Installer) instance.

        """
        super(CygWin, self).__init__(p)
        self.set_req("req_cyg")
        self.set_cmdos("cmd_cyg")
        self.set_features()

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

        :param req_version: (string) The minimum version you need to have for this system
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

    def __init__(self, p):
        """Create a new MacOs(Installer) instance.

        """
        super(MacOs, self).__init__(p)
        self.set_req("req_ios")
        self.set_cmdos("cmd_ios")
        self.set_features()

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        package = str(package)
        cmd = Popen(["brew", "list", package], stdout=PIPE, stderr=PIPE, text=True)
        cmd.wait()
        error = cmd.stderr.read()
        if len(error) != 0:
            return False
        else:
            return True

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install the system package given as an argument on your computer.

        :param package: (string) The system package will try to install on your computer.

        """
        package = str(package)
        cmd = Popen(["brew", "install", package], stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        error = cmd.stderr.read()
        error = str(error)
        if len(error) != 0:
            if "Warning: You are using macOS" in error:
                if self.search_package(package) is False:
                    self.set_system_errors("An error has occurred during the installation of the package : {name} "
                                           "\n {error} \n".format(name=package, error=error))
                else:
                    logging.info("The installation of \"{name}\" is a success.".format(name=package))
            elif "No available" in error:
                self.set_system_errors("\n The package \"{name}\" isn't a package of brew : "
                                       "\n {error} \n".format(name=package, error=error))
            else:
                self.set_system_errors("An error has occurred during the installation of the package : {name} "
                                       "\n {error} \n".format(name=package, error=error))
        else:
            logging.info("The installation of \"{name}\" is a success.".format(name=package))

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The brew package you are searching if his version is enough
        recent or not.

        :param req_version: (string) The minimum version you need to have for this brew
        package.

        """
        package = str(package)
        req_version = str(req_version)
        cmd = Popen(["brew", "info", package], stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        stdout = cmd.stdout.read()
        error = cmd.stderr.read()
        if len(error) != 0:
            self.set_system_errors("\"{name}\" is not installed yet.".format(name=package))
            return True
        else:
            if self.need_update_package(stdout, req_version):
                return False
            else:
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
        stdout_show = str(stdout_show)
        req_version = str(req_version)
        version = stdout_show.split("\n")[0].split("stable")[1].strip()
        v = ""
        i = 0
        for letter in version:
            if letter.isalpha() is False:
                if letter == ".":
                    i += 1
                if i == 2 or letter == " ":
                    break
                v += letter
            else:
                break

        req_version = req_version.split(";", maxsplit=1)

        comparator = req_version[0]
        comparator += "="

        v = v.strip()
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

    def update_package(self, package):
        """Update the system package given as an argument on your computer.

        :param package: (string) The system package will try to update on your computer.

        """
        package = str(package)
        cmd = Popen(["brew", "upgrade", package], stdout=PIPE, stderr=PIPE,
                    text=True)
        cmd.wait()
        error = cmd.stderr.read()
        error = str(error)
        if len(error) != 0:
            if "Could not find" in error:
                self.set_pypi_errors("\n The package \"{name}\" isn't a package of brew : "
                                     "\n {error} \n".format(name=package, error=error))
            else:
                self.set_pypi_errors("An error has occurred during the updating of the package : {name} "
                                     "\n {error} \n".format(name=package, error=error))
        else:
            logging.info("The update of {name} is a success.".format(name=package))

    # ---------------------------------------------------------------------------

