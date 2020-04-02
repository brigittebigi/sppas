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

from sppas import paths
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasAnnotation

from .basedatactrl import sppasWindowSelectedEvent
from .basedatactrl import sppasBaseDataWindow
from .annctrl import sppasAnnotationWindow

# ---------------------------------------------------------------------------


class sppasTierWindow(sppasBaseDataWindow):
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

    def set_selected_period(self, begin, end):
        """Set the period to draw."""
        self.__period = (begin, end)

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
        end_point = ann.get_highest_localization()
        end = end_point.get_midpoint()
        r = end_point.get_radius()
        if r is not None:
            end += r

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

        if duration > 0.01:
            self._pxsec = int(float(w) / duration)
            anns = self._data.find(self.__period[0], self.__period[1], overlaps=True)
            for ann in anns:
                self._DrawAnnotation(ann, x, y, w, h)
        else:
            tier_name = self._data.get_name()
            tw, th = self.get_text_extend(dc, gc, tier_name)
            self.draw_label(dc, gc, tier_name, x, y + ((h - th) // 2))
            self.draw_label(dc, gc, str(len(self._data))+" annotations", x + 200, y + ((h - th) // 2))
            if self.__ann_idx > -1:
                self.draw_label(dc, gc, x + 400, y + ((h - th) // 2),
                                "(-- {:d} -- is selected)".format(self.__ann_idx+1))

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
        # estimate the displayed duration of the annotation
        ann_begin = ann.get_lowest_localization()
        ann_end = ann.get_highest_localization()
        b_a = ann_begin.get_midpoint() - ann_begin.get_radius()
        e_a = ann_end.get_midpoint() + ann_end.get_radius()
        if b_a < self.__period[0]:
            b_a = self.__period[0]
        if e_a > self.__period[1]:
            e_a = self.__period[1]
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
        else:
            annctrl = sppasAnnotationWindow(self, pos=pos, size=size, data=ann)
            annctrl.SetPxSec(self._pxsec)
            self.__annctrls[ann] = annctrl

    # -----------------------------------------------------------------------

    def _tooltip(self):
        """Set a tooltip string indicating data content."""
        if self._data is not None:
            msg = self._data.get_name() + ": "
            msg += str(len(self._data))+" annotations"
            return msg

        return "No data"

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test TierCtrl")

        filename = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        parser = sppasRW(filename)
        trs = parser.read()

        self.p1 = sppasTierWindow(self, pos=(10, 10), size=(300, 24), data=trs[0])
        self.p1.set_selected_period(3.0, 3.5)
        self.p2 = sppasTierWindow(self, pos=(10, 100), size=(300, 48), data=trs[1])
        self.p2.set_selected_period(3.0, 3.5)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.p1, 0, wx.EXPAND)
        s.Add(self.p2, 0, wx.EXPAND)
        self.SetSizer(s)
        self.p1.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_tier_selected)
        self.p2.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_tier_selected)

    # -----------------------------------------------------------------------

    def _process_tier_selected(self, event):
        data = event.GetObj()
        value = event.GetSelected()
        obj = event.GetEventObject()

        if isinstance(data, sppasAnnotation):
            tier = data.get_parent()
            print("Selected event received. Annotation of tier {} is selected {}"
                  "".format(tier.get_name(), value))

            if self.p1.get_tiername() == tier.get_name():
                if self.p1.IsSelected() is False:
                    self.p1.SetSelected(True)
                    self.p1.SetForegroundColour(wx.RED)
                else:
                    self.p1.SetSelected(False)
                    self.p1.SetForegroundColour(self.GetForegroundColour())

            if self.p2.get_tiername() == tier.get_name():
                if self.p2.IsSelected() is False:
                    self.p2.SetSelected(True)
                    self.p2.SetForegroundColour(wx.RED)
                else:
                    self.p2.SetSelected(False)
                    self.p2.SetForegroundColour(self.GetForegroundColour())

        if isinstance(data, sppasTier):
            print("Selected event received. Tier {} is selected {}"
                  "".format(data.get_name(), value))
            if obj.IsSelected() is False:
                obj.SetSelected(True)
                obj.SetForegroundColour(wx.RED)
            else:
                obj.SetSelected(False)
                obj.SetForegroundColour(self.GetForegroundColour())

        event.Skip()

