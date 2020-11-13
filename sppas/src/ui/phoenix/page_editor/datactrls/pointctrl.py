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

    src.ui.phoenix.page_edirot.datactrls.pointctrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.lib.newevent

from sppas.src.anndata import sppasPoint

from .basedatactrl import sppasDataWindow

# ---------------------------------------------------------------------------


class sppasPointWindow(sppasDataWindow):
    """A window with a DC to draw a sppasPoint().

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=-1,
                 data=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name="pointctrl"):
        """Initialize a new sppasPointWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param data:   Data to draw.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param name:   Window name.

        """
        style = wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE
        super(sppasPointWindow, self).__init__(
            parent, id, data, pos, size, style, name)

        self._data = None
        if data is not None:
            self.SetData(data)

        # Override parent members
        self._min_width = 1
        self._min_height = 4
        self._vert_border_width = 0
        self._horiz_border_width = 0
        self._focus_width = 0
        try:
            self._bgcolor = wx.GetApp().settings.bg_color
        except AttributeError:
            self._bgcolor = self.GetParent().GetBackgroundColor()

        self.SetInitialSize(size)

    # -----------------------------------------------------------------------

    def SetData(self, data):
        """Set new data content."""
        if data != self._data:
            self._data = data
            self.SetToolTip(wx.ToolTip(self._tooltip()))
            self.Refresh()

    # -----------------------------------------------------------------------

    def SetVertBorderWidth(self, value):
        """Set the width of the left/right borders.

        :param value: (int) Border size. Not applied if not appropriate.

        """
        return

    # -----------------------------------------------------------------------

    def DrawBackground(self, dc, gc):
        """Draw the background with a gradient color from midpoint."""
        if self._data is None:
            return
        w, h = self.GetClientSize()

        brush = self.GetBackgroundBrush()
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()
        dc.SetBrush(brush)

        # If highlighted
        if self.HasFocus() is True:
            c1 = self.GetHighlightedColour(self.GetBackgroundColour())
            c2 = self.GetPenForegroundColour()
        else:
            c2 = self.GetHighlightedColour(self.GetBackgroundColour())
            c1 = self.GetPenForegroundColour()

        if w > 5:
            # Fill in the content
            mid = int(w / 2)
            box_rect = wx.Rect(0, 0, mid, h)
            dc.GradientFillLinear(box_rect, c1, c2, wx.EAST)
            box_rect = wx.Rect(mid, 0, mid, h)
            dc.GradientFillLinear(box_rect, c1, c2, wx.WEST)

        else:
            pen = wx.Pen(c1, 1, wx.SOLID)
            pen.SetCap(wx.CAP_BUTT)
            dc.SetPen(pen)
            for i in range(w):
                dc.DrawLine(i, 0, i, h)

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Override. """
        return

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test PointCtrl")

        p1 = sppasPointWindow(
            self, pos=(50, 50), size=(20, 100), data=sppasPoint(2.3, 0.01))
        p2 = sppasPointWindow(
            self, pos=(150, 50), size=(5, 100), data=sppasPoint(3))
