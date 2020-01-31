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
from wx.lib.splitter import MultiSplitterWindow

from sppas import paths

from ..windows import sppasPanel, sppasCollapsiblePanel
from ..windows import sppasMedia, MediaType
from ..windows import sppasStaticText
from ..windows import BitmapTextButton
from ..windows import ToggleButton

# ---------------------------------------------------------------------------


class sppasMultiSplitterPanel(MultiSplitterWindow):
    def __init__(self, *args, **kwargs):
        super(sppasMultiSplitterPanel, self).__init__(*args, **kwargs)

    def SetBackgroundColour(self, color):
        """Set the back ground colour.

        :param color: (wx.Colour) the colour to use

        """
        wx.Panel.SetBackgroundColour(self, color)
        self._drawSashInBackgroundColour = False
        # if  wx.NullColour == color:
        #     self._drawSashInBackgroundColour = False

    def _OnPaint(self, evt):
        """Override to provide RunTimeError."""
        if self:
            dc = wx.PaintDC(self)
            self._DrawSash(dc)

# ---------------------------------------------------------------------------


class sppasPlayerControlsPanel(sppasPanel):
    """Create a panel with controls for a list of media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi


    Four children panels are to be created and organized into a BoxSizer:
        - switch_panel: 2 buttons to send actions to the parent
        - orient_panel: 1 button to change orientation and 1 "free to use" static label


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

        super(sppasPlayerControlsPanel, self).__init__(parent, id, pos, size, style, name)

        self._create_content(orient)
        # self._setup_events()

        # Look&feel
        # self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        # self.SetForegroundColour(wx.GetApp().settings.fg_color)
        # self.SetFont(wx.GetApp().settings.text_font)

        # self.SetInitialSize()
        self.Layout()

    # -----------------------------------------------------------------------

    def EnablePlay(self, enable=True):
        """Enable or disable the Play button.

        :param enable: (bool)

        """
        nav_panel = self.FindWindow("tb_nav_panel")
        nav_panel.FindWindow("media_play").Enable(enable)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self, orient):
        """Create the content of the panel.

        :param orient: wx.HORIZONTAL or wx.VERTICAL

        """
        border = sppasPanel.fix_size(4)
        panel1 = self.__create_switch_panel(orient)
        panel2 = self.__create_orient_panel(orient)
        nav_panel = self.__create_nav_panel()
        sld_panel = self.__create_slider_media()
        vol_panel = self.__create_slider_volume()
        player_sizer = wx.BoxSizer(wx.VERTICAL)
        player_sizer.Add(nav_panel, 2, wx.EXPAND, 0)
        player_sizer.Add(sld_panel, 1, wx.EXPAND, 0)

        sizer = wx.BoxSizer(orient)
        sizer.Add(panel1, 0, wx.ALIGN_CENTRE | wx.ALL, border)
        sizer.Add(panel2, 0, wx.ALIGN_CENTER | wx.ALL, border)
        sizer.Add(player_sizer, 1, wx.EXPAND | wx.ALL, border)
        sizer.Add(vol_panel, 0, wx.ALIGN_CENTER | wx.ALL, border)

        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def __create_switch_panel(self, orient):
        """Return a panel with 2 buttons to switch parent splitter windows."""
        panel = sppasPanel(self, name="switch_panel")

        btn1 = BitmapTextButton(panel, label=" <> Player", name="btn_switch_1")
        self.__button_properties(btn1)

        btn2 = BitmapTextButton(panel, label=" <> Media", name="btn_switch_2")
        self.__button_properties(btn2)

        if orient == wx.HORIZONTAL:
            sizer = wx.BoxSizer(wx.VERTICAL)
        else:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btn1, 0, wx.EXPAND, 0)
        sizer.Add(btn2, 0, wx.EXPAND, 0)
        panel.SetSizerAndFit(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_orient_panel(self, orient):
        """A button to collapse/expand all media of the displayed root."""
        panel = sppasPanel(self, name="orient_panel")

        # change the orientation
        btn = BitmapTextButton(panel, label="", name="rotate_screen")
        self.__button_properties(btn)

        # a static label to indicate something
        text = sppasStaticText(panel, label="", style=wx.ALIGN_CENTRE)
        text.SetMinSize(wx.Size(-1, sppasPanel.fix_size(32)))

        if orient == wx.HORIZONTAL:
            sizer = wx.BoxSizer(wx.VERTICAL)
        else:
            sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(btn, 0, wx.EXPAND, 0)
        sizer.Add(text, 1, wx.EXPAND, 0)
        panel.SetSizerAndFit(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_nav_panel(self):
        """Return a panel with the buttons to play/pause/stop the media."""
        panel = sppasPanel(self, name="tb_nav_panel")
        panel.SetMinSize(wx.Size(-1, sppasPanel.fix_size(64)))

        btn_rewind = BitmapTextButton(panel, label="", name="media_rewind")
        self.__button_properties(btn_rewind)
        # btn_rewind.Enable(False)

        btn_play = BitmapTextButton(panel, label="", name="media_play")
        self.__button_properties(btn_play)
        btn_play.SetMinSize(wx.Size(sppasPanel.fix_size(56),
                                    sppasPanel.fix_size(56)))

        btn_forward = BitmapTextButton(panel, label="", name="media_forward")
        self.__button_properties(btn_forward)
        # btn_forward.Enable(False)

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

    def __create_slider_media(self):
        """Return a panel with the slider and left-right labels."""
        panel = sppasPanel(self, name="tb_slider_panel")

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
        panel.SetSizerAndFit(sizer)

        return panel

    # -----------------------------------------------------------------------

    def __create_slider_volume(self):
        """Return a panel with the slider and mute button."""
        panel = sppasPanel(self, name="tb_vol_panel")

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

    def __button_properties(self, btn):
        btn.FocusWidth = 0
        btn.Spacing = 0
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(sppasPanel.fix_size(40),
                               sppasPanel.fix_size(40)))

        return btn

# ---------------------------------------------------------------------------


class ControlPane(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        hvBox = wx.RadioBox(self, -1, "Orientation",
                            choices=["Horizontal", "Vertical"],
                            style=wx.RA_SPECIFY_COLS,
                            majorDimension=1)
        hvBox.SetSelection(0)
        self.Bind(wx.EVT_RADIOBOX, self.OnSetHV, hvBox)

        luCheck = wx.CheckBox(self, -1, "Live Update")
        luCheck.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.OnSetLiveUpdate, luCheck)

        btn = wx.Button(self, -1, "Swap 2 && 3")
        self.Bind(wx.EVT_BUTTON, self.OnSwapButton, btn)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hvBox)
        sizer.Add(luCheck, 0, wx.TOP, 5)
        sizer.Add(btn, 0, wx.TOP, 5)
        border = wx.BoxSizer()
        border.Add(sizer, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(border)


    def OnSetHV(self, evt):
        rb = evt.GetEventObject()
        self.GetParent().SetOrientation(rb.GetSelection())


    def OnSetLiveUpdate(self, evt):
        check = evt.GetEventObject()
        self.GetParent().SetLiveUpdate(check.GetValue())


    def OnSwapButton(self, evt):
        self.GetParent().Swap2and3()

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
        self._media = list()

        self._create_content()
        self._setup_events()

        # Look&feel
        # self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        # self.SetForegroundColour(wx.GetApp().settings.fg_color)
        # self.SetFont(wx.GetApp().settings.text_font)

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
        if media_type == MediaType().audio:
            parent_panel = self.FindWindow("audio_panel")
        elif media_type == MediaType().video:
            parent_panel = self.FindWindow("video_panel")

        panel = sppasCollapsiblePanel(parent_panel, label=filename)
        mc = sppasMedia(panel)
        panel.SetPane(mc)
        self._media.append(panel)

        if media_type == MediaType().audio:
            parent_panel.GetSizer().Add(panel, 0, wx.EXPAND)
        elif media_type == MediaType().video:
            parent_panel.GetSizer().Add(panel, 0, wx.EXPAND)

        # Load the media
        if mc.Load(filename) is True:
            self.__set_media_size(mc)
            panel.Expand()
        else:
            panel.Collapse()
            mc.Bind(wx.media.EVT_MEDIA_LOADED, self.__process_media_loaded)

        self.Layout()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel, managed by a splitter.

        """
        # Add the splitter window and a panel to control its properties
        splitter = sppasMultiSplitterPanel(self,
                                           style=wx.SP_LIVE_UPDATE,
                                           name="splitter")
        splitter.SetOrientation(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Fill in the splitter with panels
        tb = sppasPlayerControlsPanel(splitter, name="player_controls")
        tb.SetMinSize(tb.GetBestSize())
        splitter.AppendWindow(tb, tb.GetSize()[1])

        pa = sppasPanel(splitter, name="audio_panel")
        pa_sizer= wx.BoxSizer(wx.VERTICAL)
        pa.SetSizerAndFit(pa_sizer)
        splitter.AppendWindow(pa, sppasPanel.fix_size(128))

        pv = sppasPanel(splitter, name="video_panel")
        pv_sizer = wx.WrapSizer(orient=wx.HORIZONTAL)
        pv.SetSizerAndFit(pv_sizer)
        splitter.AppendWindow(pv, sppasPanel.fix_size(128))

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

        # The splitter sash position is changing/changed
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnChanged)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnChanging)

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
        self.__set_media_size(media)
        media.GetParent().Expand()

        self.Layout()

    # -----------------------------------------------------------------------

    def __set_media_size(self, media):
        """Fix the size of the media."""
        media.SetInitialSize()
        # media.SetMinSize(wx.Size(sppasPanel.fix_size(480),
        #                         sppasPanel.fix_size(128)))

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
        replay = False  # self.FindWindow("media_replay").GetValue()
        for panel in self._media:
            if panel.IsExpanded() is True:
                if replay is True:
                    panel.GetPane().AutoPlay()
                else:
                    panel.GetPane().NormalPlay()

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop the media currently playing."""
        for panel in self._media:
            panel.GetPane().Stop()

    # -----------------------------------------------------------------------
    # Properties of the splitter
    # -----------------------------------------------------------------------


    def OnChanging(self, evt):
        wx.LogDebug("Changing sash:%d  %s\n" %
                    (evt.GetSashIdx(), evt.GetSashPosition()))

        # This is one way to control the sash limits
        if evt.GetSashPosition() < sppasPanel.fix_size(50):
            evt.Veto()

        # Or you can reset the sash position to whatever you want
        #if evt.GetSashPosition() < 5:
        #    evt.SetSashPosition(25)


    def OnChanged(self, evt):
        wx.LogDebug("Changed sash:%d  %s\n" %
                    (evt.GetSashIdx(), evt.GetSashPosition()))

    # -----------------------------------------------------------------------

    def SetOrientation(self, value):
        if value:
            self.FindWindow("splitter").SetOrientation(wx.VERTICAL)
        else:
            self.FindWindow("splitter").SetOrientation(wx.HORIZONTAL)
        self.FindWindow("splitter").SizeWindows()

    # -----------------------------------------------------------------------

    def SetLiveUpdate(self, enable):
        if enable:
            self.FindWindow("splitter").SetWindowStyle(wx.SP_LIVE_UPDATE)
        else:
            self.FindWindow("splitter").SetWindowStyle(0)

    # -----------------------------------------------------------------------

    def Swap2and3(self):
        win2 = self.FindWindow("splitter").GetWindow(1)
        win3 = self.FindWindow("splitter").GetWindow(2)
        self.FindWindow("splitter").ExchangeWindows(win2, win3)

# ---------------------------------------------------------------------------


class TestPanel(sppasPlayerPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
        # self.SetBackgroundColour(wx.Colour(20, 20, 20))
        # self.SetForegroundColour(wx.Colour(220, 220, 220))

        self.add_media(os.path.join(paths.samples,
                                    "samples-fra",
                                    "F_F_B003-P8.wav"))
        self.add_media(os.path.join(paths.samples,
                                    "samples-fra",
                                    "F_F_C006-P6.wav"))
        # self.add_media("/Users/bigi/Movies/Monsters_Inc.For_the_Birds.mpg")
        self.add_media(os.path.join(paths.samples, "multimedia-fra", "video.mkv"))
