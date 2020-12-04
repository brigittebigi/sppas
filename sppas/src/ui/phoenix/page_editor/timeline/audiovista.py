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

    src.ui.phoenix.page_editor.timeline.audiovista.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.utils import b

from sppas.src.ui.phoenix.windows.panels import sppasPanel
from ..datactrls import sppasWaveformWindow

# ---------------------------------------------------------------------------


class AudioData(object):
    def __init__(self):
        self.sampwidth = 0
        self.nchannels = 0
        self.framerate = 0
        self.duration = 0.
        self.frames = b("")

# ---------------------------------------------------------------------------


class sppasAudioVista(sppasPanel):
    """Create a panel to display an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Events emitted by this class:

        - MediaEvents.MediaActionEvent

    """

    # -----------------------------------------------------------------------
    # This object size.
    # By default, it is a DFHD aspect ratio (super ultra-wide displays) 32:9
    MIN_WIDTH = 178
    MIN_HEIGHT = 50

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
                 name="audiovista_panel"):
        """Create an instance of sppasAudioVista.

        :param parent: (wx.Window) parent window. Must not be None;
        :param id: (int) window identifier. -1 indicates a default value;
        :param pos: the control position. (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython,
         depending on platform;
        :param name: (str) Name of the media panel.

        """
        size = wx.Size(sppasAudioVista.MIN_WIDTH,
                       sppasAudioVista.MIN_HEIGHT)
        super(sppasAudioVista, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        # The information we need about the audio, no more!
        self.__audio = AudioData()

        # All possible views
        self.__infos = None
        self.__waveform = None
        self.__spectral = None
        self.__level = None

        # Zoom level
        self._zoom = 100.

        self._create_content()

    # -----------------------------------------------------------------------

    def set_visible_period(self, start, end):
        """Set a period in time to draw the some of the views.

        :param start: (float) Start time in seconds.
        :param end: (float) End time in seconds.

        """
        # Convert the time (in seconds) into a position in the frames
        start_pos = self._time_to_frames(start)
        end_pos = self._time_to_frames(end)
        frames = self.__audio.frames[start_pos:end_pos]
        try:
            self.__waveform.SetData(frames, self.__audio.sampwidth, self.__audio.nchannels)
        except Exception as e:
            wx.LogError("The audio can't set frames to waveform: {}"
                        "".format(str(e)))

    # -----------------------------------------------------------------------

    def set_selection_period(self, start, end):
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _time_to_frames(self, time_value):
        return int(time_value * float(self.__audio.framerate)) * \
               self.__audio.sampwidth * \
               self.__audio.nchannels

    # -----------------------------------------------------------------------

    def set_audio_data(self, nchannels=None, sampwidth=None, framerate=None, duration=None, frames=None):
        """Set all or any of the data we need about the audio."""
        if nchannels is not None:
            self.__audio.nchannels = int(nchannels)
        if sampwidth is not None:
            self.__audio.sampwidth = int(sampwidth)
        if framerate is not None:
            self.__audio.framerate = int(framerate)
        if duration is not None:
            self.__audio.duration = float(duration)
        if frames is not None:
            self.__audio.frames = frames

        self.__set_infos()

    # -----------------------------------------------------------------------
    # Enable/Disable the views
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
        if value is True:
            self.__infos.Show()
            return True

        self.__infos.Hide()
        self.SetMinSize(wx.Size(-1, self.get_min_height()))
        return False

    # -----------------------------------------------------------------------

    def show_waveform(self, value):
        """Show or hide the waveform.

        Can't be enabled if the audio has more than 1 channel.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True:  # and self.__audioplay.get_nchannels() == 1:
            self.__waveform.Show()
            return True

        self.__waveform.Hide()
        self.SetMinSize(wx.Size(-1, self.get_min_height()))
        return False

    # -----------------------------------------------------------------------

    def infos_shown(self):
        return self.__infos.IsShown()

    def waveform_shown(self):
        return self.__waveform.IsShown()

    # -----------------------------------------------------------------------
    # Height of views
    # -----------------------------------------------------------------------

    def get_infos_height(self):
        """Return the height required to draw the audio information.

        This height does not depend on the zoom level.
        It depends only on the font height.

        """
        try:
            # make this height proportional to the font
            return sppasPanel.fix_size(sppasAudioVista.INFOS_HEIGHT)
        except AttributeError:
            return sppasAudioVista.INFOS_HEIGHT

    # -----------------------------------------------------------------------

    def get_waveform_height(self):
        """Return the height required to draw the Waveform.

        This height depends on both the zoom level and the font height.

        """
        h = int(float(sppasAudioVista.WAVEFORM_HEIGHT) * self._zoom / 100.)
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
                h += sppasAudioVista.INFOS_HEIGHT
        if self.__waveform is not None:
            if self.__waveform.IsShown():
                h += sppasAudioVista.WAVEFORM_HEIGHT
        if self.__level is True:
            if self.__level.IsShown():
                h += sppasAudioVista.LEVEL_HEIGHT
        if self.__spectral is True:
            if self.__spectral.IsShown():
                h += sppasAudioVista.SPECTRAL_HEIGHT

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
        value = float(value)
        if value < 25.:
            value = 25.
        if value > 400.:
            value = 400.
        self._zoom = value

        if self.__infos is not None:
            self.__infos.SetMinSize(wx.Size(-1, self.get_infos_height()))
        if self.__waveform is not None:
            self.__waveform.SetMinSize(wx.Size(-1, self.get_waveform_height()))

        self.SetMinSize(wx.Size(-1, self.get_min_height()))
        self.SendSizeEventToParent()

    # -----------------------------------------------------------------------
    # Create the panel content
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Construct our panel."""
        s = wx.BoxSizer(wx.VERTICAL)
        self.__infos = self.__create_infos_panel()
        self.__waveform = self.__create_waveform_panel()
        s.Add(self.__infos, 0, wx.EXPAND, border=0)
        s.Add(self.__waveform, 0, wx.EXPAND, border=0)
        self.SetSizer(s)
        self.SetAutoLayout(True)
        self.SetMinSize(wx.Size(-1, self.get_min_height()))

    # -----------------------------------------------------------------------

    def __create_infos_panel(self):
        st = wx.StaticText(self, id=-1, label="No audio", name="infos_panel")
        st.SetMinSize(wx.Size(-1, self.get_infos_height()))
        return st

    # -----------------------------------------------------------------------

    def __create_waveform_panel(self):
        wp = sppasWaveformWindow(self)
        wp.SetMinSize(wx.Size(-1, self.get_waveform_height()))
        return wp

    # -----------------------------------------------------------------------

    def __set_infos(self):
        audio_prop = str(self.__audio.sampwidth*16) + " bits, " + \
                     str(self.__audio.framerate) + " Hz, " + \
                     "%.3f" % self.__audio.duration + " seconds, " +  \
                     str(self.__audio.nchannels) + " channel "

        self.FindWindow("infos_panel").SetLabel(audio_prop)
        self.FindWindow("infos_panel").Refresh()

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="AudioVista Panel")

        btn5 = wx.Button(self, -1, "Zoom in")
        self.Bind(wx.EVT_BUTTON, self._on_zoom_in, btn5)
        btn6 = wx.Button(self, -1, "Zoom 100%")
        self.Bind(wx.EVT_BUTTON, self._on_zoom, btn6)
        btn7 = wx.Button(self, -1, "Zoom out")
        self.Bind(wx.EVT_BUTTON, self._on_zoom_out, btn7)

        self.ap = sppasAudioVista(self)

        sp = wx.BoxSizer()
        sp.Add(btn5, 0, wx.ALL, 4)
        sp.Add(btn6, 0, wx.ALL, 4)
        sp.Add(btn7, 0, wx.ALL, 4)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sp, 0, wx.EXPAND, 4)
        sizer.Add(self.ap, 0, wx.EXPAND)
        self.SetSizer(sizer)

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
