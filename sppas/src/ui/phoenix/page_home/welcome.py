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

    ui.phoenix.page_home.welcome.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.config import sg

from ..windows import sppasPanel
from ..windows import sppasTitleText
from ..windows import sppasMessageText

# ---------------------------------------------------------------------------


WELCOME = \
    "SPPAS is a scientific computer software package developed " \
    "by Brigitte Bigi, CNRS researcher at 'Laboratoire Parole et " \
    "Langage', Aix-en-Provence, France.\n\n" \
    "By using SPPAS, you agree to cite one of its references in your " \
    "publications.\n\n" \
    "You are invited to report problems or suggestions " \
    "with the feedback form of the 'Log Window'.\n\n" \
    "For any help when using SPPAS, see the tutorials on the web and " \
    "the documentation first."

# ---------------------------------------------------------------------------


class sppasWelcomePanel(sppasPanel):
    """Create a panel to display a welcome message with a title.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasWelcomePanel, self).__init__(
            parent=parent,
            name="welcome_panel",
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self._create_content()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        sppasPanel.SetFont(self, font)
        self.FindWindow("title").SetFont(wx.GetApp().settings.header_text_font)
        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        h = self.get_font_height()
        title = "{:s} - {:s}".format(sg.__name__, sg.__title__)

        # Create a title
        st = sppasTitleText(self, value=title)
        st.SetName("title")
        st.SetMinSize(wx.Size(sppasPanel.fix_size(420), h*3))

        # Create a "static" message text
        txt = sppasMessageText(self, WELCOME)

        # Organize the title and message
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, h)
        sizer.Add(txt, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, h)

        self.SetSizer(sizer)

# ----------------------------------------------------------------------------


class TestPanelWelcome(wx.Panel):

    def __init__(self, parent):
        super(TestPanelWelcome, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test Welcome Panel")

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(sppasWelcomePanel(self), 0, wx.ALL, 0)
        s.Add(sppasWelcomePanel(self), 1, wx.EXPAND, 0)
        self.SetSizer(s)


