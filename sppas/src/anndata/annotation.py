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

    src.anndata.annotation.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import copy

from .anndataexc import AnnDataTypeError
from .annlabel.label import sppasLabel
from .annlocation.location import sppasLocation
from .metadata import sppasMetaData

# ----------------------------------------------------------------------------


class sppasAnnotation(sppasMetaData):
    """
    :author:       Brigitte Bigi, Jibril Saffi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Represents an annotation.

    A sppasAnnotation() is a container for:
        - a sppasLocation()
        - a sppasLabel()

    >>> location = sppasLocation(sppasTimePoint(1.5, radius=0.01))
    >>> label = sppasLabel(sppasText("foo"))
    >>> ann = sppasAnnotation(location, label)
    >>> ann.get_location().get_best().get_point()
    1.5
    >>> ann.get_label().get_best().get_content()
    foo

    """
    def __init__(self, location, label=None):
        """ Creates a new sppasAnnotation instance.

        :param location: (sppasLocation) the location(s) where the annotation happens
        :param label: (sppasLabel) the label(s) to stamp this annotation

        """
        super(sppasAnnotation, self).__init__()

        if isinstance(location, sppasLocation) is False:
            raise AnnDataTypeError(location, "sppasLocation")

        if label is not None:
            if isinstance(label, sppasLabel) is False:
                raise AnnDataTypeError(label, "sppasLabel")

        self.__parent = None
        self.__location = location
        self.__label = label

    # -----------------------------------------------------------------------

    def get_label(self):
        """ Return the sppasLabel instance. """

        if self.__label is not None:
            return self.__label

        return sppasLabel("")

    # -----------------------------------------------------------------------

    def get_location(self):
        """ Return the sppasLocation instance. """

        return self.__location

    # -----------------------------------------------------------------------

    def copy(self):
        """ Return a deep copy of the annotation. """

        return copy.deepcopy(self)

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_parent(self, parent=None):
        """ Set a parent tier.

        :param parent: (sppasTier) The parent tier of this annotation.

        """
        if parent is not None:
            parent.validate_annotation_label(self.__label)
            parent.validate_annotation_location(self.__label)

        self.__parent = parent

    # -----------------------------------------------------------------------

    def set_best_tag(self, tag):
        """ Set the best tag of the label.
        It will replace the tag with the highest score by the given one,
        and do not change the score.

        :param tag: (sppasTag)

        """
        if self.__parent is not None:
            old_tag = self.__label.get_best().copy()
            self.__label.get_best().set(tag)
            try:
                self.__parent.validate_annotation_label(self.__label)
            except Exception:
                self.__label.get_best().set(old_tag)
                raise
        else:
            self.__label.get_best().set(tag)

    # -----------------------------------------------------------------------

    def add_tag(self, tag, score=None):
        """ Append an alternative tag in the label.

        :param tag: (sppasTag)
        :param score: (float)
        :raises: AnnDataTypeError

        """
        self.__label.append(tag, score)
        if self.__parent is not None:
            try:
                self.__parent.validate_annotation_label(self.__label)
            except Exception:
                self.__label.remove(tag)
                raise

    # -----------------------------------------------------------------------

    def remove_tag(self, tag):
        """ Remove an alternative tag of the label.

        :param tag: (sppasTag) the tag to be removed of the list.

        """
        self.__label.remove(tag)

    # -----------------------------------------------------------------------

    def set_best_localization(self, localization):
        """ Set the best localization of the location.

        :param localization: (sppasBaseLocalization)

        """
        old_loc = self.__location.get_best()
        self.__location.get_best().set(localization)
        if self.__parent is not None:
            try:
                self.__parent.validate_annotation_location(self.__location)
            except ValueError:
                self.__location.get_best().set(old_loc)
                raise

    # -----------------------------------------------------------------------

    def location_is_point(self):
        """ Return True if the location is made of sppasPoint localizations. """

        return self.__location.is_point()

    # -----------------------------------------------------------------------

    def location_is_interval(self):
        """ Return True if the location is made of sppasInterval localizations. """

        return self.__location.is_interval()

    # -----------------------------------------------------------------------

    def location_is_disjoint(self):
        """ Return True if the location is made of sppasDisjoint localizations. """

        return self.__location.is_disjoint()

    # -----------------------------------------------------------------------

    def get_highest_localization(self):
        """ Return the sppasPoint with the highest localization. """

        if self.location_is_point():
            return max([l for l in self.__location])
        return max([l.get_end() for l in self.__location])

    # -----------------------------------------------------------------------

    def get_lowest_localization(self):
        """ Return the sppasPoint with the lowest localization. """

        if self.location_is_point():
            return min([l for l in self.__location])
        return min([l.get_begin() for l in self.__location])

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Annotation: {:s} {:s}".format(self.__location, self.__label)

    def __str__(self):
        return "{:s} {:s}".format(self.__location, self.__label)
