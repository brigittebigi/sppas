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

    ui.phoenix.page_editor.media.tickslider.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import math

from sppas.src.ui.phoenix.windows.slider import sppasSlider

# ----------------------------------------------------------------------------


class RulerLabel:
    """Label holds information about a particular tick in sppasTicksSlider.

    """

    def __init__(self, pos=-1, lx=-1, ly=-1, text=""):
        self.pos = pos
        self.lx = lx
        self.ly = ly
        self.text = text

# ----------------------------------------------------------------------------


class sppasTicksSlider(sppasSlider):

    def __init__(self, *args, **kwargs):
        """Create a self-drawn window to display a value into a range.

        """
        super(sppasTicksSlider, self).__init__(*args, **kwargs)
        self.SetMinSize(wx.Size(-1, 24))
        self.SetBorderWidth(0)

        self._digits = 0
        self._minor = 0
        self._major = 0
        self._max_width = 0
        self._max_height = 0
        self._bits = list()
        self._middlepos = list()

        # Text indicating values
        self._major_labels = list()
        self._minor_labels = list()

    # -----------------------------------------------------------------------

    def invalidate_ticks(self):
        self._digits = 0
        self._minor = 0
        self._major = 0
        self._max_width = 0
        self._max_height = 0
        self._bits = list()
        self._middlepos = list()

        # Text indicating values
        self._major_labels = list()
        self._minor_labels = list()

    # -----------------------------------------------------------------------

    def formats_label(self, value):
        return "{:.3f}".format(value)

    # -----------------------------------------------------------------------

    def GetMajorFont(self):
        font = self.GetFont()
        f = wx.Font(int(float(font.GetPointSize()) * 0.8),
                    wx.FONTFAMILY_SWISS,  # family,
                    wx.FONTSTYLE_NORMAL,  # style,
                    wx.FONTWEIGHT_NORMAL,  # weight,
                    underline=False,
                    faceName=font.GetFaceName(),
                    encoding=wx.FONTENCODING_SYSTEM)
        return f

    # -----------------------------------------------------------------------

    def GetMinorFont(self):
        font = self.GetFont()
        f = wx.Font(int(float(font.GetPointSize()) * 0.5),
                    wx.FONTFAMILY_SWISS,   # family,
                    wx.FONTSTYLE_NORMAL,   # style,
                    wx.FONTWEIGHT_NORMAL,  # weight,
                    underline=False,
                    faceName=font.GetFaceName(),
                    encoding=wx.FONTENCODING_SYSTEM)
        return f

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Override."""
        x, y, w, h = self.GetContentRect()
        tick_height = max(8, h // 2)

        # update all the ticks calculation & draw them
        self._UpdateTicks(dc)

        dc.SetTextForeground(self.GetForegroundColour())
        dc.SetPen(wx.Pen(self.GetForegroundColour(), 2, wx.SOLID))

        # Line at top
        dc.DrawLine(x, y, x + w, y)

        # Draw major ticks
        dc.SetFont(self.GetMajorFont())
        for label in self._major_labels:
            pos = label.pos
            dc.DrawLine(x + pos, y, x + pos, y + tick_height)
            if label.text != "":
                dc.DrawText(label.text, label.lx, label.ly)

        # Draw minor ticks
        dc.SetFont(self.GetMinorFont())
        dc.SetPen(wx.Pen(self.GetForegroundColour(), 1, wx.SOLID))
        for label in self._minor_labels:
            pos = label.pos
            dc.DrawLine(x + pos, y, x + pos, y + (tick_height // 2))
            if label.text != "":
                dc.DrawText(label.text, label.lx, label.ly)

        # draw the current position
        self._DrawMoment(dc, gc)

    # -----------------------------------------------------------------------

    def _Tick(self, dc, pos, d, major):
        """Tick a particular position."""
        x, y, w, h = self.GetContentRect()
        tick_height = max(8, h // 2)

        label = RulerLabel()
        label.pos = pos
        label.lx = -1  # don't display
        label.ly = -1  # don't display
        label.text = ""
        if major:
            self._major_labels.append(label)
        else:
            self._minor_labels.append(label)

        if major:
            dc.SetFont(self.GetMajorFont())
        else:
            # a font with a smaller size
            dc.SetFont(self.GetMinorFont())

        l = self.LabelString(d)
        strw, strh = dc.GetTextExtent(l)

        strlen = strw
        strpos = pos - strw // 2
        if strpos < 0:
            strpos = 0
        if strpos + strw >= w:
            strpos = w - strw
        strleft = x + strpos
        strtop = y + tick_height
        self._max_height = max(self._max_height, h - tick_height)

        # See if any of the pixels we need to draw this label is already covered

        for ii in range(strlen):
            if self._bits[strpos+ii]:
                return

        # If not, position the label and give it text
        label.lx = strleft
        label.ly = strtop
        label.text = l
        if major:
            self._major_labels[-1] = label
        else:
            self._minor_labels[-1] = label

        # And mark these pixels, plus some surrounding
        # ones (the spacing between labels), as covered

        leftmargin = tick_height // 2
        if strpos < leftmargin:
            leftmargin = strpos

        strpos = strpos - leftmargin
        strlen = strlen + leftmargin
        rightmargin = tick_height // 2

        if strpos + strlen > w - 2:
            rightmargin = w - strpos - strlen
        strlen = strlen + rightmargin

        for ii in range(strlen):
            if strpos+ii < len(self._bits):
                self._bits[strpos+ii] = 1

    # -----------------------------------------------------------------------

    def _UpdateTicks(self, dc):
        """Updates all the ticks calculations."""
        self.invalidate_ticks()

        # This gets called when something has been changed
        # (i.e. we've been invalidated). Recompute all tick positions.
        x, y, w, h = self.GetContentRect()

        self._max_width = w
        self._max_height = 0

        self._bits = [0] * (w + 1)
        self._middlepos = list()

        UPP = (self._end - self._start) / float(w)  # Units per pixel
        self.FindLinearTickSizes(UPP)
        sg = ((UPP > 0.0) and [1.0] or [-1.0])[0]

        # Major ticks
        d = self._start - UPP / 2.
        majorint = int(math.floor(sg * d / self._major))
        ii = -1

        while ii <= w:
            ii = ii + 1
            d = d + UPP
            if int(math.floor(sg * d / self._major)) > majorint:
                majorint = int(math.floor(sg * d / self._major))
                self._Tick(dc, ii, sg * majorint * self._major, major=True)

        # Minor ticks
        d = self._start - UPP / 2.
        minorint = int(math.floor(sg*d/self._minor))
        ii = -1

        while ii <= w:
            ii = ii + 1
            d = d + UPP
            if int(math.floor(sg*d/self._minor)) > minorint:
                minorint = int(math.floor(sg*d/self._minor))
                self._Tick(dc, ii, sg * minorint * self._minor, major=False)

    # -----------------------------------------------------------------------

    def FindLinearTickSizes(self, UPP):
        """Used internally.

        Given the dimensions of the slider, the range of values it
        has to display figure out how many units are in one Minor tick,
        and in one Major tick.

        The goal is to always put tick marks on nice round numbers
        that are easy for humans to grok.  This is the most tricky
        with time.

        :param UPP: (float) Unit-per-pixel

        """
        # As a heuristic, we want at least 16 pixels between each minor tick
        units = 16.0*abs(UPP)
        d = 0.000001
        self._digits = 6

        while 1:
            if units < d:
                self._minor = d
                self._major = d * 5.0
                return

            d = d * 5.0
            if units < d:
                self._minor = d
                self._major = d * 2.0
                return

            d = d * 2.0
            self._digits = self._digits - 1

    # -----------------------------------------------------------------------

    def LabelString(self, d):
        """Used internally.

        Given a value, turn it into a string. The number of digits of
        accuracy depends on the resolution of the slider,
        i.e. how far zoomed in or out you are.

        """
        s = ""
        if d < 0.0 and d + self._minor > 0.0:
            d = 0.0

        if self._minor >= 1.0:
            s = "%d" % int(math.floor(d+0.5))
        else:
            s = (("%." + str(self._digits) + "f") % d).strip()

        return s

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Ticks & Labels Slider")
        self.SetMinSize(wx.Size(320, 20))

        p1 = sppasTicksSlider(self)
        p1.set_range(1.234, 6.6789987)
        p1.set_value(4.345)
        p1.SetMinSize(wx.Size(-1, 32))

        p2 = sppasTicksSlider(self)
        p2.set_range(0.0, 0.0)

        p3 = sppasTicksSlider(self)
        p3.set_range(1.234, 3676.6789987)
        p3.set_value(467.345)
        p3.SetMinSize(wx.Size(-1, 32))

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND)
        s.Add(p2, 0, wx.EXPAND)
        s.Add(p3, 0, wx.EXPAND)

        self.SetSizer(s)
