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

from sppas.src.ui import sppasTrash
from sppas.src.files import FileRoot, FileName

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.annotations.TGA import TimeGroupAnalysis

# ---------------------------------------------------------------------------


def tier_to_intervals(tier, segments=None):
    """Create a tier in which the intervals contains the numbers.

    :param tier: (sppasTier)
    :param segments: (sppasTier) Use this tier to create the intervals
    :returns: (sppasTier, sppasTier) Time segments, NOT time segments

    """
    # Create the tier with the intervals (from segments)
    if segments is None:
        intervals = tier.export_to_intervals(list())
        intervals.set_name("Values")
    else:
        intervals = sppasTier("Values")
        for ann in segments:
            if ann.label_is_filled():
                intervals.create_annotation(ann.get_location().copy())

    # Fill in the intervals with the values of the tier
    for i, interval in enumerate(intervals):
        tier_anns = tier.find(interval.get_lowest_localization(),
                              interval.get_highest_localization(),
                              overlaps=True)
        for ann in tier_anns:
            for label in ann.get_labels():
                interval.append_label(label)

    # Not Intervals
    not_intervals = intervals.export_unfilled()
    not_intervals.set_name("NotValues")

    # first "unfilled" interval
    begin = tier[0].get_lowest_localization()
    prev_ann = intervals[0]
    prev_begin = prev_ann.get_lowest_localization()
    if prev_begin > begin:
        not_intervals.create_annotation(
            sppasLocation(sppasInterval(begin, prev_begin))
        )

    # last "unfilled" interval
    end = tier[-1].get_highest_localization()
    prev_end = intervals[-1].get_highest_localization()
    if prev_end < end:
        not_intervals.create_annotation(
            sppasLocation(sppasInterval(prev_end, end))
        )

    # Fill in the intervals with the values of the tier
    for i, interval in enumerate(not_intervals):
        tier_anns = tier.find(interval.get_lowest_localization(),
                              interval.get_highest_localization(),
                              overlaps=False)
        for ann in tier_anns:
            for label in ann.get_labels():
                interval.append_label(label)

    return intervals, not_intervals

# ---------------------------------------------------------------------------


def intervals_to_numbers(tier):
    """Return a dict with interval'names and numbers and a tier with names.

    :param tier: (sppasTier) Tier with intervals containing the numbers
    :returns: (dict, sppasTier)

    """
    numbers = dict()
    groups = sppasTier("StatGroup")
    for i, ann in enumerate(tier):
        name = "st_" + str(i+1)
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

    parser.add_argument("-s",
                        metavar="segments",
                        required=False,
                        help="Name of a tier with the time segments.")

    parser.add_argument("-p",
                        metavar="pattern",
                        required=False,
                        default="sg",
                        help="Pattern of the output file.")

    parser.add_argument("--notsegments",
                        action="store_true",
                        help="Create a tier with the not-selected intervals")

    parser.add_argument("--occ",
                        action="store_true",
                        help="Estimate the number of values in the intervals.")

    parser.add_argument("--mean",
                        action="store_true",
                        help="Estimate the mean of the intervals.")

    parser.add_argument("--stdev",
                        action="store_true",
                        help="Estimate the standard deviation of the intervals.")

    parser.add_argument("--curve",
                        action="store_true",
                        help="Estimate the intercept and the slope of the intervals.")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 2:
        sys.argv.append('-h')

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Read the input data
    # -----------------------------------------------------------------------

    print("Apply StatsGroup on file {:s}".format(args.i))
    parser = sppasRW(args.i)
    trs_input = parser.read()
    print("   - StatsGroup is reading the data...")
    tier = trs_input.find(args.t, case_sensitive=False)
    if tier is None:
        print("ERROR: A tier with name '{:s}' wasn't found.".format(args.t))
        sys.exit(1)

    trs_out = sppasTranscription("StatsGroups")

    # -----------------------------------------------------------------------
    # Convert input data and estimate stats
    # -----------------------------------------------------------------------

    # Create a tier with the appropriate intervals.
    # Each interval contains the list of numbers (= inside the labels)
    segments = None
    if args.s:
        segments = trs_input.find(args.s, case_sensitive=False)
        if segments is None:
            print("ERROR: A tier with name '{:s}' wasn't found.".format(args.s))
            sys.exit(1)
    intervals, not_intervals = tier_to_intervals(tier, segments)
    intervals.set_meta('intervals_from_tier', tier.get_name())
    trs_out.append(intervals)
    if args.notsegments:
        not_intervals.set_meta('not_intervals_from_tier', tier.get_name())
        trs_out.append(not_intervals)

    if args.occ or args.mean or args.stdev or args.curve:

        # Extract numbers into a dict
        print("   - StatsGroup is creating the groups...")
        numbers, groups = intervals_to_numbers(intervals)
        trs_out.append(groups)
        trs_out.add_hierarchy_link("TimeAssociation", intervals, groups)

        # Estimate stats
        print("   - StatsGroup is estimating the stats...")
        ts = TimeGroupAnalysis(numbers)

        # --------------------------------------------------------------------
        # Convert stats into tiers
        # --------------------------------------------------------------------

        # Put TGA results into tiers
        if args.occ:
            tier = tga_to_tier(ts.len(), groups, "Occurrence", "int")
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

    # -----------------------------------------------------------------------
    # Save the result
    # -----------------------------------------------------------------------

    print("   - StatsGroup is saving the result...")
    fn = FileName(args.i)
    name = fn.get_name()
    pattern = FileRoot.pattern(name)
    p = args.p
    if p.startswith("-") is False:
        p = "-" + p
    if len(pattern) > 0:
        name = name.replace(pattern, p)
    else:
        name = name + p
    output = os.path.join(fn.folder(), name + fn.get_extension())
    if os.path.exists(output):
        print("A file with name {:s} is already existing.".format(name))
        trash_filename = sppasTrash().put_file_into(output)
        print("This file is moved into the Trash of SPPAS: "
              "{:s}".format(trash_filename))

    p = sppasRW(output)
    p.write(trs_out)
    print("Result saved in file: {:s}".format(output))
