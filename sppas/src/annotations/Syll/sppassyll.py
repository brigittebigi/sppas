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

    src.annotations.sppassyll.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.config import symbols
from sppas.src.config import annots
from sppas.src.config import annotations_translation

from sppas import sppasRW
from sppas import sppasTranscription
from sppas import sppasTier
from sppas import sppasInterval
from sppas import sppasLocation
from sppas import sppasTag
from sppas import sppasLabel

from sppas.src.utils.makeunicode import sppasUnicode

from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyOutputError

from .syllabify import Syllabifier

# ----------------------------------------------------------------------------

_ = annotations_translation.gettext

# ----------------------------------------------------------------------------

MSG_INVALID = (_(":INFO 1224: "))
MSG_NO_TIER = (_(":INFO 1264: "))

# ----------------------------------------------------------------------------


class sppasSyll(sppasBaseAnnotation):
    """SPPAS integration of the automatic syllabification annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, logfile=None):
        """Create a new sppasSyll instance with only general rules.

        :param logfile: (sppasLog)

        """
        super(sppasSyll, self).__init__(logfile, "Syllabification")

        # Default syllabifier with only general rules
        self.syllabifier = Syllabifier()

        # List of options to configure this automatic annotation
        self._options = dict()
        self._options['usesintervals'] = False
        self._options['usesphons'] = True
        self._options['tiername'] = "TokensAlign"
        self._options['createclasses'] = True

    # -----------------------------------------------------------------------

    def set_rules(self, config_filename):
        """Fix the syllabification rules from a configuration file.

        :param config_filename: Name of the configuration file with the rules

        """
        self.syllabifier = Syllabifier(config_filename)

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - usesintervals
            - usesphons
            - tiername
            - createclasses
            - createstructures

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "usesintervals" == key:
                self.set_usesintervals(opt.get_value())

            elif "usesphons" == key:
                self.set_usesphons(opt.get_value())

            elif "tiername" == key:
                self.set_tiername(opt.get_value())

            elif "createclasses" == key:
                self.set_create_tier_classes(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # ------------------------------------------------------------------------

    def set_usesintervals(self, mode):
        """Fix the usesintervals option.

        :param mode: (bool) If mode is set to True, the syllabification
        operates inside specific (given) intervals.

        """
        self._options['usesintervals'] = mode

    # ----------------------------------------------------------------------

    def set_usesphons(self, mode):
        """Fix the usesphons option.

        :param mode: (str) If mode is set to True, the syllabification operates
        by using only tier with phonemes.

        """
        self._options['usesphons'] = mode

    # ----------------------------------------------------------------------

    def set_create_tier_classes(self, create=True):
        """Fix the createclasses option.

        :param create: (bool)

        """
        self._options['createclasses'] = create

    # ----------------------------------------------------------------------

    def set_tiername(self, tier_name):
        """Fix the tiername option.

        :param tier_name: (str)

        """
        self._options['tiername'] = sppasUnicode(tier_name).to_strip()

    # ----------------------------------------------------------------------
    # Syllabification of time-aligned phonemes stored into a tier
    # ----------------------------------------------------------------------

    def convert(self, phonemes, intervals=None):
        """Syllabify labels of a time-aligned phones tier.

        :param phonemes: (sppasTier) time-aligned phonemes tier
        :param intervals: (sppasTier)
        :returns: (sppasTier)

        """
        if intervals is None:
            intervals = sppasSyll._phon_to_intervals(phonemes)

        syllables = sppasTier("SyllAlign")
        syllables.set_meta('syllabification_of_tier', phonemes.get_name())

        for interval in intervals:

            # get the index of the phonemes containing the begin
            # of the interval
            start_phon_idx = phonemes.lindex(
                interval.get_lowest_localization())
            if start_phon_idx == -1:
                start_phon_idx = phonemes.mindex(
                    interval.get_lowest_localization(),
                    bound=-1)

            # get the index of the phonemes containing the end of the interval
            end_phon_idx = phonemes.rindex(interval.get_highest_localization())
            if end_phon_idx == -1:
                end_phon_idx = phonemes.mindex(
                    interval.get_highest_localization(),
                    bound=1)

            # syllabify within the interval
            if start_phon_idx != -1 and end_phon_idx != -1:
                self.syllabify_interval(phonemes,
                                        start_phon_idx,
                                        end_phon_idx,
                                        syllables)
            else:
                self.print_message(MSG_INVALID.format(interval),
                                   indent=2, status=annots.warning)

        return syllables

    # ----------------------------------------------------------------------

    def make_classes(self, syllables):
        """Create the tier with syllable classes.

        :param syllables: (sppasTier)

        """
        classes = sppasTier("SyllClassAlign")
        classes.set_meta('syllabification_classes_of_tier',
                         syllables.get_name())

        for syll in syllables:
            location = syll.get_location().copy()
            syll_tag = syll.get_best_tag()
            class_tag = sppasTag(
                self.syllabifier.classes_phonetized(
                    syll_tag.get_typed_content()))
            classes.create_annotation(location, sppasLabel(class_tag))

        return classes

    # ----------------------------------------------------------------------

    def syllabify_interval(self, phonemes, from_p, to_p, syllables):
        """Perform the syllabification of one interval.

        :param phonemes: (sppasTier)
        :param from_p: (int) index of the first phoneme to be syllabified
        :param to_p: (int) index of the last phoneme to be syllabified
        :param syllables: (sppasTier)

        """
        # create the sequence of phonemes to syllabify
        p = list()
        for ann in phonemes[from_p:to_p+1]:
            tag = ann.get_best_tag()
            p.append(tag.get_typed_content())

        # create the sequence of syllables
        s = self.syllabifier.annotate(p)

        # add the syllables into the tier
        for i, syll in enumerate(s):
            start_idx, end_idx = syll

            # create the location
            begin = phonemes[start_idx+from_p].get_lowest_localization().copy()
            end = phonemes[end_idx+from_p].get_highest_localization().copy()
            location = sppasLocation(sppasInterval(begin, end))

            # create the label
            syll_string = Syllabifier.phonetize_syllables(p, [syll])
            label = sppasLabel(sppasTag(syll_string))

            # add the syllable
            syllables.create_annotation(location, label)

    # ----------------------------------------------------------------------

    def run(self, input_filename, output_filename=None):
        """Perform the Syllabification process.

        :param input_filename: (str) Input file with the aligned phonemes
        :param output_filename: (str) Resulting file with syllabification

        """
        # Get the tier to syllabify
        parser = sppasRW(input_filename)
        trs_input = parser.read()
        tier_input = sppasFindTier.aligned_phones(trs_input)

        # Create the transcription result
        trs_output = sppasTranscription("Syllabification")
        trs_output.set_meta('syllabification_result_of', input_filename)

        # Syllabify the tier
        if self._options['usesphons'] is True:
            tier_syll = self.convert(tier_input)
            trs_output.append(tier_syll)
            if self._options['createclasses']:
                trs_output.append(self.make_classes(tier_syll))

        # Extra tier: syllabify between given intervals
        if self._options['usesintervals'] is True:
            intervals = trs_input.find(self._options['tiername'])
            if intervals is None:
                self.print_message(
                    MSG_NO_TIER.format(tiername=self._options['tiername']),
                    indent=2,
                    status=annots.warning)
            else:
                tier_syll_int = self.convert(tier_input, intervals)
                tier_syll_int.set_name("SyllAlign-Intervals")
                tier_syll_int.set_meta('syllabification_used_intervals',
                                       intervals.get_name())
                trs_output.append(tier_syll_int)
                if self._options['createclasses']:
                    t = self.make_classes(tier_syll_int)
                    t.set_name("SyllClassAlign-Intervals")
                    trs_output.append(t)

        # Save in a file
        if output_filename is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_filename)
                parser.write(trs_output)
            else:
                raise EmptyOutputError

        return trs_output

    # ----------------------------------------------------------------------

    @staticmethod
    def get_pattern():
        """Return the pattern this annotation uses in an output filename."""
        return '-syll'

    @staticmethod
    def get_replace_pattern():
        """Return the pattern this annotation expects for its input filename."""
        return '-palign'

    # -----------------------------------------------------------------------
    # Utilities:
    # -----------------------------------------------------------------------

    @staticmethod
    def _phon_to_intervals(phonemes):
        """Create the intervals to be syllabified.

        we could use symbols.phone only, but for backward compatibility
        we hardly add the symbols we previously used into SPPAS.

        """
        stop = list(symbols.phone.keys())
        stop.append('#')
        stop.append('@@')
        stop.append('+')
        stop.append('gb')
        stop.append('lg')

        return phonemes.export_to_intervals(stop)
