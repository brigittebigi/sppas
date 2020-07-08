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

    src.wkps.fileref.py
    ~~~~~~~~~~~~~~~~~~~~

    Define a sppasRefAttribute() and a sppasCatReference().

"""

from sppas.src.exceptions.exc import sppasTypeError, sppasIndexError
from sppas.src.config import annots
from sppas.src.utils.makeunicode import sppasUnicode

from .filebase import FileBase
from .wkpexc import AttributeIdValueError, AttributeTypeValueError
from .wkpexc import FileAddValueError, FileRemoveValueError

# ---------------------------------------------------------------------------


class sppasRefAttribute(object):
    """Represent any attribute with an id, a value, and a description.

    :author:       Barthélémy Drabczuk, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    VALUE_TYPES = ('str', 'int', 'float', 'bool')

    def __init__(self, identifier, value=None, att_type=None, descr=None):
        """Constructor of sppasRefAttribute.

        :param identifier: (str) The identifier of the attribute
        :param value: (str) String representing the value of the attribute
        :param att_type: (str) One of the VALUE_TYPES
        :param descr: (str) A string to describe what the attribute is
        :raises: AttributeIdValueError

        """
        self.__id = ""
        self.__set_id(identifier)

        self.__value = None
        self.set_value(value)
        
        self.__valuetype = 'str'
        self.set_value_type(att_type)

        self.__descr = None
        self.set_description(descr)

    # -----------------------------------------------------------------------

    @staticmethod
    def validate(identifier):
        """Return True if the given identifier matches the requirements.

        An id should contain between 3 and 12 ASCII-characters only, i.e.
        letters a-z, letters A-Z and numbers 0-9.

        :param identifier: (str) Key to be validated
        :returns: (bool)

        """
        if 1 < len(identifier) < 13:
            return True
        return False

    # -----------------------------------------------------------------------

    def __set_id(self, identifier):
        su = sppasUnicode(identifier)
        identifier = su.unicode()

        if sppasRefAttribute.validate(identifier) is False:
            raise AttributeIdValueError(identifier)

        self.__id = identifier

    # -----------------------------------------------------------------------

    def get_id(self):
        """Return the identifier of the attribute."""
        return self.__id

    # -----------------------------------------------------------------------

    id = property(get_id, None)

    # -----------------------------------------------------------------------

    def get_value(self):
        """Return the current non-typed value.

        :returns: (str)

        """
        if self.__value is None:
            return ""
        return self.__value

    # -----------------------------------------------------------------------

    def set_value(self, value):
        """Set a new value.

        :param value: (str)

        """
        if value is None:
            self.__value = None
        else:
            su = sppasUnicode(value)
            self.__value = su.to_strip()

    # -----------------------------------------------------------------------

    def get_value_type(self):
        """Return the current type of the value.

        :returns: (str) Either: "str", "int", "float", "bool".

        """
        return self.__valuetype if self.__valuetype is not None else 'str'

    # -----------------------------------------------------------------------

    def set_value_type(self, type_name):
        """Set a new type for the current value.

        :param type_name: (str) the new type name
        :raises: sppasTypeError

        """
        if type_name in sppasRefAttribute.VALUE_TYPES:
            self.__valuetype = type_name
            try:
                self.get_typed_value()
            except AttributeTypeValueError:
                self.__valuetype = 'str'
                raise

        elif type_name is None:
            self.__valuetype = 'str'

        else:
            raise sppasTypeError(type_name, " ".join(sppasRefAttribute.VALUE_TYPES))

    # -----------------------------------------------------------------------

    def get_typed_value(self):
        """Return the current typed value.

        :returns: (any type) the current typed value.

        """
        if self.__valuetype is not None or self.__valuetype != 'str':
            try:
                if self.__valuetype == 'int':
                    return int(self.__value)
                elif self.__valuetype == 'float':
                    return float(self.__value)
                elif self.__valuetype == 'bool':
                    return self.__value.lower() == 'true'
            except ValueError:
                raise AttributeTypeValueError(self.__value, self.__valuetype)
            except TypeError:
                raise AttributeTypeValueError(self.__value, self.__valuetype)

        return self.__value

    # -----------------------------------------------------------------------

    def get_description(self):
        """Return current description of the attribute.

        :returns: (str)

        """
        if self.__descr is None:
            return ""
        return self.__descr

    # -----------------------------------------------------------------------

    def set_description(self, description):
        """Set a new description of the attribute.

        :param description: (str)

        """
        if description is None:
            self.__descr = None
        else:
            su = sppasUnicode(description)
            self.__descr = su.to_strip()

    # ---------------------------------------------------------
    # Overloads
    # ----------------------------------------------------------

    def __str__(self):
        return '{:s}, {:s}, {:s}'.format(
            self.__id,
            self.get_value(),
            self.get_description())

    def __repr__(self):
        return '{:s}, {:s}, {:s}'.format(
            self.__id,
            self.get_value(),
            self.get_description())

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__id, self.get_typed_value(), self.__descr))

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, sppasRefAttribute) is False:
            return False
        if self.__id != other.get_id():
            return False
        if self.get_typed_value() != other.get_typed_value():
            return False
        if self.get_description() != other.get_description():
            return False
        return True

