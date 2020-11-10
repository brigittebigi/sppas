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
import wx.lib.gizmos as gizmos

from sppas.src.config import paths  # used only in the Test Panel

from ..buttons import ToggleButton
from ..buttons import BitmapTextButton, BitmapButton
from ..panels import sppasImagePanel, sppasPanel
from ..frame import sppasImageFrame

from .mediaevents import MediaEvents
from .timeslider import TimeSliderPanel
from .smmps import sppasMMPS  # used only in the Test Panel

# ---------------------------------------------------------------------------


class TogglePause(ToggleButton):
    """A toggle button with a specific design and properties.

     :author:       Brigitte Bigi
     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
     :contact:      contact@sppas.org
     :license:      GPL, v3
     :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size.

        The name of the button is "media_pause" by default; use SetName()
        to change it after creation.

        """
        super(TogglePause, self).__init__(parent, id, label, pos, size, "media_pause")
        self.Enable(False)
        self.SetValue(False)

# ---------------------------------------------------------------------------


class PressPlay(BitmapButton):
    """A toggle button with a specific design and properties.

     :author:       Brigitte Bigi
     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
     :contact:      contact@sppas.org
     :license:      GPL, v3
     :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    COLOUR = wx.Colour(48, 96, 250)
    # BG_IMAGE = os.path.join(paths.etc, "images", "bg_brushed_metal2.jpg")

    # -----------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param pos: the position;
        :param size: the size.

        The name of the button is "media_play" by default; use SetName()
        to change it after creation.

        """
        super(PressPlay, self).__init__(parent, id, pos, size, "media_play")
        self.Enable(False)
        # self.SetBackgroundImage(PressPlay.BG_IMAGE)

    # -----------------------------------------------------------------------
    #
    # def Enable(self, value):
    #     BitmapButton.Enable(self, value)
    #     if self.IsEnabled() is True:
    #         self.SetForegroundColour(PressPlay.COLOUR)
    #     else:
    #         self.SetForegroundColour(self.GetParent().GetForegroundColour())

# ---------------------------------------------------------------------------


