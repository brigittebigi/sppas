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

from ..windows import sppasPanel, sppasCollapsiblePanel
from ..windows import sppasMedia
from ..windows import sppasStaticLine
from ..windows import sppasStaticText
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

    def __init__(self, parent, id=wx.ID_ANY,
                 align=wx.ALIGN_TOP,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="CollapsiblePane"):
        """Create a sppasPlayerPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.
        :param align: (wx.ALIGN_TOP or wx.ALIGN_BOTTOM) position of the toolbar (top or bottom)

        """

        sppasPanel.__init__(self, parent, id, pos, size, style, name)

        self._create_content(align)
        self._setup_events()

        # Look&feel
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # self.SetInitialSize()
        self.Layout()

    # -----------------------------------------------------------------------

    def add_media(self, filename):
        """Add a media into the player.

        Under Windows, the player crashes if the media is not supported.
        Other platforms raise an exception.

        :param filename: (str)

        """
        # We will embed the media into a collapsible panel
        parent_panel = self.FindWindow("media_player_panel")
        panel = sppasCollapsiblePanel(parent_panel, label=filename)
        panel.SetMinSize(wx.Size(sppasPanel.fix_size(480),
                                 sppasPanel.fix_size(64)))

        # Create the media and add to the panel
        backend = ""  # choose default backend, i.e. the system dependent one
        mc = sppasMedia(panel, style=wx.SIMPLE_BORDER, szBackend=backend)
        panel.SetPane(mc)

        # Load the media
        if mc.Load(filename) is True:
            self.__set_media_size(mc)
            panel.Expand()
        else:
            panel.Collapse()
            mc.SetMinSize(wx.Size(sppasPanel.fix_size(480),
                                  sppasPanel.fix_size(32)))
            mc.Bind(wx.media.EVT_MEDIA_LOADED, self.__process_media_loaded)

        self.__add_to_audio_sizer(panel)
        self.Layout()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self, align):
        """Create the content of the panel, a toolbar and a content panel.

        :param align: wx.ALIGN_BOTTOM for bottom, anything else for top alignment.

        """
        tb = self.__create_toolbar()
        pp = self.__create_media_panel()

        sizer = wx.BoxSizer(wx.VERTICAL)
        if align == wx.ALIGN_BOTTOM:
            sizer.Add(pp, 0, wx.EXPAND, 0)
            sizer.Add(tb, 0, wx.EXPAND, 0)
        else:
            sizer.Add(tb, 0, wx.EXPAND, 0)
            sizer.Add(pp, 0, wx.EXPAND, 0)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def __get_video_sizer(self):
        """Return the sizer to display video medias."""
        main_panel = self.FindWindow("media_player_panel")
        return main_panel.GetSizer()

    # -----------------------------------------------------------------------

    def __add_to_video_sizer(self, panel):
        """Add a panel to the sizer to display video medias."""
        main_panel = self.FindWindow("media_player_panel")
        main_panel.GetSizer().Add(panel, 0, wx.EXPAND)

    # -----------------------------------------------------------------------

    def __get_audio_sizer(self):
        """Return the sizer to display audio medias."""
        main_panel = self.FindWindow("media_player_panel")
        return main_panel.GetSizer()

    # -----------------------------------------------------------------------

    def __add_to_audio_sizer(self, panel):
        """Add a panel to the sizer to display audio waveform."""
        main_panel = self.FindWindow("media_player_panel")
        main_panel.GetSizer().Add(panel, 0, wx.EXPAND)
        main_panel.GetSizer().Add(self.__create_hline(), 0, wx.EXPAND)

    # -----------------------------------------------------------------------

    def __create_media_panel(self):
        """Main panel to display the content of the media."""
        panel = sppasPanel(self, name="media_player_panel")
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        """Tools to manage the media (a player, a slider, the volume...)."""
        panel = sppasPanel(self, name="toolbar_player_panel")

        file_btn = self.__create_filename_button(panel)
        nav_panel = self.__create_player_buttons(panel)
        sld_panel = self.__create_slider_media(panel)
        vol_panel = self.__create_slider_volume(panel)
        player_sizer = wx.BoxSizer(wx.VERTICAL)
        player_sizer.Add(nav_panel, 2, wx.EXPAND, 0)
        player_sizer.Add(sld_panel, 1, wx.EXPAND, 0)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(file_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(player_sizer, 1, wx.EXPAND, 0)
        sizer.Add(vol_panel, 0, wx.ALIGN_CENTER_VERTICAL)

        panel.SetSizerAndFit(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_filename_button(self, parent):
        """A button to collapse/expand all media of the displayed root."""
        btn = BitmapTextButton(parent, label="No file", name="media_multimedia")
        self.__button_properties(btn)
        btn.SetLabelPosition(wx.RIGHT)
        btn.SetSpacing(sppasPanel.fix_size(8))
        btn.SetMinSize(wx.Size(sppasPanel.fix_size(128),
                               sppasPanel.fix_size(64)))
        return btn

    # -----------------------------------------------------------------------

    def __create_player_buttons(self, parent):
        """Return a panel with the buttons to play/pause/stop the media."""
        panel = sppasPanel(parent, name="tb_nav_panel")

        btn_rewind = BitmapTextButton(panel, label="", name="media_rewind")
        self.__button_properties(btn_rewind)
        btn_rewind.Enable(False)

        btn_play = BitmapTextButton(panel, label="", name="media_play")
        self.__button_properties(btn_play)
        btn_play.SetMinSize(wx.Size(sppasPanel.fix_size(40),
                                    sppasPanel.fix_size(40)))

        btn_forward = BitmapTextButton(panel, label="", name="media_forward")
        self.__button_properties(btn_forward)
        btn_forward.Enable(False)

        btn_stop = BitmapTextButton(panel, label="", name="media_stop")
        self.__button_properties(btn_stop)

        btn_replay = ToggleButton(panel, label="", name="media_replay")
        btn_replay = self.__button_properties(btn_replay)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(btn_rewind, 0, wx.EXPAND, 0)
        sizer.Add(btn_play, 0, wx.EXPAND, 0)
        sizer.Add(btn_forward, 0, wx.EXPAND, 0)
        sizer.Add(btn_stop, 0, wx.EXPAND, 0)
        sizer.Add(btn_replay, 0, wx.EXPAND, 0)
        sizer.AddStretchSpacer(1)

        panel.SetSizerAndFit(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_slider_media(self, parent):
        """Return a panel with the slider and left-right labels."""
        panel = sppasPanel(parent, name="tb_slider_panel")

        lt = sppasStaticText(panel, label="---.---", style=wx.ALIGN_RIGHT)
        lt.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        rt = sppasStaticText(panel, label="---.---", style=wx.ALIGN_LEFT)
        rt.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        slider = wx.Slider(panel, -1, 0, 0, 10, style=wx.SL_HORIZONTAL)
        slider.SetMinSize(wx.Size(sppasPanel.fix_size(200), -1))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lt, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT, sppasPlayerPanel.fix_size(4))
        sizer.Add(slider, 1, wx.EXPAND, 0)
        sizer.Add(rt, 0, wx.ALIGN_CENTER | wx.LEFT, sppasPlayerPanel.fix_size(4))
        panel.SetSizer(sizer)

        return panel

    # -----------------------------------------------------------------------

    def __create_slider_volume(self, parent):
        """Return a panel with the slider and mute button."""
        panel = sppasPanel(parent, name="tb_vol_panel")

        btn_mute = BitmapTextButton(panel, label="", name="vol_mute")
        self.__button_properties(btn_mute)

        slider = wx.Slider(panel, value=50, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        slider.SetMinSize(wx.Size(sppasPanel.fix_size(80),
                                  sppasPanel.fix_size(64)))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btn_mute, 0, wx.ALIGN_CENTER, sppasPlayerPanel.fix_size(4))
        sizer.Add(slider, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALIGN_LEFT, 0)
        panel.SetSizerAndFit(sizer)

        return panel

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

    def __process_media_loaded(self, event):
        """Process the end of load of a media."""
        # wx.LogMessage("Media size is {:s}".format(str(media_size)))
        media = event.GetEventObject()
        self.__set_media_size(media)
        media.GetParent().Expand()

    # -----------------------------------------------------------------------

    def __set_media_size(self, media):
        """Fix the size of the media."""
        #media.SetInitialSize()
        media.SetMinSize(wx.Size(sppasPanel.fix_size(480),
                                 sppasPanel.fix_size(128)))

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process a button event: an action has to be performed.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()

        if name == "media_play":
            self.play()

        elif name == "media_stop":
            self.stop()

        event.Skip()

    # -----------------------------------------------------------------------

    def play(self):
        """Play the selected media."""
        main_panel = self.FindWindow("media_player_panel")
        replay = self.FindWindow("media_replay").GetValue()
        for child in main_panel.GetChildren():
            pane = child.GetPane()
            try:
                if child.IsExpanded() is True:
                    if replay is True:
                        pane.AutoPlay()
                    else:
                        pane.NormalPlay()
            except AttributeError:
                wx.LogMessage("Child panel {:s} is not a media.".format(pane.GetName()))

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop the media currently playing."""
        main_panel = self.FindWindow("media_player_panel")
        for child in main_panel.GetChildren():
            pane = child.GetPane()
            try:
                pane.Stop()
            except AttributeError:
                wx.LogMessage("Child panel {:s} is not a media.".format(pane.GetName()))

# ---------------------------------------------------------------------------


class TestPanel(sppasPlayerPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
        self.SetBackgroundColour(wx.Colour(20, 20, 20))
        self.SetForegroundColour(wx.Colour(220, 220, 220))
        self.add_media(os.path.join(paths.samples,
                                    "samples-fra",
                                    "F_F_B003-P8.wav"))
        self.add_media(os.path.join(paths.samples,
                                    "samples-fra",
                                    "F_F_C006-P6.wav"))
