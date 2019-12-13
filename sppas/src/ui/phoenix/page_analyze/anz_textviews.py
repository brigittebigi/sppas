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

import os
import wx

from sppas import paths

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
        """Create a CollapsiblePanel and a TextViewPanel to display a file.

        :param name: (str) Name of the file to view
        :return: wx.Window

        """
        wx.LogMessage("Displaying file {:s} in TextView mode.".format(name))
        panel = TextViewPanel(self.GetScrolledPanel(), filename=name)
        self.GetScrolledSizer().Add(panel, 0, wx.EXPAND)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)

        return panel

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(TextViewFilesPanel):
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

