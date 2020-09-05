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

    anndata.annotation.py
    ~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import warnings

from sppas.src.anndata.anndataexc import AnnDataTypeError
from sppas.src.anndata.metadata import sppasMetaData

from .annlabel import sppasTag
from .annlabel import sppasLabel
from .annlocation import sppasLocation
from .annlabel import sppasTagCompare

# ----------------------------------------------------------------------------


class sppasAnnotation(sppasMetaData):
    """Represents an annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A sppasAnnotation() is defined as a container for:

        - a sppasLocation()
        - a list of sppasLabel()

    :Example:

        >>> location = sppasLocation(sppasPoint(1.5, radius=0.01))
        >>> labels = sppasLabel(sppasTag("foo"))
        >>> ann = sppasAnnotation(location, labels)

    """

    def __init__(self, location, labels=list()):
        """Create a new sppasAnnotation instance.

        :param location: (sppasLocation) the location(s) where the annotation\
        happens
        :param labels: (sppasLabel, list) the label(s) to stamp this\
        annotation, or a list of them.

        """
        super(sppasAnnotation, self).__init__()

        # Check location instance.
        if isinstance(location, sppasLocation) is False:
            raise AnnDataTypeError(location, "sppasLocation")

        self.__parent = None
        self.__location = location
        self.__labels = list()
        self.__score = None
        self.set_labels(labels)

    # -----------------------------------------------------------------------
    # Member getters
    # -----------------------------------------------------------------------

    def get_parent(self):
        """Return the parent tier or None."""
        return self.__parent

    # -----------------------------------------------------------------------

    def get_score(self):
        """Return the score of this annotation or None if no score is set."""
        return self.__score

    # -----------------------------------------------------------------------

    def get_location(self):
        """Return the sppasLocation() of this annotation."""
        return self.__location

    # -----------------------------------------------------------------------

    def get_labels(self):
        """Return the list of sppasLabel() of this annotation."""
        return self.__labels

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a full copy of the annotation.

        The location, the labels and the metadata are all copied. The 'id'
        of the returned annotation is then the same.

        :returns: sppasAnnotation()

        """
        # Create a copy of the location/labels
        location = self.__location.copy()
        labels = list()
        for l in self.__labels:
            labels.append(l.copy())

        # Create the new Annotation
        other = sppasAnnotation(location, labels)
        other.set_parent(self.__parent)
        other.set_score(self.__score)

        # Copy all metadata, including the 'id'.
        for key in self.get_meta_keys():
            other.set_meta(key, self.get_meta(key))

        return other

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_parent(self, parent=None):
        """Set a parent tier.

        :param parent: (sppasTier) The parent tier of this annotation.
        :raises: CtrlVocabContainsError, HierarchyContainsError, \
        HierarchyTypeError

        """
        if parent is not None:
            parent.validate_annotation_location(self.__location)
            for label in self.__labels:
                parent.validate_annotation_label(label)

        self.__parent = parent

    # -----------------------------------------------------------------------

    def set_score(self, score=None):
        """Set or reset the score to this annotation.

        :param score: (float)

        """
        if score is not None:
            try:
                self.__score = float(score)
            except ValueError:
                raise AnnDataTypeError(score, "float")
        else:
            self.__score = None

    # -----------------------------------------------------------------------

    def set_labels(self, labels=[]):
        """Fix/reset the list of labels of this annotation.

        :param labels: (sppasLabel, list) the label(s) to stamp this \
        annotation, or a list of them.
        :raises: AnnDataTypeError, TypeError, CtrlVocabContainsError, \
        HierarchyContainsError, HierarchyTypeError

        """
        self.__labels = list()
        if labels is None:
            return

        if isinstance(labels, sppasLabel) is True:
            self.validate_label(labels)
            self.__labels.append(labels)

        elif isinstance(labels, list) is True:
            for label in labels:
                if label is not None:
                    self.validate_label(label)
                    self.__labels.append(label)
        else:
            raise AnnDataTypeError(labels, "sppasLabel/list")

    # -----------------------------------------------------------------------

    def validate(self):
        """Validate the annotation.

        Check if the labels and location match the requirements.

        :raises: TypeError, CtrlVocabContainsError, HierarchyContainsError, \
        HierarchyTypeError

        """
        for label in self.__labels:
            self.validate_label(label)
        if self.__parent is not None:
            self.__parent.validate_annotation_location(self.__location)

    # -----------------------------------------------------------------------

    def validate_label(self, label):
        """Validate the label.

        Check if the label matches the requirements of this annotation.

        :raises: CtrlVocabContainsError, TypeError

        """
        if label is None:
            return

        if isinstance(label, sppasLabel) is False:
            raise AnnDataTypeError(label, "sppasLabel")

        if len(self.__labels) > 0:
            current_type = set(l.get_type()
                               for l in self.__labels if l is not None)
            if len(current_type) > 0 and label.get_type() not in current_type:
                raise TypeError()

        if self.__parent is not None:
            self.__parent.validate_annotation_label(label)

    # -----------------------------------------------------------------------
    # Labels
    # -----------------------------------------------------------------------

    def is_labelled(self):
        """Return True if at least a sppasTag exists and is not None."""
        if len(self.__labels) == 0:
            return False

        for label in self.__labels:
            if label is not None:
                if label.is_tagged() is True:
                    return True

        return False

    # -----------------------------------------------------------------------

    def get_label_type(self):
        """Return the current type of tags, or an empty string."""
        if len(self.__labels) == 0:
            return ""

        for label in self.__labels:
            if label is not None:
                if label.is_tagged() is True:
                    return label.get_type()

        return ""

    # -----------------------------------------------------------------------

    def append_label(self, label):
        """Append a label into the list of labels.

        :param label: (sppasLabel)

        """
        self.validate_label(label)
        self.__labels.append(label)

    # -----------------------------------------------------------------------

    def get_labels_best_tag(self):
        """Return a list with the best tag of each label."""
        tags = list()
        for label in self.__labels:
            best = label.get_best()
            if best is not None:
                tags.append(best)
            else:
                tags.append(sppasTag(''))

        return tags

    # -----------------------------------------------------------------------

    def get_best_tag(self, label_idx=0):
        """Return the tag with the highest score of a label or an empty str.

        :param label_idx: (int)

        """
        # No label defined
        if len(self.__labels) == 0:
            return sppasTag("")

        try:
            label = self.__labels[label_idx]
        except IndexError:
            raise IndexError('Invalid label index')

        if label is None:
            return sppasTag('')

        best = label.get_best()
        if best is not None:
            return best
        return sppasTag("")

    # -----------------------------------------------------------------------

    def add_tag(self, tag, score=None, label_idx=0):
        """Append an alternative tag in a label.

        :param tag: (sppasTag)
        :param score: (float)
        :param label_idx: (int)
        :raises: AnnDataTypeError, IndexError

        """
        # No label previously defined
        if len(self.__labels) == 0:
            label = sppasLabel(tag, score)
            self.__labels.append(label)
        else:
            try:
                label = self.__labels[label_idx]
                if label is None:
                    label = sppasLabel(tag, score)
                else:
                    label.append(tag, score)
            except IndexError:
                raise IndexError('Invalid label index')

        # tag, score were added. Now, validate.
        try:
            self.validate_label(label)
        except:
            # restore
            label.remove(tag)
            raise

    # -----------------------------------------------------------------------

    def remove_tag(self, tag, label_idx=0):
        """Remove an alternative tag of the label.

        :param tag: (sppasTag) the tag to be removed of the list.
        :param label_idx: (int)

        """
        try:
            label = self.__labels[label_idx]
        except IndexError:
            raise IndexError('Invalid label index')

        label.remove(tag)

    # -----------------------------------------------------------------------

    def contains_tag(self, tag, function='exact', reverse=False, label_idx=0):
        """Return True if the given tag is in the label.

        :param tag: (sppasTag)
        :param function: Search function
        :param reverse: Reverse the function.
        :param label_idx: (int)

        """
        # No label defined
        if len(self.__labels) == 0:
            return False

        try:
            label = self.__labels[label_idx]
        except IndexError:
            raise IndexError('Invalid label index')

        if label is None:
            return False
        if label.is_tagged() is False:
            return False

        t = sppasTagCompare()
        tag_functions = list()
        tag_functions.append((t.get(function), tag.get_typed_content(), reverse))
        r = label.match(tag_functions)
        if reverse is False:
            return r

        return not r

    # -----------------------------------------------------------------------

    def label_is_filled(self):
        """Return True if at least one BEST tag is filled."""
        for label in self.__labels:
            if label is not None:
                if label.is_tagged() is True:
                    if label.get_best().get_content() != "":
                        return True
        return False

    # -----------------------------------------------------------------------

    def label_is_string(self):
        """Return True if the type of the labels is 'str'."""
        if len(self.__labels) == 0:
            return False

        for label in self.__labels:
            if label.is_tagged() is True:
                return label.is_string()

        return False

    # -----------------------------------------------------------------------

    def label_is_float(self):
        """Return True if the type of the labels is 'float'."""
        if len(self.__labels) == 0:
            return False

        for label in self.__labels:
            if label.is_tagged() is True:
                return label.is_float()

        return False
    # -----------------------------------------------------------------------

    def label_is_int(self):
        """Return True if the type of the labels is 'int'."""
        if len(self.__labels) == 0:
            return False

        for label in self.__labels:
            if label.is_tagged() is True:
                return label.is_int()

        return False

    # -----------------------------------------------------------------------

    def label_is_bool(self):
        """Return True if the type of the labels is 'bool'."""
        if len(self.__labels) == 0:
            return False

        for label in self.__labels:
            if label.is_tagged() is True:
                return label.is_bool()

        return False

    # -----------------------------------------------------------------------

    def serialize_labels(self, separator="\n", empty="", alt=True):
        """DEPRECATED. Return labels serialized into a string.

        TODO: REMOVE THIS METHOD. Use aioutils.serialize_labels() instead.

        :param separator: (str) String to separate labels.
        :param empty: (str) The text to return if a tag is empty or not set.
        :param alt: (bool) Include alternative tags
        :returns: (str)

        """
        warnings.warn("Use serialize_labels(ann.get_labels()) of aioutils package instead",
                      DeprecationWarning)

        if len(self.__labels) == 0:
            return empty

        if len(self.__labels) == 1:
            return self.__labels[0].serialize(empty, alt)

        c = list()
        for label in self.__labels:
            c.append(label.serialize(empty, alt))

        return separator.join(c)

    # -----------------------------------------------------------------------
    # Localization
    # -----------------------------------------------------------------------

    def set_best_localization(self, localization):
        """Set the best localization of the location.

        :param localization: (sppasBaseLocalization)

        """
        old_loc = self.__location.get_best().copy()
        self.__location.get_best().set(localization)
        if self.__parent is not None:
            try:
                self.__parent.validate_annotation_location(self.__location)
            except Exception:
                self.__location.get_best().set(old_loc)
                raise

    # -----------------------------------------------------------------------

    def location_is_point(self):
        """Return True if the location is made of sppasPoint locs."""
        return self.__location.is_point()

    # -----------------------------------------------------------------------

    def location_is_interval(self):
        """Return True if the location is made of sppasInterval locs."""
        return self.__location.is_interval()

    # -----------------------------------------------------------------------

    def location_is_disjoint(self):
        """Return True if the location is made of sppasDisjoint locs."""
        return self.__location.is_disjoint()

    # -----------------------------------------------------------------------

    def get_highest_localization(self):
        """Return a copy of the sppasPoint with the highest loc."""
        return self.__location.get_highest_localization()

    # -----------------------------------------------------------------------

    def get_lowest_localization(self):
        """Return a copy of the sppasPoint with the lowest localization."""
        return self.__location.get_lowest_localization()

    # -----------------------------------------------------------------------

    def get_all_points(self):
        """Return the list of a copy of all points of this annotation."""
        points = list()

        if self.__location.is_point():
            for localization, score in self.__location:
                points.append(localization.copy())

        elif self.__location.is_interval():
            for localization, score in self.__location:
                points.append(localization.get_begin().copy())
                points.append(localization.get_end().copy())

        elif self.__location.is_disjoint():
            for localization, score in self.__location:
                for interval in localization.get_intervals():
                    points.append(interval.get_begin().copy())
                    points.append(interval.get_end().copy())

        return points

    # -----------------------------------------------------------------------

    def contains_localization(self, localization):
        """Return True if the given localization is in the location."""
        return self.__location.contains(localization)

    # -----------------------------------------------------------------------

    def validate_location(self):
        """Validate the location of the annotation.

        :raises: 

        """
        if self.__parent is not None:
            self.__parent.validate_annotation_location(self.__location)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Annotation {:s}: {:s} {:s}".format(self.get_meta('id'),
                                                   str(self.__location),
                                                   str(self.__labels))

    # -----------------------------------------------------------------------

    def __str__(self):
        return "{:s} {:s} {:s}".format(self.get_meta('id'),
                                       str(self.__location),
                                       str(self.__labels))

    # -----------------------------------------------------------------------

    def __hash__(self):
        # use the hashcode of self identifier since that is used
        # for equality checks as well, like "ann in my_dict".
        # not required by Python 2.7 but necessary for Python 3.4+
        return hash(self.get_id())

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, sppasAnnotation) is False:
            return False

        if self.__score != other.get_score():
            return False

        if self.__location != other.get_location():
            return False

        if len(self.__labels) != len(other.get_labels()):
            return False

        for label1, label2 in zip(self.__labels, other.get_labels()):
            if label1 != label2:
                return False

        return True

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        return not self == other
