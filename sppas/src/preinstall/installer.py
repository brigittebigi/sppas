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

    Compatible only with Python 3+.

"""

import logging
import shutil
import shlex
import subprocess
import os
import urllib.request
import zipfile

from sppas.src.config import cfg
from sppas.src.config import info
from sppas.src.config import paths
from sppas.src.exceptions.exc import sppasInstallationError
from sppas.src.utils.makeunicode import u

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


class ProcessRunner(object):
    """Convenient class to execute a subprocess.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A Process is a wrapper of subprocess.run command.
    After 30 sec. of waiting, it will stops and raise TimoutExpired.
    
    Launch a command:
    >>> p = ProcessRunner()
    >>> p.run("ls -l")

    Return stdout of a command:
    >>> p.out()

    Return stderr of a command:
    >>> p.error()
    
    Return the status of the command:
    >>> p.status()

    """

    def __init__(self):
        """Create a new Process instance."""
        self.__process = None  # subprocess.CompletedProcess()

    # ------------------------------------------------------------------------

    def run(self, command):
        """Execute command with subprocess.run.

        :param command: (str) The command you want to execute

        """
        logging.info("Process command: {}".format(command))
        command = command.strip()
        command_args = shlex.split(command)
        self.__process = subprocess.run(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            cwd=None,
            timeout=120,   # will raise TimeoutExpired() after 120 seconds
            check=False,
            encoding=None,
            errors=None,
            # text=None,   # does not work with python 3.6
            env=None,
            universal_newlines=True)

    # ------------------------------------------------------------------------

    def out(self):
        """Return the stdout of the process.

        :return: (str) output message

        """
        if self.__process is None:
            return ""
        return self.__process.stdout

    # ------------------------------------------------------------------------

    def error(self):
        """Return the stderr of the process.

        :return: (str) error message

        """
        if self.__process is None:
            return ""
        return self.__process.stderr

    # ------------------------------------------------------------------------

    def status(self):
        """Return value of the process."""
        if self.__process is None:
            return 0
        return self.__process.returncode

# -----------------------------------------------------------------------


class Installer(object):
    """Manage the installation of external required or optional features.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        It will browse the Features() to install, according to the OS of
        the computer. Must be sub-classed to create the appropriate Features().
        Then, the installation is launched with:

        >>> class SubInstaller(Installer):
        >>>     def __init__(self):
        >>>         super(SubInstaller, self).__init__()
        >>>         self._features = Features(req="", cmdos="")
        >>> SubInstaller().install()

    """

    def __init__(self):
        """Create a new Installer instance. """
        self.__pbar = None
        self.__pvalue = 0
        self._features = None

        self.__python = self.__search_python_cmd()
        logging.info("... the python command used by the installer system is '{}'"
                     "".format(self.__python))

    # ------------------------------------------------------------------------

    def __search_python_cmd(self):
        """Search for a valid python command. Raise SystemError if not found."""
        logging.info("Search for a 'python' command that this installer can launch...")
        process = ProcessRunner()

        command = "python -c 'import sys; print(sys.version_info.major)' "
        try:
            process.run(command)
            out = process.out().replace("b'", "")
            out = out.replace("'", "")
            if len(out) == 1:
                pyversion = int(out)
                if pyversion == 3:
                    return "python"
        except:
            pass

        command = "python3 -c 'import sys; print(sys.version_info.major)' "
        try:
            process.run(command)
            out = process.out().strip()
            out = out.replace("b'", "")
            out = out.replace("'", "")
            if len(out) == 1:
                pyversion = int(out)
                if pyversion == 3:
                    return "python3"
        except:
            pass

        raise SystemError("No valid python command can be invoked by the installer system.")

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

    def get_fids(self, feat_type=None):
        """Return the list of feature identifiers.

        :param feat_type: (str) Only return features of the given type.
        :returns: (list)

        """
        if feat_type is None:
            return self._features.get_ids()

        f = list()
        for fid in self._features.get_ids():
            if self.feature_type(fid) == feat_type:
                f.append(fid)
        return f

    # ------------------------------------------------------------------------

    def feature_type(self, fid):
        """Return the feature type: deps, lang, annot.

        :param fid: (str) Identifier of a feature

        """
        ft = self._features.feature_type(fid)
        return ft

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
        """Return the long description of the feature.

        :param fid: (str) Identifier of a feature
        :return: (str)

        """
        return self._features.description(fid)

    # ------------------------------------------------------------------------

    def brief(self, fid):
        """Return the brief description of the feature.

        :param fid: (str) Identifier of a feature
        :return: (str)

        """
        return self._features.brief(fid)

    # ------------------------------------------------------------------------

    def update_pip(self):
        logging.info("Update pip, the package installer for Python:")
        try:
            process = ProcessRunner()
            process.run(self.__python + " -m pip install --upgrade pip")
        except Exception as e:
            raise sppasInstallationError(str(e))

    # ------------------------------------------------------------------------

    def install(self, feat_type=None):
        """Process the installation.

        :param feat_type: (str) Install only features of the given type. None to install all.
        :return: (list) Error messages.

        """
        errors = list()
        for fid in self._features.get_ids(feat_type):
            self.__pheader(self.__message("beginning_feature", fid))

            if self._features.available(fid) is False:
                self.__pmessage(self.__message("available_false", fid))

            elif self._features.enable(fid) is False:
                # force to add a package dependency into the .app~file.
                # even if not enabled. it'll help manual edit of the file.
                if self._features.feature_type(fid) == "deps":
                    if cfg.feature_installed(fid) is False:
                        cfg.set_feature(fid, False)
                self.__pmessage(self.__message("enable_false", fid))

            else:
                self.__pmessage("")
                try:
                    self.__install_feature(fid)

                except sppasInstallationError as e:
                    self._features.enable(fid, False)
                    self.__pmessage(self.__message("install_failed", fid))
                    if self._features.feature_type(fid) == "deps":
                        cfg.set_feature(fid, False)
                    errors.append(str(e))
                    logging.error(str(e))

                except NotImplementedError:
                    self._features.enable(fid, False)
                    self.__pmessage(self.__message("install_failed", fid))
                    msg = "Installation of feature {} is not implemented yet " \
                          "for this os.".format(fid)
                    errors.append(msg)
                    logging.error(msg)

                else:
                    self._features.enable(fid, True)
                    cfg.set_feature(fid, True)
                    self.__pmessage(self.__message("install_success", fid))

        cfg.save()
        return errors

    # ------------------------------------------------------------------------
    # Private methods to install
    # ------------------------------------------------------------------------

    @staticmethod
    def test_command(command):
        command = command.strip()
        command_args = shlex.split(command)
        if len(command_args) == 0:
            return True

        if shutil.which(command_args[0]):
            return False
        return True

    # ------------------------------------------------------------------------

    def __install_feature(self, fid):
        """Install the given feature depending on its type."""
        ft = self._features.feature_type(fid)
        if ft == "deps":
            if len(self._features.cmd(fid)) > 0:
                self.__install_cmd(fid)
            if len(self._features.packages(fid)) > 0:
                self.__install_packages(fid)
            if len(self._features.pypi(fid)) > 0:
                self.__install_pypis(fid)
        elif ft == "lang":
            self.__install_lang(fid)
        elif ft == "annot":
            self.__install_annot(fid)
        else:
            raise sppasInstallationError("Unknown feature type {}."
                                         "".format(fid))

    # ------------------------------------------------------------------------

    def __install_lang(self, fid):
        """Download, unzip and install resources for a given language.

        :param fid: (str) Identifier of a feature
        :raises: sppasInstallationError

        """
        self.__pmessage("Download, unzip and install linguistic resources for {} language".format(fid))
        zip_path = self._features.lang(fid) + ".zip"
        url = paths.urlresources
        if url.endswith("/") is False:
            url += "/"
        url += "lang/"
        Installer.install_resource(url, zip_path)
        self.__pupdate(fid, MESSAGES["install_success"].format(name=fid))

    # ------------------------------------------------------------------------

    def __install_annot(self, fid):
        """Download, unzip and install resources for a given annotation.

        :param fid: (str) Identifier of a feature
        :raises: sppasInstallationError

        """
        self.__pmessage("Download, unzip and install resources for {} annotation".format(fid))
        zip_path = self._features.annot(fid) + ".zip"
        url = paths.urlresources
        if url.endswith("/") is False:
            url += "/"
        url += "annot/"
        Installer.install_resource(url, zip_path)
        self.__pupdate(fid, MESSAGES["install_success"].format(name=fid))

    # ------------------------------------------------------------------------

    @staticmethod
    def install_resource(web_url, zip_path):
        """Install the given zip file in the resources of SPPAS.

        :param web_url: (str) URL of the directory
        :param zip_path: (str) Zip filename to download and install

        """
        err = ""
        url = web_url + zip_path
        tmp = os.path.join(paths.resources, zip_path)

        # Attempt to open the url and manage the errors if any
        try:
            req = urllib.request.Request(url)
        except ValueError as e:
            err = str(e)
        else:
            try:
                response = urllib.request.urlopen(req)
            except urllib.error.URLError as e:
                if hasattr(e, 'reason'):
                    err = "Failed to establish a connection to the url {}: {}" \
                          "".format(url, e.reason)
                elif hasattr(e, 'code'):
                    err = "The web server couldn't fulfill the request for url {}. " \
                          "Error code: {}".format(url, e.code)
                else:
                    err = "Unknown connection error."
            except Exception as e:
                err = str(e)

            else:
                # Everything is fine. Download the file.
                with open(tmp, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)

                # Unzip the downloaded resource file
                try:
                    z = zipfile.ZipFile(tmp)
                    z.extractall(os.path.join(paths.resources))
                    z.close()
                except zipfile.error as e:
                    err = str(e)

        if os.path.exists(tmp) is True:
            os.remove(tmp)
        if len(err) > 0:
            raise sppasInstallationError(err)

    # ------------------------------------------------------------------------

    def __install_cmd(self, fid):
        """Execute a system command for a feature.

        :param fid: (str) Identifier of a feature
        :raises: sppasInstallationError

        """
        err = ""
        command = self._features.cmd(fid)
        cmd_exists = Installer.test_command(command)
        if cmd_exists is False:
            try:
                process = ProcessRunner()
                process.run(self._features.cmd(fid))
                err = process.error()
                stdout = process.out()
                logging.info("Return code: {}".format(process.status()))
                if len(stdout) > 3:
                    logging.info(stdout)
            except Exception as e:
                raise sppasInstallationError(str(e))

        if len(err) > 3:
            raise sppasInstallationError(err)

        self.__pupdate(fid, MESSAGES["install_success"].format(name=fid))

    # ------------------------------------------------------------------------

    def __install_packages(self, fid):
        """Manage installation of system packages.

        :param fid: (str) Identifier of a feature
        :raises: sppasInstallationError

        """
        for package, version in self._features.packages(fid).items():
            if self._search_package(package) is False:
                self._install_package(package)

            elif self._version_package(package, version) is False:
                self._update_package(package, version)

            self.__pupdate(fid, MESSAGES["install_success"].format(name=package))

    # ------------------------------------------------------------------------

    def __install_pypis(self, fid):
        """Manage the installation of pip packages.

        :param fid: (str) Identifier of a feature
        :raises: sppasInstallationError

        """
        for package, version in self._features.pypi(fid).items():
            if self.__search_pypi(package) is False:
                self.__install_pypi(package)
            elif self.__version_pypi(package, version) is False:
                self.__update_pypi(package)

            self.__pupdate(fid, MESSAGES["install_success"].format(name=package))

    # ------------------------------------------------------------------------
    # Management of package dependencies. OS dependent: must be overridden.
    # ------------------------------------------------------------------------

    def _search_package(self, package):
        """To be overridden. Return True if package is already installed.

        :param package: (str) The system package to search.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _install_package(self, package):
        """To be overridden. Install package.

        :param package: (str) The system package to install.
        :returns: False or None

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _version_package(self, package, req_version):
        """To be overridden. Return True if the package is up to date.

        :param package: (str) The system package to search.
        :param req_version: (str) The minimum version required.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    @staticmethod
    def _need_update_package(stdout_show, req_version):
        """To be overridden. Return True if the package need to be update.

        :param stdout_show: (str) The stdout of the command.
        :param req_version: (str) The minimum version required.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _update_package(self, package, req_version):
        """To be overridden. Update package.

        :param package: (str) The system package to update.
        :returns: False or None

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------
    # Private, for internal use only. Not needed by any sub-class.
    # ------------------------------------------------------------------------

    def __pheader(self, text):
        if self.__pbar is not None:
            self.__pvalue = 0
            self.__pbar.set_header(text)
        logging.info("    * * * * *   {}   * * * * * ".format(text))

    def __pmessage(self, text):
        if self.__pbar is not None:
            self.__pbar.set_text(text)
        logging.info("  ==> {text}".format(text=text))

    def __pupdate(self, fid, text):
        self.__pvalue += self.__eval_step(fid)
        if self.__pbar is not None:
            self.__pbar.update(self.__pvalue, text)
        if self.__pvalue > 90:
            self.__pvalue = 100
        logging.info("  ==> {}".format(text))
        # Makes GUI crashing: logging.info("({}%)".format(text, self.__pvalue))

    def __message(self, mid, fid):
        if mid in MESSAGES:
            return MESSAGES[mid].format(name=fid)
        else:
            return mid

    # ------------------------------------------------------------------------

    def __eval_step(self, fid):
        """Return the percentage of 1 step in progression for a given feature.

        :param fid: (str) Identifier of a feature
        :return: (float)

        """
        nb_total = 0
        ft = self._features.feature_type(fid)
        if ft == "deps":
            nb_cmd = 0
            if len(self._features.cmd(fid)) > 0:
                nb_cmd = 1
            nb_packages = len(self._features.packages(fid))
            nb_pypi = len(self._features.pypi(fid))
            nb_total = nb_cmd + nb_packages + nb_pypi
        elif ft == "annot":
            if len(self._features.annot(fid)) > 0:
                nb_total = 1
        elif ft == "lang":
            if len(self._features.lang(fid)) > 0:
                nb_total = 1

        if nb_total > 0:
            return int(round((1. / float(nb_total)), 2) * 100.)
        return 0

    # ------------------------------------------------------------------------

    def __search_pypi(self, package):
        """Return True if given Pypi package is already installed.

        :param package: (str) The pip package to search.

        """
        try:
            command = self.__python + " -m pip show " + package
            process = ProcessRunner()
            process.run(command)
            logging.info("Return code: {}".format(process.status()))
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
            raise sppasInstallationError(str(e))

        return True

    # ------------------------------------------------------------------------

    def __install_pypi(self, package):
        """Install a Python Pypi package.

        :param package: (str) The pip package to install
        :raises: sppasInstallationError

        """
        err = ""
        try:
            logging.info("Try to install {:s} for all users.".format(package))
            command = self.__python + " -m pip install " + package + " --no-warn-script-location"
            process = ProcessRunner()
            process.run(command)
            logging.info("Return code: {}".format(process.status()))
            err = process.error()
            stdout = process.out()

            if len(stdout) > 3:
                logging.info(stdout)

        except Exception as e:
            if len(err) > 3:
                logging.error(err)
            logging.error(str(e))
            logging.info("So... Try to install {:s} only for the current user.".format(package))
            command = self.__python + " -m pip install " + package + " --user --no-warn-script-location"
            process = ProcessRunner()
            process.run(command)
            logging.info("Return code: {}".format(process.status()))
            err = process.error()
            stdout = process.out()

            if len(stdout) > 3:
                logging.info(stdout)

        if len(err) > 3:
            raise sppasInstallationError(err)

    # ------------------------------------------------------------------------

    def __version_pypi(self, package, req_version):
        """Returns True if package is up to date.

        :param package: (str) The pip package to search.
        :param req_version: (str) The minimum version required.

        """
        try:
            command = self.__python + " -m pip show " + package
            process = ProcessRunner()
            process.run(command)
            logging.info("Return code: {}".format(process.status()))
            err = process.error()
            if len(err) > 3:
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
        version = stdout_show.split("\\r\\n")[1].split(":")[1].replace(" ", "")
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
        :raises: sppasInstallationError

        """
        try:
            # Deprecated:
            # command = "pip3 install -U " + package
            command = self.__python + " -m pip install -U " + package + " --no-warn-script-location"
            process = ProcessRunner()
            process.run(command)
            logging.info("Return code: {}".format(process.status()))
        except Exception as e:
            raise sppasInstallationError(str(e))

        err = u(process.error().strip())
        stdout = u(process.out())
        if len(stdout) > 3:
            logging.info(stdout)
        if len(err) > 3:
            raise sppasInstallationError(err)

# ----------------------------------------------------------------------------


class DebianInstaller(Installer):
    """An installer for Debian-based package manager systems.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        This DebianInstaller(Installer) is made for the apt package installer,
        like Debian, Ubuntu or Mint.

    """

    def __init__(self):
        """Create a new DebianInstaller instance."""
        super(DebianInstaller, self).__init__()
        self._features = Features(req="req_deb", cmdos="cmd_deb")

    # -----------------------------------------------------------------------

    def _search_package(self, package):
        """Returns True if package is already installed.

        :param package: (str) The system package to search.

        """
        try:
            command = "dpkg -s " + package
            process = ProcessRunner()
            process.run(command)
        except Exception as e:
            raise sppasInstallationError(str(e))

        err = process.error()
        if len(err) > 3:
            return False

        return True

    # -----------------------------------------------------------------------

    def _install_package(self, package):
        """Install the given package.

        :param package: (str) The system package to install.
        :returns: False or None

        """
        try:
            # -y option is to answer yes to confirmation questions
            command = "apt install " + package + " -y"
            process = ProcessRunner()
            process.run(command)
        except Exception as e:
            raise sppasInstallationError(str(e))

        stdout = process.out()
        if len(stdout) > 3:
            logging.info(stdout)

        err = process.error()
        if len(err) > 3 and "WARNING" not in err:
            raise sppasInstallationError(err)

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

    def _update_package(self, package, req_version):
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

    def _update_package(self, package, req_version):
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
        raise NotImplementedError

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

    def _update_package(self, package, req_version):
        """Update package.

        :param package: (str) The system package to update.
        :returns: False or None

        """
        raise NotImplementedError

# ---------------------------------------------------------------------------


class WindowsInstaller(Installer):
    """An installer for Microsoft Windows system.

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
            package = str(package)
            command = "brew list " + package
            process = ProcessRunner()
            process.run(command)
            if len(process.out()) > 3:
                return True
            return False
        except Exception as e:
            raise sppasInstallationError(str(e))

    # ------------------------------------------------------------------------

    def _install_package(self, package):
        """Install package.

        :param package: (str) The system package to install.
        :raises: sppasInstallationError

        """
        try:
            package = str(package)
            command = "brew install " + package
            process = ProcessRunner()
            process.run(command)
            err = process.error()
            stdout = process.out()
            if len(stdout) > 3:
                logging.info(stdout)

        except Exception as e:
            raise sppasInstallationError(str(e))

        if len(err) > 3:
            if "Warning: You are using macOS" in err:
                if self._search_package(package) is False:
                    raise sppasInstallationError(err)
            else:
                raise sppasInstallationError(err)

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
            process = ProcessRunner()
            process.run(command)
            err = process.error()
        except Exception as e:
            raise sppasInstallationError(str(e))

        if len(err) > 3:
            raise sppasInstallationError(err)
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
            return v < version

        raise ValueError("The comparator: " + comparator +
                         " does not refer to a valid comparator")

    # ------------------------------------------------------------------------

    def _update_package(self, package, req_version):
        """Update package.

        :param package: (str) The system package to update.
        :returns: False or None

        """
        try:
            package = str(package)
            command = "brew upgrade " + package
            process = ProcessRunner()
            process.run(command)
            err = process.error()
            stdout = process.out()
            if len(stdout) > 3:
                logging.info(stdout)
        except Exception as e:
            raise sppasInstallationError(str(e))

        if len(err) > 3:
            if "Warning: You are using macOS" or "already installed" in err:
                if self._version_package(package, req_version) is False:
                    raise sppasInstallationError(err)
            else:
                raise sppasInstallationError(err)
