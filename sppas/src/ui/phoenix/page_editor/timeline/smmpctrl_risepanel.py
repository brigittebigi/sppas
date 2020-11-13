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

    ui.phoenix.page_editor.timeline.smmpctrl_risepanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.ui.phoenix.windows.panels import sppasPanel
from sppas.src.ui.phoenix.windows.panels import sppasVerticalRisePanel
from sppas.src.ui.phoenix.windows.media import sppasMMPCtrl

# ----------------------------------------------------------------------------


class SMMPCPanel(sppasVerticalRisePanel):
    """A rise Panel for the SPPAS Multi Media Control System.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Create exactly the same rise panel with the same borders than any other
    rise panel of the timeline view... so all panels - including this one,
    will be vertically aligned on screen.

    Events emitted by this class:

        - EVT_TIME_VIEW

    """

    def __init__(self, parent, name="smmpc_risepanel"):
        super(SMMPCPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            label="",
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
            name=name)

        # Create the GUI
        mmpc = sppasMMPCtrl(self, name="smmpc_panel")
        mmpc.SetButtonWidth(32)
        self.SetPane(mmpc)

        # Look&feel
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()
        self.Expand()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        sppasVerticalRisePanel.SetBackgroundColour(self, colour)
        self._tools_panel.SetBackgroundColour(self.GetHighlightedBackgroundColour())

    # -----------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        color = self.GetBackgroundColour()
        r, g, b, a = color.Red(), color.Green(), color.Blue(), color.Alpha()

        delta = 15
        if (r + g + b) > 384:
            return wx.Colour(r, g, b, a).ChangeLightness(100 - delta)
        return wx.Colour(r, g, b, a).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Override in order to disable the collapsible button.

        Create a panel with the collapsible button but without
        the slashdot button normally used to show a filename.

        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Create, disable and hide the button to collapse/expand.
        self._btn = self._create_collapsible_button()
        self._btn.Enable(False)
        self._btn.Hide()
        sizer.Add(self._btn, 0, wx.FIXED_MINSIZE, 0)
        self._tools_panel.SetSizer(sizer)
        w = self.GetButtonWidth()
        # Fix the size of the tools,
        self._tools_panel.SetMinSize(wx.Size(w, w*2))

# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="MultiMediaPlayerControl RisePanel")

        panel = SMMPCPanel(self)
        # panel.SetBackgroundColour(wx.LIGHT_GREY)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(panel, 0, wx.EXPAND, 0)
        self.SetSizer(s)

