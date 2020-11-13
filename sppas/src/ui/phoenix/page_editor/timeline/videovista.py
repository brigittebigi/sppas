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

    src.ui.phoenix.page_editor.timeline.videovista.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas.src.config import paths

from sppas.src.ui.phoenix.windows.panels import sppasPanel

# ---------------------------------------------------------------------------


class VideoData(object):
    def __init__(self):
        self.framerate = 0
        self.duration = 0.
        self.width = 0
        self.height = 0

# ---------------------------------------------------------------------------


class sppasVideoVista(sppasPanel):
    """Create a panel to display a summary of a video.

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
    FILM_HEIGHT = 100

    # -----------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 name="videovista_panel"):
        """Create an instance of sppasVideoVista.

        :param parent: (wx.Window) parent window. Must not be None;
        :param id: (int) window identifier. -1 indicates a default value;
        :param pos: the control position. (-1, -1) indicates a default
         position, chosen by either the windowing system or wxPython,
         depending on platform;
        :param name: (str) Name of the media panel.

        """
        size = wx.Size(sppasVideoVista.MIN_WIDTH,
                       sppasVideoVista.MIN_HEIGHT)
        super(sppasVideoVista, self).__init__(
            parent, id, pos, size,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=name)

        # The information we need about the audio, no more!
        self.__video = VideoData()

        # All possible views
        self.__infos = None
        self.__film = None

        # Zoom level
        self._zoom = 100.

        self._create_content()

    # -----------------------------------------------------------------------

    def set_video_data(self,  framerate=None, duration=None, width=None, height=None):
        """Set all or any of the data we need about the video."""
        if framerate is not None:
            self.__video.framerate = int(framerate)
        if duration is not None:
            self.__video.duration = float(duration)
        if width is not None:
            self.__video.width = width
        if height is not None:
            self.__video.height = height

        self.__set_infos()

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
        try:
            # make this height proportional to the font
            return sppasPanel.fix_size(sppasVideoVista.INFOS_HEIGHT)
        except AttributeError:
            return sppasVideoVista.INFOS_HEIGHT

    # -----------------------------------------------------------------------

    def get_film_height(self):
        """Return the height required to draw the film."""
        h = int(float(sppasVideoVista.FILM_HEIGHT) * self._zoom / 100.)
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
                h += self.get_infos_height()
        if self.__film is not None:
            if self.__film.IsShown():
                h += self.get_film_height()

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
        self.__film = self.__create_film_panel()
        s.Add(self.__infos, 0, wx.EXPAND, border=0)
        s.Add(self.__film, 0, wx.EXPAND, border=0)
        self.SetSizerAndFit(s)
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
        video_prop = str(self.__video.framerate) + " fps, " + \
                     "%.3f" % self.__video.duration + " seconds, " +  \
                     str(self.__video.width) + "x" + \
                     str(self.__video.height)

        self.FindWindow("infos_panel").SetLabel(video_prop)
        self.FindWindow("infos_panel").Refresh()

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="VideoVista Panel")

        btn5 = wx.Button(self, -1, "Zoom in")
        self.Bind(wx.EVT_BUTTON, self._on_zoom_in, btn5)
        btn6 = wx.Button(self, -1, "Zoom 100%")
        self.Bind(wx.EVT_BUTTON, self._on_zoom, btn6)
        btn7 = wx.Button(self, -1, "Zoom out")
        self.Bind(wx.EVT_BUTTON, self._on_zoom_out, btn7)

        self.ap = sppasVideoVista(self)

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
