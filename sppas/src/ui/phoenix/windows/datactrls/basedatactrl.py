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

    src.ui.phoenix.windows.datactrls.basedatactrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A base class for all windows used to draw data SPPAS can manage (waveform,
    tiers, etc).

"""

import wx
import logging

from ..winevents import sppasWindowEvent
from ..basedraw import sppasBaseWindow
from ..basedraw import WindowState

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


class sppasBaseDataWindow(sppasBaseWindow):
    """A base window with a DC to draw some data.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    MIN_WIDTH = 24
    MIN_HEIGHT = 12

    HORIZ_MARGIN_SIZE = 6
    VERT_MARGIN_SIZE = 6

    # -----------------------------------------------------------------------

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="datactrl"):
        """Initialize a new sppasBaseDataWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param name:      Window name.

        """
        super(sppasBaseDataWindow, self).__init__(
            parent, id, pos, size, style, name)

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
            btn = sppasBaseDataWindow(self, pos=(x, 10), size=(w, h))
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
            btn = sppasBaseDataWindow(self, pos=(x, 100), size=(w, h))
            btn.SetBorderWidth(1)
            btn.SetFocusWidth(i)
            btn.SetFocusColour(wx.Colour(c, c, c))
            btn.SetFocusStyle(st[i-1])
            c += 40
            x += w + 10

        vertical = sppasBaseDataWindow(self, pos=(10, 300), size=(50, 110))
        vertical.SetBackgroundColour(wx.Colour(128, 255, 196))

        btn = sppasBaseDataWindow(self, pos=(100, 300), size=(50, 110))
        btn.Enable(False)
