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

    src.files.fileref.py
    ~~~~~~~~~~~~~~~~~~~~

"""

from sppas import sppasTypeError, sppasIndexError
from sppas import annots
from sppas.src.utils.makeunicode import sppasUnicode
from .filebase import FileBase, States


# ---------------------------------------------------------------------------


class sppasAttribute(object):
    """Represent any attribute with an id, a value, and a description.

    :author:       Barthélémy Drabczuk, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This class embeds an id, a value, its type and a description.

    """

    VALUE_TYPES = ('str', 'int', 'float', 'bool')

    def __init__(self, identifier, value=None, att_type=None, descr=None):
        """Constructor of sppasAttribute.

        :param identifier: (str) The identifier of the attribute
        :param value: (str) String representing the value of the attribute
        :param att_type: (str) One of the VALUE_TYPES
        :param descr: (str) A string to describe what the attribute is

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
        """Return True the given identifier matches the requirements.

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

        if sppasAttribute.validate(identifier) is False:
            raise ValueError(
                "Identifier '{:s}' is not valid. It should be between 2 "
                "and 12 ASCII-characters.".format(identifier))

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

        """
        if type_name in sppasAttribute.VALUE_TYPES:
            self.__valuetype = type_name
        elif type_name is None:
            self.__valuetype = 'str'
        else:
            raise sppasTypeError(type_name, " ".join(sppasAttribute.VALUE_TYPES))

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
                raise
                # TODO: raise sppas Exception with appropriate msg

        return self.__value

    # -----------------------------------------------------------------------

    def get_description(self):
        """Return current description.

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

    # -----------------------------------------------------------------------

    def serialize(self):
        """Return a dict representing this instance for json format."""
        d = dict()
        d['id'] = self.__id
        d['value'] = self.__value
        d['type'] = self.__valuetype
        d['descr'] = self.__descr
        return d

    # -----------------------------------------------------------------------

    @staticmethod
    def parse(d):
        """Return the sppasAttribute from the given dict.

        :param d: (dict) 'id' required. optional: 'value', 'type', 'descr'

        """
        k = d['id']
        v = d.get('value', None)
        t = d.get('type', sppasAttribute.VALUE_TYPES[0])
        descr = d.get('descr', None)

        return sppasAttribute(k, v, t, descr)

    # ---------------------------------------------------------
    # overloads
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

# ---------------------------------------------------------------------------


class FileReference(FileBase):
    """Represent a reference of a catalog about files.

    :author:       Barthélémy Drabczuk, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Reference is a dictionary with a name. Its keys are only alphanumerics characters
    spaced with underscores and its values are all sppasAttribute objects.

    """

    def __init__(self, identifier):
        """Constructor of the FileReference class.

        :param identifier: (str) identifier for the object, the name of the reference

        """
        super(FileReference, self).__init__(identifier)

        self.__attributs = list()
        self.__type = annots.types[0]

        # A free to use member to expand the class
        self.subjoined = None

    # ------------------------------------------------------------------------

    def att(self, identifier):
        """Return the attribute matching the given identifier or None.

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

        """
        self.append(sppasAttribute(identifier, value, att_type, descr))

    # ------------------------------------------------------------------------

    def append(self, att):
        """Add an attribute.

        :param att: (sppasAttribute)

        """
        if isinstance(att, sppasAttribute) is False:
            raise sppasTypeError(att, "sppasAttribute")

        if att in self:
            raise KeyError("The identifier '{:s}' is already existing in the "
                           "reference '{:s}'.".format(att.get_id(), self.id))

        self.__attributs.append(att)

    # ------------------------------------------------------------------------

    def pop(self, identifier):
        """Delete an attribute of this reference.

        :param identifier: (str, sppasAttribute) the id of the attribute to delete

        """
        if identifier in self:
            if isinstance(identifier, sppasAttribute) is False:
                identifier = self.att(identifier)
            self.__attributs.remove(identifier)
        else:
            raise ValueError('{:s} is not a valid identifier for {:s}'
                             ''.format(identifier, self.id))

    # ------------------------------------------------------------------------

    def set_state(self, state):
        """Set the current state to a new one.

        :param state: (Reference.States)
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
        """Set the type of the Reference within the authorized ones."""
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

    # -----------------------------------------------------------------------

    def serialize(self):
        """Return a dict representing this instance for json format."""
        d = FileBase.serialize(self)
        d['type'] = self.__type
        d['attributes'] = list()
        for att in self.__attributs:
            a = att.serialize()
            d['attributes'].append(a)
        d['subjoin'] = self.subjoined
        return d

    # -----------------------------------------------------------------------

    @staticmethod
    def parse(d):
        """Return the FileReference instance represented by the given dict.

        """
        if 'id' not in d:
            raise KeyError("Reference 'id' is missing of the dictionary to parse.")

        ref = FileReference(d['id'])

        # Parse the type of reference
        if 'type' in d:
            ref.set_type(d['type'])

        # Parse the list of attributes
        if 'attributes' in d:
            for att_dict in d['attributes']:
                ref.append(sppasAttribute.parse(att_dict))

        # Parse the state value
        s = d.get('state', States().UNUSED)
        if s > 0:
            ref.set_state(States().CHECKED)
        else:
            ref.set_state(States().UNUSED)

        # Parse the subjoined member, "as it"!
        ref.subjoined = d['subjoin']

        return ref

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

        :param att: (str or sppasAttribute)

        """
        if isinstance(att, sppasAttribute) is False:
            try:
                att = sppasAttribute(att)
            except:
                return False

        for a in self.__attributs:
            # if a is identifier:
            #     return True
            if a.get_id() == att.get_id():
                return True

        return False
