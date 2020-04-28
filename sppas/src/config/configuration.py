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

        src.config.configuration.py
    ~~~~~~~~~~~~~~~~

:author:       Florian Hocquet
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2020  Brigitte Bigi
:summary:      the class Feature of SPPAS

"""


class Configuration:
    """Creation features.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

    """

    def __init__(self):
        """Create a new Configuration instance.

        """
        # An identifier to represent the config params.
        self.__features_enable = dict()

    # ---------------------------------------------------------------------------

    def get_features_enable(self):
        """Return the packages_dictionary, of the required system packages, of the instantiate Feature.

        """
        return self.__features_enable

    # ---------------------------------------------------------------------------

    def add_feature(self, key, value):
        """add a feature in the private dictionary __features_enable.

        :param key: (str()) The key
        :param value: (str()) The value

        """
        self.__features_enable[key] = value

    # ---------------------------------------------------------------------------

    def modify_feature(self, key, value):
        """add a feature in the private dictionary __features_enable.

        :param key: (str()) The key
        :param value: (str()) The value

        """
        self.__features_enable[key] = value

    # ---------------------------------------------------------------------------

