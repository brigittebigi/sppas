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

    src.annotations.windowing.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import decimal

from sppas import sppasTypeError
from sppas.src.config import symbols
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasAnnSet

# ---------------------------------------------------------------------------


SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class sppasTierWindow(object):
    """Windowing system on a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    Support windows in the time domain or with tag separators, both with or
    with overlaps among windows.

    """

    def __init__(self, tier):
        """Create an instance of a sppasTierWindow.

        :param tier: (sppasTier) Tier to analyze

        """
        if isinstance(tier, sppasTier) is False:
            raise sppasTypeError(tier, "sppasTier")

        if tier.is_disjoint():
            raise NotImplementedError('sppasTierWindow does not support disjoint interval tiers.')

        self.__tier = tier

    # -----------------------------------------------------------------------
    # Utility methods
    # -----------------------------------------------------------------------

    @staticmethod
    def drange(x, y, jump):
        """Mimics 'range' with either float or int values.

        :param x: start value
        :param y: end value
        :param jump: step value

        """
        if isinstance(jump, int):
            x = int(x)
            y = int(y)
            while x < y:
                yield x
                x += jump

        elif isinstance(jump, float):
            x = decimal.Decimal(x)
            y = decimal.Decimal(y)
            while x < y:
                yield float(x)
                x += decimal.Decimal(jump)

    # -----------------------------------------------------------------------

    def search_for_annotations(self, start_time, end_time, delta=0.5, ignore=[]):
        """Return the annotation set among the given interval.

        :param start_time: (int/float)
        :param end_time: (int/float)
        :param delta: (float) Rate of time the annotation must overlap
        :param ignore: (list of str) List of tag contents to ignore -- currently applied only on the best tag
        :returns: (sppasAnnSet) The annotations matching all the requirements

        """
        ann_set = sppasAnnSet()

        # find annotations on the current time interval
        anns = self.__tier.find(start_time, end_time, overlaps=True)
        if len(anns) == 0:
            return ann_set

        # remove overlapping annotations if not overlapping enough
        for ann in reversed(anns):
            begin = ann.get_lowest_localization().get_midpoint()
            dur = ann.get_location().get_best().duration().get_value()
            overlap_point = float(begin) + (float(dur) * delta)
            if overlap_point < float(start_time) or overlap_point > float(end_time):
                anns.remove(ann)

        if len(anns) == 0:
            return ann_set

        # check the tag content then append
        for a in anns:
            if a.label_is_filled():
                tag_content = a.get_best_tag().get_typed_content()
                if tag_content not in ignore:
                    ann_set.append(a, list())
            else:
                ann_set.append(a, list())

        return ann_set

    # -----------------------------------------------------------------------

    def continuous_anchor_split(self, separators):
        """Return all time intervals within a window given by separators.

        :param separators: (list) list of separators
        :returns: (List of intervals)

        """
        if isinstance(separators, list) is False:
            raise sppasTypeError(separators, list)

        begin = self.__tier.get_first_point()
        end = begin
        prev_ann = None
        intervals = list()
        # is_point = self.__tier.is_point()

        for ann in self.__tier:

            tag = None
            if ann.label_is_filled():
                tag = ann.get_best_tag()

            if prev_ann is not None:
                # if no tag or stop tag or hole between prev_ann and ann
                if tag.get_typed_content() in separators:
                    # tag is None or prev_ann.get_highest_localization() < ann.get_lowest_localization():
                    if end > begin:
                        intervals.append((begin.get_midpoint(),
                                          prev_ann.get_highest_localization().get_midpoint()))

                    #if tag is None or
                    if tag.get_typed_content() in separators:
                        begin = ann.get_highest_localization()
                    else:
                        begin = ann.get_lowest_localization()
            else:
                # can start with a non-labelled interval!
                # if tag is None or \
                if tag.get_typed_content() in separators:
                    begin = ann.get_highest_localization()

            end = ann.get_highest_localization()
            prev_ann = ann

        if end > begin:
            ann = self.__tier[-1]
            end = ann.get_highest_localization()
            intervals.append((begin.get_midpoint(), end.get_midpoint()))

        return intervals

    # -----------------------------------------------------------------------
    # Split methods
    # -----------------------------------------------------------------------

    def time_split(self, duration, step, delta=0.6):
        """Return a set of annotations within a time window.

        :param duration: (float) the duration of a window
        :param step: (float) the step duration
        :param delta: (float) percentage of confidence for an overlapping label
        :returns: (sppasAnnSet) Set of sppasAnnotation
        :raises: sppasTypeError, ValueError

        """
        if self.__tier.is_int() is True and isinstance(duration, int) is False:
            raise sppasTypeError(duration, "int")
        if self.__tier.is_float() is True and isinstance(duration, float) is False:
            raise sppasTypeError(duration, "float")

        # todo: test duration > step

        ann_set_list = list()
        start_time = self.__tier.get_first_point().get_midpoint()
        end_time = self.__tier.get_last_point().get_midpoint()

        for i in sppasTierWindow.drange(start_time, end_time, step):

            ann_set = self.search_for_annotations(i, i+duration, delta)
            ann_set_list.append(ann_set)

            # Stop if end!
            if i+duration > end_time:
                break

        return ann_set_list

    # -----------------------------------------------------------------------

    def anchor_split(self, duration=1, step=1, separators=[SIL_ORTHO]):
        """Return a set of annotations within a window given by separators.

        :param duration: (int) the duration of a window - number of intervals among the separators
        :param step: (int) the step duration - number of intervals
        :param separators: (list) list of separators
        :returns: (List of sppasAnnSet)

        """
        ann_set_list = list()
        intervals = self.continuous_anchor_split(separators)

        for i in range(0, len(intervals)+1, step):

            end_idx = min(i+duration-1, len(intervals)-1)

            ann_set = self.search_for_annotations(
                intervals[i][0], intervals[end_idx][1],
                delta=0.1, ignore=separators
            )
            ann_set_list.append(ann_set)

            # Stop if end!
            if end_idx == len(intervals)-1:
               break

        return ann_set_list

