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

    anndata.transcription.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from sppas.src.files import sppasGUID
from sppas.src.utils import sppasUnicode

from .anndataexc import AnnDataTypeError
from .anndataexc import TrsAddError
from .anndataexc import TrsRemoveError
from .anndataexc import AnnDataIndexError
from .anndataexc import TierHierarchyError
from .anndataexc import TrsInvalidTierError

from .metadata import sppasMetaData
from .ctrlvocab import sppasCtrlVocab
from .media import sppasMedia
from .tier import sppasTier
from .hierarchy import sppasHierarchy
from .ann.annotation import sppasAnnotation

# ----------------------------------------------------------------------------


class sppasTranscription(sppasMetaData):
    """Representation of a transcription, a structured set of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Transcriptions in SPPAS are represented with:

        - metadata: a list of tuple key/value;
        - a name (used to identify the transcription);
        - a list of tiers;
        - a hierarchy between tiers.

    Inter-tier relations are managed by establishing alignment or association
    links between 2 tiers:

        - alignment: annotations of a tier A (child) have only localization
          instances included in those of annotations of tier B (parent);
        - association: annotations of a tier A have exactly localization
         instances included in those of annotations of tier B.

    :Example:

        >>> # Create an instance
        >>> trs = sppasTranscription("trs name")

        >>> # Create a tier
        >>> trs.create_tier("tier name")

        >>> # Get a tier of a transcription from its index:
        >>> tier = trs[0]

        >>> # Get a tier of a transcription from its name
        >>> tier = trs.find("tier name")

    """

    def __init__(self, name=None):
        """Create a new sppasTranscription instance.

        :param name: (str) Name of the transcription.

        """
        super(sppasTranscription, self).__init__()

        self._name = None
        self._media = list()      # a list of sppasMedia() instances
        self._ctrlvocab = list()  # a list of sppasCtrlVocab() instances
        self._tiers = list()      # a list of sppasTier() instances
        self._hierarchy = sppasHierarchy()

        self.set_name(name)

        # Add metadata about SPPAS, the language and the license.
        self.add_software_metadata()
        self.add_language_metadata()
        self.add_license_metadata(0)

    # ------------------------------------------------------------------------

    def get_object(self, identifier):
        """Return the object matching the given identifier.

        :param identifier: (GUID)

        """
        if self.get_id() == identifier:
            return self

        obj = self.get_tier_from_id(identifier)
        if obj is not None:
            return obj

        obj = self.get_media_from_id(identifier)
        if obj is not None:
            return obj

        obj = self.get_ctrl_vocab_from_id(identifier)
        if obj is not None:
            return obj

        for ann in self._tiers:
            if ann.get_id() == identifier:
                return ann

        return None

    # -----------------------------------------------------------------------
    # Name
    # -----------------------------------------------------------------------

    def get_name(self):
        """Return the name of the transcription."""
        return self._name

    # -----------------------------------------------------------------------

    def set_name(self, name=None):
        """Set the name of the transcription.

        :param name: (str or None) The identifier name or None.
        :returns: the name

        """
        if name is None:
            name = sppasGUID().get()
        su = sppasUnicode(name)
        self._name = su.to_strip()

        return self._name

    # ------------------------------------------------------------------------
    # Media
    # ------------------------------------------------------------------------

    def get_media_list(self):
        """Return the list of sppasMedia."""
        return self._media

    # ------------------------------------------------------------------------

    def get_media_from_id(self, media_id):
        """Return a sppasMedia from its name or None.

        :param media_id: (str) Identifier name of a media

        """
        idt = media_id.strip()
        for m in self._media:
            if m.get_meta('id') == idt:
                return m
        return None

    # ------------------------------------------------------------------------

    def add_media(self, new_media):
        """Add a new media in the list of media.

        Does not add the media if a media with the same id is already in self.

        :param new_media: (sppasMedia) The media to add.
        :raises: AnnDataTypeError, TrsAddError

        """
        if isinstance(new_media, sppasMedia) is False:
            raise AnnDataTypeError(new_media, "sppasMedia")

        ids = [m.get_meta('id') for m in self._media]
        if new_media.get_meta('id') in ids:
            raise TrsAddError(new_media.get_filename(), self._name)

        self._media.append(new_media)

    # ------------------------------------------------------------------------

    def remove_media(self, old_media):
        """Remove a media of the list of media.

        :param old_media: (sppasMedia)
        :raises: AnnDataTypeError, TrsRemoveError

        """
        if not isinstance(old_media, sppasMedia):
            raise AnnDataTypeError(old_media, "sppasMedia")

        if old_media not in self._media:
            raise TrsRemoveError(old_media.get_filename())

        self._media.remove(old_media)
        for tier in self._tiers:
            if tier.get_media() == old_media:
                tier.set_media(None)

    # ------------------------------------------------------------------------

    def set_media_list(self, media_list):
        """Set the list of media.

        :param media_list: (list)
        :returns: list of rejected media

        """
        self._media = list()
        rejected = list()
        for m in media_list:
            try:
                self.add_media(m)
            except Exception:
                rejected.append(m)

        return rejected

    # ------------------------------------------------------------------------
    # Controlled vocabularies
    # ------------------------------------------------------------------------

    def get_ctrl_vocab_list(self):
        """Return the list of controlled vocabularies."""
        return self._ctrlvocab

    # ------------------------------------------------------------------------

    def get_ctrl_vocab_from_name(self, ctrl_vocab_name):
        """Return a sppasCtrlVocab from its name or None.

        :param ctrl_vocab_name: (str) Identifier name of a ctrl vocabulary

        """
        idt = ctrl_vocab_name.strip()
        for c in self._ctrlvocab:
            if c.get_name() == idt:
                return c

        return None

    # ------------------------------------------------------------------------

    def get_ctrl_vocab_from_id(self, ctrl_vocab_id):
        """Return a sppasCtrlVocab from its id or None.

        :param ctrl_vocab_id: (str) Identifier name of a ctrl vocab

        """
        idt = ctrl_vocab_id.strip()
        for m in self._ctrlvocab:
            if m.get_meta('id') == idt:
                return m
        return None

    # ------------------------------------------------------------------------

    def add_ctrl_vocab(self, new_ctrl_vocab):
        """Add a new controlled vocabulary in the list of ctrl vocab.

        :param new_ctrl_vocab: (sppasCtrlVocab)
        :raises: AnnDataTypeError, TrsAddError

        """
        if not isinstance(new_ctrl_vocab, sppasCtrlVocab):
            raise AnnDataTypeError(new_ctrl_vocab, "sppasCtrlVocab")

        ids = [c.get_name() for c in self._ctrlvocab]
        if new_ctrl_vocab.get_name() in ids:
            raise TrsAddError(new_ctrl_vocab.get_name(), self._name)

        self._ctrlvocab.append(new_ctrl_vocab)

    # ------------------------------------------------------------------------

    def remove_ctrl_vocab(self, old_ctrl_vocab):
        """Remove a controlled vocabulary of the list of ctrl vocab.

        :param old_ctrl_vocab: (sppasCtrlVocab)
        :raises: AnnDataTypeError, TrsRemoveError

        """
        if not isinstance(old_ctrl_vocab, sppasCtrlVocab):
            raise AnnDataTypeError(old_ctrl_vocab, "sppasCtrlVocab")

        if old_ctrl_vocab not in self._ctrlvocab:
            raise TrsRemoveError(old_ctrl_vocab.get_name())

        self._ctrlvocab.remove(old_ctrl_vocab)
        for tier in self._tiers:
            if tier.get_ctrl_vocab() == old_ctrl_vocab:
                tier.set_ctrl_vocab(None)

    # ------------------------------------------------------------------------

    def set_ctrl_vocab_list(self, ctrl_vocab_list):
        """Set the list of controlled vocabularies.

        :param ctrl_vocab_list: (list)
        :returns: list of rejected ctrl_vocab

        """
        self._ctrlvocab = list()
        rejected = list()
        for c in ctrl_vocab_list:
            try:
                self.add_ctrl_vocab(c)
            except Exception:
                rejected.append(c)

        return rejected

    # ------------------------------------------------------------------------
    # Hierarchy
    # ------------------------------------------------------------------------

    def add_hierarchy_link(self, link_type, parent_tier, child_tier):
        """Validate and add a hierarchy link between 2 tiers.

        :param link_type: (constant) One of the hierarchy types
        :param parent_tier: (Tier) The reference tier
        :param child_tier: (Tier) The child tier to be linked to reftier

        """
        if parent_tier not in self._tiers:
            raise TrsInvalidTierError(parent_tier.get_name(), self._name)

        if child_tier not in self._tiers:
            raise TrsInvalidTierError(parent_tier.get_name(), self._name)

        self._hierarchy.add_link(link_type, parent_tier, child_tier)

    # -----------------------------------------------------------------------

    def invalidate_annotation_location(self, tier, location):
        """Validate a location in case it is removed.

        The location can't be removed:
            - If tier is a child/parent of a TimeAssociation,
            - If tier is a parent of a TimeAlignment and child has the location

        :param tier: (Tier) The reference tier
        :param location: (sppasLocation)
        :raises: AnnDataTypeError, HierarchyContainsError, HierarchyTypeError

        to be tested.

        """
        # if tier is a child
        parent_tier = self._hierarchy.get_parent(tier)
        if parent_tier is not None:
            link_type = self._hierarchy.get_hierarchy_type(tier)
            if link_type == "TimeAssociation":
                raise TierHierarchyError(tier.get_name())

        else:
            # if current tier is a parent
            for child_tier in self._hierarchy.get_children(tier):
                link_type = self._hierarchy.get_hierarchy_type(child_tier)

                # Ensure the hierarchy will still be valid with children
                if link_type == "TimeAssociation":
                    raise TierHierarchyError(tier.get_name())
                elif link_type == "TimeAlignment":
                    # check if child has an annotation with the same location
                    if child_tier.has_location(location):
                        raise TierHierarchyError(tier.get_name())
                    # check if child has the same localizations and self has no other ones

    # -----------------------------------------------------------------------

    def validate_annotation_location(self, tier, location):
        """Validate a location.

        :param tier: (Tier) The reference tier
        :param location: (sppasLocation)
        :raises: AnnDataTypeError, HierarchyContainsError, HierarchyTypeError

        """
        # if tier is a child
        parent_tier = self._hierarchy.get_parent(tier)
        if parent_tier is not None:
            link_type = self._hierarchy.get_hierarchy_type(tier)

            if link_type == "TimeAssociation":
                sppasHierarchy.validate_time_association(parent_tier, tier)
                # raise TierHierarchyError(tier.get_name())

            # The parent must have such location...
            if link_type == "TimeAlignment":
                # Find annotations in the parent, matching with our location
                if location.is_point():
                    lowest = min([l[0] for l in location])
                    highest = max([l[0] for l in location])
                else:
                    lowest = min([l[0].get_begin() for l in location])
                    highest = max([l[0].get_end() for l in location])
                anns = parent_tier.find(lowest, highest)

                # Check if all localization are matching,
                # so without checking the scores.
                if len(anns) == 0:
                    raise TierHierarchyError(tier.get_name())

                points = list()
                for ann in anns:
                    points.extend(ann.get_all_points())
                a = sppasAnnotation(location)
                find_points = a.get_all_points()
                for point in find_points:
                    if point not in points:
                        raise TierHierarchyError(tier.get_name())

        else:
            # if current tier is a parent
            for child_tier in self._hierarchy.get_children(tier):
                link_type = self._hierarchy.get_hierarchy_type(child_tier)

                # Ensure the hierarchy is still valid with children
                if link_type == "TimeAssociation":
                    sppasHierarchy.validate_time_association(tier, child_tier)
                elif link_type == "TimeAlignment":
                    sppasHierarchy.validate_time_alignment(tier, child_tier)

    # -----------------------------------------------------------------------

    def get_hierarchy(self):
        """Return the hierarchy."""
        return self._hierarchy

    # -----------------------------------------------------------------------

    def validate_hierarchy(self, tier):
        parent_tier = self._hierarchy.get_parent(tier)
        if parent_tier is not None:
            link_type = self._hierarchy.get_hierarchy_type(tier)
            if link_type == "TimeAssociation":
                sppasHierarchy.validate_time_association(parent_tier, tier)
            if link_type == "TimeAlignment":
                sppasHierarchy.validate_time_alignment(parent_tier, tier)
        else:
            for child_tier in self._hierarchy.get_children(tier):
                link_type = self._hierarchy.get_hierarchy_type(child_tier)
                if link_type == "TimeAssociation":
                    sppasHierarchy.validate_time_association(tier, child_tier)
                elif link_type == "TimeAlignment":
                    sppasHierarchy.validate_time_alignment(tier, child_tier)

    # -----------------------------------------------------------------------
    # Tiers
    # -----------------------------------------------------------------------

    def get_tier_list(self):
        """Return the list of tiers."""
        return self._tiers

    # ------------------------------------------------------------------------

    def get_tier_from_id(self, tier_id):
        """Return a sppasTier from its id or None.

        :param tier_id: (str) Identifier name of a tier

        """
        idt = tier_id.strip()
        for t in self._tiers:
            if t.get_meta('id') == idt:
                return t
        return None

    # -----------------------------------------------------------------------

    tiers = property(get_tier_list, None)

    # -----------------------------------------------------------------------

    def is_empty(self):
        """Return True if the transcription does not contain tiers."""
        return len(self._tiers) == 0

    # -----------------------------------------------------------------------

    def contains(self, tier):
        """Return True if the given tier is in the list of tiers.

        """
        if tier in self._tiers:
            return True
        for t in self._tiers:
            if t.get_id() == tier.get_id():
                return True
        return False

    # -----------------------------------------------------------------------

    def find(self, name, case_sensitive=True):
        """Find a tier from its name.

        :param name: (str) EXACT name of the tier
        :param case_sensitive: (bool)
        :returns: sppasTier or None

        """
        for tier in self._tiers:
            if case_sensitive:
                if tier.get_name() == name.strip():
                    return tier
            else:
                if tier.get_name().lower() == name.strip().lower():
                    return tier

        return None

    # -----------------------------------------------------------------------

    def find_id(self, tier_id):
        """Find a tier from its identifier.

        :param tier_id: (str) Exact identifier of the tier
        :returns: sppasTier or None

        """
        tier_id = str(tier_id).strip()
        for tier in self._tiers:
            if tier.get_id() == tier_id:
                return tier

        return None

    # -----------------------------------------------------------------------

    def get_tier_index(self, name, case_sensitive=True):
        """Get the index of a tier from its name.

        :param name: (str) EXACT name of the tier
        :param case_sensitive: (bool)
        :returns: index or -1 if not found

        """
        name = sppasUnicode(name).to_strip()
        t = self.find(name, case_sensitive)
        if t is None:
            return -1
        return self._tiers.index(t)

    # -----------------------------------------------------------------------

    def get_tier_index_id(self, identifier):
        """Get the index of a tier from its id.

        :param identifier: (str) GUID
        :returns: index or -1 if not found

        """
        for i, tier in enumerate(self._tiers):
            if tier.get_id() == identifier:
                return i
        return -1

    # -----------------------------------------------------------------------

    def set_tier_index_id(self, identifier, new_index):
        """Set the index of a tier from its identifier.

        :param identifier: (str)
        :param new_index: (int) New index of the tier in self
        :returns: index or -1 if not found

        """
        old_index = self.get_tier_index_id(identifier)
        if old_index == -1:
            raise IndexError("No tier with identifier {:s}".format(identifier))

        try:
            self._tiers.insert(new_index, self._tiers.pop(old_index))
        except:
            raise IndexError("{:d} is not a valid index for tier {:s}"
                             "".format(new_index, identifier))

    # -----------------------------------------------------------------------

    def set_tier_index(self, name, new_index, case_sensitive=True):
        """Set the index of a tier from its name.

        THIS SHOULD NEVER BE USED. USE TIER IDENTIFIER INSTEAD OF ITS NAME.

        :param name: (str) EXACT name of the tier
        :param new_index: (int) New index of the tier in self
        :param case_sensitive: (bool)
        :returns: index or -1 if not found

        """
        old_index = self.get_tier_index(name, case_sensitive)
        if old_index == -1:
            raise IndexError

        try:
            self._tiers.insert(new_index, self._tiers.pop(old_index))
        except:
            raise IndexError

    # -----------------------------------------------------------------------

    def rename_tier(self, tier):
        """Rename a tier by appending a digit.

        :param tier: (sppasTier) The tier to rename.

        """
        if not isinstance(tier, sppasTier):
            raise AnnDataTypeError(tier, "sppasTier")

        name = tier.get_name()
        i = 2
        while self.find(name) is not None:
            name = "{:s}({:d})".format(tier.get_name(), i)
            i += 1
        tier.set_name(name)

    # -----------------------------------------------------------------------

    def create_tier(self, name=None, ctrl_vocab=None, media=None):
        """Create and append a new empty tier.

        :param name: (str) the name of the tier to create
        :param ctrl_vocab: (sppasCtrlVocab)
        :param media: (sppasMedia)
        :returns: newly created empty tier

        """
        tier = sppasTier(name, ctrl_vocab, media, parent=self)
        self.append(tier)

        return tier

    # -----------------------------------------------------------------------

    def append(self, tier):
        """Append a new tier.

        :param tier: (sppasTier) the tier to append

        """
        if self.contains(tier) is True:
            raise TrsAddError(tier.get_name(), self._name)

        self.rename_tier(tier)
        if tier.get_ctrl_vocab() is not None:
            try:
                self.add_ctrl_vocab(tier.get_ctrl_vocab())
            except TrsAddError:
                pass
        if tier.get_media() is not None:
            try:
                self.add_media(tier.get_media())
            except TrsAddError:
                pass

        self._tiers.append(tier)
        tier.set_parent(self)

    # -----------------------------------------------------------------------

    def pop(self, index=-1):
        """Remove the tier at the given position in the transcription.

        Return it. If no index is specified, pop() removes
        and returns the last tier in the transcription.

        :param index: (int) Index of the tier to remove.
        :returns: (sppasTier)
        :raise: AnnDataIndexError

        """
        try:
            tier = self._tiers[index]
            self._hierarchy.remove_tier(tier)
            self._tiers.pop(index)
            tier.set_parent(None)
            return tier
        except IndexError:
            raise AnnDataIndexError(index)

    # -----------------------------------------------------------------------

    def get_min_loc(self):
        """Return the sppasPoint with the lowest value through all tiers."""
        if self.is_empty():
            return None

        min_point = None
        for tier in self:
            if tier.is_empty():
                continue
            first_loc = tier.get_first_point()
            if first_loc.is_point():
                first_point = first_loc
            else:
                first_point = first_loc.get_begin()
            if min_point is None or first_point < min_point:
                min_point = first_point

        return min_point

    # -----------------------------------------------------------------------

    def get_max_loc(self):
        """Return the sppasPoint with the highest value through all tiers."""
        if self.is_empty():
            return None

        max_point = None
        for tier in self:
            if tier.is_empty():
                continue
            last_loc = tier.get_last_point()
            if last_loc.is_point():
                last_point = last_loc
            else:
                last_point = last_loc.get_end()
            if max_point is None or last_point > max_point:
                max_point = last_point

        return max_point

    # -----------------------------------------------------------------------

    def shift(self, delay):
        """Shift all annotation' location to a given delay.

        :param delay: (int, float) delay to shift all localizations
        :raise: AnnDataTypeError

        """
        if float(delay) == 0.:
            return

        for tier in self._tiers:
            if delay < 0:
                # shifted to left: from the first to the last annotation
                for ann in tier:
                    ann.get_location().shift(delay)
            else:
                # shifted to right: from the last to the first annotation
                for ann in reversed(tier):
                    ann.get_location().shift(delay)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._tiers)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for x in self._tiers:
            yield x

    # -----------------------------------------------------------------------

    def __getitem__(self, i):
        return self._tiers[i]

    # -----------------------------------------------------------------------

    def __contains__(self, tier):
        if tier in self._tiers:
            return True
        for t in self._tiers:
            if t.get_id() == tier.get_id():
                return True
        return False

