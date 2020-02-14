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

import os
import time
import wx
import wx.media

from sppas.src.config import paths

from ..button import ToggleButton, BitmapTextButton
from ..panel import sppasPanel
from .mediatest import sppasMediaPanel
from .mediaevents import MediaEvents
from .mediactrl import MediaType

# ---------------------------------------------------------------------------


class sppasPlayerControlsPanel(sppasPanel):
    """Create a panel with controls for media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Four children panels are to be created and organized into a BoxSizer:
        - widgets_panel: a panel, free to be used to add widgets
        - transport_panel: all buttons to play a media and a slider
        - volume_panel: a button to mute and a slider to adjust the volume
        - slider_panel: a wx.Slider

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

        self._create_content()
        self._setup_events()

        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods, for the controls
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
        return self.FindWindow("seek_slider")

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
    # Public methods, for the media
    # -----------------------------------------------------------------------

    def play(self):
        self.notify(action="play", value=None)

    # -----------------------------------------------------------------------

    def stop(self):
        self.notify(action="stop", value=None)

    # -----------------------------------------------------------------------

    def rewind(self):
        self.notify(action="rewind", value=None)

    # -----------------------------------------------------------------------

    def forward(self):
        self.notify(action="forward", value=None)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """"""
        wx.Panel.SetBackgroundColour(self, colour)
        hi_color = self.GetHighlightedColour()

        for name in ("transport", "widgets", "volume"):
            w = self.FindWindow(name + "_panel")
            for c in w.GetChildren():
                if isinstance(c, BitmapTextButton) is True:
                    c.SetBackgroundColour(hi_color)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
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

        btn_rewind = BitmapTextButton(panel, name="media_rewind")
        self.SetButtonProperties(btn_rewind)

        btn_play = BitmapTextButton(panel, name="media_play")
        self.SetButtonProperties(btn_play)
        btn_play.SetFocus()
        btn_play.SetMinSize(wx.Size(sppasPanel.fix_size(32),
                                    sppasPanel.fix_size(32)))

        btn_forward = BitmapTextButton(panel, name="media_forward")
        self.SetButtonProperties(btn_forward)

        btn_stop = BitmapTextButton(panel, name="media_stop")
        self.SetButtonProperties(btn_stop)

        btn_replay = ToggleButton(panel, name="media_repeat")
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

        btn_mute = ToggleButton(panel, name="volume_mute")
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

    def GetHighlightedColour(self):
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

        # The slider position has changed
        self.Bind(wx.EVT_SLIDER, self._process_action)

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()
        wx.LogDebug("Process action from {:s}".format(name))

        if name == "media_play":
            wx.LogMessage("PLAY ACTION")
            self.play()

        elif name == "media_stop":
            self.stop()

        elif name == "media_rewind":
            self.rewind()

        elif name == "media_forward":
            self.forward()

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


class sppasMultiPlayerPanel(sppasPlayerControlsPanel):
    """Create a panel with controls to manage a list of media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    A player controls panel to play several media at a time.

    """

    def __init__(self, parent, id=-1,
                 media=list(),
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="multi_player_panel"):
        """Create a sppasMultiPlayerPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param media: (list) List of wx.media.MediaCtrl
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        """
        super(sppasMultiPlayerPanel, self).__init__(
            parent, id, pos, size, style, name)

        self.__media = media
        self._length = 0
        self._offsets = (0, 0)
        self._autoreplay = True
        self._timer = wx.Timer(self)
        self._refreshtimer = 40
        self.Bind(wx.EVT_TIMER, self.OnTimer)

    # -----------------------------------------------------------------------

    def set_media(self, media_lst):
        """Set a new list of media.

        :param media_lst: (list)

        """
        self.__reset()
        self.__media = list()

        for m in media_lst:
            self.__add_and_init_media(m)

        # re-evaluate length
        self._length = max(m.Length() for m in self.__media)

        # validate current offsets
        self.__validate_offsets()

        # seek at the beginning of the period
        self.media_seek(self._offsets[0])

    # -----------------------------------------------------------------------

    def __add_and_init_media(self, m):
        try:
            m.Play()
            time.sleep(0.1)
            m.Stop()
            self.__media.append(m)
        except Exception as e:
            wx.LogError(str(e))

    # -----------------------------------------------------------------------

    def add_media(self, media):
        """Add a media into the list of media managed by this control."""
        if media in self.__media:
            return False
        self.__media.append(media)

        # seek the new media to the current position.
        media.seek(self.media_tell())

        # re-evaluate length
        self._length = max(m.Length() for m in self.__media)

    # -----------------------------------------------------------------------

    def media_playing(self):
        """Return the first media we found playing, None instead."""
        for m in self.__media:
            if m.GetState() == wx.media.MEDIASTATE_PLAYING:
                return m
        return None

    # -----------------------------------------------------------------------

    def media_paused(self):
        """Return the first media we found playing, None instead."""
        for m in self.__media:
            if m.GetState() == wx.media.MEDIASTATE_PAUSED:
                return m
        return None

    # -----------------------------------------------------------------------

    def media_stopped(self):
        """Return the first media we found playing, None instead."""
        for m in self.__media:
            if m.GetState() == wx.media.MEDIASTATE_STOPPED:
                return m
        return None

    # -----------------------------------------------------------------------

    def media_tell(self):
        """Return the actual position in time in a media."""
        # In theory, all media should return the same value... but framerate
        # of the media are different. Tell() in an audio is more precise.
        # And in theory it should be equal to the cursor value.
        value = self.GetSlider().GetValue()
        wx.LogMessage("MEDIA TELL. SLIDER VALUE IS {:d}".format(value))
        # Search for an audio first
        for m in self.__media:
            if m.GetMediaType() == MediaType().audio:
                wx.LogMessage("MEDIA TELL. AUDIO VALUE IS {:d}".format(m.Tell()))
                return m.Tell()
        # No audio... search for a video
        for m in self.__media:
            if m.GetMediaType() == MediaType().video:
                wx.LogMessage("MEDIA TELL. VIDEO VALUE IS {:d}".format(m.Tell()))
                return m.Tell()

        # No audio nor video in the list of media
        wx.LogMessage("MEDIA TELL. No audio nor video. VALUE IS 0")
        return 0

    # -----------------------------------------------------------------------

    def media_seek(self, offset):

        if offset < self._offsets[0]:
            offset = self._offsets[0]
        if offset > self._offsets[1]:
            offset = self._offsets[1]

        for m in self.__media:
            m.Seek(offset)

    # -----------------------------------------------------------------------

    def play(self):
        """Override. Play the media and notify parent."""
        wx.LogMessage("Play media... period is {:s}".format(str(self._offsets)))
        self._timer.Start(self._refreshtimer)
        self.notify(action="play", value=None)
        for m in self.__media:
            if m.GetMediaType() == MediaType().video:
                m.Play()
        for m in self.__media:
            if m.GetMediaType() == MediaType().audio:
                m.Play()

    # -----------------------------------------------------------------------

    def stop(self):
        """Override. Stop playing the media and notify parent."""
        self._timer.Stop()
        self.notify(action="stop", value=None)
        for m in self.__media:
            m.Stop()

    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------

    def OnTimer(self, event):
        """Call it if EVT_TIMER is captured."""

        offset = self.media_tell()
        if self.media_playing():
            self.GetSlider().SetValue(offset)

        # On MacOS, it seems that offset is not precise enough...
        # It can be + or - 3 compared to the expected value!
        if self.media_stopped() or \
                (self.media_playing() and (offset + 3 > self._offsets[1])):
            # Media reached the end of the file and automatically stopped
            # but our Stop() does much more things
            # or
            # Media is playing and the current position is very close to the
            # end of our limit, so we can stop playing.
            if self._autoreplay is True:
                self.stop()
                self._autoreplay = True
                self.play()
            else:
                self.stop()

    # ----------------------------------------------------------------------

    def __reset(self):
        self.stop()
        self._length = 0
        self.__offsets = (0, 0)

    # ----------------------------------------------------------------------

    def __validate_offsets(self):
        """Adjust if given offsets are not in an appropriate range."""
        if len(self.__media) > 0:
            offset = self.media_tell()
            if offset < self._offsets[0] or offset > self._offsets[1]:
                self.media_seek(self._offsets[0])
                self.GetSlider().SetValue(offset)

        # validate end position (no longer than the length)
        if self._offsets[1] > self._length:
            self._offsets = (self._offsets[0], self._length)
            self.GetSlider().SetRange(self._offsets[0], self._offsets[1])

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        p1 = sppasPlayerControlsPanel(self)
        btn1 = BitmapTextButton(p1.GetWidgetsPanel(), name="way_up_down")
        p1.SetButtonProperties(btn1)
        p1.AddWidget(btn1)

        self.p2 = sppasMultiPlayerPanel(self)
        self.mc = sppasMediaPanel(self)
        self.mc.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND)
        s.Add(self.p2, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.SetForegroundColour(wx.Colour(225, 225, 225))

        wx.CallAfter(
            self.DoLoadFile,
            os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))

    # ----------------------------------------------------------------------

    def OnMediaLoaded(self, evt):
        wx.LogDebug(" ON MEDIA LOADED DU TEST PANEL * * * ")

    # ----------------------------------------------------------------------

    def DoLoadFile(self, path):
        if self.mc.Load(path) is False:
            wx.MessageBox("Unable to load %s: Unsupported format?" % path,
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            # self.mc.SetInitialSize()
            # self.GetSizer().Layout()
            wx.LogMessage("File loaded. Length is {:d}".format(self.mc._length))
            self.p2.set_media([self.mc])
