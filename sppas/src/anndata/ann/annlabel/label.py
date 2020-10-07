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

    anndata.ann.annlabel.label.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import copy

from ...anndataexc import AnnDataTypeError
from .tag import sppasTag

# ----------------------------------------------------------------------------


class sppasLabel(object):
    """Represent the content of an annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    
    sppasLabel allows to store a set of sppasTags with their scores.
    This class is using a list of lists, i.e. a list of pairs (tag, score).
    This is the best compromise between memory usage, speed and
    readability. 

    A label is a list of possible sppasTag(), represented as a UNICODE 
    string. A data type can be associated, as sppasTag() can be 'int', 
    'float' or 'bool'.

    """

    def __init__(self, tag, score=None):
        """Create a new sppasLabel instance.

        :param tag: (sppasTag or list of sppasTag or None)
        :param score: (float or list of float or None)

        """
        self.__tags = None

        if tag is not None:
            if isinstance(tag, list):
                if isinstance(score, list) and len(tag) == len(score):
                    for t, s in zip(tag, score):
                        self.append(t, s)
                else:
                    # scores are ignored
                    for t in tag:
                        self.append(t)
            else:
                if isinstance(score, list):
                    score = None
                self.append(tag, score)

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def append_content(self, content, data_type="str", score=None):
        """Add a text into the list.

        :param content: (str)
        :param data_type: (str): The type of this text content.\ 
        One of: (str, int, float, bool)
        :param score: (float)

        """
        tag = sppasTag(content, data_type)
        self.append(tag, score)

    # -----------------------------------------------------------------------

    def append(self, tag, score=None):
        """Add a sppasTag into the list.

        Do not add the tag if this alternative is already inside the list,
        but add the scores.

        :param tag: (sppasTag)
        :param score: (float)

        """
        if not isinstance(tag, sppasTag):
            raise AnnDataTypeError(tag, "sppasTag")

        if self.__tags is None:
            self.__tags = list()

        # check types consistency.
        if len(self.__tags) > 0:
            if self.__tags[0][0].get_type() != tag.get_type():
                raise AnnDataTypeError(tag, self.__tags[0][0].get_type())

        # check if this tag content is already in the list
        for i in range(len(self.__tags)):
            current_tag, current_score = self.__tags[i]
            if tag.get_typed_content() == current_tag.get_typed_content():
                if score is not None:
                    if current_score is None:
                        self.__tags[i][1] = score
                    else:
                        self.__tags[i][1] += score
                return False

        self.__tags.append([tag, score])
        return True

    # -----------------------------------------------------------------------

    def remove(self, tag):
        """Remove a tag of the list.

        :param tag: (sppasTag) the tag to be removed of the list.

        """
        if not isinstance(tag, sppasTag):
            raise AnnDataTypeError(tag, "sppasTag")

        if self.__tags is not None:
            if len(self.__tags) == 1:
                self.__tags = None
            else:
                for t in self.__tags:
                    if t[0] == tag:
                        self.__tags.remove(t)

    # -----------------------------------------------------------------------

    def get_score(self, tag):
        """Return the score of a tag or None if tag is not in the label.

        :param tag: (sppasTag)
        :returns: score: (float)

        """
        if not isinstance(tag, sppasTag):
            raise AnnDataTypeError(tag, "sppasTag")

        if self.__tags is not None:
            for t in self.__tags:
                if t[0] == tag:
                    return t[1]

        return None

    # -----------------------------------------------------------------------

    def set_score(self, tag, score):
        """Set a score to a given tag.

        :param tag: (sppasTag)
        :param score: (float)

        """
        if not isinstance(tag, sppasTag):
            raise AnnDataTypeError(tag, "sppasTag")

        if self.__tags is not None:
            for i, t in enumerate(self.__tags):
                if t[0] == tag:
                    self.__tags[i][1] = score

    # -----------------------------------------------------------------------

    def get_best(self):
        """Return the best sppasTag, i.e. the one with the better score.

        :returns: (sppasTag or None)

        """
        if self.__tags is None:
            return None

        if len(self.__tags) == 1:
            return self.__tags[0][0]

        _max_tag = self.__tags[0][0]
        _max_score = self.__tags[0][1]
        for (t, s) in reversed(self.__tags):
            if _max_score is None or (s is not None and s > _max_score):
                _max_score = s
                _max_tag = t

        return _max_tag

    # -----------------------------------------------------------------------

    def get_type(self):
        """Return the type of the tags content."""
        if self.__tags is None:
            return "str"

        return self.__tags[0][0].get_type()

    # -----------------------------------------------------------------------

    def is_tagged(self):
        """Return False if no tag is set."""
        if self.__tags is None:
            return False
        if len(self.__tags) == 0:
            return False

        return True

    # -----------------------------------------------------------------------

    def is_string(self):
        """Return True if tags are string or unicode.

        Return False if no tag is set.

        """
        if self.is_tagged() is False:
            return False
        return self.__tags[0][0].get_type() == "str"

    # -----------------------------------------------------------------------

    def is_float(self):
        """Return True if tags are of type "float".

        Return False if no tag is set.

        """
        if self.is_tagged() is False:
            return False
        return self.__tags[0][0].get_type() == "float"

    # -----------------------------------------------------------------------

    def is_int(self):
        """Return True if tags are of type "int".

        Return False if no tag is set.

        """
        if self.is_tagged() is False:
            return False
        return self.__tags[0][0].get_type() == "int"

    # -----------------------------------------------------------------------

    def is_bool(self):
        """Return True if tags are of type "bool".

        Return False if no tag is set.

        """
        if self.is_tagged() is False:
            return False
        return self.__tags[0][0].get_type() == "bool"

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of the label."""
        return copy.deepcopy(self)

    # -----------------------------------------------------------------------

    def match(self, tag_functions, logic_bool="and"):
        """Return True if a tag matches all or any of the functions.

        :param tag_functions: list of (function, value, logical_not)
        :param logic_bool: (str) Apply a logical "and" or a logical "or" \
        between the functions.
        :returns: (bool)

            - function: a function in python with 2 arguments: tag/value
            - value: the expected value for the tag
            - logical_not: boolean

        :Example: Search if a tag is exactly matching "R":

            >>> l.match([(exact, "R", False)])

        :Example: Search if a tag is starting with "p" or starting with "t":

            >>> l.match([(startswith, "p", False),
            >>>          (startswith, "t", False), ], logic_bool="or")

        """
        is_matching = False

        # any tag can match
        for tag, score in self.__tags:

            matches = list()
            for func, value, logical_not in tag_functions:
                if logical_not is True:
                    matches.append(not func(tag, value))
                else:
                    matches.append(func(tag, value))

            if logic_bool == "and":
                is_matching = all(matches)
            else:
                is_matching = any(matches)

            # no need to test the next tags if the current one is matching.
            if is_matching is True:
                return True

        return is_matching

    # -----------------------------------------------------------------------

    def serialize(self, empty="", alt=True):
        """Convert the label into a string, include or not alternative tags.

        @DeprecationWarning
        Use aioutils.serialize_label() instead.

        """
        if self.__tags is None:
            return empty
        if len(self.__tags) == 0:
            return empty
        if self.get_best() is None:
            return empty

        if alt is False or len(self.__tags) == 1:
            best = self.get_best()
            if best.is_empty():
                return empty
            return best.get_content()

        # we store the alternative tags into a list.
        # empty tags are replaced by the empty item.
        tag_contents = list()
        for tag, score in self.__tags:
            content = tag.get_content()
            if len(content) > 0:
                tag_contents.append(content)
            else:
                tag_contents.append(empty)

        return "{" + "|".join(tag_contents) + "}"

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        st = ""
        if self.__tags is not None:
            for t, s in self.__tags:
                st += "sppasTag({!s:s}, score={!s:s}), ".format(t, s)
        return st

    # -----------------------------------------------------------------------

    def __str__(self):
        st = ""
        if self.__tags is not None:
            for t, s in self.__tags:
                st += "{!s:s}, {!s:s} ; ".format(t, s)
        return st

    # -----------------------------------------------------------------------

    def __iter__(self):
        if self.__tags is not None:
            for t in self.__tags:
                yield t

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        if self.__tags is not None:
            return self.__tags[i]
        else:
            raise IndexError(i)

    # -----------------------------------------------------------------------

    def __len__(self):
        if self.__tags is not None:
            return len(self.__tags)
        return 0

    # -----------------------------------------------------------------------

    def __eq__(self, other):

        if self.__tags is not None:
            if other is None:
                return False
            if isinstance(other, sppasLabel) is False:
                return False
            if len(self.__tags) != len(other):
                return False
            for (tag1, tag2) in zip(self.__tags, other):
                # compare the typed content of the tags and
                # also compare the scores...
                if tag1[0] != tag2[0]:
                    return False
                if tag1[1] != tag2[1]:
                    return False
            return True
        else:
            # self and other are both None
            if other is None:
                return True
        return False

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        return not self == other
