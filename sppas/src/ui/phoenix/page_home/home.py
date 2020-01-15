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

    ui.phoenix.page_files.welcome.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import webbrowser

from sppas.src.config import sg

from ..windows import sppasTitleText
from ..windows import sppasMessageText
from ..windows import sppasPanel
from ..windows import BitmapTextButton

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
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        sppasPanel.SetFont(self, font)
        self.FindWindow("title").SetFont(wx.GetApp().settings.header_text_font)
        self.Layout()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        pass

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
        st.SetMinSize(wx.Size(len(title)*h*2, h*2))

        # Create the welcome message
        message = \
            "This is the new version of the Graphical User Interface. " \
            "It includes very interesting new features but is still under " \
            "development and un-documented.\n"\
            "For any help, see the web page and the documentation included " \
            "in the package.\n"
        txt = sppasMessageText(self, message)

        sppas_logo = BitmapTextButton(self, name="SPPAS")
        sppas_logo.SetMinSize(wx.Size(sppasPanel.fix_size(64), -1))
        sppas_logo.SetBorderWidth(0)
        sppas_logo.SetLabelPosition(wx.TOP)

        # Organize the title and message
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(st, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, h)
        sizer.Add(txt, 1, wx.EXPAND)
        sizer.Add(sppas_logo, 1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer.AddStretchSpacer(2)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "SPPAS":
            webbrowser.open(sg.__url__)
        else:
            event.Skip()
