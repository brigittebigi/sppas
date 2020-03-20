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

# ---------------------------------------------------------------------------


class sppasDrawWindow(wx.Window):
    """A base window with a DC to draw some data.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="listctrl"):
        """Initialize a new sppasDrawWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param name:      Window name.

        """
        super(sppasDrawWindow, self).__init__(parent, id, pos, size, style, name)

        # Members
        self._min_width = 12
        self._min_height = 12

        # Background
        self._bgcolor = None

        # Border to draw (0=no border)
        pc = self.GetPenForegroundColour()
        self._vert_border_width = 2
        self._horiz_border_width = 2
        self._default_border_color = pc
        self._border_color = self._default_border_color
        self._border_style = wx.PENSTYLE_SOLID

        # Focus (True when mouse/keyboard is entered)
        self._has_focus = False
        self._default_focus_color = pc
        self._focus_color = self._default_focus_color
        self._focus_width = 1
        self._focus_style = wx.PENSTYLE_DOT

        # Bind the events related to our window
        self.Bind(wx.EVT_PAINT, lambda evt: self.DrawWindow())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

        # self.Bind(wx.EVT_SET_FOCUS, self.OnGainFocus)
        # self.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)

        # Setup Initial Size
        self.SetInitialSize(size)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def InitOtherEvents(self):
        """Initialize other events than paint, mouse or focus.

        Override this method in a subclass to initialize any other events that
        need to be bound.  Added so __init__ method doesn't need to be
        overridden, which is complicated with multiple inheritance.

        """
        pass

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override. Apply bg colour instead of transparency.

        :param colour: (wx.Colour) None to be transparent

        """
        self._bgcolor = colour

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        wx.Window.SetForegroundColour(self, colour)
        pc = self.GetPenForegroundColour()

        # If the bordercolor wasn't changed by the user
        if self._border_color == self._default_border_color:
            self._border_color = pc

        # If the focuscolor wasn't changed by the user
        if self._focus_color == self._default_focus_color:
            self._focus_color = pc

        self._default_border_color = pc
        self._default_focus_color = pc

    # -----------------------------------------------------------------------

    def GetDefaultAttributes(self):
        """Overridden base class virtual.

        :returns: an instance of wx.VisualAttributes.

        """
        return self.GetParent().GetClassDefaultAttributes()

    # -----------------------------------------------------------------------

    def AcceptsFocusFromKeyboard(self):
        """Can this window be given focus by tab key?"""
        # return True
        return False

    # -----------------------------------------------------------------------

    def AcceptsFocus(self):
        """Can this window be given focus by mouse click?"""
        return self.IsShown() and self.IsEnabled()

    # -----------------------------------------------------------------------

    def HasFocus(self):
        """Return whether or not we have the focus."""
        return self._has_focus

    # -----------------------------------------------------------------------

    def ShouldInheritColours(self):
        """Overridden base class virtual."""
        return True

    # ----------------------------------------------------------------------

    def Enable(self, enable=True):
        """Enable or disable the window.

        :param enable: (bool) True to enable the window.

        """
        if enable != self.IsEnabled():
            wx.Window.Enable(self, enable)
            # re-assign an appropriate border color (Pen)
            self.SetForegroundColour(self.GetForegroundColour())

    # ----------------------------------------------------------------------

    def SetFocusWidth(self, value):
        """Set the width of the focus at bottom of the button.

        :param value: (int) Focus size. Minimum is 1.

        """
        value = int(value)
        w, h = self.GetClientSize()
        if value < 0:
            return
        if value >= (w // 4):
            return
        if value >= (h // 4):
            return
        self._focus_width = value

    # -----------------------------------------------------------------------

    def GetFocusWidth(self):
        """Return the width of the focus at bottom of the button.

        :returns: (int)

        """
        return self._focus_width

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

        Pen foreground is normal if the window is enabled.

        """
        color = self.GetForegroundColour()
        if self.IsEnabled() is True:
            return color

        r, g, b = color.Red(), color.Green(), color.Blue()
        delta = 40
        if (r + g + b) > 384 and self.IsEnabled() is False:
            return wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)

        return wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------

    def GetBorderColour(self):
        """Return the colour of the border all around the button.

        :returns: (int)

        """
        return self._border_color

    # -----------------------------------------------------------------------

    def SetBorderColour(self, color):
        self._border_color = color

    # -----------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        if self._bgcolor is not None:
            color = self._bgcolor
        else:
            color = self.GetParent().GetBackgroundColour()
        r, g, b, a = color.Red(), color.Green(), color.Blue(), color.Alpha()

        delta = 15
        if (r + g + b) > 384:
            return wx.Colour(r, g, b, a).ChangeLightness(100 - delta)
        return wx.Colour(r, g, b, a).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------

    def GetFocusColour(self):
        return self._focus_color

    # -----------------------------------------------------------------------

    def SetFocusColour(self, color):
        if color == self.GetParent().GetBackgroundColour():
            return
        self._focus_color = color

    # -----------------------------------------------------------------------

    def GetBorderStyle(self):
        return self._focus_style

    # -----------------------------------------------------------------------

    def SetBorderStyle(self, style):
        if style not in [wx.PENSTYLE_SOLID, wx.PENSTYLE_LONG_DASH,
                         wx.PENSTYLE_SHORT_DASH, wx.PENSTYLE_DOT_DASH,
                         wx.PENSTYLE_HORIZONTAL_HATCH]:
            wx.LogWarning("Invalid border style {:s}.".format(str(style)))
            return
        self._border_style = style

    # -----------------------------------------------------------------------

    def GetFocusStyle(self):
        return self._focus_style

    # -----------------------------------------------------------------------

    def SetFocusStyle(self, style):
        if style not in [wx.PENSTYLE_SOLID, wx.PENSTYLE_LONG_DASH,
                         wx.PENSTYLE_SHORT_DASH, wx.PENSTYLE_DOT_DASH,
                         wx.PENSTYLE_HORIZONTAL_HATCH]:
            wx.LogWarning("Invalid focus style {:s}.".format(str(style)))
            return
        self._focus_style = style

    # -----------------------------------------------------------------------

    VertBorderWidth = property(GetVertBorderWidth, SetVertBorderWidth)
    HorizBorderWidth = property(GetHorizBorderWidth, SetHorizBorderWidth)
    BorderColour = property(GetBorderColour, SetBorderColour)
    BorderStyle = property(GetBorderStyle, SetBorderStyle)
    FocusWidth = property(GetFocusWidth, SetFocusWidth)
    FocusColour = property(GetFocusColour, SetFocusColour)
    FocusStyle = property(GetFocusStyle, SetFocusStyle)

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
                # a motion event and no mouse buttons were pressed.
                self.OnMotion(event)

            elif event.Dragging():
                # wx.LogDebug('{:s} Dragging'.format(self.GetName()))
                # motion while a button was pressed
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
        self._has_focus = True

    # -----------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        self._has_focus = False

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
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

    # -----------------------------------------------------------------------

    def OnGainFocus(self, event):
        """Handle the wx.EVT_SET_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        self._has_focus = True

    # -----------------------------------------------------------------------

    def OnLoseFocus(self, event):
        """Handle the wx.EVT_KILL_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        self._has_focus = False

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
        if self._bgcolor is None:
            if wx.Platform == '__WXMAC__':
                return wx.TRANSPARENT_BRUSH

            color = self.GetParent().GetBackgroundColour()
            return wx.Brush(color, wx.BRUSHSTYLE_TRANSPARENT)
        else:
            return wx.Brush(self._bgcolor, wx.SOLID)

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
        """Draw some parts of the button.

            1. Prepare the Drawing Context
            2. Draw the background
            3. Draw focus indicator (if state is 'HIGHLIGHT')
            4. Draw the border (if border > 0)

        :returns: dc, gc

        """
        dc, gc = self.PrepareDraw()

        self.DrawBackground(dc, gc)

        if (self._vert_border_width + self._horiz_border_width) > 0:
            self.DrawBorder(dc, gc)

        if self._has_focus is True:
            self.DrawFocusIndicator(dc, gc)

        return dc, gc

    # -----------------------------------------------------------------------

    def DrawBackground(self, dc, gc):
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

    def DrawFocusIndicator(self, dc, gc):
        """The focus indicator is a line at the bottom of the window."""
        if self._focus_width == 0:
            return

        focus_pen = wx.Pen(self._focus_color,
                           self._focus_width,
                           self._focus_style)

        w, h = self.GetClientSize()
        dc.SetPen(focus_pen)
        gc.SetPen(focus_pen)
        x = (self._vert_border_width * 2) + 2
        y = h - self._horiz_border_width - self._focus_width - 2
        dc.DrawLine(x, y, w - x - 2, y)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Test sppasBaseWindow")

        self.SetForegroundColour(wx.Colour(150, 160, 170))
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
            win = sppasDrawWindow(self, pos=(x, 10), size=(w, h))
            win.SetBorderWidth(i)
            win.SetBorderColour(wx.Colour(c, c, c))
            win.SetBorderStyle(st[i-1])
            c += 40
            x += w + 10

        # play with the focus
        x = 10
        w = 100
        h = 50
        c = 10
        for i in range(1, 6):
            win = sppasDrawWindow(self, pos=(x, 70), size=(w, h))
            win.SetBorderWidth(1)
            win.SetFocusWidth(i)
            win.SetFocusColour(wx.Colour(c, c, c))
            win.SetFocusStyle(st[i-1])
            c += 40
            x += w + 10

        win = sppasDrawWindow(self, pos=(560, 10), size=(50, 110))
        win.SetHorizBorderWidth(10)
        win.SetVertBorderWidth(2)
        win.SetBackgroundColour(wx.Colour(128, 255, 196))