class sppasPlayerControlsPanel(sppasImagePanel):
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
                 image=None,
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
            parent, id, image, pos, size, style, name)

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
        self.FindWindow("media_pause").SetFocusColour(colour)
        self.FindWindow("media_stop").SetFocusColour(colour)
        self.FindWindow("media_rewind").SetFocusColour(colour)
        self.FindWindow("media_forward").SetFocusColour(colour)
        self.FindWindow("media_repeat").SetFocusColour(colour)

    # -----------------------------------------------------------------------

    def AddLeftWidget(self, wxwindow):
        """Add a widget into the customizable panel.

        :param wxwindow: (wx.Window)
        :return: True if added, False if parent does not match.

        """
        if wxwindow.GetParent() != self.widgets_left_panel:
            return False
        self.widgets_left_panel.GetSizer().Add(
            wxwindow, 0, wx.ALIGN_CENTER | wx.ALL, sppasPanel.fix_size(2))
        self.widgets_left_panel.Show(True)
        return True

    # -----------------------------------------------------------------------

    def AddRightWidget(self, wxwindow):
        """Add a widget into the customizable panel.

        :param wxwindow: (wx.Window)
        :return: True if added, False if parent does not match.

        """
        if wxwindow.GetParent() != self.widgets_right_panel:
            return False
        self.widgets_right_panel.GetSizer().Add(
            wxwindow, 0, wx.ALIGN_CENTER | wx.ALL, sppasPanel.fix_size(2))
        self.widgets_right_panel.Show(True)
        return True

    # -----------------------------------------------------------------------

    def SetButtonWidth(self, value):
        """Fix the width/height of the buttons.

        The given value will be adjusted to a proportion of the font height.
        Min is 12, max is 128.
        The buttons are not refreshed.

        """
        self._btn_size = min(sppasPanel.fix_size(value), 128)
        self._btn_size = max(self._btn_size, 12)

        for name in ("rewind", "forward"):
            btn = self.FindWindow("media_"+name)
            btn.SetMinSize(wx.Size(self._btn_size // 2, self._btn_size))

        for name in ("play", "pause", "stop", "repeat"):
            btn = self.FindWindow("media_" + name)
            btn.SetMinSize(wx.Size(self._btn_size, self._btn_size))

    # -----------------------------------------------------------------------

    def ShowSlider(self, value=True):
        self._timeslider.Show(value)

    # -----------------------------------------------------------------------

    def ShowLeftWidgets(self, value=True):
        self.widgets_left_panel.Show(value)

    # -----------------------------------------------------------------------

    def ShowRightWidgets(self, value=True):
        self.widgets_right_panel.Show(value)

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
    # Public methods, for the media. To be overridden.
    # -----------------------------------------------------------------------

    def play(self):
        """To be overridden. Start playing media."""
        self.notify(action="play", value=None)

    # -----------------------------------------------------------------------

    def pause(self):
        """To be overridden. Pause in playing media."""
        self.notify(action="pause", value=None)

    # -----------------------------------------------------------------------

    def stop(self):
        """To be overridden. Stop playing media."""
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
        """To be overridden. Seek media to the given time value."""
        self.notify(action="seek", value=value)

    # -----------------------------------------------------------------------

    def media_period(self, start, end):
        """To be overridden. Set the time period of the media to the given range."""
        self.notify(action="period", value=(start, end))

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
        panel1 = self.__create_widgets_left_panel(self)
        panel3 = self.__create_widgets_right_panel(self)
        panel2 = self.__create_transport_panel(self)
        slider = TimeSliderPanel(self, name="slider_panel")

        border = sppasPanel.fix_size(2)
        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nav_sizer.Add(panel1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border)

        # Organize the panels into the main sizer
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
    def _timeslider(self):
        """Return the slider to indicate offsets, duration, etc."""
        return self.FindWindow("slider_panel")

    # -----------------------------------------------------------------------

    @property
    def widgets_left_panel(self):
        """Return the panel to be customized."""
        return self.FindWindow("widgets_left_panel")

    # -----------------------------------------------------------------------

    @property
    def widgets_right_panel(self):
        """Return the panel to be customized."""
        return self.FindWindow("widgets_right_panel")

    # -----------------------------------------------------------------------

    def __create_widgets_left_panel(self, parent):
        """Return an empty panel with a sizer."""
        panel = sppasPanel(parent, name="widgets_left_panel")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_widgets_right_panel(self, parent):
        """Return an empty panel with a sizer."""
        panel = sppasPanel(parent, name="widgets_right_panel")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_transport_panel(self, parent):
        """Return a panel with the buttons to play/pause/stop the media."""
        panel = sppasPanel(parent, name="transport_panel")

        btn_rewind = BitmapTextButton(panel, name="media_rewind")
        self.SetButtonProperties(btn_rewind)
        btn_rewind.SetMinSize(wx.Size(self._btn_size // 2, self._btn_size))

        btn_play = PressPlay(panel)
        self.SetButtonProperties(btn_play)

        btn_pause = TogglePause(panel)
        self.SetButtonProperties(btn_pause)

        btn_forward = BitmapTextButton(panel, name="media_forward")
        self.SetButtonProperties(btn_forward)
        btn_forward.SetMinSize(wx.Size(self._btn_size // 2, self._btn_size))

        btn_stop = BitmapTextButton(panel, name="media_stop")
        self.SetButtonProperties(btn_stop)
        btn_stop.SetFocus()

        btn_replay = ToggleButton(panel, name="media_repeat")
        btn_replay = self.SetButtonProperties(btn_replay)
        btn_replay.SetBorderWidth(1)

        border = sppasPanel.fix_size(2)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btn_rewind, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_play, 0, wx.ALL | wx.ALIGN_CENTER, border)
        sizer.Add(btn_pause, 0, wx.ALL | wx.ALIGN_CENTER, border)
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
        self.FindWindow("media_play").Bind(wx.EVT_BUTTON, self._process_action)
        self.FindWindow("media_stop").Bind(wx.EVT_BUTTON, self._process_action)
        self.FindWindow("media_rewind").Bind(wx.EVT_BUTTON, self._process_action)
        self.FindWindow("media_forward").Bind(wx.EVT_BUTTON, self._process_action)
        self.FindWindow("media_pause").Bind(wx.EVT_TOGGLEBUTTON, self._process_action)

        # The slider position has changed. Currently not supported by the sppasSlider.
        self.Bind(wx.EVT_SLIDER, self._process_action)

        # Event received when the period of the slider has changed
        self.Bind(MediaEvents.EVT_MEDIA_PERIOD, self._on_period_changed)

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()
        wx.LogDebug("Action to perform: {}".format(name.replace("media_", "")))

        if name == "media_play":
            self.play()

        elif name == "media_pause":
            self.pause()

        elif name == "media_stop":
            self.stop()

        elif name == "media_rewind":
            self.media_rewind()

        elif name == "media_forward":
            self.media_forward()

        else:
            event.Skip()

    # ----------------------------------------------------------------------

    def _on_period_changed(self, event):
        p = event.period
        self.media_period(p[0], p[1])

# ---------------------------------------------------------------------------


class PlayerExamplePanel(sppasPlayerControlsPanel):

    # BG_IMAGE = os.path.join(paths.etc, "images", "bg_brushed_metal.jpg")

    # ----------------------------------------------------------------------

    def __init__(self, parent):
        super(PlayerExamplePanel, self).__init__(
            parent,
            #image=PlayerExamplePanel.BG_IMAGE,
            name="player_panel")

        self.smmps = sppasMMPS(self)  # the SPPAS Multi Media Player system
        # self.prev_time = None

        btn1 = BitmapTextButton(self.widgets_left_panel, name="scroll_left")
        self.SetButtonProperties(btn1)
        self.AddLeftWidget(btn1)
        btn1.Bind(wx.EVT_BUTTON, self._on_set_visible)

        btn3 = BitmapTextButton(self.widgets_left_panel, name="expand_false")
        self.SetButtonProperties(btn3)
        self.AddLeftWidget(btn3)
        btn3.Bind(wx.EVT_BUTTON, self._on_set_visible)

        btn4 = BitmapTextButton(self.widgets_left_panel, name="expand_true")
        self.SetButtonProperties(btn4)
        self.AddLeftWidget(btn4)
        btn4.Bind(wx.EVT_BUTTON, self._on_set_visible)

        btn7 = BitmapTextButton(self.widgets_left_panel, name="scroll_zoom_all")
        self.SetButtonProperties(btn7)
        self.AddLeftWidget(btn7)
        btn7.Bind(wx.EVT_BUTTON, self._on_set_visible)

        btn5 = BitmapTextButton(self.widgets_left_panel, name="scroll_to_selection")
        self.SetButtonProperties(btn5)
        self.AddLeftWidget(btn5)
        btn5.Bind(wx.EVT_BUTTON, self._on_set_visible)

        btn6 = BitmapTextButton(self.widgets_left_panel, name="scroll_zoom_selection")
        self.SetButtonProperties(btn6)
        self.AddLeftWidget(btn6)
        btn6.Bind(wx.EVT_BUTTON, self._on_set_visible)

        btn2 = BitmapTextButton(self.widgets_left_panel, name="scroll_right")
        self.SetButtonProperties(btn2)
        self.AddLeftWidget(btn2)
        btn2.Bind(wx.EVT_BUTTON, self._on_set_visible)

        led = gizmos.LEDNumberCtrl(self.widgets_left_panel, name="moment_led")
        led.SetValue("0.000")
        led.SetAlignment(gizmos.LED_ALIGN_RIGHT)
        led.SetDrawFaded(True)
        led.SetMinSize(wx.Size(self.get_font_height()*10, self.get_font_height()*3))
        led.SetForegroundColour(wx.Colour(40, 90, 220))
        self.AddLeftWidget(led)

        # Events
        # Custom event to inform the media is loaded
        self.smmps.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.smmps.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        # Event received every X ms when the audio is playing
        self.Bind(wx.EVT_TIMER, self._on_timer)

        self.Layout()

    # ----------------------------------------------------------------------

    def load_files(self, with_threads=True):
        self.FindWindow("media_play").Enable(False)

        # Loading the videos with threads make the app crashing under MacOS:
        # Python[31492:1498940] *** Terminating app due to uncaught exception
        # 'NSInternalInconsistencyException', reason: 'NSWindow drag regions
        # should only be invalidated on the Main Thread!'
        player = sppasImageFrame(
            parent=self,  # if parent is destroyed, the frame will be too
            title="Video",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT)

        self.smmps.add_video([os.path.join(paths.samples, "faces", "video_sample.mp4")],
                             player)

        # To load files in parallel, with threads:
        if with_threads is True:
            self.smmps.add_audio(
                [os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"),
                 os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"),
                 os.path.join(paths.samples, "samples-eng", "oriana1.wav"),
                 os.path.join(paths.samples, "samples-eng", "oriana2.WAV"),
                 ])

        else:
            # To load files sequentially, without threads:
            self.smmps.add_audio(os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
            self.smmps.add_audio(os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))
            self.smmps.add_audio(os.path.join(paths.samples, "samples-eng", "oriana1.wav"))
            self.smmps.add_audio(os.path.join(paths.samples, "samples-eng", "oriana2.WAV"))

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        filename = event.filename
        self.smmps.enable(filename)
        self.FindWindow("media_play").Enable(True)
        self.FindWindow("media_pause").Enable(True)

        duration = self.smmps.get_duration()
        self._timeslider.set_duration(duration)
        # Under MacOS, the following line enters in an infinite loop with the message:
        #   In file /Users/robind/projects/bb2/dist-osx-py38/build/ext/wxWidgets/src/unix/threadpsx.cpp at line 370: 'pthread_mutex_[timed]lock()' failed with error 0x00000023 (Resource temporarily unavailable).
        # Under Linux it crashes with the message:
        #   pure virtual method called
        # self.smmps.set_period(0., duration)

        # to test if it works, set a selection period and a visible period:
        self._timeslider.set_visible_range(3.45, 7.08765)
        self._timeslider.set_selection_range(5.6, 6.8)
        self.Layout()

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        filename = event.filename
        wx.LogError("File {} not loaded".format(filename))
        # self.smmps.remove(filename)

    # -----------------------------------------------------------------------
    # the methods to override...
    # -----------------------------------------------------------------------

    def play(self):
        wx.LogDebug("Play")
        if self.smmps.is_playing() is False and self.smmps.is_loading() is False:
            if self.smmps.is_paused() is False:
                start, end = self._timeslider.get_range()
                self.smmps.set_period(start, end)
            played = self.smmps.play()
            if played is True:
                # self.prev_time = datetime.datetime.now()
                self.FindWindow("media_pause").SetValue(False)

    # -----------------------------------------------------------------------

    def pause(self):
        pause_status = self.FindWindow("media_pause").GetValue()

        # It was asked to pause
        if pause_status is True:
            # and the audio is not already paused
            if self.smmps.is_paused() is False:
                paused = self.smmps.pause()
                if paused is not True:
                    # but paused was not done in the audio
                    self.FindWindow("media_pause").SetValue(False)
                else:

                    # Put the slider exactly at the right time position
                    position = self.smmps.tell()
                    self._timeslider.set_value(position)
                    self.FindWindow("moment_led").SetValue("{:.3f}".format(position))

        else:
            # it was asked to end pausing
            if self.smmps.is_paused() is True:
                self.play()

    # -----------------------------------------------------------------------

    def stop(self):
        wx.LogDebug("Stop")
        self.smmps.stop()
        # self.prev_time = None
        self.DeletePendingEvents()
        self.FindWindow("media_pause").SetValue(False)

        # Put the slider exactly at the right time position
        position = self.smmps.tell()
        self._timeslider.set_value(position)
        self.FindWindow("moment_led").SetValue("{:.3f}".format(position))

    # -----------------------------------------------------------------------

    def media_rewind(self):
        """Seek media 10% earlier."""
        wx.LogDebug("Rewind")
        d = self.smmps.get_duration()
        d /= 10.
        cur = self.smmps.tell()
        period = self._timeslider.get_range()

        self.smmps.seek(max(period[0], cur - d))
        position = self.smmps.tell()
        self._timeslider.set_value(position)
        self.FindWindow("moment_led").SetValue("{:.3f}".format(position))

    # -----------------------------------------------------------------------

    def media_forward(self):
        """Override. Seek media 10% later."""
        wx.LogDebug("Forward")
        duration = self.smmps.get_duration()
        d = duration / 10.
        cur = self.smmps.tell()
        period = self._timeslider.get_range()
        position = min(cur + d, period[1])

        # if we reach the end of the stream for the given period
        if position == period[1] and self.IsReplay() is True:
            position = 0.  # restart from the beginning

        self.smmps.seek(position)
        position = self.smmps.tell()
        self._timeslider.set_value(position)
        self.FindWindow("moment_led").SetValue("{:.3f}".format(position))

    # -----------------------------------------------------------------------

    def media_seek(self, value):
        """Override. Seek media at given time value."""
        wx.LogDebug("Seek at {}".format(value))
        self.smmps.seek(value)
        self._timeslider.set_value(value)
        self.FindWindow("moment_led").SetValue("{:.3f}".format(value))

    # -----------------------------------------------------------------------

    def media_period(self, start, end):
        """Override. Set time period to media at given time range."""
        # self.smmps.set_period(start, end)
        value = self.smmps.tell()
        self._timeslider.set_value(value)
        self.FindWindow("moment_led").SetValue("{:.3f}".format(value))

    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        # at least one audio is still playing
        if self.smmps.is_playing() is True:
            # if we doesn't want to update the slider so frequently:
            # cur_time = datetime.datetime.now()
            # delta = cur_time - self.prev_time
            # delta_seconds = delta.seconds + delta.microseconds / 1000000.
            # if delta_seconds > self.delta_slider:
            # self.prev_time = cur_time
            time_pos = self.smmps.tell()
            self._timeslider.set_value(time_pos)
            self.FindWindow("moment_led").SetValue("{:.3f}".format(time_pos))

        # all enabled audio are now stopped
        elif self.smmps.are_stopped() is True:
            self.stop()
            if self.IsReplay() is True:
                self.play()

        # event.Skip()

    # ----------------------------------------------------------------------

    def _on_set_visible(self, event):
        """Change the visible part.

        Scroll the visible part, depending on its current duration:
            - reduce of 50%
            - increase of 100%
            - shift 80% before
            - shift 80% after

        """
        evt_obj = event.GetEventObject()
        cur_period = self._timeslider.get_range()
        start = self._timeslider.get_visible_start()
        end = self._timeslider.get_visible_end()
        dur = end - start
        if evt_obj.GetName() == "expand_false":
            shift = dur / 4.
            self._timeslider.set_visible_range(start + shift, end - shift)
        elif evt_obj.GetName() == "expand_true":
            shift = dur / 2.
            self._timeslider.set_visible_range(start - shift, end + shift)
        elif evt_obj.GetName() == "scroll_left":
            shift = 0.8 * dur
            if start > 0.:
                self._timeslider.set_visible_range(start - shift, end - shift)
        elif evt_obj.GetName() == "scroll_right":
            shift = 0.8 * dur
            if end < self._timeslider.get_duration():
                self._timeslider.set_visible_range(start + shift, end + shift)
        elif evt_obj.GetName() == "scroll_to_selection":
            sel_start = self._timeslider.get_selection_start()
            sel_end = self._timeslider.get_selection_end()
            sel_middle = sel_start + ((sel_end - sel_start) / 2.)
            shift = dur / 2.
            self._timeslider.set_visible_range(sel_middle - shift, sel_middle + shift)
        elif evt_obj.GetName() == "scroll_zoom_selection":
            sel_start = self._timeslider.get_selection_start()
            sel_end = self._timeslider.get_selection_end()
            self._timeslider.set_visible_range(sel_start, sel_end)
        elif evt_obj.GetName() == "scroll_zoom_all":
            end = self._timeslider.get_duration()
            self._timeslider.set_visible_range(0., end)
        else:
            wx.LogError("Unknown visible action {}".format(evt_obj.GetName()))
            return

        self._timeslider.Layout()
        self._timeslider.Refresh()

        new_period = self._timeslider.get_range()
        if new_period != cur_period:
            self.smmps.set_period(new_period[0], new_period[1])

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="PlayControls Panel")

        button = wx.Button(self, -1, pos=(10, 10), size=(100, 50), label="LOAD", name="load_button")
        panel = PlayerExamplePanel(self)
        panel.SetMinSize(wx.Size(640, 120))
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(button, 0)
        s.Add(panel, 1, wx.EXPAND)
        self.SetSizer(s)
        button.Bind(wx.EVT_BUTTON, self._on_load)

    def _on_load(self, event):
        self.FindWindow("player_panel").load_files()
        self.FindWindow("load_button").Enable(False)
