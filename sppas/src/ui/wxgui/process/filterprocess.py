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

    wxgui.process.filterprocess.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx
import logging

from sppas.src.analysis import sppasTierFilters
from sppas.src.ui.wxgui.views.processprogress import ProcessProgressDialog

# ----------------------------------------------------------------------------


class FilterProcess(object):

    def __init__(self, parent, file_manager):
        """Filter process for any kind of filters.

        :param parent: (SingleFilterDialog/RelationFilterDialog)
        :param file_manager: (xFiles)

        """
        self.parent = parent.GetParent()

        # List of files/tiers to filter
        self.file_manager = file_manager

        # for "rel" and "sel" filters only
        try:
            # List of selected data
            self.data = parent.GetSelectedData()
            # Output tier name
            self.tier_name = parent.GetFiltererdTierName()
            # Output format
            self.annot_format = parent.GetAnnotationFormat()
        except:
            self.data = None

        # for "rel" filter only
        try:
            self.y_tier_name = parent.GetRelationTierName()
        except AttributeError:
            self.y_tier_name = None

        # for "tag", "loc" and "dur" filters
        try:
            # Match all or match any of the filters
            self.match_all = parent.GetMatchAll()
        except AttributeError:
            self.match_all = None

    # -----------------------------------------------------------------------

    def run_on_tier(self, tier, tierY=None):
        """Apply filters on a tier.

        :param tier: (sppasTier)
        :param tierY: (sppasTier)
        :returns: (sppasTier)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def run(self):
        """Filter all the given tiers."""

        wx.BeginBusyCursor()
        # Create a progress bar
        progress = ProcessProgressDialog(self.parent,
                                         self.parent._prefsIO,
                                         "Filtering progress...")
        progress.set_header("Filter system")
        progress.update(0, "")
        total = self.file_manager.GetSize()

        for i in range(self.file_manager.GetSize()):
            # obj is a TrsList instance
            obj = self.file_manager.GetObject(i)
            trs = obj.GetTranscription()

            # find the Y-tier
            y_tier = None
            if self.y_tier_name is not None:
                y_tier = trs.find(self.y_tier_name)

            for tier in trs:
                # tier is selected to be filtered
                if obj.IsSelected(tier.get_name()):
                    progress.set_header(self.file_manager.GetFilename(i))
                    progress.set_text(tier.get_name())

                    # so, we do the job!
                    try:
                        new_tier = self.run_on_tier(tier, y_tier)
                        if new_tier is not None:
                            # add the new tier both in Transcription and in the list
                            obj.AddTier(new_tier)
                    except Exception as e:
                        logging.error(str(e))

                    progress.set_fraction(float((i+1))/float(total))

        # Indicate completed!
        progress.update(1, "Completed.\n")
        # progress.set_header("")
        progress.close()
        wx.EndBusyCursor()

# ----------------------------------------------------------------------------


class UnlabelledFilterProcess(FilterProcess):

    def run_on_tier(self, tier, tier_y=None):
        """Apply filters on a tier.

        :param tier: (sppasTier) tier to be filtered
        :param tier_y: (sppasTier) ignored
        :returns: (sppasTier)

        """
        logging.info("Apply UnlabelledFilter() on tier: {:s}".format(tier.get_name()))
        filtered_tier = tier.copy()
        nb = filtered_tier.remove_unlabelled()
        logging.info("  -> {:d} annotation(s) removed".format(nb))
        filtered_tier.set_name(tier.get_name() + "-gaps")
        return filtered_tier

# ----------------------------------------------------------------------------


class SingleFilterProcess(FilterProcess):

    def run_on_tier(self, tier, tier_y=None):
        """Apply filters on a tier.

        :param tier: (sppasTier) tier to be filtered
        :param tier_y: (sppasTier) ignored
        :returns: (sppasTier)

        """
        logging.info("Apply sppasFilter() on tier: {:s}".format(tier.get_name()))
        sfilter = sppasTierFilters(tier)
        ann_sets = list()

        for d in self.data:

            if len(d[2]) >= 1:
                d2 = sppasTierFilters.cast_data(tier, d[0], d[2][0])

                # a little bit of doc:
                #   - getattr() returns the value of the named attributed of object:
                #     it returns f.tag if called like getattr(f, "tag")
                #   - func(**{'x': '3'}) is equivalent to func(x='3')
                #
                logging.info(" >>> filter.{:s}({:s}={!s:s})".format(d[0], d[1], d2))

                ann_set = getattr(sfilter, d[0])(**{d[1]: d2})
                for i in range(1, len(d[2])):
                    d2 = sppasTierFilters.cast_data(tier, d[0], d[2][i])
                    logging.info(" >>>    | filter.{:s}({:s}={!s:s})".format(d[0], d[1], d2))
                    ann_set = ann_set | getattr(sfilter, d[0])(**{d[1]: d2})
            else:
                return None
            ann_sets.append(ann_set)

        # no annotation is matching
        if len(ann_sets) == 0:
            return None

        # Merge results (apply '&' or '|' on the resulting data sets)
        ann_set = ann_sets[0]
        if self.match_all:
            for i in range(1, len(ann_sets)):
                ann_set = ann_set & ann_sets[i]
                if len(ann_set) == 0:
                    return None
        else:
            for i in range(1, len(ann_sets)):
                ann_set = ann_set | ann_sets[i]

        # convert the annotations set into a tier
        filtered_tier = ann_set.to_tier(name=self.tier_name,
                                        annot_value=self.annot_format)

        return filtered_tier

# ---------------------------------------------------------------------------


class RelationFilterProcess(FilterProcess):

    def run_on_tier(self, tier, tier_y=None):
        """Apply filters on a tier.

        :param tier: (sppasTier) tier to be filtered
        :param tier_y: (sppasTier) required
        :returns: (sppasTier)

        """
        if tier_y is None:
            return None

        logging.info("Apply sppasFilter() on tier: {:s}".format(tier.get_name()))
        sfilter = sppasTierFilters(tier)

        logging.debug("Data in RelationFilterProcess: {:s}".format(self.data))
        ann_set = sfilter.rel(tier_y,
                              *(self.data[0]),
                              **{self.data[1][i][0]: self.data[1][i][1] for i in range(len(self.data[1]))})

        # convert the annotations set into a tier
        filtered_tier = ann_set.to_tier(name=self.tier_name,
                                        annot_value=self.annot_format)

        return filtered_tier
