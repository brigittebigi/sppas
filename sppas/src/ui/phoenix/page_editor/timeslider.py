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

    ui.phoenix.page_editor.timeslider.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from ..windows import ToggleButton
from ..windows import sppasPanel


# ---------------------------------------------------------------------------


MSG_TOTAL_DURATION = "Total duration: "
MSG_VISIBLE_DURATION = "Visible part: "

# ----------------------------------------------------------------------------


class TimeSliderPanel(sppasPanel):
    """A panel embedding information about time: start, end, selected, etc.

     :author:       Brigitte Bigi
     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
     :contact:      contact@sppas.org
     :license:      GPL, v3
     :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    SELECTION_COLOUR = wx.Colour(160, 60, 60, 128)

    # -----------------------------------------------------------------------

    def __init__(self, parent, name="time_slider_panel"):
        """Create the panel to display time information.

        """
        super(TimeSliderPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
            name=name)

        # Create the GUI
        self._create_content()
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_toggle_event)

        # Look&feel
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. """
        wx.Panel.SetFont(self, font)
        for c in self.GetChildren():
            f = wx.Font(int(font.GetPointSize() * 0.75),
                        wx.FONTFAMILY_SWISS,   # family,
                        wx.FONTSTYLE_NORMAL,   # style,
                        wx.FONTWEIGHT_BOLD,    # weight,
                        underline=False,
                        faceName=font.GetFaceName(),
                        encoding=wx.FONTENCODING_SYSTEM)
            c.SetFont(f)

        self.Layout()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override. """
        wx.Panel.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            if "during" not in c.GetName():
                c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        btn_dur = self.__create_toggle_btn(self, MSG_TOTAL_DURATION+"0.000000", "total_btn")
        btn_dur.SetValue(True)
        btn_part = self.__create_toggle_btn(self, MSG_VISIBLE_DURATION+"0.000000", "part_btn")
        btn_part.SetBorderWidth(0)

        panel_sel = sppasPanel(self, name="selection_panel")
        btn_before_sel = self.__create_toggle_btn(panel_sel, "0.000000", "before_btn")
        btn_during_sel = self.__create_toggle_btn(panel_sel, "0.000000", "during_btn")
        btn_after_sel = self.__create_toggle_btn(panel_sel, "0.000000", "after_btn")
        sizer_sel = wx.BoxSizer(wx.HORIZONTAL)
        sizer_sel.Add(btn_before_sel, 0, wx.ALL, 0)
        sizer_sel.Add(btn_during_sel, 0, wx.ALL, 0)
        sizer_sel.Add(btn_after_sel, 0, wx.ALL, 0)
        panel_sel.SetSizer(sizer_sel)

        slider = sppasPanel(self, style=wx.SIMPLE_BORDER, name="time_slider")
        height = self.get_font_height()
        slider.SetMinSize(wx.Size(-1, height))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(slider, 0, wx.EXPAND, 0)
        sizer.Add(panel_sel, 0, wx.EXPAND, 0)
        sizer.Add(btn_part, 0, wx.EXPAND, 0)
        sizer.Add(btn_dur, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_toggle_btn(self, parent, label, name):
        height = self.get_font_height()
        btn = ToggleButton(parent, label=label)
        btn.SetName(name)
        btn.SetMinSize(wx.Size(-1, height))

        btn.SetBorderWidth(1)
        btn.SetFocusWidth(0)
        btn.SetValue(False)

        return btn

    # -----------------------------------------------------------------------

    def _process_toggle_event(self, event):
        for child in self.GetChildren():
            if isinstance(child, ToggleButton) is True:
                if child is event.GetEventObject():
                    child.SetValue(True)
                else:
                    child.SetValue(False)
            for c in child.GetChildren():
                if isinstance(c, ToggleButton) is True:
                    if c is event.GetEventObject():
                        c.SetValue(True)
                    else:
                        c.SetValue(False)


# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Time Edit Panel")

        p = TimeSliderPanel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

