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

    src.analysis.tierfilters.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from sppas.src.exceptions import sppasKeyError

from sppas.src.utils import u
from sppas.src.structs import sppasBaseFilters

from sppas.src.anndata.ann.annset import sppasAnnSet
from sppas.src.anndata.ann.annlabel import sppasTagCompare
from sppas.src.anndata.ann.annlocation import sppasDurationCompare
from sppas.src.anndata.ann.annlocation import sppasLocalizationCompare
from sppas.src.anndata.ann.annlocation import sppasIntervalCompare

# ---------------------------------------------------------------------------


class SingleFilterTier(object):
    """This class applies predefined filters on a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Apply defined filters, as a list of tuples with:
        - name of the filter: one of "tag", "loc", "dur", "rel"
        - name of the function in sppasCompare (equal, lt, ...)
        - value of its expected type (str, float, int, bool)

    """

    functions = ("tag", "loc", "dur")

    def __init__(self, filters, annot_format=False, match_all=True):
        """Filter process of a tier.

        :param filters: (list) List of tuples (filter, function, [typed values])
        :param annot_format: (bool) The annotation result contains the
        name of the filter (if True) or the original label (if False)
        :param match_all: (bool) The annotations must match all the filters
        (il set to True) or any of them (if set to False)

        """
        self.__filters = filters
        self.__match_all = bool(match_all)
        self.__annot_format = bool(annot_format)

    # -----------------------------------------------------------------------

    def filter_tier(self, tier, out_tiername="Filtered"):
        """Apply the filters on the given tier.

        Applicable functions are "tag", "loc" and "dur".

        :param tier: (sppasTier)
        :param out_tiername: (str) Name or the filtered tier
        :return: sppasTier or None if no annotation is matching

        """
        for f in self.__filters:
            if f[0] not in SingleFilterTier.functions:
                raise ValueError("{:s} is not a Single Filter and can't be "
                                 "applied".format(f[0]))

        logging.info("Apply sppasTiersFilter() on tier: {:s}".format(tier.get_name()))

        # Apply each filter and append the result in a list of annotation sets
        ann_sets = list()
        sfilter = sppasTierFilters(tier)

        for f in self.__filters:

            if len(f[2]) == 0:
                raise ValueError("No value defined for filter {:s}".format(f[0]))

            value = sppasTierFilters.cast_data(tier, f[0], f[2][0])
            if type(value) != type(f[2][0]):
                raise TypeError(
                    "Types error: tier is {:s} but filter value is {:s}."
                    "".format(type(value), type(f[2][0])))

            # a little bit of doc:
            #   - getattr() returns the value of the named attributed of object:
            #     it returns f.tag if called like getattr(f, "tag")
            #   - func(**{'x': '3'}) is equivalent to func(x='3')
            #
            logging.info(" >>> filter.{:s}({:s}={!s:s})".format(f[0], f[1], value))

            ann_set = getattr(sfilter, f[0])(**{f[1]: value})
            for i in range(1, len(f[2])):
                value = sppasTierFilters.cast_data(tier, f[0], f[2][i])
                logging.info(" >>>    | filter.{:s}({:s}={!s:s})".format(f[0], f[1], value))
                ann_set = ann_set | getattr(sfilter, f[0])(**{f[1]: value})
            ann_sets.append(ann_set)

        # no annotation is matching
        if len(ann_sets) == 0:
            return None

        # Merge results (apply '&' or '|' on the resulting annotation sets)
        ann_set = ann_sets[0]
        if self.__match_all:
            for i in range(1, len(ann_sets)):
                ann_set = ann_set & ann_sets[i]
                if len(ann_set) == 0:
                    return None
        else:
            for i in range(1, len(ann_sets)):
                ann_set = ann_set | ann_sets[i]

        # convert the annotation sets into a tier
        filtered_tier = ann_set.to_tier(name=out_tiername,
                                        annot_value=self.__annot_format)

        return filtered_tier

# ---------------------------------------------------------------------------


