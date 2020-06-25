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

    src.annotations.SpkLexVar.sppasspklexvar.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    """SPPAS integration of the speaker lexical variation annotation.

    :author:       Laurent Vouriot
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Main differences compared to repetitions:
    The span option is used to fix the max number of continuous tokens to analyze.

    """
    def __init__(self, log=None):
        """Create a new sppasLexVar instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasLexVar, self).__init__("lexvar.json", log)
        self.max_span = 30
        self.__rules = OtherRules(self._stop_words)

    # ----------------------------------------------------------------------

    @staticmethod
    def tier_to_list(tier, loc=False):
        """Create a list with the tokens contained in a tier.

        :param tier: (sppasTier)
        :param loc: (bool) if true create the corresponding list of sppasLocation()
        :returns:  (list, list) list of unicode content and list of location

        """
        content = list()
        localiz = list()

        for ann in tier:
            for label in ann.get_labels():
                for tag, score in label:
                    if tag.is_speech():
                        content.append(tag.get_content())
                        if loc is True:
                            localiz.append(ann.get_location())

        return content, localiz

    # ----------------------------------------------------------------------

    @staticmethod
    def get_longest(speaker1, speaker2):
        """Return the index of the last token of the longest repeated sequence.

        No matter if a non-speech event occurs in the middle of the repeated
        sequence and no matter if a non-speech event occurs in the middle of
        the source sequence.
        No matter if tokens are not repeated in the same order.

        :param speaker1: (DataSpeaker) Entries of speaker 1
        :param speaker2: (DataSpeaker) Entries of speaker 2
        :returns: (int) Index or -1

        """
        last_token = -1
        # Get the longest repeated number of words
        for index1 in range(len(speaker1)):
            if speaker1.is_word(index1) is True:
                param2 = 0
                # search
                repet_idx = speaker1.is_word_repeated(index1, param2, speaker2)
                if repet_idx > -1:
                    last_token = index1
                else:
                    break

        return last_token

    # ----------------------------------------------------------------------

    def select(self, index1, speaker1, speaker2):
        """Append (or not) a repetition.

        :param index1: (int) end index of the entry of the source (speaker1)
        :param speaker1: (DataSpeaker) Entries of speaker 1
        :param speaker2: (DataSpeaker) Entries of speaker 2
        :returns: (bool)

        """
        # Rule 1: keep any repetition containing at least 1 relevant token
        keep_me = self.__rules.rule_syntagme(0, index1, speaker1)
        if keep_me is False:
            # Rule 2: keep any repetition if N>2 AND strict echo
            keep_me = self.__rules.rule_strict(0, index1, speaker1, speaker2)
        return keep_me

    # ----------------------------------------------------------------------

    def _get_longest_selected(self, data_spk1, data_spk2):
        """Return the end-index of the longest selected sequence."""
        # get the index of the longest repeated sequence of tokens
        spk2_echo_idx = sppasLexVar.get_longest(data_spk1, data_spk2)
        if spk2_echo_idx != -1:
            # apply the selection rules to verify that the repeated
            # sequence is validated.
            if self.select(spk2_echo_idx, data_spk1, data_spk2):
                return spk2_echo_idx
        return -1

    # ----------------------------------------------------------------------

    @staticmethod
    def _add_source(sources, start, end):
        """Add the source key (start, end) in the dict of sources."""
        # store the repeated sequence in our list of sources
        if (start, end) not in sources:
            # add it in the dict if we found it for the first time
            sources[(start, end)] = 0

            # increment the number of times the source was repeated
        cpt = sources[(start, end)]
        sources[(start, end)] = cpt + 1

    # ----------------------------------------------------------------------

    def _detect_all_sources(self, win_spk1, win_spk2):
        """Return all reprises of speaker1 in speaker2.

        :return: (dict) dict of sources

        - key: (index_start, index_end)
        - value: the number of time the source is repeated

        """
        sources = dict()

        # for each window on data of speaker 1
        spk1_widx = 0
        while spk1_widx < len(win_spk1):
            data_spk1 = win_spk1[spk1_widx]
            print("Window of speaker 1: {}".format(data_spk1))
            # index of the longest detected source in the window of speaker2
            max_index = 0

            # for each window on data of speaker 2
            spk2_widx = 0
            while spk2_widx < len(win_spk2):
                data_spk2 = win_spk2[spk2_widx]
                print("   Window of speaker 2: {}".format(data_spk2))

                # get the index of the longest selected sequence of tokens
                spk2_echo_idx = self._get_longest_selected(data_spk1, data_spk2)
                if spk2_echo_idx != -1:
                    sppasLexVar._add_source(sources, start=spk1_widx,
                                            end=spk1_widx + spk2_echo_idx)

                    if spk2_echo_idx > max_index:
                        max_index = spk2_echo_idx

                spk2_widx += 1

            # Index of the next speaker1 window to analyze
            if max_index > 0:
                spk1_widx += max_index
            spk1_widx += 1

        return sources

    # ----------------------------------------------------------------------

    def _merge_sources(self, sources):
        """Merge sources if their start index is the same."""
        return sources

    # ----------------------------------------------------------------------

    @staticmethod
    def create_tier(sources, content, location):
        """Create a tier from content end localization lists.

        :param sources: (dict) dict of sources -- in fact, the indexes.
        :param content: (list) list of tokens
        :param location: (list) list of location corresponding to the tokens
        :returns: (sppasTier)

        """
        tier_content = sppasTier("RepeatContent")
        tier_occ = sppasTier("RepeatCount")
        for src in sources:
            start_idx, end_idx = src
            count = sources[src]
            # Create the location of the source, from start to end
            loc_begin = location[start_idx]
            loc_end = location[end_idx]
            begin_point = loc_begin.get_lowest_localization()
            end_point = loc_end.get_highest_localization()
            location = sppasLocation(sppasInterval(begin_point, end_point))

            # Create the list of labels of the source from the content
            labels = list()
            for i in range(start_idx, end_idx+1):
                labels.append(sppasLabel(sppasTag(content[i])))

            # Add the annotation into the source tier
            tier_content.create_annotation(location, labels)
            tier_occ.create_annotation(location.copy(),
                                       sppasLabel(sppasTag(count, "int")))

        return tier_content, tier_occ

    # ----------------------------------------------------------------------

    def windowing(self, content):
        """Return all the list of dataspk."""
        windows = list()
        for i in range(len(content)-1):
            window = content[i:i+self._options["span"]]
            windows.append(DataSpeaker(window))
        return windows

    # ----------------------------------------------------------------------

    def lexical_variation_detect(self, tier1, tier2):
        """Detect the lexical variations in between 2 tiers

        :param tier1: (sppasTier)
        :param tier2: (sppasTier)

        """
        # getting all the unicode tokens from the first tier + the localization
        content_tier1, loc_tier1 = self.tier_to_list(tier1, True)
        content_tier2, loc_none = self.tier_to_list(tier2, False)
        # windowing the unicode list for the speakers
        window_list1 = self.windowing(content_tier1)
        window_list2 = self.windowing(content_tier2)

        # detect all possible sources and store them in a dict with
        # key=(start, end) and value=occ.
        sources = self._detect_all_sources(window_list1, window_list2)

        # merge sources if they are starting at the same index but not
        # ending the same???
        # merge source if they are overlapping???
        # remove sources with an identical token sequence??? (or count)?
        merged_sources = self._merge_sources(sources)

        # create result tiers from the sources
        tiers = self.create_tier(merged_sources, content_tier1, loc_tier1)
        return tiers

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

        :param input_file: (list of str) time-aligned tokens of 2 files
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
        tier_input1.set_name(tier_input1.get_name() + "-src")

        # Get the tier to be used
        parser = sppasRW(input_file[1])
        trs_input2 = parser.read()
        tier_tokens = sppasFindTier.aligned_tokens(trs_input2)
        tier_input2 = self.make_word_strain(tier_tokens)
        tier_input2.set_name(tier_input2.get_name() + "-echo")

        # Reprise Automatic Detection - i.e. a repeated passage of lexical entries
        tiers = self.lexical_variation_detect(tier_input1, tier_input2)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('speaker_lexvar_result_of_src', input_file[0])
        trs_output.set_meta('spkeaker_lexvar_result_of_echo', input_file[1])
        if len(self._word_strain) > 0:
            trs_output.append(tier_input1)
        if self._options['stopwords'] is True:
            trs_output.append(self.make_stop_words(tier_input1))
        if len(self._word_strain) > 0:
            trs_output.append(tier_input2)

        for out_tier in tiers:
            trs_output.append(out_tier)

        # Save in a file
        if output_file is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_file)
                parser.write(trs_output)
                self.print_filename(output_file)
            else:
                raise EmptyOutputError

        return trs_output


















