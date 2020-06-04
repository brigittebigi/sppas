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

from .basedcwindow import sppasDCWindow
from .basedcwindow import sppasWindowEvent

# ---------------------------------------------------------------------------


class WindowState(object):
    """All states of any sppasBaseWindow.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :Example:

        >>>with WindowState() as s:
        >>>    print(s.disabled)

    This class is a solution to mimic an 'Enum' but is compatible with both
    Python 2.7 and Python 3+.

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            disabled=0,
            normal=1,
            focused=2,
            selected=3
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

# ---------------------------------------------------------------------------


class sppasWindow(sppasDCWindow):
    """A base window with a DC to draw some data.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This window is implemented as "the focus follows mouse" so that when the
    mouse is over the window, it gives it the focus.

    """

    MIN_WIDTH = 24
    MIN_HEIGHT = 12

    HORIZ_MARGIN_SIZE = 6
    VERT_MARGIN_SIZE = 6

    # -----------------------------------------------------------------------

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="sppaswindow"):
        """Initialize a new sppasBaseWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param name:      Window name.

        """
        # The previous and the current states
        self._state = [WindowState().normal, WindowState().normal]

        super(sppasWindow, self).__init__(
            parent, id, pos, size, style, name)

        # Focus (True when mouse/keyboard is entered)
        pc = self.GetPenForegroundColour()
        self._default_focus_color = pc
        self._focus_color = self._default_focus_color
        self._focus_width = 1
        self._focus_style = wx.PENSTYLE_DOT

        self.Bind(wx.EVT_SET_FOCUS, self.OnGainFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override.

        :param colour: (wx.Colour)

        """
        super(sppasWindow, self).SetForegroundColour(colour)

        # If the focus color wasn't changed by the user
        pc = self.GetPenForegroundColour()
        if self._focus_color == self._default_focus_color:
            self._focus_color = pc

        self._default_focus_color = pc

    # -----------------------------------------------------------------------

    def AcceptsFocus(self):
        """Can this window be given focus by mouse click?"""
        return self.IsShown() and self.IsEnabled()

    # -----------------------------------------------------------------------

    def HasFocus(self):
        """Return whether or not we have the focus."""
        return self._state[1] == WindowState().focused

    # -----------------------------------------------------------------------

    def IsSelected(self):
        return self._state[1] == WindowState().selected

    # ----------------------------------------------------------------------

    def IsEnabled(self):
        return self._state[1] != WindowState().disabled

    # ----------------------------------------------------------------------

    def Enable(self, enable=True):
        """Overridden. Enable or disable the window.

        :param enable: (bool) True to enable the window.

        """
        enable = bool(enable)
        if enable != self.IsEnabled():
            # wx.Window.Enable(self, enable)
            if enable is False:
                self._set_state(WindowState().disabled)
            else:
                # set to the previous state
                self._set_state(self._state[0])
            # re-assign an appropriate border color (Pen)
            # self.SetForegroundColour(self.GetForegroundColour())

    # -----------------------------------------------------------------------

    def SetFocus(self):
        """Overridden. Force this window to have the focus."""
        if self._state[1] != WindowState().selected:
            self._set_state(WindowState().focused)
        super(sppasDCWindow, self).SetFocus()

    # ----------------------------------------------------------------------

    def SetFocusWidth(self, value):
        """Set the width of the focus at bottom of the window.

        :param value: (int) Focus size. Minimum is 0 ; maximum is height/4.

        """
        value = int(value)
        w, h = self.GetClientSize()
        if value < 0:
            value = 0
        if value >= (w // 4):
            value = w // 4
        if value >= (h // 4):
            value = h // 4

        self._focus_width = value

    # -----------------------------------------------------------------------

    def GetFocusWidth(self):
        """Return the width of the focus at bottom of the window.

        :returns: (int)

        """
        return self._focus_width

    # -----------------------------------------------------------------------

    def GetFocusColour(self):
        return self._focus_color

    # -----------------------------------------------------------------------

    def SetFocusColour(self, color):
        if color == self.GetParent().GetBackgroundColour():
            return
        self._focus_color = color

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

    FocusWidth = property(GetFocusWidth, SetFocusWidth)
    FocusColour = property(GetFocusColour, SetFocusColour)
    FocusStyle = property(GetFocusStyle, SetFocusStyle)

    # -----------------------------------------------------------------------

    def GetPenForegroundColour(self):
        """Get the foreground color for the pen.

        Pen foreground is normal if the window is enabled and state is normal,
        but this color is lightness if window is disabled and darkness if
        state is focused, or the contrary depending on the color.

        """
        color = self.GetForegroundColour()
        if self.IsEnabled() is True and self.HasFocus() is False:
            return color

        r, g, b = color.Red(), color.Green(), color.Blue()
        delta = 40
        if ((r + g + b) > 384 and self.IsEnabled() is False) or \
                ((r + g + b) < 384 and self.HasFocus() is True):
            return wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)

        return wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------

    def Notify(self):
        logging.debug("Notify parent of command left click")
        evt = sppasWindowEvent(wx.wxEVT_COMMAND_LEFT_CLICK, self.GetId())
        evt.SetObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    # -----------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the wx.EVT_LEFT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self.IsEnabled() is False:
            return

        self.CaptureMouse()
        self.SetFocus()
        self._set_state(WindowState().selected)

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self.IsEnabled() is False:
            return

        # Mouse was down outside of the window but is up inside.
        if self.HasCapture() is False:
            return

        # Directs all mouse input to this window
        self.ReleaseMouse()

        # If the window was down when the mouse was released...
        if self._state[1] == WindowState().selected:
            self.Notify()
            # if we haven't been destroyed by this notify...
            if self:
                self._set_state(self._state[0])

    # -----------------------------------------------------------------------

    def OnMouseEnter(self, event):
        """Handle the wx.EVT_ENTER_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self._state[1] == WindowState().normal:
            self._set_state(WindowState().focused)

    # -----------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        # mouse is leaving either while button is pressed (state is selected)
        # or not (state is focused). In both cases, we switch to normal state.
        if self._state[1] != WindowState().disabled:
            self._state[1] = WindowState().normal
            self._set_state(WindowState().normal)

    # -----------------------------------------------------------------------

    def OnGainFocus(self, event):
        """Handle the wx.EVT_SET_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        if self._state[1] == WindowState().normal:
            self._set_state(WindowState().focused)
            self.Update()

    # -----------------------------------------------------------------------

    def OnLoseFocus(self, event):
        """Handle the wx.EVT_KILL_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        if self._state[1] == WindowState().focused:
            self._set_state(self._state[0])

    # -----------------------------------------------------------------------

    def _set_state(self, state):
        """Manually set the state of the window.

        :param state: (int) one of the state values

        """
        self._state[0] = self._state[1]
        self._state[1] = state

        if state == WindowState().focused:
            self._has_focus = True
        else:
            self._has_focus = False

        if self:
            if wx.Platform == '__WXMSW__':
                self.GetParent().RefreshRect(self.GetRect(), False)
            else:
                self.Refresh()

    # -----------------------------------------------------------------------
    # Draw methods
    # -----------------------------------------------------------------------

    def Draw(self):
        """Draw normally then add focus indicator."""
        dc, gc = super(sppasWindow, self).Draw()

        if self._state[1] == WindowState().focused:
            self.DrawFocusIndicator(dc, gc)

    # -----------------------------------------------------------------------

    def GetContentRect(self):
        """Return Rect and Size to draw the content."""
        x, y, w, h = self.GetClientRect()
        x += self._vert_border_width
        y += self._horiz_border_width
        w -= (2 * self._vert_border_width)
        if self._focus_width > 0:
            h -= ((2 * self._horiz_border_width) + self._focus_width + 3)
        else:
            h -= (2 * self._horiz_border_width)

        return x, y, w, h

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Must be overridden.

        Here, we draw the active state of the window.

        """
        label = "unknown"
        with WindowState() as s:
            if self._state[1] == s.disabled:
                label = "disabled"
            elif self._state[1] == s.normal:
                label = "normal"
            elif self._state[1] == s.selected:
                label = "selected"
            elif self._state[1] == s.focused:
                label = "focused"

        x, y, w, h = self.GetContentRect()
        tw, th = self.get_text_extend(dc, gc, label)

        self.draw_label(dc, gc, label, (w - tw) // 2, (h - th) // 2)

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

    # -----------------------------------------------------------------------

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def draw_label(self, dc, gc, label, x, y):
        font = self.GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        # if wx.Platform == '__WXGTK__':
        #     dc.SetTextForeground(self.GetPenForegroundColour())
        #     dc.DrawText(label, x, y)
        # else:
        gc.SetTextForeground(self.GetPenForegroundColour())
        gc.DrawText(label, x, y)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Test sppasBaseWindow")

        bgbtn = wx.Button(self, label="BG", pos=(10, 10), size=(64, 64), name="bg_color")
        fgbtn = wx.Button(self, label="FG", pos=(100, 10), size=(64, 64), name="font_color")
        fontbtn = wx.Button(self, label="FONT", pos=(200, 10), size=(64, 64), name="font")
        self.Bind(wx.EVT_BUTTON, self.on_bg_color, bgbtn)
        self.Bind(wx.EVT_BUTTON, self.on_fg_color, fgbtn)
        self.Bind(wx.EVT_BUTTON, self.on_font, fontbtn)

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
            win = sppasWindow(self, pos=(x, 100), size=(w, h))
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
            win = sppasWindow(self, pos=(x, 170), size=(w, h))
            win.SetBorderWidth(1)
            win.SetFocusWidth(i)
            win.SetFocusColour(wx.Colour(c, c, c))
            win.SetFocusStyle(st[i-1])
            c += 40
            x += w + 10

        w1 = sppasWindow(self, pos=(10, 300), size=(50, 110), name="w1")
        w1.SetBackgroundColour(wx.Colour(128, 255, 196))
        w1.Enable(True)

        w2 = sppasWindow(self, pos=(110, 300), size=(50, 110), name="w2")
        w2.SetBackgroundColour(wx.Colour(128, 255, 196))
        w2.Enable(False)

        w3 = sppasWindow(self, pos=(210, 300), size=(50, 110), name="w3")
        w3.Enable(False)
        w3.Enable(True)

        w4 = sppasWindow(self, pos=(310, 300), size=(50, 110), name="w4")
        w4.Enable(False)
        w4.Enable(True)
        w4.Enable(False)

    # -----------------------------------------------------------------------

    def on_bg_color(self, event):
        self.SetBackgroundColour(wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250)
        ))
        self.Refresh()

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

    # -----------------------------------------------------------------------

    def on_font(self, event):
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(wx.GetApp().settings.fg_color)
        data.SetInitialFont(wx.GetApp().settings.text_font)
        dlg = wx.FontDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self.SetFont(font)
            for c in self.GetChildren():
                c.SetFont(font)

        self.Refresh()
