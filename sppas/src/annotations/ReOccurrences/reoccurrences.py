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

"""

from sppas import sppasTier, sppasLocation
from sppas import sppasInterval, sppasPoint
from sppas import sppasLabel, sppasTag


class Reoccurences(object):

    def __init__(self):
        super(Reoccurences, self).__init__()

    @staticmethod
    def make_reoccurrences(ref_window, comp_window, delta):
        occ = dict()
        reocc = list()
        reoccTier = sppasTier()

        for ann_set_ref in ref_window:
            occ[ann_set_ref] = 0

        for ann_set_ref in ref_window:
            for ann_set_comp in comp_window:
                if len(ann_set_ref & ann_set_comp) != 0 and \
                        len(ann_set_ref & ann_set_comp) / len(ann_set_ref):
                    occ[ann_set_ref] += 1
                    reocc.append(ann_set_comp)

        for ann_set in occ.keys():
            curr_reocc = list()
            for ann_set_comp in reocc:
                if len(ann_set & ann_set_comp) / len(ann_set):
                    curr_reocc.append(ann_set_comp)

            begin = 0.0
            end = 0.0
            i = 0
            for ann in ann_set:
                if i == 0:
                    begin = ann.get_location().get_best().get_begin().get_value()
                elif i == len(ann_set) - 1:
                    end = ann.get_location().get_best().get_end().get_value()

            reoccTier.create_annotation(
                sppasLocation(sppasInterval(sppasPoint(begin), sppasPoint(end))),
                [sppasLabel(sppasTag(begin)), sppasLabel(sppasTag())]
            )
