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

    src.ui.phoenix.windows.buttons.togglebutton.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A toggle button with a bitmap, and eventually a label text.

"""

import wx

from ..basewindow import WindowState
from .basebutton import ButtonEvent
from .basebutton import BaseButton
from .bitmapbutton import BitmapTextButton
from .textbutton import TextButton

# ----------------------------------------------------------------------------


class ToggleButtonEvent(ButtonEvent):
    """Base class for an event sent when the toggle button is activated.

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
        super(ToggleButtonEvent, self).__init__(event_type, event_id)
        self.__isdown = False

    # -----------------------------------------------------------------------

    def SetIsDown(self, is_down):
        """Set the button toggle status as 'down' or 'up'.

        :param is_down: (bool) True if the button is clicked, False otherwise.

        """
        self.__isdown = bool(is_down)

    # -----------------------------------------------------------------------

    def GetIsDown(self):
        """Return the button toggle status as True if the button is down.

        :returns: (bool)

        """
        return self.__isdown

# ---------------------------------------------------------------------------


class ToggleTextButton(TextButton):
    """A toggle button with a label text only.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor."""
        self._pressed = False

        super(ToggleTextButton, self).__init__(
            parent, id, label=label, pos=pos, size=size, name=name)

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
                self._set_state(WindowState().selected)
            else:
                self._set_state(WindowState().normal)
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
        if self._state[1] == WindowState().selected:
            self.Notify()

            if self._pressed:
                self._set_state(WindowState().selected)
            else:
                self._set_state(WindowState().focused)

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
            self._set_state(WindowState().selected)
            return

        if self._state[1] == WindowState().focused:
            self._set_state(WindowState().normal)
            self.Refresh()
            event.Skip()

        elif self._state[1] == WindowState().selected:
            self._state[0] = WindowState().normal
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


class ToggleButton(BitmapTextButton):
    """A toggle button with a label text and a bitmap.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor."""
        self._pressed = False

        super(ToggleButton, self).__init__(
            parent, id, label=label, pos=pos, size=size, name=name)

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
                self._set_state(WindowState().selected)
            else:
                self._set_state(WindowState().normal)
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
        if self._state[1] == WindowState().selected:
            self.Notify()

            if self._pressed:
                self._set_state(WindowState().selected)
            else:
                self._set_state(WindowState().focused)

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
            self._set_state(WindowState().selected)
            return

        if self._state[1] == WindowState().focused:
            self._set_state(WindowState().normal)
            self.Refresh()
            event.Skip()

        elif self._state[1] == WindowState().selected:
            self._state[0] = WindowState().normal
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


class TestPanelToggleButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelToggleButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name="Test ToggleButton")

        self.SetForegroundColour(wx.Colour(150, 160, 170))
        # b1 = BitmapTextButton(self, label="sppas_colored")
        # b2 = BitmapTextButton(self, name="like")

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(ToggleButton(self), 1, wx.EXPAND, 0)
        sizer.Add(ToggleButton(self, name="rotate_screen"), 1, wx.EXPAND, 0)
        sizer.Add(ToggleTextButton(self, label=""), 1, wx.EXPAND, 0)
        sizer.Add(ToggleTextButton(self, label="label"), 1, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)
