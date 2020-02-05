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

    src.ui.phoenix.windows.media.playerctrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from ..button import ToggleButton, BitmapTextButton
from ..panel import sppasPanel
from .mediactrl import sppasMedia

# ---------------------------------------------------------------------------


class sppasPlayerControlsPanel(sppasPanel):
    """Create a panel with controls for a list of media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Four children panels are to be created and organized into a BoxSizer:
        - widgets_panel: a panel, free to be used to add widgets
        - transport_panel: all buttons to play a media and a slider
        - volume_panel: a button to mute and a slider to adjust the volume

    Any action of the user (click on a button, move a slider...) is sent to
    the parent by the event: EVT_PLAYER.

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="player_controls_panel"):
        """Create a sppasPlayerControlsPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.
        :param orient: wx.HORIZONTAL or wx.VERTICAL

        """
        super(sppasPlayerControlsPanel, self).__init__(
            parent, id, pos, size, style, name)

        self._create_content()
        self._setup_events()

        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def GetWidgetsPanel(self):
        """Return the customizable panel."""
        return self.FindWindow("widgets_panel")

    # -----------------------------------------------------------------------

    def AddWidget(self, wxwindow):
        """Add a widget into the first panel.

        :param wxwindow: (wx.Window)
        :return: True if added, False if parent does not match.

        """
        widgets_panel = self.FindWindow("widgets_panel")
        if wxwindow.GetParent() != widgets_panel:
            return False
        widgets_panel.GetSizer().Add(wxwindow, 0, wx.ALIGN_CENTER | wx.ALL, sppasPanel.fix_size(2))
        widgets_panel.Show(True)
        return True

    # -----------------------------------------------------------------------

    def GetSlider(self):
        """Return the slider to indicate offsets."""
        transport_panel = self.FindWindow("transport_panel")
        return transport_panel.FindWindow("seek_slider")

    # -----------------------------------------------------------------------

    def IsReplay(self):
        """Return True if the button to replay is enabled."""
        transport_panel = self.FindWindow("transport_panel")
        return transport_panel.FindWindow("media_repeat").IsPressed()

    # -----------------------------------------------------------------------

    def EnableReplay(self, enable=True):
        """Enable or disable the Replay button.

        The replay button should be disabled if several media of different
        durations have to be played...

        :param enable: (bool)

        """
        transport_panel = self.FindWindow("transport_panel")
        transport_panel.FindWindow("media_repeat").Enable(enable)

    # -----------------------------------------------------------------------

    def EnablePlay(self, enable=True):
        """Enable or disable the Play button.

        :param enable: (bool)

        """
        transport_panel = self.FindWindow("transport_panel")
        transport_panel.FindWindow("media_play").Enable(enable)

    # -----------------------------------------------------------------------

    def Paused(self, value=False):
        """Make the Play button in Play or Pause position.

        :param value: (bool) True to make the button in Pause position

        """
        transport_panel = self.FindWindow("transport_panel")
        btn = transport_panel.FindWindow("media_play")
        if value is True:
            btn.SetImage("media_pause")
            btn.Refresh()
        else:
            btn.SetImage("media_play")
            btn.Refresh()

    # -----------------------------------------------------------------------

    def SetRange(self, min_value=0, max_value=100):
        """Set the range values of the seek slider.

        Value of the slider is then set to the min.

        :param min_value: (int)
        :param max_value: (int)

        """
        transport_panel = self.FindWindow("transport_panel")
        slider = transport_panel.FindWindow("seek_slider")
        slider.SetRange(min_value, max_value)
        slider.SetValue(min_value)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """"""
        wx.Panel.SetBackgroundColour(self, colour)
        hi_color = self.GetHighlightedColour(colour)

        for name in ("transport", "widgets", "volume"):
            w = self.FindWindow(name + "_panel")
            for c in w.GetChildren():
                if isinstance(c, BitmapTextButton) is True:
                    c.SetBackgroundColour(hi_color)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel.

        :param orient: wx.HORIZONTAL or wx.VERTICAL

        """
        # Create the main panels
        panel1 = self.__create_widgets_panel()
        # panel1.Hide()
        panel2 = self.__create_transport_panel()
        panel3 = self.__create_volume_panel()
        slider = self.__create_seek_slider_panel()

        # Organize the panels into the main sizer
        border = sppasPanel.fix_size(2)
        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nav_sizer.Add(panel1, 3, wx.ALIGN_CENTRE | wx.EXPAND | wx.LEFT | wx.RIGHT, border)
        nav_sizer.Add(panel2, 5, wx.ALIGN_CENTER | wx.EXPAND | wx.LEFT | wx.RIGHT, border)
        nav_sizer.Add(panel3, 3, wx.ALIGN_CENTER | wx.EXPAND | wx.LEFT | wx.RIGHT, border)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(slider, 0, wx.ALIGN_CENTRE | wx.EXPAND | wx.ALL, border)
        sizer.Add(nav_sizer, 0, wx.ALIGN_CENTRE | wx.EXPAND | wx.ALL, border)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_widgets_panel(self):
        """Return an empty panel with a wrap sizer."""
        panel = sppasPanel(self, name="widgets_panel")
        sizer = wx.WrapSizer(orient=wx.VERTICAL)
        panel.SetSizerAndFit(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_seek_slider_panel(self):
        """Return a panel with a slider to indicate the position in time."""
        panel = sppasPanel(self, name="widgets_panel")

        # Labels of wx.Slider are not supported under MacOS.
        slider = wx.Slider(self, style=wx.SL_HORIZONTAL | wx.SL_MIN_MAX_LABELS)
        slider.SetRange(0, 100)
        slider.SetValue(0)
        slider.SetName("seek_slider")

        border = sppasPanel.fix_size(2)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(slider, 1, wx.EXPAND | wx.ALL, border)
        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_transport_panel(self):
        """Return a panel with the buttons to play/pause/stop the media."""
        panel = sppasPanel(self, name="transport_panel")

        btn_rewind = BitmapTextButton(panel, label="", name="media_rewind")
        self.SetButtonProperties(btn_rewind)

        btn_play = BitmapTextButton(panel, label="", name="media_play")
        self.SetButtonProperties(btn_play)
        # btn_play.Enable(False)
        btn_play.SetFocus()
        btn_play.SetMinSize(wx.Size(sppasPanel.fix_size(32),
                                    sppasPanel.fix_size(32)))

        btn_forward = BitmapTextButton(panel, label="", name="media_forward")
        self.SetButtonProperties(btn_forward)

        btn_stop = BitmapTextButton(panel, label="", name="media_stop")
        self.SetButtonProperties(btn_stop)

        btn_replay = ToggleButton(panel, label="", name="media_repeat")
        btn_replay = self.SetButtonProperties(btn_replay)

        border = sppasPanel.fix_size(2)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(btn_rewind, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_play, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_forward, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_stop, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_replay, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.AddStretchSpacer(1)
        panel.SetSizer(sizer)

        return panel

    # -----------------------------------------------------------------------

    def __create_volume_panel(self):
        """Return a panel with a slider for the volume and a mute button."""
        panel = sppasPanel(self, name="volume_panel")

        btn_mute = ToggleButton(panel, label="", name="volume_mute")
        btn_mute.SetImage("volume_high")
        self.SetButtonProperties(btn_mute)

        # Labels of wx.Slider are not supported under MacOS.
        slider = wx.Slider(panel, style=wx.SL_HORIZONTAL | wx.SL_MIN_MAX_LABELS)
        slider.SetName("volume_slider")
        slider.SetValue(100)
        slider.SetRange(0, 100)

        border = sppasPanel.fix_size(2)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btn_mute, 0, wx.ALIGN_CENTER | wx.ALL, border)
        sizer.Add(slider, 1, wx.ALIGN_CENTER | wx.EXPAND, border)
        panel.SetSizer(sizer)

        return panel

    # -----------------------------------------------------------------------

    def SetButtonProperties(self, btn):
        btn.FocusWidth = 1
        btn.Spacing = 0
        btn.BorderWidth = 0
        btn.SetMinSize(wx.Size(sppasPanel.fix_size(28),
                               sppasPanel.fix_size(28)))
        return btn

    # -----------------------------------------------------------------------

    def GetHighlightedColour(self, color):
        """Return a color slightly different of the given one."""
        color = self.GetParent().GetBackgroundColour()
        r, g, b, a = color.Red(), color.Green(), color.Blue(), color.Alpha()
        return wx.Colour(r, g, b, a).ChangeLightness(80)

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def notify(self, action, value=None):
        """The parent has to be informed that an action is required.

        An action can be:
            - play/stop/rewind/forward, without value;
            - volume, with a percentage value;
            - seek, the slider value (a percentage by default).

        :param action: (str) Name of the action to perform
        :param value: (any) Any kind of value linked to the action

        """
        evt = sppasMedia.MediaActionEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_action)

        # The slider position has changed
        self.Bind(wx.EVT_SLIDER, self._process_action)

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name in ("media_play", "media_stop", "media_rewind", "media_forward"):
            self.notify(action=name[6:], value=None)

        elif name == "volume_mute":
            self.__action_volume(to_notify=True)

        elif name == "volume_slider":
            self.__action_volume(to_notify=False)

        elif name == "seek_slider":
            self.notify(action="seek", value=obj.GetValue())

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def __action_volume(self, to_notify=True):
        """The toggle button to mute volume or the slider has changed.

        :param to_notify: (bool) notify or not if toggle is pressed.

        """
        vol_panel = self.FindWindow("volume_panel")
        mute_btn = vol_panel.FindWindow("volume_mute")
        if mute_btn.IsPressed() is True:
            if to_notify is True:
                mute_btn.SetImage("volume_mute")
                mute_btn.Refresh()
                self.notify(action="volume", value=0.)
        else:
            # get the volume value from the slider
            slider = vol_panel.FindWindow("volume_slider")
            volume = slider.GetValue()
            if volume == 0:
                mute_btn.SetImage("volume_off")
            elif volume < 30:
                mute_btn.SetImage("volume_low")
            elif volume < 70:
                mute_btn.SetImage("volume_medium")
            else:
                mute_btn.SetImage("volume_high")
            mute_btn.Refresh()

            # convert this percentage in a volume value ranging [0..1]
            volume = float(volume) / 100.
            self.notify(action="volume", value=volume)

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        p = sppasPlayerControlsPanel(self)

        btn1 = BitmapTextButton(p.GetWidgetsPanel(), label="", name="way_up_down")
        p.SetButtonProperties(btn1)
        p.AddWidget(btn1)

        s = wx.BoxSizer()
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)
        self.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.SetForegroundColour(wx.Colour(225, 225, 225))
