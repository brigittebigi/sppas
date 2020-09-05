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

    src.preinstall.feature.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import uuid
import re
from sppas.src.config import paths

# ---------------------------------------------------------------------------


MSG_NO_BRIEF = "No brief description available"
MSG_NO_DESCR = "No description is available for this feature."

# ---------------------------------------------------------------------------


class Feature(object):
    """Store information of one feature required by the application.

        :author:       Florian Hocquet, Brigitte Bigi
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        :Example:

        >>> feature = Feature("feature")
        >>> feature.get_id()
        >>> "feature"
        >>> feature.set_enable(True)
        >>> feature.set_available(True)
        >>> feature.set_desc("An example of feature")
        >>> feature.set_packages({"wxpython": ">;4.0"})
        >>> feature.set_pypi({"numpy": ">;0.0"})
        >>> feature.set_cmd("pip freeze")

    """

    def __init__(self, identifier):
        """Create a new Feature instance.

        :param identifier: (str) An identifier string.

        The identifier must contain at least 2 characters and US-ASCII only.
        If these requirements are not satisfied, a GUID is used instead.

        """
        # Represent the identifier of the feature
        self.__id = str(uuid.uuid4())
        self.__set_id(identifier)

        # Represent if the feature is enable
        self.__enable = False

        # Represent if the feature is available
        self.__available = False

        # Represent a short description of the feature
        self.__brief = MSG_NO_BRIEF

        # Represent a full description of the feature
        self.__descr = MSG_NO_DESCR

    # ------------------------------------------------------------------------

    def get_type(self):
        return str()

    # ------------------------------------------------------------------------

    def __set_id(self, identifier):
        """Private. Set the id if valid."""
        identifier = identifier.strip()
        # Check length
        if len(identifier) > 1:
            # Check if US-ASCII only characters
            ra = re.sub(r'[^a-zA-Z0-9_]', '', identifier)
            if identifier == ra:
                self.__id = identifier

    # ------------------------------------------------------------------------

    def get_id(self):
        """Return the feature identifier."""
        return self.__id

    # ------------------------------------------------------------------------

    def get_enable(self):
        """Return True if the feature is enabled."""
        return self.__enable

    # ------------------------------------------------------------------------

    def set_enable(self, value):
        """Set the value of enable.

        :param value: (bool) Enable or disable the feature.

        """
        if not self.get_available():
            self.__enable = False
        else:
            value = bool(value)
            self.__enable = value

    # ------------------------------------------------------------------------

    def get_available(self):
        """Return True if the feature is available."""
        return self.__available

    # ------------------------------------------------------------------------

    def set_available(self, value):
        """Set the value of available.

        :param value: (bool) Make the feature available or not.

        """
        value = bool(value)
        if not value:
            self.set_enable(False)
        self.__available = value

    # ------------------------------------------------------------------------

    def get_brief(self):
        """Return a short description of the feature."""
        return self.__brief

    # ------------------------------------------------------------------------

    def set_brief(self, value):
        """Set the brief description of the feature.

        :param value: (str) The description to describe the feature.

        """
        value = str(value)
        value = value.strip()
        if len(value) == 0:
            value = MSG_NO_BRIEF
        self.__brief = value

    # ------------------------------------------------------------------------

    def get_desc(self):
        """Return the description of the feature."""
        return self.__descr

    # ------------------------------------------------------------------------

    def set_desc(self, value):
        """Set the description of the feature.

        :param value: (str) The description to describe the feature.

        """
        value = str(value)
        value = value.strip()
        if len(value) == 0:
            value = MSG_NO_DESCR
        self.__descr = value

    # ------------------------------------------------------------------------

    def __str__(self):
        return "id: " + str(self.get_id()) + "\n" \
               "enable: " + str(self.get_enable()) + "\n" \
               "available: " + str(self.get_available()) + "\n" \
               "brief: " + str(self.get_brief()) + "\n" \
               "description: " + str(self.get_desc()) + "\n"


