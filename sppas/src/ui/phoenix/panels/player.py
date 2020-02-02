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
from wx.lib.splitter import MultiSplitterWindow


from sppas import paths

from ..windows import sppasPanel, sppasCollapsiblePanel
from ..windows import sppasMedia, MediaType
from ..windows import sppasStaticText
from ..windows import BitmapTextButton
from ..windows import ToggleButton
from ..tools import sppasSwissKnife

# ---------------------------------------------------------------------------
# Event to be used by a player.

PlayerEvent, EVT_PLAYER = wx.lib.newevent.NewEvent()
PlayerCommandEvent, EVT_PLAYER_COMMAND = wx.lib.newevent.NewCommandEvent()

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


class sppasAudioAmplitudePanel(sppasPanel):
    """Create a panel with an image as background representing amplitudes.

    """
    def __init__(self, parent, id=wx.ID_ANY,
                 orient=wx.HORIZONTAL,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="audio_amp_panel"):
        super(sppasAudioAmplitudePanel, self).__init__(parent, id, pos, size, style, name)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(384),
                                sppasPanel.fix_size(128)))

        # Bind the events related to our window
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        return

    def OnEraseBackground(self, evt):
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        # yanked from ColourDB.py
        dc = evt.GetDC()

        if not dc:
            dc = wx.ClientDC(self)
        dc.Clear()

        w, h = self.GetClientSize()
        img = sppasSwissKnife.get_image("audio")
        img.Rescale(w, h)
        dc.DrawBitmap(wx.Bitmap(img), 0, 0)


# ---------------------------------------------------------------------------


