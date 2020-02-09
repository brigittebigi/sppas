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
import wx.lib.newevent

from sppas import paths

from ..windows import sppasPanel, sppasScrolledPanel
from ..windows import sppasMediaPanel, MediaType
from ..windows import BitmapTextButton
from ..windows import sppasPlayerControlsPanel

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

        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def add_media(self, filename):
        """Add a media into the player.

        Under Windows, the player crashes if the media is not supported.
        Other platforms raise an exception.

        :param filename: (str)

        """
        # We embed the media into a collapsible panel
        parent_panel = self.FindWindow("media_panel")
        try:
            panel = sppasMediaPanel(parent_panel, filename=filename)
        except Exception as e:
            wx.LogError(str(e))
            return
        mc = panel.GetPane()
        self._media[mc] = False
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self._OnCollapseChanged, panel)
        panel.Bind(sppasMediaPanel.EVT_MEDIA_ACTION, self._process_action)

        # Insert in the sizer
        if mc.GetMediaType() == MediaType().audio:
            # Audio is inserted at the first position
            pos = 0
        else:
            # Video is inserted at the end (append)
            pos = parent_panel.GetSizer().GetItemCount()
        parent_panel.GetSizer().Insert(pos, panel, 0, wx.EXPAND | wx.TOP,
                                       sppasPanel.fix_size(4))
        parent_panel.Layout()

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
        p2 = sppasPanel(splitter, name="media_panel")
        p2_sizer = wx.BoxSizer(wx.VERTICAL)
        p2.SetSizer(p2_sizer)
        # p2.SetupScrolling(scroll_x=False, scroll_y=True)

        best_size = p1.GetBestSize()
        splitter.SetMinimumPaneSize(best_size[1])
        splitter.SplitHorizontally(p1, p2, best_size[1])
        splitter.SetSashGravity(0.)

    # -----------------------------------------------------------------------

    def __add_custom_controls(self, control_panel):
        """Add custom widgets to the player controls panel."""
        # to switch panels of the splitter
        btn1 = BitmapTextButton(control_panel.GetWidgetsPanel(), label="", name="way_up_down")
        control_panel.SetButtonProperties(btn1)
        control_panel.AddWidget(btn1)

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
        self.FindWindow("splitter").Bind(sppasMediaPanel.EVT_MEDIA_ACTION, self._process_action)
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

        if name == "way_up_down":
            self.SwapPanels()

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

        controls.Paused(not paused_now)

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
        if playing_media is not None:
            pos = playing_media.Tell()
            new_pos = pos + value
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
        media = panel.GetPane()
        expanded = panel.IsExpanded()
        self._media[media] = expanded
        if expanded is True:
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
        controls.Paused(not is_paused)
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

# ---------------------------------------------------------------------------


class TestPanel(sppasPlayerPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)

        self.add_media(os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
        self.add_media(os.path.join(paths.samples, "samples-fra", "F_F_C006-P6.wav"))
        # self.add_media("/Users/bigi/Movies/Monsters_Inc.For_the_Birds.mpg")
        self.add_media("/E/Videos/Monsters_Inc.For_the_Birds.mpg")

        # self.add_media(os.path.join(paths.samples, "multimedia-fra", "audio_left.wav"))
        # self.add_media(os.path.join(paths.samples, "multimedia-fra", "audio_right.wav"))
        # self.add_media(os.path.join(paths.samples, "multimedia-fra", "video.mkv"))

        self.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.SetForegroundColour(wx.Colour(225, 225, 225))
