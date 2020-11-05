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

    src.ui.phoenix.windows.media.videopanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires opencv library to play the video file stream. Do not play the
    audio streams embedded in the video: display only the frames.

"""

import os
import wx

from sppas.src.config import paths
from sppas.src.config import MediaState

from ..panels import sppasPanel

from .mediaevents import MediaEvents
from .mediatype import MediaType
from src.ui.players.wxvideoplay import sppasVideoPlayer

# ---------------------------------------------------------------------------


class sppasVideoPanel(sppasPanel):
    """Create a panel to play and display a video.

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
    # Default height of each element of this control
    INFOS_HEIGHT = 20
    FILM_HEIGHT = 100

    # -----------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 name="video_panel"):
        """Create an instance of sppasVideoPanel.

        :param parent: (wx.Window) parent window. Must not be None;
        :param id: (int) window identifier. -1 indicates a default value;
        :param pos: the control position. (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython,
         depending on platform;
        :param name: (str) Name of the media panel.

        """
        size = wx.Size(sppasVideoPanel.MIN_WIDTH,
                       sppasVideoPanel.MIN_HEIGHT)
        super(sppasVideoPanel, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        # Members
        self._mt = MediaType().video
        self._ms = MediaState().unknown
        self._zoom = 100.
        self.__videoplay = sppasVideoPlayer(self)

        # All possible views
        self.__infos = None
        self.__film = None

        self._create_content()

        # Custom event to inform the media is loaded
        self.__videoplay.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.__videoplay.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        self.__videoplay.Bind(wx.EVT_TIMER, self.__on_timer)

    # -----------------------------------------------------------------------

    def media_type(self):
        """Return the media type.

        :return: (MediaType) The media type value

        """
        return self._mt

    # -----------------------------------------------------------------------
    # Play the video
    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the file associated to the media or None."""
        return self.__videoplay.get_filename()

    # -----------------------------------------------------------------------

    def load(self, filename):
        self.__videoplay.load(filename)

    # -----------------------------------------------------------------------

    def play(self):
        self.__videoplay.play()

    def pause(self):
        self.__videoplay.pause()

    def stop(self):
        self.__videoplay.stop()

    def seek(self, value):
        self.__videoplay.seek(value)

    def tell(self):
        return self.__videoplay.tell()

    # ----------------------------------------------------------------------

    def set_period(self, start, end):
        """Fix the period of time to play and display.

        :param start_time: (float) Time to start playing in seconds
        :param end_time: (float) Time to stop playing in seconds

        """
        self.__videoplay.set_period(start, end)
        # todo: set the period to the film panel

    # ----------------------------------------------------------------------
    # Getters for video infos
    # -----------------------------------------------------------------------

    def get_framerate(self):
        if self.__videoplay is None:
            return 0
        return self.__videoplay.get_framerate()

    framerate = property(fget=get_framerate)

    # -----------------------------------------------------------------------

    def get_duration(self):
        if self.__videoplay is None:
            return 0.
        return self.__videoplay.get_duration()

    duration = property(fget=get_duration)

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the frames in the video."""
        return self.__videoplay.get_width()

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the frames in the video."""
        return self.__videoplay.get_height()

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
        if value is True:
            self.__infos.Show()
            return True

        self.__infos.Hide()
        return False

    # -----------------------------------------------------------------------

    def show_film(self, value):
        """Show or hide the film -  sequence of pictures of the video.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True:
            self.__film.Show()
            return True

        self.__film.Hide()
        return False

    # -----------------------------------------------------------------------
    # Height of the views
    # -----------------------------------------------------------------------

    def get_infos_height(self):
        """Return the height required to draw the video information."""
        h = int(float(sppasVideoPanel.INFOS_HEIGHT) * self._zoom / 100.)
        try:
            # make this height proportional
            h = sppasPanel.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def get_film_height(self):
        """Return the height required to draw the film."""
        h = int(float(sppasVideoPanel.FILM_HEIGHT) * self._zoom / 100.)
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
                h += sppasVideoPanel.INFOS_HEIGHT
        if self.__film is not None:
            if self.__film.IsShown():
                h += sppasVideoPanel.FILM_HEIGHT

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
        value = int(value)
        if value < 25.:
            value = 25.
        if value > 400.:
            value = 400.
        self._zoom = value

        if self.__infos is not None:
            self.__infos.SetMinSize(wx.Size(-1, self.get_infos_height()))
        if self.__film is not None:
            self.__film.SetMinSize(wx.Size(-1, self.get_film_height()))

        self.SetMinSize(wx.Size(-1, self.get_min_height()))
        self.SendSizeEventToParent()

    # -----------------------------------------------------------------------
    # Create the panel content
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Construct our panel, made only of the media control."""
        s = wx.BoxSizer(wx.VERTICAL)
        self.__infos = self.__create_infos_panel()
        self.__waveform = self.__create_film_panel()
        s.Add(self.__infos, 1, wx.EXPAND, border=0)
        s.Add(self.__waveform, 1, wx.EXPAND, border=0)
        self.SetSizer(s)
        self.SetAutoLayout(True)
        self.SetMinSize(wx.Size(-1, self.get_min_height()))

    # -----------------------------------------------------------------------

    def __create_infos_panel(self):
        st = wx.StaticText(self, id=-1, label="No video", name="infos_panel")
        st.SetMinSize(wx.Size(-1, self.get_infos_height()))

        return st

    # -----------------------------------------------------------------------

    def __create_film_panel(self):
        wp = sppasPanel(self)  # sppasFilmPanel(self)
        wp.SetMinSize(wx.Size(-1, self.get_film_height()))
        return wp

    # -----------------------------------------------------------------------

    def __set_infos(self):
        audio_prop = str(self.get_framerate()) + " fps, " + \
                     "%.3f" % self.get_duration() + " seconds, " +  \
                     str(self.get_width()) + "x" + \
                     str(self.get_height())

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
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="VideoPanel")

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

        self.vp = sppasVideoPanel(self)

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
        sizer.Add(self.vp, 0, wx.EXPAND, 4)
        self.SetSizer(sizer)

        # events
        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        self.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self.DoLoadFile)

    # ----------------------------------------------------------------------

    def DoLoadFile(self):
        wx.LogDebug("Start loading audio...")
        self.vp.load(os.path.join(paths.samples, "faces", "video_sample.mp4"))
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
        self.vp.seek(float(time_pos_ms) / 1000.)

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        self.vp.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        self.vp.pause()

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        self.vp.stop()
        time_pos = self.vp.tell()
        self.slider.SetValue(int(time_pos * 1000.))

    # ----------------------------------------------------------------------

    def _on_zoom_in(self, evt):
        zoom = self.vp.get_zoom()
        zoom *= 1.25
        self.vp.set_zoom(zoom)

    # ----------------------------------------------------------------------

    def _on_zoom_out(self, evt):
        zoom = self.vp.get_zoom()
        zoom *= 0.75
        self.vp.set_zoom(zoom)

    # ----------------------------------------------------------------------

    def _on_zoom(self, evt):
        self.vp.set_zoom(100.)

    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        time_pos = self.vp.tell()
        self.slider.SetValue(int(time_pos * 1000.))
        event.Skip()

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        wx.LogDebug("Video file loaded successfully")
        self.FindWindow("btn_play").Enable(True)
        self.slider.SetRange(0, int(self.vp.duration * 1000.))

        # self.vp.set_period(10., 12.)
        # self.vp.seek(10.)
        # self.slider.SetRange(10000, 12000)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        wx.LogError("Video file not loaded")
        self.FindWindow("btn_play").Enable(False)
        self.slider.SetRange(0, 0)
