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

    src.ui.phoenix.views.statsview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import codecs

from sppas.src.config import paths
from sppas.src.config import msg
from sppas.src.utils import u
from sppas.src.anndata import sppasRW
from sppas.src.analysis.tierstats import sppasTierStats

from src.ui.phoenix.windows import Confirm
from src.ui.phoenix.windows import sppasFileDialog
from src.ui.phoenix.windows import sppasDialog
from src.ui.phoenix.windows import sppasPanel
from src.ui.phoenix.windows import sppasRadioBoxPanel
from src.ui.phoenix.windows.book import sppasNotebook
from src.ui.phoenix.windows.listctrl import SortListCtrl
from src.ui.phoenix.windows import sppasComboBox

# --------------------------------------------------------------------------


MSG_HEADER_STATSVIEW = u(msg("View descriptive stats of tiers", "ui"))
OPT_TAG_BEST = u(msg("Use only the tag with the best score", "ui"))
OPT_TAG_ALT = u(msg("Use alternative tags", "ui"))
OPT_TAGS = u(msg("Annotation label tags: ", "ui"))
OPT_MIDPOINT_ONLY = u(msg("Use only midpoint value", "ui"))
OPT_MIDPOINT_RADD = u(msg("Add the radius value", "ui"))
OPT_MIDPOINT_RDEL = u(msg("Deduct the radius value", "ui"))
OPT_DUR = u(msg("Annotation durations: ", "ui"))
MSG_CONFIRM_OVERRIDE = \
    u(msg("A file with name {:s} is already existing. Override it?", "ui"))
MSG_CONFIRM_NAME = u(msg("Confirm file name?", "ui"))
MSG_ACT_SAVE = u(msg("Save", "ui"))
MSS_SELECTED = u(msg("Selected statistical distribution: {:s}", "ui"))

# --------------------------------------------------------------------------


def writecsv(filename, rows, separator="\t", encoding="utf-8-sig"):
    """Write the rows to the file.

    :param filename: (str)
    :param rows: (list)
    :param separator: (str):
    :param encoding: (str):

    """
    with codecs.open(filename, "w+", encoding) as f:
        for row in rows:
            tmp = []
            for s in row:
                if isinstance(s, (float, int)):
                    s = str(s)
                else:
                    s = '"%s"' % s
                tmp.append(s)
            f.write('%s\n' % separator.join(tmp))

# --------------------------------------------------------------------------


