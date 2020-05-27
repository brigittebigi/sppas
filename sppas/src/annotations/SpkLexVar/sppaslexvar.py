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

from sppas import sppasUnicode
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription

from ..SelfRepet.sppasbaserepet import sppasBaseRepet
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import NoInputError
from ..annotationsexc import EmptyOutputError
from ..searchtier import sppasFindTier

# -----------------------------------------------------------------------------


class sppasLexVar(sppasBaseRepet):
    """SPPAS integration of the occ and rank estimator.

    :author:       Brigitte Bigi
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

    def lexical_variation_detect(self, tier1, tier2):
        """Detect the lexical variations in between 2 tiers

        :param tier1: (sppasTier)
        :param tier2: (sppasTier)

        """
        for ann in tier1:
            for label in ann.get_labels():
                for tag, score in label:
                    print(tag)
        print("\n")

        return tier1

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
        echo_tier = self.lexical_variation_detect(tier_input1, tier_input2)

        """# Create the transcription result
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
        """

















