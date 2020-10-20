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

    src.annotations.SpkLexRep.sppaslexrep.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata.aio.aioutils import serialize_labels

from ..SelfRepet.datastructs import DataSpeaker
from ..SelfRepet.sppasbaserepet import sppasBaseRepet
from ..annotationsexc import EmptyOutputError
from ..searchtier import sppasFindTier
from ..OtherRepet import OtherRules

# ---------------------------------------------------------------------------


class LexReprise(object):
    """Data structure to store a lexical reprise.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, win_idx, end_idx):
        self.__win_idx = win_idx    # index of the window
        self.__end = end_idx        # index of the last repeated entry in the window
        self.__labels = list()

    def get_start(self):
        return self.__win_idx

    def get_end(self):
        return self.__end

    def set_content(self, dataspk):
        """Set the labels from the content.

        :param dataspk: (DataSpk) The data content of the window win_idx and end refer to

        """
        for i in range(self.__end + 1):
            tag = sppasTag(dataspk[i])
            self.__labels.append(sppasLabel(tag))

    def get_labels(self):
        return [label.copy() for label in self.__labels]

    def __eq__(self, other):
        if isinstance(other, (list, tuple)) and len(other) > 1:
            return self.__win_idx == other[0] and self.__end == other[1]

        if isinstance(other, LexReprise):
            return self.__win_idx == other.get_start() and self.__end == other.get_end()

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        labels = serialize_labels(self.__labels, separator=" ")
        return str(self.__win_idx)+" "+str(self.__end)+": "+labels

# ---------------------------------------------------------------------------


class sppasLexRep(sppasBaseRepet):
    """SPPAS integration of the speaker lexical variation annotation.

    :author:       Laurent Vouriot, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Main differences compared to repetitions:
    The span option is used to fix the max number of continuous tokens to analyze.
    The span window has a duration limit.

    """
    def __init__(self, log=None):
        """Create a new sppasLexVar instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasLexRep, self).__init__("lexrep.json", log)
        self.max_span = 30
        self.__rules = OtherRules(self._stop_words)

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: list of sppasOption instances

        """
        spanduropt = None
        for opt in options:
            key = opt.get_key()
            if "spandur" == key:
                self.set_span_duration(opt.get_value())
                spanduropt = opt
        if spanduropt is not None:
            options.remove(spanduropt)

        sppasBaseRepet.fix_options(self, options)

    # -----------------------------------------------------------------------

    def set_span_duration(self, value):
        """Set the spandur option.

        :param value: (float, int) Max duration of a span window.

        """
        self._options["spandur"] = value

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------

    def _get_longest_selected(self, data_spk1, data_spk2):
        """Return the end-index of the longest selected sequence."""
        # get the index of the longest repeated sequence of tokens
        spk2_echo_idx = sppasLexRep.get_longest(data_spk1, data_spk2)
        if spk2_echo_idx != -1:
            # apply the selection rules to verify that the repeated
            # sequence is validated.
            if self.select(spk2_echo_idx, data_spk1, data_spk2):
                return spk2_echo_idx
        return -1

    # -----------------------------------------------------------------------

    @staticmethod
    def _add_source(sources, win_idx, end, dataspk):
        """Add the source in the list of sources."""
        # store the repeated sequence in our list of sources
        if (win_idx, end) not in sources:
            # add it in the dict if we found it for the first time
            lex_reprise = LexReprise(win_idx, end)
            lex_reprise.set_content(dataspk)
            sources.append(lex_reprise)

    # -----------------------------------------------------------------------

    def _detect_all_sources(self, win_spk1, win_spk2):
        """Return all reprises of speaker1 in speaker2.

        :return: (dict) dict of sources

        - key: (index_start, index_end)
        - value: the number of time the source is repeated

        """
        sources = list()

        # index of the end-token of the longest detected source in the previous window
        prev_max_index = -1
        # for each window on data of speaker 1, spk_widx1=index of the window1
        spk1_widx = 0
        while spk1_widx < len(win_spk1):
            data_spk1 = win_spk1[spk1_widx]

            max_index = -1
            # for each window on data of speaker 2
            spk2_widx = 0
            while spk2_widx < len(win_spk2):
                data_spk2 = win_spk2[spk2_widx]

                # get the index of the longest selected sequence of tokens
                spk2_echo_idx = self._get_longest_selected(data_spk1, data_spk2)
                if spk2_echo_idx > -1 and (spk1_widx+spk2_echo_idx) > prev_max_index:
                    if spk2_echo_idx > max_index:
                        max_index = spk2_echo_idx
                        if max_index == self._options["span"]:
                            break
                spk2_widx += 1

            if max_index > -1:
                sppasLexRep._add_source(sources,
                                        win_idx=spk1_widx,
                                        end=max_index,
                                        dataspk=data_spk1)
                prev_max_index = spk1_widx + max_index

            # Index of the next speaker1 window to analyze
            spk1_widx += 1

        return sources

    # -----------------------------------------------------------------------

    def _merge_sources(self, sources):
        """Merge sources if content is the same."""
        return sources

    # -----------------------------------------------------------------------

    @staticmethod
    def create_tier(sources, locations):
        """Create a tier from content end localization lists.

        :param sources: (dict) dict of sources -- in fact, the indexes.
        :param locations: (list) list of location corresponding to the tokens
        :returns: (sppasTier)

        """
        tier_content = sppasTier("LexRepContent")
        for lexreprise in sources:
            start_idx = lexreprise.get_start()
            end_idx = start_idx + lexreprise.get_end()

            # Create the location of the source, from start to end
            loc_begin = locations[start_idx]
            loc_end = locations[end_idx]
            begin_point = loc_begin.get_lowest_localization()
            end_point = loc_end.get_highest_localization()
            location = sppasLocation(sppasInterval(begin_point, end_point))

            # Add the annotation into the source tier
            tier_content.create_annotation(location, lexreprise.get_labels())

        return tier_content

    # -----------------------------------------------------------------------

    def windowing(self, content, location=None):
        """Return the list of DataSpeaker matching the given content.

        :param content: (list) List of entries
        :param location: (list) List of locations of the entries
        :returns: list of DataSpeaker

        """
        span_tok = self._options["span"]
        span_dur = self._options["spandur"]
        windows = list()
        for i in range(len(content)):
            end_size = min(span_tok, len(content)-i)
            if location is not None and end_size > 1:
                win_loc = location[i:i+end_size]
                # Get the duration this window is covering
                start_point = win_loc[0].get_lowest_localization()
                end_point = win_loc[end_size-1].get_highest_localization()
                win_dur = end_point.get_midpoint() - start_point.get_midpoint()
                # Reduce the window duration to match the max duration
                while win_dur > span_dur and end_size > 0:
                    end_point = win_loc[end_size-1].get_highest_localization()
                    win_dur = end_point.get_midpoint() - start_point.get_midpoint()
                    if win_dur <= span_dur:
                        break
                    end_size -= 1

                if end_size < min(span_tok, len(content)-i):
                    logging.debug(" ... window was reduced to {} tokens."
                                  "".format(end_size+1))

            win_tok = content[i:i+end_size]
            windows.append(DataSpeaker(win_tok))

        return windows

    # -----------------------------------------------------------------------

    def lexical_variation_detect(self, tier1, tier2):
        """Detect the lexical variations between 2 tiers.

        :param tier1: (sppasTier)
        :param tier2: (sppasTier)

        """
        # getting all the unicode tokens from the first tier + the localization
        content_tier1, loc_tier1 = self.tier_to_list(tier1, True)
        content_tier2, loc_tier2 = self.tier_to_list(tier2, True)

        # windowing the unicode list for the speakers
        window_list1 = self.windowing(content_tier1, loc_tier1)
        window_list2 = self.windowing(content_tier2, loc_tier2)

        # detect all possible sources and store them in a dict with
        # key=(start, end) and value=occ.
        sources1 = self._detect_all_sources(window_list1, window_list2)
        sources2 = self._detect_all_sources(window_list2, window_list1)

        # create result tiers from the sources
        tier1 = self.create_tier(sources1, loc_tier1)
        tier2 = self.create_tier(sources2, loc_tier2)
        tier1.set_name(tier1.get_name() + "-1")
        tier2.set_name(tier2.get_name() + "-2")

        return tier1, tier2

    # -----------------------------------------------------------------------
    # Patterns
    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-rms")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "")

    # -----------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) time-aligned tokens of 2 files
        :param opt_input_file: (list of str) ignored
        :param output: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get the tier to be used
        parser = sppasRW(input_file[0])
        trs_input1 = parser.read()
        tier_tokens = sppasFindTier.aligned_tokens(trs_input1)
        tier_input1 = self.make_word_strain(tier_tokens)

        # Get the tier to be used
        parser = sppasRW(input_file[1])
        trs_input2 = parser.read()
        tier_tokens = sppasFindTier.aligned_tokens(trs_input2)
        tier_input2 = self.make_word_strain(tier_tokens)

        # Reprise Automatic Detection - i.e. a repeated passage of lexical entries
        tier1, tier2 = self.lexical_variation_detect(tier_input1, tier_input2)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('speaker_lexrep_result_of_spk1', input_file[0])
        trs_output.set_meta('spkeaker_lexrep_result_of_spk2', input_file[1])
        self.transfer_metadata(trs_input1, trs_output)

        if len(self._word_strain) > 0:
            tier_input1.set_name(tier_input1.get_name() + "-1")
            trs_output.append(tier_input1)
        if self._options['stopwords'] is True:
            stopwords1 = self.make_stop_words(tier_input1)
            stopwords1.set_name(stopwords1.get_name() + "-1")
            trs_output.append(stopwords1)
        trs_output.append(tier1)

        if len(self._word_strain) > 0:
            tier_input2.set_name(tier_input2.get_name() + "-2")
            trs_output.append(tier_input2)
        if self._options['stopwords'] is True:
            stopwords2 = self.make_stop_words(tier_input2)
            stopwords2.set_name(stopwords2.get_name() + "-2")
            trs_output.append(stopwords2)
        trs_output.append(tier2)

        # Save in a file
        if output is not None:
            if len(trs_output) > 0:
                output_file = self.fix_out_file_ext(output)
                parser = sppasRW(output_file)
                parser.write(trs_output)
                return [output_file]
            else:
                raise EmptyOutputError

        return trs_output


















