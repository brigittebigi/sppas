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

    src.ui.phoenix.windows.buttons.basebutton.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Description
    ===========

    This module implements a base class of a generic button, meaning that
    it is not built on native controls but is self-drawn.
    It acts like a normal button except for the focus that can follow the
    mouse.

    Sample usage:
    ============

        import wx
        import buttons

        class appFrame(wx.Frame):
            def __init__(self, parent, title):

                wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(400, 300))
                panel = wx.Panel(self)
                btn = buttons.Button(panel, -1, pos=(50, 50), size=(128, 32))

        app = wx.App()
        frame = appFrame(None, 'Button Test')
        frame.Show()
        app.MainLoop()

"""

import wx

from ..basewindow import sppasWindow

# ---------------------------------------------------------------------------


class ButtonEvent(wx.PyCommandEvent):
    """Base class for an event sent when the button is activated."""

    def __init__(self, event_type, event_id):
        """Default class constructor.

        :param event_type: the event type;
        :param event_id: the event identifier.

        """
        super(ButtonEvent, self).__init__(event_type, event_id)
        self.__button = None

    # ------------------------------------------------------------------------

    def SetButtonObj(self, btn):
        """Set the event object for the event.

        :param btn: the button object

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


class Button(sppasWindow):
    """Button is a custom type of window to represent a button.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

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
        super(Button, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        # By default, our buttons don't have borders
        self._vert_border_width = 0
        self._horiz_border_width = 0

        self._min_width = 12
        self._min_height = 12

        # Setup Initial Size
        self.SetInitialSize(size)

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_BUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
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
        # -------------------
        x = 10
        w = 100
        h = 50
        c = 10
        for i in range(1, 6):
            btn = Button(self, pos=(x, 10), size=(w, h))
            btn.SetBorderWidth(i)
            btn.SetBorderColour(wx.Colour(c, c, c))
            btn.SetBorderStyle(st[i-1])
            c += 40
            x += w + 10
            btn.Bind(wx.EVT_BUTTON, self.on_btn_event)

        # play with the focus
        # -------------------
        x = 10
        c = 10
        for i in range(1, 6):
            btn = Button(self, pos=(x, 70), size=(w, h))
            btn.SetBorderWidth(1)
            btn.SetFocusWidth(i)
            btn.SetFocusColour(wx.Colour(c, c, c))
            btn.SetFocusStyle(st[i-1])
            c += 40
            x += w + 10
            btn.Bind(wx.EVT_BUTTON, self.on_btn_event)

        # play with H/V
        # -------------
        vertical = Button(self, pos=(560, 10), size=(50, 110))
        vertical.SetBackgroundColour(wx.Colour(128, 255, 196))

        # play with enabled/disabled and colors
        # -------------------------------------
        btn1 = Button(self, pos=(10, 130), size=(w, h))
        btn1.Enable(True)
        btn1.SetBorderWidth(1)

        btn2 = Button(self, pos=(150, 130), size=(w, h))
        btn2.Enable(False)
        btn2.SetBorderWidth(1)

        btn3 = Button(self, pos=(290, 130), size=(w, h))
        btn3.Enable(True)
        btn3.SetBorderWidth(1)
        btn3.SetBackgroundColour(wx.Colour(222, 222, 200))
        btn3.SetForegroundColour(wx.Colour(22, 22, 20))

        btn4 = Button(self, pos=(430, 130), size=(w, h))
        btn4.Enable(False)
        btn4.SetBorderWidth(1)
        btn4.SetBackgroundColour(wx.Colour(222, 222, 200))
        btn4.SetForegroundColour(wx.Colour(22, 22, 20))

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def on_btn_event(self, event):
        obj = event.GetEventObject()
