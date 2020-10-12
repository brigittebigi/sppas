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

    ui.phoenix.page_editor.timeslider.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from ..windows import ToggleTextButton
from ..windows import sppasPanel
from ..windows import sppasDCWindow

# ---------------------------------------------------------------------------


MSG_TOTAL_DURATION = "Total duration: "
MSG_VISIBLE_DURATION = "Visible part: "
SECONDS_UNIT = "seconds"

# ----------------------------------------------------------------------------


class sppasSliderPanel(sppasDCWindow):
    """A window imitating a slider but with the same look on all platforms.

     :author:       Brigitte Bigi
     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
     :contact:      contact@sppas.org
     :license:      GPL, v3
     :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Non-interactive: show values but can't be moved with the mouse.

    """

    LABEL_COLOUR = wx.Colour(96, 96, 196, 200)
    POINT_COLOUR = wx.Colour(128, 128, 196, 200)

    # -----------------------------------------------------------------------

    def __init__(self, parent, name="time_slider_panel"):
        """Create a panel to display a value into a range.

        """
        super(sppasSliderPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
            name=name)

        self.__start = 0
        self.__end = 0
        self.__pos = 0
        self._vert_border_width = 2
        self._horiz_border_width = 0

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Override."""
        x, y, w, h = self.GetContentRect()

        # Start label
        label = str(self.__start)
        tw, th = self.get_text_extend(dc, gc, label)
        self.DrawLabel(label, dc, gc, 2, (h - th) // 2)

        # End label
        label = str(self.__end)
        tw, th = self.get_text_extend(dc, gc, label)
        self.DrawLabel(label, dc, gc, w - tw - 2, (h - th) // 2)

        # Current position label
        label = str(self.__pos)
        tw, th = self.get_text_extend(dc, gc, label)
        self.DrawLabel(label, dc, gc, (w - tw) // 2, (h - th) // 2)

# ----------------------------------------------------------------------------


class TimeSliderPanel(sppasPanel):
    """A panel embedding information about time: start, end, selected, etc.

     :author:       Brigitte Bigi
     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
     :contact:      contact@sppas.org
     :license:      GPL, v3
     :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    SELECTION_COLOUR = wx.Colour(160, 60, 60, 128)

    # -----------------------------------------------------------------------

    def __init__(self, parent, name="time_slider_panel"):
        """Create the panel to display time information.

        """
        super(TimeSliderPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
            name=name)

        # Members
        self.__duration = 0.
        self.__start_visible = 0.
        self.__end_visible = 0.
        self.__start_selection = 0.
        self.__end_selection = 0.
        self.__moment = 0.

        # Create the GUI
        self._create_content()
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_toggle_event)

        # Look&feel
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        # Setting the duration will set all the other members
        self.Layout()

    # -----------------------------------------------------------------------
    # Whole duration - i.e. the max value
    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration value (float)"""
        return self.__duration

    def set_duration(self, value=0.):
        """Fix the duration value.

        :param value: (float) Time value in seconds.

        """
        value = float(value)
        if value < 0.:
            raise ValueError

        self.__duration = value
        self._btn_duration.SetLabel("{:s} {:s} {:s}"
                                    "".format(MSG_TOTAL_DURATION, str(value), SECONDS_UNIT))

        # Disable all other values. Enable duration toggle button.
        if value == 0.:
            self._btn_duration.SetValue(True)
            self.set_visible_range(0., 0.)

        # Update the slider
        if self._btn_duration.GetValue() is True:
            # self._slider.set_range(0., self.__duration)
            pass

    duration = property(get_duration, set_duration)

    # -----------------------------------------------------------------------
    # Visible part - must be less than duration
    # -----------------------------------------------------------------------

    def get_visible_start(self):
        """Return start time value of the visible part."""
        return self.__start_visible

    def set_visible_start(self, value=0.):
        """Set start time value of the visible part."""
        value = float(value)
        if value < self.__end_visible:
            raise ValueError
        if value < 0.:
            raise ValueError

        self.__start_visible = value
        dur = self.__end_visible - value
        self._btn_visible.SetLabel("{:s} {:s} {:s}"
                                   "".format(MSG_VISIBLE_DURATION, str(dur), SECONDS_UNIT))

        # Update the slider
        if self._btn_visible.GetValue() is True:
            # self._slider.set_range(self.__start_visible, self.__end_visible)
            pass

    def get_visible_end(self):
        """Return end time value of the visible part."""
        return self.__end_visible

    def set_visible_end(self, value=0.):
        """Set end time value of the visible part."""
        value = float(value)
        if value > self.__start_visible:
            raise ValueError
        if value > self.__duration:
            raise ValueError

        self.__end_visible = value
        dur = value - self.__start_visible
        self._btn_visible.SetLabel("{:s} {:s} {:s}"
                                   "".format(MSG_VISIBLE_DURATION, str(dur), SECONDS_UNIT))

        # Update the slider
        if self._btn_visible.GetValue() is True:
            # self._slider.set_range(self.__start_visible, self.__end_visible)
            pass

    def get_visible_range(self):
        """Return (start, end) time values of the visible part."""
        return self.__start_visible, self.__end_visible

    def set_visible_range(self, start, end):
        """Set the visible time range."""
        start = float(start)
        end = float(end)
        if end > self.__duration:
            raise ValueError
        if end < start:
            raise ValueError
        if start < 0.:
            raise ValueError

        self.__start_visible = start
        self.__end_visible = end
        dur = end - start
        self._btn_visible.SetLabel("{:s} {:s} {:s}"
                                   "".format(MSG_VISIBLE_DURATION, str(dur), SECONDS_UNIT))
        if dur == 0.:
            self._btn_duration.SetValue(True)
            self._btn_visible.SetValue(False)

        # Update the slider
        if self._btn_visible.GetValue() is True:
            # self._slider.set_range(self.__start_visible, self.__end_visible)
            pass

    start_visible = property(get_visible_start, set_visible_start)
    end_visible = property(get_visible_end, set_visible_end)

    # -----------------------------------------------------------------------
    # Set selected part - must be less than duration
    # -----------------------------------------------------------------------

    def get_selection_start(self):
        """Return start time value of the selected part."""
        return self.__start_selection

    def set_selection_start(self, value=0.):
        """Set start time value of the selection part."""
        value = float(value)
        if value < self.__end_selection:
            raise ValueError
        if value < 0.:
            raise ValueError

        self.__start_selection = value
        dur_sel = self.__end_selection - value  # non si chevauchement
        """
        if self.__start_selection > self.__start_visible:
            # The selection started after the visible part
            dur_before = self.__start_selection - self.__start_visible
            self._btn_before.SetLabel("{:s}".format(str(dur_before)))
            self._btn_visible.Show(True)

            dur_visible = self.__end_visible - self.__start_visible

        else:
            self._btn_before.SetLabel("--")
            self._btn_visible.Show(False)
            
        dur_after = self.__end_visible - self.__end_selection

        # Update selection toggle button
        self._btn_selection.SetLabel("{:s}".format(str(dur_sel)))
        self._btn_before.SetLabel("{:s}".format(str(dur_after)))
        """

        # Update the toggles
        if dur_sel == 0.:
            if self._btn_selection is True:
                self._btn_selection.SetValue(False)
                self._btn_visible.SetValue(True)

        # Update the slider
        if self._btn_before.GetValue() is True:
            # self._slider.set_range(self.__start_visible, self.__start_selection)
            pass
        elif self._btn_selection.GetValue() is True:
            # self._slider.set_range(self.__start_selection, self.__end_selection)
            pass
        elif self._btn_after.GetValue() is True:
            # self._slider.set_range(self.__end_selection, self.__end_visible)
            pass

    def get_selection_end(self):
        """Return end time value of the selected part."""
        return self.__end_selection

    def set_selection_end(self, value=0.):
        """Set end time value of the selection part."""
        value = float(value)
        if value > self.__start_selection:
            raise ValueError
        if value > self.__duration:
            raise ValueError

        self.__end_selection = value
        dur = value - self.__start_visible
        if dur == 0.:
            if self._btn_selection is True:
                self._btn_selection.SetValue(False)
                self._btn_selection.SetValue(False)

    def get_selection_range(self):
        """Return (start, end) time values of the selected part."""
        return self.__start_selection, self.__end_selection

    def set_selection_range(self, start, end):
        """Set the selected time range."""
        start = float(start)
        end = float(end)
        if end > self.__duration:
            raise ValueError
        if end < start:
            raise ValueError
        if start < 0.:
            raise ValueError

        self.__start_selection = start
        self.__end_selection = end
        dur = end - start
        if dur == 0.:
            if self._btn_selection is True:
                self._btn_selection.SetValue(False)
                self._btn_selection.SetValue(False)

        # Update the slider

    start_selection = property(get_selection_start, set_selection_start)
    end_selection = property(get_selection_end, set_selection_end)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. """
        wx.Panel.SetFont(self, font)
        for c in self.GetChildren():
            f = wx.Font(int(font.GetPointSize() * 0.75),
                        wx.FONTFAMILY_SWISS,   # family,
                        wx.FONTSTYLE_NORMAL,   # style,
                        wx.FONTWEIGHT_BOLD,    # weight,
                        underline=False,
                        faceName=font.GetFaceName(),
                        encoding=wx.FONTENCODING_SYSTEM)
            c.SetFont(f)

        self.Layout()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override. """
        wx.Panel.SetBackgroundColour(self, colour)
        for child in self.GetChildren():
            child.SetBackgroundColour(colour)
            for c in child.GetChildren():
                print(c.GetName())
                if c.GetName() == "selection_button":
                    c.SetBackgroundColour(wx.Colour(255, 190, 200))
                else:
                    c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        btn_dur = self.__create_toggle_btn(self, "--", "total_button")
        btn_part = self.__create_toggle_btn(self, "--", "visible_part_button")
        btn_part.SetBorderWidth(0)

        panel_sel = sppasPanel(self, name="selection_panel")
        btn_before_sel = self.__create_toggle_btn(panel_sel, "--", "before_sel_button")
        btn_during_sel = self.__create_toggle_btn(panel_sel, "--", "selection_button")
        btn_after_sel = self.__create_toggle_btn(panel_sel, "--", "after_sel_button")
        sizer_sel = wx.BoxSizer(wx.HORIZONTAL)
        sizer_sel.Add(btn_before_sel, 0, wx.ALL, 0)
        sizer_sel.Add(btn_during_sel, 0, wx.ALL, 0)
        sizer_sel.Add(btn_after_sel, 0, wx.ALL, 0)
        panel_sel.SetSizer(sizer_sel)

        slider = sppasSliderPanel(self, name="time_slider")
        height = self.get_font_height()
        slider.SetMinSize(wx.Size(-1, self.get_font_height()))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(slider, 0, wx.EXPAND, 0)
        sizer.Add(panel_sel, 0, wx.EXPAND, 0)
        sizer.Add(btn_part, 0, wx.EXPAND, 0)
        sizer.Add(btn_dur, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.SetMinSize(wx.Size(-1, 4*height))

        self.set_duration(0.)

    # -----------------------------------------------------------------------

    @property
    def _btn_duration(self):
        return self.FindWindow("total_button")

    @property
    def _btn_visible(self):
        return self.FindWindow("visible_part_button")

    @property
    def _btn_before(self):
        return self.FindWindow("before_sel_button")

    @property
    def _btn_after(self):
        return self.FindWindow("after_sel_button")

    @property
    def _btn_selection(self):
        return self.FindWindow("selection_button")

    @property
    def _slider(self):
        return self.FindWindow("time_slider")

    # -----------------------------------------------------------------------

    def __create_toggle_btn(self, parent, label, name):
        btn = ToggleTextButton(parent, label=label, name=name)
        btn.SetBorderWidth(1)
        btn.SetFocusWidth(0)
        btn.SetValue(False)
        btn.SetMinSize(wx.Size(-1, self.get_font_height()))

        return btn

    # -----------------------------------------------------------------------

    def _process_toggle_event(self, event):
        for child in self.GetChildren():
            if isinstance(child, ToggleTextButton) is True:
                if child is event.GetEventObject():
                    child.SetValue(True)
                else:
                    child.SetValue(False)
            for c in child.GetChildren():
                if isinstance(c, ToggleTextButton) is True:
                    if c is event.GetEventObject():
                        c.SetValue(True)
                    else:
                        c.SetValue(False)

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Time Edit Panel")

        p = TimeSliderPanel(self)
        # p.set_duration(0.123456)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