class sppasVideoAmplitudePanel(sppasPanel):
    """Create a panel with an image as background representing amplitudes.

    """
    def __init__(self, parent, id=wx.ID_ANY,
                 orient=wx.HORIZONTAL,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="audio_amp_panel"):
        super(sppasVideoAmplitudePanel, self).__init__(parent, id, pos, size, style, name)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(384),   # a 16:9 ratio
                                sppasPanel.fix_size(216)))

        # Bind the events related to our window
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        return

    def OnEraseBackground(self, evt):
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        # yanked from ColourDB.py
        dc = evt.GetDC()

        if not dc:
            dc = wx.ClientDC(self)
        dc.Clear()

        w, h = self.GetClientSize()
        img = sppasSwissKnife.get_image("video")
        img.Rescale(w, h)
        dc.DrawBitmap(wx.Bitmap(img), 0, 0)

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

        # Bind the events related to our window
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        # Look&feel
        # self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.Colour(200, 200, 200))
        self.SetFont(wx.GetApp().settings.text_font)

        self.SetInitialSize()
        self.Layout()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        return

    def OnEraseBackground(self, evt):
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        # yanked from ColourDB.py
        dc = evt.GetDC()

        if not dc:
            dc = wx.ClientDC(self)
        dc.Clear()

        w, h = self.GetClientSize()
        img = sppasSwissKnife.get_image("trbg4")
        img.Rescale(w, h)
        dc.DrawBitmap(wx.Bitmap(img), 0, 0)

    # -----------------------------------------------------------------------
    # Public methods
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

        transport_panel.SetBackgroundColour(wx.RED)
        volume_panel.SetBackgroundColour(wx.BLUE)
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

    def SetLeftTick(self, text):
        """Set the text to display at left/top of the slider.

        :param text: (str) a short text

        """
        transport_panel = self.FindWindow("transport_panel")
        lt = transport_panel.FindWindow("left_text_splitter")
        lt.SetLabel(text)

    # -----------------------------------------------------------------------

    def SetRightTick(self, text):
        """Set the text to display at right/bottom of the slider.

        :param text: (str) a short text

        """
        transport_panel = self.FindWindow("transport_panel")
        rt = transport_panel.FindWindow("right_text_splitter")
        rt.SetLabel(text)

    # -----------------------------------------------------------------------

    def IsReplay(self):
        """Return True if the button to replay is enabled."""
        transport_panel = self.FindWindow("transport_panel")
        return transport_panel.FindWindow("media_replay").IsPressed()

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
        if value is True:
            transport_panel.FindWindow("media_play").SetImage("media_play")
        else:
            transport_panel.FindWindow("media_play").SetImage("media_pause")

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
        sizer.Add(panel3, 1, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_widgets_panel(self, orient):
        """Return an empty panel with a wrap sizer."""
        panel = sppasPanel(self, name="widgets_panel")
        if orient == wx.HORIZONTAL:
            sizer = wx.WrapSizer(orient=wx.VERTICAL)
        else:
            sizer = wx.WrapSizer(orient=wx.HORIZONTAL)
        panel.SetSizerAndFit(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_transport_panel(self, orient):
        """Return a panel with the buttons to play/pause/stop the media."""
        panel = sppasPanel(self, style=wx.TRANSPARENT_WINDOW, name="transport_panel")

        btn_rewind = BitmapTextButton(panel, label="", name="media_rewind")
        self.SetButtonProperties(btn_rewind)

        btn_play = BitmapTextButton(panel, label="", name="media_play")
        self.SetButtonProperties(btn_play)
        btn_play.Enable(False)

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
        panel = sppasPanel(self, name="volume_panel")

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
        # btn.SetTransparent(128)
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
            - exchange_1/exchange_2/rotate_screen, without value;
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
                self.notify(action="volume", value=0)
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
        self._media = list()

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

        Three panels are created and organized:

            - player_controls_panel
            - audio_panel
            - video_panel

        """
        # Add the splitter window and a panel to control its properties
        splitter = sppasMultiSplitterPanel(self,
                                           style=wx.SP_LIVE_UPDATE,
                                           name="splitter")
        splitter.SetOrientation(wx.VERTICAL)
        splitter.SetMinimumPaneSize(sppasPanel.fix_size(112))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Fill in the splitter with panels
        tb = sppasPlayerControlsPanel(splitter, name="player_controls_panel")
        self.__customize_controls(tb)
        splitter.AppendWindow(tb, tb.GetSize()[1])

        pa = sppasPanel(splitter, name="audio_panel")
        pa_sizer = wx.BoxSizer(wx.VERTICAL)
        pa_sizer.Add(sppasAudioAmplitudePanel(pa), 1, wx.EXPAND)
        pa.SetSizer(pa_sizer)
        splitter.AppendWindow(pa, sppasPanel.fix_size(128))

        pv = sppasPanel(splitter, name="video_panel")
        pv_sizer = wx.WrapSizer(orient=wx.HORIZONTAL)
        pv_sizer.Add(sppasVideoAmplitudePanel(pv), 1, wx.EXPAND)
        pv.SetSizer(pv_sizer)
        splitter.AppendWindow(pv, sppasPanel.fix_size(128))

    # -----------------------------------------------------------------------

    def __customize_controls(self, control_panel):

        # to switch panels 1 & 3
        btn1 = BitmapTextButton(control_panel.GetWidgetsPanel(), label="", name="exchange_1")
        control_panel.SetButtonProperties(btn1)
        control_panel.AddWidget(btn1)

        # to switch panels 2 & 3
        btn2 = BitmapTextButton(control_panel.GetWidgetsPanel(), label="", name="exchange_2")
        control_panel.SetButtonProperties(btn2)
        control_panel.AddWidget(btn2)

        # change the orientation
        btn3 = BitmapTextButton(control_panel.GetWidgetsPanel(), label="", name="rotate_screen")
        control_panel.SetButtonProperties(btn3)
        control_panel.AddWidget(btn3)

        # a static label to indicate something
        text = sppasStaticText(control_panel.GetWidgetsPanel(), label="No file", style=wx.ALIGN_CENTRE, name="free_statictext")
        text.SetMinSize(wx.Size(-1, sppasPanel.fix_size(32)))
        control_panel.AddWidget(text)

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
        self.FindWindow("splitter").Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnChanged)
        self.FindWindow("splitter").Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnChanging)

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
        name = event.action
        wx.LogDebug("Received a player event. "
                    "Action is {:s}. Value is {:s}"
                    "".format(name, str(event.value)))

        if name == "play":
            self.play()

        elif name == "stop":
            self.stop()

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """
        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "exchange_1":
            self.SwapPanels(1, 3)

        elif name == "exchange_2":
            self.SwapPanels(2, 3)

        elif name == "rotate_screen":
            # self.SetOrientation()
            pass

    # -----------------------------------------------------------------------

    def is_playing(self):
        """Return True if at least one of the media is playing."""
        for panel in self._media:
            if panel.IsExpanded() is True:
                pass
        return False

    # -----------------------------------------------------------------------

    def play(self):
        """Play the selected media."""
        controls = self.FindWindow("player_controls_panel")
        replay = controls.IsReplay()
        is_playing = self.is_playing()
        for panel in self._media:
            if panel.IsExpanded() is True:
                if is_playing is True:
                    # this media is stopped or playing
                    panel.GetPane().Pause()
                else:
                    # this media is stopped or paused
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
        if evt.GetSashPosition() > sppasPanel.fix_size(512):
            evt.Veto()

        # Or you can reset the sash position to whatever you want
        #if evt.GetSashPosition() < 5:
        #    evt.SetSashPosition(25)

    # -----------------------------------------------------------------------

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

    def SwapPanels(self, orig, dest):
        win_orig = self.FindWindow("splitter").GetWindow(orig)
        win_dest = self.FindWindow("splitter").GetWindow(dest)
        self.FindWindow("splitter").ExchangeWindows(win_orig, win_dest)

# ---------------------------------------------------------------------------


class TestPanel(sppasPlayerPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)

        # self.add_media(os.path.join(paths.samples,
        #                             "samples-fra",
        #                             "F_F_B003-P8.wav"))
        # self.add_media(os.path.join(paths.samples,
        #                             "samples-fra",
        #                             "F_F_C006-P6.wav"))
        # self.add_media("/Users/bigi/Movies/Monsters_Inc.For_the_Birds.mpg")
        # self.add_media(os.path.join(paths.samples, "multimedia-fra", "video.mkv"))
