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

from sppas import error
from sppas.src.config.process import Process, search_cmd
from sppas.src.config import info
from .features import Features

# ---------------------------------------------------------------------------


def _(identifier):
    return info(identifier, "globals")


MESSAGES = {
    "beginning_feature": _(510),
    "available_false": _(520),
    "enable_false": _(530),
    "install_success": _(540),
    "install_failed": _(550),
    "install_finished": _(560),
    "does_not_exist": _(570),
}

# -----------------------------------------------------------------------


class InstallationError(OSError):
    """:ERROR 500:.

    Installation failed with error: {error}.

    """

    def __init__(self, error_msg):
        self.parameter = error(500) + \
                         (error(500, "globals")).format(error=error_msg)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class Installer(object):
    """Manage the installation of external required or optional features.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        It will browse the Features() to install, according to the OS of
        the computer. The installation is launched with:

        >>> Installer().install()

    """

    def __init__(self):
        """Create a new Installer instance. """
        self.__pbar = None
        self.__progression = 0
        self._features = Features(req="", cmdos="")

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def set_progress(self, progress):
        """Set the progress bar.

        :param progress: (ProcessProgressTerminal) The installation progress.

        """
        # TODO: we should test if instance if ok
        self.__pbar = progress

    # ------------------------------------------------------------------------

    def get_fids(self):
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
        """Process to the installation procedure."""
        errors = list()
        for fid in self._features.get_ids():
            self.__pheader(self.__message("beginning_feature", fid))

            if self._features.available(fid) is False:
                self.__pupdate(self.__get_set_progress(1), self.__message("available_false", fid))

            elif self._features.enable(fid) is False:
                self.__pupdate(self.__get_set_progress(1), self.__message("enable_false", fid))

            else:
                try:
                    self.__install_cmd(fid)
                    self.__install_packages(fid)
                    self.__install_pypis(fid)
                    self._features.enable(fid, True)
                    self.__pupdate(self.__eval_percent(fid), self.__message("install_success", fid))
                except InstallationError as e:
                    self._features.enable(fid, False)
                    self.__pupdate(self.__eval_percent(fid), self.__message("install_failed", fid))
                    errors.append(str(e))

        self._features.update_config()
        return errors

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    def __install_cmd(self, fid):
        """Execute a system command for a feature.

        :param fid: (str) Identifier of a feature
        :raises: InstallationError()

        """
        err = ""

        if self._features.cmd(fid) == "none":
            self._features.available(fid, False)

        elif self._features.cmd(fid) == "nil":
            self._features.enable(fid, False)

        else:
            if search_cmd(fid) is False:
                try:
                    process = Process()
                    process.run_popen(self._features.cmd(fid))
                    err = process.error()
                    stdout = process.out()
                    if len(stdout) > 3:
                        logging.info(stdout)
                except Exception as e:
                    raise InstallationError(str(e))

        if len(err) > 0:
            raise InstallationError(err)
        if self.__pbar:
            self.__pbar.update(self.__get_set_progress(self.__eval_percent(fid)), fid)

    # ------------------------------------------------------------------------

    def __install_packages(self, fid):
        """Manage installation of system packages.

        :param fid: (str) Identifier of a feature
        :raises: InstallationError()

        """
        for package, version in self._features.packages(fid).items():
            if package != "nil":
                if self._search_package(package) is False:
                    self._install_package(package)

                elif self._version_package(package, version) is False:
                    self._update_package(package)

                if self.__pbar:
                    self.__pbar.update(self.__get_set_progress(self.__eval_percent(fid)), MESSAGES["install_success"].format(name=package))

    # ------------------------------------------------------------------------

    def __install_pypis(self, fid):
        """Manage the installation of pip packages.

        :param fid: (str) Identifier of a feature
        :raises: InstallationError()

        """
        for package, version in self._features.pypi(fid).items():
            if package != "nil":
                if Installer.__search_pypi(package) is False:
                    Installer.__install_pypi(package)

                elif Installer.__version_pypi(package, version) is False:
                    Installer.__update_pypi(package)

                if self.__pbar:
                    self.__pbar.update(self.__get_set_progress(self.__eval_percent(fid)), package)

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

    def __pheader(self, text):
        if self.__pbar is not None:
            self.__get_set_progress(0)
            self.__pbar.set_header(text)
        logging.info("    * * * * *   {}   * * * * * ".format(text))

    def __pupdate(self, value, text):
        if self.__pbar is not None:
            self.__pbar.update(value, text)
        logging.info("  ==> {text} ({percent}%)".format(text=text, percent=value))

    def __message(self, mid, fid):
        (MESSAGES[mid]).format(name=self._features.description(fid))

    # ------------------------------------------------------------------------

    def __eval_percent(self, fid):
        """Estimate and return a percentage of progression.

        :param fid: (str) Identifier of a feature
        :return: (float)

        """
        nb_packages = float(len(self._features.packages(fid)))
        nb_pypi = float(len(self._features.pypi(fid)))
        return round((1. / (1. + nb_packages + nb_pypi)), 2)

    # ------------------------------------------------------------------------

    def __get_set_progress(self, value):
        """Return the progression, and it to the current value.

        :param value: (int) The progress value to add.
        :return: (float) The current value of the progress.

        """
        if value == 0:
            self.__progression = 0.
            return self.__progression

        self.__progression += value

        if self.__progression >= 0.99:
            self.__progression = 1.0

        return self.__progression

    # ------------------------------------------------------------------------

    @staticmethod
    def __search_pypi(package):
        """Return True if given Pypi package is already installed.

        :param package: (str) The pip package to search.

        """
        try:
            command = "pip3 show " + package
            process = Process()
            process.run_popen(command)
            err = process.error()
            stdout = process.out()
            stdout = stdout.replace("b''", "")

            # pip3 can either:
            #   - show information about the Pypi package,
            #   - show nothing, or
            #   - make an error with a message including 'not found'.
            if len(err) > 3 or len(stdout) == 0:
                return False
        except Exception as e:
            raise InstallationError(str(e))

        return True

    # ------------------------------------------------------------------------

    @staticmethod
    def __install_pypi(package):
        """Install a Python Pypi package.

        :param package: (str) The pip package to install
        :raises: InstallationError()

        """
        try:
            command = "pip3 install " + package + " --no-warn-script-location"
            process = Process()
            process.run_popen(command)
            err = process.error()
            stdout = process.out()
            if len(stdout) > 3:
                logging.info(stdout)
        except Exception as e:
            raise InstallationError(str(e))

        if len(err) > 0:
            raise InstallationError(err)

    # ------------------------------------------------------------------------

    @staticmethod
    def __version_pypi(package, req_version):
        """Returns True if package is up to date.

        :param package: (str) The pip package to search.
        :param req_version: (str) The minimum version required.

        """
        try:
            command = "pip3 show " + package
            process = Process()
            process.run_popen(command)
            err = process.error()
            if len(err) > 0:
                return False
            stdout = process.out()
            return not Installer.__need_update_pypi(stdout, req_version)

        except Exception:
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

    @staticmethod
    def __update_pypi(package):
        """Update package.

        :param package: (str) The pip package to update.
        :raises: InstallationError()

        """
        try:
            command = "pip3 install -U " + package
            process = Process()
            process.run_popen(command)
            err = process.error()
        except Exception as e:
            raise InstallationError(str(e))

        if len(err) > 0:
            raise InstallationError(err)

