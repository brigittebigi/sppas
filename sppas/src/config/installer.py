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

"""

import os
from subprocess import call, STDOUT
import logging

from sppas.src.config.features import Features, Feature
from sppas.src.config.process import Process

# ---------------------Sentences for the method install-----------------------
MSG_INSTALL = {
    "begining": "Start Installation",
    "begining_feature": "Installation \"{desc}\"",
    "available_false": "\"{desc}\" not available on your OS.",
    "enable_false": "You choose to don't install : \"{desc}\"",
    "installation_success": "Installation \"{desc}\" successful",
    "installation_failed": "Installation \"{desc}\" failed",
    "installation_process_finished": "Installation finished"
}

# --------------------Sentences for the method install_cmd---------------------
MSG_INSTALL_GLOBAL = {
    "does_not_exist": "{name} invalid package.\n",
    "dont_need": "Don't need command",
    "installation_successful": "Installation \"{name}\" successful"
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

        Installer is a Class which allows to install dependencies from a
        Features Object.
        It will browse your Features Object to install, according to the
        OS of the computer, the dependencies inform in your Features Objects.
        The installation is launched with the method :

        >>> Installer.install()

    """

    def __init__(self, p):
        """Create a new Installer instance.

        :param p: (ProcessProgressTerminal) The installation progress.

        """
        logging.basicConfig(level=logging.DEBUG)
        self.__pbar = p
        self.__progression = 0
        self.__total__errors = ""
        self.__errors = ""
        self._features = None

    # ---------------------------------------------------------------------------

    def get_feat_ids(self):
        """Return the list of feature identifiers."""
        return self._features.get_ids()

    # ---------------------------------------------------------------------------

    def enable(self, fid, value=None):
        """Return True if the feature is enabled and/or set it.

        :param fid: (str) Identifier of a feature
        :param value: (bool or None) Enable of disable the feature.

        """
        return self._features.enable(fid, value)

    # ---------------------------------------------------------------------------

    def available(self, fid, value=None):
        """Return True if the feature is available and/or set it.

        :param fid: (str) Identifier of a feature
        :param value: (bool or None) Make the feature available or not.

        """
        return self._features.available(fid, value)

    # ---------------------------------------------------------------------------

    def description(self, fid):
        """Return the description of the feature.

        :param fid: (str) Identifier of a feature
        :return: (str)

        """
        return self._features.description(fid)

    # ---------------------------------------------------------------------------

    def get_set_progress(self, value):
        """Return the progression and/or set it.

        :param value: (int) The value you want to add.
        :return: (float) The value of the progression.

        """
        if value == 0:
            self.__progression = 0
            return self.__progression
        self.__progression += value
        if self.__progression >= 0.99:
            self.__progression = 1.0
        return self.__progression

    # ---------------------------------------------------------------------------

    def calcul_pourc(self, fid):
        """Calcul and return a percentage of progression.

        :param fid: (str) Identifier of a feature
        :return: (float)

        """
        nb_packages = len(self._features.packages(fid))
        nb_pypi = len(self._features.pypi(fid))
        pourc = round((1 / (1 + nb_packages + nb_pypi)), 2)
        return pourc

    # ---------------------------------------------------------------------------

    def get_cfg_exist(self):
        """Return True if the config file exist."""
        return self._features.get_cfg_exist()

    # ---------------------------------------------------------------------------

    def _set_total_errors(self, msg):
        """Add an error message in total errors.

        :param msg: (str)

        """
        if len(msg) != 0:
            string = str(msg)
            self.__total__errors += string

    # ---------------------------------------------------------------------------

    def _set_errors(self, msg):
        """Append an error message.

        :param msg: (str)

        """
        msg = str(msg)
        if len(msg) == 0:
            self.__errors = ""
        else:
            self.__errors += msg

    # ---------------------------------------------------------------------------

    def fill_errors(self, error_msg):
        """Fill errors and total_errors.

        :param error_msg: (str)

        """
        self._set_errors(error_msg)
        self._set_total_errors(error_msg)

    # ---------------------------------------------------------------------------

    def install(self):
        """Manage the installation procedure."""
        if self.get_cfg_exist() is False:
            if self.__pbar is not None:
                self.__pbar.set_header(MSG_INSTALL["begining"])

            for feat_id in self.get_feat_ids():
                self._set_errors("")
                self.get_set_progress(0)
                self.__pbar.set_header(MSG_INSTALL["begining_feature"]
                                       .format(desc=self._features.description(feat_id)))
                if self._features.available(feat_id) is False:
                    self.__pbar.update(self.get_set_progress(1),
                                       MSG_INSTALL["available_false"].format(desc=self._features.description(feat_id)))
                    continue
                if self._features.enable(feat_id) is False:
                    self.__pbar.update(self.get_set_progress(1),
                                       MSG_INSTALL["enable_false"].format(desc=self._features.description(feat_id)))
                    continue

                try:
                    self.install_cmd(feat_id)
                    self.install_packages(feat_id)
                    self.install_pypis(feat_id)
                    self._features.enable(feat_id, True)
                    self.__pbar.set_header(MSG_INSTALL["installation_success"]
                                           .format(desc=self._features.description(feat_id)))
                except NotImplementedError:
                    self.__pbar.set_header(MSG_INSTALL["installation_failed"]
                                           .format(desc=self._features.description(feat_id)))

            self.__pbar.set_header(MSG_INSTALL["installation_process_finished"])

            self._features.update_config()

        else:
            self._features.update_config()
        return self.__total__errors

    # ---------------------------------------------------------------------------

    def install_cmd(self, feat_id):
        """Manage the installation of the command of a feature.

        :param feat_id: (str) Identifier of a feature

        """
        feat_id = str(feat_id)

        feature_command = self._features.cmd(feat_id)

        if feature_command == "none":
            self._features.available(feat_id, False)
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc(feat_id)),
                MSG_INSTALL_GLOBAL["does_not_exist"].format(name=feat_id))
        elif feature_command == "nil":
            self.__pbar.update(
                self.get_set_progress(self.calcul_pourc(feat_id)),
                MSG_INSTALL_GLOBAL["dont_need"])
        else:
            if self.search_cmds(feat_id) is False:
                self.install_cmds(feature_command, feat_id)
            else:
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(feat_id)), feat_id)
                logging.info(MSG_INSTALL_GLOBAL["installation_successful"].format(name=feat_id))

        if len(self.__errors) != 0:
            self._features.enable(feat_id, False)
            raise NotImplementedError()

    # ---------------------------------------------------------------------------

    def search_cmds(self, command):
        """Return True if the command is installed on a PC.

        :param command: (string) The command to search.

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

    def install_cmds(self, command, feat_id):
        """Install feat_id.

        :param command: (string) The command to execute.
        :param feat_id: (str) Identifier of a feature

        """
        feat_id = str(feat_id)

        try:
            process = Process()
            process.run_popen(command)
            error = process.error()
            if len(error) != 0:
                self.fill_errors("Installation \"{name}\" failed.\nError : {error}".format(name=feat_id, error=error))

        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=feat_id, error=FileNotFoundError))

    # ---------------------------------------------------------------------------

    def install_pypis(self, feat_id):
        """Manage the installation of pip packages.

        :param feat_id: (str) Identifier of a feature

        """
        feat_id = str(feat_id)

        for package, version in self._features.pypi(feat_id).items():
            if package == "nil":
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(feat_id)),
                    MSG_INSTALL_GLOBAL["dont_need"].format(name=feat_id))
            else:
                if self.search_pypi(package) is False:
                    if self.install_pypi(package) is False:
                        break
                elif self.version_pypi(package, version) is False:
                    if self.update_pypi(package) is False:
                        break
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(feat_id)), package)
                logging.info(MSG_INSTALL_GLOBAL["installation_successful"].format(name=package))

        if len(self.__errors) != 0:
            self._features.enable(feat_id, False)
            raise NotImplementedError()

    # ---------------------------------------------------------------------------

    def search_pypi(self, package):
        """Returns True if package is already installed.

        :param package: (string) The pip package to search.

        """
        try:
            package = str(package)
            command = "pip3 show " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            if "not found" in error:
                return False
            else:
                return True
        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=package, error=FileNotFoundError))
            return False

    # ---------------------------------------------------------------------------

    def install_pypi(self, package):
        """Install package.

        :param package: (string) The pip package to install
        :returns: False or None

        """
        try:
            package = str(package)
            command = "pip3 install " + package + " --no-warn-script-location"
            process = Process()
            process.run_popen(command)
            error = process.error()
            if len(error) != 0:
                if "Could not find" in error:
                    self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                else:
                    self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                return False
        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=package, error=FileNotFoundError))
            return False

    # ---------------------------------------------------------------------------

    def version_pypi(self, package, req_version):
        """Returns True if package is up to date.

        :param package: (string) The pip package to search.
        :param req_version: (string) The minimum version required.

        """
        try:
            package = str(package)
            command = "pip3 show " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            stdout = process.out()
            if self.need_update_pypi(stdout, req_version):
                return False
            else:
                return True
        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=package, error=FileNotFoundError))
            return False

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_pypi(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout of the command.
        :param req_version: (string) The minimum version required.

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
        """Update package.

        :param package: (string) The pip package to update.
        :returns: False or None

        """
        try:
            package = str(package)
            command = "pip3 install -U " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            if len(error) != 0:
                if "Could not find" in error:
                    self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                else:
                    self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                return False
        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=package, error=FileNotFoundError))
            return False

    # ---------------------------------------------------------------------------

    def install_packages(self, feat_id):
        """Manage installation of system packages.

        :param feat_id: (str) Identifier of a feature

        """
        feat_id = str(feat_id)

        for package, version in self._features.packages(feat_id).items():
            if package == "nil":
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(feat_id)),
                    MSG_INSTALL_GLOBAL["dont_need"].format(name=feat_id))

            else:
                if self.search_package(package) is False:
                    if self.install_package(package) is False:
                        break
                elif self.version_package(package, version) is False:
                    if self.update_package(package) is False:
                        break
                self.__pbar.update(
                    self.get_set_progress(self.calcul_pourc(feat_id)),
                    MSG_INSTALL_GLOBAL["installation_successful"].format(name=package))
                logging.info(MSG_INSTALL_GLOBAL["installation_successful"].format(name=package))

        if len(self.__errors) != 0:
            self._features.enable(feat_id, False)
            raise NotImplementedError()

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if package is already installed.

        :param package: (string) The system package to search.

        """
        package = str(package)
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install package.

        :param package: (string) The system package to install.
        :returns: False or None

        """
        package = str(package)
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (string) The system package to search.
        :param req_version: (string) The minimum version required.

        """
        package = str(package)
        req_version = str(req_version)
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout of the command.
        :param req_version: (string) The minimum version required.

        """
        stdout_show = str(stdout_show)
        req_version = str(req_version)
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update package.

        :param package: (string) The system package to update.
        :returns: False or None

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
        """Create a new Deb(Installer) instance."""
        super(Deb, self).__init__(p)
        self._features = Features("req_deb", "cmd_deb")

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if package is already installed.

        :param package: (string) The system package to search.

        """
        return True

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install package.

        :param package: (string) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (string) The system package to search.
        :param req_version: (string) The minimum version required.

        """
        return True

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout of the command.
        :param req_version: (string) The minimum version required.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update package.

        :param package: (string) The system package to update.
        :returns: False or None

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
        """Create a new Rpm(Installer) instance."""
        super(Rpm, self).__init__(p)
        self._features = Features("req_rpm", "cmd_rpm")

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if package is already installed.

        :param package: (string) The system package to search.

        """
        return True

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install package.

        :param package: (string) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (string) The system package to search.
        :param req_version: (string) The minimum version required.

        """
        return True

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout of the command.
        :param req_version: (string) The minimum version required.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update package.

        :param package: (string) The system package to update.
        :returns: False or None

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
        """Create a new Dnf(Installer) instance."""
        super(Dnf, self).__init__(p)
        self._features = Features("req_dnf", "cmd_dnf")

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if package is already installed.

        :param package: (string) The system package to search.

        """
        return True

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install package.

        :param package: (string) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (string) The system package to search.
        :param req_version: (string) The minimum version required.

        """
        return True

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout of the command.
        :param req_version: (string) The minimum version required.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update package.

        :param package: (string) The system package to update.
        :returns: False or None

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
        """Create a new Windows(Installer) instance."""
        super(Windows, self).__init__(p)
        self._features = Features("req_win", "cmd_win")

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if package is already installed.

        :param package: (string) The system package to search.

        """
        return True

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install package.

        :param package: (string) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (string) The system package to search.
        :param req_version: (string) The minimum version required.

        """
        return True

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout of the command.
        :param req_version: (string) The minimum version required.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update package.

        :param package: (string) The system package to update.
        :returns: False or None

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
        """Create a new CygWin(Installer) instance."""
        super(CygWin, self).__init__(p)
        self._features = Features("req_cyg", "cmd_cyg")

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if package is already installed.

        :param package: (string) The system package to search.

        """
        return True

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install package.

        :param package: (string) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (string) The system package to search.
        :param req_version: (string) The minimum version required.

        """
        return True

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout of the command.
        :param req_version: (string) The minimum version required.

        """
        raise NotImplementedError

    # ---------------------------------------------------------------------------

    def update_package(self, package):
        """Update package.

        :param package: (string) The system package to update.
        :returns: False or None

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
        """Create a new MacOs(Installer) instance."""
        super(MacOs, self).__init__(p)
        self._features = Features("req_ios", "cmd_ios")

    # ---------------------------------------------------------------------------

    def search_package(self, package):
        """Returns True if package is already installed.

        :param package: (string) The system package to search.

        """
        try:
            package = str(package)
            command = "brew list " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            if len(error) != 0:
                return False
            else:
                return True
        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=package, error=FileNotFoundError))
            return False

    # ---------------------------------------------------------------------------

    def install_package(self, package):
        """Install package.

        :param package: (string) The system package to install.
        :returns: False or None

        """
        try:
            package = str(package)
            command = "brew install " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            if len(error) != 0:
                if "Warning: You are using macOS" in error:
                    if self.search_package(package) is False:
                        self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                        return False

                elif "No available" in error:
                    self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                    return False
                else:
                    self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                    return False
        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=package, error=FileNotFoundError))
            return False

    # ---------------------------------------------------------------------------

    def version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (string) The system package to search.
        :param req_version: (string) The minimum version required.

        """
        try:
            req_version = str(req_version)
            package = str(package)
            command = "brew info " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            stdout = process.out()
            if self.need_update_package(stdout, req_version):
                return False
            else:
                return True
        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=package, error=FileNotFoundError))
            return False

    # ---------------------------------------------------------------------------

    @staticmethod
    def need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (string) The stdout of the command.
        :param req_version: (string) The minimum version required.

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
        """Update package.

        :param package: (string) The system package to update.
        :returns: False or None

        """
        try:
            package = str(package)
            command = "brew upgrade " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            if len(error) != 0:
                if "Could not find" in error:
                    self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                else:
                    self.fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                return False
        except FileNotFoundError:
            self.fill_errors("Installation \"{name}\" failed.\nError : {error}"
                             .format(name=package, error=FileNotFoundError))
            return False

    # ---------------------------------------------------------------------------