class sppasStatsViewDialog(sppasDialog):
    """Display descriptive statistics of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Dialog for the user to display and save various descriptive statistics
    of a set of tiers.

    """

    def __init__(self, parent, tiers=None):
        """Create a dialog to display statistics.

        :param parent: (wx.Window) the parent wx object.
        :param tiers: dictionary with key=filename, value=list of selected tiers

        """
        super(sppasStatsViewDialog, self).__init__(
            parent,
            title="Stats View",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="statsview-dialog")

        # Members to evaluate stats
        if tiers is None:
            tiers = dict()
        self.ngram = 1        # n range 1..8
        self.withradius = 0   # -1, 0 or 1
        self.withalt = False
        self._data = dict()   # key=filename, value=list of sppasTier
        self.load_data(tiers)

        self.CreateHeader(MSG_HEADER_STATSVIEW, "tier_stat_view")
        self._create_content()
        self.CreateActions([wx.ID_SAVE], [wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_button_clicked)

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn()

    # -----------------------------------------------------------------------

    def load_data(self, tiers):
        """Convert tiers into sppasTiersStats.

        :param tiers: dictionary with key=filename, value=list of selected tiers

        """
        if tiers is None or len(tiers) == 0:
            return
        for k, v in tiers.items():
            # k = filename, v = list of tiers
            for tier in v:
                ts = sppasTierStats(tier, self.ngram, self.withradius, self.withalt)
                self._data[ts] = k
                # remark: statistics are not estimated yet.
                # ts contains a pointer to the tier; ts.tier

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_toolbar(self, parent):
        """Create a panel to fix options."""
        panel = sppasPanel(parent)

        ngram_text = wx.StaticText(panel, label=" N-gram:  ")
        nrange = [str(i) for i in range(1, 6)]
        ngrambox = wx.ComboBox(panel, -1, choices=nrange, style=wx.CB_READONLY)
        ngrambox.SetSelection(0)
        sizern = wx.BoxSizer(wx.HORIZONTAL)
        sizern.Add(ngram_text, 0, wx.ALIGN_CENTER_VERTICAL)
        sizern.Add(ngrambox, 0, wx.ALIGN_CENTER_VERTICAL)

        alt_text = wx.StaticText(panel, label=OPT_TAGS)
        withaltbox = sppasRadioBoxPanel(
            panel,
            choices=[OPT_TAG_BEST, OPT_TAG_ALT],
            majorDimension=0)
        sizera = wx.BoxSizer(wx.VERTICAL)
        sizera.Add(alt_text, 0, wx.ALIGN_LEFT)
        sizera.Add(withaltbox, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT | wx.TOP, sppasPanel.fix_size(6))

        radius_text = wx.StaticText(panel, label=OPT_DUR)
        withradiusbox = sppasRadioBoxPanel(
            panel,
            choices=[OPT_MIDPOINT_ONLY, OPT_MIDPOINT_RADD, OPT_MIDPOINT_RDEL],
            majorDimension=0)
        sizerr = wx.BoxSizer(wx.VERTICAL)
        sizerr.Add(radius_text, 0, wx.ALIGN_LEFT)
        sizerr.Add(withradiusbox, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT | wx.TOP, sppasPanel.fix_size(6))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizern, 2, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, border=sppasPanel.fix_size(8))
        sizer.AddSpacer(1)
        sizer.Add(sizera, 2, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, border=sppasPanel.fix_size(8))
        sizer.AddSpacer(1)
        sizer.Add(sizerr, 2, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(8))
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_COMBOBOX, self._process_ngram, ngrambox)
        self.Bind(wx.EVT_RADIOBOX, self._process_alt, withaltbox)
        self.Bind(wx.EVT_RADIOBOX, self._process_radius, withradiusbox)

        return panel

    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog.

        notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, ...) not used because it
        is bugged under MacOS (do not display the page content).

        """
        main_panel = sppasPanel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Propose some options to estimate stats
        tools = self._create_toolbar(main_panel)
        main_sizer.Add(tools, 0, wx.EXPAND)

        # Make the notebook to show each stat
        notebook = sppasNotebook(main_panel, name="stats-notebook")

        # Create and add the pages to the notebook with the label to show on the tab
        page1 = SummaryPanel(notebook,  "summary")
        notebook.AddPage(page1, "   Summary   ")

        page2 = DetailedPanel(notebook, "occurrences")
        notebook.AddPage(page2, " Occurrences ")

        page3 = DetailedPanel(notebook, "total")
        notebook.AddPage(page3, "Total durations")

        page4 = DetailedPanel(notebook, "mean")
        notebook.AddPage(page4, "Mean durations")

        page5 = DetailedPanel(notebook, "median")
        notebook.AddPage(page5, "Median durations")

        page6 = DetailedPanel(notebook, "stdev")
        notebook.AddPage(page6, "Std dev. durations")

        self.__show_stats()

        main_sizer.Add(notebook, 1, wx.EXPAND)

        main_panel.SetSizer(main_sizer)
        main_panel.Layout()
        self.SetContent(main_panel)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _process_button_clicked(self, event):
        evt_object = event.GetEventObject()
        evt_name = evt_object.GetName()

        if evt_name == "save":
            pathname = os.path.dirname(paths.samples)
            for ts in self._data:
                pathname = os.path.dirname(self._data[ts])
                break
            notebook = self.FindWindow("stats-notebook")
            page = notebook.GetPage(notebook.GetSelection())
            filename = os.path.join(pathname, "stats-%s.csv" % page.GetName())
            wx.LogDebug("Default output filename {:s}".format(filename))
            page.SaveAs(outfilename=filename)

        event.Skip()

    # ------------------------------------------------------------------------

    def _process_ngram(self, event):
        wx.LogDebug("Process ngram")
        # get new n value of the N-gram
        self.ngram = int(event.GetEventObject().GetSelection() + 1)

        # update infos of TierStats objects
        for ts in self._data:
            ts.set_ngram(self.ngram)

        self.__show_stats()

    # ------------------------------------------------------------------------

    def _process_alt(self, event):
        obj = event.GetEventObject()
        new_value = bool(obj.GetSelection())
        wx.LogDebug("Old value = {:s}".format(str(self.withalt)))
        wx.LogDebug("New value = {:s}".format(str(new_value)))
        if self.withalt == new_value:
            return
        self.withalt = new_value

        # update infos of TierStats objects
        for ts in self._data:
            ts.set_withalt(self.withalt)

        self.__show_stats()

    # ------------------------------------------------------------------------

    def _process_radius(self, event):
        obj = event.GetEventObject()

        if obj.GetSelection() == 0:
            if self.withradius != 0:
                self.withradius = 0
            else:
                return

        elif obj.GetSelection() == 1:
            if self.withradius != -1:
                self.withradius = -1
            else:
                return

        elif obj.GetSelection() == 2:
            if self.withradius != 1:
                self.withradius = 1
            else:
                return

        # update infos of TierStats objects
        for ts in self._data:
            ts.set_with_radius(self.withradius)

        self.__show_stats()

    # ------------------------------------------------------------------------

    def __show_stats(self):
        notebook = self.FindWindow("stats-notebook")
        for i in range(notebook.GetPageCount()):
            page = notebook.GetPage(i)
            page.ShowStats(self._data)
        self.Refresh()

# ----------------------------------------------------------------------------
# Base Stat Panel
# ----------------------------------------------------------------------------


class BaseStatPanel(sppasPanel):
    """Base class to display stats of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name):
        super(BaseStatPanel, self).__init__(parent, name=name)

        self.rowdata = []
        self.cols = ('',)
        self.statctrl = SortListCtrl(
            self,
            style=wx.NO_BORDER | wx.LC_REPORT | wx.LC_VRULES,
            size=(-1, sppasPanel.fix_size(400)))

        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(self, label=MSS_SELECTED.format(self.GetName()))
        sizer.Add(text, 0, flag=wx.ALL | wx.EXPAND, border=2)
        sizer.Add(self.statctrl, 1, flag=wx.ALL | wx.EXPAND, border=2)
        self.SetSizer(sizer)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(420),
                                sppasPanel.fix_size(320)))
        self.Layout()

    # ------------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        sppasPanel.SetBackgroundColour(self, colour)
        self.statctrl.RecolorizeBackground()

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """Base method to show stats of a tier in the panel.

        :param data: Dictionary of stats

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def SaveAs(self, outfilename="stats.csv"):
        with sppasFileDialog(self,
                             title=MSG_ACT_SAVE,
                             style=wx.FD_SAVE,  # | wx.FD_OVERWRITE_PROMPT,
                             ) as dlg:
            if wx.Platform == "__WXMSW__":
                dlg.SetWildcard("UTF-16 (*.csv)|*.csv |UTF-8 (*.csv)|*.csv")
            else:
                dlg.SetWildcard("UTF-8 (*.csv)|*.csv |UTF-16 (*.csv)|*.csv")

            dlg.SetPath(outfilename)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            pathname = dlg.GetPath()
            if len(pathname) == 0:
                return
            index = dlg.GetFilterIndex()
            if pathname.lower().endswith(".csv") is False:
                pathname += ".csv"

        if os.path.exists(pathname):
            message = MSG_CONFIRM_OVERRIDE.format(pathname)
            response = Confirm(message, MSG_CONFIRM_NAME)
            if response == wx.ID_CANCEL:
                return

        if wx.Platform == "__WXMSW__":
            encoding = "utf-16" if index == 0 else "utf-8"
        else:
            encoding = "utf-8" if index == 0 else "utf-16"

        self.rowdata.insert(0, self.cols)
        writecsv(pathname, self.rowdata, separator=";", encoding=encoding)
        self.rowdata.pop(0)
        wx.LogMessage("File {:s} saved in {:s} encoding"
                      "".format(pathname, encoding))

    # ------------------------------------------------------------------------

    def AppendRow(self, i, row):
        # append the row in the list
        pos = self.statctrl.InsertItem(i, row[0])
        for j in range(1, len(row)):
            s = row[j]
            if isinstance(s, float):
                s = str(round(s, 4))
            elif isinstance(s, int):
                s = str(s)
            self.statctrl.SetItem(pos, j, s)

# ----------------------------------------------------------------------------
# First tab: summary
# ----------------------------------------------------------------------------


class SummaryPanel(BaseStatPanel):
    """Summary of descriptive stats of all merged-tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name):
        BaseStatPanel.__init__(self, parent, name)
        self.cols = ("Label",
                     "Occurrences",
                     "Total durations",
                     "Mean durations",
                     "Median durations",
                     "Std dev. durations")

        for i, col in enumerate(self.cols):
            self.statctrl.InsertColumn(i, col)
            self.statctrl.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
        self.statctrl.SetColumnWidth(0, 200)

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """Show descriptive statistics of set of tiers as list.

        """
        wx.LogDebug("Show stats of page {:s}".format(self.GetName()))
        if data is None:
            data = dict()

        # create a TierStats (with durations of all tiers)
        ts = self.__get_ts(data)

        # estimates descriptive statistics
        ds = ts.ds()
        occurrences = ds.len()
        total = ds.total()
        mean = ds.mean()
        median = ds.median()
        stdev = ds.stdev()

        # fill rows
        self.statctrl.DeleteAllItems()
        self.rowdata = []
        for i, key in enumerate(occurrences.keys()):
            row = [key, occurrences[key], total[key], mean[key], median[key], stdev[key]]
            # add the data content in rowdata
            self.rowdata.append(row)
            # add into the listctrl
            self.AppendRow(i, row)

        self.statctrl.Refresh()
        self.Layout()

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

    """

    def __init__(self, parent, name):
        super(DetailedPanel, self).__init__(parent, name)
        self.cols = ("Tags",)

    # ------------------------------------------------------------------------

    def ShowStats(self, data):
        """Show descriptive statistics of set of tiers as list.

        The columns of the list are re-created: one column is one file of data.

        :param data: (dict) Dictionary with key=TierStats and value=filename

        """
        wx.LogDebug("Show stats of page {:s}".format(self.GetName()))
        if data is None:
            data = dict()

        # re-create columns
        self.statctrl.DeleteAllColumns()
        self.cols = ("Tags",) + tuple(
            os.path.basename(v) + ":" + ts.get_tier().get_name() for ts, v in
            data.items())
        for i, col in enumerate(self.cols):
            self.statctrl.InsertColumn(i, col)
            self.statctrl.SetColumnWidth(i, 120)
        self.statctrl.SetColumnWidth(0, 200)

        # estimates descriptive statistics
        name = self.GetName()
        statvalues = []
        items = []  # the list of labels
        for ts in data.keys():
            ds = ts.ds()
            if name == "occurrences":
                statvalues.append(ds.len())

            elif name == "total":
                statvalues.append(ds.total())

            elif name == "mean":
                statvalues.append(ds.mean())

            elif name == "median":
                statvalues.append(ds.median())

            elif name == "stdev":
                statvalues.append(ds.stdev())

            items.extend(ds.len().keys())

        # fill rows
        self.rowdata = []
        for i, item in enumerate(sorted(set(items))):
            row = [item] + [statvalues[i].get(item, 0) for i in
                            range(len(statvalues))]
            self.rowdata.append(row)
            self.AppendRow(i, row)

        self.statctrl.Refresh()
        self.Layout()

# ----------------------------------------------------------------------------
# Panel that can be tested
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super(TestPanel, self).__init__(parent, pos=pos, size=size,
                                        name="TestPanel StatsView")
        s = wx.BoxSizer()
        b = wx.Button(self, label="Stats View", name="stats-btn")
        s.Add(b, 1, wx.EXPAND)
        self.SetSizer(s)
        self.Bind(wx.EVT_BUTTON, self._open_stats)

    def _open_stats(self, evt):
        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra",
                          "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra",
                          "F_F_B003-P9-palign.xra")
        parser = sppasRW(f1)
        trs1 = parser.read()
        parser = sppasRW(f2)
        trs2 = parser.read()
        tier1 = trs1.find("PhonAlign")
        tier2 = trs2.find("PhonAlign")

        dialog = sppasStatsViewDialog(self, tiers={f1: [tier1], f2: [tier2]})
        dialog.ShowModal()
        dialog.DestroyFadeOut()
