# -*- coding: UTF-8 -*-
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

    structs.lang.py
    ~~~~~~~~~~~~~~~~~~~

"""

import os

from sppas.src.config import paths
from sppas.src.config import annots
from sppas.src.wkps import sppasDirUtils

from .structsexc import LangTypeError
from .structsexc import LangPathError
from .structsexc import LangNameError

# ----------------------------------------------------------------------------


class sppasLangResource(object):
    """Manage information of a resource for a language.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    In most of the automatic annotations, we have to deal with language
    resources. Here, we store information about the type of resources,
    the path to get them, etc.

    """

    RESOURCES_TYPES = ["file", "directory"]

    def __init__(self):
        """Create a sppasLangResource instance.

        """
        # All available language resources (type, path, filename, extension)
        self._rtype = ""
        self._rpath = ""
        self._rname = ""
        self._rext = ""

        # The list of languages the resource can provide
        self.langlist = list()

        # The selected language
        self.lang = ""

        # The language resource of the selected language
        self.langresource = ""

    # ------------------------------------------------------------------------

    def reset(self):
        """Set all members to their default value."""
        self._rtype = ""
        self._rpath = ""
        self._rname = ""
        self._rext = ""

        self.langlist = []
        self.lang = ""
        self.langresource = ""

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_lang(self):
        """Return the language name.

        Language names in SPPAS are commonly represented in iso-639-3.
        It is a code that aims to define three-letter identifiers for all
        known human languages. "und" is representing an undetermined language.
        See <http://www-01.sil.org/iso639-3/> for details...

        :returns: (str) Language code or an empty string if no lang was set.

        """
        return self.lang

    # ------------------------------------------------------------------------

    def get_langlist(self):
        """Return the list of available languages.

        :returns: List of str

        """
        return self.langlist

    # ------------------------------------------------------------------------

    def get_langresource(self):
        """Return the resource name defined for the given language."""
        # Is there a resource available for this language?
        if self.lang in self.langlist:
            if len(self._rname) > 0:
                return self.langresource + self.lang + self._rext
            else:
                return os.path.join(self.langresource, self.lang + self._rext)

        return self.langresource

    # ------------------------------------------------------------------------

    def get_resourcetype(self):
        """Return the language type."""
        return self._rtype

    # ------------------------------------------------------------------------

    def get_resourceext(self):
        """Return the language extension."""
        return self._rext

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_type(self, resource_type):
        """Set the type of the resource.

        :param resource_type: (str) One of "file" or "directory".

        """
        resource_type = str(resource_type)
        if resource_type not in sppasLangResource.RESOURCES_TYPES:
            self.reset()
            raise LangTypeError(resource_type)

        self._rtype = resource_type

    # ------------------------------------------------------------------------

    def set_path(self, resource_path):
        """Fix the language resource path.

        :param resource_path: (str) Relative path to find the resource.

        """
        resource_path = str(resource_path)

        folder = os.path.join(paths.resources, resource_path)
        if os.path.exists(folder) is False:
            self.reset()
            raise LangPathError(folder)

        self._rpath = resource_path

    # ------------------------------------------------------------------------

    def set_filename(self, resource_filename):
        """Fix the language resource filename.

        :param resource_filename: (str) Resource filename.

        """
        self._rname = str(resource_filename)

    # ------------------------------------------------------------------------

    def set_extension(self, resource_extension):
        """Fix the language resource file extension.

        :param resource_extension: (str) Resource filename extension.

        """
        self._rext = str(resource_extension)

    # ------------------------------------------------------------------------

    def set(self, rtype, rpath, rname="", rext=""):
        """Set resources then fix the list of available languages.

        :param rtype: (str) Resource type. One of: "file" or "directory"
        :param rpath: (str) Resource path
        :param rname: (str) Resource file name
        :param rext: (str)  Resource extension

        """
        self.reset()

        # Fix the language resource basis information
        self.set_type(rtype)
        self.set_path(rpath)
        self.set_filename(rname)
        self.set_extension(rext)

        directory = os.path.join(paths.resources, self._rpath)

        # Fix the language resource information
        if len(self._rname) > 0:
            self.langresource = os.path.join(paths.resources,
                                             self._rpath,
                                             self._rname)
        else:
            self.langresource = directory

        # Fix the list of available languages
        if rtype == "file":
            if len(rext) > 0:
                sd = sppasDirUtils(directory)
                for selectedfile in sd.get_files(self._rext):
                    filename, fext = os.path.splitext(selectedfile)
                    filename = os.path.basename(filename)
                    self.langlist.append(filename.replace(self._rname, ""))

        else:
            self._rext = ""
            if len(self._rname) > 0:
                for dirname in os.listdir(directory):
                    if dirname.startswith(rname) is True:
                        self.langlist.append(dirname.replace(self._rname, ""))

    # ------------------------------------------------------------------------

    def set_lang(self, lang):
        """Set the language.

        To reset the language, fix lang to None.

        :param lang: (str) The language must be either UNDETERMINED
        or one of the language of the list.

        """
        if lang is None:
            self.lang = ""
            return

        if lang.lower() != annots.UNDETERMINED and lang not in self.langlist:
            raise LangNameError(lang)

        self.lang = lang
