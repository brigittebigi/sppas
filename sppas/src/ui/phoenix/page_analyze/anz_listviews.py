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

import os
import wx

from sppas import paths
from ..windows import sppasToolbar
from .anz_baseviews import BaseViewFilesPanel
from .listview import TrsListViewPanel

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
        """Create a ViewPanel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        wx.LogMessage("Displaying file {:s} in ListView mode.".format(name))
        panel = TrsListViewPanel(self, filename=name)
        self.GetScrolledSizer().Add(panel, 0, wx.EXPAND)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)

        return panel

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create the main toolbar.

        :return: (sppasPanel, wx.Panel, sppasToolbar, ...)

        """
        toolbar = sppasToolbar(self, name="toolbar_views")
        #toolbar.set_focus_color()

        toolbar.AddButton("tier_rename")
        toolbar.AddButton("tier_delete")
        toolbar.AddButton("tier_cut")
        toolbar.AddButton("tier_copy")
        toolbar.AddButton("tier_paste")
        toolbar.AddButton("tier_duplicate")
        toolbar.AddButton("tier_moveup")
        toolbar.AddButton("tier_movedown")
        toolbar.AddButton("tier_radius")
        toolbar.AddButton("tier_view")
        return toolbar

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.ScrollChildIntoView(panel)
        self.Layout()


# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(ListViewFilesPanel):
    TEST_FILES = (
        os.path.join(paths.samples, "COPYRIGHT.txt"),
        os.path.join(paths.samples, "annotation-results", "samples-fra",
                     "F_F_B003-P8-palign.xra")
    )

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            name="TestPanel-anz_baseviews",
            files=TestPanel.TEST_FILES)
        self.SetBackgroundColour(wx.Colour(128, 128, 128))

