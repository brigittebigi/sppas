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

    src.ui.phoenix.windows.media.baseplaypanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A base class panel to display buttons to manage the actions on the media
    player. Some methods must be overridden to be able to play/pause/stop/...

    Can play audio and video, based on our customs audioplayer/videoplayer.
    Requires the following libraries:

     - simpleaudio, installed by the audioplay feature;
     - opencv, installed by the videoplay feature.

"""

import wx
import os
import datetime

from sppas.src.config import paths  # used only in the Test Panel

from ..buttons import ToggleButton
from ..buttons import BitmapTextButton
from ..panels import sppasPanel

from .mediaevents import MediaEvents
from .timeslider import TimeSliderPanel
from .audioplay import sppasAudioPlayer  # used only in the Test Panel

# ---------------------------------------------------------------------------


class sppasPlayerControlsPanel(sppasPanel):
    """Create a panel with controls to manage media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Three children are to be created and organized into a BoxSizer:
        - widgets_panel: a customizable panel, free to be used to add widgets
        - transport_panel: all buttons to play a media
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

    # -----------------------------------------------------------------------

    def ShowSlider(self, value=True):
        self._slider.Show(value)

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
    # Construct the GUI
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Set the background of our panel to the given color or hi-color."""
        wx.Panel.SetBackgroundColour(self, colour)
        hi_color = self.GetHighlightedBackgroundColour()

        for name in ("transport", "widgets", "slider"):
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

        for name in ("transport", "widgets", "slider"):
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
        slider = self.__create_slider_panel(self)

        # Organize the anz_panels into the main sizer
        border = sppasPanel.fix_size(2)
        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border)
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
        slider = TimeSliderPanel(parent, name="slider_panel")

        # slider = wx.Slider(self, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        # slider.SetRange(0, 0)
        # slider.SetValue(0)
        # slider.SetName("slider_panel")
        slider.SetMinSize(wx.Size(-1, 3 * self.get_font_height()))

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
    # Manage events
    # -----------------------------------------------------------------------

    def notify(self, action, value=None):
        """The parent has to be informed that an action is required.

        An action can be:
            - play/stop/rewind/forward, without value;
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

        elif name == "slider_panel":
            # todo: notify parent to get authorization to seek...
            # then it'll the parent to call the media_seek method.
            self.media_seek(obj.GetValue())

        else:
            event.Skip()

# ---------------------------------------------------------------------------


class TestPanel(sppasPlayerControlsPanel):

    AUDIO = os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav")
    SLIDER_UPDATE_DELAY = 0.100   # update the slider every 100ms only

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Base PlayControls Panel")

        self.audio = sppasAudioPlayer(self)
        self.prev_time = None

        btn1 = BitmapTextButton(self.widgets_panel, name="way_up_down")
        self.SetButtonProperties(btn1)
        self.AddWidget(btn1)

        # Events
        # Custom event to inform the media is loaded
        self.audio.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.audio.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        # Event received every Xms when the audio is playing
        self.audio.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        self.FindWindow("media_play").Enable(False)
        self.audio.load(TestPanel.AUDIO)

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        wx.LogDebug("Audio file loaded successfully")
        self.FindWindow("media_play").Enable(True)
        # duration = self.audio.get_duration()
        # self._slider.SetRange(0, int(duration * 1000.))

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        wx.LogError("Audio file not loaded")
        # self._slider.SetRange(0, 0)

    # -----------------------------------------------------------------------
    # the methods to override...
    # -----------------------------------------------------------------------

    def play(self):
        wx.LogDebug("Play")
        played = self.audio.play()
        if played is True:
            self.prev_time = datetime.datetime.now()

    # -----------------------------------------------------------------------

    def stop(self):
        wx.LogDebug("Stop")
        if self.audio.is_stopped() is False:
            self.audio.stop()
        self.prev_time = None
        self.DeletePendingEvents()

    # -----------------------------------------------------------------------

    def media_rewind(self):
        """Seek media 10% earlier."""
        wx.LogDebug("Rewind")
        d = self.audio.get_duration()
        d /= 10.
        cur = self.audio.tell()
        self.audio.seek(max(0., cur - d))

    # -----------------------------------------------------------------------

    def media_forward(self):
        """Seek media 10% later."""
        wx.LogDebug("Forward")
        duration = self.audio.get_duration()
        d = duration / 10.
        cur = self.audio.tell()

        position = cur + d
        # if we reach the end of the stream
        if position > duration:
            if self.IsReplay() is True:
                position = 0.  # restart from the beginning
            else:
                position = duration

        self.audio.seek(position)

    # -----------------------------------------------------------------------

    def media_seek(self, value):
        wx.LogDebug("Seek at {}".format(value))
        self.audio.seek(value)
        # self._slider.Seek(value)

    # ----------------------------------------------------------------------

    def _on_timer(self, event):

        if self.audio.is_stopped() is True:
            self.stop()
            if self.IsReplay() is True:
                self.play()
        else:
            cur_time = datetime.datetime.now()
            delta = cur_time - self.prev_time
            delta_seconds = delta.seconds + delta.microseconds / 1000000.
            if delta_seconds > TestPanel.SLIDER_UPDATE_DELAY:
                self.prev_time = cur_time
                time_pos = self.audio.tell()
                # self._slider.SetValue(int(time_pos * 1000.))
                wx.LogDebug("Update the slider at time {}".format(time_pos))

        # event.Skip()
