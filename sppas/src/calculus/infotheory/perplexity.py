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

    src.calculus.infotheory.perplexity.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from ..calculusexc import EmptyError, InsideIntervalError
from ..calculusexc import SumProbabilityError, ProbabilityError
from .utilit import log2
from .utilit import MAX_NGRAM
from .utilit import symbols_to_items

# ----------------------------------------------------------------------------


class sppasPerplexity(object):
    r"""Perplexity estimator.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Perplexity is a measurement of how well a probability distribution or
    probability model predicts a sample.
    The perplexity of a discrete probability distribution p is defined as:
    2^{H(p)}=2^{-\sum_x p(x)\log_2 p(x)}
    where H(p) is the entropy of the distribution and x ranges over events.

    Perplexity is commonly used to compare models on the same list of
    symbols - this list of symbols is "representing" the problem we are
    facing one. The higher perplexity, the better model.

    A model is represented as a distribution of probabilities: the key is
    representing the symbol and the value is the the probability.

    >>>model = dict()
    >>>model["peer"] = 0.1
    >>>model["pineapple"] = 0.2
    >>>model["tomato"] = 0.3
    >>>model["apple"] = 0.4
    >>>pp = sppasPerplexity(model)

    The observation on which the perplexity must be estimated on is
    represented as a list:
    >>>observed=['apple', 'pineapple', 'apple', 'peer']
    >>>pp.eval_perplexity(observed)
    >>>3.61531387398

    A higher adequacy between the model and the observed sequence implies an
    higher perplexity value:
    >>>observed=['apple', 'pineapple', 'apple', 'tomato']
    >>>pp.eval_perplexity(observed)
    >>>4.12106658324

    It is possible that an observed item isn't in the model... Then, the
    perplexity value is lower (because of an higher entropy). An epsilon
    probability is assigned to missing symbols.
    >>>observed=['apple', 'grapefruit', 'apple', 'peer']
    >>>pp.eval_perplexity(observed)
    >>>2.62034217479

    """

    DEFAULT_EPSILON = 0.000001

    # -----------------------------------------------------------------------

    def __init__(self, model, ngram=1):
        """Create a Perplexity instance with a list of symbols.

        :param model: (dict) a dictionary with key=item, value=probability
        :param ngram: (int) the n value, in the range 1..8

        """
        self._model = dict()
        self._ngram = 1
        self._epsilon = sppasPerplexity.DEFAULT_EPSILON

        self.set_model(model)
        self.set_ngram(ngram)

    # -----------------------------------------------------------------------

    def set_epsilon(self, eps=0.):
        """Set a value for epsilon.

        This value must be significantly lower than the minimum value in the
        model.

        :param eps: (float) new epsilon value.
        If eps is set to 0, a default value will be assigned.

        """
        eps = float(eps)
        if eps < 0. or eps > 0.1:
            raise InsideIntervalError(eps, 0., 0.1)

        if self._model is not None:
            # Find the minimum...
            p_min = round(min(proba for proba in self._model.values()), 6)
            if eps > p_min/2.:
                eps = p_min/3.

        if eps == 0.:
            self._epsilon = self.DEFAULT_EPSILON
        else:
            self._epsilon = eps

    # -----------------------------------------------------------------------

    def set_model(self, model):
        """Set the probability distribution to the model.

        Notice that the epsilon value is re-assigned.

        :param model: (dict) Dictionary with symbols as keys and values as
        probabilities.

        """
        # check the model before assigning to the member
        if model is None or len(model) == 0:
            raise EmptyError

        for v in model.values():
            if v < 0. or v > 1.:
                raise ProbabilityError(v)

        p_sum = sum(model.values())
        if round(p_sum, 6) != 1.:
            raise SumProbabilityError(p_sum)

        self._model = model
        self.set_epsilon()

    # -----------------------------------------------------------------------

    def set_ngram(self, n):
        """Set the n value of n-grams.

        :param n: (int) Value ranging from 1 to MAX_GRAM

        """
        n = int(n)
        if 0 < n <= MAX_NGRAM:
            self._ngram = n
        else:
            raise InsideIntervalError(n, 1, MAX_NGRAM)

    # -----------------------------------------------------------------------

    def eval_pp(self, symbols):
        """Estimate the perplexity of a list of symbols.

        :returns: float value

        """
        exr = symbols_to_items(symbols, self._ngram)
        entropy = 0.

        for symbol, occurrences in exr.items():

            real_symbol = " ".join(symbol).strip()
            probability = self._model.get(real_symbol, self._epsilon)
            self_information = log2(1.0/probability)

            entropy += ((probability * self_information) * occurrences)

        return pow(2, entropy)
