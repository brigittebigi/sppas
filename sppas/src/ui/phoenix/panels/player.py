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

    src.ui.phoenix.panels.player.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.media

from sppas import paths

from ..windows import sppasPanel
from ..windows import sppasMedia
from ..windows import sppasStaticLine
from ..windows import BitmapTextButton
from ..windows import ToggleButton

# ---------------------------------------------------------------------------


class sppasPlayerPanel(sppasPanel):
    """Create a panel to play a media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="CollapsiblePane"):
        """Create a sppasPlayerPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        """

        sppasPanel.__init__(self, parent, id, pos, size, style, name)

        self._create_content()
        self._setup_events()

        # Look&feel
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.SetMinSize(wx.Size(sppasPanel.fix_size(240), -1))
        self.SetInitialSize()
        self.Layout()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        tb = self.__create_toolbar()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        tb = sppasPanel(self, name="toolbar_player_panel")

        nav = sppasPanel(tb, name="tb_nav_panel")
        sizer_nav = wx.BoxSizer(wx.VERTICAL)

        btn_play = BitmapTextButton(nav, label="", name="media_play")
        self.__button_properties(btn_play)
        btn_play.SetMinSize(wx.Size(sppasPanel.fix_size(48),
                                    sppasPanel.fix_size(48)))

        btn_pause = BitmapTextButton(nav, label="", name="media_pause")
        self.__button_properties(btn_pause)

        btn_stop = BitmapTextButton(nav, label="", name="media_stop")
        self.__button_properties(btn_stop)

        btn_replay = ToggleButton(nav, label="", name="media_stop")
        btn_replay = self.__button_properties(btn_replay)

        sizer_btns = wx.BoxSizer(wx.HORIZONTAL)
        sizer_btns.Add(btn_play, 0, wx.EXPAND, 0)
        sizer_btns.Add(btn_pause, 0, wx.EXPAND, 0)
        sizer_btns.Add(btn_stop, 0, wx.EXPAND, 0)
        sizer_btns.Add(btn_replay, 0, wx.EXPAND, 0)

        slider = wx.Slider(nav)
        sizer_nav.Add(sizer_btns, 1, wx.EXPAND)
        sizer_nav.Add(slider, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(sizer_nav, 1, wx.EXPAND)
        sizer.AddStretchSpacer(1)
        tb.SetSizer(sizer)
        return tb

    # -----------------------------------------------------------------------

    def __create_hline(self):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        return line

    # -----------------------------------------------------------------------

    def __button_properties(self, btn):
        btn.FocusWidth = 0
        btn.Spacing = 0
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(sppasPanel.fix_size(32),
                               sppasPanel.fix_size(32)))

        return btn

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """The parent has to be informed of a change of content."""
        # evt = DataChangedEvent(data=self.__data)
        # evt.SetEventObject(self)
        # wx.PostEvent(self.GetParent(), evt)
        pass

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user pressed a key of its keyboard
        self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()

        # Ctrl+s
        if key_code == 83 and cmd_down is True:
            # self.pin_save()
            pass

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()

        if name == "media_play":
            self.play()

        elif name == "media_pause":
            self.pause()

        event.Skip()

    # -----------------------------------------------------------------------

    def play(self):
        pass

    # -----------------------------------------------------------------------

    def pause(self):
        pass


# ---------------------------------------------------------------------------


class TestPanel(sppasPlayerPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

