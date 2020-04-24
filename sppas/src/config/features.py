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
        >>> feature.set_packages({"1": "a"})
        >>> feature.set_pypi({"2": "b"})
        >>> feature.set_cmd("pip freeze")

        You can set the values of your privates attributes with the setters by parsing
        a requirements.ini file.

    """

    def __init__(self):
        """Create a new Feature instance.

        """
        # An identifier to represent if the feature is enable or no
        self.__enable = False

        # An identifier to represent if the feature is available on your system or no
        self.__available = True

        # An identifier that represent the id/name of the feature
        self.__id = str()

        # An identifier that represent the description of the feature
        self.__desc = str()

        # An identifier to represent the required system packages
        self.__packages = dict()

        # An identifier to represent the required pip packages
        self.__pypi = dict()

        # An identifier to represent a system command
        self.__cmd = str()

    # ---------------------------------------------------------------------------

    def __str__(self):
        """Print the privates attributes of your Feature object.

        """
        return "enable : " + str(self.get_enable()) + "\n" \
               "available : " + str(self.get_available()) + "\n" \
               "id : " + str(self.get_id()) + "\n" \
               "desc : " + str(self.get_desc()) + "\n" \
               "packages : " + str(self.get_packages()) + "\n" \
               "pypi : " + str(self.get_pypi()) + "\n" \
               "cmd : " + str(self.get_cmd()) + "\n"

    # ---------------------------------------------------------------------------

    def get_enable(self):
        """Return the value of the private attribute enable of the instantiate Feature.

        """
        return self.__enable

    # ---------------------------------------------------------------------------

    def get_available(self):
        """Return the value of the private attribute available of the instantiate Feature.

        """
        return self.__available
    # ---------------------------------------------------------------------------

    def set_enable(self, value):
        """Fix the value of the private attribute __enable.

        :param value: (boolean) The boolean which represent if you want to install the
        feature or if it's installed or not on your system.

        """
        if not self.get_available():
            self.__enable = False
        else:
            value = bool(value)
            self.__enable = value

    # ---------------------------------------------------------------------------

    def set_available(self, value):
        """Fix the value of the private attribute __available.

        :param value: (boolean) The boolean which represent if you want to install the
        feature or if it is already installed or not on your system.
        """
        value = bool(value)
        if not value:
            self.set_enable(False)
        self.__available = value

    # ---------------------------------------------------------------------------

    def get_id(self):
        """Return the value of the private attribute __id of the instantiate Feature.

        """
        return self.__id

    # ---------------------------------------------------------------------------

    def set_id(self, value):
        """Fix the value of the private attribute __id.

        :param value: (str) The id/name which represent the feature.

        """
        value = str(value)
        self.__id = value

    # ---------------------------------------------------------------------------

    def get_desc(self):
        """Return the value of the private attribute __desc of the instantiate Feature.

        """
        return self.__desc

    # ---------------------------------------------------------------------------

    def set_desc(self, value):
        """Fix the value of the private attribute __desc.

        :param value: (str) The description which represent the feature.

        """
        value = str(value)
        self.__desc = value

    # ---------------------------------------------------------------------------

    def get_packages(self):
        """Return the packages_dictionary, of the required system packages, of the instantiate Feature.

        """
        return self.__packages

    # ---------------------------------------------------------------------------

    def set_packages(self, dependencies):
        """Fix the values of the private attribute __packages.

        :param dependencies: (dict()) The dictionary with the one you will fill
        your __packages, that represent some of the packages you will
        install later.

        """
        dependencies = dict(dependencies)
        self.__packages = dependencies

    # ---------------------------------------------------------------------------

    def get_pypi(self):
        """Return the pypi_dictionary, of the required pypi packages, of the instantiate Feature.

        """
        return self.__pypi

    # ---------------------------------------------------------------------------

    def set_pypi(self, dependencies):
        """Fix the values of the private attribute __pypi.

        :param dependencies: (dict()) The dictionary with the one you will fill
        your __pypi, that represent some of the packages you will
        install later.

        """
        dependencies = dict(dependencies)
        self.__pypi = dependencies

    # ---------------------------------------------------------------------------

    def get_cmd(self):
        """Return the value of the private attribute __cmd of the instantiate Feature.

        """
        return self.__cmd

    # ---------------------------------------------------------------------------

    def set_cmd(self, value):
        """Fix the value of the private attribute __cmd.

        :param value: (str) The unique command for the OS.

        """
        value = str(value)
        self.__cmd = value

    # ---------------------------------------------------------------------------

