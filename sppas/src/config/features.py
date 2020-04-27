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

        src.config.features.py
    ~~~~~~~~~~~~~~~~

:author:       Florian Hocquet
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      the class Feature of SPPAS

"""

import os

try:
    import configparser as cp
except ImportError:
    import ConfigParser as cp

from sppas.src.config.support import sppasPathSettings
from sppas.src.config.feature import Feature


class Features:
    """Creation features.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

    """

    def __init__(self, req, cmdos):
        """Create a new Feature instance.

        """
        self.__req = req
        self.__cmdos = cmdos
        self.__cfg_exist = False
        self.__config_file = None
        self.__config_parser = cp.ConfigParser()
        self.__feature_file = self.set_features_file()
        self.__features_parser = cp.ConfigParser()
        self.__features = list()
        self.init_config()
        self.__features_parser = self.init_features()
        self.set_features()

    # ---------------------------------------------------------------------------

    def init_config(self):
        """Check if the config already exist or not.

        """
        paths = sppasPathSettings()
        config_file = os.path.join(paths.basedir, "config.ini")
        self.__config_file = config_file

        if os.path.exists(config_file) is False:
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

