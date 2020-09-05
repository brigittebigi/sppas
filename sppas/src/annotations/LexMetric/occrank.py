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

    src.annotations.LexMetric.occrank.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel
from sppas.src.exceptions.exc import sppasTypeError
from sppas.src.resources import sppasUnigram

# ---------------------------------------------------------------------------


class OccRank(object):
    """A class to estimate occurrences and ranks of items of a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, tier, alt=True):
        """Create an instance of OccRank.

        :param tier: (sppasTier)
        :param alt: (bool) Use alternative tags to estimate counts and rank

        """
        if isinstance(tier, sppasTier) is False:
            raise sppasTypeError(tier, "sppasTier")

        self.__tier = tier
        self.__alt = True
        self.set_use_alt(alt)
        self.__unigram = sppasUnigram()
        self.__estimate_counts()

    # -----------------------------------------------------------------------

    def __estimate_counts(self):
        self.__unigram = sppasUnigram()
        for ann in self.__tier:
            for label in ann.get_labels():
                if self.__alt is True:
                    for tag, score in label:
                        self.__unigram.add(tag.get_content())
                else:
                    tag = label.get_best()
                    self.__unigram.add(tag.get_content())

    # -----------------------------------------------------------------------

    def get_use_alt(self):
        """Return True if alternative tags are used."""
        return self.__alt

    # -----------------------------------------------------------------------

    def set_use_alt(self, value):
        """Either alternative tags are used or not.

        :param value: (bool)

        """
        alt = bool(value)
        if alt != self.__alt:
            self.__alt = alt
            self.__estimate_counts()

    # -----------------------------------------------------------------------

    def occ(self):
        """Return a tier with occurrences of labels.

        :Example:
            input:   the | little | little | cat
            output:    1 |    2   |    2   |  1

        """
        new_tier = sppasTier("Occ-%s" % self.__tier.get_name())
        new_tier.set_meta("occurrences_of_tier", self.__tier.get_name())

        for ann in self.__tier:
            location = ann.get_location().copy()
            labels = list()
            for label in ann.get_labels():
                if self.__alt is True:
                    occ_label = sppasLabel(tag=None)
                    for tag, score in label:
                        content = tag.get_content()
                        occ = self.__unigram.get_count(content)
                        occ_label.append(sppasTag(occ, "int"), score)
                    labels.append(occ_label)

                else:
                    tag = label.get_best()
                    content = tag.get_content()
                    occ = self.__unigram.get_count(content)
                    labels.append(sppasLabel(sppasTag(occ, "int")))

            if len(labels) > 0:
                new_tier.create_annotation(location, labels)

        return new_tier

    # -----------------------------------------------------------------------

    def rank(self):
        """Return a tier with the rank of each label.

        :Example:
            input:   the | little | little | cat
            output:    1 |    1   |    2   |  1

        """
        new_tier = sppasTier("Rank-%s" % self.__tier.get_name())
        new_tier.set_meta("rank_of_tier", self.__tier.get_name())
        unigram = sppasUnigram()

        for ann in self.__tier:
            location = ann.get_location().copy()
            labels = list()
            for label in ann.get_labels():
                if self.__alt is True:
                    rank_label = sppasLabel(tag=None)
                    for tag, score in label:
                        content = tag.get_content()
                        unigram.add(content)
                        occ = unigram.get_count(content)
                        rank_label.append(sppasTag(occ, "int"), score)
                    labels.append(rank_label)

                else:
                    tag = label.get_best()
                    content = tag.get_content()
                    unigram.add(content)
                    occ = unigram.get_count(content)
                    labels.append(sppasLabel(sppasTag(occ, "int")))

            if len(labels) > 0:
                new_tier.create_annotation(location, labels)

        return new_tier
