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

    src.ui.phoenix.windows.line.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description
    ===========

    This module implements various forms of generic lines, meaning that
    they are not built on native controls but are self-drawn.

"""

import wx

from .basedcwindow import sppasDCWindow

# ---------------------------------------------------------------------------


class sppasStaticLine(sppasDCWindow):
    """A static line is a window in which a line is drawn centered.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 orient=wx.LI_HORIZONTAL,
                 name=wx.StaticLineNameStr):

        # Members to draw a line
        self.__orient = orient
        self.__depth = 2
        self.__pen_style = wx.PENSTYLE_SOLID

        super(sppasStaticLine, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        try:
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            # only fg needed. bg of the parent. no need of a font.
        except:
            wx.LogWarning('No settings to construct sppasStaticLine.')
            pass

        # Members of the base class
        self._min_height = 4
        self._min_width = 4
        self._vert_border_width = 1
        self._horiz_border_width = 1

        self.SetInitialSize(size)

    # ------------------------------------------------------------------------
    # Getters/Setters of members
    # ------------------------------------------------------------------------

    def GetPenStyle(self):
        """Return the pen style used to draw the line."""
        return self.__pen_style

    # -----------------------------------------------------------------------

    def SetPenStyle(self, style):
        """Set the pen style used to draw the line.

        :param style: (wx.PENSTYLE_xxx)

        """
        if style not in [wx.PENSTYLE_SOLID, wx.PENSTYLE_LONG_DASH,
                         wx.PENSTYLE_SHORT_DASH, wx.PENSTYLE_DOT_DASH,
                         wx.PENSTYLE_HORIZONTAL_HATCH]:
            return

        self.__pen_style = style

    # -----------------------------------------------------------------------

    def GetDepth(self):
        """Return the depth of the line.

        :returns: (int)

        """
        return self.__depth

    # -----------------------------------------------------------------------

    def SetDepth(self, value):
        """Set the depth of the line.

        :param value: (int) Depth size. Not applied if not appropriate.

        """
        value = int(value)
        w, h = self.GetClientSize()
        if value < 0:
            return
        if self.__orient == wx.LI_VERTICAL and value > w:
            wx.LogError("Depth value {:d} of a vertical line can't be > "
                        "width {:d}".format(value, w))
            return
        if self.__orient == wx.LI_HORIZONTAL and value > h:
            wx.LogError("Depth value {:d} of an horizontal line can't be > "
                        "height {:d}".format(value, h))
            return

        self.__depth = value

    # -----------------------------------------------------------------------

    Depth = property(GetDepth, SetDepth)
    PenStyle = property(GetPenStyle, SetPenStyle)

    # ------------------------------------------------------------------------
    # Design
    # ------------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        if self.__orient == wx.LI_VERTICAL:
            self.SetMinSize(wx.Size(-1, self._min_height))
        elif self.__orient == wx.LI_HORIZONTAL:
            self.SetMinSize(wx.Size(self._min_width, -1))
        else:
            self.SetMinSize(wx.Size(self._min_width, self._min_height))

        if size is None:
            size = wx.DefaultSize

        wx.Window.SetInitialSize(self, wx.Size(size))

    SetBestSize = SetInitialSize

    # ------------------------------------------------------------------------
    # Draw methods (private)
    # ------------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        w, h = self.GetClientSize()
        pen = wx.Pen(self.GetForegroundColour(),
                     self.__depth,
                     self.__pen_style)
        dc.SetPen(pen)
        gc.SetPen(pen)

        if self.__orient == wx.LI_HORIZONTAL:
            dc.DrawLine(self._vert_border_width,
                        (h - self.__depth) // 2,
                        w - (2 * self._vert_border_width),
                        (h - self.__depth) // 2)

        if self.__orient == wx.LI_VERTICAL:
            dc.DrawLine((w - self.__depth) // 2,
                        self._horiz_border_width,
                        (w - self.__depth) // 2,
                        h - (2 * self._horiz_border_width))

    def DrawBorder(self, dc, gc):
        pass

    def DrawFocusIndicator(self, dc, gc):
        pass

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE,
            name="Test Lines")
        self.SetForegroundColour(wx.Colour(150, 160, 170))

        p = wx.Panel(self)
        s0 = sppasStaticLine(p, pos=(50, 50), size=(10, 200), orient=wx.LI_VERTICAL)
        s0.Depth = 3

        s1 = sppasStaticLine(p, pos=(60, 50), size=(200, 10), orient=wx.LI_HORIZONTAL)
        s1.PenStyle = wx.PENSTYLE_SHORT_DASH
        s1.Depth = 2

        s1 = sppasStaticLine(p, pos=(280, 50), size=(20, 100), orient=wx.LI_VERTICAL)
        s1.PenStyle = wx.PENSTYLE_DOT_DASH
        s1.Depth = 4
        s1.SetForegroundColour(wx.Colour(220, 20, 20))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, id=wx.ID_ANY, label="This is an horizontal line:"), 0, wx.EXPAND)
        sizer.Add(sppasStaticLine(self), 1, wx.EXPAND)
        sizer.Add(wx.StaticText(self, id=wx.ID_ANY, label="These are positioned/sized lines:"), 0, wx.EXPAND)
        sizer.Add(p, 3, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
