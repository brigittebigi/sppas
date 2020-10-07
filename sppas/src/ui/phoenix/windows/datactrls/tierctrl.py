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

    src.ui.phoenix.windows.datactrls.tierctrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import logging
import wx
from math import ceil, floor

from sppas.src.config import paths
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasAnnotation

from ..panels import sppasPanel
from .basedatactrl import sppasDataWindow
from .annctrl import sppasAnnotationWindow

# ---------------------------------------------------------------------------


class sppasTierWindow(sppasDataWindow):
    """A window with a DC to draw a sppasTier().

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
        """Initialize a new sppasTierWindow instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param data:   Data to draw.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param name:   Window name.

        """
        style = wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE
        super(sppasTierWindow, self).__init__(
            parent, id, data, pos, size, style, name)

        self._data = None
        if data is not None:
            self.SetData(data)
        self.__ann_idx = -1
        self.__period = (0, 0)
        self._pxsec = 0   # the number of pixels to represent 1 second of time
        self.__annctrls = dict()

        # Override parent members
        self._is_selectable = True
        self._min_width = 256
        self._min_height = 4
        self._vert_border_width = 0
        self._horiz_border_width = 1
        self._focus_width = 0

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        return self.__ann_idx

    # -----------------------------------------------------------------------

    def GetDrawPeriod(self):
        """Return (begin, end) time values of the period to draw."""
        return self.__period[0], self.__period[1]

    # -----------------------------------------------------------------------

    def SetDrawPeriod(self, begin, end):
        """Set the period to draw."""
        if begin != self.__period[0] or end != self.__period[1]:
            self.__period = (begin, end)
            self.Refresh()

    # -----------------------------------------------------------------------

    def get_selected_localization(self):
        """Return begin and end time value (float)."""
        if self.__ann_idx == -1:
            return 0, 0
        ann = self._data[self.__ann_idx]

        start_point = ann.get_lowest_localization()
        start = start_point.get_midpoint()
        r = start_point.get_radius()
        if r is not None:
            start -= r
        start = float(floor(start*100.)) / 100.

        end_point = ann.get_highest_localization()
        end = end_point.get_midpoint()
        r = end_point.get_radius()
        if r is not None:
            end += r
        end = float(ceil(end*100.)) / 100.

        return start, end

    # -----------------------------------------------------------------------

    def set_selected_ann(self, idx):
        logging.debug("an annotation is selected : {}".format(idx))
        self.__ann_idx = idx
        self.Refresh()

    # -----------------------------------------------------------------------

    def update_ann(self, idx):
        logging.debug("an annotation was modified : {}".format(idx))
        self.Refresh()

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        logging.debug("an annotation was deleted : {}".format(idx))
        self.Refresh()

    # -----------------------------------------------------------------------

    def create_ann(self, idx):
        logging.debug("an annotation was created : {}".format(idx))
        self.Refresh()

    # -----------------------------------------------------------------------

    def get_tiername(self):
        return self._data.get_name()

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        x, y, w, h = self.GetContentRect()
        duration = float(self.__period[1]) - float(self.__period[0])

        if duration > 0.01 and self._data.is_interval() is True:
            self._pxsec = int(float(w) / duration)
            anns = self._data.find(self.__period[0], self.__period[1], overlaps=True)
            for ann in self.__annctrls:
                if ann not in anns:
                    self.__annctrls[ann].Hide()
            for ann in anns:
                self._DrawAnnotation(ann, x, y, w, h)
        else:
            tier_name = self._data.get_name()
            tw, th = self.get_text_extend(dc, gc, tier_name)
            self.draw_label(dc, gc, tier_name, x, y + ((h - th) // 2))
            self.draw_label(dc, gc, str(len(self._data))+" annotations", x + 200, y + ((h - th) // 2))
            if self.__ann_idx > -1:
                self.draw_label(dc, gc, "(-- {:d} -- is selected)".format(self.__ann_idx+1),
                                x + 400, y + ((h - th) // 2))

    # -----------------------------------------------------------------------

    def _DrawAnnotation(self, ann, x, y, w, h):
        """Draw an annotation.

        x          x_a                x+w
        |----------|-------|-----------|
        p0        b_a     b_e         p1

        d = p1 - p0
        d_a = annotation duration that will be displayed
        w_a = d_a * pxsec
        x_a ?
        delay = b_a - p0  # delay between time of x and time of begin ann

        """
        draw_points = [True, True]
        # estimate the displayed duration of the annotation
        b_a = self.get_ann_begin(ann)
        e_a = self.get_ann_end(ann)
        if b_a < self.__period[0]:
            b_a = self.__period[0]
            draw_points[0] = False
        if e_a > self.__period[1]:
            e_a = self.__period[1]
            draw_points[1] = False
        d_a = e_a - b_a
        # annotation width
        w_a = d_a * self._pxsec
        # annotation x-axis
        if self.__period[0] == b_a:
            x_a = x
        else:
            delay = b_a - self.__period[0]
            d = float(self.__period[1]) - float(self.__period[0])
            x_a = x + int((float(w) * delay) / d)
        pos = wx.Point(x_a, y)
        size = wx.Size(int(w_a), h)
        if ann in self.__annctrls:
            annctrl = self.__annctrls[ann]
            annctrl.SetPxSec(self._pxsec)
            annctrl.SetPosition(pos)
            annctrl.SetSize(size)
            annctrl.ShouldDrawPoints(draw_points)
            annctrl.Show()
        else:
            annctrl = sppasAnnotationWindow(self, pos=pos, size=size, data=ann)
            annctrl.SetPxSec(self._pxsec)
            annctrl.ShouldDrawPoints(draw_points)
            annctrl.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_ann_selected)
            self.__annctrls[ann] = annctrl

    # -----------------------------------------------------------------------

    @staticmethod
    def get_ann_begin(ann):
        ann_begin = ann.get_lowest_localization()
        value = ann_begin.get_midpoint()
        r = ann_begin.get_radius()
        if r is not None:
            value -= r
        return value

    @staticmethod
    def get_ann_end(ann):
        ann_end = ann.get_highest_localization()
        value = ann_end.get_midpoint()
        r = ann_end.get_radius()
        if r is not None:
            value += r
        return value

    # -----------------------------------------------------------------------

    def _tooltip(self):
        """Set a tooltip string indicating data content."""
        if self._data is not None:
            msg = self._data.get_name() + ": "
            msg += str(len(self._data))+" annotations"
            return msg

        return "No data"
    # -----------------------------------------------------------------------

    def _process_ann_selected(self, event):
        logging.debug("Tier {} received annotation selected event."
                      "".format(self._data.get_name()))
        self.Notify()

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test TierCtrl")

        filename = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        parser = sppasRW(filename)
        trs = parser.read()

        self.p1 = sppasTierWindow(self, pos=(10, 10), size=(300, 24), data=trs[0])
        self.p1.SetDrawPeriod(2.49, 3.49)
        self.p2 = sppasTierWindow(self, pos=(10, 100), size=(300, 48), data=trs[1])
        self.p2.SetDrawPeriod(2.49, 3.49)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.p1, 0, wx.EXPAND)
        s.Add(self.p2, 0, wx.EXPAND)
        self.SetSizer(s)
        self.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_tier_selected)

    # -----------------------------------------------------------------------

    def _process_tier_selected(self, event):
        tier = event.GetObj()
        value = event.GetSelected()
        obj = event.GetEventObject()

        print("Selected event received. Tier {} is selected {}"
              "".format(tier.get_name(), value))
        if obj.IsSelected() is False:
            obj.SetSelected(True)
            obj.SetForegroundColour(wx.RED)
        else:
            obj.SetSelected(False)
            obj.SetForegroundColour(self.GetForegroundColour())

