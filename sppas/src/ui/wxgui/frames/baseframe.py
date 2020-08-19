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

    src.wxgui.frames.baseframe.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    GUI base frame for analysis components of SPPAS.

"""
import wx

from sppas.src.ui.wxgui import SETTINGS_FILE

from sppas.src.ui.wxgui.sp_icons import SETTINGS_ICON
from sppas.src.ui.wxgui.sp_icons import COMPONENTS_ICON
from sppas.src.ui.wxgui.sp_icons import ADD_FILE_ICON
from sppas.src.ui.wxgui.sp_icons import REMOVE_ICON
from sppas.src.ui.wxgui.sp_icons import TAB_NEW_ICON
from sppas.src.ui.wxgui.sp_icons import TAB_CLOSE_ICON
from sppas.src.ui.wxgui.sp_icons import ABOUT_ICON
from sppas.src.ui.wxgui.sp_icons import HELP_ICON

from sppas.src.ui.wxgui.sp_consts import DEFAULT_APP_NAME
from sppas.src.ui.wxgui.sp_consts import MIN_PANEL_W, MIN_PANEL_H
from sppas.src.ui.wxgui.sp_consts import MIN_FRAME_W
from sppas.src.ui.wxgui.sp_consts import MIN_FRAME_H
from sppas.src.ui.wxgui.sp_consts import FRAME_STYLE
from sppas.src.ui.wxgui.sp_consts import FRAME_TITLE

from sppas.src.ui.wxgui.ui.CustomEvents import FileWanderEvent, spEVT_FILE_WANDER
from sppas.src.ui.wxgui.ui.CustomEvents import FileCheckEvent
from sppas.src.ui.wxgui.ui.CustomEvents import NotebookNewPageEvent
from sppas.src.ui.wxgui.ui.CustomEvents import NotebookClosePageEvent
from sppas.src.ui.wxgui.ui.CustomEvents import SettingsEvent
from sppas.src.ui.wxgui.ui.splitterpanel import SplitterPanel

from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowYesNoQuestion, ShowInformation
from sppas.src.ui.wxgui.views.about import ShowAboutDialog
from sppas.src.ui.wxgui.views.settings import SettingsDialog

from sppas.src.ui.wxgui.structs.prefs import Preferences_IO

from sppas.src.ui.wxgui.panels.filemanager import FileManager
import sppas.src.ui.wxgui.dialogs.filedialogs as filedialogs

from sppas.src.ui.wxgui.cutils.imageutils import spBitmap
from sppas.src.ui.wxgui.panels.mainbuttons import MainMenuPanel,MainToolbarPanel

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

ID_TB_NEWTAB = wx.NewId()
ID_TB_CLOSETAB = wx.NewId()

# ----------------------------------------------------------------------------


class ComponentFrame(wx.Frame):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Component main frame (base class).

    The Component base main frame. This frames is made of:
    
        - a menu
        - a toolbar
        - a panel at left, which is a file manager (with check buttons)
        - a panel at right, which contains the client.

    """
    def __init__(self, parent, idf, args={}):

        wx.Frame.__init__(self, parent, idf, title=FRAME_TITLE+" - Component", style=FRAME_STYLE)

        # Members
        self._init_members(args)

        # Create GUI
        self._init_infos(args)
        self._mainpanel = self._create_content()

        # Events of this frame
        self.Bind(wx.EVT_CLOSE,  self.ProcessEvent)
        self.Bind(wx.EVT_BUTTON, self.ProcessEvent)

        # events sent by the file manager
        spEVT_FILE_WANDER(self, self.OnFileWander)

        self.SetMinSize((MIN_FRAME_W, MIN_FRAME_H))
        (w, h) = wx.GetDisplaySize()
        self.SetSize(wx.Size(w*0.6, h*0.6))
        self.Centre()
        self.Enable()
        self.SetFocus()

        self.Show(True)

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_members(self, args):
        """Sets the members settings with default values."""

        if "prefs" in args.keys():
            self._prefsIO = args["prefs"]
        else:
            # Try to get prefs from a file, or fix default values.
            self._prefsIO = Preferences_IO(SETTINGS_FILE)
            if self._prefsIO.Read() is False:
                self._prefsIO = Preferences_IO(None)

        self._fmtype = "DATAFILES"
        if "type" in args.keys():
            self._fmtype = args['type']
            # expected: "DATAFILES", "SOUNDFILES", "ANYFILES"

    # ------------------------------------------------------------------------

    def _init_infos(self, args):
        """ Set the title and the icon."""

        # Set title
        _app = DEFAULT_APP_NAME
        if "title" in args.keys():
            _app = args["title"]
        self.SetTitle(_app)
        wx.GetApp().SetAppName(_app)

        # Set icon
        _iconname = COMPONENTS_ICON
        if "icon" in args.keys():
            _iconname = args["icon"]

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(spBitmap(_iconname))
        self.SetIcon(_icon)

        # colors
        self.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        self.SetFont(self._prefsIO.GetValue('M_FONT'))

    # ------------------------------------------------------------------------

    def _create_content(self):
        """Organize all sub-anz_panels into a main panel and return it."""

        mainpanel = wx.Panel(self, -1,  style=wx.NO_BORDER)
        mainpanel.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        mainpanel.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        mainpanel.SetFont(self._prefsIO.GetValue('M_FONT'))

        self.menu    = self._create_menu(mainpanel)
        self.toolbar = self._create_toolbar(mainpanel)
        splitpanel   = self._create_splitter(mainpanel)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.toolbar,  proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
        vsizer.Add(splitpanel, proportion=1, flag=wx.ALL|wx.EXPAND, border=0)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.menu, proportion=0, flag=wx.ALL|wx.EXPAND, border=0)
        sizer.Add(vsizer, proportion=2, flag=wx.ALL|wx.EXPAND, border=0)
        mainpanel.SetSizer(sizer)

        return mainpanel

    # ------------------------------------------------------------------------

    def _create_menu(self, parent):
        """Create the default menu and append new items."""

        menu = MainMenuPanel(parent,  self._prefsIO)
        menu.AddSpacer()
        menu.AddButton(wx.ID_PREFERENCES, SETTINGS_ICON)
        menu.AddButton(wx.ID_ABOUT, ABOUT_ICON)
        menu.AddButton(wx.ID_HELP,  HELP_ICON)
        return menu

    # ------------------------------------------------------------------------

    def _create_toolbar(self, parent):
        """Creates the default toolbar."""

        toolbar = MainToolbarPanel(parent, self._prefsIO)
        toolbar.AddButton(wx.ID_ADD, ADD_FILE_ICON, "Add files", tooltip="Add files into the list.")
        toolbar.AddButton(wx.ID_REMOVE, REMOVE_ICON, "Remove", tooltip="Remove files of the list.")
        toolbar.AddButton(ID_TB_NEWTAB, TAB_NEW_ICON, "New tab", tooltip="Open a new page in the notebook.")
        toolbar.AddButton(ID_TB_CLOSETAB, TAB_CLOSE_ICON, "Close tab", tooltip="Close the current page in the notebook.")
        toolbar.AddSpacer()
        return toolbar

    # ------------------------------------------------------------------------

    def _create_splitter(self, parent):
        """Create the main panel content."""

        splitpanel = SplitterPanel(parent, proportion=0.25)
        splitpanel.SetBackgroundColour(self._prefsIO.GetValue('M_BGM_COLOUR'))
        splitpanel.SetForegroundColour(self._prefsIO.GetValue('M_BGM_COLOUR'))

        self._filepanel = self.CreateFileManager(splitpanel, self._prefsIO)
        self._clientpanel = self.CreateClient(splitpanel, self._prefsIO)

        splitpanel.SetMinimumPaneSize(MIN_PANEL_W)
        splitpanel.SplitVertically(self._filepanel, self._clientpanel)

        self._filepanel.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))
        self._clientpanel.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))

        return splitpanel

    # ------------------------------------------------------------------------

    def _LayoutFrame(self):
        """Lays out the frame."""

        wx.LayoutAlgorithm().LayoutFrame(self, self._mainpanel)
        self._clientpanel.SendSizeEvent()
        self.Refresh()

    # ------------------------------------------------------------------------
    # Public method to create the GUI
    # ------------------------------------------------------------------------

    def CreateClient(self, parent, prefsIO):
        """
        Create the client panel and return it.
        Must be overridden.

        :param parent: (wx.Frame)
        :param prefsIO: (Preferences_IO)

        :returns: wx.Panel

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def CreateFileManager(self, parent, prefsIO):
        """
        Create the file manager panel and return it.
        Can be overridden.

        :param parent: (wx.Frame)
        :param prefsIO: (Preferences_IO)

        :returns: wx.Panel

        """
        return FileManager(parent, prefsIO=self._prefsIO)

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
        ide = event.GetId()

        if ide == wx.ID_EXIT:
            self.OnExitApp(event)
            return True

        elif ide == wx.ID_CLOSE:
            self.OnClose(event)
            return True

        elif ide == wx.ID_ADD:
            self.OnAdd(event)
            return True

        elif ide == wx.ID_REMOVE:
            self.OnRemove(event)
            return True

        elif ide == ID_TB_NEWTAB:
            self.OnNewTab(event)
            return True

        elif ide == ID_TB_CLOSETAB:
            self.OnCloseTab(event)
            return True

        elif ide == wx.ID_PREFERENCES:
            self.OnSettings(event)

        elif ide == wx.ID_HELP:
            self.OnHelp(event)
            return True

        elif ide == wx.ID_ABOUT:
            ShowAboutDialog(self, self._prefsIO)
            return True

        return wx.GetApp().ProcessEvent(event)

    # ------------------------------------------------------------------------

    def OnExitApp(self, event):
        """Destroys the main frame which quits the wxPython application."""

        response = ShowYesNoQuestion(self, self._prefsIO, "Are you sure you want to quit?")
        if response == wx.ID_YES:
            if self.GetParent() is not None:
                self.GetParent().SetFocus()
                self.GetParent().Raise()
            self.Destroy()
        else:
            event.StopPropagation()

    # ------------------------------------------------------------------------

    def OnClose(self, event):
        """Close properly the client then exit."""

        closeEvent = wx.CloseEvent(wx.wxEVT_CLOSE_WINDOW, self.GetId())
        closeEvent.SetEventObject(self)
        wx.PostEvent(self._clientpanel, closeEvent)
        self.Close()

    # ------------------------------------------------------------------------
    # File management... Callbacks.
    # ------------------------------------------------------------------------

    def OnAdd(self, event):
        """Received an event to add new files."""

        if self._fmtype == "DATAFILES":
            self.AddFiles(filedialogs.OpenAnnotationFiles())

        elif self._fmtype == "SOUNDFILES":
            self.AddFiles(filedialogs.OpenSoundFiles())

        else:
            self.AddFiles(filedialogs.OpenAnyFiles())

    # ------------------------------------------------------------------------

    def OnRemove(self, event):
        """Received an event to close files."""

        evt = FileWanderEvent(filename=None,status=False)
        evt.SetEventObject(self)
        wx.PostEvent(self._filepanel, evt)

    # -------------------------------------------------------------------------
    # Client Callbacks
    # -------------------------------------------------------------------------

    def OnNewTab(self, event):
        """Add a page in the client."""

        evt = NotebookNewPageEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self._clientpanel, evt)

    # -------------------------------------------------------------------------

    def OnCloseTab(self, event):
        """Close a page in the client."""

        evt = NotebookClosePageEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self._clientpanel, evt)

    # -------------------------------------------------------------------------

    def OnFileAdded(self, event):
        """Add a file of the file manager."""

        self.AddFiles([event.filename])

    # -------------------------------------------------------------------------

    def OnFileClosed(self, event):
        """Remove of the file manager."""

        # Get the list of closed files and remove them of the file manager
        files = event.filenames

        for f in files:
            # Remove of the file manager
            evt = FileWanderEvent(filename=f, status=False)
            evt.SetEventObject(self)
            wx.PostEvent(self._filepanel, evt)

    # -------------------------------------------------------------------------
    # Help... Callbacks
    # -------------------------------------------------------------------------

    def OnHelp(self, evt):
        """Open the help frame."""

        ShowInformation(self, self._prefsIO,
                        "The documentation is available online and "
                        "the SPPAS package contains a printable version.")

    # ------------------------------------------------------------------------

    def OnSettings(self, event):
        """Open the Settings box."""

        import copy
        p = copy.deepcopy(self._prefsIO)

        prefdlg = SettingsDialog(self, p)
        res = prefdlg.ShowModal()
        if res == wx.ID_OK:
            self.SetPrefs(prefdlg.GetPreferences())
            if self.GetParent() is not None:
                try:
                    self.GetParent().SetPrefs(prefdlg.GetPreferences())
                except Exception:
                    pass
        prefdlg.Destroy()
        self._LayoutFrame()

    # -------------------------------------------------------------------------
    # Data management
    # -------------------------------------------------------------------------

    def AddFiles(self, files):
        """
        Add files into the file manager.

        :param files: (list of String)

        """
        if len(files) > 0:
            # Get the list of files to open/view
            for f in files:
                # Add in the file manager
                evt = FileWanderEvent(filename=f, status=True)
                evt.SetEventObject(self)
                wx.PostEvent(self._filepanel, evt)

            self.Refresh()

    # ------------------------------------------------------------------------

    def OnFileWander(self, event):
        """We received an event: a file was added/removed."""

        owner = event.GetEventObject()
        f = event.filename
        s = event.status

        if owner == self._filepanel:
            event.SetEventObject(self)
            wx.PostEvent(self._clientpanel, event)
        else:
            evt = FileCheckEvent(filename=f, status=s)
            evt.SetEventObject(self)
            wx.PostEvent(self._filepanel, evt)

    # -------------------------------------------------------------------------
    # Other
    # -------------------------------------------------------------------------

    def SetPrefs(self, prefs):
        """Fix new preferences."""

        self._prefsIO = prefs
        self.toolbar.SetPrefs(self._prefsIO)

        # change to the children anz_panels
        evt = SettingsEvent(prefsIO=self._prefsIO)
        evt.SetEventObject(self)
        wx.PostEvent(self._filepanel, evt)
        wx.PostEvent(self._clientpanel, evt)