# ---------------------------------------------------------------------------


class sppasCatReference(FileBase):
    """Represent a reference in the catalogue of a workspace.

    :author:       Barthélémy Drabczuk, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Reference is a dictionary with a name. Its keys are only alphanumerics
    characters spaced with underscores and its values are all sppasRefAttribute
    objects.

    """

    def __init__(self, identifier):
        """Constructor of the sppasCatReference class.

        :param identifier: (str) identifier for the object, the name of the reference

        """
        super(sppasCatReference, self).__init__(identifier)

        self.__attributs = list()
        self.__type = annots.types[0]

        # A free to use member to expand the class
        self.subjoined = None

    # ------------------------------------------------------------------------

    def att(self, identifier):
        """Return the attribute matching the given identifier or None.

        :param identifier: (str) Id of a sppasRefAttribute
        :return: sppasRefAttribute or None if the identifier does not match
        any attribute of this reference.

        """
        su = sppasUnicode(identifier)
        identifier = su.unicode()
        for a in self.__attributs:
            if a.get_id() == identifier:
                return a

        return None

    # ------------------------------------------------------------------------

    def add(self, identifier, value=None, att_type=None, descr=None):
        """Append an attribute into the reference.

        :param identifier: (str) Id of a sppasRefAttribute
        :param value: (any type)
        :param att_type: (str) One of 'str', 'bool', 'int', 'float'. Default is 'str'.
        :param descr: (str) A text to describe the attribute
        :raise: AttributeIdValueError

        """
        self.append(sppasRefAttribute(identifier, value, att_type, descr))

    # ------------------------------------------------------------------------

    def append(self, att):
        """Append an attribute into a reference.

        :param att: (sppasRefAttribute)

        """
        if isinstance(att, sppasRefAttribute) is False:
            raise sppasTypeError(att, "sppasRefAttribute")

        if att in self:
            raise FileAddValueError(att.get_id())

        self.__attributs.append(att)

    # ------------------------------------------------------------------------

    def pop(self, identifier):
        """Delete an attribute of this reference.

        :param identifier: (str, sppasRefAttribute) the attribute or its id to delete

        """
        if identifier in self:
            if isinstance(identifier, sppasRefAttribute) is False:
                identifier = self.att(identifier)
            self.__attributs.remove(identifier)
        else:
            raise FileRemoveValueError(identifier)

    # ------------------------------------------------------------------------

    def set_state(self, state):
        """Set the current state to a new one.

        :param state: (State)
        :raises (sppasTypeError)

        """
        if isinstance(state, int):
            self._state = state
        else:
            raise sppasTypeError(state, 'States')

    # ------------------------------------------------------------------------

    def get_type(self):
        """Returns the type of the Reference."""
        return self.__type

    # ------------------------------------------------------------------------

    def set_type(self, ann_type):
        """Set the type of the Reference within the authorized ones.

        :param ann_type: (int) One of the annots.types
        :raise: sppasIndexError, sppasTypeError

        """
        if ann_type in annots.types:
            self.__type = ann_type
        else:
            try:
                ref_index = int(ann_type)
                if ref_index in range(0, len(annots.types)):
                    self.__type = annots.types[ref_index]
                else:
                    raise sppasIndexError(ref_index)
            except:
                raise sppasTypeError(ann_type, annots.types)

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __len__(self):
        return len(self.__attributs)

    def __str__(self):
        return '{:s}: {!s:s}'.format(self.id, self.__attributs)

    def __repr__(self):
        return '{:s}: {!s:s}'.format(self.id, self.__attributs)

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    def __iter__(self):
        for att in self.__attributs:
            yield att

    def __contains__(self, att):
        """Return true if self contains the given attribute/identifier.

        :param att: (str or sppasRefAttribute)

        """
        if isinstance(att, sppasRefAttribute) is False:
            try:
                att = sppasRefAttribute(att)
            except:
                return False

        for a in self.__attributs:
            # if a is identifier:
            #     return True
            if a.get_id() == att.get_id():
                return True

        return False
