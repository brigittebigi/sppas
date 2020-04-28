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

from sppas.src.config.features import Features, Feature, sppasPathSettings
from sppas.src.config.process import Process

# ---------------------Sentences for the method install-----------------------
message_install = {
    "begining": "Begining of the installation",
    "begining_feature": "Begining of the installation for the feature \" {desc} \"",
    "available_false": "{name} can't be installed by using only command line on your computer because of your OS.",
    "enable_false": "You choose to don't install the feature \"{name}\"",
    "installation_success": "The installation of \" {desc} \" is a success",
    "installation_failed": "The installation of \" {desc} \" failed",
    "installation_process_finished": "The installation process is finished"
}

# --------------------Sentences for the method install_cmd---------------------
message_install_global = {
    "does_not_exist": "{name} does not exist on your OS computer.\n",
    "dont_need": "You don't have any command to use because of your OS",
    "already_installed": "\"{name}\" is already installed on your computer"
}

# --------------------Sentences for the method install_cmds---------------------
message_install_sub = {
    "error_find_progress": "The package \"{name}\" isn't valid",
    "error_find_error": "The package \"{name}\" isn't valid :\n {error} \n",
    "error_occured_progress": "An error has occurred during the installation of : {name}",
    "error_occured_error": "An error has occurred during the installation of : {name}\n {error} \n",
    "installation_success": "The installation of \"{name}\" is a success."
}

# --------------------Sentences for the method version_pypi---------------------
message_version_sub = {
    "not_installed_progress": "\"{name}\" is not installed yet.",
    "not_installed_error": "\"{name}\" is not installed yet.\n {error} \n",
}

