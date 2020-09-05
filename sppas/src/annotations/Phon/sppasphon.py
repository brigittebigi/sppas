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

    src.annotations.sppasphon.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import symbols
from sppas.src.config import separators
from sppas.src.config import annots
from sppas.src.config import info

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from sppas.src.resources import sppasDictPron
from sppas.src.resources import sppasMapping

from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyInputError
from ..annotationsexc import EmptyOutputError
from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier

from .phonetize import sppasDictPhonetizer

# ---------------------------------------------------------------------------

SIL = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]
SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class sppasPhon(sppasBaseAnnotation):
    """SPPAS integration of the Phonetization automatic annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a sppasPhon instance without any linguistic resources.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasPhon, self).__init__("phonetize.json", log)
        self.__phonetizer = None
        self.maptable = sppasMapping()
        self.load_resources()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - phonunk
            - usesstdtokens

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()

            if key == "phonunk":
                self.set_unk(opt.get_value())

            elif key == "usestdtokens":
                self.set_usestdtokens(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_unk(self, unk):
        """Fix the unk option value.

        :param unk: (bool) If unk is set to True, the system attempts
        to phonetize unknown entries (i.e. tokens missing in the dictionary).
        Otherwise, the phonetization of an unknown entry unit is set to the
        default stamp.

        """
        self._options['phonunk'] = unk

    # -----------------------------------------------------------------------

    def set_usestdtokens(self, stdtokens):
        """Fix the stdtokens option.

        :param stdtokens: (bool) If it is set to True, the phonetization
        uses the standard transcription as input, instead of the faked
        transcription. This option does make sense only for an Enriched
        Orthographic Transcription.

        """
        self._options['usestdtokens'] = stdtokens

    # -----------------------------------------------------------------------
    # Methods to phonetize series of data
    # -----------------------------------------------------------------------

    def load_resources(self, dict_filename=None, map_filename=None, **kwargs):
        """Set the pronunciation dictionary and the mapping table.

        :param dict_filename: (str) The pronunciation dictionary in HTK-ASCII
        format with UTF-8 encoding.

        :param map_filename: (str) is the filename of a mapping table. It is \
        used to generate new pronunciations by mapping phonemes of the dict.

        """
        if map_filename is not None:
            self.maptable = sppasMapping(map_filename)
            self.logfile.print_message(
                (info(1160, "annotations")).format(len(self.maptable)),
                indent=0)
        else:
            self.maptable = sppasMapping()

        pdict = sppasDictPron(dict_filename, nodump=False)
        if dict_filename is not None:
            self.__phonetizer = sppasDictPhonetizer(pdict, self.maptable)
            self.logfile.print_message(
                (info(1162, "annotations")).format(len(pdict)),
                indent=0)
        else:
            self.__phonetizer = sppasDictPhonetizer(pdict)

    # -----------------------------------------------------------------------

    def _phonetize(self, entry):
        """Phonetize a text.

        Because we absolutely need to match with the number of tokens, this
        method will always return a string: either the automatic phonetization
        (from dict or from phonunk) or the unk stamp.

        :param entry: (str) The string to be phonetized.
        :returns: phonetization of the given entry

        """
        unk = symbols.unk
        tab = self.__phonetizer.get_phon_tokens(
            entry.split(),
            phonunk=self._options['phonunk'])
        tab_phones = list()
        for tex, p, s in tab:
            message = None
            if s == annots.error:
                message = (info(1110, "annotations")).format(tex) + \
                          info(1114, "annotations")
                self.logfile.print_message(message, indent=2, status=s)
                return [unk]
            else:
                if s == annots.warning:
                    message = (info(1110, "annotations")).format(tex)
                    if len(p) > 0:
                        message = message + (info(1112, "annotations")).format(p)
                    else:
                        message = message + info(1114, "annotations")
                        p = unk
                tab_phones.append(p)

            if message:
                self.logfile.print_message(message, indent=2, status=s)

        return tab_phones

    # -----------------------------------------------------------------------

    def convert(self, tier):
        """Phonetize annotations of a tokenized tier.

        :param tier: (Tier) the ortho transcription previously tokenized.
        :returns: (Tier) phonetized tier with name "Phones"

        """
        if tier is None:
            raise IOError('No given tier.')
        if tier.is_empty() is True:
            raise EmptyInputError(name=tier.get_name())

        phones_tier = sppasTier("Phones")
        for i, ann in enumerate(tier):
            self.logfile.print_message(
                (info(1220, "annotations")).format(number=i+1), indent=1)

            location = ann.get_location().copy()
            labels = list()

            # Some labels can contain a whitespace and it's a token separator.
            # (when transcription was read, the \n was used as separator but
            # some file formats don't support it and are using whitespace)
            normalized = list()
            for label in ann.get_labels():
                if " " in label:
                    normalized.extend(label.split())
                else:
                    normalized.append(label)

            # Phonetize all labels of the normalized transcription
            for label in normalized:

                phonetizations = list()
                for text, score in label:
                    if text.is_pause() or text.is_silence():
                        # It's in case the pronunciation dictionary
                        # were not properly fixed.
                        phonetizations.append(SIL)

                    elif text.is_empty() is False:
                        phones = self._phonetize(text.get_content())
                        for p in phones:
                            phonetizations.extend(p.split(separators.variants))

                # New in SPPAS 1.9.6.
                #  - The result is a sequence of labels.
                #  - Variants are alternative tags.
                tags = [sppasTag(p) for p in set(phonetizations)]
                labels.append(sppasLabel(tags))

            phones_tier.create_annotation(location, labels)

        return phones_tier

    # ------------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) normalized text
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get the tier to be phonetized.
        pattern = ""
        if self._options['usestdtokens'] is True:
            pattern = "std"
        parser = sppasRW(input_file[0])
        trs_input = parser.read()
        tier_input = sppasFindTier.tokenization(trs_input, pattern)

        # Phonetize the tier
        tier_phon = self.convert(tier_input)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        if tier_phon is not None:
            trs_output.append(tier_phon)

        trs_output.set_meta('text_phonetization_result_of',
                            input_file[0])
        trs_output.set_meta('text_phonetization_dict',
                            self.__phonetizer.get_dict_filename())
        self.transfer_metadata(trs_input, trs_output)

        # Save in a file
        if output_file is not None:
            if len(trs_output) > 0:
                parser = sppasRW(output_file)
                parser.write(trs_output)
            else:
                raise EmptyOutputError

        return trs_output

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-phon")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "-token")
