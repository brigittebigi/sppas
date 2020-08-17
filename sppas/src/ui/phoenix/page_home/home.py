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

    One of the main pages of the wx4-based GUI of SPPAS.

    The workspace is not needed in this page. It simply display a welcome
    message and links to the SPPAS web site.

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
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
            name="page_home"
        )
        self._create_content()

        # Capture keys to get access to links
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        # Organize items and fix a size for each of them
        self.Layout()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        pass

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        pw = sppasWelcomePanel(self)
        pl = sppasLinksPanel(self, name="links_panel")

        # Organize the title and message
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(pw, 2, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, sppasPanel.fix_size(8))
        sizer.Add(pl, 2, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, sppasPanel.fix_size(8))
        sizer.AddStretchSpacer(1)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if event.AltDown() is True:
            if key_code == 66:      # alt+b Browse to the author home page
                self.FindWindow("links_panel").author_btn.browse()

            elif key_code == 68:    # alt+d Browse to the documentation page
                self.FindWindow("links_panel").doc_btn.browse()

            elif key_code == 72:    # alt+h Browse to SPPAS Home page
                self.FindWindow("links_panel").home_btn.browse()

            elif key_code == 81:    # alt+q Browse to the F.A.Q. page
                self.FindWindow("links_panel").faq_btn.browse()

            elif key_code == 84:    # alt+t Browse to tutorials page
                self.FindWindow("links_panel").tuto_btn.browse()


# ----------------------------------------------------------------------------


class TestPanelHome(sppasHomePanel):
    def __init__(self, parent):
        super(TestPanelHome, self).__init__(parent)

