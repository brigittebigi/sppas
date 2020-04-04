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

    anndata.ann.annlabel.tag.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import symbols
from sppas.src.utils.makeunicode import sppasUnicode, b

from ...anndataexc import AnnDataTypeError
from ...anndataexc import AnnUnkTypeError

# ---------------------------------------------------------------------------


class sppasTag(object):
    """Represent one of the possible tags of a label.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    A sppasTag is a data content of any type.
    By default, the type of the data is "str" and the content is empty, but
    sppasTag stores 'None' values because None is 16 bits and an empty string
    is 37.

    A sppasTag() content can be one of the following types:

        1. string/unicode - (str)
        2. integer - (int)
        3. float - (float)
        4. boolean - (bool)
        5. a list of sppasTag(), all of the same type - (list)

    Get access to the content with the get_content() method and to the typed
    content with get_typed_content().

        >>> t1 = sppasTag("2")                      # "2" (str)
        >>> t2 = sppasTag(2)                        # "2" (str)
        >>> t3 = sppasTag(2, tag_type="int")        # 2 (int)
        >>> t4 = sppasTag("2", tag_type="int")      # 2 (int)
        >>> t5 = sppasTag("2", tag_type="float")    # 2. (float)
        >>> t6 = sppasTag("true", tag_type="bool")  # True (bool)
        >>> t7 = sppasTag(0, tag_type="bool")       # False (bool)

    """

    TAG_TYPES = ("str", "float", "int", "bool")

    # ------------------------------------------------------------------------

    def __init__(self, tag_content, tag_type=None):
        """Initialize a new sppasTag instance.

        :param tag_content: (any) Data content
        :param tag_type: (str): The type of this content.\
        One of: ('str', 'int', 'float', 'bool').

        'str' is the default tag_type.

        """
        self.__tag_content = ""
        self.__tag_type = None
        
        self.set_content(tag_content, tag_type)

    # ------------------------------------------------------------------------

    def set(self, other):
        """Set self members from another sppasTag instance.

        :param other: (sppasTag)

        """
        if isinstance(other, sppasTag) is False:
            raise AnnDataTypeError(other, "sppasTag")

        self.set_content(other.get_content())
        self.__tag_type = other.get_type()

    # -----------------------------------------------------------------------

    def get_content(self):
        """Return an unicode string corresponding to the content.

        Also returns a unicode string in case of a list (elements are
        separated by a space).

        :returns: (unicode)

        """
        return self.__tag_content

    # ------------------------------------------------------------------------

    def get_typed_content(self):
        """Return the content value, in its appropriate type.

        Excepted for strings which are systematically returned as unicode.

        """
        if self.__tag_type is not None:

            if self.__tag_type == "int":
                return int(self.__tag_content)

            if self.__tag_type == "float":
                return float(self.__tag_content)

            if self.__tag_type == "bool":
                if self.__tag_content.lower() == "true":
                    return True
                else:
                    return False

        return self.__tag_content

    # ------------------------------------------------------------------------

    def set_content(self, tag_content, tag_type=None):
        """Change content of this sppasTag.

        :param tag_content: (any) New text content for this sppasTag
        :param tag_type: The type of this tag.\
        Default is 'str' to represent an unicode string.

        """
        # Check type
        if tag_type is not None and tag_type not in sppasTag.TAG_TYPES:
            raise AnnUnkTypeError(tag_type)
        if tag_type == "str":
            tag_type = None

        # Check content depending on the given type
        if tag_content is None:
            tag_content = ""

        if tag_type == "float":
            try:
                tag_content = float(tag_content)
            except ValueError:
                raise AnnDataTypeError(tag_content, "float")

        elif tag_type == "int":
            try:
                tag_content = int(tag_content)
            except ValueError:
                raise AnnDataTypeError(tag_content, "int")

        elif tag_type == "bool":
            if tag_content not in ('False', 'True'):
                # always works. Never raises ValueError!
                tag_content = bool(tag_content)

        # we systematically convert data into strings
        self.__tag_type = tag_type
        tag_content = str(tag_content)
        su = sppasUnicode(tag_content)
        self.__tag_content = su.to_strip()

    # ------------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of self."""
        return sppasTag(self.__tag_content, self.__tag_type)

    # ------------------------------------------------------------------------

    def get_type(self):
        """Return the type of the tag content."""
        if self.__tag_type is None:
            return "str"
        return self.__tag_type

    # ------------------------------------------------------------------------

    def is_empty(self):
        """Return True if the tag is an empty string."""
        return self.__tag_content == ""

    # -----------------------------------------------------------------------

    def is_speech(self):
        """Return True if the tag is not a silence."""
        return not (self.is_silence() or
                    self.is_pause() or
                    self.is_laugh() or
                    self.is_noise() or
                    self.is_dummy())

    # -----------------------------------------------------------------------

    def is_silence(self):
        """Return True if the tag is a silence."""
        if self.__tag_type is None or self.__tag_type == "str":
            # create a list of silence symbols from the list of all symbols
            silences = list()
            for symbol in symbols.all:
                if symbols.all[symbol] == "silence":
                    silences.append(symbol)

            if self.__tag_content in silences:
                return True

            # HACK. Exception for the French CID corpus:
            if self.__tag_content.startswith("gpf_"):
                return True

        return False

    # -----------------------------------------------------------------------

    def is_pause(self):
        """Return True if the tag is a short pause."""
        # create a list of pause symbols from the list of all symbols
        pauses = list()
        for symbol in symbols.all:
            if symbols.all[symbol] == "pause":
                pauses.append(symbol)

        return self.__tag_content in pauses

    # -----------------------------------------------------------------------

    def is_laugh(self):
        """Return True if the tag is a laughing."""
        # create a list of laughter symbols from the list of all symbols
        laugh = list()
        for symbol in symbols.all:
            if symbols.all[symbol] == "laugh":
                laugh.append(symbol)

        return self.__tag_content in laugh

    # -----------------------------------------------------------------------

    def is_noise(self):
        """Return True if the tag is a noise."""
        # create a list of noise symbols from the list of all symbols
        noises = list()
        for symbol in symbols.all:
            if symbols.all[symbol] == "noise":
                noises.append(symbol)

        return self.__tag_content in noises

    # -----------------------------------------------------------------------

    def is_dummy(self):
        """Return True if the tag is a dummy label."""
        return self.__tag_content == "dummy"

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Tag: {!s:s},{!s:s}".format(b(self.get_content()),
                                           self.get_type())

    # -----------------------------------------------------------------------

    def __str__(self):
        return "{!s:s} ({!s:s})".format(b(self.get_content()),
                                        self.get_type())

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Compare 2 tags."""
        if isinstance(other, sppasTag):
            return self.get_typed_content() == other.get_typed_content()
        return False

    # -----------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__tag_content, self.__tag_type))

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        if isinstance(other, sppasTag):
            return self.get_typed_content() != other.get_typed_content()
        return True
