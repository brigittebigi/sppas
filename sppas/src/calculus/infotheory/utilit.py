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

    src.calculus.infotheory.utilit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utilities for the information theory package.

"""
import math

MAX_NGRAM = 8

# ----------------------------------------------------------------------------


def log2(x):
    """Estimate log in base 2.

    :param x: (int, float) value
    :returns: (float)
    """
    x = float(x)
    return math.log(x)/math.log(2)

# ----------------------------------------------------------------------------


def find_ngrams(symbols, ngram):
    """Return a list of n-grams from a list of symbols.

    :param symbols: (list)
    :param ngram: (int) n value for the ngrams
    :returns: list of tuples

    Example:

        >>>symbols=[0,1,0,1,1,1,0]
        >>>print(find_ngrams(symbols, 2))
        >>>[(0, 1), (1, 0), (0, 1), (1, 1), (1, 1), (1, 0)]

    """
    return zip(*[symbols[i:] for i in range(ngram)])

# ----------------------------------------------------------------------------


def symbols_to_items(symbols, ngram):
    """Convert a list of symbols into a dictionary of items.

    Example:

        >>>symbols=[0, 1, 0, 1, 1, 1, 0]
        >>>print symbols_to_items(symbols,2)
        >>>{(0, 1): 2, (1, 0): 2, (1, 1): 2}

    :returns: dictionary with key=tuple of symbols, value=number of occurrences

    """
    nsymbols = find_ngrams(symbols, ngram)

    exr = dict()
    for each in nsymbols:
        v = 1 + exr.get(each, 0)
        exr[each] = v

    return exr
