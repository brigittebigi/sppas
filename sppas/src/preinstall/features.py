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

    src.preinstall.features.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import logging

try:
    import configparser as cp
except ImportError:
    import ConfigParser as cp

from sppas.src.config import paths
from sppas.src.config import cfg
from .feature import Feature

# ---------------------------------------------------------------------------


class Features(object):
    """Manage the list of required external features of the software.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, req="", cmdos=""):
        """Create a new Feature instance.

            A Features instance is a container for a list of features.
            It parses a '.ini' file to get each feature config.

        :param req: (str)
        :param cmdos: (str)

        """
        self.__req = req
        self.__cmdos = cmdos
        self.__features = list()
        self.set_features()
        self.update_features()

    # ------------------------------------------------------------------------

    @staticmethod
    def get_features_filename():
        """Return the name of the file with the features descriptions."""
        return os.path.join(paths.etc, "features.ini")

    # ------------------------------------------------------------------------

    def update_config(self):
        """Update the active configuration instance with the features."""
        for f in self.__features:
            cfg.set_dep(f.get_id(), f.get_enable())
        # The running application will do it (if desired): cfg.save()

    # ------------------------------------------------------------------------

    def update_features(self):
        """Update the features with the config file."""
        ids = self.get_ids()
        for f in cfg.get_deps():
            if f in ids:
                self.enable(f, cfg.dep_enabled(f))
            else:
                logging.error("The config file contains an unknown "
                              "feature identifier {}".format(f))

    # ------------------------------------------------------------------------

    def get_ids(self):
        """Return the list of feature identifiers."""
        return [f.get_id() for f in self.__features]

    # ------------------------------------------------------------------------

    def enable(self, fid, value=None):
        """Return True if the feature is enabled and/or set it.

        :param fid: (str) Identifier of a feature
        :param value: (bool or None) Enable of disable the feature.

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                if value is None:
                    return feat.get_enable()
                return feat.set_enable(value)

        return False

    # ------------------------------------------------------------------------

    def available(self, fid, value=None):
        """Return True if the feature is available and/or set it.

        :param fid: (str) Identifier of a feature
        :param value: (bool or None) Make the feature available or not.

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                if value is None:
                    return feat.get_available()
                return feat.set_available(value)

        return False

    # ------------------------------------------------------------------------

    def description(self, fid):
        """Return the description of the feature

        :param fid: (str) Identifier of a feature

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                return feat.get_desc()

        return None

    # ------------------------------------------------------------------------

    def packages(self, fid):
        """Return the dictionary of system dependencies of the feature.

        :param fid: (str) Identifier of a feature

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                return feat.get_packages()

        return dict()

    # ------------------------------------------------------------------------

    def pypi(self, fid):
        """Return the dictionary of pip dependencies of the feature.

        :param fid: (str) Identifier of a feature

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                return feat.get_pypi()
        return dict()

    # ------------------------------------------------------------------------

    def cmd(self, fid):
        """Return the command to execute for the feature.

        :param fid: (str) Identifier of a feature

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                return feat.get_cmd()
        return str()

    # ---------------------------------------------------------------------------

    def set_features(self):
        """Browses the features.ini file and instantiate a Feature()."""
        self.__features = list()
        features_parser = self.__init_features()

        for fid in (features_parser.sections()):
            feature = Feature(fid)
            self.__features.append(feature)

            # Description of the feature
            desc = features_parser.get(fid, "desc")
            feature.set_desc(desc)

            # Feature is enabled or not
            feature.set_enable(features_parser.getboolean(fid, "enable"))

            # Package dependencies
            try:
                d = features_parser.get(fid, self.__req)
                if d == "nil" or d == "":
                    feature.set_packages({"nil": "1"})
                    feature.set_available(True)
                else:
                    feature.set_available(True)
                    depend_packages = self.__parse_depend(d)
                    feature.set_packages(depend_packages)
            except cp.NoOptionError:
                logging.debug("Feature {} has no defined section name '{}'."
                              "".format(feature.get_id(), self.__req))

            # Pypi dependencies
            try:
                d = features_parser.get(fid, "req_pip")
                if d == "nil" or d == "":
                    feature.set_pypi({"nil": "1"})
                else:
                    depend_pypi = self.__parse_depend(d)
                    feature.set_pypi(depend_pypi)
            except cp.NoOptionError:
                logging.debug("Feature {} has no defined section name '{}'."
                              "".format(feature.get_id(), self.__req))

            # Command to be executed
            try:
                cmd = features_parser.get(fid, self.__cmdos)
                if cmd == "none":
                    feature.set_available(False)
                feature.set_cmd(cmd)
            except cp.NoOptionError:
                logging.debug("Feature {} has no defined section name '{}'."
                              "".format(feature.get_id(), self.__req))

    # ------------------------------------------------------------------------
    # Private: Internal use only.
    # ------------------------------------------------------------------------

    def __init_features(self):
        """Return a parsed version of the features.ini file."""
        cfg = self.get_features_filename()
        if cfg is None:
            raise IOError("Installation error: the file {filename} to "
                          "configure the software is missing."
                          .format(filename=cfg))

        features_parser = cp.ConfigParser()
        try:
            features_parser.read(self.get_features_filename())
        except cp.MissingSectionHeaderError:
            raise IOError("Malformed features configuration file {}: "
                          "missing section header.".format(cfg))

        return features_parser

    # ---------------------------------------------------------------------------

    @staticmethod
    def __parse_depend(string_require):
        """Create a dictionary from the string given as an argument.

        :param string_require: (string) The value of one
        of the req_*** key in one of the section of feature.ini.
        :return: (dict)

        """
        string_require = str(string_require)
        dependencies = string_require.split(" ")
        depend = dict()
        for line in dependencies:
            tab = line.split(":")
            depend[tab[0]] = tab[1]
        return depend

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __str__(self):
        """Print each Feature of the list. """
        for f in self.__features:
            print(f.__str__())

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    def __len__(self):
        """Return the number of features."""
        return len(self.__features)

    def __contains__(self, value):
        """Value can be either a Feature or its identifier."""
        if isinstance(value, Feature):
            return value in self.__features
        else:
            for f in self.__features:
                if f.get_id() == value:
                    return True
        return False
