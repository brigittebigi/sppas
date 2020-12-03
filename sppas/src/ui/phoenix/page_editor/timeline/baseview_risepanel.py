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

    ui.phoenix.page_edit.baseview_risepanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A base class for any object that displays the content of a file in a
    timeline.

"""

import wx
import os
import random

from sppas.src.config import paths

from sppas.src.ui.phoenix.windows.panels import sppasPanel
from sppas.src.ui.phoenix.windows.panels import sppasVerticalRisePanel

from .timedatatype import TimelineType
from .timeevents import TimelineViewEvent

# ----------------------------------------------------------------------------


class sppasFileViewPanel(sppasVerticalRisePanel):
    """Rise Panel to view&edit the content of a file in a time-view style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Events emitted by this class:

        - EVT_TIMELINE_VIEW

    """

    def __init__(self, parent, filename, name="baseview_risepanel"):
        super(sppasFileViewPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            label=filename,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
            name=name)

        self._ft = TimelineType().unknown
        self._dirty = False
        self._filename = filename

        # Default background color ranges
        self._rgb1 = (150, 150, 150)
        self._rgb2 = (220, 220, 220)

        # Create the GUI
        self._create_content()

        # Look&feel
        try:
            settings = wx.GetApp().settings
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()
        self.Layout()

    # -----------------------------------------------------------------------

    def SetRandomColours(self):
        """Set background and foreground colors from our range of rgb colors."""
        # Fix the color of the background
        r = random.randint(min(self._rgb1[0], self._rgb2[0]), max(self._rgb1[0], self._rgb2[0]))
        g = random.randint(min(self._rgb1[1], self._rgb2[1]), max(self._rgb1[1], self._rgb2[1]))
        b = random.randint(min(self._rgb1[2], self._rgb2[2]), max(self._rgb1[2], self._rgb2[2]))
        color = wx.Colour(r, g, b)

        if (r + g + b) > 384:
            hi_color = color.ChangeLightness(90)
        else:
            hi_color = color.ChangeLightness(110)

        # Set the colors to the panel itself and to its children
        wx.Panel.SetBackgroundColour(self, color)
        self._child_panel.SetBackgroundColour(color)
        self._tools_panel.SetBackgroundColour(hi_color)

        min_i = min(self._rgb1 + self._rgb2 + (150,))
        fg = wx.Colour(r - min_i, g - min_i, b - min_i)
        self._child_panel.SetForegroundColour(fg)
        self._tools_panel.SetForegroundColour(fg)

    # ------------------------------------------------------------------------
    # About the file
    # ------------------------------------------------------------------------

    def is_unknown(self):
        return self._ft == TimelineType().unknown

    def is_audio(self):
        return self._ft == TimelineType().audio

    def is_video(self):
        return self._ft == TimelineType().video

    def is_trs(self):
        return self._ft == TimelineType().trs

    def is_image(self):
        return self._ft == TimelineType().image

    # ------------------------------------------------------------------------

    def get_filename(self):
        """Return the filename this panel is displaying."""
        return self._filename

    # ------------------------------------------------------------------------

    def set_filename(self, name):
        """Set a new name to the file.

        :param name: (str) Name of a file. It is not verified.

        """
        self._filename = name
        self.SetLabel(name)
        self._dirty = True

    # ------------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self._dirty

    # -----------------------------------------------------------------------
    # Visible part
    # -----------------------------------------------------------------------

    def set_visible_period(self, start, end):
        """Fix the period of time to display (seconds).

        :param start: (int)
        :param end: (int) Time in seconds

        """
        try:
            self.GetPane().set_visible_period(start, end)
        except AttributeError:
            pass

    # -----------------------------------------------------------------------

    def set_selection_period(self, start, end):
        """Fix a period of time to highlight (seconds).

        :param start: (int)
        :param end: (int) Time in seconds

        """
        try:
            self.GetPane().set_selection_period(start, end)
        except AttributeError:
            pass

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action, value=None):
        """Notify the parent of a TimelineViewEvent.

        The parent can catch the event with EVT_TIMELINE_VIEW.

        """
        wx.LogDebug(
            "{:s} notifies its parent {:s} of action {:s}."
            "".format(self.GetName(), self.GetParent().GetName(), action))
        evt = TimelineViewEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------


class TestPanel(sppasFileViewPanel):

    FILENAME = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, TestPanel.FILENAME, name="BaseView RisePanel")
        self.Collapse(False)

    def _create_content(self):
        panel = sppasPanel(self)
        st = wx.StaticText(panel, -1, self.get_filename(), pos=(10, 100))
        sz = st.GetBestSize()
        panel.SetSize((sz.width + 20, sz.height + 20))
        self.SetPane(panel)

