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

    src.calculus.kappa.py
    ~~~~~~~~~~~~~~~~~~~~~

    Inter-observer variation can be measured in any situation in which two or
    more independent observers are evaluating the same thing. The Kappa
    statistic seems the most commonly used measure of inter-rater agreement
    in Computational Linguistics.

    Kappa is intended to give the reader a quantitative measure of the
    magnitude of agreement between observers.

"""

from __future__ import division

from ..geometry.distances import squared_euclidian as sq
from ..calculusexc import VectorsError, EuclidianDistanceError

# ----------------------------------------------------------------------------


class sppasKappa(object):
    """Inter-observer variation estimation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi

    The calculation is based on the difference between how much agreement is
    actually present (“observed” agreement) compared to how much agreement
    would be expected to be present by chance alone (“expected” agreement).

    Imagine a situation in which annotators have to answer Yes or No to
    5 questions.

        - Person "P" answered: Yes, No, No, Yes, Yes
        - Person "Q" answered: Yes, No, Yes, Yes, Yes

    This results in the following vectors of probabilities:

    >>> p = [(1., 0.), (0., 1.), (0., 1.), (1., 0.), (1., 0.)]
    >>> q = [(1., 0.), (0., 1.), (1., 0.), (1., 0.), (1., 0.)]

    The Cohen's Kappa is then evaluated as follow:

    >>> sppasKappa.check_vector(p)
    >>> True
    >>> sppasKappa.check_vector(q)
    >>> True
    >>> kappa = sppasKappa(p, q)
    >>> kappa.evaluate()
    >>> 0.54545

    """
    def __init__(self, p=list(), q=list()):
        """Create a sppasKappa instance with two lists of tuples p and q.

        >>> p=[(1., 0.), (1., 0.), (0.8, 0.2)]

        :param p: a vector of tuples of float values
        :param q: a vector of tuples of float values

        """
        self._p = list()
        self._q = list()
        if len(p) > 0 and len(q) > 0:
            self.set_vectors(p, q)
    
    # -----------------------------------------------------------------------

    def set_vectors(self, p, q):
        """Set the vectors of probabilities to estimate the sppasKappa value.
        
        :param p: a vector of tuples of float values
        :param q: a vector of tuples of float values

        """
        if sppasKappa.check_vector(p) and sppasKappa.check_vector(q) is False:
            raise VectorsError
        self._p = p
        self._q = q

    # -----------------------------------------------------------------------

    def sqv(self):
        """Estimate the Euclidian distance between two vectors.

        :returns: v

        """
        if len(self._p) != len(self._q):
            raise VectorsError

        return sum([sq(x, y) for (x, y) in zip(self._p, self._q)])

    # -----------------------------------------------------------------------

    def sqm(self):
        """Estimate the Euclidian distance between two vectors.

        :returns: row, col

        """
        if len(self._p) != len(self._q):
            raise VectorsError

        row = list()
        for x in self._p:
            row.append(sum(sq(x, y) for y in self._q))

        col = list()
        for y in self._q:
            col.append(sum(sq(y, x) for x in self._p))

        if sum(row) != sum(col):
            raise EuclidianDistanceError

        return row, col

    # -----------------------------------------------------------------------

    def check(self):
        """Check if the given p and q vectors are correct to be used.

        :returns: bool

        """
        return sppasKappa.check_vector(self._p) and sppasKappa.check_vector(self._q)

    # -----------------------------------------------------------------------

    def evaluate(self):
        """Estimate the Cohen's Kappa between two lists of tuples p and q.

        The tuple size corresponds to the number of categories, each value is
        the score assigned to each category for a given sample.

        :returns: float value

        """
        v = self.sqv() / float(len(self._p))
        row, col = self.sqm()

        r = sum(row) / float(len(self._p)**2)
        if r == 0.:
            return 1.

        return 1.0 - v/r

    # -----------------------------------------------------------------------

    @staticmethod
    def check_vector(v):
        """Check if the vector is correct to be used.

        :param v: a vector of tuples of probabilities.

        """
        # Must contain data!
        if v is None or len(v) == 0:
            return False

        for t in v:

            # Must contain tuples only.
            if not type(t) is tuple:
                return False

            # All tuples have the same size (more than 1).
            if len(t) != len(v[0]) or len(t) < 2:
                return False

            # Tuple values are probabilities.
            s = 0.
            for p in t:
                if p < 0. or p > 1.:
                    return False
                s += p
            s = round(s, 3)
            if s < 0.999 or s > 1.001:
                return False

        return True
