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

    src.calculus.stats.frequency.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

A collection of basic frequency functions for python.

"""

import math

from ..calculusexc import EmptyError, ProbabilityError

# ---------------------------------------------------------------------------


def freq(mylist, item):
    """Return the relative frequency of an item of a list.

    :param mylist: (list) list of elements
    :param item: (any) an element of the list (or not!)
    :returns: frequency (float) of item in mylist

    """
    return float(mylist.count(item)) / float(len(mylist))

# ---------------------------------------------------------------------------


def percent(mylist, item):
    """Return the percentage of an item of a list.

    :param mylist: (list) list of elements
    :param item: (any) an element of the list (or not!)
    :returns: percentage (float) of item in mylist

    """
    return 100.0 * freq(mylist, item)

# ---------------------------------------------------------------------------


def percentile(mylist, p=(25, 50, 75), sort=True):
    """Return the pth percentile of an unsorted or sorted numeric list.

    This is equivalent to calling quantile(mylist, p/100.0).

    >>> round(percentile([15, 20, 40, 35, 50], 40), 2)
    26.0
    >>> for perc in percentile([15, 20, 40, 35, 50], (0, 25, 50, 75, 100)):
    ...     print("{:.2f}".format(perc))
    ...
    15.00
    17.50
    35.00
    45.00
    50.00

    :param mylist: (list) list of elements.
    :param p: (tuple) the percentile we are looking for.
    :param sort: whether to sort the vector.
    :returns: percentile as a float

    """
    if hasattr(p, "__iter__"):
        return quantile(mylist, (x/100.0 for x in p), sort)

    return quantile(mylist, p/100.0, sort)

# ---------------------------------------------------------------------------


def quantile(mylist, q=(0.25, 0.5, 0.75), sort=True):
    """Return the qth quantile of an unsorted or sorted numeric list.

     Calculates a rank n as q(N+1), where N is the number of items in mylist,
     then splits n into its integer component k and decimal component d.
     If k <= 1, returns the first element;
     if k >= N, returns the last element;
     otherwise returns the linear interpolation between
     mylist[k-1] and mylist[k] using a factor d.

     >>> round(quantile([15, 20, 40, 35, 50], 0.4), 2)
     26.0

    :param mylist: (list) list of elements.
    :param q: (tuple) the quantile we are looking for.
    :param sort: whether to sort the vector.
    :returns: quantile as a float

    """
    if len(mylist) == 0:
        raise EmptyError

    if sort is True:
        mylist = sorted(mylist)

    if hasattr(q, "__iter__"):
        qs = q
        return_single = False
    else:
        qs = [q]
        return_single = True

    for p in qs:
        if p < 0. or p > 1.:
            raise ProbabilityError(p)

    result = list()
    for p in qs:

        n = float(p) * (len(mylist)+1)
        k, d = int(n), n-int(n)
        if k >= len(mylist):
            result.append(mylist[-1])
        elif k < 1:
            result.append(mylist[0])
        else:
            result.append((1-d) * mylist[k-1] + d * mylist[k])

    if return_single:
        result = result[0]

    return result

# ---------------------------------------------------------------------------
# NLP functions related to frequency
# ---------------------------------------------------------------------------


def hapax(mydict):
    """Return a list of hapax.

    :param mydict: (dict)
    :returns: list of keys for which value = 1

    """
    return [k for k in mydict.keys() if mydict[k] == 1]

# ---------------------------------------------------------------------------


def occranks(mydict):
    """Return a dictionary with key=occurrence, value=rank.

    :param mydict: (dict)
    :returns: dict

    """
    # how many occurrences of each value of mydict?
    occ = dict()
    for k in mydict:
        v = mydict[k]
        if v in occ:
            occ[v] += 1
        else:
            occ[v] = 1

    # ranking with the occurrence as key
    occ_dict = dict()
    for r, o in enumerate(reversed(sorted(occ.keys()))):
        occ_dict[o] = r + 1

    return occ_dict

# ---------------------------------------------------------------------------


def ranks(counter):
    """Return a dictionary with key=token, value=rank.

    :param counter: (collections.Counter)
    :returns: dict

    """
    r = dict()
    oclist = occranks(counter)
    for k in counter.keys():
        occ = counter[k]
        r[k] = oclist[occ]

    return r

# ---------------------------------------------------------------------------


def zipf(dict_ranks, item):
    """Return the Zipf Law value of an item.

    Zipf's law states that given some corpus of natural language utterances,
    the frequency of any word is inversely proportional to its rank in the
    frequency table. Thus the most frequent word will occur approximately
    twice as often as the second most frequent word, three times as often
    as the third most frequent word, etc.

    :param dict_ranks: (dict) is a dictionary with key=entry, value=rank.
    :param item: (any) is an entry of the ranks dictionary
    :returns: Zipf value or -1 if the entry is missing

    """
    if item in dict_ranks:
        return 0.1 / dict_ranks[item]

    return -1

# ---------------------------------------------------------------------------


def tfidf(documents, item):
    """Return the tf.idf of an item.

    Term frequency–inverse document frequency, is a numerical statistic
    that is intended to reflect how important a word is to a document in a
    collection or corpus. The tf.idf value increases proportionally to the
    number of times a word appears in the document, but is offset by the
    frequency of the word in the corpus, which helps to control for the fact
    that some words are generally more common than others.

    :param documents: a list of list of entries.
    :param item:
    :returns: float

    """
    # Estimate tf of item in the corpus
    alltokens = []
    for d in documents:
        alltokens.extend(d)
    tf = freq(alltokens, item)

    # number of documents in the corpus
    D = len(documents)

    # number of documents with at least one occurrence of item
    dw = 0.
    for d in documents:
        if item in d:
            dw += 1.
    if dw == 0.:
        return 0.

    return tf * (math.log(D / dw))
