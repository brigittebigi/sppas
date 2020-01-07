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


    Sample usage:
    ============

        import wx
        import buttons

        class appFrame(wx.Frame):
            def __init__(self, parent, title):

                wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(400, 300))
                panel = wx.Panel(self)
                line = sppasStaticLine(panel, -1, pos=(50, 50), size=(128, 32))

        app = wx.App()
        frame = appFrame(None, 'Line Test')
        frame.Show()
        app.MainLoop()

"""

import wx

# ---------------------------------------------------------------------------


class sppasStaticLine(wx.Window):
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

        self.__orient = orient
        self.__depth = 2
        self.__penstyle = wx.PENSTYLE_SOLID

        # Setup Initial Size
        self.InheritAttributes()
        self.SetInitialSize(size)

        # Bind the events related to our window
        self.Bind(wx.EVT_PAINT, lambda evt: self.DrawLine())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    # -----------------------------------------------------------------------

    def GetDefaultAttributes(self):
        """Overridden base class virtual.

        :returns: an instance of wx.VisualAttributes.

        """
        return self.GetParent().GetClassDefaultAttributes()

    # ------------------------------------------------------------------------

    def ShouldInheritColours(self):
        """Overridden base class virtual.

        """
        return True

    # ------------------------------------------------------------------------

    def GetPenStyle(self):
        return self.__penstyle

    # -----------------------------------------------------------------------

    def SetPenStyle(self, style):
        if style not in [wx.PENSTYLE_SOLID, wx.PENSTYLE_LONG_DASH,
                         wx.PENSTYLE_SHORT_DASH, wx.PENSTYLE_DOT_DASH,
                         wx.PENSTYLE_HORIZONTAL_HATCH]:
            return

        self.__penstyle = style

    # -----------------------------------------------------------------------

    def GetDepth(self):
        """Return the width of the border all around the button.

        :returns: (int)

        """
        return self.__depth

    # -----------------------------------------------------------------------

    def SetDepth(self, value):
        """Set the width of the border all around the button.

        :param value: (int) Border size. Not applied if not appropriate.

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

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a wx.SizeEvent event to be processed.

        """
        event.Skip()
        self.Refresh()

    # ------------------------------------------------------------------------

    def OnErase(self, evt):
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

    # ------------------------------------------------------------------------
    # Design
    # ------------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        if self.__orient == wx.LI_VERTICAL:
            self.SetMinSize(wx.Size(-1, 4))
        elif self.__orient == wx.LI_VERTICAL:
            self.SetMinSize(wx.Size(4, -1))
        else:
            self.SetMinSize(wx.Size(4, 4))

        if size is None:
            size = wx.DefaultSize

        wx.Window.SetInitialSize(self, wx.Size(size))

    SetBestSize = SetInitialSize

    # ------------------------------------------------------------------------

    def GetBackgroundBrush(self):
        """Get the brush for drawing the background of the button.

        :returns: (wx.Brush)

        """
        color = self.GetParent().GetBackgroundColour()

        if wx.Platform == '__WXMAC__':
            return wx.TRANSPARENT_BRUSH

        brush = wx.Brush(color, wx.SOLID)
        my_attr = self.GetDefaultAttributes()
        p_attr = self.GetParent().GetDefaultAttributes()
        my_def = color == my_attr.colBg
        p_def = self.GetParent().GetBackgroundColour() == p_attr.colBg
        if my_def and not p_def:
            color = self.GetParent().GetBackgroundColour()
            brush = wx.Brush(color, wx.SOLID)

        return brush

    # ------------------------------------------------------------------------
    # Draw methods (private)
    # ------------------------------------------------------------------------

    def PrepareDraw(self):
        """Prepare the DC to draw the button.

        :returns: (tuple) dc, gc

        """
        # Create the Graphic Context
        dc = wx.AutoBufferedPaintDCFactory(self)
        gc = wx.GCDC(dc)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()

        # In any case, the brush is transparent
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBackgroundMode(wx.TRANSPARENT)
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            # The background needs some help to look transparent on
            # Gtk and Windows
            gc.SetBackground(self.GetBackgroundBrush())
            gc.Clear()

        return dc, gc

    # ------------------------------------------------------------------------

    def DrawLine(self):
        """Draw the line after the WX_EVT_PAINT event.

        """
        # Get the actual client size of ourselves
        width, height = self.GetClientSize()
        if not width or not height:
            # Nothing to do, we still don't have dimensions!
            return

        dc, gc = self.PrepareDraw()
        w, h = self.GetClientSize()

        brush = self.GetBackgroundBrush()
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(brush)
        dc.DrawRectangle(0, 0, w, h)

        pen = wx.Pen(self.GetForegroundColour(),
                     self.__depth,
                     self.__penstyle)
        dc.SetPen(pen)
        gc.SetPen(pen)

        if self.__orient == wx.LI_HORIZONTAL:
            dc.DrawLine(0,
                        (h - self.__depth) // 2,
                        w,
                        (h - self.__depth) // 2)

        if self.__orient == wx.LI_VERTICAL:
            dc.DrawLine((w - self.__depth) // 2,
                        0,
                        (w - self.__depth) // 2,
                        h)

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
