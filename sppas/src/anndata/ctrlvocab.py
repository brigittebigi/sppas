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

    anndata.ctrlvocab.py
    ~~~~~~~~~~~~~~~~~~~~

"""

from collections import OrderedDict

from sppas.src.utils import sppasUnicode
from .anndataexc import AnnDataTypeError
from .anndataexc import CtrlVocabContainsError
from .ann.annlabel import sppasTag
from .metadata import sppasMetaData

# ----------------------------------------------------------------------------


class sppasCtrlVocab(sppasMetaData):
    """Generic representation of a controlled vocabulary.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018 Brigitte Bigi

    A controlled Vocabulary is a set of tags. It is used to restrict the use
    of tags in a label: only the accepted tags can be set to a label.

    A controlled vocabulary is made of an identifier name, a description and
    a list of pairs tag/description.

    """

    def __init__(self, name, description=""):
        """Create a new sppasCtrlVocab instance.

        :param name: (str) Identifier name of the controlled vocabulary
        :param description: (str)

        """
        super(sppasCtrlVocab, self).__init__()

        # The name:
        # make unicode, strip and replace whitespace by underscore.
        su = sppasUnicode(str(name))
        self.__name = su.clear_whitespace()

        # The description:
        self.__desc = ""
        if len(description) > 0:
            self.set_description(description)

        # The set of tags:
        self.__entries = OrderedDict()

    # -----------------------------------------------------------------------

    def get_name(self):
        """Return the name of the controlled vocabulary."""
        return self.__name

    # -----------------------------------------------------------------------

    def get_description(self):
        """Return the unicode str of the description of the ctrl vocab."""
        return self.__desc

    # -----------------------------------------------------------------------

    def get_tag_description(self, tag):
        """Return the unicode string of the description of an entry.

        :param tag: (sppasTag) the tag to get the description.
        :returns: (str)

        """
        if self.contains(tag) is False:
            raise CtrlVocabContainsError(tag)

        return self.__entries[tag]

    # ------------------------------------------------------------------------

    def set_description(self, description=""):
        """Set the description of the controlled vocabulary.

        :param description: (str)

        """
        su = sppasUnicode(description)
        self.__desc = su.to_strip()

    # -----------------------------------------------------------------------

    def contains(self, tag):
        """Test if a tag is in the controlled vocabulary.

        Attention: Do not check the instance but the data content of the tag.

        :param tag: (sppasTag) the tag to check.
        :returns: Boolean

        """
        if isinstance(tag, sppasTag) is False:
            raise AnnDataTypeError(tag, "sppasTag")

        for entry in self.__entries:
            if tag == entry:
                # compare the content and the type...
                return True

        return False

    # -----------------------------------------------------------------------

    def validate_tag(self, tag):
        """Check if the given tag can be added to the ctrl vocabulary.

        :param tag: (sppasTag) the tag to check.
        :returns: Boolean

        """
        if isinstance(tag, sppasTag) is False:
            raise AnnDataTypeError(tag, "sppasTag")

        # check if the tag is of the same type than the existing ones.
        current_type = tag.get_type()
        for k in self.__entries:
            current_type = k.get_type()
            break
        if tag.get_type() != current_type:
            raise AnnDataTypeError(tag, "sppasTag:"+current_type)

    # -----------------------------------------------------------------------

    def add(self, tag, description=""):
        """Add a tag to the controlled vocab.

        :param tag: (sppasTag): the tag to add.
        :param description: (str)
        :returns: Boolean

        """
        self.validate_tag(tag)
        if self.contains(tag) is True:
            return False

        su = sppasUnicode(description)
        self.__entries[tag] = su.to_strip()
        return True

    # -----------------------------------------------------------------------

    def remove(self, tag):
        """Remove a tag of the controlled vocab.

        :param tag: (sppasTag) the tag to remove.
        :returns: Boolean

        """
        if isinstance(tag, sppasTag) is False:
            raise AnnDataTypeError(tag, "sppasTag")

        if self.contains(tag) is False:
            return False

        del self.__entries[tag]
        return True

    # ------------------------------------------------------------------------

    def set_tag_description(self, tag, description):
        """Set the unicode string of the description of an entry.

        :param tag: (sppasTag) the tag to get the description.
        :param description: (str)
        :returns: (str)

        """
        if self.contains(tag) is False:
            raise CtrlVocabContainsError(tag)

        su = sppasUnicode(description)
        self.__entries[tag] = su.to_strip()

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__entries:
            yield a

    def __len__(self):
        return len(self.__entries)

    def __repr__(self):
        return "CtrlVocab: id={:s} name={:s} description={:s}" \
               "".format(self.get_meta('id'), self.__name, self.__desc)

    def __eq__(self, other):
        """Test if other is strictly identical to self (even the id)."""

        if isinstance(other, sppasCtrlVocab) is False:
            return False

        for meta_key in self.get_meta_keys():
            if self.get_meta(meta_key) != other.get_meta(meta_key):
                return False
        for meta_key in other.get_meta_keys():
            if self.get_meta(meta_key) != other.get_meta(meta_key):
                return False

        if self.__name != other.get_name():
            return False
        if self.__desc != other.get_description():
            return False

        for entry in self:
            if other.contains(entry) is False:
                return False
            if self.get_tag_description(entry) != \
                    other.get_tag_description(entry):
                return False

        return len(self) == len(other)

    def __ne__(self, other):
        return not self == other
