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

    src.ui.phoenix.windows.datactrls.annctrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata.aio.aioutils import serialize_labels

from .basedatactrl import sppasBaseDataWindow
from .pointctrl import sppasPointWindow

# ---------------------------------------------------------------------------


class sppasAnnotationWindow(sppasBaseDataWindow):
    """A window with a DC to draw a sppasAnnotation().

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=-1,
                 data=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name="annctrl"):
        """Initialize a new sppasAnnotationWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param data:   Data to draw.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param name:   Window name.

        The size is representing the available area to draw the annotation.
        The member _pxsec must be fixed for the annotation to draw inside this
        area. It represents the number of pixels required for 1 second.

        """
        style = wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE
        super(sppasAnnotationWindow, self).__init__(
            parent, id, data, pos, size, style, name)

        self._data = None
        if data is not None:
            self.SetData(data)

        # Override parent members
        self._is_selectable = False
        self._min_width = 1
        self._min_height = 4
        self._vert_border_width = 0
        self._horiz_border_width = 0
        self._focus_width = 1

        # Added members
        self._pxsec = 0  # the number of pixels to represent 1 second of time
        self._pointctrl1 = None
        self._pointctrl2 = None
        self.__should_draw_points = [True, True]

        self.SetInitialSize(size)

        try:
            settings = wx.GetApp().settings
            self._bgcolor = settings.bg_color
        except AttributeError:
            self.InheritAttributes()
            self._bgcolor = self.GetTopLevelParent().GetBackgroundColour()

    # ------------------------------------------------------------------------

    def SetPxSec(self, value):
        """Fix the number of pixels to draw 1 second of time.

        :param value: (int)

        """
        value = int(value)
        assert value > 0
        self._pxsec = value

    # -----------------------------------------------------------------------

    def SetVertBorderWidth(self, value):
        """Set the width of the left/right borders.

        :param value: (int) Border size. Not applied if not appropriate.

        """
        return

    # -----------------------------------------------------------------------

    def DrawBackground(self, dc, gc):
        """Draw the background with a color or transparent."""
        w, h = self.GetClientSize()
        if self._data is None:
            return

        brush = self.GetBackgroundBrush()
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()
        dc.SetBrush(brush)
        dc.SetPen(wx.TRANSPARENT_PEN)

        if self._data.is_labelled() is False:
            # Draw a transparent rectangle...
            dc.DrawRectangle(0, 0, w, h)
        else:
            if self._bgcolor is not None:
                # Fill in the content
                c2 = self.GetHighlightedBackgroundColour()
                c1 = self._bgcolor
                mid = h // 2
                box_rect = wx.Rect(0, 0, w, mid)
                dc.GradientFillLinear(box_rect, c1, c2, wx.NORTH)
                box_rect = wx.Rect(0, mid, w, h)
                dc.GradientFillLinear(box_rect, c1, c2, wx.SOUTH)

        dc.SetBrush(self.GetTransparentBrush())
        gc.SetBrush(self.GetTransparentBrush())

    # -----------------------------------------------------------------------

    def ShouldDrawPoints(self, values):
        """Should we draw the begin/end points?"""
        self.__should_draw_points = values

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Override. """
        if self._data is None:
            return
        self._DrawEmptyContent(dc, gc)
        if self._pxsec > 0:
            if self._data.location_is_point():
                self._DrawPoint(dc, gc)
            else:
                self._DrawInterval(dc, gc)

    # -----------------------------------------------------------------------

    def _DrawInterval(self, dc, gc):
        """The annotation is an interval."""
        x, y, w, h = self.GetContentRect()
        if w < 3:
            self.set_pointctrl1(x, y, 1, h)
            if w == 2:
                self.set_pointctrl2(x + 1, y, 1, h)
            return

        wpt1 = wpt2 = 0
        # Draw locations
        if self.__should_draw_points[0] is True:
            pt1 = self._data.get_lowest_localization()
            wpt1 = max(1, self._calc_width(pt1.duration().get_value() + pt1.duration().get_margin()))
            self.set_pointctrl1(x, y, wpt1, h)
        if self.__should_draw_points[1] is True:
            pt2 = self._data.get_highest_localization()
            wpt2 = max(1, self._calc_width(pt2.duration().get_value() + pt2.duration().get_margin()))
            self.set_pointctrl2(x + w - wpt2, y, wpt2, h)

        # adjust remaining width: remove the points widths and a margin
        x = x + wpt1 + 2
        w = w - wpt1 - wpt2 - 4

        # Draw label
        fw, fh = self.get_text_extend(dc, gc, "/")
        if w > fw:
            y = y + ((h - fh) // 2)
            self._DrawAnnotationLabels(dc, gc, x, y, w, h)

    # -----------------------------------------------------------------------

    def set_pointctrl1(self, x, y, w, h):
        if self._pointctrl1 is None:
            self._pointctrl1 = sppasPointWindow(
                self,
                data=self._data.get_lowest_localization(),
                pos=(x, y),
                size=wx.Size(w, h),
                name="pointctrl1"
            )
        else:
            self._pointctrl1.SetPosition(wx.Point(x, y))
            self._pointctrl1.SetSize(wx.Size(w, h))

    # -----------------------------------------------------------------------

    def set_pointctrl2(self, x, y, w, h):
        if self._pointctrl2 is None:
            self._pointctrl2 = sppasPointWindow(
                self,
                data=self._data.get_highest_localization(),
                pos=(x, y),
                size=wx.Size(w, h),
                name="pointctrl2"
            )
        else:
            self._pointctrl2.SetPosition(wx.Point(x, y))
            self._pointctrl2.SetSize(wx.Size(w, h))

    # -----------------------------------------------------------------------

    def _DrawAnnotationLabels(self, dc, gc, x, y, w, h):
        fw, fh = self.get_text_extend(dc, gc, "/")

        # Draw label
        if w > fw:
            label = serialize_labels(self._data.get_labels(),
                                     separator=" ")
            tw, th = self.get_text_extend(dc, gc, label)
            if th > h:
                label = "..."
            while tw > w:
                # a character is added to indicate that the label is truncated
                label = label[:len(label)-2]
                label += "."
                tw, th = self.get_text_extend(dc, gc, label)
                if tw < fw:
                    label = ""
                    break
            if len(label) > 0:
                self.draw_label(dc, gc, label, x + ((w - tw) // 2), y)

    # -----------------------------------------------------------------------

    def _DrawEmptyContent(self, dc, gc):
        x, y, w, h = self.GetContentRect()
        pen = wx.Pen(self.GetHighlightedBackgroundColour(), 1, wx.SOLID)
        pen.SetCap(wx.CAP_BUTT)
        dc.SetPen(pen)
        dc.DrawRectangle(x, y, w, h)

    # -----------------------------------------------------------------------

    def _DrawPoint(self, dc, gc):
        """The annotation is a point."""
        x, y, w, h = self.GetContentRect()
        if w < 3:
            self.set_pointctrl1(x, y, 1, h)
            return
        pt1 = self._data.get_lowest_localization()
        wpt1 = max(1, self._calc_width(pt1.duration().get_value() + pt1.duration().get_margin()))
        self.set_pointctrl1(x + (w // 2), y, wpt1, h//2)

        # Draw label
        fw, fh = self.get_text_extend(dc, gc, "/")
        if w > fw:
            mid = y + (h // 2)
            y = mid + ((mid - fh) // 2)
            self._DrawAnnotationLabels(dc, gc, x, y, w, h)

    # ------------------------------------------------------------------------

    def _calc_width(self, duration):
        """Return a width from a given duration."""
        return int(duration * float(self._pxsec))

    def _calc_time(self, width):
        """Return a duration from a given width."""
        return float(width) / float(self._pxsec)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test AnnotationCtrl")

        a1 = sppasAnnotation(
            sppasLocation(sppasInterval(sppasPoint(2.5, 0.04), sppasPoint(4.5))),
            [sppasLabel(sppasTag("je")),
             sppasLabel([sppasTag("fais"), sppasTag("sais")]),
             sppasLabel(sppasTag("un")),
             sppasLabel(sppasTag("essai"))]
        )

        a2 = sppasAnnotation(
            sppasLocation(sppasPoint(4)),
            sppasLabel(sppasTag(2, "int"))
        )

        # the width is matching with the duration of the annotation
        p11 = sppasAnnotationWindow(
            self, pos=(50, 50), size=(200, 100), data=a1)
        # pxsec = width / a1.duration
        p11.SetPxSec(100)
        p11.SetForegroundColour(wx.RED)
        p11.Refresh()

        p12 = sppasAnnotationWindow(
            self, pos=(300, 50), size=(20, 100), data=a1)
        p12.SetPxSec(10)
        p12.Refresh()

        # The point is drawn at the middle of the given position/width
        p21 = sppasAnnotationWindow(
            self, pos=(50, 200), size=(200, 100), data=a2)
        p21.SetPxSec(100)
        p21.Refresh()
        p22 = sppasAnnotationWindow(
            self, pos=(300, 200), size=(5, 100), data=a2)
        p22.SetPxSec(10)
        p22.Refresh()
