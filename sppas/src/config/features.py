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
:summary:      a script to use workspaces from terminal

"""

import os
import sys

# ---------------------------------------------------------------------------


class Feature:
    """Creation features.

        :author:       Florian Hocquet
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
        :summary:      a script to use workspaces from terminal

        This class allows you to represent, by creating an object, one of the
        different features you have in your software.
        To use an object Feature you have to intantiate it without arguments,
        an then you can fix the values of privates attributes of your Feature
        object, there are 5 privates attributes :

        - enable
        - available
        - id
        - dict_packages
        - dict_pypi

        To fix their values you have to use the getters and the setters
        of the Feature.
        For example :

        >>> feature = Feature()
        >>> feature.set_enable(True)
        >>> feature.set_available(True)
        >>> feature.set_id("feature")
        >>> feature.set_dict_packages({"1": "a"})
        >>> feature.set_dict_pypi({"2": "b"})

        You can set the values of your privates attributes with the setters by parsing
        a requirements.ini file.
    """

    def __init__(self):
        """Create a new Feature instance."""

        # An identifier to represent if the feature is enable or no
        self.__enable = False

        # An identifier to represent if the feature is available on your system or no
        self.__available = False

        # An identifier that represent the id/name of the feature
        self.__id = str()

        # An identifier to represent the required system packages
        self.__dict_packages = dict()

        # An identifier to represent the required pip packages
        self.__dict_pypi = dict()

    # ---------------------------------------------------------------------------

    def get_enable(self):
        """Return the value of the private attribute enable of the instantiate
        Feature.
        """
        return self.__enable

    # ---------------------------------------------------------------------------

    def set_enable(self, value):
        """Fix the enable private attribute.

        :param value: (boolean) The boolean that represent if the feature is
        installed or no on your system.
        """
        value = bool(value)
        self.__enable = value

    # ---------------------------------------------------------------------------

    def get_available(self):
        """Return the value of the private attribute available of the instantiate
        Feature.
        """
        return self.__available

    # ---------------------------------------------------------------------------

    def set_available(self, value):
        """Fix the available private attribute.

        :param value: (boolean) The boolean that represent if the feature is
        available or no on your system.
        """
        value = bool(value)
        self.__available = value

    # ---------------------------------------------------------------------------

    def get_id(self):
        """Return the value of the private attribute id of the instantiate
        Feature.
        """
        return self.__id

    # ---------------------------------------------------------------------------

    def set_id(self, value):
        """Fix the id private attribute.

        :param value: (str) The id/name that represent the feature.
        """
        value = str(value)
        self.__id = value

    # ---------------------------------------------------------------------------

    def get_dict_packages(self):
        """Return the packages_dictionary, of the required system packages,
        of the instantiate Feature.
        """
        return self.__dict_packages

    # ---------------------------------------------------------------------------

    def set_dict_packages(self, dependencies):
        """Fix the values of your dict_packages private attribute.

        :param dependencies: (dict()) The dictionary with the one you will fill
        your dict_packages, that represent some of the packages you will
        install later.
        """
        dependencies = dict(dependencies)
        self.__dict_packages = dependencies

    # ---------------------------------------------------------------------------

    def get_dict_pypi(self):
        """Return the pypi_dictionary, of the required pypi packages,
        of the instantiate Feature.
        """
        return self.__dict_pypi

    # ---------------------------------------------------------------------------

    def set_dict_pypi(self, dependencies):
        """Fix the values of your dict_pypi private attribute.

        :param dependencies: (dict()) The dictionary with the one you will fill
        your dict_packages, that represent some of the packages you will
        install later.
        """
        dependencies = dict(dependencies)
        self.__dict_pypi = dependencies

    # ---------------------------------------------------------------------------

