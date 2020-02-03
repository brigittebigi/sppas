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

    src.ui.phoenix.windows.button.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description
    ===========

    This module implements various forms of generic buttons, meaning that
    they are not built on native controls but are self-drawn.

    They act like normal buttons.


    Sample usage:
    ============

        import wx
        import buttons

        class appFrame(wx.Frame):
            def __init__(self, parent, title):

                wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(400, 300))
                panel = wx.Panel(self)
                btn = buttons.BaseButton(panel, -1, pos=(50, 50), size=(128, 32))

        app = wx.App()
        frame = appFrame(None, 'Button Test')
        frame.Show()
        app.MainLoop()

"""

import random
import wx
import wx.lib.scrolledpanel as sc
import wx.lib.newevent
from wx.lib.buttons import GenBitmapTextButton, GenButton, GenBitmapButton

from ..tools import sppasSwissKnife
from .image import ColorizeImage

# ---------------------------------------------------------------------------

DEFAULT_STYLE = wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS

# ---------------------------------------------------------------------------


class sppasTextButton(GenButton):
    """Create a simple text button. Inherited from the wx.Button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent, label, name):
        super(sppasTextButton, self).__init__(
           parent,
           wx.ID_ANY,
           label,
           style=DEFAULT_STYLE,
           name=name)

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

# ---------------------------------------------------------------------------


class sppasBitmapTextButton(GenBitmapTextButton):
    """Create a simple text button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap and text. A tooltip can optionally be added.

    >>> button = sppasBitmapTextButton(None, "Exit", "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, label, name, style=DEFAULT_STYLE):
        btn_height = int(parent.GetSize()[1])
        super(sppasBitmapTextButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=btn_height),
            label=" "+label+" ",
            style=style,
            name=name
        )

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        current = self.GetForegroundColour()
        try:
            bmp = self.GetBitmapLabel()
            img = bmp.ConvertToImage()
            ColorizeImage(img, current, colour)
            self.SetBitmapLabel(wx.Bitmap(img))
        except:
            wx.LogDebug('SetForegroundColour not applied to image'
                        'for button {:s}'.format(self.GetName()))

        GenBitmapTextButton.SetForegroundColour(self, colour)

# ---------------------------------------------------------------------------


class sppasBitmapButton(GenBitmapButton):
    """Create a simple bitmap button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Create a button with bitmap. A tooltip can optionally be added.

    >>> button = sppasBitmapButton(None, "exit")
    >>> button.SetToolTipString("Quit the application")

    """

    def __init__(self, parent, name, style=DEFAULT_STYLE, height=None):

        if height is None:
            height = int(parent.GetSize()[1])
        super(sppasBitmapButton, self).__init__(
            parent,
            id=wx.NewId(),
            bitmap=sppasSwissKnife.get_bmp_icon(name, height=height),
            style=style,
            name=name
        )

        self.SetInitialSize()
        self.Enable(True)
        self.SetBezelWidth(0)
        self.SetUseFocusIndicator(False)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to the image.

        :param colour: (wx.Colour)

        """
        try:
            bmp = self.GetBitmapLabel()
            img = bmp.ConvertToImage()
            current = self.GetForegroundColour()
            ColorizeImage(img, current, colour)
            self.SetBitmapLabel(wx.Bitmap(img))
        except:
            wx.LogDebug('SetForegroundColour not applied to image'
                        'for button {:s}'.format(self.GetName()))

        GenBitmapButton.SetForegroundColour(self, colour)

# ---------------------------------------------------------------------------
# Custom buttons
# ---------------------------------------------------------------------------


class ButtonEvent(wx.PyCommandEvent):
    """Base class for an event sent when the button is activated."""

    def __init__(self, eventType, eventId):
        """Default class constructor.

        :param eventType: the event type;
        :param eventId: the event identifier.

        """
        super(ButtonEvent, self).__init__(eventType, eventId)
        self.__button = None

    # ------------------------------------------------------------------------

    def SetButtonObj(self, btn):
        """Set the event object for the event.

        :param `btn`: the button object, an instance of L{FileButton}.

        """
        self.__button = btn

    # ------------------------------------------------------------------------

    def GetButtonObj(self):
        """Return the object associated with this event."""
        return self.__button

    # -----------------------------------------------------------------------

    Button = property(GetButtonObj, SetButtonObj)


# ---------------------------------------------------------------------------


class ToggleButtonEvent(ButtonEvent):
    """Base class for an event sent when the toggle button is activated."""

    def __init__(self, eventType, eventId):
        """Default class constructor.

        :param eventType: the event type;
        :param eventId: the event identifier.

        """
        super(ToggleButtonEvent, self).__init__(eventType, eventId)
        self.__isdown = False

    # -----------------------------------------------------------------------

    def SetIsDown(self, isDown):
        """Set the button toggle status as 'down' or 'up'.

        :param isDown: (bool) True if the button is clicked, False otherwise.

        """
        self.__isdown = bool(isDown)

    # -----------------------------------------------------------------------

    def GetIsDown(self):
        """Return the button toggle status as ``True`` if the button is down.

        :returns: (bool)

        """
        return self.__isdown


# ---------------------------------------------------------------------------


