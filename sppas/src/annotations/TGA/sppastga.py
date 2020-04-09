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

    src.annotations.TGA.sppastga.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import symbols
from sppas.src.utils.makeunicode import sppasUnicode
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel
from sppas.src.anndata.aio.aioutils import serialize_labels

from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyOutputError

from .timegroupanalysis import TimeGroupAnalysis

# ----------------------------------------------------------------------------


class sppasTGA(sppasBaseAnnotation):
    """Estimate TGA on a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create time groups then map them into a dictionary where:

        - key is a label assigned to the time group;
        - value is the list of observed durations of segments in this TG.

    """

    def __init__(self, log=None):
        """Create a new sppasTGA instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasTGA, self).__init__("tga.json", log)

        # List of the symbols used to create the time groups
        self._tg_separators = list(symbols.phone.keys())

        # for backward compatibility, we can't simply use the symbols.phone
        self._tg_separators.append('#')
        self._tg_separators.append('@@')
        self._tg_separators.append('+')
        self._tg_separators.append('gb')
        self._tg_separators.append('lg')
        self._tg_separators.append('_')

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - with_radius
            - original
            - annotationpro
            - tg_prefix_label

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "with_radius" == key:
                self.set_with_radius(opt.get_value())

            elif "original" == key:
                self.set_intercept_slope_original(opt.get_value())

            elif "annotationpro" == key:
                self.set_intercept_slope_annotationpro(opt.get_value())

            elif "tg_prefix_label" == key:
                self.set_tg_prefix_label(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_tg_prefix_label(self, prefix):
        """Fix the prefix to add to each TG.

        :param prefix: (str) Default is 'tg_'

        """
        sp = sppasUnicode(prefix)
        tg = sp.to_strip()
        if len(tg) > 0:
            self._options['tg_prefix_label'] = tg

    # -----------------------------------------------------------------------

    def set_with_radius(self, with_radius):
        """Set the with_radius option, used to estimate the duration.

        :param with_radius: (int)

        - 0 means to use Midpoint;
        - negative value means to use R-;
        - positive radius means to use R+.

        """
        try:
            w = int(with_radius)
            self._options['with_radius'] = w
        except ValueError:
            raise

    # -----------------------------------------------------------------------

    def set_intercept_slope_original(self, value):
        """Estimate intercepts and slopes with the original method.

        Default is False.

        :param value: (boolean)

        """
        self._options['original'] = bool(value)

    # -----------------------------------------------------------------------

    def set_intercept_slope_annotationpro(self, value):
        """Estimate intercepts and slopes with the method of annotationpro.

        Default is True.

        :param value: (boolean)

        """
        self._options['annotationpro'] = bool(value)

    # -----------------------------------------------------------------------
    # Workers
    # -----------------------------------------------------------------------

    def syllables_to_timegroups(self, syllables):
        """Create the time group intervals.

        :param syllables: (sppasTier)
        :returns: (sppasTier) Time groups

        """
        intervals = syllables.export_to_intervals(self._tg_separators)
        intervals.set_name("TGA-TimeGroups")

        for i, tg in enumerate(intervals):
            tag_str = self._options['tg_prefix_label']
            tag_str += str(i+1)
            tg.append_label(sppasLabel(sppasTag(tag_str)))

        return intervals

    # ----------------------------------------------------------------------

    def syllables_to_timesegments(self, syllables):
        """Create the time segments intervals.

        Time segments are time groups with serialized syllables.

        :param syllables:
        :returns: (sppasTier) Time segments

        """
        intervals = syllables.export_to_intervals(self._tg_separators)
        intervals.set_name("TGA-TimeSegments")

        for i, tg in enumerate(intervals):
            syll_anns = syllables.find(tg.get_lowest_localization(),
                                       tg.get_highest_localization())
            tag_str = ""
            for ann in syll_anns:
                tag_str += serialize_labels(ann.get_labels(), separator=" ")
                tag_str += " "
            tg.append_label(sppasLabel(sppasTag(tag_str)))

        return intervals

    # ----------------------------------------------------------------------

    def timegroups_to_durations(self, syllables, timegroups):
        """Return a dict with timegroups and the syllable durations.

        :param syllables: (sppasTier) Syllables
        :param timegroups: (sppasTier) Time groups
        :returns: (dict)

        """
        tg_dur = dict()
        for tg_ann in timegroups:
            tg_label = serialize_labels(tg_ann.get_labels())
            tg_dur[tg_label] = list()
            syll_anns = syllables.find(tg_ann.get_lowest_localization(),
                                       tg_ann.get_highest_localization())
            for syll_ann in syll_anns:
                loc = syll_ann.get_location().get_best()

                # Fix the duration value of this syllable
                dur = loc.duration()
                value = dur.get_value()
                if self._options['with_radius'] < 0:
                    value -= dur.get_margin()
                if self._options['with_radius'] > 0:
                    value += dur.get_margin()

                # Append in the list of values of this TG
                tg_dur[tg_label].append(value)

        return tg_dur

    # -----------------------------------------------------------------------

    @staticmethod
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
            tg_label = serialize_labels(tg_ann.get_labels())
            tag_value = tga_result[tg_label]
            if tag_type == "float":
                tag_value = round(tag_value, 5)

            tier.create_annotation(
                tg_ann.get_location().copy(),
                sppasLabel(sppasTag(tag_value, tag_type)))

        return tier

    # ----------------------------------------------------------------------

    @staticmethod
    def tga_to_tier_reglin(tga_result, timegroups, intercept=True):
        """Create tiers of intercept,slope from one of the TGA result.

        :param tga_result: One of the results of TGA
        :param timegroups: (sppasTier) Time groups
        :param intercept: (boolean) Export the intercept.
        If False, export Slope.

        :returns: (sppasTier)

        """
        if intercept is True:
            tier = sppasTier('TGA-Intercept')
        else:
            tier = sppasTier('TGA-Slope')

        for tg_ann in timegroups:
            tg_label = serialize_labels(tg_ann.get_labels())
            loc = tg_ann.get_location().copy()
            if intercept is True:
                tag_value = tga_result[tg_label][0]
            else:
                tag_value = tga_result[tg_label][1]

            tag_value = round(tag_value, 5)
            tier.create_annotation(loc,
                                   sppasLabel(sppasTag(tag_value, "float")))

        return tier

    # ----------------------------------------------------------------------

    def convert(self, syllables):
        """Estimate TGA on the given syllables.

        :param syllables: (sppasTier)
        :returns: (sppasTranscription)

        """
        trs_out = sppasTranscription("TimeGroupAnalyser")

        # Create the time groups: intervals of consecutive syllables
        timegroups = self.syllables_to_timegroups(syllables)
        timegroups.set_meta('timegroups_of_tier', syllables.get_name())
        trs_out.append(timegroups)

        # Create the time segments
        timesegs = self.syllables_to_timesegments(syllables)
        trs_out.append(timesegs)
        # trs_out.add_hierarchy_link("TimeAssociation", timegroups, timesegs)

        # Get the duration of each syllable, grouped into the timegroups
        tg_dur = self.timegroups_to_durations(syllables, timegroups)
        # here, we could add an option to add durations and
        # delta durations into the transcription output

        # Estimate TGA
        ts = TimeGroupAnalysis(tg_dur)

        # Put TGA non-optional results into tiers
        tier = sppasTGA.tga_to_tier(ts.len(), timegroups, "TGA-Occurrences", "int")
        trs_out.append(tier)
        # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = sppasTGA.tga_to_tier(ts.total(), timegroups, "TGA-Total")
        trs_out.append(tier)
        # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = sppasTGA.tga_to_tier(ts.mean(), timegroups, "TGA-Mean")
        trs_out.append(tier)
        # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = sppasTGA.tga_to_tier(ts.median(), timegroups, "TGA-Median")
        trs_out.append(tier)
        # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = sppasTGA.tga_to_tier(ts.stdev(), timegroups, "TGA-StdDev")
        trs_out.append(tier)
        # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        tier = sppasTGA.tga_to_tier(ts.nPVI(), timegroups, "TGA-nPVI")
        trs_out.append(tier)
        # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        # Put TGA Intercept/Slope results
        if self._options['original'] is True:
            tier = sppasTGA.tga_to_tier_reglin(
                ts.intercept_slope_original(),
                timegroups,
                True)
            tier.set_name('TGA-Intercept_original')
            trs_out.append(tier)
            # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

            tier = sppasTGA.tga_to_tier_reglin(
                ts.intercept_slope_original(),
                timegroups,
                False)
            tier.set_name('TGA-slope_original')
            trs_out.append(tier)
            # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        if self._options['annotationpro'] is True:
            tier = sppasTGA.tga_to_tier_reglin(
                ts.intercept_slope(),
                timegroups,
                True)
            tier.set_name('TGA-Intercept_timestamps')
            trs_out.append(tier)
            # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

            tier = sppasTGA.tga_to_tier_reglin(
                ts.intercept_slope(),
                timegroups,
                False)
            tier.set_name('TGA-slope_timestamps')
            trs_out.append(tier)
            # trs_out.add_hierarchy_link("TimeAssociation", timegroups, tier)

        return trs_out

    # ----------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) syllabification
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get the tier to syllabify
        parser = sppasRW(input_file[0])
        trs_input = parser.read()
        tier_input = sppasFindTier.aligned_syllables(trs_input)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('tga_result_of', input_file[0])

        # Estimate TGA on the tier
        trs_output = self.convert(tier_input)

        # Save in a file
        if output_file is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_file)
                parser.write(trs_output)
            else:
                raise EmptyOutputError

        return trs_output

    # ----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-tga")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "-syll")
