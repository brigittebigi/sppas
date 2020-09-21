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

    src.calculus.infotheory.kullbackleibler.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from collections import Counter

from ..calculusexc import EmptyError, InsideIntervalError
from ..calculusexc import SumProbabilityError, ProbabilityError
from .utilit import log2

# ----------------------------------------------------------------------------


class sppasKullbackLeibler(object):
    u"""Kullback-Leibler distance estimator.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    In probability theory and information theory, the Kullback–Leibler
    divergence (also called relative entropy) is a measure of the difference
    between two probability distributions P and Q. It is not symmetric in P
    and Q.

    Specifically, the Kullback–Leibler divergence of Q from P, denoted
    DKL(P‖Q), is a measure of the information gained when one revises ones
    beliefs from the prior probability distribution Q to the posterior
    probability distribution P.

    However, the sppasKullbackLeibler class estimates the KL distance, i.e. the
    *symmetric Kullback-Leibler divergence*.

    This sppasKullbackLeibler class implements the distance estimation
    between a model and the content of a moving window on data,
    as described in:

    Brigitte Bigi, Renato De Mori, Marc El-Bèze, Thierry Spriet (1997).
    *Combined models for topic spotting and topic-dependent language modeling*
    IEEE Workshop on Automatic Speech Recognition and Understanding Proceedings
    (ASRU), Edited by S. Furui, B. H. Huang and Wu Chu, IEEE Signal Processing
    Society Publ, NY, pages 535-542.

    This KL distance can also be used to estimate the distance between
    documents for text categorization, as proposed in:

    Brigitte Bigi (2003).
    Using Kullback-Leibler Distance for Text Categorization.
    Lecture Notes in Computer Science, Advances in Information Retrieval,
    ISSN 0302-9743, Fabrizio Sebastiani (Editor), Springer-Verlag (Publisher),
    pages 305--319, Pisa (Italy).

    In this class...

    A model is a dictionary with:

        - key is an n-gram,
        - value is a probability.

    The window of observed symbols is represented as a list of n-grams.

    """

    DEFAULT_EPSILON = 0.000001

    # -----------------------------------------------------------------------

    def __init__(self, model=None, observations=None):
        """Create a sppasKullbackLeibler instance from a list of symbols.

        :param model: (dict) a dictionary with key=item, value=probability
        :param observations: list ob observed items

        """
        self._observations = list()
        self._model = dict()
        self._epsilon = sppasKullbackLeibler.DEFAULT_EPSILON

        if model is not None:
            self.set_model(model)
        if observations is not None:
            self.set_observations(observations)

    # -----------------------------------------------------------------------

    def get_epsilon(self):
        """Return the epsilon value."""
        return self._epsilon

    # -----------------------------------------------------------------------

    def get_model(self):
        """Return the model."""
        return self._model

    # -----------------------------------------------------------------------

    def set_model(self, model):
        """Set the model.

        :param model: (dict) Probability distribution of the model.

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

    # -----------------------------------------------------------------------

    def set_model_from_data(self, data):
        """Set the model from a given set of observations.

        :param data: (list) List of observed items.

        """
        if data is None or len(data) == 0:
            raise EmptyError

        model = dict()
        for obs in data:
            if obs not in model:
                model[obs] = data.count(obs)

        self._model = dict()
        n = float(len(data))
        for obs in model:
            self._model[obs] = (float(model[obs]) / n)

    # -----------------------------------------------------------------------

    def set_observations(self, observations):
        """Fix the set of observed items.

        :param observations: (list) The list of observed items.

        """
        if observations is None or len(observations) == 0:
            raise EmptyError

        self._observations = observations

    # -----------------------------------------------------------------------

    def set_epsilon(self, eps):
        """Fix the linear back-off value for unknown observations.

        The optimal value for this coefficient is the product of the size
        of both model and observations to estimate the KL. This value must
        be significantly lower than the minimum value in the model.

        :param eps: (float) Epsilon value.
        If eps is set to 0, a default value will be assigned.

        """
        eps = float(eps)
        if eps < 0. or eps > 0.1:
            raise InsideIntervalError(eps, 0., 0.1)

        if len(self._model) > 0:
            # Find the minimum...
            pmin = min(p for p in self._model.values())
            if eps > pmin/2.:
                eps = pmin/3.

        if eps == 0.:
            self._epsilon = self.DEFAULT_EPSILON
        else:
            self._epsilon = eps

    # -----------------------------------------------------------------------

    def eval_kld(self):
        """Estimate the KL distance between a model and observations.

        :returns: float value

        """
        if self._model is None or self._observations is None:
            raise EmptyError

        if len(self._model) == 0 or len(self._observations) == 0:
            raise EmptyError

        na = 0
        nb = 0
        for x in self._observations:
            if x in self._model:
                nb += 1
            else:
                na += 1

        # coefficient applied to the model
        alpha = 1. - (na * self._epsilon)
        # coefficient applied to the observed n-grams
        beta = 1. - (nb * self._epsilon)

        return self.__distance(alpha, beta)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __distance(self, alpha, beta):
        """Kullback-Leibler Distance between the model and observations.

        We expect a model, observations and epsilon already estimated properly.

        :param alpha: (float) Coefficient applied to the model
        :param beta: (float) Coefficient applied to the observed items

        """
        dist = 0.
        n = len(self._observations)

        # Convert the list of observed events to a dict with value=count
        obs_dict = Counter(self._observations)
        for x in obs_dict:
            # get the observation proba
            proba_model = self._epsilon
            if x in self._model:
                proba_model = alpha * self._model[x]
            count_obs = obs_dict[x]
            proba_obs = beta * (float(count_obs) / float(n))

            # evaluate the contribution ot the distance between
            # the observation proba and the model proba
            d = (proba_model - proba_obs) * log2(proba_model / proba_obs)

            # this observation contributes 'count_obs' times to the KLD
            dist += (d * count_obs)

        # Estimates the distance using n-grams in the model
        for x in self._model:
            if x not in obs_dict:
                proba_model = alpha * self._model[x]
                dist += ((proba_model - self._epsilon) *
                         log2(proba_model / self._epsilon))

        return dist
