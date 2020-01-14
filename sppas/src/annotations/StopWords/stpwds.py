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

    src.annotations.StopWords.stpwds.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas import symbols
from sppas import IndexRangeException

from sppas.src.resources import sppasVocabulary
from sppas.src.resources import sppasUnigram

# -----------------------------------------------------------------------


class StopWords(sppasVocabulary):
    """Automatic evaluation of a list of Stop-Words.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    An entry 'w' is relevant for the speaker if its probability is less than
    a threshold:

        | P(w) <= 1 / (alpha * V)

    where 'alpha' is an empirical coefficient and 'V' is the vocabulary
    size of the speaker.

    """

    def __init__(self, case_sensitive=False):
        """Create a new StopWords instance. """
        super(StopWords, self).__init__(filename=None,
                                        nodump=True,
                                        case_sensitive=case_sensitive)
        self.__alpha = 0.5
        self.max_alpha = 4.

    # ------------------------------------------------------------------------

    def set_alpha(self, alpha):
        """Fix the alpha option.

        Alpha is a coefficient to add specific stop-words in the list.
        Default value is 0.5.

        :param alpha: (float) Value in range [0..4]

        """
        alpha = float(alpha)
        if 0. < alpha < self.max_alpha:
            self.__alpha = alpha
        else:
            raise IndexRangeException(alpha, 0, self.max_alpha)

    # -----------------------------------------------------------------------

    def copy(self):
        """Make a deep copy of the instance.

        :returns: (StopWords)

        """
        s = StopWords()
        for i in self:
            s.add(i)

        return s

    # -----------------------------------------------------------------------

    def load(self, filename, merge=True):
        """Load a list of stop-words from a file.

        :param filename: (str)
        :param merge: (bool) Merge with the existing list (if True) or
        delete the existing list (if False)

        """
        if merge is False:
            self.clear()
        self.load_from_ascii(filename)

    # -----------------------------------------------------------------------

    def evaluate(self, tier=None, merge=True):
        """Add entries to the list of stop-words from the content of a tier.

        :param tier: (sppasTier) A tier with entries to be analyzed.
        :param merge: (bool) Merge with the existing list (if True) or
        delete the existing list and create a new one (if False)

        """
        if tier is None or len(tier) < 5:
            return

        # Create the sppasUnigram and put data
        u = sppasUnigram()
        for a in tier:
            content = a.serialize_labels()
            if content not in symbols.all:
                u.add(content)

        # Estimate values for relevance
        _v = float(len(u))
        threshold = 1. / (self.__alpha * _v)

        # Estimate if a token is relevant; if not: put it in the stop-list
        if merge is False:
            self.clear()

        for token in u.get_tokens():
            p_w = float(u.get_count(token)) / float(u.get_sum())
            if p_w > threshold:
                self.add(token)

