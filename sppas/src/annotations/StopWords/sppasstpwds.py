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

    src.annotations.StopWords.sppaswtpwds.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os

from sppas import symbols
from sppas import sppasUnicode

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from ..annotationsexc import EmptyOutputError
from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError
from .stpwds import StopWords

# ----------------------------------------------------------------------------


class sppasStopWords(sppasBaseAnnotation):
    """SPPAS integration of the search for stop words in a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasStopWords instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasStopWords, self).__init__("stopwords.json", log)
        self._stops = StopWords()

    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: list of sppasOption instances

        """
        for opt in options:

            key = opt.get_key()

            if "alpha" == key:
                self.set_alpha(opt.get_value())

            elif "tiername" == key:
                self.set_tiername(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_alpha(self, alpha):
        """Fix the alpha option.

        Alpha is a coefficient to add specific stop-words in the list.

        :param alpha: (float)

        """
        self._stops.set_alpha(alpha)

    # -----------------------------------------------------------------------

    def set_tiername(self, tier_name):
        """Fix the tiername option.

        :param tier_name: (str)

        """
        self._options['tiername'] = sppasUnicode(tier_name).to_strip()

    # -----------------------------------------------------------------------

    def load_resources(self, lang_resources, lang=None):
        """Load a list of stop-words and replacements.

        Override the existing loaded lists...

        :param lang_resources: (str) File with extension '.stp' or nothing
        :param lang: (str)

        """
        fn, fe = os.path.splitext(lang_resources)

        try:
            stp = fn + '.stp'
            self._stops.load(stp, merge=False)
            self.logfile.print_message(
                "The initial list contains {:d} stop-words"
                "".format(len(self._stops)), indent=0)

        except Exception as e:
            self._stops.clear()
            self.logfile.print_message(
                "No stop-words loaded: {:s}".format(str(e)), indent=1)

    # ----------------------------------------------------------------------

    def input_tier(self, input_file):
        """Return the input tier from the input file.

        :param input_file: (str) Name of an annotated file

        """
        parser = sppasRW(input_file)
        trs_input = parser.read()

        tier_spk = trs_input.find(self._options['tiername'], case_sensitive=False)
        if tier_spk is None:
            raise Exception("Tier with name '{:s}' not found in input files."
                            "".format(self._options['tiername']))
        if tier_spk.is_empty() is True:
            raise Exception("Empty tier {:s}".format(self._options['tiername']))
        if tier_spk.is_interval() is False:
            raise Exception("Tier {:s} is not of type Interval".format(self._options['tiername']))

        return tier_spk

    # -----------------------------------------------------------------------

    def make_stp_tier(self, tier):
        """Return a tier indicating if entries are stop-words.

        :param tier: (sppasTier)

        """
        stp_tier = sppasTier('StopWord')
        for ann in tier:
            token = ann.serialize_labels()
            if token not in symbols.all:
                stp = self._stops.is_in(token)
                stp_tier.create_annotation(
                    ann.get_location().copy(),
                    sppasLabel(sppasTag(stp, tag_type="bool"))
                )
        return stp_tier

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
        # Get the tier to be used
        tier = self.input_tier(input_file[0])

        # Detection
        stp_tier = self.make_stp_tier(tier)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('stopwords_result_of', input_file[0])
        trs_output.append(stp_tier)

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
        return self._options.get("outputpattern", "-stops")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "")