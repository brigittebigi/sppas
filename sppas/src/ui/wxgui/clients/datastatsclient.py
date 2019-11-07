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

    src.wxgui.clients.datastatsclient.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    GUI statistics system of annotated data.

"""

import wx
import wx.lib.scrolledpanel as scrolled

from sppas.src.ui.wxgui.sp_icons import SPREADSHEETS
from sppas.src.ui.wxgui.sp_icons import FILTER_CHECK
from sppas.src.ui.wxgui.sp_icons import FILTER_UNCHECK
from sppas.src.ui.wxgui.sp_icons import TIER_PREVIEW

from sppas.src.ui.wxgui.ui.CustomEvents import FileWanderEvent, spEVT_FILE_WANDER
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_PANEL_SELECTED
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_SETTINGS

from sppas.src.ui.wxgui.structs.files import xFiles

from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation
from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowYesNoQuestion

from sppas.src.ui.wxgui.panels.trslist import TrsList
from sppas.src.ui.wxgui.panels.mainbuttons import MainToolbarPanel
from sppas.src.ui.wxgui.views.descriptivestats import DescriptivesStatsDialog

from .baseclient import BaseClient


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

FILTER_CHECK_ID = wx.NewId()
FILTER_UNCHECK_ID = wx.NewId()
DESCRIPTIVES_ID = wx.NewId()
PREVIEW_ID = wx.NewId()


# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------


class DataStatsClient(BaseClient):
    """

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      This class is used to manage the opened files.

    This class manages the pages of a notebook with all opened files.
    Each page (except if empty...) contains an instance of a Statistics panel.

    """
    def __init__(self, parent, prefsIO):
        BaseClient.__init__(self, parent, prefsIO)
        self._update_members()

    # ------------------------------------------------------------------------

    def _update_members(self):
        """Update members."""

        self._multiplefiles = True

        # Quick and dirty solution to communicate to the file manager:
        self._prefsIO.SetValue('F_CCB_MULTIPLE', t='bool', v=True, text='')

    # ------------------------------------------------------------------------

    def CreateComponent(self, parent, prefsIO):
        return DataStats(parent, prefsIO)

# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------


class DataStats(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Estimates statistics on annotated files.

    """
    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent, -1)

        # members
        self._filetrs = xFiles()  # Associate files/trsdata
        self._selection = None    # the index of the selected trsdata panel
        self._prefsIO = prefsIO
        self.SetBackgroundColour(prefsIO.GetValue('M_BG_COLOUR'))

        # create the client panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = self._create_toolbar()
        sizer.Add(toolbar, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)
        self._trspanel = self._create_content()
        sizer.Add(self._trspanel, proportion=2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)

        # Bind events
        self.Bind(spEVT_PANEL_SELECTED, self.OnPanelSelection)
        self.Bind(spEVT_FILE_WANDER,    self.OnFileWander)
        self.Bind(spEVT_SETTINGS,       self.OnSettings)
        self.Bind(wx.EVT_BUTTON,        self.ProcessEvent)

        self.SetSizer(sizer)
        self.Layout()

    # ----------------------------------------------------------------------

    def _create_toolbar(self):
        """Creates a toolbar panel."""

        toolbar = MainToolbarPanel(self, self._prefsIO)

        toolbar.AddButton(FILTER_CHECK_ID, FILTER_CHECK, 'Check', tooltip="Choose the tier(s) to check.")
        toolbar.AddButton(FILTER_UNCHECK_ID, FILTER_UNCHECK, 'Uncheck', tooltip="Uncheck all the tier(s) of the page.")
        toolbar.AddButton(PREVIEW_ID, TIER_PREVIEW, 'View', tooltip="Preview one checked tier of the selected file.")
        toolbar.AddSpacer()
        toolbar.AddButton(DESCRIPTIVES_ID, SPREADSHEETS, 'Statistics', tooltip="Estimates descriptive statistics of checked tier(s).")
        toolbar.AddSpacer()

        return toolbar

    # -------------------------------------------------------------------------

    def _create_content(self):
        """Create the panel with files content."""

        panel = scrolled.ScrolledPanel(self, -1)
        self._trssizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizerAndFit(self._trssizer)
        panel.SetAutoLayout(True)
        panel.SetupScrolling()
        return panel

    # ------------------------------------------------------------------------
    # Callbacks to any kind of event
    # ------------------------------------------------------------------------

    def ProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.
        """
        id = event.GetId()

        if id == FILTER_CHECK_ID:
            self.Check()
            return True
        elif id == FILTER_UNCHECK_ID:
            self.Uncheck()
            return True
        elif id == PREVIEW_ID:
            self.Preview()
            return True

        elif id == DESCRIPTIVES_ID:
            self.DescriptivesStats()
            return True

        return wx.GetApp().ProcessEvent(event)

    # ------------------------------------------------------------------------
    # Callbacks to any kind of event
    # ------------------------------------------------------------------------

    def OnFileWander(self, event):
        """
        A file was checked/unchecked somewhere else, then, set/unset the data.

        """
        f = event.filename
        s = event.status

        if s is True:
            r = self.SetData(f)
            if r is False:
                evt = FileWanderEvent(filename=f, status=False)
                evt.SetEventObject(self)
                wx.PostEvent(self.GetParent().GetParent().GetParent(), evt)

        else:
            if f is None:
                self.UnsetAllData()

            else:
                try:
                    self.UnsetData(f)
                    evt = FileWanderEvent(filename=f, status=False)
                    evt.SetEventObject(self)
                    wx.PostEvent(self.GetParent().GetParent().GetParent(), evt)
                except Exception:
                    pass

    # ------------------------------------------------------------------------

    def OnPanelSelection(self, event):
        """Change the current selection (the transcription file that was clicked on)."""
        self._selection = event.panel
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.SetBackgroundColour(wx.Colour(245,235,210))
            else:
                p.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))

    # -----------------------------------------------------------------------
    # Actions on tiers...
    # -----------------------------------------------------------------------

    def Check(self):
        """Choose tiers to check."""

        nb = 0
        dlg = wx.TextEntryDialog(self, 'What is the name of tier(s) to check?', 'Tier checker', '')
        case_sensitive = False  # TODO: add a check button in the entry dialog
        ret = dlg.ShowModal()

        # Let's check if user clicked OK or pressed ENTER
        if ret == wx.ID_OK:
            tiername = dlg.GetValue()
            for i in range(self._filetrs.GetSize()):
                p = self._filetrs.GetObject(i)
                r = p.Select(tiername, case_sensitive)
                if r:
                    nb += 1
        dlg.Destroy()

    # -----------------------------------------------------------------------

    def Uncheck(self):
        """Un-check all tiers in all files."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.Deselect()

    # -----------------------------------------------------------------------

    def Preview(self):
        """Open a frame to view a tier."""

        # Show the tier which is checked in the selected files
        nb = self._get_nbselectedtiers(inselection=True)
        if nb == 1:
            self._selection.Preview()
        else:
            # show the tier which is checked... even if it's not in a selected file
            nb = self._get_nbselectedtiers(inselection=False)
            if nb == 0:
                ShowInformation(self, self._prefsIO, "One tier must be checked.", wx.ICON_INFORMATION)
            elif nb == 1:
                for i in range(self._filetrs.GetSize()):
                    p = self._filetrs.GetObject(i)
                    if p.tier_list.GetSelectedItemCount()==1:
                        p.Preview()
            else:
                ShowInformation(self, self._prefsIO, "Only one tier must be checked.", wx.ICON_INFORMATION)

    # ----------------------------------------------------------------------

    def DescriptivesStats(self):
        """Descriptives Statistics ."""
        
        nb = self._get_nbselectedtiers(inselection=False)
        if nb > 0:
            dlg = DescriptivesStatsDialog(self, self._prefsIO, self._get_selectedtiers())
            dlg.ShowModal()
            dlg.Destroy()
        else:
            ShowInformation(self, self._prefsIO, "At least one tier must be checked!", wx.ICON_INFORMATION)

    # ----------------------------------------------------------------------
    # GUI
    # ----------------------------------------------------------------------

    def OnSettings(self, event):
        """Set new preferences, then apply them."""

        self._prefsIO = event.prefsIO

        # Apply the changes on self
        self.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        self.SetFont(self._prefsIO.GetValue('M_FONT'))

        for i in range(self._filetrs.GetSize()):
            obj = self._filetrs.GetObject(i)
            obj.SetPreferences(self._prefsIO)

        self.Layout()
        self.Refresh()

    # ----------------------------------------------------------------------

    def SetFont(self, font):
        """Change font of all texts."""

        wx.Window.SetFont(self,font)
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetFont(font)

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """Change background of all texts."""

        wx.Window.SetBackgroundColour(self,color)
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetBackgroundColour(color)

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """Change foreground of all texts."""

        wx.Window.SetForegroundColour(self,color)
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetForegroundColour(color)

    # ----------------------------------------------------------------------
    # Manage the data
    # ----------------------------------------------------------------------

    def SetData(self, filename):
        """Add a file."""

        # Do not add an existing file
        if self._filetrs.Exists(filename):
            return False

        # create the object
        new_trs = TrsList(self._trspanel, filename, multiple=self._prefsIO.GetValue('F_CCB_MULTIPLE'))
        new_trs.SetPreferences(self._prefsIO)
        new_trs.Protect()
        if new_trs.GetTranscriptionName() == "IO-Error":
            ShowInformation(self, 
                            self._prefsIO, 
                            'Error loading: '+filename, 
                            style=wx.ICON_ERROR)

        # put the new trs in a sizer (required to enable sizer.Remove())
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(new_trs, 1, wx.EXPAND)
        self._trssizer.Add(s, proportion=1, flag=wx.EXPAND|wx.TOP, border=4)
        
        # add in the list of files
        self._filetrs.Append(filename,new_trs)

        self.Layout()
        self._trspanel.Refresh()

        return True

    # ----------------------------------------------------------------------

    def UnsetData(self, f):
        """Remove the given file."""

        if self._filetrs.Exists(f):
            i = self._filetrs.GetIndex(f)
            o = self._filetrs.GetObject(i)

            if o._dirty is True:
                # dlg to ask to save or not
                userChoice = ShowYesNoQuestion(None, self._prefsIO, "Do you want to save changes of the file %s?" % f)
                if userChoice == wx.ID_YES:
                    o.Save()

            o.Destroy()
            self._filetrs.Remove(i)
            self._trssizer.Remove(i)

        self.Layout()
        self.Refresh()

    # ----------------------------------------------------------------------

    def UnsetAllData(self):
        """Clean information and destroy all data."""

        self._filetrs.RemoveAll()
        self._trssizer.DeleteWindows()

        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _get_tiernames(self):
        """Create a list of selected tier names, and the whole list of tier names."""

        tiersX = []
        tiersY = []

        for i in range(self._filetrs.GetSize()):
            obj = self._filetrs.GetObject(i)
            trs = obj.GetTranscription()
            for tier in trs:
                name = tier.get_name()
                if obj.IsSelected(name):
                    if name not in tiersX:
                        tiersX.append(name)
                if name not in tiersY:
                    tiersY.append(name)

        return sorted(tiersX), sorted(tiersY)

    # -----------------------------------------------------------------------

    def _get_selectedtiers(self):
        """Create a list of selected tiers for each file."""

        data = {}
        for i in range(self._filetrs.GetSize()):
            fname = self._filetrs.GetFilename(i)
            # obj is a TrsList instance
            obj = self._filetrs.GetObject(i)
            trs = obj.GetTranscription()
            for tier in trs:
                if obj.IsSelected(tier.get_name()):
                    if fname not in data.keys():
                        data[fname] = []
                    data[fname].append(tier)
        return data

    # -----------------------------------------------------------------------

    def _get_nbselectedtiers(self, inselection=False):
        """Get the number of selected tiers."""

        nb = 0
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if inselection is False or (inselection is True and p == self._selection):
                nb = nb + p.tier_list.GetSelectedItemCount()
        return nb
