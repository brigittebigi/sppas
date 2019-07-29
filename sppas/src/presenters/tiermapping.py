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

    src.presenters.tiermapping.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.utils import u
from sppas.src.resources import sppasMapping
from sppas.src.anndata import sppasLabel, sppasTag
from sppas.src.anndata import sppasAnnotation, sppasTier

# ---------------------------------------------------------------------------


class sppasMappingTier(sppasMapping):
    """Map content of annotations of a tier from a mapping table.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    A conversion table is used to map symbols of labels of a tier with new
    symbols. This class can convert either individual symbols or strings of
    symbols (syllables, words, ...) if a separator is given.

    Any symbols in the transcription tier which is not in the conversion
    table is replaced by a specific symbol (by default '*').

    """

    def __init__(self, dict_name=None):
        """Create a sppasMappingTier instance.

        :param dict_name: (str) The mapping dictionary.

        """
        super(sppasMappingTier, self).__init__(dict_name)
        self._delimiters = sppasMapping.DEFAULT_SEP
        self._map_symbols = False

    # -----------------------------------------------------------------------

    def get_delimiters(self):
        """Return the list of delimiters."""
        return self._delimiters

    # -----------------------------------------------------------------------

    def set_delimiters(self, delimit_list):
        """Fix the list of characters to be used as symbol delimiters.

        If delimit_list is an empty list, the mapping system will map with a
        longest matching algorithm.

        :param delimit_list: List of characters, for example [" ", ".", "-"]

        """
        delimit_list = list(delimit_list)
        # Each element of the list must contain only one character
        for i, c in enumerate(delimit_list):
            delimit_list[i] = u(c)[0]

        # Set the delimiters as Iterable() and not as List()
        self._delimiters = tuple(delimit_list)

    # -----------------------------------------------------------------------

    def set_map_symbols(self, value):
        """Define if symbols has to be mapped or not.

        :param value: (bool)

        """
        self._map_symbols = value

    # -----------------------------------------------------------------------

    def map_tier(self, tier):
        """Run the mapping process on an input tier.

        :param tier: (sppasTier) The tier instance to map label symbols.
        :returns: a new tier

        """
        # Create the output tier
        new_tier = sppasTier(tier.get_name()+"-map")
        new_tier.set_media(tier.get_media())
        for key in tier.get_meta_keys():
            if key != 'id':
                new_tier.set_meta(key, tier.get_meta(key))
        new_tier.set_meta('tier_was_mapped_from', tier.get_name())

        # if no annotations
        if len(tier) == 0:
            return new_tier

        # always map, even if empty mapping table: it will copy annotations
        for ann in tier:
            new_tier.add(self.map_annotation(ann))

        return new_tier

    # -----------------------------------------------------------------------

    def map_annotation(self, annotation):
        """Run the mapping process on an annotation.

        :param annotation: (sppasAnnotation) annotation with symbols to map
        :returns: a new annotation, with the same 'id' as the given one

        """
        # Annotation without label
        if annotation.is_labelled() is False:
            a = annotation.copy()
            a.gen_id()
            return a

        # Map all tags of all labels, if tags are strings
        new_labels = list()
        for label in annotation.get_labels():
            new_labels.append(self.map_label(label))

        # Create an annotation with the new version of labels
        a = sppasAnnotation(annotation.get_location().copy(), new_labels)
        for m in annotation.get_meta_keys():
            if m != 'id':
                a.set_meta(m, annotation.get_meta(m))

        return a

    # -----------------------------------------------------------------------

    def map_label(self, label):
        """Run the mapping process on a label.

        :param label: (sppasLabel) label with symbols to map
        :returns: sppasLabel()

        """
        new_label = sppasLabel(None)
        for tag, score in label:
            new_tags = self.map_tag(tag)
            for new_tag in new_tags:
                s = None
                if score is not None:
                    s = float(score) / float(len(new_tags))
                new_label.append(new_tag, s)

        return new_label

    # -----------------------------------------------------------------------

    def map_tag(self, tag):
        """Run the mapping process on a tag.

        :param tag: (sppasTag) tag with symbols to map
        :returns: List of sppasTag()

        """
        # only non-empty strings can me mapped
        if tag.get_type() == 'str' and tag.is_empty() is False:
            # only speech can be mapped, not the symbols.
            if tag.is_speech() is True or self._map_symbols is True:

                result = list()
                content = tag.get_content()
                if content.startswith('{') and content.endswith('}'):
                    content = content[1:-1]
                mapped_content = self.map(content, self._delimiters)
                for content in mapped_content.split('|'):
                    result.append(sppasTag(content))
                return result

        return [tag.copy()]
