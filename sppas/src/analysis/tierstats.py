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

    analysis.tierstats.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.calculus.stats.descriptivesstats import sppasDescriptiveStatistics
from sppas.src.calculus.infotheory.utilit import MAX_NGRAM
from sppas.src.calculus.calculusexc import InsideIntervalError

# ----------------------------------------------------------------------------


class sppasTierStats(object):
    """Estimate descriptive statistics of annotations of a tier.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Map a tier into a dictionary where:
    
        - key is a tag
        - value is the list of observed durations of this tag in annotations

    """

    def __init__(self, tier=None, n=1, with_radius=0, with_alt=False):
        """Create a new TierStats instance.

        :param tier: (either sppasTier or list of them)
        :param n: (int) n-gram value
        :param with_radius: (int) 0 to use Midpoint, negative value
        to use R-, positive value to use R+
        :param with_alt: (bool) Use or not use of alternative labels

        """
        self.tier = tier
        self._with_radius = with_radius
        self._with_alt = with_alt
        self._ngram = 1

        self.set_ngram(n)

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_ngram(self):
        """Returns the n-gram value."""
        return self._ngram

    # ------------------------------------------------------------------

    def get_with_radius(self):
        """Returns how to use the radius in duration estimations.

        0 means to use Midpoint, negative value means to use R-, and 
        positive value means to use R+.
        
        """
        return self._with_radius

    # ------------------------------------------------------------------

    def get_with_alt(self):
        """Return if alternative labels will be used or not."""
        return self._with_alt

    # ------------------------------------------------------------------
    
    def get_tier(self):
        """Return the tier to estimate stats."""
        return self.tier

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def set_with_radius(self, with_radius):
        """Set the with_radius option, used to estimate the duration.
        
        :param with_radius: (int) Fix the with_radius option

        with_radius can take the following values:

            - 0 means to use midpoint;
            - negative value means to use (midpoint-radius);
            - positive radius means to use (midpoint+radius).
        
        """
        self._with_radius = int(with_radius)

    # ------------------------------------------------------------------
    
    def set_withalt(self, withalt):
        """Set the withalt option, used to select the labels.


            - False means to use only the label with the higher score
            of each annotation
            - True means to use all labels of each annotation

        """
        self._with_alt = withalt

    # ------------------------------------------------------------------
    
    def set_ngram(self, n):
        """Set the n value of the n-grams.

        It is used to fix the history size (at least =1).
        
        """
        n = int(n)
        if 0 < n <= MAX_NGRAM:
            self._ngram = n
        else:
            raise InsideIntervalError(n, 1, MAX_NGRAM)

    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    def ds(self):
        """Create a DescriptiveStatistic object for the given tier. 
        
        :returns: (DescriptiveStatistic)
        
        """
        ltup = self.__tiers_to_tuple()
        ngrams = list()
        for t in ltup:
            ngrams.extend(self.__ngrams(t))
        items = sppasTierStats.tuple_to_dict(ngrams)
        
        return sppasDescriptiveStatistics(items)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def __tiers_to_tuple(self):
        """Return a list of tuples of label/duration pairs."""
        tiers = self.tier
        if not isinstance(self.tier, list):
            tiers = [self.tier]

        return [self.__tier_to_tuple(tier) for tier in tiers]

    # ------------------------------------------------------------------

    def __tier_to_tuple(self, tier):
        """Return a tuple of label/duration pairs for a given tier.
        
        :param tier: (Tier)
        :returns: tuple
        
        """
        l = list()
        for ann in tier:

            labels = ann.get_labels()
            if labels is None:
                continue
            if len(labels) == 0:
                continue

            contents = list()
            for label in labels:
                if self._with_alt is False:
                    # get the best tag
                    contents.append(label.get_best())
                else:
                    # get all tags
                    for tag, score in label:
                        if tag is not None:
                            contents.append(tag)

            dur = 0.
            if len(labels) == 1:
                duration = ann.get_location().get_best().duration()
                dur = duration.get_value()

                if self._with_radius < 0:
                    dur += duration.get_margin()
                elif self._with_radius > 0:
                    dur -= duration.get_margin()

            for tag in contents:
                l.append((tag.get_content(), dur))

        return tuple(l)

    # ------------------------------------------------------------------
    
    def __ngrams(self, items):
        """Yield a sequences of ngrams. 

        :param items: (tuple) the ngram items

        """
        l = list()
        size = len(items)
        if (size - self._ngram) > 0:
            limit = size - self._ngram + 1
            for i in range(limit):
                l.append(items[i:i + self._ngram])
        return l

    # ------------------------------------------------------------------

    @staticmethod
    def tuple_to_dict(items):
        """Convert into a dictionary.
        
        :param items: (tuple) the ngram items
        :returns: dictionary key=text, value=list of durations.
        
        """
        d = dict()
        for item in items:
            dur = sum([i[1] for i in item])
            text = " ".join([i[0] for i in item])
            if text not in d:
                d[text] = []
            d[text].append(dur)
        return d
