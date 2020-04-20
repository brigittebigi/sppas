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

        config.class_installer.py
    ~~~~~~~~~~~~~~~~

:author:       Florian Hocquet
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      a script to use workspaces from terminal

"""

import sys
import os

from sppas.src.config.features import Feature
from sppas import paths

try:
    import configparser as cp
except ImportError:
    import ConfigParser as cp


# ---------------------------------------------------------------------------


class Installer:

    def __init__(self):
        self.__features = list()
        self.__config_file = self.init_features("features.ini")
        self.set_features()

    # ---------------------------------------------------------------------------

    @staticmethod
    def init_features(filename):
        global config
        if filename.endswith('.ini'):
            config = os.path.join(paths.etc, filename)

            if os.path.exists(config) is False:
                raise IOError('Installation error: the file to configure the '
                              'list of features does not exist.')

        config_file = cp.ConfigParser()
        try:
            config_file.read(config)
        except cp.MissingSectionHeaderError:
            print("Votre fichier ne contient pas de sections")
        return config_file

    # ---------------------------------------------------------------------------

    def set_features(self):
        list_features = (self.__config_file.sections())
        for f in list_features:
            feature = Feature()

            enable = self.__config_file.getboolean(f, "enable")
            feature.set_enable(enable)

            available = self.__config_file.getboolean(f, "available")
            feature.set_enable(available)

            feature.set_id(f)

            d = self.__config_file.get(f, "req_win")
            if d == "nil":
                feature.set_dict_packages({"nil": "1"})
            elif d == "none":
                feature.set_dict_packages({"none": "0"})
            else:
                dependencies = d.split(" ")
                depend_packages = dict()
                for line in dependencies:
                    tab = line.split("=", maxsplit=1)
                    depend_packages[tab[0]] = tab[1]
                feature.set_dict_packages(depend_packages)

            d = self.__config_file.get(f, "req_pip")
            if d == "nil":
                feature.set_dict_pypi({"nil": "1"})
            elif d == "none":
                feature.set_dict_pypi({"none": "0"})
            else:
                dependencies = d.split(" ")
                depend_pypi = dict()
                for line in dependencies:
                    tab = line.split("=", maxsplit=1)
                    depend_pypi[tab[0]] = tab[1]
                feature.set_dict_pypi(depend_pypi)

            self.__features.append(feature)

    # ---------------------------------------------------------------------------

    def show_features(self):
        for f in self.__features:
            print(f.get_enable(), "\n",
                  f.get_available(), "\n",
                  f.get_id(), "\n",
                  f.get_dict_packages(), "\n",
                  f.get_dict_pypi(), "\n",)

    # ---------------------------------------------------------------------------

    def install_packages(self, packages_dictonnary):
        print(packages_dictonnary)

    # ---------------------------------------------------------------------------

    def install_pypi(self, pypi_dictonnary):
        print(pypi_dictonnary)

    # ---------------------------------------------------------------------------


class Deb(Installer):
    def __init__(self):
        print("Deb")

    # ---------------------------------------------------------------------------

    def install_packages(self, packages_dictonnary):
        print(packages_dictonnary)

    # ---------------------------------------------------------------------------

    def install_pypi(self, pypi_dictonnary):
        print(pypi_dictonnary)


class Rpm(Installer):
    def __init__(self):
        print("Rpm")

    # ---------------------------------------------------------------------------

    def install_packages(self, packages_dictonnary):
        print(packages_dictonnary)

    # ---------------------------------------------------------------------------

    def install_pypi(self, pypi_dictonnary):
        print(pypi_dictonnary)


class Windows(Installer):
    def __init__(self):
        print("Windows")

    # ---------------------------------------------------------------------------

    def install_packages(self, packages_dictonnary):
        print(packages_dictonnary)

    # ---------------------------------------------------------------------------

    def install_pypi(self, pypi_dictonnary):
        print(pypi_dictonnary)


class CygWin(Installer):
    def __init__(self):
        print("CygWin")

    # ---------------------------------------------------------------------------

    def install_packages(self, packages_dictonnary):
        print(packages_dictonnary)

    # ---------------------------------------------------------------------------

    def install_pypi(self, pypi_dictonnary):
        print(pypi_dictonnary)


class MacOs(Installer):
    def __init__(self):
        print("MacOs")

    # ---------------------------------------------------------------------------

    def install_packages(self, packages_dictonnary):
        print(packages_dictonnary)

    # ---------------------------------------------------------------------------

    def install_pypi(self, pypi_dictonnary):
        print(pypi_dictonnary)