class RelationFilterTier(object):
    """This class applies predefined filters on a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    functions = ("rel")

    def __init__(self, filters, annot_format=False):
        """Filter process of a tier.

        :param filters: (tuple) ([list of functions], [list of options])
        each option is a tuple with (name, value)
        :param annot_format: (bool) The annotation result contains the
        name of the filter (if True) or the original label (if False)

        """
        self.__filters = filters
        self.__annot_format = bool(annot_format)

    # -----------------------------------------------------------------------

    def filter_tier(self, tier, tier_y, out_tiername="Filtered"):
        """Apply the filters on the given tier.

        :param tier: (sppasTier)
        :param tier_y: (sppasTier)
        :param out_tiername: (str) Name or the filtered tier

        """
        logging.info("Apply sppasTiersFilter() on tier: {:s}".format(tier.get_name()))
        sfilter = sppasTierFilters(tier)

        ann_set = sfilter.rel(
            tier_y,
            *(self.__filters[0]),
            **{self.__filters[1][i][0]: self.__filters[1][i][1] for i in range(len(self.__filters[1]))})

        # convert the set of annotations into a tier
        filtered_tier = ann_set.to_tier(name=out_tiername,
                                        annot_value=self.__annot_format)

        return filtered_tier

# ---------------------------------------------------------------------------


class sppasTierFilters(sppasBaseFilters):
    """This class implements the 'SPPAS tier filter system'.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Search in tiers. The class sppasTierFilters() allows to apply several types
    of filter (tag, duration, ...), and the class sppasAnnSet() is a data set
    manager, i.e. it contains the annotations selected by a filter and a
    string representing the filter.

    Create a filter:

        >>> f = sppasTierFilters(tier)

    then, apply a filter with some pattern like in the following examples.
    sppasAnnSet() can be combined with operators & and |, like for any other
    'set' in Python, 'an unordered collection of distinct hashable objects'.

    :Example1: extract silences:

        >>> f.tag(exact=u('#')))

    :Example2: extract silences more than 200ms

        >>> f.tag(exact=u("#")) & f.dur(gt=0.2)

    :Example3: find the annotations with at least a label with a tag
    starting by "pa" and ending by "a" like "pa", "papa", "pasta", etc:

        >>> f.tag(startswith="pa", endswith='a')

    It's equivalent to write:

        >>> f.tag(startswith="pa", endswith='a', logic_bool="and")

    The classical "and" and "or" logical boolean predicates are accepted;
    "and" is the default one. It defines whether all the functions must
    be True ("and") or any of them ("or").

    The result of the two previous lines of code is the same, but two
    times faster, compared to use this one:

        >>> f.tag(startswith="pa") & f.tag(endswith='a')

    In the first case, for each tag, the method applies the logical boolean
    between two predicates and creates the data set matching the combined
    condition. In the second case, each call to the method creates a data
    set matching each individual condition, then the data sets are
    combined.

    """

    def __init__(self, obj):
        """Create a sppasTierFilters instance.

        :param obj: (sppasTier) The tier to be filtered.

        """
        super(sppasTierFilters, self).__init__(obj)

    # -----------------------------------------------------------------------

    def tag(self, **kwargs):
        """Apply functions on all tags of all labels of annotations.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.tag(startswith="pa", not_endswith='a', logic_bool="and")
            >>> f.tag(startswith="pa") & f.tag(not_endswith='a')
            >>> f.tag(startswith="pa") | f.tag(startswith="ta")

        :param kwargs: logic_bool/any sppasTagCompare() method.
        :returns: (sppasAnnSet)

        """
        comparator = sppasTagCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        tag_logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        label_logic_bool = sppasBaseFilters.fix_logic_bool_label(**kwargs)
        tag_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        tag_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        data = sppasAnnSet()

        # search for the annotations to be returned:
        for annotation in self.obj:

            is_matching = False

            # "any" or "all" labels can match
            for label in annotation.get_labels():

                is_matching = label.match(tag_functions, tag_logic_bool)

                # do not test the next labels if...
                if is_matching is True and label_logic_bool == "any":
                    # if at least one is matching
                    break
                if is_matching is False and label_logic_bool == "all":
                    # if one is not matching
                    break

            if is_matching is True:
                data.append(annotation, tag_fct_values)

        return data

    # -----------------------------------------------------------------------

    def dur(self, **kwargs):
        """Apply functions on durations of the location of annotations.

        :param kwargs: logic_bool/any sppasDurationCompare() method.
        :returns: (sppasAnnSet)

        Examples:
            >>> f.dur(ge=0.03) & f.dur(le=0.07)
            >>> f.dur(ge=0.03, le=0.07, logic_bool="and")

        """
        comparator = sppasDurationCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        dur_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        dur_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        data = sppasAnnSet()

        # search for the annotations to be returned:
        for annotation in self.obj:

            location = annotation.get_location()
            is_matching = location.match_duration(dur_functions, logic_bool)
            if is_matching is True:
                data.append(annotation, dur_fct_values)

        return data

    # -----------------------------------------------------------------------

    def loc(self, **kwargs):
        """Apply functions on localizations of annotations.

        :param kwargs: logic_bool/any sppasLocalizationCompare() method.
        :returns: (sppasAnnSet)

        :Example:

            >>> f.loc(rangefrom=3.01) & f.loc(rangeto=10.07)
            >>> f.loc(rangefrom=3.01, rangeto=10.07, logic_bool="and")

        """
        comparator = sppasLocalizationCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        loc_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        loc_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        data = sppasAnnSet()

        # search for the annotations to be returned:
        for annotation in self.obj:

            location = annotation.get_location()
            is_matching = location.match_localization(loc_functions, logic_bool)
            if is_matching is True:
                data.append(annotation, loc_fct_values)

        return data

    # -----------------------------------------------------------------------

    def rel(self, other_tier, *args, **kwargs):
        """Apply functions of relations between localizations of annotations.

        :param other_tier: the tier to be in relation with.
        :param args: any sppasIntervalCompare() method.
        :param kwargs: any option of the methods.
        :returns: (sppasAnnSet)

        :Example:

            >>> f.rel(other_tier, "equals",
            >>>                   "overlaps",
            >>>                   "overlappedby", min_overlap=0.04)

        """
        comparator = sppasIntervalCompare()

        # extract the information from the arguments
        rel_functions = sppasTierFilters.__fix_relation_functions(comparator, *args)

        data = sppasAnnSet()

        # search for the annotations to be returned:
        for annotation in self.obj:

            location = annotation.get_location()
            match_values = sppasTierFilters.__connect(location,
                                                      other_tier,
                                                      rel_functions,
                                                      **kwargs)
            if len(match_values) > 0:
                data.append(annotation, list(set(match_values)))

        return data

    # -----------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def cast_data(tier, sfilter, entry):
        """Return an entry into the appropriate type.

        :param tier: (sppasTier)
        :param sfilter: (str) Name of the filter (tag, loc, ...)
        :param entry: (str) The entry to cast
        :returns: typed entry

        """
        if sfilter == "tag":
            if tier.is_float():
                return float(entry)
            elif tier.is_int():
                return int(entry)
            elif tier.is_bool():
                return bool(entry)

        elif sfilter == "loc":
            p = tier.get_first_point()
            if isinstance(p.get_midpoint(), int):
                return int(entry)
            else:
                return float(entry)

        elif sfilter == "dur":
            return float(entry)

        return u(entry)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def __fix_relation_functions(comparator, *args):
        """Parse the arguments to get the list of function/complement."""
        f_functions = list()
        for func_name in args:

            logical_not = False
            if func_name.startswith("not_"):
                logical_not = True
                func_name = func_name[4:]

            if func_name in comparator.get_function_names():
                f_functions.append((comparator.get(func_name),
                                    logical_not))
            else:
                raise sppasKeyError("rel filter args function name", func_name)

        return f_functions

    # -----------------------------------------------------------------------

    @staticmethod
    def __connect(location, other_tier, rel_functions, **kwargs):
        """Find connections between location and the other tier."""
        values = list()
        for other_ann in other_tier:
            for localization, score in location:
                for other_loc, other_score in other_ann.get_location():
                    for func_name, complement in rel_functions:
                        is_connected = func_name(localization,
                                                 other_loc,
                                                 **kwargs)
                        if is_connected:
                            values.append(func_name.__name__)

        return values
