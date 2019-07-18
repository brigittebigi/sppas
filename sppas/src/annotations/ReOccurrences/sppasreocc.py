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

    src.annotations.ReOccurrences.sppasreocc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from sppas import IndexRangeException

from sppas.src.utils import sppasUnicode
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription

from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyOutputError
from ..baseannot import sppasBaseAnnotation

from .reoccurrences import ReOccurences
from .reoccset import sppasAnnReOccSet

# ----------------------------------------------------------------------------


class sppasReOcc(sppasBaseAnnotation):
    """SPPAS integration of the automatic re-occurrences annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasReOcc instance with only the general rules.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasReOcc, self).__init__("reoccurrences.json", log)
        self.__reocc = ReOccurences()
        self.max_span = 20

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "tiername" == key:
                self.set_tiername(opt.get_value())

            elif "span" == key:
                self.set_span(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------

    def set_tiername(self, tier_name):
        """Fix the tiername option.

        :param tier_name: (str)

        """
        self._options['tiername'] = sppasUnicode(tier_name).to_strip()

    # -----------------------------------------------------------------------

    def set_span(self, span):
        """Fix the span option.

        Span is the maximum number of annotations to search for re-occ.
        A value of 1 means to search only in the next annotation.

        :param span: (int) Value between 1 and 20

        """
        span = int(span)
        if 0 < span <= self.max_span:
            self._options['span'] = span
        else:
            raise IndexRangeException(span, 0, self.max_span)

    # ----------------------------------------------------------------------
    # The search for re-occurrences is here
    # ----------------------------------------------------------------------

    def detection(self, tier_spk1, tier_spk2):
        """Search for the re-occurrences of annotations.

        :param tier_spk1: (sppasTier)
        :param tier_spk2: (sppasTier)

        """
        annset = sppasAnnReOccSet()
        if tier_spk1.is_float():
            tier_spk1.set_radius(0.04)
        if tier_spk1.is_float():
            tier_spk2.set_radius(0.04)

        end_loc = tier_spk2[-1].get_highest_localization()
        for ann1 in tier_spk1:

            # Localization of the end of the current annotation of spk1
            cur_loc = ann1.get_highest_localization()

            # Search for the annotations of spk2 after this localization
            all_anns2 = tier_spk2.find(cur_loc, end_loc, overlaps=False)

            # Select only the next N annotations of spk2
            window_size = min(len(all_anns2), self._options["span"])
            anns2 = all_anns2[:window_size]

            # Search for the re-occurring labels of annotations
            # -------------------------------------------------
            reoccs = self.__reocc.eval(ann1, anns2)
            if len(reoccs) > 0:
                annset.append(ann1, reoccs)

        return annset.to_tier()

    # ----------------------------------------------------------------------
    # Apply the annotation on a given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        Input file is a tuple with 2 files:
        the main speaker and the echoing speaker.

        :param input_file: (list of str) (time-aligned items, time-aligned items)
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output file name
        :returns: (sppasTranscription)

        """
        self.print_options()
        self.print_diagnosis(input_file[0])
        self.print_diagnosis(input_file[1])

        # Get the tier to be used
        parser1 = sppasRW(input_file[0])
        trs_input1 = parser1.read()
        parser2 = sppasRW(input_file[1])
        trs_input2 = parser2.read()

        tier_spk1 = trs_input1.find(self._options['tiername'], case_sensitive=False)
        tier_spk2 = trs_input2.find(self._options['tiername'], case_sensitive=False)

        if tier_spk1 is None or tier_spk2 is None:
            raise Exception("Tier with name '{:s}' not found in input files."
                            "".format(self._options['tiername']))

        # Re-occurrences Automatic Detection
        new_tiers = self.detection(tier_spk1, tier_spk2)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('reoccurrences_result_of_src', input_file[0])
        trs_output.set_meta('reoccurrences_result_of_echo', input_file[1])

        for tier in new_tiers:
            trs_output.append(tier)

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

    @staticmethod
    def get_pattern():
        """Pattern this annotation uses in an output filename."""
        return "-reocc"

    @staticmethod
    def get_input_pattern():
        """Pattern this annotation expects for its input filename."""
        return ""
