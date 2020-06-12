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

    bin.sppasspklexvar.py
    ~~~~~~~~~~~~~~~~

"""

import logging
import sys
from itertools import islice

from sppas import sppasUnicode
from sppas import RangeBoundsException

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag


from ..SelfRepet.rules import SelfRules
from ..SelfRepet.datastructs import DataSpeaker
from ..SelfRepet.sppasbaserepet import sppasBaseRepet
from ..SelfRepet import sppasSelfRepet
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import NoInputError
from ..annotationsexc import EmptyOutputError
from ..searchtier import sppasFindTier
from ..OtherRepet import OtherRules

# -----------------------------------------------------------------------------


class sppasLexVar(sppasBaseRepet):
    """SPPAS integration of the occ and rank estimator.

    :author:       Laurent Vouriot
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """
    def __init__(self, log=None):
        """Create a new sppasLexMetric instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasLexVar, self).__init__("lexvar.json", log)

        self.__rules = OtherRules(self._stop_words)
        self.__sources = dict()

    # -----------------------------------------------------------------------

    def set_use_stopwords(self, use_stopwords):
        return

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Override Fix all options of the annotation from list sppasOption().

        :param options: (list of sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "tiername" == key:
                self.set_tiername(opt.get_value())
            elif "stopwords" == key:
                self.set_use_stopwords(opt.get_value())
            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_tiername(self, tier_name):
        """Fix the tiername option.

        :param tier_name: (str)

        """
        self._options['tiername'] = sppasUnicode(tier_name).to_strip()

    # ----------------------------------------------------------------------

    def input_tier(self, input_file):
        """Return the input tier from the input file.

        :param input_file: (str) Name of an annotated file

        """
        parser = sppasRW(input_file)
        trs_input = parser.read()

        tier_spk = trs_input.find(self._options['tiername'], case_sensitive=False)
        if tier_spk is None:
            logging.error("Tier with name '{:s}' not found in input file {:s}."
                          "".format(self._options['tiername'], input_file))
            raise NoInputError

        return tier_spk

    # ----------------------------------------------------------------------

    @staticmethod
    def contains(list1, list2):
        """Check if a list is contained in an other one

        :param list1: (list)
        :param list2: (list)
        :returns: (bool)

        """
        for i in range(len(list1) - len(list2) + 1):
            if list1[i:i + len(list2)] == list2:
                return True
        return False

    # ----------------------------------------------------------------------

    @staticmethod
    def window(sequence, window_size=2):
        """Returns a sliding window (of width n) over data from the iterable
        
        https://stackoverflow.com/questions/6822725/rolling-or-sliding-window-iterator
        :param sequence: (list)
        :param window_size: (int)
        
        """
        it = iter(sequence)
        result = list(islice(it, window_size))
        if len(result) == window_size:
            return result
        for elem in it:
            result = result[1:] + [elem, ]
        return result
    # ----------------------------------------------------------------------

    @staticmethod
    def get_longest(speaker1, speaker2):
        """Return the index of the last token of the longest repeated string.

        :param speaker1: (DataSpeaker) Entries of speaker 1
        :param speaker2: (DataSpeaker2) Entries of speaker 2 (or None)
        :returns: (int) Index or -1

        """
        last_token = -1
        # Get the longest string
        for t in range(len(speaker1)):

            param2 = 0

            # search
            repet_idx = speaker1.is_word_repeated(t, param2, speaker2)
            if repet_idx > -1:
                last_token = t
            else:
                break

        return last_token

    # ----------------------------------------------------------------------

    def select(self, index, speaker1, speaker2):
        """Append (or not) an repetition.

        :param index: (int) end index of the entry of the source (speaker1)
        :param speaker1: (DataSpeaker) Entries of speaker 1
        :param speaker2: (DataSpeaker) Entries of speaker 2
        :returns: (bool)

        """
        # Rule 1: keep any repetition containing at least 1 relevant token
        keep_me = self.__rules.rule_syntagme(0, index, speaker1)
        if keep_me is False:
            # Rule 2: keep any repetition if N>2 AND strict echo
            keep_me = self.__rules.rule_strict(0, index, speaker1, speaker2)
        return keep_me

    # ----------------------------------------------------------------------

    @staticmethod
    def tier_content_listing(tier, time=False):
        """Create a list with the tokens contained in a tier
        :param tier: (sppasTier)
        :param time: (bool) if true create a the corresponding time list

        :returns:  (list) list of content and list of time or just list of content

        """
        content = list()
        time_list = list()

        for ann in tier:
            for label in ann.get_labels():
                for tag, score in label:
                    if tag.is_speech():
                        content.append(tag.get_content())
                        if time:
                            time_list.append(ann.get_location())

        # if time:
        #     return content, time_list
        # else:
        #     return content

        return content, time_list if time else content

    # ----------------------------------------------------------------------

    def create_tier(self, content_list, time_list):
        """Create a source tier from content en time liste

        :param content_list: (list) list of repeated token
        :param time_list: (list) list of time corresponding to a token used to recreate a tier
        :returns: (sppasTier)

        """
        tier_src = sppasTier("Repeats")
        for src in self.__sources:
            (i, nb) = src
            loc_begin = time_list[i]
            loc_end = time_list[nb]

            begin_point = loc_begin.get_lowest_localization()
            end_point = loc_end.get_highest_localization()

            interval = sppasInterval(begin_point, end_point)
            location = sppasLocation(interval)

            tags = [sppasTag(content_list[i] for i in range(i, i + nb))]
            tier_src.create_annotation(location, [sppasLabel(tag) for tag in tags])

        return tier_src

    # ----------------------------------------------------------------------

    def lexical_variation_detect(self, tier1, tier2, window_size):
        """Detect the lexical variations in between 2 tiers

        :param tier1: (sppasTier)
        :param tier2: (sppasTier)
        :param window_size: (int)

        """
        # getting all the unicodes tokens from the first tier + the time location
        # useful for creating the tier
        content_list_tier1, time_list_tier1 = self.tier_content_listing(tier1, True)
        # getting all the unicodes tokens from the second tier
        content_list_tier2 = self.tier_content_listing(tier2, False)
        
        window_list2 = list()
        window_list1 = list()
        # windowing the unicode list for the first speaker
        for window in self.window(content_list_tier1, window_size):
            window_list1.append(window)
        # windowing the unicode list for the second speaker
        for window in self.window(content_list_tier2, window_size):
            window_list2.append(window)

        i = 0
        while i < len(window_list1):
            data_spk1 = DataSpeaker(window_list1[i])
            max_index = 0
            y = 0
            cpt = 0
            while y < len(window_list2):
                data_spk2 = DataSpeaker(window_list2[y])
                # TODO : RENAME INDEX
                index = self.get_longest(data_spk1, data_spk2)
                print(index)
                if index != -1:
                    if self.select(index, data_spk1, data_spk2):
                        if (i, i + index) in self.__sources:
                            cpt += 1
                        else:
                            self.__sources[(i, i + index)] = 1
                        self.__sources[(i, i + index)] = cpt
                        if index > max_index:
                            max_index = index
                y += 1
            if max_index == 0:
                i += 1
            else:
                i += max_index + 1

        # Creating the src tier
        return self.create_tier(content_list_tier1, time_list_tier1)

        # ./sppaslexvar -i AB -s CM -o toto.Textgrid -r ressource/vocab/frap.lem
    # ----------------------------------------------------------------------
    # Patterns
    # ----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-rms")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "")

    # -----------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) time-aligned tokens
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output file name
        :returns: (sppasTranscription)

        """
        self.print_options()
        self.print_diagnosis(input_file[0])
        self.print_diagnosis(input_file[1])

        # Get the tier to be used
        parser = sppasRW(input_file[0])
        trs_input1 = parser.read()
        tier_tokens = sppasFindTier.aligned_tokens(trs_input1)
        tier_input1 = self.make_word_strain(tier_tokens)
        tier_input1.set_name(tier_input1.get_name() + "-source")

        # Get the tier to be used
        parser = sppasRW(input_file[1])
        trs_input2 = parser.read()
        tier_tokens = sppasFindTier.aligned_tokens(trs_input2)
        tier_input2 = self.make_word_strain(tier_tokens)
        tier_input2.set_name(tier_input2.get_name() + "-echo")

        # Repetition Automatic Detection
        src_tier = self.lexical_variation_detect(tier_input1, tier_input2, 2)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('other_repetition_result_of_src', input_file[0])
        trs_output.set_meta('other_repetition_result_of_echo', input_file[1])
        if len(self._word_strain) > 0:
            trs_output.append(tier_input1)
        if self._options['stopwords'] is True:
            trs_output.append(self.make_stop_words(tier_input1))
        trs_output.append(src_tier)
        if len(self._word_strain) > 0:
            trs_output.append(tier_input2)

        # Save in a file
        if output_file is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_file)
                parser.write(trs_output)
                self.print_filename(output_file)
            else:
                raise EmptyOutputError

        print(self.__sources)

        return trs_output


















