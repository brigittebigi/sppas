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

    ui.phoenix.page_analyze.anz_listviews.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas import paths
import sppas.src.audiodata.aio
from sppas.src.config import msg
from sppas.src.utils import u

from ..windows import sppasToolbar
from ..windows import sppasPanel
from ..windows import sppasCollapsiblePanel
from ..windows import sppasScrolledPanel
from ..windows import sppasPlayerControlsPanel
from ..windows import sppasProgressDialog
from ..dialogs import sppasChoiceDialog
from ..dialogs import sppasTextEntryDialog
from ..dialogs import Confirm
from ..dialogs import TiersView
from ..dialogs import StatsView
from ..dialogs import sppasTiersSingleFilterDialog
from ..dialogs import sppasTiersRelationFilterDialog

from .anz_baseviews import BaseViewFilesPanel
# from .timeview import MediaViewPanel
# from .timeview import TrsViewPanel

# ----------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_CONFIRM = u(msg("Confirm?"))
ACT_MOVE_UP = u(msg("Move Up"))
ACT_MOVE_DOWN = u(msg("Move Down"))

# ----------------------------------------------------------------------------


class sppasSplitterWindow(wx.SplitterWindow):
    """Override the splitter base class.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init_(self, *args, **kwargs):
        super(sppasSplitterWindow, self).__init__(*args, **kwargs)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.Window.SetFont(self, font)
        for c in self.GetChildren():
            c.SetFont(font)
        self.Layout()

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------


class TimeViewFilesPanel(BaseViewFilesPanel):
    """Panel to play media and show content of the opened files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, name="timeviewfiles", files=tuple()):
        super(TimeViewFilesPanel, self).__init__(
            parent,
            name=name,
            files=files)

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self._hicolor = color
        # set to toolbar
        btn = self.FindWindow("subtoolbar1").get_button("tier_paste")
        btn.SetFocusColour(color)
        # set to the panels
        for filename in self._files:
            panel = self._files[filename]
            panel.SetHighLightColor(color)

    # -----------------------------------------------------------------------

    def can_edit(self):
        """Return True if this view can edit/save the file content.

        Override base class.

        The methods 'is_modified' and 'save' should be implemented in the
        view panel of each file.

        """
        return False

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def _show_file(self, name):
        """Override. Create a ViewPanel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        panel = sppasCollapsiblePanel(self.GetScrolledPanel(), label=name)
        self.GetScrolledSizer().Add(panel, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 20)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)
        self.Layout()
        return panel
        fe = ""
        if name is not None:
            fn, fe = os.path.splitext(name)
        if fe.lower() in sppas.src.audiodata.aio.extensions:
            wx.LogMessage("Displaying audio file {} in TimeView mode.".format(name))
            panel = AudioListViewPanel(self.GetScrolledPanel(), filename=name)
        else:
            wx.LogMessage("Displaying transcription file {} in TimeView mode.".format(name))
            panel = TrsListViewPanel(self.GetScrolledPanel(), filename=name)
            panel.SetHighLightColor(self._hicolor)
        self.GetScrolledSizer().Add(panel, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 20)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)

        return panel

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create the main toolbar.

        :return: (sppasPanel, wx.Panel, sppasToolbar, ...)

        """
        toolbar = sppasToolbar(self, name="toolbar_views")
        toolbar.AddTitleText("A toolbar will be here!")
        toolbar.Bind(wx.EVT_BUTTON, self._process_toolbar_event)
        return toolbar

    # -----------------------------------------------------------------------

    def _create_scrolled_content(self):
        """Override. Create the main panel to display the content.

        In the base class, it is supposed that it returns a scrolled panel.
        In this case, we'll return a wx.Splitter. Window1 of the splitter is
        a player controls, and Window2 is another splitter, in which Window1
        is a scrolled panel and Window2 is a ListCtrl.

        :return: (sppasPanel, wx.Panel, sppasScrolled, ...)

        """
        splitter = sppasSplitterWindow(self,
                                       style=wx.SP_LIVE_UPDATE | wx.NO_BORDER,
                                       name="horiz_splitter")

        # Window 1 of the splitter: player controls
        p1 = sppasPlayerControlsPanel(splitter, name="player_controls_panel")
        best_size = p1.GetBestSize()
        # self.__add_custom_controls(p1)

        # Window 2 of the splitter: a scrolled panel with all media
        p2 = self.__create_scrolled_panel(splitter)

        # Fix size&layout
        splitter.SetMinimumPaneSize(best_size[1])
        splitter.SplitHorizontally(p1, p2, best_size[1])
        splitter.SetSashGravity(0.)

        return splitter

    # -----------------------------------------------------------------------

    def __create_scrolled_panel(self, parent):
        """The scrolled panel is at left in a splitter."""
        splitter = sppasSplitterWindow(parent,
                                       style=wx.SP_LIVE_UPDATE | wx.NO_BORDER,
                                       name="vert_splitter")

        # Window 1 of the splitter: time view of media and other files
        p1 = sppasScrolledPanel(splitter,
                                style=wx.SHOW_SB_ALWAYS | wx.VSCROLL,
                                name="scrolled_views")
        sizer = wx.BoxSizer(wx.VERTICAL)
        p1.SetupScrolling(scroll_x=False, scroll_y=True)
        p1.SetSizer(sizer)
        p1.SetMinSize(wx.Size(sppasPanel.fix_size(256), -1))
        # min_height = sppasPanel.fix_size(48)*len(self._files)
        # panel.SetMinSize(wx.Size(sppasPanel.fix_size(420), min_height))

        # Window 2 of the splitter: edit view of annotated files
        p2 = sppasPanel(splitter)
        p2.SetMinSize(wx.Size(sppasPanel.fix_size(128), -1))

        # Fix size&layout
        splitter.SetMinimumPaneSize(sppasPanel.fix_size(128))
        splitter.SplitVertically(p1, p2, sppasPanel.fix_size(512))
        splitter.SetSashGravity(0.5)

        return splitter

    # -----------------------------------------------------------------------

    def _process_toolbar_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        event.Skip()

    # -----------------------------------------------------------------------

    def play(self):
        """Play all the media at a time."""
        for filename in self._files:
            panel = self._files[filename]
            # if isinstance(panel, MediaViewPanel):
            #    panel.play()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(TimeViewFilesPanel):
    TEST_FILES = (
        os.path.join(paths.samples, "COPYRIGHT.txt"),
        os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.wav"),
        os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra"),
        os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")
    )

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="TestPanel-anz_timeviews",
            files=TestPanel.TEST_FILES)

