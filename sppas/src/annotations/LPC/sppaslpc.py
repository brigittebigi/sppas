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

    src.annotations.sppaslpc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import cfg
from sppas.src.config import symbols
from sppas.src.config import annots
from sppas.src.config import info

from sppas import sppasRW
from sppas import sppasTranscription
from sppas import sppasTier
from sppas import sppasInterval
from sppas import sppasLocation
from sppas import sppasTag
from sppas import sppasLabel

from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyOutputError

from .lpckeys import LPC

# ----------------------------------------------------------------------------


class sppasLPC(sppasBaseAnnotation):
    """SPPAS integration of the automatic LPC key-code generation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasLPC instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasLPC, self).__init__("lpc.json", log)
        self.__lpc = LPC()

    # -----------------------------------------------------------------------

    def load_resources(self, config_filename, **kwargs):
        """Fix the keys from a configuration file.

        :param config_filename: Name of the configuration file with the keys

        """
        self.__lpc = LPC(config_filename)

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - createvideo

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "createvideo" == key:
                self.set_create_video(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # ------------------------------------------------------------------------

    def set_create_video(self, create=True):
        """Fix the createvideo option.

        :param create: (bool)

        """
        self._options['createvideo'] = create

    # ----------------------------------------------------------------------
    # Syllabification of time-aligned phonemes stored into a tier
    # ----------------------------------------------------------------------

    def convert(self, phonemes):
        """Syllabify labels of a time-aligned phones tier.

        :param phonemes: (sppasTier) time-aligned phonemes tier
        :returns: (sppasTier)

        """
        lpc_tier = sppasTier("LPC-Syll")
        lpc_tier.set_meta('lpc_syll_of_tier', phonemes.get_name())

        # create a tier without the separators, i.e. keep only the phonemes
        intervals = sppasLPC._phon_to_intervals(phonemes)

        # generate keys for each sequence of phonemes
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

            # generate keys within the interval
            if start_phon_idx != -1 and end_phon_idx != -1:
                self.gen_keys_interval(phonemes, start_phon_idx, end_phon_idx, lpc_tier)
            else:
                self.logfile.print_message(
                    (info(1224, "annotations")).format(interval),
                    indent=2, status=annots.warning)

        return lpc_tier

    # ----------------------------------------------------------------------

    def gen_keys_interval(self, phonemes, from_p, to_p, lpc_keys):
        """Perform the key generation of one sequence of phonemes.

        :param phonemes: (sppasTier)
        :param from_p: (int) index of the first phoneme to be syllabified
        :param to_p: (int) index of the last phoneme to be syllabified
        :param lpc_keys: (sppasTier)

        """
        # create the sequence of phonemes to syllabify
        p = list()
        for ann in phonemes[from_p:to_p+1]:
            tag = ann.get_best_tag()
            p.append(tag.get_typed_content())

        # create the sequence of keys
        s = self.__lpc.annotate(p)

        # add the keys into the output tier
        for i, syll in enumerate(s):
            start_idx, end_idx = syll

            # create the location
            begin = phonemes[start_idx+from_p].get_lowest_localization().copy()
            end = phonemes[end_idx+from_p].get_highest_localization().copy()
            location = sppasLocation(sppasInterval(begin, end))

            # create the label
            syll_string = self.__lpc.phonetize_syllables(p, [syll])
            label = sppasLabel(sppasTag(syll_string))

            # add the lpc keys into the output tier
            lpc_keys.create_annotation(location, label)

    # ----------------------------------------------------------------------

    def create_keys(self, lpc_tier):
        """Return a tier with the LPC keys from LPC syllables.

        :param lpc_tier: (sppasTier)
        :returns: (sppasTier)

        """
        keys_tier = sppasTier("LPC-Keys")
        for ann in lpc_tier:
            a = ann.copy()
            for label in a.get_labels():
                for tag, score in label:
                    tag_content = tag.get_content()
                    keys = self.__lpc.keys_phonetized(tag_content)
                    tag.set_content(keys)
            keys_tier.add(a)

        return keys_tier

    # ----------------------------------------------------------------------

    def make_video(self, video_file, lpc_keys):
        """Create a video with the LPC keys.

        :param video_file: (str) Filename of the video
        :param lpc_keys: (sppasTier) Codes of the C-V syllables

        """
        if cfg.dep_installed("video") is True:
            self.logfile.print_message("Create the tagged video", status=annots.info)

        else:
            self.logfile.print_message(
                "To tag a video, the video support feature must be enabled."
                "", status=annots.error)

    # ----------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) time-aligned phonemes, video file
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get the tier from which we'll generate LPC keys
        parser = sppasRW(input_file[0])
        trs_input = parser.read()
        tier_input = sppasFindTier.aligned_phones(trs_input)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('lpc_result_of', input_file[0])

        # Create the tier with the lpc syllables
        tier_lpc = self.convert(tier_input)
        trs_output.append(tier_lpc)
        # Create the tier with the lpc keys
        tier_keys = self.create_keys(tier_lpc)
        trs_output.append(tier_keys)

        # Extra result: create a video with the keys
        if self._options['createvideo']:
            if len(input_file) > 1:
                self.make_video(input_file[1], tier_keys)
            else:
                self.logfile.print_message(
                    "The option to tag the video was enabled but no video "
                    "was found related to the annotated file {}"
                    "".format(input_file[0]), status=-1)

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
        return self._options.get("outputpattern", "-lpc")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "-palign")

    # -----------------------------------------------------------------------
    # Utilities:
    # -----------------------------------------------------------------------

    @staticmethod
    def _phon_to_intervals(phonemes):
        """Create the intervals to be syllabified.

        We could use symbols.phone only, but for backward compatibility
        we hardly add the symbols we previously used into SPPAS.

        :return: a tier with the consecutive filled intervals.

        """
        stop = list(symbols.phone.keys())
        stop.append('#')
        stop.append('@@')
        stop.append('+')
        stop.append('gb')
        stop.append('lg')

        return phonemes.export_to_intervals(stop)
