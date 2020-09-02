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

    src.annotations.sppasrms.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import os

from sppas.src.utils import sppasUnicode

import sppas.src.audiodata.aio

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata.aio.aioutils import serialize_labels

from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import AudioChannelError
from ..annotationsexc import NoInputError
from ..annotationsexc import BadInputError
from ..annotationsexc import EmptyInputError
from ..annotationsexc import EmptyOutputError
from ..baseannot import sppasBaseAnnotation

from .irms import IntervalsRMS

# ----------------------------------------------------------------------------


class sppasRMS(sppasBaseAnnotation):
    """SPPAS integration of the automatic rms estimator on intervals.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasRMS instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasRMS, self).__init__("rms.json", log)
        self.__rms = IntervalsRMS()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "tiername" == key:
                self.set_tiername(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

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

    # ----------------------------------------------------------------------
    # The RMS estimator is here
    # ----------------------------------------------------------------------

    def estimator(self, tier):
        """Estimate RMS on all non-empty intervals.

        :param tier: (sppasTier)

        """
        rms_avg = sppasTier("RMS")
        rms_values = sppasTier("RMS-values")
        rms_mean = sppasTier("RMS-mean")

        for ann in tier:

            content = serialize_labels(ann.get_labels())
            if len(content) == 0:
                continue

            # Localization of the current annotation
            begin = ann.get_lowest_localization()
            end = ann.get_highest_localization()

            # Estimate all RMS values during this ann
            self.__rms.estimate(begin.get_midpoint(), end.get_midpoint())

            # The global RMS of the fragment between begin and end
            rms_tag = sppasTag(self.__rms.get_rms(), "int")
            rms_avg.create_annotation(
                ann.get_location().copy(),
                sppasLabel(rms_tag)
            )

            # All the RMS values (one each 10 ms)
            labels = list()
            for value in self.__rms.get_values():
                labels.append(sppasLabel(sppasTag(value, "int")))
            rms_values.create_annotation(ann.get_location().copy(), labels)

            # The fmean RMS of the fragment between begin and end
            rms_mean_tag = sppasTag(self.__rms.get_fmean(), "float")
            rms_mean.create_annotation(
                ann.get_location().copy(),
                sppasLabel(rms_mean_tag)
            )

        return rms_avg, rms_values, rms_mean

    # ----------------------------------------------------------------------

    def input_tier(self, trs_input):
        """Return the input tier from the input file.

        :param trs_input: (sppasTranscription)

        """
        tier_spk = trs_input.find(self._options['tiername'], case_sensitive=False)
        if tier_spk is None:
            logging.error("Tier with name '{:s}' not found in input file."
                          "".format(self._options['tiername']))
            raise NoInputError
        if tier_spk.is_empty() is True:
            raise EmptyInputError(self._options['tiername'])
        if tier_spk.is_interval() is False:
            logging.error("Tier {:s} is not of expected type Interval"
                          "".format(self._options['tiername']))
            raise BadInputError()

        return tier_spk

    # ----------------------------------------------------------------------

    def input_channel(self, input_file):
        """Return the input channel from the input file.

        :param input_file: (str) Name of an audio file

        """
        audio_speech = sppas.src.audiodata.aio.open(input_file)
        n = audio_speech.get_nchannels()
        if n != 1:
            raise AudioChannelError(n)

        # Extract the channel and set it to the RMS estimator
        idx = audio_speech.extract_channel(0)
        return audio_speech.get_channel(idx)

    # ----------------------------------------------------------------------
    # Apply the annotation on a given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        Input file is a tuple with 2 files:
        the audio file and the annotation file

        :param input_file: (list of str) (audio, time-aligned items)
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get the tier with the intervals we'll estimate rms values
        parser = sppasRW(input_file)
        trs_input = parser.read()
        tier = self.input_tier(trs_input)

        # Get audio and the channel we'll work on
        channel = self.input_channel(input_file[0])
        self.__rms.set_channel(channel)

        # RMS Automatic Estimator
        new_tiers = self.estimator(tier)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('rms_result_of_audio', input_file[0])
        trs_output.set_meta('rms_result_of_transcription', input_file[1])
        self.transfer_metadata(trs_input, trs_output)

        extm = os.path.splitext(input_file[0])[1].lower()[1:]
        media = sppasMedia(os.path.abspath(input_file[0]),
                           mime_type="audio/"+extm)

        for tier in new_tiers:
            tier.set_media(media)
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

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-rms")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "")
