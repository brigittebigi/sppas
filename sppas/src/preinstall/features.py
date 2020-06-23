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
from .feature import Feature, DepsFeature, LangFeature, AnnotFeature

# ---------------------------------------------------------------------------


class Features(object):
    """Manage the list of required external features of the software.

        :author:       Florian Hocquet, Brigitte Bigi
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, req="", cmdos=""):
        """Create a new Features instance.

        A Features instance is a container for a list of features.
        It parses a '.ini' file to get each feature config.

        :param req: (str)
        :param cmdos: (str)

        """
        self.__req = req
        self.__cmdos = cmdos
        self.__features = list()
        self.set_features()

    # ------------------------------------------------------------------------

    @staticmethod
    def get_features_filename():
        """Return the name of the file with the features descriptions."""
        return os.path.join(paths.etc, "features.ini")

    # ------------------------------------------------------------------------

    def get_ids(self):
        """Return the list of feature identifiers."""
        return [f.get_id() for f in self.__features]

    # ------------------------------------------------------------------------

    def feature_type(self, fid):
        """Return the feature type: deps, lang, annot.

        :param fid: (str) Identifier of a feature

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                return feat.get_type()

        logging.error("Unknown feature {}".format(fid))
        return None

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

        logging.error("Unknown feature {}".format(fid))
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

        logging.error("Unknown feature {}".format(fid))
        return False

    # ------------------------------------------------------------------------

    def brief(self, fid):
        """Return the brief description of the feature.

        :param fid: (str) Identifier of a feature

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                return feat.get_brief()

        logging.error("Unknown feature {}".format(fid))
        return None

    # ------------------------------------------------------------------------

    def description(self, fid):
        """Return the description of the feature

        :param fid: (str) Identifier of a feature

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                return feat.get_desc()

        logging.error("Unknown feature {}".format(fid))
        return None

    # ------------------------------------------------------------------------

    def packages(self, fid):
        """Return the dictionary of system dependencies of the feature.

        :param fid: (str) Identifier of a feature
        :return: (dict) key=package; value=version

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                if isinstance(feat, DepsFeature) is True:
                    return feat.get_packages()
                else:
                    logging.error("Feature {} is not a DepsFeature:"
                                  "No packages are defined.".format(fid))

        logging.error("Unknown feature {}".format(fid))
        return dict()

    # ------------------------------------------------------------------------

    def pypi(self, fid):
        """Return the dictionary of pip dependencies of the feature.

        :param fid: (str) Identifier of a feature
        :return: (dict) key=package; value=version

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                if isinstance(feat, DepsFeature) is True:
                    return feat.get_pypi()
                else:
                    logging.error("Feature {} is not a DepsFeature:"
                                  "No pypi are defined.".format(fid))

        logging.error("Unknown feature {}".format(fid))
        return dict()

    # ------------------------------------------------------------------------

    def cmd(self, fid):
        """Return the command to execute for the feature.

        :param fid: (str) Identifier of a feature
        :return: (str)

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                if isinstance(feat, DepsFeature) is True:
                    return feat.get_cmd()
                else:
                    logging.error("Feature {} is not a DepsFeature:"
                                  "No cmd is defined.".format(fid))

        logging.error("Unknown feature {}".format(fid))
        return str()

    # ------------------------------------------------------------------------

    def lang(self, fid):
        """Return the lang code of the linguistic resource to download.

        :param fid: (str) Identifier of a feature
        :return: (str)

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                if isinstance(feat, LangFeature) is True:
                    return feat.get_lang()
                else:
                    logging.error("Feature {} is not a LangFeature:"
                                  "No lang is defined.".format(fid))

        logging.error("Unknown feature {}".format(fid))
        return str()

    # ------------------------------------------------------------------------

    def annot(self, fid):
        """Return the name the annotation resource to download.

        :param fid: (str) Identifier of a feature
        :return: (str)

        """
        for feat in self.__features:
            if feat.get_id() == fid:
                if isinstance(feat, AnnotFeature) is True:
                    return feat.get_annot()
                else:
                    logging.error("Feature {} is not an AnnotFeature:"
                                  "No annot is defined.".format(fid))

        logging.error("Unknown feature {}".format(fid))
        return str()

    # ---------------------------------------------------------------------------

    def set_features(self):
        """Browses the features.ini file and instantiate a Feature().

        Only unix-based systems can have package requirements. If they don't,
        the corresponding req_ attribute is missing or empty or with "nil".

        A feature is not available for a system, if none of the corresponding "cmd_"
        and "req_" and the "pip" attributes are defined.

        """
        self.__features = list()
        features_parser = self.__init_features()

        for fid in (features_parser.sections()):
            # Type of the feature
            try:
                feature = self.__set_feature(fid, features_parser)
            except cp.NoOptionError:
                logging.error("Missing or wrong feature type for feature {}"
                              "".format(fid))
                continue

            # here we should verify if fid is not already in the list of features
            self.__features.append(feature)

            # Brief description of the feature
            try:
                desc = features_parser.get(fid, "brief")
                feature.set_brief(desc)
            except cp.NoOptionError:
                pass

            # Long description of the feature
            try:
                desc = features_parser.get(fid, "desc")
                feature.set_desc(desc)
            except cp.NoOptionError:
                pass

            # Feature is enabled or not
            try:
                e = features_parser.getboolean(fid, "enable")
                feature.set_enable(e)
            except cp.NoOptionError:
                pass

        # Disable the installation of the already installed features, but
        # they are still available: they can be updated if selected.
        ids = self.get_ids()
        for f in cfg.get_deps():
            if f in ids:
                self.enable(f, not cfg.dep_installed(f))
            else:
                logging.error("The config file contains an unknown "
                              "feature identifier {}".format(f))

    # ------------------------------------------------------------------------

    def __set_feature(self, fid, parser):
        feature = None
        try:
            ft = parser.get(fid, "type")
            if ft == "deps":
                feature = DepsFeature(fid)
                self.__fill_deps_feature(feature, parser)
            if ft == "lang":
                feature = LangFeature(fid)
                self.__fill_lang_feature(feature)
            if ft == "annot":
                feature = AnnotFeature(fid)
                self.__fill_annot_feature(feature)
        except cp.NoOptionError:
            pass

        if feature is not None:
            return feature
        raise cp.NoOptionError

    # ------------------------------------------------------------------------

    def __fill_deps_feature(self, feature, parser):
        fid = feature.get_id()
        # System package dependencies
        try:
            d = parser.get(fid, self.__req)
            if len(d) > 0 and d.lower() != "nil":
                depend_packages = self.__parse_depend(d)
                feature.set_packages(depend_packages)
        except cp.NoOptionError:
            pass

        # Pypi dependencies
        try:
            d = parser.get(fid, "pip")
            if len(d) > 0 and d.lower() != "nil":
                depend_pypi = self.__parse_depend(d)
                feature.set_pypi(depend_pypi)
        except cp.NoOptionError:
            pass

        # Command to be executed
        try:
            cmd = parser.get(fid, self.__cmdos)
            if len(cmd) > 0 and cmd != "none" and cmd != "nil":
                feature.set_cmd(cmd)
        except cp.NoOptionError:
            pass

        # Is available?
        if len(feature.get_cmd()) > 0 or len(feature.get_pypi()) > 0 or len(feature.get_packages()) > 0:
            feature.set_available(True)

    # ------------------------------------------------------------------------

    def __fill_lang_feature(self, feature):
        # the identifier of the feature is also the name of the zip file to
        # download and install
        fid = feature.get_id()
        feature.set_lang(fid)
        feature.set_available(True)

    # ------------------------------------------------------------------------

    def __fill_annot_feature(self, feature):
        # the identifier of the feature is also the name of the zip file to
        # download and install
        fid = feature.get_id()
        feature.set_annot(fid)
        feature.set_available(True)

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
