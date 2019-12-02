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

    src.wxgui.cliens.dataroamerclient.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    GUI management of annotated data.

"""
import os.path
import wx
import wx.lib.scrolledpanel as scrolled

from sppas.src.ui.wxgui.sp_icons import TIER_RENAME
from sppas.src.ui.wxgui.sp_icons import TIER_DELETE
from sppas.src.ui.wxgui.sp_icons import TIER_CUT
from sppas.src.ui.wxgui.sp_icons import TIER_COPY
from sppas.src.ui.wxgui.sp_icons import TIER_PASTE
from sppas.src.ui.wxgui.sp_icons import TIER_DUPLICATE
from sppas.src.ui.wxgui.sp_icons import TIER_MOVE_UP
from sppas.src.ui.wxgui.sp_icons import TIER_MOVE_DOWN
from sppas.src.ui.wxgui.sp_icons import TIER_PREVIEW
from sppas.src.ui.wxgui.sp_icons import TIER_RADIUS

from sppas.src.ui.wxgui.ui.CustomEvents import FileWanderEvent, spEVT_FILE_WANDER
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_PANEL_SELECTED
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_SETTINGS

from sppas.src.ui.wxgui.panels.trslist import TrsList
from sppas.src.ui.wxgui.panels.mainbuttons import MainToolbarPanel
from sppas.src.ui.wxgui.structs.files import xFiles
import sppas.src.ui.wxgui.dialogs.filedialogs as filedialogs
from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation
from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowYesNoQuestion

from .baseclient import BaseClient

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

RENAME_ID = wx.NewId()
DUPLICATE_ID = wx.NewId()
PREVIEW_ID = wx.NewId()
TIER_RADIUS_ID = wx.NewId()

# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------


class DataRoamerClient(BaseClient):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Manage the opened files.

    This class manages the pages of a notebook with all opened files.
    Each page (except if empty...) contains an instance of a DataRoamer.

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
        return DataRoamer(parent, prefsIO)

    # ------------------------------------------------------------------------

    def New(self):
        """Add a new file into the current page."""
        
        # Ask for the new file name
        filename = filedialogs.SaveAsAnnotationFile()
        if filename is None:
            return
        
        # Add the newly created file in the file manager and that's it!
        evt = FileWanderEvent(filename=filename, status=False)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetTopLevelParent(), evt)

    # ------------------------------------------------------------------------

    def Save(self):
        """Save the current file(s)."""
        
        page = self._notebook.GetCurrentPage()
        for i in range(self._xfiles.GetSize()):
            if self._xfiles.GetOther(i) == page:
                o = self._xfiles.GetObject(i)
                o.Save()

    # ------------------------------------------------------------------------

    def SaveAs(self):
        """Save the current file(s)."""
        
        page = self._notebook.GetCurrentPage()
        for i in range(self._xfiles.GetSize()):
            if self._xfiles.GetOther(i) == page:
                o = self._xfiles.GetObject(i)
                o.SaveAs()

    # ------------------------------------------------------------------------

    def SaveAll(self):
        """Save all files of a page."""
        
        for i in range(self._xfiles.GetSize()):
            o = self._xfiles.GetObject(i)
            # save even if the file is not selected
            o.SaveAll(selected=False)

# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------


class DataRoamer(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      This component allows to manage annotated files.

    """
    def __init__(self, parent, prefsIO):
        wx.Panel.__init__(self, parent, -1)

        # members
        self._filetrs = xFiles()  # Associate files/trsdata
        self._selection = None    # the index of the selected trsdata panel
        self._clipboard = None    # Used to cut and paste
        self._prefsIO = prefsIO

        # create the client panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = self._create_toolbar()
        sizer.Add(toolbar, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)
        self._trspanel = self._create_content()
        sizer.Add(self._trspanel, proportion=2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=4)

        # Bind events
        self._trspanel.Bind(spEVT_PANEL_SELECTED, self.OnPanelSelection)
        self.Bind(spEVT_FILE_WANDER, self.OnFileWander)
        self.Bind(spEVT_SETTINGS, self.OnSettings)
        self.Bind(wx.EVT_BUTTON, self.ProcessEvent)

        self.SetBackgroundColour(prefsIO.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(prefsIO.GetValue('M_FG_COLOUR'))
        self.SetFont(prefsIO.GetValue('M_FONT'))

        self.SetSizer(sizer)
        self.Layout()

    # ----------------------------------------------------------------------

    def _create_toolbar(self):
        """Creates a toolbar panel."""

        toolbar = MainToolbarPanel(self, self._prefsIO)

        toolbar.AddButton(RENAME_ID,
                          TIER_RENAME,
                          'Rename',
                          tooltip="Rename the selected tier.")

        toolbar.AddButton(wx.ID_DELETE,
                          TIER_DELETE,
                          'Delete',
                          tooltip="Delete the selected tier.")

        toolbar.AddButton(wx.ID_CUT,
                          TIER_CUT,
                          'Cut',
                          tooltip="Cut the selected tier.")

        toolbar.AddButton(wx.ID_COPY,
                          TIER_COPY,
                          "Copy",
                          tooltip="Copy the selected tier.")

        toolbar.AddButton(wx.ID_PASTE,
                          TIER_PASTE,
                          "Paste",
                          tooltip="Paste the selected tier.")

        toolbar.AddButton(DUPLICATE_ID,
                          TIER_DUPLICATE,
                          "Duplicate",
                          tooltip="Duplicate the selected tier.")

        toolbar.AddButton(wx.ID_UP,
                          TIER_MOVE_UP,
                          "Move Up",
                          tooltip="Move up the selected tier.")

        toolbar.AddButton(wx.ID_DOWN,
                          TIER_MOVE_DOWN,
                          "Move Down",
                          tooltip="Move down the selected tier.")

        toolbar.AddButton(TIER_RADIUS_ID,
                          TIER_RADIUS,
                          "Radius",
                          tooltip="Fix the vagueness of each boundary. "
                                  "Useful only for .xra file format.")

        toolbar.AddButton(PREVIEW_ID,
                          TIER_PREVIEW,
                          "View",
                          tooltip="Preview of the selected tier.")

        return toolbar

    # ----------------------------------------------------------------------

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
        """Processes an event.

        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s). Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.

        :param event: (wx.Event)

        """
        ide = event.GetId()

        if ide == RENAME_ID:
            self.Rename()
            return True
        elif ide == wx.ID_DELETE:
            self.Delete()
            return True
        elif ide == wx.ID_CUT:
            self.Cut()
            return True
        elif ide == wx.ID_COPY:
            self.Copy()
            return True
        elif ide == wx.ID_PASTE:
            self.Paste()
            return True
        elif ide == DUPLICATE_ID:
            self.Duplicate()
            return True
        elif ide == wx.ID_UP:
            self.MoveUp()
            return True
        elif ide == wx.ID_DOWN:
            self.MoveDown()
            return True
        elif ide == PREVIEW_ID:
            self.Preview()
            return True
        elif ide == TIER_RADIUS_ID:
            self.Radius()
            return True

        return wx.GetApp().ProcessEvent(event)

    # ----------------------------------------------------------------------
    # Callbacks
    # ----------------------------------------------------------------------

    def OnFileWander(self, event):
        """A file was checked/unchecked somewhere else, then set/unset the data.

        :param event: (wx.Event)

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
                self.UnsetData(f)
                evt = FileWanderEvent(filename=f, status=False)
                evt.SetEventObject(self)
                wx.PostEvent(self.GetParent().GetParent().GetParent(), evt)

    # ------------------------------------------------------------------------

    def OnPanelSelection(self, event):
        """Change the current selection (the transcription file that was clicked on)."""

        sel = event.panel

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p != sel:
                p.Deselect()
                p.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
            else:
                # set the new selection
                self._selection = p
                p.SetBackgroundColour(wx.Colour(215, 215, 240))

    # -----------------------------------------------------------------------
    # Functions on a tier...
    # -----------------------------------------------------------------------

    def Rename(self):
        """Rename a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Rename()

    # -----------------------------------------------------------------------

    def Delete(self):
        """Delete a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Delete()

    # -----------------------------------------------------------------------

    def Cut(self):
        """Cut a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                self._clipboard = p.Cut()

    # -----------------------------------------------------------------------

    def Copy(self):
        """Copy a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                self._clipboard = p.Copy()

    # -----------------------------------------------------------------------

    def Paste(self):
        """Paste a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Paste(self._clipboard)

    # -----------------------------------------------------------------------

    def Duplicate(self):
        """Duplicate a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Duplicate()

    # -----------------------------------------------------------------------

    def MoveUp(self):
        """Move up a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.MoveUp()

    # -----------------------------------------------------------------------

    def MoveDown(self):
        """Move down a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.MoveDown()

    # -----------------------------------------------------------------------

    def Preview(self):
        """Open a frame to view a tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Preview()

    # -----------------------------------------------------------------------

    def Radius(self):
        """Change radius value of all TimePoint instances of the tier."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                p.Radius()

    # ----------------------------------------------------------------------
    # Functions on a file...
    # ----------------------------------------------------------------------

    def Save(self, selected=True):
        """Save the selected file."""

        if self._selection is None:
            ShowInformation(self,
                            self._prefsIO,
                            "No file selected!\n"
                            "Click on a tier to select a file...",
                            style=wx.ICON_INFORMATION)
            return

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if (selected is True and p == self._selection) or selected is False:
                p.Save()

    # ----------------------------------------------------------------------

    def SaveAs(self):
        """Save as... the selected file."""

        if self._selection is None:
            ShowInformation(self,
                            self._prefsIO,
                            "No file selected!\n"
                            "Click on a tier to select a file...",
                            style=wx.ICON_INFORMATION)
            return

        found = -1
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            if p == self._selection:
                found = i
                break

        if found > -1:
            f = self._filetrs.GetFilename(i)
            p = self._filetrs.GetObject(i)

            # Ask for the new file name
            filename = filedialogs.SaveAsAnnotationFile()

            if filename is None:
                return

            # do not erase the file if it is already existing!
            if os.path.exists(filename) and f != filename:
                ShowInformation(self,
                                self._prefsIO,
                                "File not saved: this file name is already existing!",
                                style=wx.ICON_INFORMATION)
            elif f == filename:
                p.Save()
            else:
                p.SaveAs(filename)
                # Add the newly created file in the file manager
                evt = FileWanderEvent(filename=filename, status=True)
                evt.SetEventObject(self)
                wx.PostEvent(self.GetTopLevelParent(), evt)

                evt = FileWanderEvent(filename=filename, status=True)
                evt.SetEventObject(self)
                wx.PostEvent(self.GetParent().GetParent().GetParent(), evt)

    # ----------------------------------------------------------------------

    def SaveAll(self):
        """Save all files."""

        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.Save()

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

        wx.Window.SetFont(self, font)
        # Apply to all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetFont(font)

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """Change background of all texts."""

        wx.Window.SetBackgroundColour(self,color)
        # Apply as background on all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetBackgroundColour(color)

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """Change foreground of all texts."""

        wx.Window.SetForegroundColour(self, color)
        # Apply as foreground on all panels
        for i in range(self._filetrs.GetSize()):
            p = self._filetrs.GetObject(i)
            p.SetForegroundColour(color)

    # ----------------------------------------------------------------------
    # Manage the data
    # ----------------------------------------------------------------------

    def SetData(self, filename):
        """Add a file."""

        # Do not add an already loaded file
        if self._filetrs.Exists(filename):
            return False

        # create the object
        new_trs = TrsList(self._trspanel, filename)
        new_trs.SetPreferences(self._prefsIO)
        if new_trs.GetTranscriptionName() == "IO-Error":
            ShowInformation(self,
                            self._prefsIO,
                            'Error loading: '+filename,
                            style=wx.ICON_ERROR)

        # put the new trs in a sizer (required to enable sizer.Remove())
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(new_trs, proportion=1, flag=wx.EXPAND, border=0)
        self._trssizer.Add(s, proportion=1, flag=wx.EXPAND | wx.TOP, border=4)

        # add in the list of files
        self._filetrs.Append(filename, new_trs)

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
                userChoice = ShowYesNoQuestion(None, self._prefsIO,
                                               "Do you want to save changes on the transcription of\n%s?" % f)
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

    # ----------------------------------------------------------------------

    def GetSelection(self):
        """Return the current selection (the panel TrsList witch is selected)."""

        return self._selection

# ----------------------------------------------------------------------------
