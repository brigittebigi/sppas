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

    src.annotations.Intsint.sppasintsint.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from sppas import sppasRW
from sppas import sppasTranscription
from sppas import sppasTier
from sppas import sppasLabel
from sppas import sppasTag

from sppas.src.anndata.anndataexc import AnnDataTypeError
from sppas.src.anndata.anndataexc import AnnDataEqError

from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier

from .intsint import Intsint

# ---------------------------------------------------------------------------


class sppasIntsint(sppasBaseAnnotation):
    """SPPAS integration of the INTSINT automatic annotation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasIntsint instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasIntsint, self).__init__("intsint.json", log)
        self.__intsint = Intsint()

    # -----------------------------------------------------------------------
    # Methods to annotate
    # -----------------------------------------------------------------------

    @staticmethod
    def tier_to_anchors(momel_tier):
        """Initialize INTSINT attributes from a Tier with anchors.

        :param momel_tier: (sppasTier)
        :returns: List of tuples (time, f0 value)

        """
        if momel_tier.is_point() is False:
            raise AnnDataTypeError(momel_tier.get_name(), 'PointTier')

        targets = list()
        for ann in momel_tier:

            # Get the f0 value
            tag = ann.get_best_tag(label_idx=0)
            try:
                f0 = float(tag.get_content())
            except TypeError:
                raise AnnDataTypeError(tag, 'float')
            except ValueError:
                raise AnnDataTypeError(tag, 'float')

            # Get the time value
            try:
                time = float(ann.get_highest_localization().get_midpoint())
            except TypeError:
                raise AnnDataTypeError(ann.get_highest_localization(), 'float')
            except ValueError:
                raise AnnDataTypeError(ann.get_highest_localization(), 'float')

            targets.append((time, f0))

        return targets

    # -------------------------------------------------------------------

    @staticmethod
    def tones_to_tier(tones, anchors_tier):
        """Convert the INTSINT result into a tier.

        :param tones: (list)
        :param anchors_tier: (sppasTier)

        """
        if len(tones) != len(anchors_tier):
            raise AnnDataEqError("tones:"+str(len(tones)),
                                 "anchors:"+str(len(anchors_tier)))

        tier = sppasTier("INTSINT")
        for tone, anchor_ann in zip(tones, anchors_tier):
            # Create the label
            tag = sppasTag(tone)
            # Create the location
            location = anchor_ann.get_location().copy()
            # Create the annotation
            tier.create_annotation(location, sppasLabel(tag))

        return tier

    # -----------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output_file=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) momel anchors
        :param opt_input_file: (list of str) ignored
        :param output_file: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get the tier to be annotated.
        parser = sppasRW(input_file[0])
        trs_input = parser.read()
        tier_input = sppasFindTier.pitch_anchors(trs_input)

        # Annotate the tier
        targets = sppasIntsint.tier_to_anchors(tier_input)
        tones = self.__intsint.annotate(targets)
        tier_intsint = sppasIntsint.tones_to_tier(tones, tier_input)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        trs_output.append(tier_intsint)
        trs_output.set_meta('intsint_result_of', input_file[0])

        # Save in a file
        if output_file is not None:
            parser = sppasRW(output_file)
            parser.write(trs_output)

        return trs_output

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-intsint")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", "-momel")
