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
import wx.media

from ..buttons import ToggleButton
from ..buttons import BitmapTextButton
from ..panels import sppasPanel

from ..slider import sppasSlider
from .timeslider import TimeSliderPanel
from .mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class sppasPlayerControlsPanel(sppasPanel):
    """Create a panel with controls for managing media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Four children are to be created and organized into a BoxSizer:
        - widgets_panel: a panel, free to be used to add widgets
        - transport_panel: all buttons to play a media
        - volume_panel: a button to mute and a slider to adjust the volume
        - slider_panel: a panel to indicate duration, selection, position...

    Any action of the user (click on a button, move a slider...) is sent to
    the parent by the event: EVT_MEDIA_ACTION.

    Any widget added to the widgets panel will send its own events.

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

        """
        super(sppasPlayerControlsPanel, self).__init__(
            parent, id, pos, size, style, name)

        self._btn_size = sppasPanel.fix_size(32)
        self._focus_color = wx.Colour(128, 128, 128, 128)
        self._create_content()
        self._setup_events()

        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods, for the controls
    # -----------------------------------------------------------------------

    def SetFocusColour(self, colour):
        self._focus_color = colour
        self.FindWindow("media_play").SetFocusColour(colour)
        self.FindWindow("media_stop").SetFocusColour(colour)
        self.FindWindow("media_rewind").SetFocusColour(colour)
        self.FindWindow("media_forward").SetFocusColour(colour)
        self.FindWindow("media_repeat").SetFocusColour(colour)
        self.FindWindow("volume_mute").SetFocusColour(colour)

    # -----------------------------------------------------------------------

    def AddWidget(self, wxwindow):
        """Add a widget into the customizable panel.

        :param wxwindow: (wx.Window)
        :return: True if added, False if parent does not match.

        """
        if wxwindow.GetParent() != self.widgets_panel:
            return False
        self.widgets_panel.GetSizer().Add(
            wxwindow, 0, wx.ALIGN_CENTER | wx.ALL, sppasPanel.fix_size(2))
        self.widgets_panel.Show(True)
        return True

    # -----------------------------------------------------------------------

    def SetButtonWidth(self, value):
        """Fix the width/height of the buttons.

        The given value will be adjusted to a proportion of the font height.
        Min is 12, max is 128.
        The buttons are not updated.

        """
        self._btn_size = min(sppasPanel.fix_size(value), 128)
        self._btn_size = max(self._btn_size, 12)

        btn = self.FindWindow("media_rewind")
        btn.SetMinSize(wx.Size(self._btn_size, self._btn_size))
        btn = self.FindWindow("media_play")
        btn.SetMinSize(wx.Size(self._btn_size, self._btn_size))
        btn = self.FindWindow("media_forward")
        btn.SetMinSize(wx.Size(self._btn_size, self._btn_size))
        btn = self.FindWindow("media_stop")
        btn.SetMinSize(wx.Size(self._btn_size, self._btn_size))
        btn = self.FindWindow("media_repeat")
        btn.SetMinSize(wx.Size(self._btn_size, self._btn_size))
        btn = self.FindWindow("volume_mute")
        btn.SetMinSize(wx.Size(self._btn_size, self._btn_size))

        btn = self.FindWindow("volume_slider")
        btn.SetMinSize(wx.Size(self._btn_size * 2, self._btn_size))

    # -----------------------------------------------------------------------

    def ShowSlider(self, value=True):
        self._slider.Show(value)

    # -----------------------------------------------------------------------

    def ShowVolume(self, value=True):
        self._volume_panel.Show(value)

    # -----------------------------------------------------------------------

    def ShowWidgets(self, value=True):
        self.widgets_panel.Show(value)

    # -----------------------------------------------------------------------

    def IsReplay(self):
        """Return True if the button to replay is enabled."""
        return self._transport_panel.FindWindow("media_repeat").IsPressed()

    # -----------------------------------------------------------------------

    def EnableReplay(self, enable=True):
        """Enable or disable the Replay button.

        The replay button should be disabled if several media of different
        durations have to be played...

        :param enable: (bool)

        """
        self._transport_panel.FindWindow("media_repeat").Enable(enable)

    # -----------------------------------------------------------------------

    def EnablePlay(self, enable=True):
        """Enable or disable the Play button.

        :param enable: (bool)

        """
        self._transport_panel.FindWindow("media_play").Enable(enable)

    # -----------------------------------------------------------------------

    def Paused(self, value=False):
        """Make the Play button in Play or Pause position.

        :param value: (bool) True to make the button in Pause position

        """
        btn = self._transport_panel.FindWindow("media_play")
        if value is True:
            btn.SetImage("media_pause")
            btn.Refresh()
        else:
            btn.SetImage("media_play")
            btn.Refresh()

    # -----------------------------------------------------------------------
    # Public methods, for the media. To be overridden.
    # -----------------------------------------------------------------------

    def play(self):
        self.notify(action="play", value=None)

    # -----------------------------------------------------------------------

    def stop(self):
        self.notify(action="stop", value=None)

    # -----------------------------------------------------------------------

    def media_rewind(self):
        """To be overridden. Seek media to some time earlier."""
        self.notify(action="rewind", value=None)

    # -----------------------------------------------------------------------

    def media_forward(self):
        """To be overridden. Seek media to some time later."""
        self.notify(action="forward", value=None)

    # -----------------------------------------------------------------------

    def media_seek(self, value):
        """To be overridden. Seek media to the given offset value (ms)."""
        self.notify(action="seek", value=value)

    # -----------------------------------------------------------------------

    def media_volume(self, value):
        """To be overridden. Adjust volume to the given scale value."""
        self.notify(action="volume", value=value)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Set the background of our panel to the given color or hi-color."""
        wx.Panel.SetBackgroundColour(self, colour)
        hi_color = self.GetHighlightedBackgroundColour()

        for name in ("transport", "widgets", "volume", "slider"):
            w = self.FindWindow(name + "_panel")
            w.SetBackgroundColour(colour)
            for c in w.GetChildren():
                if isinstance(c, BitmapTextButton) is True:
                    c.SetBackgroundColour(hi_color)
                else:
                    c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Set the foreground of our panel to the given color."""
        wx.Panel.SetForegroundColour(self, colour)

        for name in ("transport", "widgets", "volume", "slider"):
            w = self.FindWindow(name + "_panel")
            w.SetForegroundColour(colour)
            for c in w.GetChildren():
                c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        """Return a color slightly different of the parent background one."""
        color = self.GetParent().GetBackgroundColour()
        r, g, b, a = color.Red(), color.Green(), color.Blue(), color.Alpha()
        return wx.Colour(r, g, b, a).ChangeLightness(85)

    # -----------------------------------------------------------------------

    def SetButtonProperties(self, btn):
        """Set the properties of a button.

        :param btn: (BaseButton of sppas)

        """
        btn.SetFocusColour(self._focus_color)
        btn.SetFocusWidth(1)
        btn.SetSpacing(0)
        btn.SetMinSize(wx.Size(self._btn_size, self._btn_size))
        return btn

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        # Create the main anz_panels
        panel1 = self.__create_widgets_panel(self)
        panel2 = self.__create_transport_panel(self)
        panel3 = self.__create_volume_panel(self)
        slider = self.__create_slider_panel(self)

        # Organize the anz_panels into the main sizer
        border = sppasPanel.fix_size(2)
        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border)
        nav_sizer.AddStretchSpacer(1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(slider, 0, wx.EXPAND, 0)
        sizer.Add(nav_sizer, 0, wx.EXPAND | wx.ALL, border)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    @property
    def _transport_panel(self):
        """Return the panel embedding buttons to manage the media."""
        return self.FindWindow("transport_panel")

    # -----------------------------------------------------------------------

    @property
    def _slider(self):
        """Return the slider to indicate offsets, duration, etc."""
        return self.FindWindow("slider_panel")

    # -----------------------------------------------------------------------

    @property
    def _volume_panel(self):
        """Return the slider to indicate offsets."""
        return self.FindWindow("volume_panel")

    # -----------------------------------------------------------------------

    @property
    def widgets_panel(self):
        """Return the panel to be customized."""
        return self.FindWindow("widgets_panel")

    # -----------------------------------------------------------------------

    def __create_widgets_panel(self, parent):
        """Return an empty panel with a wrap sizer."""
        panel = sppasPanel(parent, name="widgets_panel")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_slider_panel(self, parent):
        """Return a panel with a slider to indicate the position in time."""
        # TODO: return TimeSliderPanel(parent, name="slider_panel")

        slider = wx.Slider(self, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        slider.SetRange(0, 0)
        slider.SetValue(0)
        slider.SetName("slider_panel")
        slider.SetMinSize(wx.Size(-1, 4 * self.get_font_height()))

        return slider

    # -----------------------------------------------------------------------

    def __create_transport_panel(self, parent):
        """Return a panel with the buttons to play/pause/stop the media."""
        panel = sppasPanel(parent, name="transport_panel")

        btn_rewind = BitmapTextButton(panel, name="media_rewind")
        self.SetButtonProperties(btn_rewind)
        btn_rewind.SetMinSize(wx.Size(self._btn_size // 2, self._btn_size))

        btn_play = BitmapTextButton(panel, name="media_play")
        self.SetButtonProperties(btn_play)
        btn_play.SetFocus()

        btn_forward = BitmapTextButton(panel, name="media_forward")
        self.SetButtonProperties(btn_forward)
        btn_forward.SetMinSize(wx.Size(self._btn_size // 2, self._btn_size))

        btn_stop = BitmapTextButton(panel, name="media_stop")
        self.SetButtonProperties(btn_stop)

        btn_replay = ToggleButton(panel, name="media_repeat")
        btn_replay = self.SetButtonProperties(btn_replay)
        btn_replay.SetBorderWidth(1)

        border = sppasPanel.fix_size(2)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btn_rewind, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_play, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_forward, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_stop, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_replay, 0, wx.ALL | wx.ALIGN_CENTER, border)
        panel.SetSizer(sizer)

        return panel

    # -----------------------------------------------------------------------

    def __create_volume_panel(self, parent):
        """Return a panel with a slider for the volume and a mute button."""
        panel = sppasPanel(parent, name="volume_panel")

        btn_mute = ToggleButton(panel, name="volume_mute")
        btn_mute.SetImage("volume_high")
        self.SetButtonProperties(btn_mute)
        btn_mute.SetBorderWidth(1)

        # Labels of wx.Slider are not supported under MacOS.
        slider = wx.Slider(panel, style=wx.SL_HORIZONTAL)  # | wx.SL_MIN_MAX_LABELS)
        slider.SetName("volume_slider")
        slider.SetValue(100)
        slider.SetRange(0, 100)
        slider.SetMinSize(wx.Size(self._btn_size * 2, self._btn_size))

        border = sppasPanel.fix_size(2)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btn_mute, 0, wx.ALIGN_CENTER | wx.ALL, border)
        sizer.Add(slider, 1, wx.EXPAND, border)
        panel.SetSizer(sizer)

        return panel

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
        wx.LogDebug("Send action event to parent {:s}".format(self.GetParent().GetName()))
        evt = MediaEvents.MediaActionEvent(action=action, value=value)
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

        # The slider position has changed.
        # Currently not supported by the sppasSlider.
        self.Bind(wx.EVT_SLIDER, self._process_action)

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "media_play":
            self.play()

        elif name == "media_stop":
            self.stop()

        elif name == "media_rewind":
            self.media_rewind()

        elif name == "media_forward":
            self.media_forward()

        elif name == "volume_mute":
            self.__action_volume(to_notify=True)

        elif name == "volume_slider":
            self.__action_volume(to_notify=False)

        elif name == "slider_panel":
            # todo: notify parent to get authorization to seek...
            # then it'll the parent to call the media_seek method.
            self.media_seek(obj.GetValue())

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
                self.media_volume(0.)

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
            self.media_volume(volume)

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        p1 = sppasPlayerControlsPanel(self)
        btn1 = BitmapTextButton(p1.widgets_panel, name="way_up_down")
        p1.SetButtonProperties(btn1)
        p1.AddWidget(btn1)
        p1.Bind(MediaEvents.EVT_MEDIA_ACTION, self.process_action)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.SetForegroundColour(wx.Colour(225, 225, 225))

    def process_action(self, evt):
        wx.LogDebug("Action received: {:s} with value={:s}"
                    "".format(evt.action, str(evt.value)))
