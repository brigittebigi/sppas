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

    ui.phoenix.page_analyze.trsfileedit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.lib
import wx.media

from sppas.src.config import paths
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasRW

from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import MediaEvents
from ..windows.datactrls import sppasTierWindow
from ..main_events import ViewEvent, EVT_VIEW

from .basefileedit import sppasFileViewPanel

# ---------------------------------------------------------------------------


class TrsViewPanel(sppasFileViewPanel):
    """A panel to display the content of an annotated files in a timeline.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    The object this class is displaying is a sppasTranscription.
    Can not be constructed if the file is not supported and/or if an error
    occurred when opening or reading.

    """

    def __init__(self, parent, filename, name="trs_view_panel"):
        try:
            # Before creating the trs, check if the file is supported.
            parser = sppasRW(filename)
            self._trs = parser.read()
        except TypeError:
            self.Destroy()
            raise

        super(TrsViewPanel, self).__init__(parent, filename, name)
        self.Bind(wx.EVT_BUTTON, self.__process_tool_event)
        self.Bind(EVT_VIEW, self.__process_view_event)

    # -----------------------------------------------------------------------

    def is_selected(self):
        """Return True is this file is selected."""
        return self.IsExpanded()

    # -----------------------------------------------------------------------

    def get_tier_list(self):
        """Return the list of all tiers."""
        return self._trs.get_tier_list()

    # -----------------------------------------------------------------------

    def get_tiernames(self):
        """Return the list of all tier names."""
        return [tier.get_name() for tier in self._trs.get_tier_list()]

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        """Return the name of the selected tier or None."""
        return self.GetPane().get_selected_tiername()

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, tier_name):
        """Set the selected tier."""
        self.GetPane().set_selected_tiername(tier_name)

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        """Return the index of the selected ann or -1."""
        return self.GetPane().get_selected_ann()

    # -----------------------------------------------------------------------

    def set_selected_ann(self, idx):
        """Set the index of the selected ann or -1."""
        return self.GetPane().set_selected_ann(idx)

    # -----------------------------------------------------------------------

    def update_ann(self, idx):
        """An annotation was modified."""
        self._dirty = True
        return self.GetPane().update_ann(idx)

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        """An annotation was deleted."""
        self._dirty = True
        return self.GetPane().delete_ann(idx)

    # -----------------------------------------------------------------------

    def create_ann(self, idx):
        """An annotation was created."""
        self._dirty = True
        return self.GetPane().create_ann(idx)

    # -----------------------------------------------------------------------

    def set_draw_period(self, start, end):
        """Fix the time period to display (milliseconds).

        :param start: (int)
        :param end: (int) Time in milliseconds

        """
        self.GetPane().SetDrawPeriod(start, end)

    # -----------------------------------------------------------------------

    def get_selected_period(self):
        """Return the time period of the currently selected annotation.

        :return: (int, int) Start and end values in milliseconds

        """
        idx = self.GetPane().get_selected_ann()
        if idx == -1:
            return 0, 0

        return self.GetPane().get_selected_period()

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def save(self, filename=None):
        """Save the displayed transcription into a file.

        :param filename: (str) To be used to "save as..."

        """
        parser = None
        if filename is None and self._dirty is True:
            # the writer will increase the file version
            parser = sppasRW(self._filename)
            self._dirty = False
        if filename is not None:
            parser = sppasRW(filename)

        if parser is not None:
            parser.write(self._trs)
            return True
        return False

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("save")
        self.AddButton("close")

        self.SetPane(TrsTimePanel(self, self._trs))
        self.Expand()

    # -----------------------------------------------------------------------

    def __process_view_event(self, event):
        """Process a click on a tier.

        :param event: (wx.Event)

        """
        self.notify(action="tier_selected")

    # -----------------------------------------------------------------------

    def __process_tool_event(self, event):
        """Process the button event of the tools.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "save":
            self.save()
            # self.notify(action="save")

        elif name == "close":
            self.notify(action="close")

        else:
            event.Skip()

# ---------------------------------------------------------------------------


class TrsTimePanel(sppasPanel):
    """Display a transcription in a timeline view.

    """

    def __init__(self, parent, transcription=None, name="trs_panel"):
        super(TrsTimePanel, self).__init__(parent, name=name)
        self.__trs = transcription
        self._create_content()

    # -----------------------------------------------------------------------

    def set_transcription(self, transcription):
        """Fix the transcription object if it wasn't done when init.

        """
        if self.__trs is not None:
            raise Exception("A sppasTranscription is already defined.")
        if isinstance(transcription, sppasTranscription):
            self.__trs = transcription

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                return child.get_tiername()
        return None

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, tier_name=None):
        """Set the selected tier.

        :param tier_name: (str)

        """
        if tier_name is not None:
            assert tier_name in [t.get_name() for t in self.__trs]

        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.SetBorderColour(self.GetForegroundColour())
                child.SetSelected(False)
                child.Refresh()
            if child.get_tiername() == tier_name:
                child.SetBorderColour(wx.RED)
                child.SetSelected(True)
                child.Refresh()

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                return child.get_selected_ann()

        return -1

    # -----------------------------------------------------------------------

    def get_selected_period(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                period = child.get_selected_localization()
                start = int(period[0] * 1000.)
                end = int(period[1] * 1000.)
                return start, end

        return 0, 0

    # -----------------------------------------------------------------------

    def set_selected_ann(self, idx):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.set_selected_ann(idx)

    # -----------------------------------------------------------------------

    def update_ann(self, idx):
        """An annotation was modified."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.update_ann(idx)

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        """An annotation was deleted."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.delete_ann(idx)

    # -----------------------------------------------------------------------

    def create_ann(self, idx):
        """An annotation was created."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.create_ann(idx)

    # -----------------------------------------------------------------------

    def SetDrawPeriod(self, start, end):
        """Period to display (in milliseconds)."""
        for child in self.GetChildren():
            child.SetDrawPeriod(
                float(start) / 1000.,
                float(end) / 1000.)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for tier in self.__trs:
            tier_ctrl = sppasTierWindow(self, data=tier)
            tier_ctrl.SetMinSize(wx.Size(-1, sppasPanel.fix_size(24)))
            tier_ctrl.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_data_selected)

            sizer.Add(tier_ctrl, 0, wx.EXPAND, 0)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a EVT_VIEW event to the listener (if any)."""
        evt = ViewEvent(action="tier_selected")
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_data_selected(self, event):
        """Process a click on a tier.

        :param event: (wx.Event)

        """
        tier = event.GetObj()
        self.set_selected_tiername(tier.get_name())
        self.Notify()

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test Trs View")

        p2 = TrsViewPanel(self, filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.TextGrid"))
        p3 = TrsViewPanel(self, filename=os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra"))

        p3.set_draw_period(2300, 3500)
        p3.set_selected_tiername("PhonAlign")

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p2, 0, wx.EXPAND | wx.ALL, 10)
        s.Add(p3, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Bind(MediaEvents.EVT_MEDIA_ACTION, self._process_media_action)

    # -----------------------------------------------------------------------

    def _process_media_action(self, event):
        """Process an action event from the player.

        An action on media files has to be performed.

        :param event: (wx.Event)

        """
        name = event.action
        value = event.value

        if name == "loaded":
            if value is True:
                event.GetEventObject().get_object().Play()

        event.Skip()
