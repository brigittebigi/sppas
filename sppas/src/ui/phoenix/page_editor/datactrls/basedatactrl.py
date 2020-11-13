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

    src.ui.phoenix.page_editor.datactrls.basedatactrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A base class for all windows used to draw data SPPAS can manage (waveform,
    tiers, etc).

"""

import wx
import logging

from sppas.src.ui.phoenix.windows.winevents import sppasWindowEvent
from sppas.src.ui.phoenix.windows.basewindow import sppasWindow
from sppas.src.ui.phoenix.windows.basewindow import WindowState

# ---------------------------------------------------------------------------


class sppasWindowSelectedEvent(sppasWindowEvent):
    """Base class for an event sent when the window is selected.

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
        super(sppasWindowSelectedEvent, self).__init__(event_type, event_id)
        self.__selected = False

    # -----------------------------------------------------------------------

    def SetSelected(self, value):
        """Set the window status as selected or not.

        :param value: (bool) True if the window is selected, False otherwise.

        """
        value = bool(value)
        self.__selected = value

    # -----------------------------------------------------------------------

    def GetSelected(self):
        """Return the window status as True if selected.

        :returns: (bool)

        """
        return self.__selected

    # -----------------------------------------------------------------------

    Selected = property(GetSelected, SetSelected)

# ---------------------------------------------------------------------------


class sppasDataWindow(sppasWindow):
    """A base window with a DC to draw some data.

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
                 style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="datactrl"):
        """Initialize a new sppasBaseDataWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param data:   Data to draw.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param name:      Window name.

        """

        super(sppasDataWindow, self).__init__(
            parent, id, pos, size, style, name)
        self._selected = False
        self._is_selectable = False
        self._data = None
        if data is not None:
            self.SetData(data)

    # -----------------------------------------------------------------------

    def GetData(self):
        """Retrieve the data associated to the Ctrl.

        :return: data instance.

        """
        return self._data

    # -----------------------------------------------------------------------

    def SetData(self, data):
        """Set new data content."""
        if data != self._data:
            self._data = data
            self.SetToolTip(wx.ToolTip(self._tooltip()))
            self.Refresh()

    # -----------------------------------------------------------------------

    def _tooltip(self):
        """Set a tooltip string indicating data content."""
        if self._data is not None:
            return str(self._data)

        return "No data"

    # -----------------------------------------------------------------------

    def IsSelectable(self):
        """Return if the window can be selected."""
        return self._is_selectable

    # -----------------------------------------------------------------------

    def SetSelectable(self, value):
        value = bool(value)
        self._is_selectable = value

    # -----------------------------------------------------------------------

    def IsSelected(self):
        """Return if window is selected."""
        return self._selected

    # -----------------------------------------------------------------------

    def SetSelected(self, value):
        """Select or deselect the window except if not selectable.

        :param value: (bool)

        """
        if self._is_selectable is False:
            return

        value = bool(value)
        if self._selected != value:
            self._selected = value
            if value is True:
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
            if self._is_selectable is True:
                self._selected = not self._selected
            super(sppasDataWindow, self).OnMouseLeftDown(event)

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
            # if we haven't been destroyed by this notify...
            if self:
                if self._is_selectable is False:
                    self._set_state(self._state[0])
                else:
                    if self._selected is True:
                        self._set_state(WindowState().selected)
                    else:
                        self._set_state(WindowState().focused)
                self.Notify()
        else:
            if self._is_selectable is False:
                event.Skip()

    # -----------------------------------------------------------------------

    def OnMouseLeave(self, event):
        """Handle the wx.EVT_LEAVE_WINDOW event.

        :param event: a wx.MouseEvent event to be processed.

        """
        # mouse is leaving either while button is pressed (state is selected)
        # or not (state is focused). In both cases, we switch to normal state.
        if self._state[1] != WindowState().disabled:
            if self._is_selectable is False:
                self._state[1] = WindowState().normal
                self._set_state(WindowState().normal)
            else:

                if self._selected is True:
                    self._set_state(WindowState().selected)
                    return

                #if self._state[1] == WindowState().focused:
                self._set_state(WindowState().normal)
                #elif self._state[1] == WindowState().selected:
                #    self._state[0] = WindowState().normal
                #    self.Refresh()
                event.Skip()

        self._selected = False

    # -----------------------------------------------------------------------

    def Notify(self):
        logging.debug("Notify parent of selected with command left click event.")
        evt = sppasWindowSelectedEvent(wx.wxEVT_COMMAND_LEFT_CLICK, self.GetId())
        evt.SetObj(self._data)
        evt.SetSelected(self._selected)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test BaseDataWindow")

        self.SetForegroundColour(wx.Colour(150, 160, 170))
        st = [wx.PENSTYLE_SHORT_DASH,
              wx.PENSTYLE_LONG_DASH,
              wx.PENSTYLE_DOT_DASH,
              wx.PENSTYLE_SOLID,
              wx.PENSTYLE_HORIZONTAL_HATCH]

        # play with the border
        x = 10
        w = 120
        h = 80
        c = 10
        for i in range(1, 6):
            btn = sppasDataWindow(self, pos=(x, 10), size=(w, h))
            btn.SetBorderWidth(i)
            btn.SetBorderColour(wx.Colour(c, c, c))
            btn.SetBorderStyle(st[i-1])
            c += 40
            x += w + 10

        # play with the focus
        x = 10
        w = 120
        h = 80
        c = 10
        for i in range(1, 6):
            btn = sppasDataWindow(self, pos=(x, 100), size=(w, h))
            btn.SetBorderWidth(1)
            btn.SetFocusWidth(i)
            btn.SetFocusColour(wx.Colour(c, c, c))
            btn.SetFocusStyle(st[i-1])
            btn.SetSelectable(True)
            c += 40
            x += w + 10

        vertical = sppasDataWindow(self, pos=(10, 300), size=(50, 110))
        vertical.SetBackgroundColour(wx.Colour(128, 255, 196))

        btn = sppasDataWindow(self, pos=(100, 300), size=(50, 110))
        btn.Enable(False)
