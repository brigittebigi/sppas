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

    src.ui.phoenix.windows.baselabelwindow.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description
    ===========

    This module implements a self-drawn base class used to draw our wx.window,
    with a label.

"""

import wx

from .basedcwindow import sppasDCWindow

# ---------------------------------------------------------------------------


class sppasLabelWindow(sppasDCWindow):
    """A base window with a DC to draw a label text.

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
                 name="sppaslabelwindow"):
        """Initialize a new sppasLabelWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    A position of (-1, -1) indicates a default position.
        :param size:   If the default size (-1, -1) is specified
                       then the best size is chosen.
        :param style:  See https://wxpython.org/Phoenix/docs/html/wx.Window.html
        :param name:   Name of the window.

        """
        self._label = label
        self._align = wx.ALIGN_LEFT  # or ALIGN_CENTER or ALIGN_RIGHT

        super(sppasLabelWindow, self).__init__(parent, id, pos, size, style, name)

        # By default, our label don't have borders
        self._vert_border_width = 0
        self._horiz_border_width = 0

        # Setup Initial Size
        self.SetBestSize(size)

    # ------------------------------------------------------------------------

    def SetFont(self, font):
        """Override. A change of font implies eventually to resize..."""
        wx.Window.SetFont(self, font)
        self.SetBestSize()
        self.Refresh()

    # ------------------------------------------------------------------------

    def GetLabel(self):
        """Return the label text as it was passed to SetLabel."""
        return self._label

    # ------------------------------------------------------------------------

    def SetLabel(self, label):
        """Set the label text.

        :param label: (str) Label text.

        """
        if label is None:
            label = ""
        self._label = str(label)
        self.SetBestSize()

    # -----------------------------------------------------------------------

    def GetAlign(self):
        return self._align

    # -----------------------------------------------------------------------

    def SetAlign(self, align=wx.ALIGN_CENTER):
        """Set the position of the label in the button.

        :param align: (int) label is at the center, at left or at right.

        """
        if align not in [wx.ALIGN_CENTER, wx.ALIGN_LEFT, wx.ALIGN_RIGHT]:
            return
        self._align = align

    # -----------------------------------------------------------------------

    Label = property(GetLabel, SetLabel)
    Align = property(GetAlign, SetAlign)

    # -----------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        self.SetMinSize(wx.Size(self._min_width, self._min_height))
        size = self.DoGetBestSize()

        (w, h) = size
        if w < self._min_width:
            w = self._min_width
        if h < self._min_height:
            h = self._min_height

        wx.Window.SetInitialSize(self, wx.Size(w, h))

    SetBestSize = SetInitialSize

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Overridden base class virtual.

        Determines the best size based on the label text size.

        """
        # if out label wasn't already defined
        if not self._label:
            return wx.Size(self._min_width, self._min_height)

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        ret_width, ret_height = dc.GetTextExtent(self._label)

        return wx.Size(ret_width, ret_height)

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Draw the label text. """
        x, y, w, h = self.GetContentRect()
        tw, th = self.get_text_extend(dc, gc, self._label)

        # min height to draw the label.
        # we authorize the font to be 20% truncated in height, at max.
        min_height = int(float(self.get_font_height()) * 0.8)
        if tw < min_height or th < min_height:
            return

        if self._align == wx.ALIGN_LEFT:
            self._draw_label(dc, gc, 1, ((h - th) // 2) + (2*self._horiz_border_width))

        elif self._align == wx.ALIGN_RIGHT:
            self._draw_label(dc, gc, w - tw - 1, ((h - th) // 2) + (2*self._horiz_border_width))

        else:
            # Center the text.
            self._draw_label(dc, gc, (w - tw) // 2, ((h - th) // 2) + (2*self._horiz_border_width))

    # -----------------------------------------------------------------------

    def _draw_label(self, dc, gc, x, y):
        font = self.GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetPenForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetPenForegroundColour())
            gc.DrawText(self._label, x, y)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE,
            name="Test Label Window")

        # A panel without sizer. Labels have fixed pos.
        # ----------------------------------------------
        p1 = wx.Panel(self, name="p1")
        l1 = sppasLabelWindow(p1, label="A simple text no size by default.",
                              pos=(10, 10))
        l2 = sppasLabelWindow(p1, label="A simple text with a default size.",
                              pos=(10, 40), size=(200, 25))
        l3 = sppasLabelWindow(p1, label="Text with set font applied.",
                              pos=(10, 70))
        font = self.GetFont()
        l3.SetFont(wx.Font(
            font.GetPointSize()*2, font.GetFamily(), font.GetStyle(),
            wx.FONTWEIGHT_BOLD, underline=False, faceName=font.GetFaceName()))

        # A panel with a sizer. Proportion of labels in the sizer is 0.
        # ----------------------------------------------
        p2 = wx.Panel(self, name="p2")
        p2.SetBackgroundColour(wx.LIGHT_GREY)

        la = sppasLabelWindow(p2, label="A simple text in a sizer")
        lb = sppasLabelWindow(p2)
        lb.SetBackgroundColour(wx.YELLOW)
        lb.SetLabel("Set label after the window was created. A very *%¨£%°_ long simple text in a sizer ....")
        lc = sppasLabelWindow(p2, label="A bold text in a sizer")
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

        lx = sppasLabelWindow(p3, label="A simple text in a sizer")
        ly = sppasLabelWindow(p3, label="A very very very very very *%¨£%°_ long simple text in a sizer sizer sizer sizer....")
        lz = sppasLabelWindow(p3, label="A bold text in a sizer")
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
