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

    src.annotations.Activity.sppasactivity.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import logging

from sppas.src.config import info, annots
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription, sppasTier
from sppas.src.anndata import sppasLabel, sppasTag, sppasLocation

from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError
from ..searchtier import sppasFindTier
from ..annotationsexc import NoInputError
from .activity import Activity

# ---------------------------------------------------------------------------

MSG_EXTRA_TIER = (info(1270, "annotations"))

# ---------------------------------------------------------------------------


class sppasActivity(sppasBaseAnnotation):
    """SPPAS integration of the Activity generation.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, log=None):
        """Create a new sppasActivity instance.

        Log is used for a better communication of the annotation process and
        its results.
        If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        sppasBaseAnnotation.__init__(self, "activity.json", log)
        self.__activity = Activity()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - duration

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()

            if "duration" == key:
                self.set_duration_tier(opt.get_value())

            elif key in ("inputpattern", "outputpattern", "inputoptpattern"):
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_duration_tier(self, value):
        """Fix the activity duration option.

        :param value: (bool) Activity tier generation.

        """
        self._options['duration'] = bool(value)

    # -----------------------------------------------------------------------
    # Automatic annotation
    # -----------------------------------------------------------------------

    def convert(self, tier, tmin, tmax):
        """Create an Activity and ActivityDuration tier.

        :param tier: (sppasTier)
        :param tmin: (sppasPoint)
        :param tmax: (sppasPoint)
        :returns: (tier, tier)

        """
        try:
            activity = self.__activity.get_tier(tier, tmin, tmax)
        except Exception as e:
            self.logfile.print_message(
                MSG_EXTRA_TIER.format(
                    tiername="Activity", message=str(e)),
                    indent=2, status=annots.warning)
            return None, None

        duration = None
        if self._options['duration'] is True:
            duration = sppasTier('ActivityDuration')
            for a in activity:
                interval = a.get_location().get_best()
                dur = interval.duration().get_value()
                duration.create_annotation(
                    sppasLocation(interval.copy()),
                    sppasLabel(sppasTag(dur, tag_type="float"))
                )

        return activity, duration

    # -----------------------------------------------------------------------

    def run(self, input_file, opt_input_file=None, output=None):
        """Run the automatic annotation process on an input.

        Important: options could be changed!

        :param input_file: (list of str) (time-aligned tokens)
        :param opt_input_file: (list of str) Ignored.
        :param output: (str) the output name - either filename or basename
        :returns: (sppasTranscription)

        """
        # Get the time-aligned tokens tier
        parser = sppasRW(input_file[0])
        trs_input = parser.read()
        tok_tier = sppasFindTier.aligned_tokens(trs_input)
        if tok_tier is None:
            raise NoInputError

        tmin = trs_input.get_min_loc()
        tmax = trs_input.get_max_loc()
        activity, duration = self.convert(tok_tier, tmin, tmax)

        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('token_activity_result_of', input_file[0])
        self.transfer_metadata(trs_input, trs_output)
        trs_output.append(activity)

        # if duration is not None:
        #     try:
        #         trs_output.append(duration)
        #         trs_output.add_hierarchy_link("TimeAssociation", activity, duration)
        #     except:
        #         logging.error('No hierarchy was created between activity and duration.')

        # Save results
        if output is not None:
            output_file = self.fix_out_file_ext(output)
            parser = sppasRW(output_file)
            parser.write(trs_output)

        return trs_output

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-activity")

    def get_input_pattern(self):
        """Pattern this annotation expects for its input filename."""
        return self._options.get("inputpattern", '-palign')
