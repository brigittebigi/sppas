#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: descriptivestats.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

import os.path
import wx

from sppas.src.analysis.tierstats import sppasTierStats

from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog
from sppas.src.ui.wxgui.sp_icons import SPREADSHEETS
from sppas.src.ui.wxgui.ui.CustomListCtrl import SortListCtrl
from sppas.src.ui.wxgui.panels.basestats import BaseStatPanel

# ----------------------------------------------------------------------------


class DescriptivesStatsDialog(spBaseDialog):
    """Display descriptive stats of tiers.

    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL, v3

    Dialog for the user to display and save various descriptive statistics
    of a set of tiers.

    """

    def __init__(self, parent, preferences, tiers={}):
        """Constructor.

        @param parent is the parent wx object.
        @param preferences (Preferences)
        @param tiers: a dictionary with key=filename, value=list of selected tiers

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Descriptive statistics")
        wx.GetApp().SetAppName("descriptivesstats")

        # Options to evaluate stats:
        self.n = 1
        self.withradius = 0
        self.withalt = False

        self._data = {}   # to store stats
        for k, v in tiers.items():
            # k = filename
            # v = list of tiers
            for tier in v:
                ts = sppasTierStats(tier, self.n, self.withradius, self.withalt)
                self._data[ts] = k
                # remark: statistics are not estimated yet.
                # ts contains a pointer to the tier; ts.tier

        titlebox = self.CreateTitle(SPREADSHEETS, "Descriptive statistics of a set of tiers")
        contentbox = self._create_content()
        buttonbox = self._create_buttons()

        self.LayoutComponents(titlebox, contentbox, buttonbox)

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_toolbar(self):
        font = self.preferences.GetValue('M_FONT')
        font.SetPointSize(font.GetPointSize() - 2)

        title_label = wx.StaticText(self, label="N-gram:", style=wx.ALIGN_CENTER)
        title_label.SetFont(font)
        ngrambox = wx.ComboBox(self, -1, choices=[str(i) for i in range(1,6)], style=wx.CB_READONLY)
        ngrambox.SetSelection(0)
        ngrambox.SetFont(font)

        lablist = ['Use only the tag with the best score', 'Include also alternative tags']
        withaltbox = wx.RadioBox(self, -1, label="Annotation labels:", choices=lablist, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        withaltbox.SetFont(font)

        durlist = ['Use only Midpoint value', 'Add the Radius value', 'Deduct the Radius value']
        withradiusbox = wx.RadioBox(self, -1, label="Annotation durations:", choices=durlist, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        withradiusbox.SetFont(font)

        self.AddToolbar([title_label, ngrambox], [withaltbox, withradiusbox])

        self.Bind(wx.EVT_COMBOBOX, self.OnNgram, ngrambox)
        self.Bind(wx.EVT_RADIOBOX, self.OnWithAlt, withaltbox)
        self.Bind(wx.EVT_RADIOBOX, self.OnWithRadius, withradiusbox)

    def _create_content(self):
        self._create_toolbar()
        self.notebook = wx.Notebook(self)

        page1 = SummaryPanel(self.notebook,  self.preferences, "summary")
        page2 = DetailedPanel(self.notebook, self.preferences, "occurrences")
        page3 = DetailedPanel(self.notebook, self.preferences, "total")
        page4 = DetailedPanel(self.notebook, self.preferences, "mean")
        page5 = DetailedPanel(self.notebook, self.preferences, "median")
        page6 = DetailedPanel(self.notebook, self.preferences, "stdev")

        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "   Summary   ")
        self.notebook.AddPage(page2, " Occurrences ")
        self.notebook.AddPage(page3, "Total durations")
        self.notebook.AddPage(page4, "Mean durations")
        self.notebook.AddPage(page5, "Median durations")
        self.notebook.AddPage(page6, "Std dev. durations")

        page1.ShowStats(self._data)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged)

        return self.notebook

    def _create_buttons(self):
        btn_save = self.CreateSaveButton("Save the currently displayed sheet")
        btn_close = self.CreateCloseButton()
        self.Bind(wx.EVT_BUTTON, self._on_save, btn_save)
        return self.CreateButtonBox([btn_save], [btn_close])

    # -------------------------------------------------------------------------
    # Callbacks to events
    # -------------------------------------------------------------------------

    def _on_save(self, event):
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.SaveAs(outfilename="stats-%s.csv" % page.name)

    def OnNotebookPageChanged(self, event):
        oldselection = event.GetOldSelection()
        newselection = event.GetSelection()
        if oldselection != newselection:
            page = self.notebook.GetPage(newselection)
            page.ShowStats(self._data)
            page.Refresh()

    def OnNgram(self, event):
        # get new n value of the N-gram
        self.n = int(event.GetSelection()+1)
        # update infos of TierStats objects
        for ts in self._data:
            ts.set_ngram(self.n)
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.ShowStats(self._data)

    def OnWithAlt(self, event):
        newvalue = bool(event.GetSelection())
        if self.withalt == newvalue:
            return
        self.withalt = newvalue
        # update infos of TierStats objects
        for ts in self._data:
            ts.set_withalt(self.withalt)
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.ShowStats(self._data)

    def OnWithRadius(self, event):
        if event.GetSelection() == 0:
            if not self.withradius == 0:
                self.withradius = 0
            else:
                return
        elif event.GetSelection() == 1:
            if not self.withradius == -1:
                self.withradius = -1
            else:
                return
        elif event.GetSelection() == 2:
            if not self.withradius == 1:
                self.withradius = 1
            else:
                return
        # update infos of TierStats objects
        for ts in self._data:
            ts.set_with_radius(self.withradius)
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.ShowStats(self._data)

# ----------------------------------------------------------------------------
# First tab: summary
# ----------------------------------------------------------------------------


class SummaryPanel(BaseStatPanel):
    """Summary of descriptive stats of all merged-tiers.

    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ("Label", "Occurrences", "Total durations", "Mean durations", "Median durations", "Std dev. durations")

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """Show descriptive statistics of set of tiers as list."""

        if not data or len(data) == 0:
            self.ShowNothing()
            return

        self.statctrl = SortListCtrl(self, size=(-1, 400))

        for i, col in enumerate(self.cols):
            self.statctrl.InsertColumn(i, col)
            self.statctrl.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        self.statctrl.SetColumnWidth(0, 200)

        # create a TierStats (with durations of all tiers)
        ts = self.__get_ts(data)

        # estimates descriptives statistics
        ds = ts.ds()
        occurrences = ds.len()
        total = ds.total()
        mean = ds.mean()
        median = ds.median()
        stdev = ds.stdev()

        # fill rows
        self.rowdata = []
        for i, key in enumerate(occurrences.keys()):
            row = [key, occurrences[key], total[key], mean[key], median[key], stdev[key]]
            # add the data content in rowdata
            self.rowdata.append(row)
            # add into the listctrl
            self.AppendRow(i, row, self.statctrl)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL | wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

    # ------------------------------------------------------------------------

    def __get_ts(self, data):
        tiers = []
        n = 1
        with_alt = False
        with_radius = 0
        for ts, f in data.items():
            if isinstance(ts.tier, list) is False:
                tiers.append(ts.tier)
            else:
                tiers.extend(ts.tier)
            # TODO:check if all n/withalt/withradius are the same
            # (it can happen for now, so it's a todo!)
            n = ts.get_ngram()
            with_alt = ts.get_with_alt()
            with_radius = ts.get_with_radius()
        return sppasTierStats(tiers, n, with_radius, with_alt)

