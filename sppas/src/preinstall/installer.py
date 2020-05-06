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

    src.preinstall.installer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from sppas.src.config.process import Process, search_cmd
from sppas.src.config import info
from .features import Features

# ---------------------------------------------------------------------------


def _(identifier):
    return info(identifier, "globals")


MESSAGES = {
    "beginning": _(500),
    "beginning_feature": _(510),
    "available_false": _(520),
    "enable_false": _(530),
    "install_success": _(540),
    "install_failed": _(550),
    "install_finished": _(560),
    "does_not_exist": _(570),
    "dont_need": _(580)
}

# ---------------------------------------------------------------------------


class Installer(object):
    """Manage the installation of external required or optional features.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        It will browse the Features() to install, according to the OS of
        the computer. The installation is launched with the method:

        >>> Installer.install()

    """

    def __init__(self, p=None):
        """Create a new Installer instance.

        :param p: (ProcessProgressTerminal) The installation progress.

        """
        logging.basicConfig(level=logging.DEBUG)
        self.__pbar = p
        self.__progression = 0
        self.__total__errors = ""
        self.__errors = ""
        self._features = Features(req="", cmdos="")

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def get_feat_ids(self):
        """Return the list of feature identifiers."""
        return self._features.get_ids()

    # ------------------------------------------------------------------------

    def enable(self, fid, value=None):
        """Return True if the feature is enabled and/or set it.

        :param fid: (str) Identifier of a feature
        :param value: (bool or None) Enable of disable the feature.

        """
        return self._features.enable(fid, value)

    # ------------------------------------------------------------------------

    def available(self, fid, value=None):
        """Return True if the feature is available and/or set it.

        :param fid: (str) Identifier of a feature
        :param value: (bool or None) Make the feature available or not.

        """
        return self._features.available(fid, value)

    # ------------------------------------------------------------------------

    def description(self, fid):
        """Return the description of the feature.

        :param fid: (str) Identifier of a feature
        :return: (str)

        """
        return self._features.description(fid)

    # ------------------------------------------------------------------------

    def install(self):
        """Process the installation procedure."""
        if self.__pbar is not None:
            self.__pbar.set_header(MESSAGES["beginning"])

        for feat_id in self.get_feat_ids():
            self.__set_errors("")
            self.__get_set_progress(0)
            self.__pbar.set_header(
                MESSAGES["beginning_feature"].format(name=self._features.description(feat_id)))

            if self._features.available(feat_id) is False:
                self.__pbar.update(
                    self.__get_set_progress(1),
                    MESSAGES["available_false"].format(name=self._features.description(feat_id)))

            elif self._features.enable(feat_id) is False:
                self.__pbar.update(
                    self.__get_set_progress(1),
                    MESSAGES["enable_false"].format(name=self._features.description(feat_id)))

            else:

                try:
                    self.__install_cmd(feat_id)
                    self.__install_packages(feat_id)
                    self.__install_pypis(feat_id)
                    self._features.enable(feat_id, True)
                    self.__pbar.set_header(
                        MESSAGES["install_success"].format(name=self._features.description(feat_id)))

                except NotImplementedError:
                    self._features.enable(feat_id, False)
                    self.__pbar.set_header(
                        MESSAGES["install_failed"].format(name=self._features.description(feat_id)))

        self._features.update_config()
        self.__pbar.set_header(MESSAGES["install_finished"])

        return self.__total__errors

    # ------------------------------------------------------------------------

    def __install_cmd(self, feat_id):
        """Execute a system command for a feature.

        :param feat_id: (str) Identifier of a feature

        """
        feat_id = str(feat_id)
        feature_command = self._features.cmd(feat_id)

        if feature_command == "none":
            self._features.available(feat_id, False)
            self.__pbar.update(
                self.__get_set_progress(self.__calcul_pourc(feat_id)),
                MESSAGES["does_not_exist"].format(name=feat_id))

        elif feature_command == "nil":
            self.__pbar.update(
                self.__get_set_progress(self.__calcul_pourc(feat_id)),
                MESSAGES["dont_need"])

        else:
            if search_cmd(feat_id) is False:
                self.__install_cmds(feature_command, feat_id)
            else:
                self.__pbar.update(
                    self.__get_set_progress(self.__calcul_pourc(feat_id)), feat_id)
                logging.info(MESSAGES["install_success"].format(name=feat_id))

        if len(self.__errors) != 0:
            raise NotImplementedError

    # ------------------------------------------------------------------------

    def __install_packages(self, feat_id):
        """Manage installation of system packages.

        :param feat_id: (str) Identifier of a feature

        """
        feat_id = str(feat_id)

        for package, version in self._features.packages(feat_id).items():
            if package == "nil":
                self.__pbar.update(
                    self.__get_set_progress(self.__calcul_pourc(feat_id)),
                    MESSAGES["dont_need"].format(name=feat_id))

            else:
                if self._search_package(package) is False:
                    if self._install_package(package) is False:
                        break
                elif self._version_package(package, version) is False:
                    if self._update_package(package) is False:
                        break
                self.__pbar.update(
                    self.__get_set_progress(self.__calcul_pourc(feat_id)),
                    MESSAGES["install_success"].format(name=package))

        if len(self.__errors) != 0:
            raise NotImplementedError

    # ------------------------------------------------------------------------

    def __install_pypis(self, feat_id):
        """Manage the installation of pip packages.

        :param feat_id: (str) Identifier of a feature

        """
        feat_id = str(feat_id)

        for package, version in self._features.pypi(feat_id).items():
            if package == "nil":
                self.__pbar.update(
                    self.__get_set_progress(self.__calcul_pourc(feat_id)),
                    MESSAGES["dont_need"].format(name=feat_id))

            else:
                if self.__search_pypi(package) is False:
                    if self.__install_pypi(package) is False:
                        break
                elif self.__version_pypi(package, version) is False:
                    if self.__update_pypi(package) is False:
                        break
                self.__pbar.update(
                    self.__get_set_progress(self.__calcul_pourc(feat_id)), package)
                logging.info(MESSAGES["install_success"].format(name=package))

        if len(self.__errors) != 0:
            raise NotImplementedError

    # ------------------------------------------------------------------------
    # Management of package dependencies. OS dependent: must be overridden.
    # ------------------------------------------------------------------------

    def _search_package(self, package):
        """To be overridden. Return True if package is already installed.

        :param package: (str) The system package to search.

        """
        package = str(package)
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _install_package(self, package):
        """To be overridden. Install package.

        :param package: (str) The system package to install.
        :returns: False or None

        """
        package = str(package)
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _version_package(self, package, req_version):
        """To be overridden. Return True if the package is up to date.

        :param package: (str) The system package to search.
        :param req_version: (str) The minimum version required.

        """
        package = str(package)
        req_version = str(req_version)
        raise NotImplementedError

    # ------------------------------------------------------------------------

    @staticmethod
    def _need_update_package(stdout_show, req_version):
        """To be overridden. Return True if the package need to be update.

        :param stdout_show: (str) The stdout of the command.
        :param req_version: (str) The minimum version required.

        """
        stdout_show = str(stdout_show)
        req_version = str(req_version)
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _update_package(self, package):
        """To be overridden. Update package.

        :param package: (str) The system package to update.
        :returns: False or None

        """
        package = str(package)
        raise NotImplementedError

    # ------------------------------------------------------------------------
    # Private, for internal use only. Not needed by any sub-class.
    # ------------------------------------------------------------------------

    def __calcul_pourc(self, fid):
        """Estimate and return a percentage of progression.

        :param fid: (str) Identifier of a feature
        :return: (float)

        """
        nb_packages = len(self._features.packages(fid))
        nb_pypi = len(self._features.pypi(fid))
        pourc = round((1 / (1 + nb_packages + nb_pypi)), 2)
        return pourc

    # ------------------------------------------------------------------------

    def __get_set_progress(self, value):
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

    # ------------------------------------------------------------------------

    def __set_total_errors(self, msg):
        """Add an error message in total errors.

        :param msg: (str)

        """
        if len(msg) != 0:
            string = str(msg)
            self.__total__errors += string

    # ------------------------------------------------------------------------

    def __set_errors(self, msg):
        """Append an error message.

        :param msg: (str)

        """
        msg = str(msg)
        if len(msg) == 0:
            self.__errors = ""
        else:
            self.__errors += msg

    # ------------------------------------------------------------------------

    def __fill_errors(self, error_msg):
        """Fill errors and total_errors.

        :param error_msg: (str)

        """
        self.__set_errors(error_msg)
        self.__set_total_errors(error_msg)

    # ------------------------------------------------------------------------

    def __install_cmds(self, command, feat_id):
        """Install feat_id with the given command.

        :param command: (str) The command to execute.
        :param feat_id: (str) Identifier of a feature

        """
        feat_id = str(feat_id)

        try:
            process = Process()
            process.run_popen(command)
            error = process.error()
            if len(error) != 0:
                self.__fill_errors("Installation \"{name}\" failed.\nError : {error}".format(name=feat_id, error=error))

        except FileNotFoundError:
            self.__fill_errors("Installation \"{name}\" failed.\nError : {error}"
                               .format(name=feat_id, error=FileNotFoundError))

    # ------------------------------------------------------------------------

    def __search_pypi(self, package):
        """Return True if given Pypi package is already installed.

        :param package: (str) The pip package to search.

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
            self.__fill_errors("Installation \"{name}\" failed.\nError : {error}"
                               .format(name=package, error=FileNotFoundError))
            return False

    # ------------------------------------------------------------------------

    def __install_pypi(self, package):
        """Install a Python Pypi package.

        :param package: (str) The pip package to install
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
                    self.__fill_errors("Package: \"{name}\"\nError: {error}".format(name=package, error=error))
                else:
                    self.__fill_errors("Package: \"{name}\"\nError: {error}".format(name=package, error=error))
                return False
        except FileNotFoundError:
            self.__fill_errors("Installation \"{name}\" failed.\nError : {error}"
                               .format(name=package, error=FileNotFoundError))
            return False

    # ------------------------------------------------------------------------

    def __version_pypi(self, package, req_version):
        """Returns True if package is up to date.

        :param package: (str) The pip package to search.
        :param req_version: (str) The minimum version required.

        """
        try:
            package = str(package)
            command = "pip3 show " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            stdout = process.out()
            return not Installer.__need_update_pypi(stdout, req_version)

        except FileNotFoundError:
            self.__fill_errors("Installation \"{name}\" failed.\nError : {error}"
                               .format(name=package, error=FileNotFoundError))

        return False

    # ------------------------------------------------------------------------

    @staticmethod
    def __need_update_pypi(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (str) The stdout of the command.
        :param req_version: (str) The minimum version required.

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
            return v < version

        raise ValueError("The comparator: " + comparator +
                         " does not refer to a valid comparator")

    # ------------------------------------------------------------------------

    def __update_pypi(self, package):
        """Update package.

        :param package: (str) The pip package to update.
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
                    self.__fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                else:
                    self.__fill_errors("package : \"{name}\"\nError: {error}".format(name=package, error=error))
                return False
        except FileNotFoundError:
            self.__fill_errors("Installation \"{name}\" failed.\nError : {error}"
                               .format(name=package, error=FileNotFoundError))
            return False

# ----------------------------------------------------------------------------


class Deb(Installer):
    """An installer for Debian-based package manager systems.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        This Deb(Installer) is made for the Debians distributions of Linux,
        like Debian, Ubuntu or Mint.

    """

    def __init__(self, p):
        """Create a new Deb instance."""
        super(Deb, self).__init__(p)
        self._features = Features("req_deb", "cmd_deb")

    # -----------------------------------------------------------------------

    def _search_package(self, package):
        """Returns True if package is already installed.

        :param package: (str) The system package to search.

        """
        return True

    # -----------------------------------------------------------------------

    def _install_package(self, package):
        """Install the given package.

        :param package: (str) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (str) The system package to search.
        :param req_version: (str) The minimum version required.

        """
        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def _need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (str) The stdout of the command.
        :param req_version: (str) The minimum version required.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _update_package(self, package):
        """Update package.

        :param package: (str) The system package to update.
        :returns: False or None

        """
        raise NotImplementedError

# ---------------------------------------------------------------------------


class Rpm(Installer):
    """An installer for RPM-based package manager system.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        This RPM is made for the linux distributions like RedHat, or Suse.

    """

    def __init__(self, p):
        """Create a new Rpm(Installer) instance."""
        super(Rpm, self).__init__(p)
        self._features = Features("req_rpm", "cmd_rpm")

    # ------------------------------------------------------------------------

    def _search_package(self, package):
        """Returns True if package is already installed.

        :param package: (str) The system package to search.

        """
        return True

    # ------------------------------------------------------------------------

    def _install_package(self, package):
        """Install the given package.

        :param package: (str) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (str) The system package to search.
        :param req_version: (str) The minimum version required.

        """
        return True

    # ------------------------------------------------------------------------

    @staticmethod
    def _need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (str) The stdout of the command.
        :param req_version: (str) The minimum version required.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _update_package(self, package):
        """Update package.

        :param package: (str) The system package to update.
        :returns: False or None

        """
        raise NotImplementedError

# ---------------------------------------------------------------------------


class Dnf(Installer):
    """An installer for DNF-based package manager systems.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This DNF is made for linux distributions like Fedora.

    """

    def __init__(self, p):
        """Create a new Dnf(Installer) instance."""
        super(Dnf, self).__init__(p)
        self._features = Features("req_dnf", "cmd_dnf")

    # ------------------------------------------------------------------------

    def _search_package(self, package):
        """Returns True if package is already installed.

        :param package: (str) The system package to search.

        """
        return True

    # ------------------------------------------------------------------------

    def _install_package(self, package):
        """Install the given package.

        :param package: (str) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (str) The system package to search.
        :param req_version: (str) The minimum version required.

        """
        return True

    # ------------------------------------------------------------------------

    @staticmethod
    def _need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (str) The stdout of the command.
        :param req_version: (str) The minimum version required.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _update_package(self, package):
        """Update package.

        :param package: (str) The system package to update.
        :returns: False or None

        """
        raise NotImplementedError

# ---------------------------------------------------------------------------


class Windows(Installer):
    """An installer for Microsoft Windows system.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        This Windows installer was tested with Windows 10.

    """

    def __init__(self, p):
        """Create a new Windows instance."""
        super(Windows, self).__init__(p)
        self._features = Features("req_win", "cmd_win")

    # ------------------------------------------------------------------------

    def _version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (str) The system package to search.
        :param req_version: (str) The minimum version required.

        """
        return True

# ----------------------------------------------------------------------------


class MacOs(Installer):
    """An installer for MacOS systems.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, p):
        """Create a new MacOs(Installer) instance."""
        super(MacOs, self).__init__(p)
        self._features = Features("req_ios", "cmd_ios")

    # ------------------------------------------------------------------------

    def _search_package(self, package):
        """Returns True if package is already installed.

        :param package: (str) The system package to search.

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
            self.__fill_errors("Installation \"{name}\" failed.\nError : {error}"
                               .format(name=package, error=FileNotFoundError))
            return False

    # ------------------------------------------------------------------------

    def _install_package(self, package):
        """Install package.

        :param package: (str) The system package to install.
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
                    if self._search_package(package) is False:
                        self.__fill_errors("Package: \"{name}\"\nError: {error}".format(name=package, error=error))
                        return False

                elif "No available" in error:
                    self.__fill_errors("Package: \"{name}\"\nError: {error}".format(name=package, error=error))
                    return False
                else:
                    self.__fill_errors("Package: \"{name}\"\nError: {error}".format(name=package, error=error))
                    return False
        except FileNotFoundError:
            self.__fill_errors("Installation \"{name}\" failed.\nError: {error}"
                               .format(name=package, error=FileNotFoundError))
            return False

    # ------------------------------------------------------------------------

    def _version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (str) The system package to search.
        :param req_version: (str) The minimum version required.

        """
        try:
            req_version = str(req_version)
            package = str(package)
            command = "brew info " + package
            process = Process()
            process.run_popen(command)
            error = process.error()
            stdout = process.out()
            if self._need_update_package(stdout, req_version):
                return False
            else:
                return True
        except FileNotFoundError:
            self.__fill_errors("Installation \"{name}\" failed.\nError: {error}"
                               .format(name=package, error=FileNotFoundError))
            return False

    # ------------------------------------------------------------------------

    @staticmethod
    def _need_update_package(stdout_show, req_version):
        """Return True if the package need to be update.

        :param stdout_show: (str) The stdout of the command.
        :param req_version: (str) The minimum version required.

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

    # ------------------------------------------------------------------------

    def _update_package(self, package):
        """Update package.

        :param package: (str) The system package to update.
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
                    self.__fill_errors("Package: \"{name}\"\nError: {error}".format(name=package, error=error))
                else:
                    self.__fill_errors("Package: \"{name}\"\nError: {error}".format(name=package, error=error))
                return False
        except FileNotFoundError:
            self.__fill_errors("Installation \"{name}\" failed.\nError: {error}"
                               .format(name=package, error=FileNotFoundError))
            return False


