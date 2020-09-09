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

    src.annotations.Momel.sppasmomel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from sppas.src.structs import sppasOption

import sppas.src.anndata.aio
from sppas.src.config import annots

from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyInputError
from ..annotationsexc import NoInputError

from .momel import Momel

# ---------------------------------------------------------------------------


class sppasMomel(sppasBaseAnnotation):
    """SPPAS integration of Momel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasMomel instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasMomel, self).__init__("momel.json", log)
        self.__momel = Momel()

        # Add an option
        self._options['elim_glitch'] = True

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - lfen1
            - hzinf
            - hzsup
            - maxec
            - lfen2
            - seuildiff_x
            - seuildiff_y
            - glitch

        :param options: (sppasOption)

        """
        for opt in options:

            if isinstance(opt, sppasOption):
                key = opt.get_key()
                value = opt.get_value()
            else:
                key = opt
                value = options[key]

            if "win1" == key:
                self.set_option_win1(value)

            elif "lo" == key:
                self.set_option_lo(value)

            elif "hi" == key:
                self.set_option_hi(value)

            elif "maxerr" == key:
                self.set_option_maxerr(value)

            elif "win2" == key:
                self.set_option_win2(value)

            elif "mind" == key:
                self.set_option_mind(value)

            elif "minr" == key:
                self.set_option_minr(value)

            elif "elim_glitch" == key:
                self.set_option_elim_glitch(value)

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_option_win1(self, value):
        self._options['win1'] = value

    # -----------------------------------------------------------------------

    def set_option_lo(self, value):
        self._options['lo'] = value

    # -----------------------------------------------------------------------

    def set_option_hi(self, value):
        self._options['hi'] = value

    # -----------------------------------------------------------------------

    def set_option_maxerr(self, value):
        self._options['maxerr'] = value

    # -----------------------------------------------------------------------

    def set_option_win2(self, value):
        self._options['win2'] = value

    # -----------------------------------------------------------------------

    def set_option_mind(self, value):
        self._options['mind'] = value

    # -----------------------------------------------------------------------

    def set_option_minr(self, value):
        self._options['minr'] = value

    # -----------------------------------------------------------------------

    def set_option_elim_glitch(self, value):
        self._options['elim_glitch'] = value

    # -----------------------------------------------------------------------
    # Annotate
    # -----------------------------------------------------------------------

    @staticmethod
    def fix_pitch(input_filename):
        """Load pitch values from a file.

        It is supposed that the given file contains a tier with name "Pitch"
        with a pitch value every 10ms, or a tier with name "PitchTier".

        :returns: A list of pitch values (one value each 10 ms).

        """
        parser = sppasRW(input_filename)
        trs = parser.read()
        pitch_tier = trs.find("Pitch")
        if pitch_tier is None:
            pitch_tier = trs.find("PitchTier")
            if pitch_tier is not None:
                pitch_list = trs.to_pitch()
            else:
                raise NoInputError
        else:
            pitch_list = [round(a.get_best_tag().get_typed_content(), 6)
                          for a in pitch_tier]

        if len(pitch_list) == 0:
            raise EmptyInputError(name="Pitch")

        return pitch_list

    # -----------------------------------------------------------------------

    def estimate_momel(self, ipu_pitch, current_time):
        """Estimate momel on an IPU.

        :param ipu_pitch: (list of float) Pitch values of an IPU.
        :param current_time: (float) Time value of the last pitch value
        :returns: (list of Anchor)

        """
        self.__momel.set_option_win1(self._options['win1'])
        self.__momel.set_option_lo(self._options['lo'])
        self.__momel.set_option_hi(self._options['hi'])
        self.__momel.set_option_maxerr(self._options['maxerr'])
        self.__momel.set_option_win2(self._options['win2'])
        self.__momel.set_option_mind(self._options['mind'])
        self.__momel.set_option_minr(self._options['minr'])
        self.__momel.set_option_elim_glitch(self._options['elim_glitch'])

        # Estimates the real start time of the IPU
        ipu_start_time = current_time - (len(ipu_pitch)) + 1

        # Search for anchors
        try:
            anchors = self.__momel.annotate(ipu_pitch)
        except Exception as e:
            self.logfile.print_message(
                    'No anchors found between time ' +
                    str(ipu_start_time * 0.01) + " and time " +
                    str(current_time * 0.01) + ": " + str(e),
                    indent=2, status=annots.warning)
            anchors = list()
            pass

        # Adjust time values in the anchors
        for i in range(len(anchors)):
            anchors[i].x += ipu_start_time

        return anchors

    # -----------------------------------------------------------------------

    @staticmethod
    def anchors_to_tier(anchors):
        """Transform anchors to a sppasTier.

        Anchors are stored in frames. It is converted to seconds (a frame is
        during 10ms).

        :param anchors: (List of Anchor)
        :returns: (sppasTier)

        """
        tier = sppasTier('Momel')
        for anchor in anchors:
            tier.create_annotation(
                sppasLocation(sppasPoint(anchor.x * 0.01, 0.005)),
                sppasLabel(sppasTag(anchor.y, "float"))
            )

        return tier

    # -----------------------------------------------------------------------

    def convert(self, pitch):
        """Search for momel anchors.

        :param pitch: (list of float) pitch values samples at 10ms
        :returns: sppasTier

        """
        # Selected values (anchor points) for this set of pitch values
        targets = list()

        # List of pitch values of one **estimated** Inter-Pausal-Unit (ipu)
        ipu_pitch = []
        # Number of consecutive null F0 values
        nbzero = 0
        # Current time value
        curtime = 0
        # For each f0 value of the wav file
        for p in pitch:
            if p == 0.:
                nbzero += 1
            else:
                nbzero = 0
            ipu_pitch.append(p)

            # If the number of 0. values exceed 250ms,
            # we consider this is a silence and we estimate Momel
            # on the recorded list of pitch values of the **estimated** IPU.
            if (nbzero * 10) > 249:
                if len(ipu_pitch) > 0 and (len(ipu_pitch) > nbzero):
                    ipu_anchors = self.estimate_momel(ipu_pitch, curtime)
                    # add this targets to the targets list
                    targets.extend(ipu_anchors)
                    ipu_pitch = list()

            curtime += 1

        # last ipu
        ipu_anchors = self.estimate_momel(ipu_pitch, curtime)
        targets.extend(ipu_anchors)

        return sppasMomel.anchors_to_tier(targets)

    # -----------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output=None):
        """Run the automatic annotation process on an input.

        :param input_file: (list of str) pitch values
        :param opt_input_file: (list of str) ignored
        :param output: (str) the output name
        :returns: (sppasTranscription)

        """
        # Get pitch values from the input
        pitch = self.fix_pitch(input_file[0])

        # Search for anchors
        anchors_tier = self.convert(pitch)
        self.logfile.print_message(str(len(anchors_tier)) + " anchors found.",
                                   indent=2, status=annots.info)

        # Fix result
        trs_output = sppasTranscription(self.name)
        trs_output.append(anchors_tier)
        trs_output.set_meta('annotation_result_of', input_file[0])

        if output is not None:
            output_file = self.fix_out_file_ext(output)
            parser = sppasRW(output_file)
            parser.write(trs_output)
            return [output_file]

        return trs_output

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-momel")

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        return sppas.src.anndata.aio.primary_in
