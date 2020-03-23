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

    src.ui.phoenix.windows.datactrls.waveform.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A window to draw the amplitude of a fragment of a channel.

"""

import os
import time
import wx

from sppas import paths
from sppas.src.audiodata.aio import open as audio_open
from sppas.src.audiodata.autils import extract_channel_fragment
from sppas.src.audiodata import sppasAudioFrames
from sppas.src.audiodata import sppasChannel
from .basedatactrl import sppasBaseDataWindow

# ---------------------------------------------------------------------------


class sppasWaveformWindow(sppasBaseDataWindow):
    """A base window with a DC to draw amplitude of a channel of an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 data=None,
                 style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="waveform"):
        """Initialize a new sppasWaveformWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param data:   a list of samples
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param name:      Window name.

        """
        self._auto_scroll = False
        self._data_max = 0
        self._data_min = 0
        self._sampwidth = 0

        super(sppasWaveformWindow, self).__init__(
            parent, id, data, pos, size, style, name)

        self.SetSelectable(False)
        self.SetFocusWidth(0)

        self._pen_width = 1

    # -----------------------------------------------------------------------

    def SetAutoScroll(self, value):
        value = bool(value)
        if value != self._auto_scroll:
            self._auto_scroll = value
            self.SetData([self._data, self._sampwidth])
            self.Refresh()

    # -----------------------------------------------------------------------

    def SetData(self, data):
        """Override. Set new data content.

        :param data: (list of samples, samples width)

        """
        self._data = data[0]
        self._sampwidth = data[1]

        if self._auto_scroll is False:
            self._data_max = sppasAudioFrames().get_maxval(self._sampwidth)
            self._data_min = -self._data_max
        else:
            # autoscroll is limited to at least 10%
            self._data_max = max(max(self._data) + 1, (self._data_max * 0.1))
            self._data_min = min(min(self._data) - 1, -(self._data_max * 0.1))

        self.Refresh()

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Draw the amplitude values as a waveform."""

        if self._data is None:
            return

        x, y, w, h = self.GetContentRect()
        ycenter = y + (h // 2)
        ypixelsminprec = ycenter
        xprec = x
        xcur = (x + (self._pen_width // 2))
        d = 0

        # Number of samples to be read at each step
        incd = int(len(self._data) / (w/self._pen_width))
        while incd < 2:
            self._pen_width += 1
            incd = int(len(self._data) / (w/self._pen_width))

        # Draw an horizontal line at the middle (0 value)
        pen = wx.Pen(wx.Colour(64, 64, 212, 128), 1, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)
        dc.DrawLine(x, ycenter, x+w, ycenter)

        # Fix the pen style and color
        pen = wx.Pen(self.GetPenForegroundColour(), self._pen_width, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)

        while xcur < (x+w):

            # Get data of n frames (data of xsteps pixels of time) -- width
            dnext = min((d+incd), len(self._data))
            if d == dnext:
                data = self._data[d:d+1]
            else:
                data = self._data[d:dnext]

            # Get min and max (take care if saturation...)
            datamin = max(min(data), self._data_min + 1)
            datamax = min(max(data), self._data_max - 1)

            # convert the data into a "number of pixels" -- height
            ypixelsmax = int(float(datamax) * (float(h)/2.0) / float(self._data_max))
            if self._data_min != 0:
                ypixelsmin = int(float(datamin) * (float(h)/2.0) / float(abs(self._data_min)))
            else:
                ypixelsmin = 0

            # draw a line between prec. value to current value
            dc.DrawLine(xprec, ycenter-ypixelsminprec, xcur, ycenter-ypixelsmax)
            dc.DrawLine(xcur,  ycenter-ypixelsmin, xcur, ycenter-ypixelsmax)

            ypixelsminprec = ypixelsmin

            # set values for next step
            xprec = xcur
            xcur = xcur + self._pen_width
            d = dnext

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test Waveform")

        sample = os.path.join(paths.samples, "samples-eng", "oriana1.wav")   # mono
        self._audio = audio_open(sample)

        sizer = wx.BoxSizer(wx.VERTICAL)
        w1 = self.__draw_waveform(2., 3.)
        w2 = self.__draw_waveform(2.56, 2.60)
        sizer.Add(w1, 1, wx.EXPAND)
        sizer.Add(w2, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def __draw_waveform(self, start_time, end_time):
        nframes = int((end_time - start_time) * self._audio.get_framerate())
        self._audio.seek(int(start_time * float(self._audio.get_framerate())))
        # read samples of all channels. Channel 0 is data[0]
        data = self._audio.read_samples(nframes)
        w = sppasWaveformWindow(self, data=(data[0], self._audio.get_sampwidth()))
        return w




