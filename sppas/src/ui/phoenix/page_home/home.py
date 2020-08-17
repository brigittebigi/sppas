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

    ui.phoenix.page_home.home.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Home page of the GUI.
    The workspace is not needed in this page.

"""

import wx

from ..windows import sppasPanel
from .welcome import sppasWelcomePanel
from .links import sppasLinksPanel

# ---------------------------------------------------------------------------


class sppasHomePanel(sppasPanel):
    """Create a panel to display a welcome message.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasHomePanel, self).__init__(
            parent=parent,
            name="page_home",
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self._create_content()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------

    def set_data(self, data):
        pass

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        pw = sppasWelcomePanel(self)
        pl = sppasLinksPanel(self)

        # Organize the title and message
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(pw, 1, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, sppasPanel.fix_size(8))
        sizer.Add(pl, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, sppasPanel.fix_size(8))
        sizer.AddStretchSpacer(1)

        self.SetSizer(sizer)

# ----------------------------------------------------------------------------


class TestPanelHome(sppasHomePanel):
    def __init__(self, parent):
        super(TestPanelHome, self).__init__(parent)

