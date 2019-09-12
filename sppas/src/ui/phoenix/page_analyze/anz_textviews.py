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

    ui.phoenix.page_analyze.anz_textviews.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from ..main_events import EVT_VIEW
from .anz_baseviews import BaseViewFilesPanel
from .textview import TextViewPanel

# ----------------------------------------------------------------------------


class TextViewFilesPanel(BaseViewFilesPanel):
    """Panel to display the list of opened files and their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    In this views, the content of each file is displayed "as it", like
    a text editor.

    """

    def __init__(self, parent, name="textviewfiles", files=tuple()):
        super(TextViewFilesPanel, self).__init__(
            parent,
            name=name,
            files=files)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    # -----------------------------------------------------------------------

    def can_edit(self):
        """Return True if this view can edit/save the file content.

        Override base class.

        The methods 'is_modified' and 'save' should be implemented in the
        view panel of each file.

        """
        return True

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def _show_file(self, name):
        """Display the file."""
        wx.LogMessage("Displaying file {:s} in TextView mode.".format(name))
        panel = TextViewPanel(self, filename=name)
        panel.SetHighLightColor(self._hicolor)
        self.GetSizer().Add(panel, 0, wx.EXPAND)
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

        if action == "size":
            self.Layout()
            self.Refresh()

        elif action == "save":
            self.notify(action="save", filename=fn)

        elif action == "close":
            self.notify(action="close", filename=fn)

