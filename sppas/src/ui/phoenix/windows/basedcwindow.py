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

    src.ui.phoenix.windows.basedraw.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description
    ===========

    This module implements a base class used to draw our custom wx.window,
    like for buttons, lines, etc.

"""

import wx
import random
import logging

# ---------------------------------------------------------------------------


class sppasWindowEvent(wx.PyCommandEvent):
    """Base class for an event sent when needed.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, event_type, event_id):
        """Default class constructor.

        :param event_type: the event type;
        :param event_id: the event identifier.

        """
        super(sppasWindowEvent, self).__init__(event_type, event_id)
        self.__window = None

    # ------------------------------------------------------------------------

    def SetObj(self, win):
        """Set the event object for the event.

        :param win: (wx.Window) the window object

        """
        self.__window = win

    # ------------------------------------------------------------------------

    def GetObj(self):
        """Return the object associated with this event."""
        return self.__window

    # -----------------------------------------------------------------------

    Window = property(GetObj, SetObj)

# ---------------------------------------------------------------------------


class sppasDCWindow(wx.Window):
    """A base window with a DC to draw some data.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A very basic window. Can't have the focus.
    In a previous version, the background was transparent by default but
    it is not properly supported under Windows.

    Under Windows, when changing bg color, a refresh is needed to apply it.

    """

    def __init__(self, parent, id=-1,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="dcwindow"):
        """Initialize a new sppasDCWindow instance.

        :param parent: (wx.Window) Parent window.
        :param id: (int) A value of -1 indicates a default value.
        :param pos: (wx.Point) If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size: (wx.Size) If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style: (int)
        :param name: (str) Window name.

        """
        super(sppasDCWindow, self).__init__(parent, id, pos, size, style, name)

        # Size
        self._min_width = 12
        self._min_height = 12

        try:
            settings = wx.GetApp().settings
            wx.Window.SetForegroundColour(self, settings.fg_color)
            wx.Window.SetBackgroundColour(self, settings.bg_color)
            wx.Window.SetFont(self, settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        # Border to draw (0=no border)
        pc = self.GetPenForegroundColour()
        self._vert_border_width = 2
        self._horiz_border_width = 2
        self._default_border_color = pc
        self._border_color = self._default_border_color
        self._border_style = wx.PENSTYLE_SOLID

        # Bind the events related to our window
        self.Bind(wx.EVT_PAINT, lambda evt: self.DrawWindow())
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

    # -----------------------------------------------------------------------

    def InheritsBackgroundColour(self):
        """Return False.

        Return True if this window inherits the background colour from its
        parent. But our window has a transparent background by default or
        a custom color.

        """
        try:
            s = wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # -----------------------------------------------------------------------

    def InheritsForegroundColour(self):
        """Return True if this window inherits the foreground colour."""
        try:
            s = wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # -----------------------------------------------------------------------

    def InitOtherEvents(self):
        """Initialize other events than paint, mouse or focus.

        Override this method in a subclass to initialize any other events
        that need to be bound. Added so __init__ method doesn't need to be
        overridden, which is complicated with multiple inheritance.

        """
        pass

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        wx.Window.SetForegroundColour(self, colour)

        # If the border color wasn't changed by the user
        pc = self.GetPenForegroundColour()
        if self._border_color == self._default_border_color:
            self._border_color = pc

        self._default_border_color = pc

    # -----------------------------------------------------------------------

    def GetDefaultAttributes(self):
        """Overridden base class virtual.

        We should create a customized Visual Attribute with our settings.
        But the wx.VisualAttributes are more-or-less read-only, there is no
        SetVisualAttributes or similar.

        :returns: an instance of wx.VisualAttributes.

        """
        return self.GetClassDefaultAttributes()

    # -----------------------------------------------------------------------

    def AcceptsFocusFromKeyboard(self):
        """Can this window be given focus by tab key?"""
        return False

    # -----------------------------------------------------------------------

    def AcceptsFocus(self):
        """Can this window be given focus by mouse click?"""
        return False

    # -----------------------------------------------------------------------

    def HasFocus(self):
        """Return whether or not we have the focus."""
        return False

    # -----------------------------------------------------------------------

    def ShouldInheritColours(self):
        """Overridden base class virtual."""
        try:
            s = wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # ----------------------------------------------------------------------

    def Enable(self, enable=True):
        """Enable or disable the window.

        :param enable: (bool) True to enable the window.

        """
        if enable != self.IsEnabled():
            wx.Window.Enable(self, enable)
            # re-assign an appropriate border color (Pen)
            normal_color = self.GetForegroundColour()
            self.SetForegroundColour(normal_color)

            # Refresh will also adjust alpha of the background
            self.Refresh()

    # -----------------------------------------------------------------------

    def SetBorderWidth(self, value):
        """Set the width of the border all around the window.

        :param value: (int) Border size. Not applied if not appropriate.

        """
        self.SetVertBorderWidth(value)
        self.SetHorizBorderWidth(value)

    # -----------------------------------------------------------------------

    def SetVertBorderWidth(self, value):
        """Set the width of the left/right borders.

        :param value: (int) Border size. Not applied if not appropriate.

        """
        value = int(value)
        w, h = self.GetClientSize()
        if value < 0:
            # wx.LogWarning("Invalid border width {:d} (negative value).".format(value))
            return
        if w > 0 and value >= (w // 2):
            # wx.LogWarning("Invalid border width {:d} (highter than width {:d}).".format(value, w))
            return
        self._vert_border_width = value

    # -----------------------------------------------------------------------

    def SetHorizBorderWidth(self, value):
        """Set the width of the top/bottom borders.

        :param value: (int) Border size. Not applied if not appropriate.

        """
        value = int(value)
        w, h = self.GetClientSize()
        if value < 0:
            # wx.LogWarning("Invalid border width {:d} (negative value).".format(value))
            return
        if h > 0 and value >= (h // 2):
            # wx.LogWarning("Invalid border width {:d} (highter than height {:d}).".format(value, h))
            return
        self._horiz_border_width = value

    # -----------------------------------------------------------------------

    def GetVertBorderWidth(self):
        """Return the width of left/right borders.

        :returns: (int)

        """
        return self._horiz_border_width

    # -----------------------------------------------------------------------

    def GetHorizBorderWidth(self):
        """Return the width of top/bottom borders.

        :returns: (int)

        """
        return self._horiz_border_width

    # -----------------------------------------------------------------------

    def GetPenForegroundColour(self):
        """Get the foreground color for the pen.

        Pen foreground is the normal foreground if the window is enabled but
        lightness and transparency are modified if the window is disabled.

        """
        normal_color = self.GetForegroundColour()
        if self.IsEnabled() is True:
            return normal_color

        r, g, b = normal_color.Red(), normal_color.Green(), normal_color.Blue()
        a = normal_color.Alpha()
        if a > 128:
            a = max(56, a // 2)
        delta = 40
        if (r + g + b) > 384 and self.IsEnabled() is False:
            return wx.Colour(r, g, b, a).ChangeLightness(100 - delta)

        return wx.Colour(r, g, b, a).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------

    def GetBorderColour(self):
        """Return the colour of the border all around the window.

        :returns: (wx.Color)

        """
        return self._border_color

    # -----------------------------------------------------------------------

    def SetBorderColour(self, color):
        """Set the color of the border all around the window.

        :param color: (wx.Color)

        """
        self._border_color = color

    # -----------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        """Return a background color with a different lightness."""
        color = self.GetBackgroundColour()
        r, g, b, a = color.Red(), color.Green(), color.Blue(), color.Alpha()
        if a > 128:
            a = max(64, a // 2)

        delta = 20
        if (r + g + b) > 384:
            return wx.Colour(r, g, b, a).ChangeLightness(100 - delta)

        return wx.Colour(r, g, b, a).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------

    def GetBorderStyle(self):
        """Return the pen style of the borders."""
        return self._border_style

    # -----------------------------------------------------------------------

    def SetBorderStyle(self, style):
        """Set the pen style for the borders.

        :param style: (wx.PENSTYLE_*)

        """
        if style not in [wx.PENSTYLE_SOLID, wx.PENSTYLE_LONG_DASH,
                         wx.PENSTYLE_SHORT_DASH, wx.PENSTYLE_DOT_DASH,
                         wx.PENSTYLE_HORIZONTAL_HATCH]:
            wx.LogWarning("Invalid border style {:s}.".format(str(style)))
            return

        self._border_style = style

    # -----------------------------------------------------------------------

    VertBorderWidth = property(GetVertBorderWidth, SetVertBorderWidth)
    HorizBorderWidth = property(GetHorizBorderWidth, SetHorizBorderWidth)
    BorderColour = property(GetBorderColour, SetBorderColour)
    BorderStyle = property(GetBorderStyle, SetBorderStyle)

    # -----------------------------------------------------------------------
    # Callbacks to mouse events
    # -----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """Handle the wx.EVT_MOUSE_EVENTS event.

        Do not accept the event if the window is disabled.

        """
        if self.IsEnabled() is True:

            if event.Entering():
                # wx.LogDebug('{:s} Entering'.format(self.GetName()))
                self.OnMouseEnter(event)

            elif event.Leaving():
                # wx.LogDebug('{:s} Leaving'.format(self.GetName()))
                self.OnMouseLeave(event)

            elif event.LeftDown():
                # wx.LogDebug('{:s} LeftDown'.format(self.GetName()))
                self.OnMouseLeftDown(event)

            elif event.LeftUp():
                # wx.LogDebug('{:s} LeftUp'.format(self.GetName()))
                self.OnMouseLeftUp(event)

            elif event.Moving():
                # wx.LogDebug('{:s} Moving'.format(self.GetName()))
                # a motion event and no mouse windows were pressed.
                self.OnMotion(event)

            elif event.Dragging():
                # wx.LogDebug('{:s} Dragging'.format(self.GetName()))
                # motion while a window was pressed
                self.OnDragging(event)

            elif event.ButtonDClick():
                # wx.LogDebug('{:s} ButtonDClick'.format(self.GetName()))
                self.OnMouseDoubleClick(event)

            elif event.RightDown():
                # wx.LogDebug('{:s} RightDown'.format(self.GetName()))
                self.OnMouseRightDown(event)

            elif event.RightUp():
                # wx.LogDebug('{:s} RightUp'.format(self.GetName()))
                self.OnMouseRightUp(event)

            else:
                # wx.LogDebug('{:s} Other mouse event'.format(self.GetName()))
                pass

        event.Skip()

    # -----------------------------------------------------------------------

    def OnMouseRightDown(self, event):
        """Handle the wx.EVT_RIGHT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnMouseRightUp(self, event):
        """Handle the wx.EVT_RIGHT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the wx.EVT_LEFT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnMotion(self, event):
        """Handle the wx.EVT_MOTION event.

        To be overridden.

        :param event: a :class:wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnDragging(self, event):
        """Handle the wx.EVT_MOTION event.

        To be overridden.

        :param event: a :class:wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnMouseEnter(self, event):
        """Handle the wx.EVT_ENTER_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnMouseDoubleClick(self, event):
        """Handle the wx.EVT_LEFT_DCLICK or wx.EVT_RIGHT_DCLICK event.

        :param event: a wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------
    # Other callbacks
    # -----------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a wx.SizeEvent event to be processed.

        """
        event.Skip()
        self.Refresh()

    # -----------------------------------------------------------------------

    def OnErase(self, evt):
        """Trap the erase event to keep the background transparent on Windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

    # -----------------------------------------------------------------------

    def OnGainFocus(self, event):
        """Handle the wx.EVT_SET_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnLoseFocus(self, event):
        """Handle the wx.EVT_KILL_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------
    # Design
    # -----------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        self.SetMinSize(wx.Size(self._min_width, self._min_height))
        if size is None:
            size = wx.DefaultSize

        (w, h) = size
        if w < self._min_width:
            w = self._min_width
        if h < self._min_height:
            h = self._min_height

        wx.Window.SetInitialSize(self, wx.Size(w, h))

    SetBestSize = SetInitialSize

    # -----------------------------------------------------------------------

    def GetBackgroundBrush(self):
        """Get the brush for drawing the background of the window.

        :returns: (wx.Brush)

        """
        bg_color = self.GetBackgroundColour()

        if self.IsEnabled() is True:
            color = bg_color

        else:
            # Wont have any effect under Windows (alpha is ignored!)
            r = bg_color.Red()
            g = bg_color.Green()
            b = bg_color.Blue()
            a = bg_color.Alpha()
            if a > 128:
                a = max(56, a // 2)
            color = wx.Colour(r, g, b, a)

        return wx.Brush(color, wx.BRUSHSTYLE_SOLID)

    # -----------------------------------------------------------------------
    # Draw methods (private)
    # -----------------------------------------------------------------------

    def PrepareDraw(self):
        """Prepare the DC to draw the window.

        :returns: (tuple) dc, gc

        """
        # Create the Graphic Context
        dc = wx.AutoBufferedPaintDCFactory(self)
        gc = wx.GCDC(dc)

        # In any case, the brush is transparent
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBackgroundMode(wx.TRANSPARENT)

        # Font
        gc.SetFont(self.GetFont())
        dc.SetFont(self.GetFont())

        return dc, gc

    # -----------------------------------------------------------------------

    def DrawWindow(self):
        """Draw the Window after the WX_EVT_PAINT event. """
        # Get the actual client size of ourselves
        width, height = self.GetClientSize()
        if not width or not height:
            # Nothing to do, we still don't have dimensions!
            return

        self.Draw()

    # -----------------------------------------------------------------------

    def Draw(self):
        """Draw some parts of the window.

            1. Prepare the Drawing Context
            2. Draw the background
            3. Draw the border (if border > 0)
            4. Draw the content

        :returns: dc, gc

        """
        dc, gc = self.PrepareDraw()
        self.DrawBackground(dc, gc)
        if (self._vert_border_width + self._horiz_border_width) > 0:
            self.DrawBorder(dc, gc)
        self.DrawContent(dc, gc)

        return dc, gc

    # -----------------------------------------------------------------------

    def DrawBackground(self, dc, gc):
        """Draw the background with a color or transparent."""
        w, h = self.GetClientSize()

        brush = self.GetBackgroundBrush()
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(brush)
        dc.DrawRoundedRectangle(
            self._vert_border_width,
            self._horiz_border_width,
            w - (2 * self._vert_border_width),
            h - (2 * self._horiz_border_width),
            (self._vert_border_width + self._horiz_border_width) // 2)

    # -----------------------------------------------------------------------

    def DrawBorder(self, dc, gc):
        w, h = self.GetClientSize()
        r = self._border_color.Red()
        g = self._border_color.Green()
        b = self._border_color.Blue()
        a = self._border_color.Alpha()

        for i in reversed(range(self._horiz_border_width)):
            # gradient border color, using transparency
            alpha = max(a - (i * 25), 0)
            pen = wx.Pen(wx.Colour(r, g, b, alpha), 1, self._border_style)
            dc.SetPen(pen)

            # upper line
            dc.DrawLine(self._vert_border_width - i, i, w - self._vert_border_width + i, i)
            # bottom line
            dc.DrawLine(self._vert_border_width - i, h - i - 1, w - self._vert_border_width + i, h - i - 1)

        for i in reversed(range(self._vert_border_width)):
            # gradient border color, using transparency
            alpha = max(a - (i * 25), 0)
            pen = wx.Pen(wx.Colour(r, g, b, alpha), 1, self._border_style)
            dc.SetPen(pen)

            # left line
            dc.DrawLine(i, self._horiz_border_width - i, i, h - self._horiz_border_width + i)
            # right line
            dc.DrawLine(w - i - 1, self._horiz_border_width - i, w - i - 1, h - self._horiz_border_width + i)

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """To be overridden."""
        pass

    # -----------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def DrawLabel(self, label, dc, gc, x, y):
        font = self.GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        color = self.GetPenForegroundColour()
        #if wx.Platform == '__WXGTK__':
        dc.SetTextForeground(color)
        dc.DrawText(label, x, y)
        #else:
        #    gc.SetTextForeground(color)
        #    gc.DrawText(label, x, y)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Test sppasBaseWindow")
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)

        bgpbtn = wx.Button(self, label="BG-panel", pos=(10, 10), size=(64, 64), name="bgp_color")
        bgbbtn = wx.Button(self, label="BG-buttons", pos=(110, 10), size=(64, 64), name="bgb_color")
        fgbtn = wx.Button(self, label="FG", pos=(210, 10), size=(64, 64), name="font_color")
        self.Bind(wx.EVT_BUTTON, self.on_bgp_color, bgpbtn)
        self.Bind(wx.EVT_BUTTON, self.on_bgb_color, bgbbtn)
        self.Bind(wx.EVT_BUTTON, self.on_fg_color, fgbtn)

        st = [wx.PENSTYLE_SHORT_DASH,
              wx.PENSTYLE_LONG_DASH,
              wx.PENSTYLE_DOT_DASH,
              wx.PENSTYLE_SOLID,
              wx.PENSTYLE_HORIZONTAL_HATCH]

        # play with the border
        x = 10
        w = 100
        h = 50
        c = 10
        for i in range(1, 6):
            win = sppasDCWindow(self, pos=(x, 100), size=(w, h))
            win.SetBorderWidth(i)
            win.SetBorderColour(wx.Colour(c, c, c))
            win.SetBorderStyle(st[i-1])
            c += 40
            x += w + 10

        w1 = sppasDCWindow(self, pos=(10, 300), size=(50, 110), name="w1")
        w1.SetBackgroundColour(wx.Colour(128, 255, 196))
        w1.Enable(True)

        w2 = sppasDCWindow(self, pos=(110, 300), size=(50, 110), name="w2")
        w2.SetBackgroundColour(wx.Colour(128, 255, 196))
        w2.Enable(False)

        w3 = sppasDCWindow(self, pos=(210, 300), size=(50, 110), name="w3")
        w3.Enable(False)
        w3.Enable(True)

        w4 = sppasDCWindow(self, pos=(310, 300), size=(50, 110), name="w4")
        w4.Enable(False)
        w4.Enable(True)
        w4.Enable(False)

    # -----------------------------------------------------------------------

    def on_bgp_color(self, event):
        """Change BG color of the panel. It shouldn't change bg of buttons."""
        self.SetBackgroundColour(wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250)
        ))
        self.Refresh()

    # -----------------------------------------------------------------------

    def on_bgb_color(self, event):
        """Change BG color of the buttons. A refresh is needed."""
        for child in self.GetChildren():
            if isinstance(child, sppasDCWindow):
                child.SetBackgroundColour(wx.Colour(
                    random.randint(10, 250),
                    random.randint(10, 250),
                    random.randint(10, 250)
                    ))
                child.Refresh()

    # -----------------------------------------------------------------------

    def on_fg_color(self, event):
        color = wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250))
        self.SetForegroundColour(color)
        for c in self.GetChildren():
            c.SetForegroundColour(color)
        self.Refresh()
