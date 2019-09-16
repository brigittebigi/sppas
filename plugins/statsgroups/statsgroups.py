#!/usr/bin/env python
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

    statsgroups.py
    ~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2019  Brigitte Bigi
:summary:      Estimate stats on sequences of numerical annotations

"""

import logging
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

if os.path.exists(SPPAS) is False:
    print("ERROR: SPPAS not found.")
    sys.exit(1)
sys.path.append(SPPAS)

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.annotations.TGA import TimeGroupAnalysis

# ---------------------------------------------------------------------------


def tier_to_intervals(tier):
    """Create a tier in which the intervals contains the numbers.

    :param tier: (sppasTier)
    :returns: (sppasTier) Time segments

    """
    intervals = tier.export_to_intervals(list())
    intervals.set_name("Values")

    for i, interval in enumerate(intervals):
        tier_anns = tier.find(interval.get_lowest_localization(),
                              interval.get_highest_localization())
        for ann in tier_anns:
            for label in ann.get_labels():
                interval.append_label(label)

    return intervals

# ---------------------------------------------------------------------------


def intervals_to_numbers(tier):
    """Return a dict with interval'names and numbers and a tier with names.

    :param tier: (sppasTier) Tier with intervals containing the numbers
    :returns: (dict, sppasTier)

    """
    numbers = dict()
    groups = sppasTier("Indexes")
    for i, ann in enumerate(tier):
        name = str(i+1)
        groups.create_annotation(ann.get_location().copy(),
                                 sppasLabel(sppasTag(name)))
        numbers[name] = list()
        for label in ann.get_labels():
            tag = label.get_best()
            str_value = tag.get_content()
            try:
                value = float(str_value)
            except ValueError:
                raise ValueError("The tier contains a non-numerical label "
                                 "{:s}".format(str_value))
            # Append in the list of values of this interval
            numbers[name].append(value)

    return numbers, groups

# ---------------------------------------------------------------------------


def tga_to_tier(tga_result, timegroups, tier_name, tag_type="float"):
    """Create a tier from one of the TGA result.

    :param tga_result: One of the results of TGA
    :param timegroups: (sppasTier) Time groups
    :param tier_name: (str) Name of the output tier
    :param tag_type: (str) Type of the sppasTag to be included

    :returns: (sppasTier)

    """
    tier = sppasTier(tier_name)

    for tg_ann in timegroups:
        tg_label = tg_ann.serialize_labels()
        tag_value = tga_result[tg_label]
        if tag_type == "float":
            tag_value = round(tag_value, 5)

        tier.create_annotation(
            tg_ann.get_location().copy(),
            sppasLabel(sppasTag(tag_value, tag_type)))

    return tier

# ---------------------------------------------------------------------------


def tga_to_tiers_reglin(tga_result, timegroups):
    """Create tiers of intercept,slope from one of the TGA result.

    :param tga_result: One of the results of TGA
    :param timegroups: (sppasTier) Time groups

    :returns: (sppasTier, sppasTier)

    """
    tierI = sppasTier('Intercept')
    tierS = sppasTier('Slope')

    for tg_ann in timegroups:
        tg_label = tg_ann.serialize_labels()
        loc = tg_ann.get_location().copy()

        tag_value_I = round(tga_result[tg_label][0], 5)
        tierI.create_annotation(loc, sppasLabel(sppasTag(tag_value_I, "float")))

        tag_value_S = round(tga_result[tg_label][1], 5)
        tierS.create_annotation(loc, sppasLabel(sppasTag(tag_value_S, "float")))

    return tierI, tierS

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s -i file [options]",
        description=" ... a program to estimate stats on intervals",
    )

    # Required parameters
    # ------------------------------------------------------

    parser.add_argument("-i",
                        metavar="file",
                        required=True,
                        help='Input annotated file name.')

    parser.add_argument("-t",
                        metavar="tier",
                        required=True,
                        help="Name of the tier with the numbers.")

    # Optional parameters
    # ------------------------------------------------------

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    parser.add_argument("--occ",
                        #metavar="bool",
                        #required=False,
                        #default=True,
                        #type=bool,
                        action="store_true",
                        help="Estimate the number of values in the intervals.")

    parser.add_argument("--mean",
                        #metavar="bool",
                        #required=False,
                        #default=True,
                        #type=bool,
                        action="store_true",
                        help="Estimate the mean of the intervals.")

    parser.add_argument("--stdev",
                        #metavar="bool",
                        #required=False,
                        #default=False,
                        #type=bool,
                        action="store_true",
                        help="Estimate the standard deviation of the intervals.")

    parser.add_argument("--curve",
                        #metavar="bool",
                        #required=False,
                        #default=True,
                        #type=bool,
                        action="store_true",
                        help="Estimate the intercept and the slope of the intervals.")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 2:
        sys.argv.append('-h')

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # The main is here:
    # -----------------------------------------------------------------------

    parser = sppasRW(args.i)
    trs_input = parser.read()
    tier = trs_input.find(args.t, case_sensitive=False)
    if tier is None:
        print("ERROR: A tier with name '{:s}' wasn't found.".format(args.t))
        sys.exit(1)

    trs_out = sppasTranscription("StatsGroups")

    # Create a tier with the appropriate intervals.
    # Each interval contains the list of numbers (= inside the labels)
    intervals = tier_to_intervals(tier)
    intervals.set_meta('intervals_from_tier', tier.get_name())
    trs_out.append(intervals)

    # Extract numbers into a dict
    numbers, groups = intervals_to_numbers(intervals)
    trs_out.append(groups)
    trs_out.add_hierarchy_link("TimeAssociation", intervals, groups)

    # Estimate stats
    ts = TimeGroupAnalysis(numbers)

    # Put TGA results into tiers
    if args.occ:
        tier = tga_to_tier(ts.len(), groups, "Occurrences", "int")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", intervals, tier)

    if args.mean:
        tier = tga_to_tier(ts.mean(), groups, "Mean")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", intervals, tier)

    if args.stdev:
        tier = tga_to_tier(ts.stdev(), groups, "StdDev")
        trs_out.append(tier)
        trs_out.add_hierarchy_link("TimeAssociation", intervals, tier)

    if args.curve:
        tierI, tierS = tga_to_tiers_reglin(ts.intercept_slope_original(), groups)
        trs_out.append(tierI)
        trs_out.add_hierarchy_link("TimeAssociation", intervals, tierI)
        trs_out.append(tierS)
        trs_out.add_hierarchy_link("TimeAssociation", intervals, tierS)

    for tier in trs_out:
        print(tier.get_name())
        for ann in tier:
            print(ann)
