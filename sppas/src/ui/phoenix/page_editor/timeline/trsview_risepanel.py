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

    ui.phoenix.page_editor.timeline.trsview_risepanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.lib.newevent

from sppas.src.config import paths
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasRW

from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import sppasScrolledPanel
from sppas.src.ui.phoenix.windows.datactrls import sppasTierWindow

from ..editorevent import EVT_TIME_VIEW
from .baseview_risepanel import sppasFileViewPanel

# ---------------------------------------------------------------------------

# Internal use of event.
TrsEvent, EVT_TRS = wx.lib.newevent.NewEvent()
TrsCommandEvent, EVT_TRS_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


class TrsViewPanel(sppasFileViewPanel):
    """A panel to display the content of an annotated file in a timeline.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    The object this class is displaying is a sppasTranscription.

    Can't be constructed if the file is not supported and/or if an error
    occurred when opening or reading.

    Events emitted by this class is EVT_TIME_VIEW:

       - action="close" to ask for closing the panel
       - action="save" to ask for saving the file of the panel
       - action="select_tier", value=name of the tier to be selected

    """

    def __init__(self, parent, filename, name="trsview_risepanel"):
        try:
            # Before creating the trs, check if the file is supported.
            parser = sppasRW(filename)
            self._trs = parser.read()
        except TypeError:
            self.Destroy()
            raise

        super(TrsViewPanel, self).__init__(parent, filename, name)
        self._setup_events()
        self.Expand()

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
        self.GetPane().set_draw_period(start, end)

    # -----------------------------------------------------------------------

    def set_select_period(self, start, end):
        """Fix the time period to highlight (milliseconds).

        :param start: (int)
        :param end: (int) Time in milliseconds

        """
        self.GetPane().set_select_period(start, end)

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
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("save")
        self.AddButton("close")

        tp = TrsTimePanel(self, self._trs)
        self.SetPane(tp)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_BUTTON, self.__process_tool_event)

        # Events related to the embedded transcription
        self.Bind(EVT_TRS, self.__process_trs_event)

    # -----------------------------------------------------------------------

    def __process_trs_event(self, event):
        """Process an event from the embedded transcription.

        :param event: (wx.Event)

        """
        # notify the parent with a TimeViewEvent. It adds the filename.
        self.notify(action=event.action, value=event.value)

    # -----------------------------------------------------------------------

    def __process_tool_event(self, event):
        """Process the button event of the tools.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "save":
            # self.save()
            self.notify(action="save")

        elif name == "close":
            self.notify(action="close")

        else:
            event.Skip()

# ---------------------------------------------------------------------------


class TrsTimePanel(sppasPanel):
    """Display a transcription in a timeline view.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    Event emitted by this class is TRS_EVENT with:
        - action="select_tier", value=name of the tier to be selected

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

    def get_draw_period(self):
        for child in self.GetChildren():
            s, e = child.GetDrawPeriod()
            return int(s*1000.), int(e*1000.)
        return 0, 0

    # -----------------------------------------------------------------------

    def set_draw_period(self, start, end):
        """Period to display (in milliseconds)."""
        for child in self.GetChildren():
            child.SetDrawPeriod(
                float(start) / 1000.,
                float(end) / 1000.)

    # -----------------------------------------------------------------------

    def set_select_period(self, start, end):
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def get_select_period(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                period = child.get_selected_localization()
                start = int(period[0] * 1000.)
                end = int(period[1] * 1000.)
                return start, end

        return 0, 0

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

    def set_selected_ann(self, idx):
        """An annotation was selected."""
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
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for tier in self.__trs:
            tier_ctrl = sppasTierWindow(self, data=tier)
            tier_ctrl.SetMinSize(wx.Size(-1, sppasPanel.fix_size(24)))
            tier_ctrl.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_tier_click)

            sizer.Add(tier_ctrl, 0, wx.EXPAND, 0)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def notify(self, action, value=None):
        """Sends a EVT_VIEW event to the listener (if any)."""
        evt = TrsEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_tier_click(self, event):
        """Process a click on a tier.

        :param event: (wx.Event)

        """
        tier = event.GetObj()
        self.notify(action="select_tier", value=tier.get_name())

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

        self.Bind(EVT_TIME_VIEW, self._process_action)

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action event from one of the trs panels.

        :param event: (wx.Event)

        """
        panel = event.GetEventObject()
        action = event.action
        value = event.value
        wx.LogDebug("{:s} received an event action {:s} of file {:s} with value {:s}"
                    "".format(self.GetName(), action, panel.get_filename(), str(value)))

        if action == "select_tier":
            panel.set_selected_tiername(value)

        event.Skip()
