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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A window to draw the amplitude of a fragment of a channel.

"""

import os
import wx

from sppas.src.config import paths
from sppas.src.audiodata.aio import open as audio_open
from sppas.src.audiodata import sppasAudioFrames
from sppas.src.audiodata.audioconvert import sppasAudioConverter

from .basedatactrl import sppasDataWindow

# ---------------------------------------------------------------------------


class sppasWaveformWindow(sppasDataWindow):
    """A base window with a DC to draw amplitude of a channel of an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=-1,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="waveform"):
        """Initialize a new sppasWaveformWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param name:      Window name.

        """
        super(sppasWaveformWindow, self).__init__(
            parent, id, None, pos, size, style, name)

        self.SetSelectable(False)
        self.SetFocusWidth(0)

        self._auto_scroll = False
        self._data_max = 0
        self._data_min = 0
        self._sampwidth = 0

        self._pen_width = 1
        self._draw_style = "lines"

        # The list of frames
        self._frames = list()

    # -----------------------------------------------------------------------
    # How the waveform will look...
    # -----------------------------------------------------------------------

    def SetLineStyle(self, style="lines"):
        """Set the draw style: lines or bars."""
        if style not in ("lines", "bars"):
            style = "lines"
        self._draw_style = style

    # -----------------------------------------------------------------------

    def SetPenWidth(self, value):
        value = int(value)
        if value < 1:
            value = 1
        if value > 20:
            value = 20
        self._pen_width = value

    # -----------------------------------------------------------------------

    def SetAutoScroll(self, value):
        value = bool(value)
        if value != self._auto_scroll:
            self._auto_scroll = value
            self.__reset_minmax()

    # -----------------------------------------------------------------------
    # Samples to draw
    # -----------------------------------------------------------------------

    def SetData(self, frames, sampwidth, nchannels):
        """Override. Set new data content.

        :param data: (list of samples, samples width)

        """
        #
        if frames is None:
            self._data = None
            self._data_max = 0
            self._data_min = 0
            self._sampwidth = 0
            self.Refresh()
        else:
            # Convert frames into samples (TEMPORARY SOLUTION)
            data = sppasAudioConverter().unpack_data(frames, sampwidth, nchannels)
            # get only samples of the 1st channel
            data = data[0]

            if data != self._data or self._sampwidth != self._sampwidth:
                self._data = data
                self._sampwidth = sampwidth
                self.__reset_minmax()

    # -----------------------------------------------------------------------

    def __reset_minmax(self):
        self._data_max = sppasAudioFrames().get_maxval(self._sampwidth)
        self._data_min = -self._data_max
        if self._auto_scroll is True:
            # autoscroll is limited to at least 10%
            self._data_max = int(max(float(max(self._data)) * 1.1, float(self._data_max) * 0.1))
            self._data_min = int(min(float(min(self._data)) * 1.1, float(self._data_min) * 0.1))

        self.Refresh()

    # -----------------------------------------------------------------------
    # Draw
    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Draw the amplitude values as a waveform."""
        x, y, w, h = self.GetContentRect()

        # Draw horizontal lines and amplitude values
        self.__DrawContentAxes(dc, gc, x, y, w, h)

        if self._data is None:
            return

        if len(self._data) > (w*2):
            if self._draw_style == "bars":
                self.__DrawContentAsBars(dc, gc, x, y, w, h)
            else:
                self.__DrawContentAsJointLines(dc, gc, x, y, w, h)
        else:
            # More pixels than values to draw...
            self.__DrawContentSmallData(dc, gc, x, y, w, h)

    # -----------------------------------------------------------------------

    def __DrawContentAxes(self, dc, gc, x, y, w, h):
        """Draw an horizontal line at the middle (indicate 0 value). """
        p = h // 100
        y_center = y + (h // 2)
        pen = wx.Pen(wx.Colour(128, 128, 212, 128), p, wx.PENSTYLE_SOLID)
        pen.SetCap(wx.CAP_BUTT)
        dc.SetPen(pen)

        # Line at the centre
        th, tw = self.get_text_extend(dc, gc, "-0.0")
        dc.DrawLine(x, y_center, x + w, y_center)
        self.DrawLabel("0", dc, gc, x, y_center - (th // 3))

        if self._auto_scroll is False:
            # Lines at top and bottom
            dc.DrawLine(x, y + (p//2), x + w, y + (p//2))
            dc.DrawLine(x, h - (p//2), x + w, h - (p//2))

            # Scale at top and bottom
            self.DrawLabel("1", dc, gc, x, y)
            self.DrawLabel("-1", dc, gc, x, h - (th//2))

            if h > 200:
                pen = wx.Pen(wx.Colour(128, 128, 212, 196), 1, wx.PENSTYLE_DOT)
                pen.SetCap(wx.CAP_BUTT)
                dc.SetPen(pen)
                dc.DrawLine(x, h//4, x + w, h//4)
                dc.DrawLine(x, y_center + h//4, x + w, y_center + h//4)

        else:
            if self._data is not None:
                pen = wx.Pen(wx.Colour(128, 128, 212, 196), 2, wx.PENSTYLE_DOT)
                pen.SetCap(wx.CAP_BUTT)
                dc.SetPen(pen)
                # the height we should use to draw the whole scale
                audio_data_max = sppasAudioFrames().get_maxval(self._sampwidth)
                viewed_ratio = float(max(self._data)) / float(audio_data_max)
                viewed_ratio = round(viewed_ratio, 1)
                value = viewed_ratio * float(audio_data_max)

                # Lines at top and bottom
                ypixels = int(value * (float(h) / 2.0) / float(self._data_max))
                dc.DrawLine(x, y_center - ypixels, x + w, y_center - ypixels)
                self.DrawLabel(str(viewed_ratio), dc, gc, x, y_center - ypixels - (th // 3))

                dc.DrawLine(x, y_center + ypixels, x + w, y_center + ypixels)
                self.DrawLabel(str(-viewed_ratio), dc, gc, x, y_center + ypixels - (th // 3))

    # -----------------------------------------------------------------------

    def __DrawContentAsJointLines(self, dc, gc, x, y, w, h):
        """Draw the waveform as joint lines.

        Current min/max observed values are joint to the next ones by a
        line. It looks like an analogic signal more than a discrete one.

        """
        y_center = y + (h // 2)
        ypixelsminprec = y_center
        xstep = self._pen_width
        x += (xstep // 2)
        xcur = x

        # Fix the pen style and color
        pen = wx.Pen(self.GetPenForegroundColour(), self._pen_width, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)

        while xcur < (x + w):

            # Get value of n samples between xcur and xnext
            dcur = (xcur - x) * len(self._data) // w
            dnext = (xcur + xstep - x) * len(self._data) // w
            data = self._data[dcur:dnext]

            # Get min and max (take care if saturation...)
            datamin = max(min(data), self._data_min + 1)
            datamax = min(max(data), self._data_max - 1)

            # Convert the data into a "number of pixels" -- height
            ypixelsmax = int(float(datamax) * (float(h) / 2.0) / float(self._data_max))
            if self._data_min != 0:
                ypixelsmin = int(float(datamin) * (float(h) / 2.0) / float(abs(self._data_min)))
            else:
                ypixelsmin = 0

            # draw a line between prec. value to current value
            if xcur != x:
                dc.DrawLine(xcur, y_center - ypixelsminprec, xcur, y_center - ypixelsmax)
                dc.DrawLine(xcur + xstep, y_center - ypixelsmin, xcur + xstep, y_center - ypixelsmax)

            ypixelsminprec = ypixelsmin

            # Set values for next step
            xcur += xstep

    # -----------------------------------------------------------------------

    def __DrawContentAsBars(self, dc, gc, x, y, w, h):
        """Draw the waveform as vertical bars.

        Current min/max observed values are drawn by a vertical line.

        """
        y_center = y + (h // 2)
        xstep = self._pen_width + (self._pen_width // 3)
        x += (xstep // 2)
        xcur = x

        # Fix the pen style and color
        pen = wx.Pen(self.GetPenForegroundColour(), self._pen_width, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)

        while xcur < (x + w):

            # Get value of n samples between xcur and xnext
            dcur = (xcur - x) * len(self._data) // w
            dnext = (xcur + xstep - x) * len(self._data) // w
            data = self._data[dcur:dnext]

            # Get min and max (take care if saturation...)
            datamin = max(min(data), self._data_min + 1)
            datamax = min(max(data), self._data_max - 1)

            # Convert the data into a "number of pixels" -- height
            ypixelsmax = int(float(datamax) * (float(h) / 2.0) / float(self._data_max))
            if self._data_min != 0:
                ypixelsmin = int(float(datamin) * (float(h) / 2.0) / float(abs(self._data_min)))
            else:
                ypixelsmin = 0

            # draw a vertical line
            if xcur != x:
                dc.DrawLine(xcur, y_center - ypixelsmax, xcur, y_center - ypixelsmin)

            # Set values for next step
            xcur += xstep

    # -----------------------------------------------------------------------

    def __DrawContentSmallData(self, dc, gc, x, y, w, h):
        """Draw the data with vertical lines.

        Apply only if there are less data values than pixels to draw them.

        """
        y_center = y + (h // 2)
        xstep = round(float(w * 1.5) / float(len(self._data)))
        x += (xstep // 2)
        xcur = x
        while (xcur + xstep) < (x + w):

            # Get value of n samples between xcur and xnext
            dcur = (xcur - x) * len(self._data) // w
            dnext = (xcur + xstep - x) * len(self._data) // w
            data = self._data[dcur:dnext]

            for value in data:
                pen = wx.Pen(self.GetPenForegroundColour(), 1, wx.PENSTYLE_SOLID)
                dc.SetPen(pen)
                if value > 0:
                    # convert the data into a "number of pixels" -- height
                    y_pixels = int(float(value) * (float(h) / 2.0) / float(self._data_max))
                else:
                    y_pixels = int(float(value) * (float(h) / 2.0) / float(abs(self._data_min)))

                if xstep > 1:
                    point_size = xstep
                    dc.DrawLine(xcur, y_center, xcur, y_center - y_pixels)
                else:
                    point_size = 3

                pen = wx.Pen(self.GetPenForegroundColour(), point_size, wx.PENSTYLE_SOLID)
                dc.SetPen(pen)
                dc.DrawPoint(xcur, y_center - y_pixels)

            xcur += xstep

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
        w0 = self.__draw_waveform(0., 100.)
        w0.SetBorderWidth(0)
        w1 = self.__draw_waveform(2., 3.)
        w1.SetPenWidth(9)
        w1.SetLineStyle("bars")
        w1.SetAutoScroll(True)
        w2 = self.__draw_waveform(2.56, 2.60)
        sizer.Add(w0, 1, wx.EXPAND)
        sizer.Add(w1, 1, wx.EXPAND)
        sizer.Add(w2, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def __draw_waveform(self, start_time, end_time):
        nframes = int((end_time - start_time) * self._audio.get_framerate())
        self._audio.seek(int(start_time * float(self._audio.get_framerate())))
        # read samples of all channels. Channel 0 is data[0]
        data = self._audio.read_frames(nframes)
        w = sppasWaveformWindow(self)
        w.SetData(data, self._audio.get_sampwidth(), self._audio.get_nchannels())
        return w