# ----------------------------------------------------------------------------
# Other tabs: details of each file
# ----------------------------------------------------------------------------


class DetailedPanel(BaseStatPanel):
    """
    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL
    @summary: Details of descriptive stats: either occurrences, or durations of each tier.

    """

    def __init__(self, parent, prefsIO, name):
        BaseStatPanel.__init__(self, parent, prefsIO, name)
        self.cols = ('',)

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """Show descriptive statistics of set of tiers as list.

        @param data (dict) Dictionary with key=TierStats and value=filename
        
        """
        if not data or len(data) == 0:
            self.ShowNothing()
            return

        self.statctrl = SortListCtrl(self, size=(-1, 400))

        # create columns
        self.cols = ("Tags",) + tuple(os.path.basename(v)+":"+ts.get_tier().get_name() for ts, v in data.items())
        for i, col in enumerate(self.cols):
            self.statctrl.InsertColumn(i, col)
            self.statctrl.SetColumnWidth(i, 120)
        self.statctrl.SetColumnWidth(0, 200)

        # estimates descriptives statistics
        statvalues = []
        items = []     # the list of labels
        for ts in data.keys():
            ds = ts.ds()
            if self.name == "occurrences":
                statvalues.append(ds.len())
                
            elif self.name == "total":
                statvalues.append(ds.total())
                
            elif self.name == "mean":
                statvalues.append(ds.mean())
                
            elif self.name == "median":
                statvalues.append(ds.median())
                
            elif self.name == "stdev":
                statvalues.append(ds.stdev())
                
            items.extend(ds.len().keys())

        # fill rows
        self.rowdata = []
        for i, item in enumerate(sorted(set(items))):
            row = [item] + [statvalues[i].get(item,0) for i in range(len(statvalues))]
            self.rowdata.append(row)
            self.AppendRow(i, row, self.statctrl)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.statctrl, 1, flag=wx.ALL | wx.EXPAND, border=5)
        self.sizer.FitInside(self)
        self.SendSizeEvent()

# ----------------------------------------------------------------------------


def ShowStatsDialog(parent, preferences, tiers):
    dialog = DescriptivesStatsDialog(parent, preferences, tiers)
    dialog.ShowModal()
    dialog.Destroy()

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app = wx.PySimpleApp()
    ShowStatsDialog(None, None, tiers={})
    app.MainLoop()