# ----------------------------------------------------------------------------


class DebInstaller(Installer):
    """An installer for Debian-based package manager systems.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        This DebInstaller(Installer) is made for the Debians distributions of Linux,
        like Debian, Ubuntu or Mint.

    """

    def __init__(self):
        """Create a new DebInstaller instance."""
        super(DebInstaller, self).__init__()
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


class RpmInstaller(Installer):
    """An installer for RPM-based package manager system.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        This RPM is made for the linux distributions like RedHat, or Suse.

    """

    def __init__(self):
        """Create a new RpmInstaller(Installer) instance."""
        super(RpmInstaller, self).__init__()
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


class DnfInstaller(Installer):
    """An installer for DNF-based package manager systems.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This DNF is made for linux distributions like Fedora.

    """

    def __init__(self):
        """Create a new DnfInstaller(Installer) instance."""
        super(DnfInstaller, self).__init__()
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


class WindowsInstaller(Installer):
    """An installer for Microsoft WindowsInstaller system.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        This WindowsInstaller installer was tested with WindowsInstaller 10.

    """

    def __init__(self):
        """Create a new WindowsInstaller instance."""
        super(WindowsInstaller, self).__init__()
        self._features = Features("req_win", "cmd_win")

    # ------------------------------------------------------------------------

    def _version_package(self, package, req_version):
        """Return True if the package is up to date.

        :param package: (str) The system package to search.
        :param req_version: (str) The minimum version required.

        """
        return True

# ----------------------------------------------------------------------------


class MacOsInstaller(Installer):
    """An installer for MacOS systems.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new MacOsInstaller(Installer) instance."""
        super(MacOsInstaller, self).__init__()
        self._features = Features("req_ios", "cmd_ios")

    # ------------------------------------------------------------------------

    def _search_package(self, package):
        """Returns True if package is already installed.

        :param package: (str) The system package to search.
        :return: (bool)

        """
        try:
            command = "brew list " + package
            process = Process()
            process.run_popen(command)
            err = process.error()
            return len(err) == 0

        except Exception as e:
            raise InstallationError(str(e))

    # ------------------------------------------------------------------------

    def _install_package(self, package):
        """Install package.

        :param package: (str) The system package to install.
        :raise: InstallationError() if an error occurred

        """
        try:
            package = str(package)
            command = "brew install " + package
            process = Process()
            process.run_popen(command)
            err = process.error()
            stdout = process.out()
            if len(stdout) > 3:
                logging.info(stdout)

        except Exception as e:
            raise InstallationError(str(e))

        if len(err) > 0:
            raise InstallationError(err)

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
            err = process.error()
        except Exception as e:
            raise InstallationError(str(e))

        if len(err) > 0:
            raise InstallationError(err)
        stdout = process.out()
        return not self._need_update_package(stdout, req_version)

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
            raise ValueError("Your comparator : " +
                             comparator +
                             " does not refer to a valid comparator")

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
            err = process.error()
            stdout = process.out()
            if len(stdout) > 3:
                logging.info(stdout)
        except Exception as e:
            raise InstallationError(str(e))

        if len(err) > 0:
            raise InstallationError(err)