# --------------------Sentences for the method update_pypi---------------------
message_update_sub = {
    "error_find_progress": "The package \"{name}\" isn't valid",
    "error_find_error": "The package \"{name}\" isn't valid :\n {error} \n",
    "error_occured_progress": "An error has occurred during the update of : {name}",
    "error_occured_error": "An error has occurred during the update of : {name}\n {error} \n",
    "update_success": "The update of \"{name}\" is a success."
}

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
        self.__actual_feature = Feature()
        self.__cmd_errors = ""
        self.__system_errors = ""
        self.__pypi_errors = ""
        self.__total_errors = ""
        self.__features = Features("req_win", "cmd_win")
        self.get_features().read_config()

    # ---------------------------------------------------------------------------

    def get_features(self):
        """Return the private attribute __req.

        """
        return self.__features

    # ---------------------------------------------------------------------------

    def get_actual_feature(self):
        """Return the private attribute __actual_feature.

        """
        return self.__actual_feature

    # ---------------------------------------------------------------------------

    def set_actual_feature(self, feature):
        """Set the value of the private attribute __actual_feature.

        """
        if isinstance(feature, Feature) is False:
            raise NotImplementedError

        self.__actual_feature = feature

    # ---------------------------------------------------------------------------

    def get_set_progress(self, value):
        """Return and Set the private attribute __progression.

        :param value: (int) The value you want to add.

        """
        if value == 0:
            self.__progression = 0
            return self.__progression
        self.__progression += value
        if self.__progression >= 0.99:
            self.__progression = 1
        return self.__progression

    # ---------------------------------------------------------------------------

    def calcul_pourc(self, feature):
        """Return pourcentage of progression.

        :param feature: (Feature) The feature you use.

        """
        pourc = round((1 / (1 + len(feature.get_packages()) + len(feature.get_pypi()))), 2)
        return pourc

    # ---------------------------------------------------------------------------

    def get_cfg_exist(self):
        """Return True if the config file exist.

        """
        return self.get_features().get_cfg_exist()

    # ---------------------------------------------------------------------------

    def get_total_errors(self):
        """Return the private attribute __total_errors.

        """
        return self.__total_errors

    # ---------------------------------------------------------------------------

    def set_total_errors(self, string):
        """Fix the value of the private attribute __total_errors.

        :param string: (str) This string is filled with the errors you will encounter during
        all the installation procedure.

        """
        string = str(string)
        self.__total_errors += string

    # ---------------------------------------------------------------------------

    def save_errors(self, string):
        """Save the all the errors in the private attribute __total_errors.

        """
        if len(string) != 0:
            self.set_total_errors(string)

    # ---------------------------------------------------------------------------

    def show_save_cmd(self, progress, file_error=None):
        """Save in the cmd errors container the errors which happened during the installation.

        """
        self.__pbar.update(
            self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
            progress)
        self.set_cmd_errors(file_error)

    # ---------------------------------------------------------------------------

    def show_save_system(self, progress, file_error=None):
        """Save in the system errors the errors which happened during the installation.

        """
        self.__pbar.update(
            self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
            progress)
        self.set_system_errors(file_error)

    # ---------------------------------------------------------------------------

    def show_save_pypi(self, progress, file_error=None):
        """Save in the pypi errors container the errors which happened during the installation.

        """
        self.__pbar.update(
            self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
            progress)
        self.set_pypi_errors(file_error)

    # ---------------------------------------------------------------------------

    def create_file_errors(self):
        """Create the file with all the errors.

        """
        self.save_errors(self.get_cmd_errors())
        self.save_errors(self.get_system_errors())
        self.save_errors(self.get_pypi_errors())

        paths = sppasPathSettings()
        errors_file = os.path.join(paths.basedir, "errors.txt")
        with open(errors_file, "w") as my_errors:
            my_errors.write(self.get_total_errors())

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
            if self.__pbar is not None:
                self.__pbar.set_header(message_install["begining"])

            for f in self.get_features().get_features():
                self.set_actual_feature(f)
                self.get_set_progress(0)
                self.__pbar.set_header(message_install["begining_feature"].format(desc=f.get_desc()))
                if f.get_available() is False:
                    self.__pbar.update(self.get_set_progress(1),
                                       message_install["available_false"].format(name=f.get_id()))
                    continue
                if f.get_enable() is False:
                    self.__pbar.update(self.get_set_progress(1),
                                       message_install["enable_false"].format(name=f.get_id()))
                    continue

                try:
                    self.install_cmd(f)
                    self.install_packages(f)
                    self.install_pypis(f)
                    f.set_enable(True)
                    self.__pbar.set_header(message_install["installation_success"].format(desc=f.get_desc()))
                except NotImplementedError:
                    self.__pbar.set_header(message_install["installation_failed"].format(desc=f.get_desc()))
                    self.create_file_errors()

            self.__pbar.set_header(message_install["installation_process_finished"])

            self.get_features().write_config()

        else:
            self.get_features().write_config()

    # ---------------------------------------------------------------------------

    def install_cmd(self, feature):
        """Use the command which is in your feature.

        :param feature: (string) The pip package you will try to install on your computer.

        """
        if isinstance(feature, Feature) is False:
            raise NotImplementedError

        feature_command = feature.get_cmd()

        if feature_command == "none":
            feature.set_available(False)
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                message_install_global["does_not_exist"].format(name=feature.get_id()))
        elif feature_command == "nil":
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                message_install_global["dont_need"])
        else:
            if self.search_cmds(feature.get_id()) is False:
                self.install_cmds(feature_command, feature)
            else:
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                    message_install_global["already_installed"].format(name=feature.get_id()))

        if len(self.get_cmd_errors()) != 0:
            feature.set_enable(False)
            raise NotImplementedError()

    # ---------------------------------------------------------------------------

    def search_cmds(self, command):
        """Return True if the command is installed on your PC.

        :param command: (string) The command you will try to install on your computer.

        """
        command = command.strip()
        NULL = open(os.path.devnull, "w")
        try:
            call(command, stdout=NULL, stderr=STDOUT)
        except OSError:
            NULL.close()
            return False

        NULL.close()
        return True

    # ---------------------------------------------------------------------------

    def install_cmds(self, command, feature):
        """Install the pip package given as an argument on your computer.

        :param command: (string) The command you will try to install on your computer.
        :param feature: (string) The name of the feature from which you will use the command.

        """
        if isinstance(feature, Feature) is False:
            raise NotImplementedError

        self.set_cmd_errors("")

        try:
            process = Process()
            process.run_popen(command)
            error = process.error()
            if len(error) != 0:
                self.show_save_cmd(message_install_sub["occured_progress"].format(name=feature.get_id()),
                                   message_install_sub["occured_error"].format(name=feature.get_id(), error=error))
            else:
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                    message_install_sub["installation_success"].format(name=feature.get_id()))

        except FileNotFoundError:
            self.show_save_cmd(message_install_sub["error_occured_progress"].format(name=feature.get_id()),
                               message_install_sub["error_occured_error"]
                               .format(name=feature.get_id(), error=FileNotFoundError))

    # ---------------------------------------------------------------------------

    def install_pypis(self, feature):
        """Manage the procedure of installation of your pip requirements.

        :param feature: (str) The feature you will use to browse the private dictionary __pypi, to install the
        pip packages.

        """
        if isinstance(feature, Feature) is False:
            raise NotImplementedError

        self.set_pypi_errors("")
        for package, version in feature.get_pypi().items():
            if package == "nil":
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                    message_install_global["dont_need"].format(name=feature.get_id()))
            else:
                if self.search_pypi(package) is False:
                    self.install_pypi(package)
                elif self.version_pypi(package, version) is False:
                    self.update_pypi(package)
                else:
                    self.__pbar.update(
                        self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                        message_install_global["already_installed"].format(name=package))

        if len(self.get_pypi_errors()) != 0:
            feature.set_enable(False)
            raise NotImplementedError()

    # ---------------------------------------------------------------------------

    @staticmethod
    def search_pypi(package):
        """Returns True if the pip package given as an argument is installed or not on your computer.

        :param package: (string) The pip package you are searching if it is installed
        or not on your computer.

        """
        package = str(package)
        command = "pip3 show " + package
        process = Process()
        process.run_popen(command)
        error = process.error()
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
        command = "pip3 install " + package + " --no-warn-script-location"
        process = Process()
        process.run_popen(command)
        error = process.error()
        if len(error) != 0:
            if "Could not find" in error:
                self.show_save_pypi(message_install_sub["error_find_progress"].format(name=package),
                                    message_install_sub["error_find_error"].format(name=package, error=error))
            else:
                self.show_save_pypi(message_install_sub["error_occured_progress"].format(name=package),
                                    message_install_sub["error_occured_error"].format(name=package, error=error))
        else:
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                message_install_sub["installation_success"].format(name=package))

    # ---------------------------------------------------------------------------

    def version_pypi(self, package, req_version):
        """Returns True if the pip package given as an argument has the good version or not on your computer.

        :param package: (string) The pip package you are searching if his version is enough
        recent or not.
        :param req_version: (string) The minimum version you need to have for this pip
        package.

        """
        package = str(package)
        command = "pip3 show " + package
        process = Process()
        process.run_popen(command)
        error = process.error()
        stdout = process.out()
        if "not found" in error:
            self.show_save_pypi(message_version_sub["not_installed_progress"].format(name=package),
                                message_version_sub["not_installed_error"].format(name=package, error=error))
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
        command = "pip3 install -U " + package
        process = Process()
        process.run_popen(command)
        error = process.error()
        if len(error) != 0:
            if "Could not find" in error:
                self.show_save_pypi(message_update_sub["error_find_progress"].format(name=package),
                                    message_update_sub["error_find_progress"].format(name=package, error=error))
            else:
                self.show_save_pypi(message_update_sub["error_occured_progress"].format(name=package),
                                    message_update_sub["error_occured_error"].format(name=package, error=error))
        else:
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                message_update_sub["update_success"].format(name=package))

    # ---------------------------------------------------------------------------

    def install_packages(self, feature):
        """Manage the procedure of installation of your __req requirements.

        :param feature: (str) The feature you will use to browse the private dictionary __packages, to install the
        system packages.

        """
        if isinstance(feature, Feature) is False:
            raise NotImplementedError

        self.set_system_errors("")
        for package, version in feature.get_packages().items():
            if package == "nil":
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                    message_install_global["dont_need"].format(name=feature.get_id()))

            else:
                if self.search_package(package) is False:
                    self.install_package(package)
                elif self.version_package(package, version) is False:
                    self.update_package(package)
                else:
                    self.__pbar.update(
                        self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                        message_install_global["already_installed"].format(name=package))

        if len(self.get_system_errors()) != 0:
            feature.set_enable(False)
            raise NotImplementedError()

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

    def __init__(self, p):
        """Create a new Deb(Installer) instance.

        """
        super(Deb, self).__init__(p)
        self.__features = Features("req_deb", "cmd_deb")

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
        self.__features = Features("req_rpm", "cmd_rpm")

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
        self.__features = Features("req_rpm", "cmd_rpm")

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
        self.__features = Features("req_win", "cmd_win")

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
        self.__features = Features("req_cyg", "cmd_win")

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
        self.__features = Features("req_ios", "cmd_ios")

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if the system package given as an argument is installed or not on your computer.

        :param package: (string) The system package you are searching if it is installed
        or not on your computer.

        """
        package = str(package)
        command = "brew list " + package
        process = Process()
        process.run_popen(command)
        error = process.error()
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
        command = "brew install " + package
        process = Process()
        process.run_popen(command)
        error = process.error()
        if len(error) != 0:
            if "Warning: You are using macOS" in error:
                if self.search_package(package) is False:
                    self.show_save_system(message_install_sub["error_occured_progress"].format(name=package),
                                          message_install_sub["error_occured_error"].format(name=package, error=error))
                else:
                    self.__pbar.update(
                        self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                        "The installation of \"{name}\" is a success.".format(name=package))

            elif "No available" in error:
                self.show_save_system(message_install_sub["error_find_progress"].format(name=package),
                                      message_install_sub["error_find_error"].format(name=package, error=error))
            else:
                self.show_save_system(message_install_sub["error_occured_progress"].format(name=package),
                                      message_install_sub["error_occured_error"].format(name=package, error=error))
        else:
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                message_install_sub["installation_success"].format(name=package))

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Update the system package given as an argument on your computer.

        :param package: (string) The brew package you are searching if his version is enough
        recent or not.

        :param req_version: (string) The minimum version you need to have for this brew
        package.

        """
        req_version = str(req_version)
        package = str(package)
        command = "brew info " + package
        process = Process()
        process.run_popen(command)
        error = process.error()
        stdout = process.out()
        if len(error) != 0:
            self.show_save_system(message_version_sub["not_installed_progress"].format(name=package),
                                  message_version_sub["not_installed_error"].format(name=package, error=error))
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
        command = "brew upgrade " + package
        process = Process()
        process.run_popen(command)
        error = process.error()
        if len(error) != 0:
            if "Could not find" in error:
                self.show_save_system(message_update_sub["error_find_progress"].format(name=package),
                                      message_update_sub["error_find_error"].format(name=package, error=error))
            else:
                self.show_save_system(message_update_sub["error_occured_progress"].format(name=package),
                                      message_update_sub["error_occured_error"].format(name=package, error=error))
        else:
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc(self.get_actual_feature())),
                message_update_sub["update_success"].format(name=package))

    # ---------------------------------------------------------------------------
