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

    anndata.hierarchy.py
    ~~~~~~~~~~~~~~~~~~~~

"""

from collections import OrderedDict

from .anndataexc import AnnDataTypeError
from .anndataexc import HierarchyAlignmentError
from .anndataexc import HierarchyAssociationError
from .anndataexc import HierarchyParentTierError
from .anndataexc import HierarchyChildTierError
from .anndataexc import HierarchyAncestorTierError
from .metadata import sppasMetaData

# ----------------------------------------------------------------------------


class sppasHierarchy(sppasMetaData):
    """Generic representation of a hierarchy between tiers.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    
    Two types of hierarchy are considered:

      - TimeAssociation:
        the points of a child tier are all equals to the points of
        a reference tier, as for example:

            | parent:  Words      | l' |  âne  | est  |  là   |
            | child:   Lemmas     | le |  âne  | être |  là  |

      - TimeAlignment:
        the points of a child tier are all included in the set of
        points of a reference tier, as for example:

            | parent: Phonemes    | l  | a | n |  e  | l | a |
            | child:  Words       | l' |  âne  | est |  là   |
            |
            | parent: Phonemes    | l  | a | n |  e  | l | a |
            | child:  Syllables   |   l.a  |  n.e    |   l.a |

    In that example, notice that there's no hierarchy link between
    "Tokens" and "Syllables" and notice that "Phonemes" is the
    grand-parent of "Lemmas".

    And the following obvious rules are applied:

        - A child can have ONLY ONE parent!
        - A parent can have as many children as wanted.
        - A hierarchy is a tree, not a graph.

    Todo is to consider a time association that is not fully completed:

            | parent:  Tokens | l' |  âne  | euh | euh | est  |  là   | @ |
            | child:   Lemmas | le |  âne  |           | être |  là  |

    """
    types = {"TimeAssociation", "TimeAlignment"}

    def __init__(self):
        """Create a new sppasHierarchy instance."""
        super(sppasHierarchy, self).__init__()

        # key = child tier ; value = tuple(parent, link_type)
        self.__hierarchy = OrderedDict()

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_parent(self, child_tier):
        """Return the parent tier for a given child tier.

        :param child_tier: (sppasTier) The child tier to found

        """
        if child_tier not in self.__hierarchy.keys():
            return None

        parent, link = self.__hierarchy[child_tier]
        return parent

    # -----------------------------------------------------------------------

    def get_hierarchy_type(self, child_tier):
        """Return the hierarchy type between a child tier and its parent.

        :returns: (str) one of the hierarchy type

        """
        if child_tier not in self.__hierarchy.keys():
            return ""

        parent, link = self.__hierarchy[child_tier]
        return link

    # -----------------------------------------------------------------------

    def get_children(self, parent_tier, link_type=None):
        """Return the list of children of a tier, for a given type.

        :param parent_tier: (sppasTier) The child tier to found
        :param link_type: (str) The type of hierarchy
        :returns: List of tiers

        """
        if link_type is not None:
            if link_type not in sppasHierarchy.types:
                raise AnnDataTypeError(link_type, 
                                       "TimeAssociation, TimeAlignment")

        children = []
        for child_tier in self.__hierarchy.keys():
            parent, link = self.__hierarchy[child_tier]
            if parent is parent_tier:
                if link_type is None or link_type == link:
                    children.append(child_tier)

        return children

    # -----------------------------------------------------------------------

    def get_ancestors(self, child_tier):
        """Return all the direct ancestors of a tier.

        :param child_tier: (sppasTier)
        :returns: List of tiers with parent, grand-parent, grand-grand-parent...

        """
        if child_tier not in self.__hierarchy.keys():
            return []

        ancestors = []
        parent = self.get_parent(child_tier)
        while parent is not None:
            ancestors.append(parent)
            parent = self.get_parent(parent)

        return ancestors

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @staticmethod
    def validate_time_alignment(parent_tier, child_tier):
        """Validate a time alignment hierarchy link between 2 tiers.

        :param parent_tier: (sppasTier) The parent tier
        :param child_tier: (sppasTier) The child tier to be linked to parent
        :raises: HierarchyAlignmentError

        """
        if parent_tier.is_superset(child_tier) is False:
            raise HierarchyAlignmentError(parent_tier.get_name(),
                                          child_tier.get_name())

    # -----------------------------------------------------------------------

    @staticmethod
    def validate_time_association(parent_tier, child_tier):
        """Validate a time association hierarchy link between 2 tiers.

        :param parent_tier: (sppasTier) The parent tier
        :param child_tier: (sppasTier) The child tier to be linked to the parent
        :raises: HierarchyAssociationError

        """
        if parent_tier.is_superset(child_tier) is False and \
           child_tier.is_superset(parent_tier) is False:
            raise HierarchyAssociationError(parent_tier.get_name(),
                                            child_tier.get_name())

    # -----------------------------------------------------------------------

    def validate_link(self, link_type, parent_tier, child_tier):
        """Validate a hierarchy link between 2 tiers.

        :param link_type: (constant) One of the hierarchy types
        :param parent_tier: (sppasTier) The parent tier
        :param child_tier: (sppasTier) The child tier to be linked to parent
        :raises: AnnDataTypeError, HierarchyParentTierError, \
        HierarchyChildTierError, HierarchyAncestorTierError, \
        HierarchyAlignmentError, HierarchyAssociationError

        """
        if link_type not in sppasHierarchy.types:
            raise AnnDataTypeError(link_type, "TimeAssociation, TimeAlignment")

        # A child has only one parent
        if child_tier in self.__hierarchy.keys():
            parent, link = self.__hierarchy[child_tier]
            raise HierarchyParentTierError(child_tier.get_name(),
                                           link,
                                           parent.get_name())

        # A tier can't be its own child/parent
        if parent_tier == child_tier:
            raise HierarchyChildTierError(child_tier.get_name())

        # Check for TimeAlignment
        if link_type == "TimeAlignment":
            sppasHierarchy.validate_time_alignment(parent_tier,
                                                   child_tier)

        # Check for TimeAssociation
        if link_type == "TimeAssociation":
            sppasHierarchy.validate_time_association(parent_tier,
                                                     child_tier)

        # No circular hierarchy allowed.
        ancestors = self.get_ancestors(parent_tier)
        family = []
        for ancestor in ancestors:
            uncles = self.get_children(ancestor)
            family.extend(uncles)
        family.extend(ancestors)
        if child_tier in family:
            raise HierarchyAncestorTierError(child_tier.get_name(),
                                             parent_tier.get_name())

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def add_link(self, link_type, parent_tier, child_tier):
        """Validate and add a hierarchy link between 2 tiers.

        :param link_type: (constant) One of the hierarchy types
        :param parent_tier: (sppasTier) The parent tier
        :param child_tier: (sppasTier) The child tier to be linked to parent

        """
        self.validate_link(link_type, parent_tier, child_tier)
        self.__hierarchy[child_tier] = (parent_tier, link_type)

    # -----------------------------------------------------------------------

    def remove_child(self, child_tier):
        """Remove a hierarchy link between a parent and a child.

        :param child_tier: (sppasTier) The tier linked to a reference

        """
        if child_tier in self.__hierarchy.keys():
            del self.__hierarchy[child_tier]

    # -----------------------------------------------------------------------

    def remove_parent(self, parent_tier):
        """Remove all hierarchy links between a parent and its children.

        :param parent_tier: (sppasTier) The parent tier

        """
        to_remove = []
        for child_tier in self.__hierarchy.keys():
            parent, link = self.__hierarchy[child_tier]
            if parent is parent_tier:
                to_remove.append(child_tier)

        for child_tier in to_remove:
            del self.__hierarchy[child_tier]

    # -----------------------------------------------------------------------

    def remove_tier(self, tier):
        """Remove all occurrences of a tier inside the hierarchy.

        :param tier: (sppasTier) The tier to remove as parent or child.

        """
        to_remove = []
        for child in self.__hierarchy.keys():
            parent, link = self.__hierarchy[child]
            if parent is tier or child is tier:
                to_remove.append(child)

        for child_tier in to_remove:
            del self.__hierarchy[child_tier]

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of the hierarchy."""
        h = sppasHierarchy()

        for child_tier in self.__hierarchy:
            parent_tier = self.__hierarchy[child_tier][0]
            link_type = self.__hierarchy[child_tier][1]
            h.add_link(link_type, parent_tier, child_tier)

        return h

    # -----------------------------------------------------------------------
    # Automatic hierarchy
    # -----------------------------------------------------------------------

    @staticmethod
    def infer_hierarchy_type(tier1, tier2):
        """Test if tier1 can be a parent tier for tier2.

        :returns: One of hierarchy types or an empty string

        """
        if tier1.is_superset(tier2) is False:
            return ""

        if tier2.is_superset(tier1) is True:
            return "TimeAssociation"

        return "TimeAlignment"

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __len__(self):
        return len(self.__hierarchy)

    def __iter__(self):
        for a in self.__hierarchy:
            yield a
