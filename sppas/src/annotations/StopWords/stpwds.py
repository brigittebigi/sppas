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

from sppas.src.config import symbols
from sppas.src.exceptions import IndexRangeException

from sppas.src.resources import sppasVocabulary
from sppas.src.resources import sppasUnigram
from ..annotationsexc import EmptyInputError, TooSmallInputError

# -----------------------------------------------------------------------


class StopWords(sppasVocabulary):
    """A vocabulary that can automatically evaluate a list of Stop-Words.

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

    MAX_ALPHA = 4.
    MIN_ANN_NUMBER = 5

    def __init__(self, case_sensitive=False):
        """Create a new StopWords instance.

        :param case_sensitive: (bool) Considers the case of entries or not.

        """
        super(StopWords, self).__init__(filename=None,
                                        nodump=True,
                                        case_sensitive=case_sensitive)
        # Member
        self.__alpha = 0.5

        # Estimated values (from a given sppasTier)
        self.__threshold = 0.
        self.__v = 0.

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def get_alpha(self):
        """Return the value of alpha coefficient (float)."""
        return self.__alpha

    def get_threshold(self):
        """Return the last estimated threshold (float)."""
        return self.__threshold

    def get_v(self):
        """Return the last estimated vocabulary size (int)."""
        return self.__v

    # ------------------------------------------------------------------------

    def set_alpha(self, alpha):
        """Fix the alpha option.

        Alpha is a coefficient to add specific stop-words in the list.
        Default value is 0.5.

        :param alpha: (float) Value in range [0..4]

        """
        alpha = float(alpha)
        if 0. < alpha <= self.MAX_ALPHA:
            self.__alpha = alpha
        else:
            raise IndexRangeException(alpha, 0, StopWords.MAX_ALPHA)

    # -----------------------------------------------------------------------

    alpha = property(get_alpha, set_alpha)

    # -----------------------------------------------------------------------
    # Data management
    # -----------------------------------------------------------------------

    def copy(self):
        """Make a deep copy of the instance.

        :returns: (StopWords)

        """
        s = StopWords()
        for i in self:
            s.add(i)

        s.set_alpha(self.__alpha)

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

        Estimate if a token is relevant: if not it adds it in the stop-list.

        :param tier: (sppasTier) A tier with entries to be analyzed.
        :param merge: (bool) Merge with the existing list (if True) or
        delete the existing list and create a new one (if False)
        :returns: (int) Number of entries added into the list
        :raises: EmptyInputError, TooSmallInputError

        """
        if tier is None or tier.is_empty():
            raise EmptyInputError(tier.get_name())
        if len(tier) < StopWords.MIN_ANN_NUMBER:
            raise TooSmallInputError(tier.get_name())

        # Create the sppasUnigram from the best tag of each label
        # and put data into a sppasUnigram to estimate frequencies
        unigram = sppasUnigram()
        for ann in tier:
            for label in ann.get_labels():
                # get the content of the best tag in 'str' type
                tag = label.get_best()
                content = tag.get_content()
                if content not in symbols.all:
                    unigram.add(content)

        # Fix values for the estimation of the relevance
        self.__v = len(unigram)
        self.__threshold = 1. / (self.__alpha * float(self.__v))

        if merge is False:
            self.clear()

        # Estimate if a token is relevant: if not, add it in the stop-list
        usum = float(unigram.get_sum())
        nb = 0
        for token in unigram.get_tokens():
            p_w = float(unigram.get_count(token)) / usum
            if p_w > self.__threshold:
                self.add(token)
                nb += 1

        return nb
