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

    src.ui.phoenix.windows.media.audiopanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires simpleaudio library to play the audio file stream.

"""

import os
import wx

from sppas.src.config import paths
from sppas.src.config import MediaState

from ..panels import sppasPanel
from ..datactrls import sppasWaveformWindow

from .mediaevents import MediaEvents
from .mediatype import MediaType
from .audioplay import sppasAudioPlayer

# ---------------------------------------------------------------------------


class sppasAudioPanel(sppasPanel):
    """Create a panel to play and display an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Events emitted by this class:

        - MediaEvents.MediaActionEvent
        - MediaEvents.MediaLoadedEvent
        - MediaEvents.MediaNotLoadedEvent

    """

    # -----------------------------------------------------------------------
    # This object size.
    # By default, it is a DFHD aspect ratio (super ultra-wide displays) 32:9
    MIN_WIDTH = 178
    MIN_HEIGHT = 50

    # -----------------------------------------------------------------------
    # Delays for loading media files
    # LOAD_DELAY = 500
    # MAX_LOAD_DELAY = 3000

    # -----------------------------------------------------------------------
    # Default height of each element of this control
    INFOS_HEIGHT = 20
    WAVEFORM_HEIGHT = 100
    SPECTRAL_HEIGHT = 100
    LEVEL_HEIGHT = 30

    # -----------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 name="audio_panel"):
        """Create an instance of sppasAudioPanel.

        :param parent: (wx.Window) parent window. Must not be None;
        :param id: (int) window identifier. -1 indicates a default value;
        :param pos: the control position. (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython,
         depending on platform;
        :param name: (str) Name of the media panel.

        """
        size = wx.Size(sppasAudioPanel.MIN_WIDTH,
                       sppasAudioPanel.MIN_HEIGHT)
        super(sppasAudioPanel, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        # Members
        self._mt = MediaType().audio
        self._ms = MediaState().unknown
        self._zoom = 100.
        self.__audioplay = sppasAudioPlayer(self)

        # All possible views
        self.__infos = None
        self.__waveform = None
        self.__spectral = None
        self.__level = None

        self._create_content()

        # Custom event to inform the media is loaded
        self.__audioplay.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.__audioplay.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        self.__audioplay.Bind(wx.EVT_TIMER, self.__on_timer)

    # -----------------------------------------------------------------------
    # Play the audio
    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the file associated to the media or None."""
        return self.__audioplay.get_filename()

    # -----------------------------------------------------------------------

    def load(self, filename):
        self.__audioplay.load(filename)

    # -----------------------------------------------------------------------

    def play(self):
        self.__audioplay.play()

    def pause(self):
        self.__audioplay.pause()

    def stop(self):
        self.__audioplay.stop()

    def seek(self, value):
        self.__audioplay.seek(value)

    def tell(self):
        return self.__audioplay.tell()

    # ----------------------------------------------------------------------

    def set_period(self, start, end):
        """Fix the period of time to play and display.

        :param start_time: (float) Time to start playing in seconds
        :param end_time: (float) Time to stop playing in seconds

        """
        self.__audioplay.set_period(start, end)
        # todo: set the period to the waveform panel

    # -----------------------------------------------------------------------
    # Getters for audio infos
    # -----------------------------------------------------------------------

    def get_nchannels(self):
        if self.__audioplay is None:
            return 0
        return self.__audioplay.get_nchannels()

    nchannels = property(fget=get_nchannels)

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        if self.__audioplay is None:
            return 0
        return self.__audioplay.get_sampwidth()

    sampwidth = property(fget=get_sampwidth)

    # -----------------------------------------------------------------------

    def get_framerate(self):
        if self.__audioplay is None:
            return 0
        return self.__audioplay.get_framerate()

    framerate = property(fget=get_framerate)

    # -----------------------------------------------------------------------

    def get_duration(self):
        if self.__audioplay is None:
            return 0.
        return self.__audioplay.get_duration()

    duration = property(fget=get_duration)

    # -----------------------------------------------------------------------
    # Enable/Disable views
    # -----------------------------------------------------------------------

    def show_infos(self, value):
        """Show or hide the audio infos.

        Can't be disabled if the audio failed to be loaded.

        :param value: (bool)
        :return: (bool)

        """
        if self.__infos is None:
            return
        value = bool(value)
        if value is True and self.__audioplay.get_nchannels() > 0:
            self.__infos.Show()
            return True

        self.__infos.Hide()
        return False

    # -----------------------------------------------------------------------

    def show_waveform(self, value):
        """Show or hide the waveform.

        Can't be enabled if the audio has more than 1 channel.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audioplay.get_nchannels() == 1:
            self.__waveform.Show()
            return True

        self.__waveform.Hide()
        return False

    # -----------------------------------------------------------------------
    # Height of views
    # -----------------------------------------------------------------------

    def get_infos_height(self):
        """Return the height required to draw the audio information."""
        h = int(float(sppasAudioPanel.INFOS_HEIGHT) * self._zoom / 100.)
        try:
            # make this height proportional
            h = sppasPanel.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def get_waveform_height(self):
        """Return the height required to draw the Waveform."""
        h = int(float(sppasAudioPanel.WAVEFORM_HEIGHT) * self._zoom / 100.)
        try:
            h = sppasPanel.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def get_min_height(self):
        """Return the min height required to draw all views."""
        h = 0
        if self.__infos is not None:
            if self.__infos.IsShown():
                h += sppasAudioPanel.INFOS_HEIGHT
        if self.__waveform is not None:
            if self.__waveform.IsShown():
                h += sppasAudioPanel.WAVEFORM_HEIGHT
        if self.__level is True:
            if self.__level.IsShown():
                h += sppasAudioPanel.LEVEL_HEIGHT
        if self.__spectral is True:
            if self.__spectral.IsShown():
                h += sppasAudioPanel.SPECTRAL_HEIGHT

        # Apply the current zoom value
        h = int(float(h) * self._zoom / 100.)

        try:
            # make this height proportional
            h = sppasPanel.fix_size(h)
        except AttributeError:
            pass

        return h

    # -----------------------------------------------------------------------

    def get_zoom(self):
        """Return the current zoom percentage value."""
        return self._zoom

    # -----------------------------------------------------------------------

    def set_zoom(self, value):
        """Fix the zoom percentage value.

        This coefficient is applied to the min size of each view panel.

        :param value: (int) Percentage of zooming, in range 25 .. 400.

        """
        print("set zoom percent to %f " % value)
        value = int(value)
        if value < 25.:
            value = 25.
        if value > 400.:
            value = 400.
        self._zoom = value

        if self.__infos is not None:
            print(" -> new infos height: %d" % self.get_infos_height())
            self.__infos.SetMinSize(wx.Size(-1, self.get_infos_height()))
        if self.__waveform is not None:
            print(" -> new wave height: %d" % self.get_waveform_height())
            self.__waveform.SetMinSize(wx.Size(-1, self.get_waveform_height()))

        print(" -> new PANEL height: %d" % self.get_min_height())
        self.SetMinSize(wx.Size(-1, self.get_min_height()))
        # self.Layout()
        # self.Refresh()
        self.SendSizeEventToParent()

    # -----------------------------------------------------------------------
    # Create the panel content
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Construct our panel, made only of the media control."""
        s = wx.BoxSizer(wx.VERTICAL)
        self.__infos = self.__create_infos_panel()
        self.__waveform = self.__create_waveform_panel()
        s.Add(self.__infos, 1, wx.EXPAND, border=0)
        s.Add(self.__waveform, 1, wx.EXPAND, border=0)
        self.SetSizer(s)
        self.SetAutoLayout(True)
        self.SetMinSize(wx.Size(-1, self.get_min_height()))

    # -----------------------------------------------------------------------

    def __create_infos_panel(self):
        st = wx.StaticText(self, id=-1, label="", name="infos_panel")
        st.SetMinSize(wx.Size(-1, self.get_infos_height()))

        return st

    # -----------------------------------------------------------------------

    def __create_waveform_panel(self):
        wp = sppasWaveformWindow(self)
        wp.SetMinSize(wx.Size(-1, self.get_waveform_height()))
        return wp

    # -----------------------------------------------------------------------

    def __set_infos(self):
        audio_prop = str(self.get_sampwidth()*16) + " bits, " + \
                     str(self.get_framerate()) + " Hz, " + \
                     "%.3f" % self.get_duration() + " seconds, " +  \
                     str(self.get_nchannels()) + " channel "

        self.FindWindow("infos_panel").SetLabel(audio_prop)
        self.FindWindow("infos_panel").Refresh()

    # -----------------------------------------------------------------------
    # Events
    # -----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        self.__set_infos()
        wx.PostEvent(self.GetParent(), event)

    def __on_media_not_loaded(self, event):
        wx.PostEvent(self.GetParent(), event)

    def __on_timer(self, event):
        wx.PostEvent(self.GetParent(), event)

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="AudioPanel")

        btn2 = wx.Button(self, -1, "Play", name="btn_play")
        btn2.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._on_play_ap, btn2)
        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self._on_pause_ap, btn3)
        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self._on_stop_ap, btn4)

        btn5 = wx.Button(self, -1, "Zoom in")
        self.Bind(wx.EVT_BUTTON, self._on_zoom_in, btn5)
        btn6 = wx.Button(self, -1, "Zoom 100%")
        self.Bind(wx.EVT_BUTTON, self._on_zoom, btn6)
        btn7 = wx.Button(self, -1, "Zoom out")
        self.Bind(wx.EVT_BUTTON, self._on_zoom_out, btn7)

        # a slider to display the current position
        self.slider = wx.Slider(self, -1, 0, 0, 10, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.slider.SetMinSize(wx.Size(250, -1))
        self.Bind(wx.EVT_SLIDER, self._on_seek_slider, self.slider)

        self.ap = sppasAudioPanel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sp = wx.BoxSizer()
        sp.Add(btn2, 0, wx.ALL, 4)
        sp.Add(btn3, 0, wx.ALL, 4)
        sp.Add(btn4, 0, wx.ALL, 4)
        sp.AddStretchSpacer(1)
        sp.Add(btn5, 0, wx.ALL, 4)
        sp.Add(btn6, 0, wx.ALL, 4)
        sp.Add(btn7, 0, wx.ALL, 4)

        sizer.Add(sp, 0, wx.EXPAND, 4)
        sizer.Add(self.slider, 0, wx.EXPAND, 4)
        sizer.Add(self.ap, 0, wx.EXPAND, 4)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_TIMER, self._on_timer)

        # Custom event to inform the media is loaded
        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)

        wx.CallAfter(self.DoLoadFile)

    # ----------------------------------------------------------------------

    def DoLoadFile(self):
        wx.LogDebug("Start loading audio...")
        self.ap.load(os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))
        wx.LogDebug("audio loaded.")

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        self.FindWindow("btn_play").Enable(True)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        wx.LogError("Media not loaded")
        self.FindWindow("btn_play").Enable(False)

    # ----------------------------------------------------------------------

    def _on_seek_slider(self, event):
        time_pos_ms = self.slider.GetValue()
        self.ap.seek(float(time_pos_ms) / 1000.)

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        self.ap.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        self.ap.pause()

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        self.ap.stop()
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))

    # ----------------------------------------------------------------------

    def _on_zoom_in(self, evt):
        zoom = self.ap.get_zoom()
        zoom *= 1.25
        self.ap.set_zoom(zoom)

    # ----------------------------------------------------------------------

    def _on_zoom_out(self, evt):
        zoom = self.ap.get_zoom()
        zoom *= 0.75
        self.ap.set_zoom(zoom)

    # ----------------------------------------------------------------------

    def _on_zoom(self, evt):
        self.ap.set_zoom(100.)

    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))
        event.Skip()

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        wx.LogDebug("Audio file loaded successfully")
        self.FindWindow("btn_play").Enable(True)
        self.slider.SetRange(0, int(self.ap.duration * 1000.))

        # self.ap.set_period(10., 12.)
        # self.ap.seek(10.)
        # self.slider.SetRange(10000, 12000)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        wx.LogError("Audio file not loaded")
        self.FindWindow("btn_play").Enable(False)
        self.slider.SetRange(0, 0)
