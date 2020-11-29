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

    src.ui.phoenix.windows.label.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description
    ===========

    This module implements self-drawn label classes used to draw a label.
    A label is a single-line non-modifiable text. It's size is automatically
    adjusted when the label or the font is changed.

"""

import wx

from .baselabelwindow import sppasLabelWindow

# ---------------------------------------------------------------------------


class sppasLabelHeader(sppasLabelWindow):
    """A label text designed for the header of a frame or dialog.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=-1, label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="header"):
        """Initialize a new sppasLabelWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    A position of (-1, -1) indicates a default position.
        :param size:   If the default size (-1, -1) is specified
                       then the best size is chosen.
        :param style:  See https://wxpython.org/Phoenix/docs/html/wx.Window.html
        :param name:   Name of the window.

        """
        super(sppasLabelHeader, self).__init__(parent, id, label, pos, size, style, name)

        self._vert_border_width = self.get_font_height() // 2
        try:
            settings = wx.GetApp().settings
            wx.Window.SetForegroundColour(self, settings.header_fg_color)
            wx.Window.SetBackgroundColour(self, settings.header_bg_color)
            self.SetFont(settings.header_text_font)
            self._min_height = settings.get_font_height()
        except AttributeError:
            self.InheritAttributes()
            self._min_height = self.get_font_height()
        self._border_color = self.GetForegroundColour()

    # -----------------------------------------------------------------------

    def DrawBackground(self, dc, gc):
        """Draw the background with a color or transparent."""
        w, h = self.GetClientSize()
        bg_color = self.GetPenBackgroundColour()
        brush = wx.Brush(bg_color, wx.BRUSHSTYLE_SOLID)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()
        dc.SetPen(wx.TRANSPARENT_PEN)

        g_color = self.GetForegroundColour()

        # Left to right gradient color
        dc.DrawRectangle(0, 0, w // 3, h)
        box_rect = wx.Rect(w // 3, 0, w, h)
        dc.GradientFillLinear(box_rect, bg_color, g_color, wx.EAST)

    # -----------------------------------------------------------------------

    def DrawBorder(self, dc, gc):
        """Override. Draw a solid top/bottom border.

        """
        w, h = self.GetClientSize()
        pen = wx.Pen(self.GetPenBorderColour(), 1, self._border_style)
        dc.SetPen(pen)

        for i in range(self._horiz_border_width):
            # upper line
            dc.DrawLine(0, i, w, i)
            # bottom line
            dc.DrawLine(0, h - i, w, h - i)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE,
            name="Test Header Window")

        # A panel without sizer. Labels have fixed pos.
        # ----------------------------------------------
        p1 = wx.Panel(self, name="p1")
        l1 = sppasLabelHeader(p1, label="A simple text no size by default.",
                              pos=(10, 10))
        l1.SetHorizBorderWidth(2)
        l2 = sppasLabelHeader(p1, label="A simple text with a default size.",
                              pos=(10, 40), size=(200, 25))
        l3 = sppasLabelHeader(p1, label="Text with set font applied.",
                              pos=(10, 70))
        font = self.GetFont()
        l3.SetFont(wx.Font(
            font.GetPointSize()*2, font.GetFamily(), font.GetStyle(),
            wx.FONTWEIGHT_BOLD, underline=False, faceName=font.GetFaceName()))

        # A panel with a sizer. Proportion of labels in the sizer is 0.
        # ----------------------------------------------
        p2 = wx.Panel(self, name="p2")
        p2.SetBackgroundColour(wx.LIGHT_GREY)

        la = sppasLabelHeader(p2, label="A simple text in a sizer")
        lb = sppasLabelHeader(p2)
        lb.SetBackgroundColour(wx.YELLOW)
        lb.SetLabel("Set label after the window was created. A very *%¨£%°_ long simple text in a sizer ....")
        lc = sppasLabelHeader(p2, label="A bold text in a sizer")
        font = self.GetFont()
        lc.SetFont(wx.Font(
            font.GetPointSize() * 2, font.GetFamily(), font.GetStyle(),
            wx.FONTWEIGHT_BOLD, underline=False, faceName=font.GetFaceName()))
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(la, 0)
        s.Add(lb, 0)
        s.Add(lc, 0)
        p2.SetSizer(s)

        # A panel with a sizer. Proportion of labels in the sizer is 1.
        # ----------------------------------------------
        p3 = wx.Panel(self, name="p3")
        p3.SetBackgroundColour(wx.Colour("light coral"))

        lx = sppasLabelHeader(p3, label="A simple text in a sizer")
        ly = sppasLabelHeader(p3, label="A very very very very very *%¨£%°_ long simple text in a sizer sizer sizer sizer....")
        lz = sppasLabelHeader(p3, label="A bold text in a sizer")
        font = self.GetFont()
        lz.SetFont(wx.Font(
            font.GetPointSize() * 2, font.GetFamily(), font.GetStyle(),
            wx.FONTWEIGHT_BOLD, underline=False, faceName=font.GetFaceName()))
        ss = wx.BoxSizer(wx.VERTICAL)
        ss.Add(lx, 1, wx.EXPAND)
        ss.Add(ly, 1, wx.EXPAND)
        ss.Add(lz, 1, wx.EXPAND)
        p3.SetSizer(ss)

        # All such panels have a proportional size in out test
        # ====================================================
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 1, wx.EXPAND)
        sizer.Add(p2, 1, wx.EXPAND)
        sizer.Add(p3, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
