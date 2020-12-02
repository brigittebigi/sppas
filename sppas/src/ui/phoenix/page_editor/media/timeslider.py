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

    A selection bar to mimic the one into Praat software tool; it allows to
    indicate a moment in time and to select different periods of time, named:

        - whole duration;
        - visible part;
        - selected part.

"""

import wx
import logging

from sppas.src.config import paths
from sppas.src.ui.phoenix.windows.buttons import ToggleTextButton
from sppas.src.ui.phoenix.windows.panels import sppasPanel, sppasImagePanel
from sppas.src.ui.phoenix.windows.slider import sppasSlider
from .tickslider import sppasTicksSlider

from .mediaevents import MediaEvents

# ---------------------------------------------------------------------------


MSG_TOTAL_DURATION = "Total duration: "
MSG_VISIBLE_DURATION = "Visible part: "
SECONDS_UNIT = "seconds"

# ----------------------------------------------------------------------------


class ToggleSlider(ToggleTextButton):
    """A toggle button with a specific design and properties.

     :author:       Brigitte Bigi
     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
     :contact:      contact@sppas.org
     :license:      GPL, v3
     :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    # Foreground of the pressed toggle is blue if pressed
    FG_TRUE_COLOUR = wx.Colour(30, 80, 210)

    # BG_IMAGE = os.path.join(paths.etc, "images", "bg_brushed_metal2.jpg")

    # -----------------------------------------------------------------------

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        """
        super(ToggleSlider, self).__init__(parent, id, label, pos, size, name)
        ToggleTextButton.SetValue(self, False)
        self._fg_false_colour = self.GetForegroundColour()
        self.SetHorizBorderWidth(1)
        self.SetFocusWidth(0)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        ToggleTextButton.SetBackgroundColour(self, colour)
        border_color = self.GetHighlightedColour(colour, 30)
        self.SetBorderColour(border_color)

    # -----------------------------------------------------------------------

    def SetValue(self, value):
        ToggleTextButton.SetValue(self, value)
        if self.GetValue() is True:
            # self.SetBackgroundImage(None)
            self._fg_false_colour = self.GetForegroundColour()
            wx.Window.SetForegroundColour(self, ToggleSlider.FG_TRUE_COLOUR)
        else:
            # self.SetBackgroundImage(ToggleSlider.BG_IMAGE)
            self.SetForegroundColour(self._fg_false_colour)

# ----------------------------------------------------------------------------


class TimeSliderPanel(sppasPanel):
    """A panel embedding information about time: start, end, selected, etc.

     :author:       Brigitte Bigi
     :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
     :contact:      contact@sppas.org
     :license:      GPL, v3
     :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    The range of the slider depends on the selected button. It's one of:
        - from the beginning of the visible part to the beginning of the selection;
        - the period during the selection;
        - the period after the selection until the end of the visible part;
        - the whole visible part;
        - the whole period, from 0 to duration.

    """

    # The selection has its own colors
    SELECTION_BG_COLOUR = wx.Colour(250, 170, 180)
    SELECTION_FG_COLOUR = wx.Colour(50, 70, 80)

    # SLIDER INDICATOR BG
    # BG_SLIDER_IMG = os.path.join(paths.etc, "images", "bg_slider.png")

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

        # Create the GUI
        self._create_content()
        self._setup_events()

        # Look&feel
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.__update_height()

    # -----------------------------------------------------------------------
    # Setters of the GUI
    # -----------------------------------------------------------------------

    def show_range(self, value=True):
        """Show the currently selected range."""
        if bool(value) is True:
            self._slider.Show()
        else:
            self._slider.Hide()
        self.__update_height()

    # -----------------------------------------------------------------------

    def show_rule(self, value=True):
        """Show a ruler of the visible part."""
        if bool(value) is True:
            self._ruler.Show()
        else:
            self._ruler.Hide()
        self.__update_height()

    # -----------------------------------------------------------------------
    # Toggle buttons value
    # -----------------------------------------------------------------------

    def is_selection(self):
        """Return True if the toggle button of the selection is pressed."""
        return self._btn_selection.GetValue()

    # -----------------------------------------------------------------------

    def is_visible(self):
        """Return True if the toggle button of the selection is pressed."""
        return self._btn_visible.GetValue()

    # -----------------------------------------------------------------------

    def is_duration(self):
        """Return True if the toggle button of the selection is pressed."""
        return self._btn_duration.GetValue()

    # -----------------------------------------------------------------------
    # Slider
    # -----------------------------------------------------------------------

    def get_range(self):
        """Return the current range value of the slider."""
        return self._slider.get_range()

    # -----------------------------------------------------------------------

    def get_value(self):
        """Return the current position value of the slider."""
        return self._slider.get_value()

    # -----------------------------------------------------------------------

    def set_value(self, pos):
        """Set the current position value of the slider."""
        pos = float(pos)
        if pos < 0.:
            return False
        if pos > self.__duration:
            return False
        current = self._slider.get_value()
        if current != pos:
            self._slider.set_value(pos)
            self._slider.Refresh()
            self._ruler.set_value(pos)
            self._ruler.Refresh()
            return True
        return False

    # -----------------------------------------------------------------------
    # Whole duration - i.e. the max value
    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration value (float)"""
        return self.__duration

    # -----------------------------------------------------------------------

    def set_duration(self, value=0.):
        """Fix the duration value.

        :param value: (float) Time value in seconds.

        """
        value = float(value)
        if value < 0.:
            raise ValueError

        self.__duration = value
        self._btn_duration.SetLabel("{:s} {:s} {:s}".format(MSG_TOTAL_DURATION, self.__seconds_label(value), SECONDS_UNIT))

        # if other values are out of duration range, they need update.
        if self.__end_visible > value:
            self.__end_visible = value
        if self.__end_selection > value:
            self.__end_selection = value
        if self.__start_visible > value:
            self.__start_visible = value
        if self.__start_selection > value:
            self.__start_selection = value

        # Disable all other buttons. Enable duration toggle button.
        if value == 0.:
            self._btn_duration.SetValue(True)
            self.set_visible_range(0., 0.)
        self._btn_duration.Refresh()

        # Update the slider
        self.__update_slider()

    # -----------------------------------------------------------------------
    # Visible part - must be less than duration
    # -----------------------------------------------------------------------

    def get_visible_start(self):
        """Return start time value of the visible part."""
        return self.__start_visible

    # -----------------------------------------------------------------------

    def get_visible_end(self):
        """Return end time value of the visible part."""
        return self.__end_visible

    # -----------------------------------------------------------------------

    def get_visible_range(self):
        """Return (start, end) time values of the visible part."""
        return self.__start_visible, self.__end_visible

    # -----------------------------------------------------------------------

    def set_visible_range(self, start, end):
        """Set the visible time range."""
        start = float(start)
        end = float(end)
        if start < 0.:
            start = 0.
        if end < start:
            raise ValueError

        if end > self.__duration:
            logging.warning(
                "Given end visible value {} is greater than duration {}. "
                "Duration is updated.".format(end, self.__duration))
            self.__duration = end

        self.__start_visible = start
        self.__end_visible = end
        dur = end - start
        self._btn_visible.SetLabel("{:s} {:s} {:s}".format(MSG_VISIBLE_DURATION, self.__seconds_label(dur), SECONDS_UNIT))
        self._ruler.set_range(start, end)
        if dur == 0.:
            self._btn_duration.SetValue(True)
            self._btn_visible.SetValue(False)

        # Update others
        self.__update_select_buttons()
        self.__update_slider()

    # -----------------------------------------------------------------------
    # Set selected part - must be less than duration
    # -----------------------------------------------------------------------

    def get_selection_start(self):
        """Return start time value of the selected part."""
        return self.__start_selection

    # -----------------------------------------------------------------------

    def get_selection_end(self):
        """Return end time value of the selected part."""
        return self.__end_selection

    # -----------------------------------------------------------------------

    def get_selection_range(self):
        """Return (start, end) time values of the selected part."""
        return self.__start_selection, self.__end_selection

    # -----------------------------------------------------------------------

    def set_selection_range(self, start, end):
        """Set the selected time range."""
        start = float(start)
        end = float(end)
        if end < start:
            raise ValueError
        if start < 0.:
            raise ValueError

        if end > self.__duration:
            logging.warning(
                "Given end selection value {} is greater than duration {}. "
                "Duration is updated.".format(end, self.__duration))
            self.__duration = end

        self.__start_selection = start
        self.__end_selection = end
        self.__update_select_buttons()
        self._selection.Layout()

        # Update the slider
        self.__update_slider()

    # -----------------------------------------------------------------------
    # Look&feel
    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. """
        # The font of this panel is used only to control its height
        f = wx.Font(int(float(font.GetPointSize()) * 1.2),
                    wx.FONTFAMILY_SWISS,   # family,
                    wx.FONTSTYLE_NORMAL,   # style,
                    wx.FONTWEIGHT_NORMAL,  # weight,
                    underline=False,
                    faceName=font.GetFaceName(),
                    encoding=wx.FONTENCODING_SYSTEM)
        wx.Panel.SetFont(self, f)

        # The font that is displaying message is inside the children
        for c in self.GetChildren():
            f = wx.Font(int(float(font.GetPointSize()) * 0.8),
                        font.GetFamily(),        # family,
                        wx.FONTSTYLE_NORMAL,     # style,
                        wx.FONTWEIGHT_NORMAL,    # weight,
                        underline=False,
                        faceName=font.GetFaceName(),
                        encoding=wx.FONTENCODING_SYSTEM)
            c.SetFont(f)

        # Update height of each panel and layout
        self.__update_height()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override. """
        wx.Panel.SetBackgroundColour(self, colour)
        for child in self.GetChildren():
            child.SetBackgroundColour(colour)
            for c in child.GetChildren():
                if c.GetName() == "selection_button":
                    c.SetBackgroundColour(TimeSliderPanel.SELECTION_BG_COLOUR)
                else:
                    c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. """
        wx.Panel.SetForegroundColour(self, colour)
        for child in self.GetChildren():
            if isinstance(child, ToggleTextButton) is True and child.GetValue() is True:
                child.SetForegroundColour(ToggleSlider.FG_TRUE_COLOUR)
            else:
                child.SetForegroundColour(colour)
                for c in child.GetChildren():
                    if isinstance(child, ToggleTextButton) is True and child.GetValue() is True:
                        child.SetForegroundColour(ToggleSlider.FG_TRUE_COLOUR)
                    else:
                        if c.GetName() == "selection_button":
                            c.SetForegroundColour(TimeSliderPanel.SELECTION_FG_COLOUR)
                        else:
                            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def OnSize(self, event):
        self.__update_select_buttons()
        self.Refresh()
        event.Skip()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        btn_dur = ToggleSlider(self, label="--", name="total_button")
        btn_part = ToggleSlider(self, label="--", name="visible_part_button")

        panel_sel = sppasImagePanel(self, name="selection_panel")
        btn_before_sel = ToggleSlider(panel_sel, label="--", name="before_sel_button")
        btn_after_sel = ToggleSlider(panel_sel, label="--", name="after_sel_button")

        btn_during_sel = ToggleTextButton(panel_sel, label="--", name="selection_button")
        btn_during_sel.SetHorizBorderWidth(1)
        btn_during_sel.SetFocusWidth(0)
        btn_during_sel.SetValue(False)

        sizer_sel = wx.BoxSizer(wx.HORIZONTAL)
        sizer_sel.Add(btn_before_sel, 0, wx.EXPAND)
        sizer_sel.Add(btn_during_sel, 0, wx.EXPAND)
        sizer_sel.Add(btn_after_sel, 0, wx.EXPAND)
        panel_sel.SetSizer(sizer_sel)

        slider = sppasSlider(self, name="time_slider")
        # slider.SetBackgroundImage(TimeSliderPanel.BG_SLIDER_IMG)

        ruler = sppasTicksSlider(self, name="time_ruler")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(slider, 0, wx.EXPAND, 0)      # indicate the range of the current toggled
        sizer.Add(btn_dur, 0, wx.EXPAND, 0)
        sizer.Add(btn_part, 0, wx.EXPAND, 0)
        sizer.Add(panel_sel, 0, wx.EXPAND, 0)
        sizer.Add(ruler, 0, wx.EXPAND, 0)       # a rule on the visible part
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    @property
    def _btn_duration(self):
        return self.FindWindow("total_button")

    @property
    def _btn_visible(self):
        return self.FindWindow("visible_part_button")

    @property
    def _ruler(self):
        return self.FindWindow("time_ruler")

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
    def _selection(self):
        return self.FindWindow("selection_panel")

    @property
    def _slider(self):
        return self.FindWindow("time_slider")

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Bind events."""
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self._btn_before.Bind(wx.EVT_TOGGLEBUTTON, self._process_toggle_event)
        self._btn_selection.Bind(wx.EVT_TOGGLEBUTTON, self._process_toggle_event)
        self._btn_after.Bind(wx.EVT_TOGGLEBUTTON, self._process_toggle_event)
        self._btn_visible.Bind(wx.EVT_TOGGLEBUTTON, self._process_toggle_event)
        self._btn_duration.Bind(wx.EVT_TOGGLEBUTTON, self._process_toggle_event)

    # -----------------------------------------------------------------------

    def _process_toggle_event(self, event):
        """Process a change of time range."""
        obj = event.GetEventObject()
        name = obj.GetName()
        wx.LogDebug("Time Slider toggle pressed: {}".format(name))
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

        modified = self.__update_slider()
        if modified is True:

            evt = MediaEvents.MediaPeriodEvent(period=self._slider.get_range())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def __update_slider(self):
        old_start, old_end = self._slider.get_range()
        if self._btn_duration.GetValue() is True:
            self._slider.set_range(0., self.__duration)
        elif self._btn_visible.GetValue() is True:
            self._slider.set_range(self.__start_visible, self.__end_visible)
        elif self._btn_before.GetValue() is True:
            self._slider.set_range(self.__start_visible, self.__start_selection)
        elif self._btn_selection.GetValue() is True:
            self._slider.set_range(self.__start_selection, self.__end_selection)
        elif self._btn_after.GetValue() is True:
            self._slider.set_range(self.__end_selection, self.__end_visible)

        new_start, new_end = self._slider.get_range()
        if old_start != new_start or old_end != new_end:
            self._slider.Refresh()
            return True
        else:
            return False

    # -----------------------------------------------------------------------

    def __update_select_buttons(self):
        w = self.GetSize().GetWidth()
        visible_duration = self.__end_visible - self.__start_visible

        # If the selection is totally outside of the visible segment
        if self.__start_selection >= self.__end_visible or self.__end_selection <= self.__start_visible:
            # De-select the button
            if self._btn_before.GetValue() is True:
                self._btn_before.SetValue(False)
                self._btn_visible.SetValue(True)
            elif self._btn_selection.GetValue() is True:
                self._btn_selection.SetValue(False)
                self._btn_visible.SetValue(True)
            elif self._btn_after.GetValue() is True:
                self._btn_after.SetValue(False)
                self._btn_visible.SetValue(True)
            # Hide the selection buttons.
            self._btn_before.Hide()
            self._btn_selection.Hide()
            self._btn_after.Hide()
            return

        # The selection is inside or overlaps the visible segment
        wb = wa = 0

        # overlap at the beginning. no before button
        before_duration = self.__start_selection - self.__start_visible
        if before_duration <= 0.:
            if self._btn_before.GetValue() is True:
                self._btn_before.SetValue(False)
                self._btn_visible.SetValue(True)
            self._btn_before.Hide()
            before_duration = 0.
        else:
            self._btn_before.Show()
            wb = int(float(w) * before_duration / visible_duration)
            self._btn_before.SetMinSize(wx.Size(wb, -1))

        # overlap at the end. no after button
        after_duration = self.__end_visible - self.__end_selection
        if after_duration <= 0.:
            if self._btn_after.GetValue() is True:
                self._btn_after.SetValue(False)
                self._btn_visible.SetValue(True)
            self._btn_after.Hide()
            after_duration = 0.
        else:
            self._btn_after.Show()
            wa = int(float(w) * after_duration / visible_duration)
            self._btn_after.SetMinSize(wx.Size(wa, -1))

        # selection button
        self._btn_selection.Show()
        selection_duration = self.__end_selection - self.__start_selection
        self._btn_selection.SetMinSize(wx.Size((w - wb - wa), -1))

        # Fix labels
        self._btn_before.SetLabel(self.__seconds_label(before_duration))
        self._btn_selection.SetLabel(self.__seconds_label(selection_duration))
        self._btn_after.SetLabel(self.__seconds_label(after_duration))

    # -----------------------------------------------------------------------

    def __update_height(self):
        h = self.GetFont().GetPixelSize()[1]

        self._selection.SetMinSize(wx.Size(-1, h))
        self._btn_duration.SetMinSize(wx.Size(-1, h))
        self._btn_visible.SetMinSize(wx.Size(-1, h))
        panel_height = 3 * h

        ruler_height = int(float(h)*1.2)
        self._ruler.SetMinSize(wx.Size(-1, ruler_height))
        if self._ruler.IsShown():
            panel_height += ruler_height

        self._slider.SetMinSize(wx.Size(-1, h))
        if self._slider.IsShown():
            panel_height += h

        self.SetMinSize(wx.Size(-1, panel_height))
        self.Layout()

    # -----------------------------------------------------------------------

    def __seconds_label(self, value):
        return "{:.3f}".format(value)

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="Time Slider Panel")
        self.SetMinSize(wx.Size(320, 20))

        btn1 = ToggleTextButton(self, label="Show/Hide slider")
        btn1.SetMinSize(wx.Size(120, 32))
        btn1.SetValue(True)
        btn2 = ToggleTextButton(self, label="Show/Hide ruler")
        btn2.SetMinSize(wx.Size(120, 32))
        btn2.SetValue(True)

        p = TimeSliderPanel(self, name="tsp1")
        p.set_duration(12.123456)
        p.set_visible_range(3.45, 7.08765)
        p.set_selection_range(5.567, 6.87)
        p.set_value(6.)
        p.show_range(True)
        p.show_rule(True)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(btn1, 0, wx.ALL, 4)
        s.Add(btn2, 0, wx.ALL, 4)
        s.Add(p, 0, wx.EXPAND)
        self.SetSizer(s)

        self.Bind(MediaEvents.EVT_MEDIA_PERIOD, self._on_period_changed)
        btn1.Bind(wx.EVT_TOGGLEBUTTON, self._on_show_slider)
        btn2.Bind(wx.EVT_TOGGLEBUTTON, self._on_show_ruler)
        self.Layout()

    def _on_period_changed(self, event):
        p = event.period
        wx.LogDebug("Slider range from {} to {}".format(p[0], p[1]))

    def _on_show_slider(self, evt):
        self.FindWindow("tsp1").show_range(evt.GetEventObject().GetValue())
        self.Layout()

    def _on_show_ruler(self, evt):
        self.FindWindow("tsp1").show_rule(evt.GetEventObject().GetValue())
        self.Layout()
