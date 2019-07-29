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

    src.calculus.infotheory.entropy.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from ..calculusexc import EmptyError, InsideIntervalError

from .utilit import log2
from .utilit import MAX_NGRAM
from .utilit import symbols_to_items

# ----------------------------------------------------------------------------


class sppasEntropy(object):
    """Entropy estimation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Entropy is a measure of unpredictability of information content.
    Entropy is one of several ways to measure diversity.

    If we want to look at the entropy on a large series, we could also compute
    the entropy for windows to measure the evenness or uncertainties.
    By looking at the definition, one could predict the areas that have a
    lot of variance would result in a higher entropy and the areas that have
    lower variance would result in lower entropy.

    """

    def __init__(self, symbols, n=1):
        """Create a sppasEntropy instance with a list of symbols.

        :param symbols: (list) a vector of symbols of any type.
        :param n: (int) n value for n-gram estimation. n ranges 1..MAX_NGRAM

        """
        self._symbols = list()
        self._ngram = 1

        self.set_symbols(symbols)
        self.set_ngram(n)

    # -----------------------------------------------------------------------

    def set_symbols(self, symbols):
        """Set the list of symbols.

        :param symbols: (list) a vector of symbols of any type.

        """
        if len(symbols) == 0:
            raise EmptyError

        self._symbols = symbols

    # -----------------------------------------------------------------------

    def set_ngram(self, n):
        """Set the n value of n-grams.

        :param n: (int) n value for n-gram estimation. n ranges 1..8

        """
        n = int(n)
        if 0 < n <= MAX_NGRAM:
            self._ngram = n
        else:
            raise InsideIntervalError(n, 1, MAX_NGRAM)

    # -----------------------------------------------------------------------

    def eval(self):
        """Estimate the Shannon entropy of a vector of symbols.

        Shannon's entropy measures the information contained in a message as
        opposed to the portion of the message that is determined
        (or predictable).

        :returns: (float) entropy value

        """
        if len(self._symbols) == 0:
            raise EmptyError

        exr = symbols_to_items(self._symbols, self._ngram)
        total = len(self._symbols) - self._ngram + 1
        result = 0.

        for symbol, occurrences in exr.items():

            probability = 1.0 * occurrences / total
            self_information = log2(1.0 / probability)
            result += (probability * self_information)

        return result