class DepsFeature(Feature):
    """Store information of one feature required by the application.

        :author:       Florian Hocquet, Brigitte Bigi
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        Sub-class to represent a package to be installed or a command to be
        executed, or both, ie the need of external programs.

    """

    def __init__(self, identifier):
        super(DepsFeature, self).__init__(identifier)

        # Represent the required system packages
        self.__packages = dict()

        # Represent the required pip packages
        self.__pypi = dict()

        # Represent a command to be executed
        self.__cmd = str()

    # ------------------------------------------------------------------------

    def get_type(self):
        return "deps"

    # ------------------------------------------------------------------------

    def get_packages(self):
        """Return the dictionary of system dependencies."""
        return self.__packages

    # ------------------------------------------------------------------------

    def set_packages(self, dependencies):
        """Set the dictionary of system dependencies.

        :param dependencies: (dict)

        """
        dependencies = dict(dependencies)
        self.__packages = dependencies

    # ------------------------------------------------------------------------

    def get_pypi(self):
        """Return the dictionary of pip dependencies."""
        return self.__pypi

    # ------------------------------------------------------------------------

    def set_pypi(self, dependencies):
        """Set the dictionary of pip dependencies.

        :param dependencies: (dict)

        """
        dependencies = dict(dependencies)
        self.__pypi = dependencies

    # ------------------------------------------------------------------------

    def get_cmd(self):
        """Return the command to execute."""
        return self.__cmd

    # ------------------------------------------------------------------------

    def set_cmd(self, value):
        """Set the command to execute.

        :param value: (str) The system command for the OS.

        """
        value = str(value)
        if "$SPPAS" in value:
            base_dir = paths.basedir
            if "\\" in base_dir:
                base_dir = base_dir.replace("\\", "\\\\")
            value = value.replace("$SPPAS", base_dir)

        self.__cmd = value

# ---------------------------------------------------------------------------


class LangFeature(Feature):
    """Store information of one feature required by the application.

        :author:       Florian Hocquet, Brigitte Bigi
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        Sub-class to represent a language support, ie the need to download
        linguistic resources of a given language to enable language-dependent
        automatic annotations.

    """

    def __init__(self, identifier):
        super(LangFeature, self).__init__(identifier)
        self.__lang = str()

    # ------------------------------------------------------------------------

    def get_type(self):
        return "lang"

    # ------------------------------------------------------------------------

    def get_lang(self):
        """Return the lang resource name to be downloaded."""
        return self.__lang

    # ------------------------------------------------------------------------

    def set_lang(self, value):
        """Set the iso-6639-3 code of the lang resource to download.

        :param value: (str) 3 chars if standard name

        """
        value = str(value)
        value = value.strip()
        if len(value) != 3:
            logging.warning("Set a non-standard language name '{:s}'"
                            " for feature '{}'.".format(value, self.get_id()))
        self.__lang = value

# ---------------------------------------------------------------------------


class AnnotFeature(Feature):
    """Store information of one feature required by the application.

        :author:       Florian Hocquet, Brigitte Bigi
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

        Sub-class to represent a the support of an automatic annotation, ie
        the need to download resources (models, protos...) to enable the
        automatic annotation.

    """

    def __init__(self, identifier):
        super(AnnotFeature, self).__init__(identifier)
        self.__annot = str()

    # ------------------------------------------------------------------------

    def get_type(self):
        return "annot"

    # ------------------------------------------------------------------------

    def get_annot(self):
        """Return the annotation resource name to be downloaded."""
        return self.__annot

    # ------------------------------------------------------------------------

    def set_annot(self, value):
        """Set the annotation resource name to download.

        :param value: (str) ascii-only chars

        """
        value = str(value)
        value = value.strip()
        if len(value) == 0:
            logging.warning("Attempted to set a wrong annot name '{:s}' for "
                            "feature '{}'.".format(value, self.get_id()))
        else:
            self.__annot = value


