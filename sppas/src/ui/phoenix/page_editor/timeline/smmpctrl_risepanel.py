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

import os
import wx

from sppas.src.config import paths
from sppas.src.ui.phoenix.windows.panels import sppasPanel
from sppas.src.ui.phoenix.windows.panels import sppasVerticalRisePanel

from ..media import sppasMMPCtrl

# ----------------------------------------------------------------------------


class SMMPCPanel(sppasVerticalRisePanel):
    """A rise Panel for the SPPAS Multi Media Control System.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Create exactly the same rise panel with the same borders than any other
    rise panel of the timeline view... All panels - including this one,
    will be vertically aligned on screen.

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
        mmpc.SetButtonWidth(24)
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

    def smmpc(self):
        """Return the smmpc if it was successfully created or None."""
        return self.FindWindow("smmpc_panel")

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
        """Override. Add custom buttons.

        Create a panel with the collapsible button but without
        the slashdot button normally used to show a filename.

        """
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create, disable and hide the button to collapse/expand.
        self._btn = self._create_collapsible_button()
        # self._btn.Enable(False)
        # self._btn.Hide()
        sizer.Add(self._btn, 0, wx.FIXED_MINSIZE, 0)

        # Create a custom button: show/hide the slider
        btn1 = self._create_tool_togglebutton(icon="position")
        btn1.Enable(True)
        btn1.SetValue(True)
        btn1.Show()
        sizer.Add(btn1, 0, wx.FIXED_MINSIZE, 0)
        btn1.Bind(wx.EVT_TOGGLEBUTTON, self._on_show_slider)

        # Create a custom button: show/hide the ruler
        btn2 = self._create_tool_togglebutton(icon="ruler")
        btn2.Enable(True)
        btn2.SetValue(True)
        btn2.Show()
        sizer.Add(btn2, 0, wx.FIXED_MINSIZE, 0)
        btn2.Bind(wx.EVT_TOGGLEBUTTON, self._on_show_ruler)

        # Fix the size of the tools
        w = self.GetButtonWidth()
        self._tools_panel.SetMinSize(wx.Size(w, w*3))
        self._tools_panel.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def _on_show_slider(self, evt):
        self.GetPane().show_range(evt.GetEventObject().GetValue())
        self.Layout()
        self.SendSizeEventToParent()

    def _on_show_ruler(self, evt):
        self.GetPane().show_rule(evt.GetEventObject().GetValue())
        self.Layout()
        self.SendSizeEventToParent()

# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="MultiMediaPlayerControl RisePanel")

        button1 = wx.Button(self, -1, size=(120, 50), label="Threading LOAD", name="load_button_1")
        button2 = wx.Button(self, -1, size=(120, 50), label="Sequential LOAD", name="load_button_2")
        panel = SMMPCPanel(self, "smmpc_risepanel")
        player = sppasPanel(self, name="player_panel")

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(button1, 0, wx.ALL, 8)
        s.Add(button2, 0, wx.ALL, 8)
        s.Add(panel, 0, wx.EXPAND, 0)
        s.Add(player, 1, wx.EXPAND, 0)
        self.SetSizer(s)

        button1.Bind(wx.EVT_BUTTON, self._on_load_1)
        button2.Bind(wx.EVT_BUTTON, self._on_load_2)

    # ----------------------------------------------------------------------

    @property
    def smmc(self):
        return self.FindWindow("smmpc_risepanel").GetPane()

    # ----------------------------------------------------------------------

    def _on_load_1(self, event):
        self.load_files(with_threads=True)

    # ----------------------------------------------------------------------

    def _on_load_2(self, event):
        self.load_files(with_threads=False)

    # ----------------------------------------------------------------------

    def load_files(self, with_threads=True):
        self.FindWindow("load_button_1").Enable(False)
        self.FindWindow("media_play").Enable(False)

        # Loading the videos with threads make the app crashing under MacOS:
        # Python[31492:1498940] *** Terminating app due to uncaught exception
        # 'NSInternalInconsistencyException', reason: 'NSWindow drag regions
        # should only be invalidated on the Main Thread!'
        player = self.FindWindow("player_panel")
        self.smmc.add_video([os.path.join(paths.samples, "faces", "video_sample.mp4")], player)

        # To load files in parallel, with threads:
        if with_threads is True:
            self.smmc.add_audio(
                [os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"),
                 os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"),
                 os.path.join(paths.samples, "samples-eng", "oriana1.wav"),
                 os.path.join(paths.samples, "samples-eng", "oriana2.WAV"),
                 ])

        else:
            # To load files sequentially, without threads:
            self.smmc.add_audio(os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
            self.smmc.add_audio(os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))
            self.smmc.add_audio(os.path.join(paths.samples, "samples-eng", "oriana1.wav"))
            self.smmc.add_audio(os.path.join(paths.samples, "samples-eng", "oriana2.WAV"))

