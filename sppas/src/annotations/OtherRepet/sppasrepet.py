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

    src.annotations.OtherRepet.sppasrepet.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas import symbols
from sppas import sppasRW
from sppas import sppasTranscription
from sppas import sppasTier
from sppas import sppasInterval
from sppas import sppasLocation
from sppas import sppasLabel
from sppas import sppasTag

from sppas.src.anndata.anndataexc import TierAddError
from sppas.src.anndata.aio.aioutils import serialize_labels

from ..searchtier import sppasFindTier
from ..annotationsexc import EmptyOutputError
from ..SelfRepet.datastructs import DataSpeaker
from ..SelfRepet.sppasbaserepet import sppasBaseRepet

from .detectrepet import OtherRepetition

# ---------------------------------------------------------------------------

SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class sppasOtherRepet(sppasBaseRepet):
    """SPPAS Automatic Other-Repetition Detection.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Detect automatically other-repetitions. Result must be re-filtered by an
    expert. This annotation is performed on the basis of time-aligned tokens
    or lemmas. The output is made of 2 tiers with sources and echos.

    """

    def __init__(self, log=None):
        """Create a new sppasOtherRepet instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasOtherRepet, self).__init__("otherrepet.json", log)

        self.max_span = 12

    # -----------------------------------------------------------------------
    # Automatic Detection search
    # -----------------------------------------------------------------------

    def other_detection(self, inputtier1, inputtier2):
        """Other-Repetition detection.

        :param inputtier1: (Tier)
        :param inputtier2: (Tier)

        """
        if inputtier1.is_float():
            inputtier1.set_radius(0.04)
        if inputtier2.is_float():
            inputtier2.set_radius(0.04)
        # Use the appropriate stop-list: add un-relevant tokens of the echoing speaker
        stop_words = self._stop_words.copy()
        stop_words.evaluate(inputtier2, merge=True)
        # Create repeat objects
        repetition = OtherRepetition(stop_words)
        # Create output data
        src_tier = sppasTier("OR-Source")
        echo_tier = sppasTier("OR-Echo")

        # Initialization of tok_start, and tok_end
        tok_start_src = 0
        tok_end_src = min(20, len(inputtier1)-1)  # 20 is the max nb of tokens in a src
        tok_start_echo = 0

        tokens2 = list()
        speaker2 = DataSpeaker(tokens2)
        # Detection is here:
        # detect() is applied work by word, from tok_start to tok_end
        while tok_start_src < tok_end_src:

            # Build an array with the tokens
            tokens1 = [inputtier1[i].serialize_labels()
                       for i in range(tok_start_src, tok_end_src+1)]
            speaker1 = DataSpeaker(tokens1)

            # Create speaker2
            # re-create only if different of the previous step...
            src_begin = inputtier1[tok_start_src].get_lowest_localization().get_midpoint()
            echo_begin = inputtier2[tok_start_echo].get_lowest_localization().get_midpoint()
            if len(tokens2) == 0 or echo_begin < src_begin:
                tokens2 = list()
                nb_breaks = 0
                old_tok_start_echo = tok_start_echo

                for i in range(old_tok_start_echo, len(inputtier2)):
                    ann = inputtier2[i]
                    label = serialize_labels(ann.get_labels())
                    if ann.get_lowest_localization().get_midpoint() >= src_begin:
                        if tok_start_echo == old_tok_start_echo:
                            tok_start_echo = i
                        if label == SIL_ORTHO:
                            nb_breaks += 1
                        if nb_breaks == self._options['span']:
                            break
                        tokens2.append(label)
                speaker2 = DataSpeaker(tokens2)

            # We can't go too further due to the required time-alignment of
            # tokens between src/echo
            # Check only if the first token is the first token of a source!!
            repetition.detect(speaker1, speaker2, 1)

            # Save repeats
            shift = 1
            if repetition.get_source() is not None:
                s, e = repetition.get_source()
                saved = sppasOtherRepet.__add_repetition(
                    repetition, inputtier1, inputtier2, tok_start_src,
                    tok_start_echo, src_tier, echo_tier)
                if saved is True:
                    shift = e + 1

            tok_start_src = min(tok_start_src + shift, len(inputtier1)-1)
            tok_end_src = min(tok_start_src + 20, len(inputtier1)-1)

        return src_tier, echo_tier

    # -----------------------------------------------------------------------

    @staticmethod
    def __add_repetition(repetition, spk1_tier, spk2_tier,
                         start_idx1, start_idx2, src_tier, echo_tier):
        """Add a repetition - source and echos - in tiers.

        :param repetition: (DataRepetition)
        :param spk1_tier: (Tier) The tier of speaker 1 (to detect sources)
        :param spk2_tier: (Tier) The tier of speaker 2 (to detect echos)
        :param start_idx1: start index of the interval in spk1_tier
        :param start_idx2: start index of the interval in spk2_tier
        :param src_tier: (Tier) The resulting tier with sources
        :param echo_tier: (Tier) The resulting tier with echos
        :returns: (bool) the repetition was added or not

        """
        index = len(src_tier)

        # Source
        s, e = repetition.get_source()
        src_begin = spk1_tier[start_idx1 + s].get_lowest_localization()
        src_end = spk1_tier[start_idx1 + e].get_highest_localization()
        time = sppasInterval(src_begin.copy(), src_end.copy())
        try:
            a = src_tier.create_annotation(
                    sppasLocation(time),
                    sppasLabel(sppasTag("S" + str(index + 1))))
            src_id = a.get_meta('id')
        except TierAddError:
            return False

        # Echos
        for (s, e) in repetition.get_echos():
            rep_begin = spk2_tier[start_idx2 + s].get_lowest_localization()
            rep_end = spk2_tier[start_idx2 + e].get_highest_localization()
            time = sppasInterval(rep_begin.copy(), rep_end.copy())
            r = sppasLabel(sppasTag("R" + str(index + 1)))
            try:
                a = echo_tier.create_annotation(
                    sppasLocation(time), r)
                a.set_meta('is_other_repetition_of', src_id)
            except TierAddError:
                a = echo_tier.find(rep_begin, rep_end)
                if len(a) > 0:
                    a[0].append_label(r)

        return True

    # -----------------------------------------------------------------------
    # Run
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        Input file is a tuple with 2 files: the main speaker and the echoing
        speaker.

        :param input_file: (list of str) (time-aligned token, time-aligned token)
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
        (src_tier, echo_tier) = self.other_detection(tier_input1, tier_input2)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('other_repetition_result_of_src', input_file[0])
        trs_output.set_meta('other_repetition_result_of_echo', input_file[1])
        if len(self._word_strain) > 0:
            trs_output.append(tier_input1)
        if self._options['stopwords'] is True:
            trs_output.append(self.make_stop_words(tier_input1))
        trs_output.append(src_tier)
        trs_output.append(echo_tier)
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

        return trs_output

    # ----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-orepet")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "-palign")
