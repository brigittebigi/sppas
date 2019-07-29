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

    src.annotations.Activity.activity.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import symbols

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasLabel, sppasTag
from sppas.src.anndata.aio.aioutils import fill_gaps, unfill_gaps
from sppas.src.utils.makeunicode import sppasUnicode

# ---------------------------------------------------------------------------


class Activity(object):
    """Create an activity tier from time-aligned tokens.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self):
        """Create a sppasActivity instance with the default symbols."""
        self._activities = dict()
        self.set_activities()

    # -----------------------------------------------------------------------

    def set_activities(self, activities=symbols.all):
        """Fix the dictionary of possible non-speech activities.

        :param activities: (dict) A dictionary of activities.
        The key is the token; the value is the name of the activity.

        """
        self._activities = dict()
        for token in activities:
            self.append_activity(token, activities[token])

        # For empty intervals... activity is unknown
        self.append_activity(symbols.unk, "")

    # -----------------------------------------------------------------------

    def append_activity(self, token, activity):
        """Append a new activity.

        :param token: (str) The token of the tier TokensAlign
        :param activity: (str) Name of the activity

        """
        sp = sppasUnicode(token)
        token = sp.to_strip()

        sp = sppasUnicode(activity)
        activity = sp.to_strip()

        if token not in self._activities:
            self._activities[token] = activity

    # -----------------------------------------------------------------------

    def fix_activity(self, annotation):
        """Return the activity name of an annotation."""
        if annotation.is_labelled() is False:
            text_content = symbols.unk
        else:
            text_content = annotation.serialize_labels()
        return self._activities.get(text_content, "speech")

    # -----------------------------------------------------------------------

    def get_tier(self, tokens_tier, tmin, tmax):
        """Create and return the activity tier.

        :param tokens_tier: (sppasTier) a tier with time-aligned tokens
        :returns: sppasTier

        """
        new_tier = sppasTier('Activity')
        activity = "<INIT>"  # initial activity

        if tokens_tier.is_empty():
            return new_tier
        tokens = fill_gaps(tokens_tier, tmin, tmax)

        if len(tokens) == 0:
            return new_tier

        if len(tokens) == 1:
            new_tier.create_annotation(
                tokens[0].get_location().copy(),
                sppasLabel(sppasTag(self.fix_activity(tokens[0]))))
            return new_tier

        for ann in tokens:
            new_activity = self.fix_activity(ann)
            # The activity has changed
            if activity != new_activity and activity != "<INIT>":
                if len(new_tier) == 0:
                    begin = tokens.get_first_point().copy()
                else:
                    begin = new_tier.get_last_point().copy()

                new_tier.create_annotation(
                    sppasLocation(
                        sppasInterval(
                            begin,
                            ann.get_lowest_localization())),
                    sppasLabel(sppasTag(activity)))

            # In any case, update current activity
            activity = new_activity

        # last registered activity (we ignored it)

        if len(new_tier) == 0:
            # we observed only one activity...
            new_tier.create_annotation(
                sppasLocation(sppasInterval(
                    tokens.get_first_point(),
                    tokens.get_last_point())),
                sppasLabel(sppasTag(activity)))

        else:
            if new_tier.get_last_point() < tokens.get_last_point():
                new_tier.create_annotation(
                    sppasLocation(sppasInterval(
                        new_tier.get_last_point(),
                        tokens.get_last_point())),
                    sppasLabel(sppasTag(activity)))

        new_tier = unfill_gaps(new_tier)
        new_tier.set_name('Activity')
        return new_tier

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        return str(self._activities)

    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._activities)

    # -----------------------------------------------------------------------

    def __contains__(self, item):
        return item in self._activities

    # ------------------------------------------------------------------------

    def __iter__(self):
        for a in self._activities:
            yield a
