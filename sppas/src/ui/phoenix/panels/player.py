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
import time
import wx.media
import wx.lib.newevent

from sppas import paths

from ..windows import sppasPanel, sppasCollapsiblePanel, sppasImgBgPanel, sppasScrolledPanel
from ..windows import sppasTransparentPanel
from ..windows import sppasMedia, MediaType
from ..windows import BitmapTextButton
from ..windows import ToggleButton

# ---------------------------------------------------------------------------
# Event to be used by a player.

PlayerEvent, EVT_PLAYER = wx.lib.newevent.NewEvent()
PlayerCommandEvent, EVT_PLAYER_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


class sppasPlayerControlsPanel(sppasImgBgPanel):
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
                 orient=wx.HORIZONTAL,
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
            parent, id, "bg1", pos, size, style, name)

        if orient == wx.HORIZONTAL:
            self.SetMinSize(wx.Size(sppasPanel.fix_size(384),
                                    sppasPanel.fix_size(64)))
            self.SetMaxSize(wx.Size(-1, sppasPanel.fix_size(128)))
        else:
            self.SetMinSize(wx.Size(sppasPanel.fix_size(64),
                                    sppasPanel.fix_size(384)))
            self.SetMaxSize(wx.Size(sppasPanel.fix_size(128), -1))

        self._create_content(orient)
        self._setup_events()

        # Look&feel
        # self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.Colour(200, 200, 200))
        self.SetFont(wx.GetApp().settings.text_font)

        self.SetInitialSize()
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        return

    # -----------------------------------------------------------------------

    def SetOrientation(self, orient):
        """Set the orientation of all the sizers.

        :param orient: wx.HORIZONTAL or wx.VERTICAL

        """
        if orient == self.GetSizer().GetOrientation():
            return

        if orient == wx.HORIZONTAL:
            self.SetMinSize(wx.Size(sppasPanel.fix_size(384),
                                    sppasPanel.fix_size(64)))
            self.SetMaxSize(wx.Size(-1, sppasPanel.fix_size(128)))
        else:
            self.SetMinSize(wx.Size(sppasPanel.fix_size(64),
                                    sppasPanel.fix_size(384)))
            self.SetMaxSize(wx.Size(sppasPanel.fix_size(128), -1))

        if orient == wx.HORIZONTAL:
            sl_orient = wx.SL_HORIZONTAL
            reversed_orient = wx.VERTICAL
        elif orient == wx.VERTICAL:
            sl_orient = wx.SL_VERTICAL
            reversed_orient = wx.HORIZONTAL
        else:
            return

        # The panels that are in orientation
        self.FindWindow("widgets_panel").GetSizer().SetOrientation(orient)

        # The panels that are in the reversed orientation
        transport_panel = self.FindWindow("transport_panel")
        volume_panel = self.FindWindow("volume_panel")
        tps = transport_panel.GetSizer()
        tps.SetOrientation(reversed_orient)
        for child in tps.GetChildren():
            s = child.GetSizer()
            if s is not None:
                s.SetOrientation(orient)

        # The main panel
        self.GetSizer().SetOrientation(orient)

        # The sliders
        slider_seek = transport_panel.FindWindow("seek_slider")
        slider_seek.SetWindowStyle(sl_orient | wx.SL_MIN_MAX_LABELS)
        slider_volume = volume_panel.FindWindow("volume_slider")
        slider_volume.SetWindowStyle(sl_orient)

        self.Layout()

    # -----------------------------------------------------------------------

    def GetWidgetsPanel(self):
        """Return the panel..."""
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
        return transport_panel.FindWindow("media_replay").IsPressed()

    # -----------------------------------------------------------------------

    def EnableReplay(self, enable=True):
        """Enable or disable the Replay button.

        The replay button should be disabled if several media of different
        durations have to be played...

        :param enable: (bool)

        """
        transport_panel = self.FindWindow("transport_panel")
        transport_panel.FindWindow("media_replay").Enable(enable)

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
        """Set the range values of the transport slider.

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

    def _create_content(self, orient):
        """Create the content of the panel.

        :param orient: wx.HORIZONTAL or wx.VERTICAL

        """
        # Create the main panels
        panel1 = self.__create_widgets_panel(orient)
        panel1.Hide()
        panel2 = self.__create_transport_panel(orient)
        panel3 = self.__create_volume_panel(orient)

        # Organize the panels into the main sizer
        border = sppasPanel.fix_size(4)
        sizer = wx.BoxSizer(orient)
        sizer.Add(panel1, 3, wx.ALIGN_CENTRE | wx.EXPAND | wx.ALL, border)
        sizer.Add(panel2, 6, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border)
        sizer.AddStretchSpacer(1)
        sizer.Add(panel3, 1, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_widgets_panel(self, orient):
        """Return an empty panel with a wrap sizer."""
        panel = sppasTransparentPanel(self, style=wx.TRANSPARENT_WINDOW, name="widgets_panel")
        if orient == wx.HORIZONTAL:
            sizer = wx.WrapSizer(orient=wx.VERTICAL)
        else:
            sizer = wx.WrapSizer(orient=wx.HORIZONTAL)
        panel.SetSizerAndFit(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_transport_panel(self, orient):
        """Return a panel with the buttons to play/pause/stop the media."""
        panel = sppasTransparentPanel(self, style=wx.TRANSPARENT_WINDOW, name="transport_panel")

        btn_rewind = BitmapTextButton(panel, label="", name="media_rewind")
        self.SetButtonProperties(btn_rewind)

        btn_play = BitmapTextButton(panel, label="", name="media_play")
        self.SetButtonProperties(btn_play)
        # btn_play.Enable(False)

        btn_forward = BitmapTextButton(panel, label="", name="media_forward")
        self.SetButtonProperties(btn_forward)

        btn_stop = BitmapTextButton(panel, label="", name="media_stop")
        self.SetButtonProperties(btn_stop)

        btn_replay = ToggleButton(panel, label="", name="media_replay")
        btn_replay = self.SetButtonProperties(btn_replay)

        # Labels of wx.Slider are not supported under MacOS.
        if orient == wx.HORIZONTAL:
            slider = wx.Slider(panel, style=wx.SL_HORIZONTAL | wx.SL_MIN_MAX_LABELS)
            # slider.SetMinSize(wx.Size(sppasPanel.fix_size(200), -1))
        else:
            slider = wx.Slider(panel, style=wx.SL_VERTICAL | wx.SL_MIN_MAX_LABELS)
            # slider.SetMinSize(wx.Size(-1, sppasPanel.fix_size(200)))
        slider.SetRange(0, 100)
        slider.SetValue(0)
        slider.SetName("seek_slider")

        border = sppasPanel.fix_size(2)
        nav_sizer = wx.BoxSizer(orient)
        nav_sizer.AddStretchSpacer(1)
        nav_sizer.Add(btn_rewind, 0, wx.ALL | wx.ALIGN_CENTER, border)
        nav_sizer.Add(btn_play, 0, wx.ALL | wx.ALIGN_CENTER, border)
        nav_sizer.Add(btn_forward, 0, wx.ALL | wx.ALIGN_CENTER, border)
        nav_sizer.Add(btn_stop, 0, wx.ALL | wx.ALIGN_CENTER, border)
        nav_sizer.Add(btn_replay, 0, wx.ALL | wx.ALIGN_CENTER, border)
        nav_sizer.AddStretchSpacer(1)

        # Organize the previous sizers into the main sizer
        if orient == wx.HORIZONTAL:
            sizer = wx.BoxSizer(wx.VERTICAL)
        else:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(nav_sizer, 4, wx.EXPAND | wx.ALIGN_CENTER, 0)
        sizer.AddStretchSpacer(1)
        sizer.Add(slider, 3, wx.EXPAND | wx.ALIGN_CENTER, 0)
        sizer.AddStretchSpacer(1)

        panel.SetSizer(sizer)

        return panel

    # -----------------------------------------------------------------------

    def __create_volume_panel(self, orient):
        """Return a panel with a slider for the volume and a mute button."""
        panel = sppasTransparentPanel(self, style=wx.TRANSPARENT_WINDOW, name="volume_panel")

        btn_mute = ToggleButton(panel, label="", name="volume_mute")
        btn_mute.SetImage("volume_high")
        self.SetButtonProperties(btn_mute)

        slider = wx.Slider(panel, style=wx.SL_VERTICAL | wx.SL_INVERSE)
        #slider.SetMinSize(wx.Size(sppasPanel.fix_size(80),
        #                         sppasPanel.fix_size(64)))
        slider.SetName("volume_slider")
        slider.SetValue(100)
        slider.SetRange(0, 100)

        sizer = wx.BoxSizer(orient)
        sizer.Add(btn_mute, 0, wx.ALIGN_CENTER, 0)
        sizer.Add(slider, 1, wx.ALIGN_CENTER | wx.EXPAND, 0)
        panel.SetSizer(sizer)

        return panel

    # -----------------------------------------------------------------------

    def SetButtonProperties(self, btn):
        btn.SetTransparent(128)
        btn.FocusWidth = 1
        btn.Spacing = 0
        btn.FocusColour = self.GetForegroundColour()
        btn.BorderWidth = 3
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(sppasPanel.fix_size(48),
                               sppasPanel.fix_size(48)))

        return btn

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
        evt = PlayerEvent(action=action, value=value)
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


class sppasPlayerPanel(sppasPanel):
    """Create a panel to play media and display their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="mediaplayer_panel"):
        """Create a sppasPlayerPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        """
        sppasPanel.__init__(self, parent, id, pos, size, style, name)

        # The list of collapsible panels embedding a media.
        # key = sppasMedia, value = bool (selected or not)
        self._media = dict()

        self._create_content()
        self._setup_events()

        # Look&feel
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # self.Layout()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def add_media(self, filename):
        """Add a media into the player.

        Under Windows, the player crashes if the media is not supported.
        Other platforms raise an exception.

        :param filename: (str)

        """
        media_type = sppasMedia.ExpectedMediaType(filename)
        if media_type == MediaType().unknown:
            raise TypeError("File {:s} is of an unknown type.")

        # We embed the media into a collapsible panel
        parent_panel = self.FindWindow("media_panel")
        panel = self.__create_media_panel(parent_panel, filename)
        mc = panel.GetPane()

        if media_type == MediaType().audio:
            # Audio is inserted at the first position
            pos = 0
        else:
            # Video is inserted at the end (append)
            pos = parent_panel.GetSizer().GetItemCount()
        parent_panel.GetSizer().Insert(pos, panel, 0, wx.EXPAND)

        # Load the media
        if mc.Load(filename) is True:
            # Under Windows, the Load methods always return True, even if the media is not loaded...
            time.sleep(0.1)
            self.__set_media_properties(mc)
        else:
            self._media[panel] = False
            panel.Collapse()
            mc.Bind(wx.media.EVT_MEDIA_LOADED, self.__process_media_loaded)

        parent_panel.Layout()

    # -----------------------------------------------------------------------

    def __create_media_panel(self, parent, filename):
        """Create the collapsible panel for a media."""
        panel = sppasCollapsiblePanel(parent, label=filename)
        panel.AddButton("zoom_in")
        panel.AddButton("zoom_out")
        panel.AddButton("zoom")
        panel.AddButton("close")
        mc = sppasMedia(panel)
        panel.SetPane(mc)
        self.media_zoom(mc, 0)  # 100% zoom = initial size
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self._OnCollapseChanged, panel)
        return panel

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel, managed by a splitter.

        Three panels are created and organized:

            - player_controls_panel
            - media_panel

        """
        # Add the splitter window
        splitter = wx.SplitterWindow(self,
                                     style=wx.SP_LIVE_UPDATE | wx.NO_BORDER,
                                     name="splitter")
        sizer = wx.BoxSizer()
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Window 1 of the splitter: player controls
        p1 = sppasPlayerControlsPanel(splitter, name="player_controls_panel")
        self.__add_custom_controls(p1)

        # Window 2 of the splitter: a scrolled panel with all media
        p2 = sppasScrolledPanel(splitter, name="media_panel")
        p2_sizer = wx.BoxSizer(wx.VERTICAL)
        p2.SetSizer(p2_sizer)
        p2.SetupScrolling(scroll_x=False, scroll_y=True)

        best_size = p1.GetBestSize()
        splitter.SetMinimumPaneSize(best_size[1])
        splitter.SplitHorizontally(p1, p2, best_size[1])
        splitter.SetSashGravity(0.)

    # -----------------------------------------------------------------------

    def __add_custom_controls(self, control_panel):
        """Add custom widgets to the player controls panel."""
        # to switch panels of the splitter
        btn1 = BitmapTextButton(control_panel.GetWidgetsPanel(), label="", name="exchange_1")
        control_panel.SetButtonProperties(btn1)
        control_panel.AddWidget(btn1)

        # to change the orientation of the splitter
        btn3 = BitmapTextButton(control_panel.GetWidgetsPanel(), label="", name="rotate_screen")
        control_panel.SetButtonProperties(btn3)
        control_panel.AddWidget(btn3)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user pressed a key of its keyboard
        self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.FindWindow("splitter").Bind(EVT_PLAYER, self._process_action)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        # The splitter sash position is changing/changed
        # self.FindWindow("splitter").Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnChanged)
        # self.FindWindow("splitter").Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnChanging)

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

    def __process_media_loaded(self, event):
        """Process the end of load of a media."""
        wx.LogMessage("Media loaded event received.")
        media = event.GetEventObject()
        self.__set_media_properties(media)

    # -----------------------------------------------------------------------

    def __set_media_properties(self, media):
        """Fix the properties of the media."""
        media.SetInitialSize()
        self._media[media] = True
        media.GetParent().Expand()
        m = self.is_playing()
        self.__set_slider()
        if m is not None:
            # Another media is currently playing. We'll play too.
            # this media is stopped or paused
            media.SetOffsetPeriod(m.GetStartPeriod(), m.GetEndPeriod())
            media.Seek(m.Tell())
            self.__play_media(media)

    # -----------------------------------------------------------------------

    def __set_slider(self):
        """Assign the seek slider to the longest appropriate media."""
        if len(self._media) == 0:
            return
        # Search for the longest media currently playing, the longest in
        # expanded panels and the longest in absolute.
        longest_playing = (None, 0)
        longest_expanded = (None, 0)
        longest = (None, 0)
        for media in self._media:
            media.SetSlider(None)
            duration = media.Length()
            if duration >= longest[1]:
                longest = (media, duration)
            if self._media[media] is True:
                if duration >= longest_expanded[1]:
                    longest_expanded = (media, duration)
                if media.IsPlaying() or media.IsPaused():
                    if duration >= longest_playing[1]:
                        longest_playing = (media, duration)

        controls = self.FindWindow("player_controls_panel")
        if longest_playing[0] is not None:
            m = longest_playing[0]
        elif longest_expanded[0] is not None:
            m = longest_expanded[0]
        else:
            m = longest[0]

        m.SetSlider(controls.GetSlider())

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        name = event.action
        wx.LogDebug("Received a player event. "
                    "Action is {:s}. Value is {:s}"
                    "".format(name, str(event.value)))

        if name == "play":
            self.play()

        elif name == "stop":
            self.stop()

        elif name == "rewind":
            self.shift(-2000)

        elif name == "forward":
            self.shift(2000)

        elif name == "volume":
            self.volume(event.value)

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """
        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "exchange_1":
            self.SwapPanels()

        elif name == "rotate_screen":
            self.Rotate()

        elif name == "zoom":
            self.media_zoom(obj, 0)

        elif name == "zoom_in":
            self.media_zoom(obj, 1)

        elif name == "zoom_out":
            self.media_zoom(obj, -1)

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def is_playing(self):
        """Return the first media we found playing, None instead."""
        for media in self._media:
            if self._media[media] is True and media.IsPlaying() is True:
                return media
        return None

    # -----------------------------------------------------------------------

    def media_zoom(self, obj, direction):
        """Zoom the media of the given panel.

        :param obj: One of the objects of a sppasCollapsiblePanel with
        an embedded media
        :param direction: (int) -1 to zoom out, +1 to zoom in and 0 to reset
        to the initial size.

        """
        panel = None
        for p in self.FindWindow("media_panel").GetChildren():
            if p.IsChild(obj) is True:
                panel = p
                break
        assert panel is not None
        zooms = (10, 25, 50, 75, 100, 125, 150, 200, 250, 300)
        if panel.IsExpanded() is False:
            return

        media = panel.GetPane()
        if direction == 0:
            media.SetZoom(100)
        else:
            idx_zoom = zooms.index(media.GetZoom())
            if direction < 0:
                new_idx_zoom = max(0, idx_zoom-1)
            else:
                new_idx_zoom = min(len(zooms)-1, idx_zoom+1)
            media.SetZoom(zooms[new_idx_zoom])

        media.SetInitialSize()
        panel.Refresh()
        self.Layout()

    # -----------------------------------------------------------------------

    def play(self):
        """Play/Pause the selected media."""
        controls = self.FindWindow("player_controls_panel")
        is_playing = self.is_playing()
        paused_now = False
        for media in self._media:
            if self._media[media] is True:
                if is_playing is not None:
                    # this media is stopped or playing
                    media.Pause()
                    paused_now = True
                else:
                    # this media is stopped or paused
                    # self.__play_media(media)
                    played = media.Play()
                    media.Pause()
                    size = media.GetParent().DoGetBestSize()
                    media.GetParent().SetInitialSize(size)

        controls.Paused(paused_now)
        # self.Layout()

        # If we have to play the media we'll do it now.
        if paused_now == 0:
            for media in self._media:
                if self._media[media] is True:
                    self.__play_media(media)

    # -----------------------------------------------------------------------

    def __play_media(self, media):
        controls = self.FindWindow("player_controls_panel")
        if controls.IsReplay() is True:
            media.AutoPlay()
        else:
            media.NormalPlay()
        media.GetParent().Refresh()
        self.Layout()

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop the media currently playing."""
        for media in self._media:
            media.Stop()

    # -----------------------------------------------------------------------

    def shift(self, value=2000):
        """Rewind or forward of 'value' milliseconds.

        :param value: (int) Time to shift

        """
        playing_media = self.is_playing()
        pos = playing_media.Tell()
        new_pos = pos + value
        if playing_media is not None:
            for media in self._media:
                media.Seek(new_pos)

    # -----------------------------------------------------------------------

    def volume(self, value):
        wx.LogDebug("Set volume to {:f}".format(value))
        for media in self._media:
            media.SetVolume(value)

    # -----------------------------------------------------------------------
    # Properties of the splitter and panels
    # -----------------------------------------------------------------------

    def _OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        media = panel.GetPane()
        expanded = panel.IsExpanded()
        self._media[media] = expanded
        if expanded is False:
            # The media was expanded, now it is collapsed.
            media.Stop()
            panel.EnableButton("zoom", False)
            panel.EnableButton("zoom_in", False)
            panel.EnableButton("zoom_out", False)
        else:
            panel.EnableButton("zoom", True)
            panel.EnableButton("zoom_in", True)
            panel.EnableButton("zoom_out", True)
            # The media was collapsed, and now it is expanded.
            m = self.is_playing()
            if m is not None:
                # Another media is currently playing. We'll play too.
                # this media is stopped or paused
                media.SetOffsetPeriod(m.GetStartPeriod(), m.GetEndPeriod())
                media.Seek(m.Tell())
                self.__play_media(media)
            else:
                wx.LogDebug(" ... no media was playing.")

        controls = self.FindWindow("player_controls_panel")
        is_paused = any(m.IsPaused() for m in self._media if self._media[m] is True)
        controls.Paused(is_paused)
        self.__set_slider()
        self.Layout()

    # -----------------------------------------------------------------------

    def SetLiveUpdate(self, enable):
        if enable:
            self.FindWindow("splitter").SetWindowStyle(wx.SP_LIVE_UPDATE)
        else:
            self.FindWindow("splitter").SetWindowStyle(0)

    # -----------------------------------------------------------------------

    def SwapPanels(self):
        splitter = self.FindWindow("splitter")
        win_1 = splitter.GetWindow1()
        win_2 = splitter.GetWindow2()
        w, h = win_2.GetSize()
        splitter.Unsplit(toRemove=win_1)
        splitter.Unsplit(toRemove=win_2)

        if splitter.GetSplitMode() == wx.SPLIT_VERTICAL:
            splitter.SplitVertically(win_2, win_1, w)
        else:
            splitter.SplitHorizontally(win_2, win_1, h)

        if win_1.GetName() == "player_controls_panel":
            splitter.SetSashGravity(1.)
        else:
            splitter.SetSashGravity(0.)

        self.Layout()
        splitter.UpdateSize()

    # -----------------------------------------------------------------------

    def Rotate(self):
        splitter = self.FindWindow("splitter")
        win_1 = splitter.GetWindow1()
        win_2 = splitter.GetWindow2()
        w, h = win_1.GetSize()
        splitter.Unsplit(toRemove=win_1)
        splitter.Unsplit(toRemove=win_2)
        if splitter.GetSplitMode() == wx.SPLIT_VERTICAL:
            orient = wx.HORIZONTAL
            splitter.SplitHorizontally(win_1, win_2, w)
        else:
            orient = wx.VERTICAL
            splitter.SplitVertically(win_1, win_2, h)

        if win_1.GetName() == "player_controls_panel":
            splitter.SetSashGravity(0.)
            win_1.SetOrientation(orient)
        else:
            splitter.SetSashGravity(1.)
            win_2.SetOrientation(orient)

        self.Layout()
        splitter.UpdateSize()

# ---------------------------------------------------------------------------


class TestPanel(sppasPlayerPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)

        # self.add_media(os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
        # self.add_media(os.path.join(paths.samples, "samples-fra", "F_F_C006-P6.wav"))
        # self.add_media("/Users/bigi/Movies/Monsters_Inc.For_the_Birds.mpg")
        # self.add_media("/E/Videos/Monsters_Inc.For_the_Birds.mpg")

        self.add_media(os.path.join(paths.samples, "multimedia-fra", "audio_left.wav"))
        self.add_media(os.path.join(paths.samples, "multimedia-fra", "audio_right.wav"))
        self.add_media(os.path.join(paths.samples, "multimedia-fra", "video.mkv"))