class BaseButton(wx.Window):
    """BaseButton is a custom type of window to represent a button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    # Button States
    NORMAL = 0
    PRESSED = 1
    HIGHLIGHT = 2

    # Button Min Size
    MIN_WIDTH = 32
    MIN_HEIGHT = 32

    # -----------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: (wx.Window) parent window. Must not be ``None``;
        :param id: (int) window identifier. A value of -1 indicates a default value;
        :param pos: the control position. A value of (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython, depending on
         platform;
        :param size: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param name: (str) Name of the button.

        """
        super(BaseButton, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        # Preceding state and current one
        self._state = [BaseButton.NORMAL, BaseButton.NORMAL]

        # Border width to draw (0=no border)
        self._borderwidth = 2
        self._default_bordercolor = self.GetPenForegroundColour()
        self._bordercolor = self._default_bordercolor
        self._borderstyle = wx.PENSTYLE_SOLID

        # Focus (True when mouse/keyboard is entered)
        self._hasfocus = False
        self._focuscolor = self.GetPenForegroundColour()
        self._focuswidth = 1
        self._focusstyle = wx.PENSTYLE_DOT

        # Setup Initial Size
        self.InheritAttributes()
        self.SetInitialSize(size)

        # Bind the events related to our window
        self.Bind(wx.EVT_PAINT, lambda evt: self.DrawButton())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

        self.Bind(wx.EVT_SET_FOCUS, self.OnGainFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)

        # Allow sub-classes to bind other events
        self.InitOtherEvents()

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        wx.Window.SetForegroundColour(self, colour)

        # If the bordercolor wasn't changed by the user
        if self._bordercolor == self._default_bordercolor:
            self._bordercolor = self.GetPenForegroundColour()

        self._default_bordercolor = self.GetPenForegroundColour()

    # -----------------------------------------------------------------------

    def InitOtherEvents(self):
        """Initialize other events than paint, mouse or focus.

        Override this method in a subclass to initialize any other events that
        need to be bound.  Added so __init__ method doesn't need to be
        overridden, which is complicated with multiple inheritance.

        """
        pass

    # -----------------------------------------------------------------------

    def GetDefaultAttributes(self):
        """Overridden base class virtual.

        By default we should use the same font/colour attributes as the
        native class wx.Button, but for this custom button we use the
        parent ones.

        :returns: an instance of wx.VisualAttributes.

        """
        return self.GetParent().GetClassDefaultAttributes()

    # -----------------------------------------------------------------------

    def AcceptsFocusFromKeyboard(self):
        """Can this window be given focus by tab key?"""
        return True

    # -----------------------------------------------------------------------

    def AcceptsFocus(self):
        """Can this window be given focus by mouse click?"""
        return self.IsShown() and self.IsEnabled()

    # -----------------------------------------------------------------------

    def HasFocus(self):
        """Return whether or not we have the focus."""
        return self._hasfocus

    # -----------------------------------------------------------------------

    def SetFocus(self):
        """Overridden. Force this button to have the focus."""
        if self._state[1] != BaseButton.PRESSED:
            self._set_state(BaseButton.HIGHLIGHT)
        super(BaseButton, self).SetFocus()

    # -----------------------------------------------------------------------

    def ShouldInheritColours(self):
        """Overridden base class virtual.

        Buttons usually don't inherit the parent's colours but we do it. We
        are customizing!!!

        """
        return True

    # ----------------------------------------------------------------------

    def Enable(self, enable=True):
        """Enable or disable the button.

        :param enable: (bool) True to enable the button.

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
        self._focuswidth = value

    # -----------------------------------------------------------------------

    def GetFocusWidth(self):
        """Return the width of the focus at bottom of the button.

        :returns: (int)

        """
        return self._focuswidth

    # -----------------------------------------------------------------------

    def SetBorderWidth(self, value):
        """Set the width of the border all around the button.

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
        if h > 0 and value >= (h // 2):
            # wx.LogWarning("Invalid border width {:d} (highter than height {:d}).".format(value, h))
            return
        self._borderwidth = value

    # -----------------------------------------------------------------------

    def GetBorderWidth(self):
        """Return the width of the border all around the button.

        :returns: (int)

        """
        return self._borderwidth

    # -----------------------------------------------------------------------

    def GetPenForegroundColour(self):
        """Get the foreground color for the pen.

        Pen foreground is normal if the button is enabled and state is normal,
        but this color is lightness if button is disabled and darkness if
        state is highlighted, or the contrary depending on the color.

        """
        color = self.GetForegroundColour()
        if self.IsEnabled() is True and self._state != BaseButton.HIGHLIGHT:
            return color

        r, g, b = color.Red(), color.Green(), color.Blue()
        delta = 40
        if ((r + g + b) > 384 and self.IsEnabled() is False) or \
                ((r + g + b) < 384 and self._state == BaseButton.HIGHLIGHT):
            return wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)

        return wx.Colour(r, g, b, 50).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------

    def GetBorderColour(self):
        """Return the colour of the border all around the button.

        :returns: (int)

        """
        return self._bordercolor

    def SetBorderColour(self, color):
        self._bordercolor = color

    # -----------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        color = self.GetParent().GetBackgroundColour()
        r, g, b = color.Red(), color.Green(), color.Blue()
        delta = 20
        if (r + g + b) > 384:
            return wx.Colour(r, g, b, 128).ChangeLightness(100 - delta)
        return wx.Colour(r, g, b, 128).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------

    def GetFocusColour(self):
        return self._focuscolor

    def SetFocusColour(self, color):
        if color == self.GetParent().GetBackgroundColour():
            return
        self._focuscolor = color

    # -----------------------------------------------------------------------

    def GetBorderStyle(self):
        return self._focusstyle

    def SetBorderStyle(self, style):
        if style not in [wx.PENSTYLE_SOLID, wx.PENSTYLE_LONG_DASH,
                         wx.PENSTYLE_SHORT_DASH, wx.PENSTYLE_DOT_DASH,
                         wx.PENSTYLE_HORIZONTAL_HATCH]:
            wx.LogWarning("Invalid border style {:s}.".format(str(style)))
            return
        self._borderstyle = style

    # -----------------------------------------------------------------------

    def GetFocusStyle(self):
        return self._focusstyle

    def SetFocusStyle(self, style):
        if style not in [wx.PENSTYLE_SOLID, wx.PENSTYLE_LONG_DASH,
                         wx.PENSTYLE_SHORT_DASH, wx.PENSTYLE_DOT_DASH,
                         wx.PENSTYLE_HORIZONTAL_HATCH]:
            wx.LogWarning("Invalid focus style {:s}.".format(str(style)))
            return
        self._focusstyle = style

    # -----------------------------------------------------------------------

    BorderWidth = property(GetBorderWidth, SetBorderWidth)
    BorderColour = property(GetBorderColour, SetBorderColour)
    BorderStyle = property(GetBorderStyle, SetBorderStyle)
    FocusWidth = property(GetFocusWidth, SetFocusWidth)
    FocusColour = property(GetFocusColour, SetFocusColour)
    FocusStyle = property(GetFocusStyle, SetFocusStyle)

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a wx.SizeEvent event to be processed.

        """
        event.Skip()
        self.Refresh()

    # -----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """Handle the wx.EVT_MOUSE_EVENTS event.

        Do not accept the event if the button is disabled.

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
        if not self.IsEnabled():
            return

        self._set_state(BaseButton.PRESSED)
        self.CaptureMouse()
        self.SetFocus()
        self.Refresh()

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if not self.IsEnabled():
            return

        if not self.HasCapture():
            return

        s = self._state[0]
        self.ReleaseMouse()
        # If the button was down when the mouse was released...
        if self._state[1] == BaseButton.PRESSED:
            self.Notify()
            # if we haven't been destroyed by this notify...
            if self:
                self._set_state(s)

    # -----------------------------------------------------------------------

    def OnMotion(self, event):
        """Handle the wx.EVT_MOTION event.

        To be overriden.

        :param event: a :class:wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnDragging(self, event):
        """Handle the wx.EVT_MOTION event.

        To be overriden.

        :param event: a :class:wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnMouseEnter(self, event):
        """Handle the wx.EVT_ENTER_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self._state[1] == BaseButton.NORMAL:
            self._set_state(BaseButton.HIGHLIGHT)
            self.Refresh()

    # -----------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        self._set_state(BaseButton.NORMAL)
        self.Refresh()

    # -----------------------------------------------------------------------

    def OnGainFocus(self, event):
        """Handle the wx.EVT_SET_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        if self._state[1] == BaseButton.NORMAL:
            self._set_state(BaseButton.HIGHLIGHT)
            self.Refresh()
            self.Update()

    # -----------------------------------------------------------------------

    def OnLoseFocus(self, event):
        """Handle the wx.EVT_KILL_FOCUS event.

        :param event: a wx.FocusEvent event to be processed.

        """
        if self._state[1] == BaseButton.HIGHLIGHT:
            self._set_state(self._state[0])
            self.Refresh()

    # -----------------------------------------------------------------------

    def OnKeyDown(self, event):
        """Handle the wx.EVT_KEY_DOWN event.

        :param event: a wx.KeyEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnKeyUp(self, event):
        """Handle the wx.EVT_KEY_UP event.

        :param event: a wx.KeyEvent event to be processed.

        """
        if event.GetKeyCode() == wx.WXK_SPACE:
            self.Notify()
            self._set_state(BaseButton.HIGHLIGHT)

        elif event.GetKeyCode() == wx.WXK_ENTER:
            self.Notify()
            self._set_state(BaseButton.PRESSED)
            wx.CallLater(100, self._set_state, BaseButton.HIGHLIGHT)

    # -----------------------------------------------------------------------

    def OnMouseDoubleClick(self, event):
        """Handle the wx.EVT_LEFT_DCLICK or wx.EVT_RIGHT_DCLICK event.

        :param event: a wx.MouseEvent event to be processed.

        """
        pass

    # -----------------------------------------------------------------------

    def OnErase(self, evt):
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

    # -----------------------------------------------------------------------
    # Design
    # -----------------------------------------------------------------------

    def SetInitialSize(self, size=None):
        """Calculate and set a good size.

        :param size: an instance of wx.Size.

        """
        self.SetMinSize(wx.Size(BaseButton.MIN_WIDTH, BaseButton.MIN_HEIGHT))
        if size is None:
            size = wx.DefaultSize

        (w, h) = size
        if w < BaseButton.MIN_WIDTH:
            w = BaseButton.MIN_WIDTH
        if h < BaseButton.MIN_HEIGHT:
            h = BaseButton.MIN_HEIGHT

        wx.Window.SetInitialSize(self, wx.Size(w, h))

    SetBestSize = SetInitialSize

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_BUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    # -----------------------------------------------------------------------

    def GetBackgroundBrush(self, dc):
        """Get the brush for drawing the background of the button.

        :returns: (wx.Brush)

        """
        c = self.GetParent().GetBackgroundColour()
        color = wx.Colour(c.Red(), c.Green(), c.Blue(), alpha=128)
        state = self._state[1]

        if state != BaseButton.PRESSED:
            return wx.Brush(color, wx.BRUSHSTYLE_TRANSPARENT)
            """
            if wx.Platform == '__WXMAC__':
                return wx.TRANSPARENT_BRUSH

            brush = wx.Brush(color, wx.BRUSHSTYLE_TRANSPARENT)
            my_attr = self.GetDefaultAttributes()
            p_attr = self.GetParent().GetDefaultAttributes()
            my_def = color == my_attr.colBg
            p_def = self.GetParent().GetBackgroundColour() == p_attr.colBg
            if my_def and not p_def:
                color = self.GetParent().GetBackgroundColour()
                brush = wx.Brush(color, wx.BRUSHSTYLE_TRANSPARENT)
            """
        else:
            # this line assumes that a pressed button should be highlighted with
            # a solid colour even if the background is supposed to be transparent
            brush = wx.Brush(self.GetHighlightedBackgroundColour(), wx.SOLID)

        return brush

    # -----------------------------------------------------------------------
    # Draw methods (private)
    # -----------------------------------------------------------------------

    def PrepareDraw(self):
        """Prepare the DC to draw the button.

        :returns: (tuple) dc, gc

        """
        # Create the Graphic Context
        dc = wx.AutoBufferedPaintDCFactory(self)
        gc = wx.GCDC(dc)
        # dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        # dc.Clear()

        # In any case, the brush is transparent
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBackgroundMode(wx.TRANSPARENT)
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            # The background needs some help to look transparent on
            # Gtk and Windows
            gc.SetBackground(self.GetBackgroundBrush(gc))
            gc.Clear()

        # Font
        gc.SetFont(self.GetFont())
        dc.SetFont(self.GetFont())

        return dc, gc

    # -----------------------------------------------------------------------

    def DrawButton(self):
        """Draw the button after the WX_EVT_PAINT event.

        """
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

        if self._state[1] == BaseButton.HIGHLIGHT:
            self.DrawFocusIndicator(dc, gc)

        if self._borderwidth > 0:
            self.DrawBorder(dc, gc)

        return dc, gc

    # -----------------------------------------------------------------------

    def DrawBorder(self, dc, gc):
        w, h = self.GetClientSize()

        pen = wx.Pen(self._bordercolor, 1, self._borderstyle)
        dc.SetPen(pen)

        # draw the upper left sides
        for i in range(self._borderwidth):
            # upper
            dc.DrawLine(0, i, w - i, i)
            # left
            dc.DrawLine(i, 0, i, h - i)

        # draw the lower right sides
        for i in range(self._borderwidth):
            dc.DrawLine(i, h - i - 1, w + 1, h - i - 1)
            dc.DrawLine(w - i - 1, i, w - i - 1, h)

    # -----------------------------------------------------------------------

    def DrawBackground(self, dc, gc):
        w, h = self.GetClientSize()

        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(brush)
        dc.DrawRectangle(self._borderwidth,
                         self._borderwidth,
                         w - (2 * self._borderwidth),
                         h - (2 * self._borderwidth))

    # -----------------------------------------------------------------------

    def DrawFocusIndicator(self, dc, gc):
        if self._focuswidth == 0:
            return

        focus_pen = wx.Pen(self._focuscolor,
                           self._focuswidth,
                           self._focusstyle)

        w, h = self.GetClientSize()
        dc.SetPen(focus_pen)
        gc.SetPen(focus_pen)
        dc.DrawLine(self._borderwidth + 2,
                    h - self._borderwidth - self._focuswidth - 2,
                    w - (2 * self._borderwidth) - 2,
                    h - self._borderwidth - self._focuswidth - 2)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _set_state(self, state):
        """Manually set the state of the button.

        :param `state`: (int) one of the state values

        """
        self._state[0] = self._state[1]
        self._state[1] = state

        # if it's not an 'exit' button, we still exist!
        if self:
            if wx.Platform == '__WXMSW__':
                self.GetParent().RefreshRect(self.Rect, False)
            else:
                self.Refresh()

# ---------------------------------------------------------------------------


class BitmapTextButton(BaseButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        By default, the name of the button is the name of its bitmap.

        The label is optional.
        By default, the label is under the bitmap.

        """
        super(BitmapTextButton, self).__init__(
            parent, id, pos, size, name)

        self._label = label
        self._labelpos = wx.BOTTOM
        self._spacing = 4
        self._default_bitmapcolor = self.GetPenForegroundColour()
        self._bitmapcolor = self._default_bitmapcolor
        self._align = wx.ALIGN_CENTER  # or LEFT or RIGHT

        # The icon image
        self._image = None
        if name != wx.ButtonNameStr:
            self.SetImage(name)

    # -----------------------------------------------------------------------

    def SetImage(self, image_name):
        """Set a new image.

        :param image_name: (str) Name of the image or full filename

        """
        self._image = image_name

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        BaseButton.SetForegroundColour(self, colour)
        if self._bitmapcolor == self._default_bitmapcolor:
            self._bitmapcolor = self.GetPenForegroundColour()

        self._default_bitmapcolor = self.GetPenForegroundColour()

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Overridden base class virtual.

        Determines the best size of the button based on the label.

        """
        label = self.GetLabel()
        if not label:
            return wx.Size(32, 32)

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        retWidth, retHeight = dc.GetTextExtent(label)

        width = int(max(retWidth, retHeight) * 1.5)
        return wx.Size(width, width)

    # -----------------------------------------------------------------------

    def GetBitmapColour(self):
        return self._bitmapcolor

    def SetBitmapColour(self, color):
        if color == self.GetParent().GetBackgroundColour():
            return
        self._bitmapcolor = color

    # -----------------------------------------------------------------------

    def GetSpacing(self):
        return self._spacing

    def SetSpacing(self, value):
        self._spacing = max(int(value), 2)

    # -----------------------------------------------------------------------

    def GetLabelPosition(self):
        return self._labelpos

    def SetLabelPosition(self, pos=wx.BOTTOM):
        """Set the position of the label: top, bottom, left, right."""
        if pos not in [wx.TOP, wx.BOTTOM, wx.LEFT, wx.RIGHT]:
            return
        self._labelpos = pos

    # -----------------------------------------------------------------------

    def GetAlign(self):
        return self._align

    def SetAlign(self, align=wx.ALIGN_CENTER):
        """Set the position of the label: top, bottom, left, right."""
        if align not in [wx.ALIGN_CENTER, wx.ALIGN_LEFT, wx.ALIGN_RIGHT]:
            return
        self._align = align

    # ------------------------------------------------------------------------

    def GetLabel(self):
        """Return the label text as it was passed to SetLabel."""
        return self._label

    # ------------------------------------------------------------------------

    def SetLabel(self, label):
        """Set the label text.

        :param label: (str) Label text.

        """
        self._label = label

    # -----------------------------------------------------------------------

    LabelPosition = property(GetLabelPosition, SetLabelPosition)
    BitmapColour = property(GetBitmapColour, SetBitmapColour)
    Spacing = property(GetSpacing, SetSpacing)
    Align = property(GetAlign, SetAlign)

    # -----------------------------------------------------------------------

    def Draw(self):
        """Draw some parts of the button.

            1. Prepare the Drawing Context
            2. Draw the background
            3. Draw the border (if border > 0)
            4. Draw focus indicator (if state is 'HIGHLIGHT')

        :returns: dc, gc

        """
        dc, gc = self.PrepareDraw()

        self.DrawBackground(dc, gc)

        if self._state[1] == BaseButton.HIGHLIGHT:
            self.DrawFocusIndicator(dc, gc)

        x, y, w, h = self.GetClientRect()
        bd = max(self.GetBorderWidth(), 2)
        x += bd
        y += bd
        w -= (2 * bd)
        h -= ((2 * bd) + self.FocusWidth + 2)

        if w >= 4 and h >= 4:
            self._DrawContent(dc, gc, x, y, w, h)

        if self._borderwidth > 0:
            self.DrawBorder(dc, gc)

    # -----------------------------------------------------------------------

    def _DrawContent(self, dc, gc, x, y, w, h):
        # No label is defined. 
        # Draw the square bitmap icon at the center with a 5% margin all around
        if self._label is None:
            x_pos, y_pos, bmp_size = self.__get_bitmap_properties(x, y, w, h)
            designed = self.__draw_bitmap(dc, gc, x_pos, y_pos, bmp_size)
            if designed is False:
                pen = wx.Pen(self.GetPenForegroundColour(), 1, self._borderstyle)
                dc.SetPen(pen)
                dc.DrawRectangle(self._borderwidth,
                                 self._borderwidth,
                                 w - (2 * self._borderwidth),
                                 h - (2 * self._borderwidth))

        else:
            tw, th = self.get_text_extend(dc, gc, self._label)

            if self._labelpos == wx.BOTTOM or self._labelpos == wx.TOP:
                # spacing is applied vertically
                x_bmp, y_pos, bmp_size = self.__get_bitmap_properties(
                    x, y + th + self._spacing,
                    w, h - th - 2 * self._spacing)
                if bmp_size > 15:
                    margin = h - bmp_size - th - self._spacing
                    y += (margin // 2)

                if self._labelpos == wx.BOTTOM:
                    #self.__draw_bitmap(dc, gc, (w - bmp_size) // 2, y, bmp_size)
                    self.__draw_bitmap(dc, gc, x_bmp, y, bmp_size)
                    self.__draw_label(dc, gc, (w - tw) // 2, h - th)

                if self._labelpos == wx.TOP:
                    self.__draw_label(dc, gc, (w - tw) // 2, y)
                    self.__draw_bitmap(dc, gc, x_bmp, y_pos, bmp_size)

            if self._labelpos == wx.LEFT or self._labelpos == wx.RIGHT:
                # spacing is applied horizontally
                x_bmp, y_bmp, bmp_size = self.__get_bitmap_properties(
                    x, y, w - tw - self._spacing, h)

                if bmp_size > 8:
                    margin = w - bmp_size - tw - self._spacing
                    if self._align == wx.ALIGN_RIGHT:
                        x += margin
                    elif self._align == wx.ALIGN_CENTER:
                        x += (margin // 2)

                    if self._labelpos == wx.LEFT:
                        self.__draw_label(dc, gc, x, (h - (th//2)) // 2)
                        self.__draw_bitmap(dc, gc, x_bmp + self._spacing + tw, y_bmp, bmp_size)

                    if self._labelpos == wx.RIGHT:
                        self.__draw_bitmap(dc, gc, x_bmp, y_bmp, bmp_size)
                        self.__draw_label(dc, gc, x_bmp + bmp_size + self._spacing, (h - (th//2)) // 2)

                else:
                    # not enough room for a bitmap.
                    if self._align == wx.ALIGN_CENTER:
                        self.__draw_label(dc, gc, (w - tw) // 2, (h - (th//2)) // 2)
                    elif self._align == wx.ALIGN_LEFT:
                        self.__draw_label(dc, gc, x, (h - (th//2)) // 2)
                    elif self._align == wx.ALIGN_RIGHT:
                        self.__draw_label(dc, gc, (w - tw), (h - (th//2)) // 2)

    # -----------------------------------------------------------------------

    def __get_bitmap_properties(self, x, y, w, h):
        # w, h is the available size
        bmp_size = min(w, h)                  # force a squared button
        margin = max(int(bmp_size * 0.2), 2)  # optimal margin (20% of btn size)
        bmp_size -= margin
        y_pos = y + (margin // 2)
        if self._align == wx.ALIGN_LEFT:
            x_pos = x
        elif self._align == wx.ALIGN_RIGHT:
            x_pos = w - bmp_size
        else:
            x_pos = x + (margin // 2)

        if w < h:
            y_pos = (h - bmp_size + margin) // 2
        else:
            if self._align == wx.ALIGN_CENTER:
                x_pos = (w - bmp_size + margin) // 2

        return x_pos, y_pos, bmp_size

    # -----------------------------------------------------------------------

    def __draw_bitmap(self, dc, gc, x, y, btn_size):
        # if no image was given
        if self._image is None:
            return False

        try:
            # get the image from its name
            img = sppasSwissKnife.get_image(self._image)
            # re-scale the image to the expected size
            sppasSwissKnife.rescale_image(img, btn_size)
            # re-colorize
            ColorizeImage(img, wx.BLACK, self._bitmapcolor)
            # convert to bitmap
            bitmap = wx.Bitmap(img)
            # draw it to the dc or gc
            if wx.Platform == '__WXGTK__':
                dc.DrawBitmap(bitmap, x, y)
            else:
                gc.DrawBitmap(bitmap, x, y)
        except Exception as e:
            wx.LogWarning('Draw image error: {:s}'.format(str(e)))
            return False

        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def __draw_label(self, dc, gc, x, y):
        font = self.GetParent().GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetParent().GetForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetParent().GetForegroundColour())
            gc.DrawText(self._label, x, y)

# ---------------------------------------------------------------------------


class TextButton(BaseButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        The label is required.

        """
        super(TextButton, self).__init__(parent, id, pos, size, name)

        self._label = label
        self._labelpos = wx.CENTER

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Overridden base class virtual.

        Determines the best size of the button based on the label.

        """
        label = self.GetLabel()
        if not label:
            return wx.Size(32, 32)

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        retWidth, retHeight = dc.GetTextExtent(label)

        width = int(max(retWidth, retHeight) * 1.5)
        return wx.Size(width, width)

    # -----------------------------------------------------------------------

    def GetLabelPosition(self):
        return self._labelpos

    def SetLabelPosition(self, pos=wx.BOTTOM):
        """Set the position of the label: top, bottom, left, right."""
        if pos not in [wx.TOP, wx.BOTTOM, wx.LEFT, wx.RIGHT]:
            return
        self._labelpos = pos

    # -----------------------------------------------------------------------

    LabelPosition = property(GetLabelPosition, SetLabelPosition)

    # -----------------------------------------------------------------------

    def Draw(self):
        """Draw some parts of the button.

            1. Prepare the Drawing Context
            2. Draw the background
            3. Draw the border (if border > 0)
            4. Draw focus indicator (if state is 'HIGHLIGHT')

        :returns: dc, gc

        """
        dc, gc = self.PrepareDraw()

        self.DrawBackground(dc, gc)

        if self._state[1] == BaseButton.HIGHLIGHT:
            self.DrawFocusIndicator(dc, gc)

        x, y, w, h = self.GetClientRect()
        bd = max(self.GetBorderWidth(), 2)
        x += bd
        y += bd
        w -= (2 * bd)
        h -= ((2 * bd) + self.FocusWidth + 2)

        # No label is defined.
        tw, th = self.get_text_extend(dc, gc, self._label)

        if self._labelpos == wx.BOTTOM:
            self.__draw_label(dc, gc, (w - tw) // 2, h - th)

        elif self._labelpos == wx.TOP:
            self.__draw_label(dc, gc, (w - tw) // 2, y)

        elif self._labelpos == wx.LEFT:
            self.__draw_label(dc, gc, 2, (h - th) // 2)

        elif self._labelpos == wx.RIGHT:
            self.__draw_label(dc, gc, w - tw - 2 , (h - th) // 2)

        else:
            # Center the text.
            self.__draw_label(dc, gc, (w - tw) // 2, (h - th) // 2)

        if self._borderwidth > 0:
            self.DrawBorder(dc, gc)

    # -----------------------------------------------------------------------

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def __draw_label(self, dc, gc, x, y):
        font = self.GetParent().GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetParent().GetForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetParent().GetForegroundColour())
            gc.DrawText(self._label, x, y)


# ---------------------------------------------------------------------------


class ToggleButton(BitmapTextButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor."""
        super(ToggleButton, self).__init__(parent, id, label=label, pos=pos, size=size, name=name)

        self._pressed = False

    # -----------------------------------------------------------------------

    def IsPressed(self):
        """Return if button is pressed.

        :returns: (bool)

        """
        return self._pressed

    # -----------------------------------------------------------------------

    def GetValue(self):
        return self._pressed

    # -----------------------------------------------------------------------

    def SetValue(self, value):
        if self._pressed != value:
            self._pressed = value
            if value:
                self._set_state(BaseButton.PRESSED)
            else:
                self._set_state(BaseButton.NORMAL)
            self.Refresh()

    # -----------------------------------------------------------------------
    # Override BaseButton
    # -----------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the wx.EVT_LEFT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self.IsEnabled() is True:
            self._pressed = not self._pressed
            BaseButton.OnMouseLeftDown(self, event)

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if not self.IsEnabled():
            return

        # Mouse was down outside of the button (but is up inside)
        if not self.HasCapture():
            return

        # Directs all mouse input to this window
        self.ReleaseMouse()

        # If the button was down when the mouse was released...
        if self._state[1] == BaseButton.PRESSED:
            self.Notify()

            if self._pressed:
                self._set_state(BaseButton.PRESSED)
            else:
                self._set_state(BaseButton.HIGHLIGHT)

            # test self, in case the button was destroyed in the eventhandler
            if self:
                # self.Refresh()  # done in set_state
                event.Skip()

    # -----------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self._pressed is True:
            self._set_state(BaseButton.PRESSED)
            return

        if self._state[1] == BaseButton.HIGHLIGHT:
            self._set_state(BaseButton.NORMAL)
            self.Refresh()
            event.Skip()

        elif self._state[1] == BaseButton.PRESSED:
            self._state[0] = BaseButton.NORMAL
            self.Refresh()
            event.Skip()

        self._pressed = False

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_TOGGLEBUTTON event to the listener (if any)."""
        evt = ToggleButtonEvent(wx.wxEVT_COMMAND_TOGGLEBUTTON_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

# ---------------------------------------------------------------------------


class BaseCheckButton(BaseButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.PanelNameStr):
        """Default class constructor.

        :param parent: (wx.Window) parent window. Must not be ``None``;
        :param id: (int) window identifier. A value of -1 indicates a default value;
        :param pos: the button position. A value of (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython, depending on
         platform;
        :param size: the button size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param name: (str) the button name.

        """
        super(BaseCheckButton, self).__init__(parent, id, pos, size, name)

        self._pressed = False

    # -----------------------------------------------------------------------

    def IsPressed(self):
        """Return if button is pressed.

        :returns: (bool)

        """
        return self._pressed

    # -----------------------------------------------------------------------

    def Check(self, value):
        if self._pressed != value:
            self._pressed = value
            if value:
                self._set_state(BaseButton.PRESSED)
            else:
                self._set_state(BaseButton.NORMAL)
            self.Refresh()

    # -----------------------------------------------------------------------
    # Override BaseButton
    # -----------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the wx.EVT_LEFT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self.IsEnabled() is True:
            self._pressed = not self._pressed
            BaseButton.OnMouseLeftDown(self, event)

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if not self.IsEnabled():
            return

        # Mouse was down outside of the button (but is up inside)
        if not self.HasCapture():
            return

        # Directs all mouse input to this window
        self.ReleaseMouse()

        # If the button was down when the mouse was released...
        if self._state[1] == BaseButton.PRESSED:
            self.Notify()

            if self._pressed:
                self._set_state(BaseButton.PRESSED)
            else:
                self._set_state(BaseButton.HIGHLIGHT)

            # test self, in case the button was destroyed in the eventhandler
            if self:
                # self.Refresh()  # done in set_state
                event.Skip()

    # ------------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self._pressed is True:
            self._set_state(BaseButton.PRESSED)
            return

        if self._state[1] == BaseButton.HIGHLIGHT:
            self._set_state(BaseButton.NORMAL)
            self.Refresh()
            event.Skip()

        elif self._state[1] == BaseButton.PRESSED:
            self._state[0] = BaseButton.NORMAL
            self.Refresh()
            event.Skip()

        self._pressed = False

    # ------------------------------------------------------------------------

    def Notify(self):
        """Actually sends the wx.wxEVT_COMMAND_CHECKBOX_CLICKED event."""
        evt = ButtonEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

# ---------------------------------------------------------------------------


class CheckButton(BaseCheckButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name.

        """
        super(CheckButton, self).__init__(
            parent, id, pos, size, name)

        self._borderwidth = 0
        self._label = label
        self._radio = False

        # Set the spacing between the check bitmap and the label to 6.
        # This can be changed using SetSpacing later.
        self._spacing = 6

    # ------------------------------------------------------------------------

    def GetLabel(self):
        """Return the label text as it was passed to SetLabel."""
        return self._label

    # ------------------------------------------------------------------------

    def IsChecked(self):
        """Return if button is checked.

        :returns: (bool)

        """
        return self._pressed

    # ------------------------------------------------------------------------

    def SetSpacing(self, spacing):
        """Set a new spacing between the check bitmap and the text.

        :param spacing: (int) Value between 0 and 30.

        """
        spacing = int(spacing)
        if spacing < 0:
            spacing = 0
        if spacing > 30:
            # wx.LogWarning('Spacing of a button is maximum 30px width. '
            #                'Got {:d}.'.format(spacing))
            spacing = 30
        # we should check if spacing < self height or width
        self._spacing = spacing

    # ------------------------------------------------------------------------

    def GetSpacing(self):
        """Return the spacing between the bitmap and the text."""
        return self._spacing

    # ------------------------------------------------------------------------

    def GetDefaultAttributes(self):
        """Overridden base class virtual.

        By default we should use
        the same font/colour attributes as the native wx.CheckBox.

        """
        return wx.CheckBox.GetClassDefaultAttributes()

    # ------------------------------------------------------------------------

    def SetValue(self, value):
        """Set the state of the button.

        :param value: (bool)

        """
        self.Check(value)
        #self._pressed = bool(value)

    # ------------------------------------------------------------------------

    def GetValue(self):
        """Return the state of the button."""
        return self._pressed

    # ------------------------------------------------------------------------

    def DrawCheckImage(self, dc, gc):
        """Draw the check image.

        """
        w, h = self.GetClientSize()

        if self._label is None or len(self._label) == 0:
            prop_size = int(min(h * 0.7, 32))
            img_size = max(16, prop_size)
        else:
            tw, th = CheckButton.__get_text_extend(dc, gc, "XX")
            img_size = int(float(th) * 1.2)

        box_x = self._borderwidth + 2
        box_y = (h - img_size) // 2

        # Adjust image size then draw
        if self._pressed:
            if self._radio:
                img = sppasSwissKnife.get_image('radio_checked')
            else:
                img = sppasSwissKnife.get_image('choice_checked')
        else:
            if self._radio:
                img = sppasSwissKnife.get_image('radio_unchecked')
            else:
                img = sppasSwissKnife.get_image('choice_checkbox')

        sppasSwissKnife.rescale_image(img, img_size)
        ColorizeImage(img, wx.BLACK, self.GetPenForegroundColour())

        # Draw image as bitmap
        bmp = wx.Bitmap(img)
        if wx.Platform == '__WXGTK__':
            dc.DrawBitmap(bmp, box_x, box_y)
        else:
            gc.DrawBitmap(bmp, box_x, box_y)

        return img_size

    # ------------------------------------------------------------------------

    @staticmethod
    def __get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # ------------------------------------------------------------------------

    def __DrawLabel(self, dc, gc, x):
        w, h = self.GetClientSize()
        tw, th = CheckButton.__get_text_extend(dc, gc, self._label)
        y = ((h - th) // 2)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetPenForegroundColour())
            dc.DrawText(self._label, x, y)
        else:
            gc.SetTextForeground(self.GetPenForegroundColour())
            gc.DrawText(self._label, x, y)

    # ------------------------------------------------------------------------

    def DrawButton(self):
        """Draw the button.

        Override the base method.

        """
        # Get the actual client size of ourselves
        width, height = self.GetClientSize()
        if not width or not height:
            # Nothing to do, we still don't have dimensions!
            return

        dc, gc = self.Draw()
        img_size = self.DrawCheckImage(dc, gc)
        if self._label:
            self.__DrawLabel(dc, gc, img_size + self._spacing)

    # ------------------------------------------------------------------------

    def OnEraseBackground(self, event):
        """Handle the wx.EVT_ERASE_BACKGROUND event.

        Override the base method.

        """
        # This is intentionally empty, because we are using the combination
        # of wx.BufferedPaintDC + an empty OnEraseBackground event to
        # reduce flicker
        pass

    # ------------------------------------------------------------------------

    def GetBackgroundBrush(self, dc):
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
            return wx.Brush(color, wx.SOLID)

        return brush

# ---------------------------------------------------------------------------


class RadioButton(CheckButton):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name.

        """
        super(RadioButton, self).__init__(parent, id, label, pos, size, name)
        self._radio = True

    # ------------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_RADIOBUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.EVT_RADIOBUTTON.typeId, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelBaseButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelBaseButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test BaseButton")

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
            btn = BaseButton(self, pos=(x, 10), size=(w, h))
            btn.SetBorderWidth(i)
            btn.SetBorderColour(wx.Colour(c, c, c))
            btn.SetBorderStyle(st[i-1])
            c += 40
            x += w + 10
            btn.Bind(wx.EVT_BUTTON, self.on_btn_event)

        # play with the focus
        x = 10
        w = 100
        h = 50
        c = 10
        for i in range(1, 6):
            btn = BaseButton(self, pos=(x, 70), size=(w, h))
            btn.SetBorderWidth(1)
            btn.SetFocusWidth(i)
            btn.SetFocusColour(wx.Colour(c, c, c))
            btn.SetFocusStyle(st[i-1])
            c += 40
            x += w + 10
            btn.Bind(wx.EVT_BUTTON, self.on_btn_event)

        vertical = BaseButton(self, pos=(560, 10), size=(50, 110))

    # -----------------------------------------------------------------------

    def on_btn_event(self, event):
        obj = event.GetEventObject()

# ----------------------------------------------------------------------------


class TestPanelBitmapButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelBitmapButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test BitmapButton")

        b1 = BitmapTextButton(self, pos=(10, 10), size=(50, 50))
        b2 = BitmapTextButton(self, pos=(70, 10), size=(50, 50))
        b3 = BitmapTextButton(self, pos=(130, 10), size=(100, 50), name="like")
        b4 = BitmapTextButton(self, pos=(240, 10), size=(30, 50), name="like")
        b5 = BitmapTextButton(self, pos=(280, 10), size=(30, 30), name="like")
        b6 = BitmapTextButton(self, pos=(320, 10), size=(50, 30), name="like")
        b7 = BitmapTextButton(self, pos=(380, 10), size=(50, 50), name="add")
        b7.SetBorderWidth(0)
        b7.SetFocusColour(wx.Colour(30, 120, 240))
        b7.SetFocusWidth(3)
        b7.SetFocusStyle(wx.PENSTYLE_SOLID)
        b8 = BitmapTextButton(self, pos=(440, 10), size=(50, 50), name="remove")
        b8.SetBorderWidth(0)
        b8.SetFocusColour(wx.Colour(30, 120, 240))
        b8.SetBitmapColour(wx.Colour(230, 120, 40))
        b8.SetFocusWidth(3)
        b8.SetFocusStyle(wx.PENSTYLE_SOLID)
        b9 = BitmapTextButton(self, pos=(500, 10), size=(50, 50), name="delete")
        b9.SetBorderWidth(0)
        b9.SetFocusColour(wx.Colour(30, 120, 240))
        b9.SetBitmapColour(wx.Colour(240, 10, 10))
        b9.SetFocusWidth(3)
        b9.SetFocusStyle(wx.PENSTYLE_SOLID)

# ----------------------------------------------------------------------------


class TestPanelBitmapTextButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelBitmapTextButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test TextBitmapButton")

        b1 = BitmapTextButton(self, label="sppas_64", pos=(10, 10), size=(50, 50))
        #font = self.GetFont().MakeBold()
        #b1.SetFont(font)

        b2 = BitmapTextButton(self, label="boldfont", pos=(70, 10), size=(100, 50))
        # bold_font = wx.Font(15,                      # point size
        #                     wx.FONTFAMILY_DEFAULT,   # family,
        #                     wx.FONTSTYLE_NORMAL,     # style,
        #                     wx.FONTWEIGHT_BOLD,      # weight,
        #                     underline=False,
        #                     faceName="Lucida sans",
        #                     encoding=wx.FONTENCODING_SYSTEM)
        # b2.SetFont(bold_font)

        b3 = BitmapTextButton(self, label="sppas_colored", pos=(180, 10), size=(50, 50))

        b4 = BitmapTextButton(self, label="Add", pos=(240, 10), size=(100, 50), name="add")
        b4.SetLabel("ADD")
        b4.SetLabelPosition(wx.RIGHT)
        b4.Refresh()

        b5 = BitmapTextButton(self, label="Add", pos=(350, 10), size=(100, 50), name="add_lower")
        b5.SetLabelPosition(wx.LEFT)
        b6 = BitmapTextButton(self, label="Room for a tiny bitmap", pos=(460, 10), size=(150, 50), name="tiny")
        b6.SetLabelPosition(wx.LEFT)

# ----------------------------------------------------------------------------


class TestPanelCheckButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelCheckButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name="Test CheckButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))

        btn_check_xs = CheckButton(self, pos=(25, 10), size=(32, 32), name="yes")
        btn_check_xs.Check(True)
        btn_check_xs.Bind(wx.EVT_BUTTON, self.on_btn_event)

        btn_check_s = CheckButton(self, label="disabled", pos=(100, 10), size=(128, 64), name="yes")
        btn_check_s.Enable(False)

        btn_check_m = CheckButton(self, label='The text label', pos=(200, 10), size=(384, 128), name="yes")
        font = self.GetFont().MakeBold().Scale(1.4)
        btn_check_m.SetFont(font)
        btn_check_m.Bind(wx.EVT_BUTTON, self.on_btn_event)

    def on_btn_event(self, event):
        obj = event.GetEventObject()

# ----------------------------------------------------------------------------


class TestPanelRadioButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelRadioButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name="Test RadioButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))

        btn_check_xs = RadioButton(self, pos=(25, 10), size=(32, 32), name="yes")
        btn_check_xs.Check(True)
        btn_check_xs.Bind(wx.EVT_BUTTON, self.on_btn_event)

        btn_check_s = RadioButton(self, label="disabled", pos=(100, 10), size=(128, 64), name="dis")
        btn_check_s.Enable(False)

        btn_check_m = RadioButton(self, label='The text label', pos=(200, 10), size=(384, 128), name="radio")
        font = self.GetFont().MakeBold().Scale(1.4)
        btn_check_m.SetFont(font)
        btn_check_m.Bind(wx.EVT_BUTTON, self.on_btn_event)

    def on_btn_event(self, event):
        obj = event.GetEventObject()

# ----------------------------------------------------------------------------


class TestPanelButtonsInSizer(wx.Panel):

    def __init__(self, parent):
        super(TestPanelButtonsInSizer, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name="Test SizerButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))
        # b1 = BitmapTextButton(self, label="sppas_colored")
        # b2 = BitmapTextButton(self, name="like")

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(BaseButton(self), 2, wx.LEFT | wx.EXPAND, 0)
        sizer.Add(BaseButton(self), 2, wx.LEFT | wx.EXPAND, 0)
        sizer.Add(BaseButton(self), 2, wx.LEFT | wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

# ----------------------------------------------------------------------------


class TestPanel(sc.ScrolledPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test Buttons")

        sizer = wx.BoxSizer(wx.VERTICAL)

        tbpanel = wx.Panel(self, size=(-1, 32), )
        tbsizer = wx.BoxSizer(wx.HORIZONTAL)

        bgbtn = BitmapTextButton(tbpanel, name="bg_color")
        bgbtn.SetFocusWidth(0)
        fgbtn = BitmapTextButton(tbpanel, name="font_color")
        fgbtn.SetFocusWidth(0)
        fontbtn = BitmapTextButton(tbpanel, name="font")
        fontbtn.SetFocusWidth(0)

        self.Bind(wx.EVT_BUTTON, self.on_bg_color, bgbtn)
        self.Bind(wx.EVT_BUTTON, self.on_fg_color, fgbtn)
        self.Bind(wx.EVT_BUTTON, self.on_font, fontbtn)
        tbsizer.AddSpacer(3)
        tbsizer.Add(bgbtn, 0, wx.LEFT | wx.RIGHT, 4)
        tbsizer.Add(fgbtn, 0, wx.LEFT | wx.RIGHT, 4)
        tbsizer.Add(fontbtn, 0, wx.LEFT | wx.RIGHT, 4)
        tbsizer.AddSpacer(3)
        tbpanel.SetSizer(tbsizer)
        sizer.Add(tbpanel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)

        sizer.Add(wx.StaticText(self, label="BaseButton()"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelBaseButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticLine(self))
        sizer.Add(wx.StaticText(self, label="BitmapTextButton() - no text"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelBitmapButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticLine(self))
        sizer.Add(wx.StaticText(self, label="BitmapTextButton() - with text"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelBitmapTextButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticText(self, label="Buttons without fixed size:"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelButtonsInSizer(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticText(self, label="Checked buttons:"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelCheckButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticText(self, label="Radio buttons:"), 0, wx.TOP | wx.BOTTOM, 2)
        sizer.Add(TestPanelRadioButton(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)

        self.SetSizer(sizer)
        self.SetupScrolling()

    def on_bg_color(self, event):
        self.SetBackgroundColour(wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250)
        ))
        self.Refresh()

    def on_fg_color(self, event):
        self.SetForegroundColour(wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250)
        ))
        self.Refresh()

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

        self.Refresh()
