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

from sppas.src.ui.phoenix.windows.buttons import ToggleButton
from sppas.src.ui.phoenix.windows.buttons import BitmapTextButton, BitmapButton
from sppas.src.ui.phoenix.windows.panels import sppasImagePanel, sppasPanel

from .mediaevents import MediaEvents
from .timeslider import TimeSliderPanel

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

        self._btn_size = sppasPanel.fix_size(24)
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
        value = sppasPanel.fix_size(value)
        self._btn_size = min(value, sppasPanel.fix_size(128))
        self._btn_size = max(self._btn_size, sppasPanel.fix_size(12))

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
        """To be overridden."""
        self.notify(action="period", value=(start, end))

    # -----------------------------------------------------------------------
    # Construct the GUI
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
        nav_panel = sppasPanel(self, name="nav_panel")
        panel1 = self.__create_widgets_left_panel(nav_panel)
        panel3 = self.__create_widgets_right_panel(nav_panel)
        panel2 = self.__create_transport_panel(nav_panel)

        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nav_sizer.Add(panel1, 1, wx.EXPAND | wx.RIGHT, sppasPanel.fix_size(2))
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel2, 1, wx.EXPAND)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(panel3, 1, wx.EXPAND | wx.LEFT, sppasPanel.fix_size(2))
        nav_panel.SetSizer(nav_sizer)

        slider = TimeSliderPanel(self, name="slider_panel")

        # Under MacOS and Linux, the scrollbar is transparent over a window, so
        # its size won't change if it appear or disappear. BUT, under Windows,
        # the scrollbar is drawn beside the window so its size (actually only
        # the width) is changed!!!! If we want that our slider is vertically
        # aligned with some other panels into a scrolled panel, we need to have
        # a border at right.
        border = 0
        if wx.Platform == "__WXMSW__":
            # get the width of a scrollbar
            s = wx.ScrollBar(self, style=wx.SB_VERTICAL)
            w, _ = s.GetSize()
            s.Destroy()
            # and use it for the border at right
            border = w

        # Organize the panels into the main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nav_panel, 0, wx.EXPAND | wx.RIGHT, border)
        sizer.Add(slider, 0, wx.EXPAND | wx.RIGHT, border)

        self.SetSizerAndFit(sizer)

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
        """Handle the event of a change of time range in the slider."""
        p = event.period
        self.media_period(p[0], p[1])

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="PlayControls Panel")

        panel = sppasPlayerControlsPanel(self)
        panel.SetMinSize(wx.Size(640, 120))
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(panel, 1, wx.EXPAND)
        self.SetSizer(s)
