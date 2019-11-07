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

    ui.phoenix.page_analyze.anz_listviews.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from ..main_events import EVT_VIEW
from ..windows import sppasCollapsiblePanel
from .anz_baseviews import BaseViewFilesPanel
from .listview import TrsViewCtrl

# ----------------------------------------------------------------------------


class ListViewFilesPanel(BaseViewFilesPanel):
    """Panel to display the list of opened files and their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="listviewfiles", files=tuple()):
        super(ListViewFilesPanel, self).__init__(
            parent,
            name=name,
            files=files)
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    # -----------------------------------------------------------------------

    def can_edit(self):
        """Return True if this view can edit/save the file content.

        Override base class.

        The methods 'is_modified' and 'save' should be implemented in the
        view panel of each file.

        """
        return False   # True

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def _show_file(self, name):
        """Create a CollapsiblePanel and a TextViewPanel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        wx.LogMessage("Displaying file {:s} in TextView mode.".format(name))
        cp = sppasCollapsiblePanel(self, label=name)
        panel = TrsViewCtrl(cp, filename=name)
        # panel.SetHighLightColor(self._hicolor)
        cp.SetPane(panel)
        self.GetSizer().Add(cp, 0, wx.EXPAND)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, cp)

        return panel

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate an handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(EVT_VIEW, self._process_view_event)

    # -----------------------------------------------------------------------

    def _process_view_event(self, event):
        """Process a view event: an action has to be performed.

        :param event: (wx.Event)

        """
        try:
            panel = event.GetEventObject()
            panel_name = panel.GetName()

            action = event.action
            fn = None
            for filename in self._files:
                p = self._files[filename]
                if p == panel:
                    fn = filename
                    break
            if fn is None:
                raise Exception("Unknown {:s} panel in ViewEvent."
                                "".format(panel_name))
        except Exception as e:
            wx.LogError(str(e))
            return

        if action == "save":
            self.notify(action="save", filename=fn)

        elif action == "close":
            self.notify(action="close", filename=fn)

    # -----------------------------------------------------------------------

    def OnSize(self, evt):
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.ScrollChildIntoView(panel)
