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

    src.calculus.descriptivestats.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from .central import fsum
from .central import fmin
from .central import fmax
from .central import fmean
from .central import fmedian

from .variability import lvariance
from .variability import lstdev
from .variability import lzs

from .moment import lvariation

# ----------------------------------------------------------------------------


class sppasDescriptiveStatistics(object):
    """Descriptive statistics estimator class.

    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :author:       Brigitte Bigi
    :contact:      develop@sppas.org

    This class estimates descriptive statistics on a set of data values,
    stored in a dictionary:

        - the key is the name of the data set;
        - the value is the list of data values for this data set.

    >>> d = {'apples':[1, 2, 3, 4], 'peers':[2, 3, 3, 5]}
    >>> s = sppasDescriptiveStatistics(d)
    >>> total = s.total()
    >>> print(total)
    >>> (('peers', 13.0), ('apples', 10.0))

    """
    def __init__(self, dict_items):
        """Descriptive statistics.

        :param dict_items: a dict of tuples (key, [values])

        """
        self._items = dict_items

    # -----------------------------------------------------------------------

    def len(self):
        """Estimate the number of occurrences of data values.

        :returns: (dict) a dictionary of tuples (key, len)

        """
        return dict((key, len(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def total(self):
        """Estimate the sum of data values.

        :returns: (dict) a dictionary of tuples (key, total) of float values

        """
        return dict((key, fsum(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def min(self):
        """Estimate the minimum of data values.

        :returns: (dict) a dictionary of (key, min) of float values

        """
        return dict((key, fmin(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def max(self):
        """Estimate the maximum of data values.

        :returns: (dict) a dictionary of (key, max) of float values

        """
        return dict((key, fmax(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def mean(self):
        """Estimate the arithmetic mean of data values.

        :returns: (dict) a dictionary of (key, mean) of float values

        """
        return dict((key, fmean(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def median(self):
        """Estimate the 'middle' score of the data values.

        :returns: (dict) a dictionary of (key, mean) of float values

        """
        return dict((key, fmedian(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def variance(self):
        """Estimate the unbiased sample variance of data values.

        :returns: (dict) a dictionary of (key, variance) of float values

        """
        return dict((key, lvariance(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def stdev(self):
        """Estimate the standard deviation of data values.

        :returns: (dict) a dictionary of (key, stddev) of float values

        """
        return dict((key, lstdev(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def coefvariation(self):
        """Estimate the coefficient of variation of data values.

        :returns: (dict) a dictionary of (key, coefvariation) of float
        values (given as a percentage).

        """
        return dict((key, lvariation(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def zscore(self):
        """Estimate the z-scores of data values.

        The z-score determines the relative location of a data value.

        :returns: (dict) a dictionary of (key, [z-scores]) of float values

        """
        return dict((key, lzs(values))
                    for key, values in self._items.items())
