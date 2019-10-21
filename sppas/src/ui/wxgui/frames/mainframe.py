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

    src.wxgui.frames.mainframe.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    GUI main frame for SPPAS.

"""
import wx
import logging

from sppas import msg
from sppas import u
import sppas.src.anndata.aio
import sppas.src.audiodata.aio

from ..cutils.imageutils import spBitmap
from ..structs.prefs import Preferences_IO
from ..sp_icons import APP_ICON

from ..sp_consts import MIN_FRAME_W
from ..sp_consts import MIN_FRAME_H
from ..sp_consts import FRAME_STYLE
from ..sp_consts import FRAME_TITLE

from ..sp_consts import ID_ANNOTATIONS
from ..sp_consts import ID_COMPONENTS
from ..sp_consts import ID_PLUGINS
from ..sp_consts import ID_ACTIONS
from ..sp_consts import ID_FILES
from ..sp_consts import ID_FRAME_DATAROAMER
from ..sp_consts import ID_FRAME_SNDROAMER
from ..sp_consts import ID_FRAME_IPUSCRIBE
from ..sp_consts import ID_FRAME_SPPASEDIT
from ..sp_consts import ID_FRAME_STATISTICS
from ..sp_consts import ID_FRAME_DATAFILTER

from ..panels.filetree import FiletreePanel
from ..panels.mainbuttons import MainActionsPanel, MainMenuPanel, MainActionsMenuPanel, MainTitlePanel, MainTooltips
from ..panels.components import AnalyzePanel
from ..panels.aannotations import AnnotationsPanel
from ..panels.pplugins import PluginsPanel
from ..panels.about import AboutSPPASPanel
from ..ui.splitterpanel import SplitterPanel

from ..frames.dataroamerframe import DataRoamerFrame
from ..frames.audioroamerframe import AudioRoamerFrame
from ..frames.ipuscribeframe import IPUscribeFrame
from ..frames.sppaseditframe import SppasEditFrame
from ..frames.datafilterframe import DataFilterFrame
from ..frames.datastatsframe import DataStatsFrame
from ..views.settings import SettingsDialog
from ..dialogs.msgdialogs import ShowInformation

from sppas.src.ui.wxgui import SETTINGS_FILE
from .logsframe import sppasLogWindow

# -----------------------------------------------------------------------
# S P P A S  Graphical User Interface... is here!
# -----------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))

# -----------------------------------------------------------------------


class FrameSPPAS(wx.Frame):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS main frame based on wx library.

    """
    def __init__(self, preferencesIO=None, log_level=0):
        """Constructor of the SPPAS main frame.

        :param preferencesIO: (Preferences_IO)

        """
        wx.Frame.__init__(self, None, -1, title=FRAME_TITLE, style=FRAME_STYLE)

        # Members
        if preferencesIO is None:
            # Try to get prefs from a file, or fix default values.
            preferencesIO = Preferences_IO(SETTINGS_FILE)
            preferencesIO.Read()
        self.preferences = preferencesIO
        self.actions = None
        self.flp = None
        self._left_panel = None
        self._right_panel = None
        self._leftsizer = None
        self._rightsizer = None

        # Create the log window of the application and show it.
        self.log_window = sppasLogWindow(self, log_level)
        wx.Log.EnableLogging(True)

        # Create GUI
        self._init_infos()
        self._main_panel = self._create_content()

        # Events of this frame
        self.Bind(wx.EVT_CLOSE,  self.ProcessEvent)
        self.Bind(wx.EVT_BUTTON, self.ProcessEvent)

        (w, h) = wx.GetDisplaySize()
        w *= 0.6
        h = min(0.9*h, w*9/16)
        self.SetMinSize((MIN_FRAME_W, MIN_FRAME_H))
        self.SetSize(wx.Size(max(int(w), MIN_FRAME_W), max(int(h), MIN_FRAME_H)))
        self.Centre()
        self.Enable()
        self.SetFocus()

        self.Show(True)

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_infos(self):
        """ Set the title and the icon."""

        wx.GetApp().SetAppName("sppas")

        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(spBitmap(APP_ICON))
        self.SetIcon(_icon)

        # colors
        self.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont(self.preferences.GetValue('M_FONT'))

    # ------------------------------------------------------------------------

    def _create_content(self):
        """Organize all sub-panels into a main panel and return it."""

        main_panel = wx.Panel(self, -1, style=wx.NO_BORDER)
        main_panel.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        main_panel.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        main_panel.SetFont(self.preferences.GetValue('M_FONT'))

        main_menu = MainMenuPanel(main_panel, self.preferences)
        main_title = MainTitlePanel(main_panel, self.preferences)
        split_panel = self._create_splitter(main_panel)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(main_title, proportion=0, flag=wx.ALL | wx.EXPAND, border=0)
        vsizer.Add(split_panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(main_menu, proportion=0, flag=wx.ALL | wx.EXPAND, border=0)
        sizer.Add(vsizer, proportion=2, flag=wx.ALL | wx.EXPAND, border=0)
        main_panel.SetSizer(sizer)

        return main_panel

    # ------------------------------------------------------------------------

    def _create_splitter(self, parent):
        """Create the main panel content."""

        split_panel = SplitterPanel(parent, proportion=0.5)
        split_panel.SetBackgroundColour(self.preferences.GetValue('M_BGM_COLOUR'))
        split_panel.SetForegroundColour(self.preferences.GetValue('M_BGM_COLOUR'))

        # Left: File explorer and tips
        self._left_panel = wx.Panel(split_panel, -1)
        self._left_panel.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        self.flp = FiletreePanel(self._left_panel, self.preferences)
        tips = MainTooltips(self._left_panel, self.preferences)

        self._leftsizer = wx.BoxSizer(wx.VERTICAL)
        self._leftsizer.Add(self.flp, proportion=2, flag=wx.EXPAND, border=0)
        self._leftsizer.Add(tips, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER, border=20)
        self._left_panel.SetSizer(self._leftsizer)
        if self.preferences.GetValue('M_TIPS') is False:
            tips.Hide()

        # Right: Actions to perform on selected files
        self._right_panel = wx.Panel(split_panel, -1)
        self.actionsmenu = MainActionsMenuPanel(self._right_panel, self.preferences)
        self.actionsmenu.ShowBack(False)
        self.actions = MainActionsPanel(self._right_panel, self.preferences)

        self._rightsizer = wx.BoxSizer(wx.VERTICAL)
        self._rightsizer.Add(self.actionsmenu, proportion=0, flag=wx.ALL | wx.EXPAND, border=0)
        self._rightsizer.Add(self.actions, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
        self._right_panel.SetSizer(self._rightsizer)

        split_panel.SetMinimumPaneSize(0.4*MIN_FRAME_W)
        split_panel.SplitVertically(self._left_panel, self._right_panel)

        self._left_panel.SetMinSize((0.4*MIN_FRAME_W, 0.7*MIN_FRAME_H))
        self._right_panel.SetMinSize((0.4*MIN_FRAME_W, 0.7*MIN_FRAME_H))

        return split_panel

    # ------------------------------------------------------------------------

    def fix_filecontent(self):
        """Fix the file explorer panel content."""

        self.flp.RefreshTree()
        self._left_panel.Layout()
        self._left_panel.Refresh()

    # ------------------------------------------------------------------------

    def fix_actioncontent(self, ide):
        """Fix the action panel content."""

        # Remove current actions panel
        if self.actions is not None:
            self._rightsizer.Detach(self.actions)
            self.actions.Destroy()

        # Create the new one:
        if ide == ID_ACTIONS:
            self.actions = MainActionsPanel(self._right_panel, self.preferences)
            self.actionsmenu.ShowBack(False, "")

        elif ide == ID_COMPONENTS:
            self.actions = AnalyzePanel(self._right_panel, self.preferences)
            self.actionsmenu.ShowBack(True, " " + _("Analyze") + " ")

        elif ide == ID_ANNOTATIONS:
            self.actions = AnnotationsPanel(self._right_panel, self.preferences)
            self.actionsmenu.ShowBack(True, " " + _("Annotate") + " ")

        elif ide == wx.ID_ABOUT:
            self.actions = AboutSPPASPanel(self._right_panel, self.preferences)
            self.actionsmenu.ShowBack(True, " " + _("About") + " ")

        elif ide == ID_PLUGINS:
            self.actions = PluginsPanel(self._right_panel, self.preferences)
            self.actionsmenu.ShowBack(True, " " + _("Plugins") + " ")

        self._rightsizer.Add(self.actions, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
        self._LayoutFrame()

    # -----------------------------------------------------------------------

    def _LayoutFrame(self):
        """Lays out the frame."""

        wx.LayoutAlgorithm().LayoutFrame(self, self._main_panel)
        self._right_panel.SendSizeEvent()
        self.Refresh()

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def ProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.

        """
        ide = event.GetId()

        if ide == wx.ID_EXIT:
            self.OnExit(event)

        elif ide == wx.ID_PREFERENCES:
            self.OnSettings(event)

        elif ide == wx.ID_HELP:
            self.OnHelp(event)

        elif ide == ID_PLUGINS:
            self.fix_actioncontent(ID_PLUGINS)

        elif ide == wx.ID_ABOUT:
            self.fix_actioncontent(wx.ID_ABOUT)

        elif ide == ID_ANNOTATIONS:
            self.fix_actioncontent(ID_ANNOTATIONS)

        elif ide == ID_COMPONENTS:
            self.fix_actioncontent(ID_COMPONENTS)

        elif ide == ID_ACTIONS:
            self.fix_actioncontent(ID_ACTIONS)

        elif ide == ID_FILES:
            self.fix_filecontent()

        elif ide == ID_FRAME_DATAROAMER or ide == ID_FRAME_SNDROAMER or ide == ID_FRAME_IPUSCRIBE or \
             ide == ID_FRAME_SPPASEDIT or ide == ID_FRAME_DATAFILTER or ide == ID_FRAME_STATISTICS:
            self.OnAnalyzer(event)

        return True

    # -----------------------------------------------------------------------

    def OnExit(self, evt):
        """Close the frame."""
        # Stop redirecting logging to this application
        self.log_window.redirect_logging(False)

        logging.info('SPPAS main frame exit.')
        self.Destroy()

    # -----------------------------------------------------------------------

    def OnSettings(self, event):
        """Open the Settings dialog."""

        import copy
        p = copy.deepcopy(self.preferences)

        prefdlg = SettingsDialog(self, p)
        res = prefdlg.ShowModal()
        if res == wx.ID_OK:
            self.SetPrefs(prefdlg.GetPreferences())

        prefdlg.Destroy()

    # -----------------------------------------------------------------------

    def OnHelp(self, evt):
        """Open the help frame."""

        ShowInformation(self, self.preferences,
                        "The documentation is available online and "
                        "the SPPAS package contains a printable version.")

    # -----------------------------------------------------------------------

    def __create_component(self, instance, idc):
        """Create or raise a component frame and return it."""

        for c in self.GetChildren():
            if isinstance(c, instance):
                c.SetFocus()
                c.Raise()
                return c
        return instance(self, idc, self.preferences)

    # -----------------------------------------------------------------------

    def OnAnalyzer(self, evt):
        """Open a component."""

        eid = evt.GetId()
        selection = []

        if eid == ID_FRAME_DATAROAMER:
            selection = self.GetTrsSelection()
            analyzer = self.__create_component(DataRoamerFrame, ID_FRAME_DATAROAMER)

        elif eid == ID_FRAME_SNDROAMER:
            selection = self.GetAudioSelection()
            analyzer = self.__create_component(AudioRoamerFrame, ID_FRAME_SNDROAMER)

        elif eid == ID_FRAME_SPPASEDIT:
            selection = self.GetTrsSelection() + self.GetAudioSelection()
            analyzer = self.__create_component(SppasEditFrame, ID_FRAME_SPPASEDIT)

        elif eid == ID_FRAME_IPUSCRIBE:
            selection = self.GetAudioSelection()
            analyzer = self.__create_component(IPUscribeFrame, ID_FRAME_IPUSCRIBE)

        elif eid == ID_FRAME_DATAFILTER:
            selection = self.GetTrsSelection()
            analyzer = self.__create_component(DataFilterFrame, ID_FRAME_DATAFILTER)

        elif eid == ID_FRAME_STATISTICS:
            selection = self.GetTrsSelection()
            analyzer = self.__create_component(DataStatsFrame, ID_FRAME_STATISTICS)

        else:
            raise ValueError('Unknown frame id: {:d}'.format(eid))

        if len(selection) > 0:
            analyzer.AddFiles(selection)

    # -----------------------------------------------------------------------
    # Functions
    # -----------------------------------------------------------------------

    def SetPrefs(self, prefs):
        """Set new preferences."""

        self.preferences = prefs

        self._left_panel.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        self.flp.SetPrefs(self.preferences)

        self._rightsizer.Detach(self.actions)
        self.actions.Destroy()
        self.actions = MainActionsPanel(self._right_panel, self.preferences)
        self._rightsizer.Add(self.actions, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)

        self._LayoutFrame()

    # -----------------------------------------------------------------------

    def GetSelected(self, extension):
        """Return the list of selected files in FLP."""
        return self.flp.GetSelected(extension)

    # -----------------------------------------------------------------------

    def GetTrsSelection(self):
        """Return the list of annotated files selected in the FLP."""
        selection = list()
        for ext in sppas.src.anndata.aio.extensions:
            selection.extend(self.flp.GetSelected(ext))
        return selection

    # -----------------------------------------------------------------------

    def GetAudioSelection(self):
        """Return the list of audio files selected in the FLP."""
        selection = list()
        for ext in sppas.src.audiodata.aio.extensions:
            selection.extend(self.flp.GetSelected(ext))
        return selection
