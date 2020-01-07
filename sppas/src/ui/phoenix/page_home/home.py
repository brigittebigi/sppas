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

from sppas.src.config import sg

from sppas.src.ui.phoenix.windows import sppasTitleText
from sppas.src.ui.phoenix.windows import sppasMessageText
from sppas.src.ui.phoenix.windows import sppasPanel

from sppas.src.ui.phoenix.tools import sppasSwissKnife

# ---------------------------------------------------------------------------


class sppasHomePanel(sppasPanel):
    """Create a panel to display a welcome message.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

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

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # create a banner
        bmp = sppasSwissKnife.get_bmp_image('splash_transparent', 100)
        sbmp = wx.StaticBitmap(self, wx.ID_ANY, bmp)

        # Create a title
        st = sppasTitleText(
            parent=self,
            value="Welcome")
        st.SetName("title")

        # Create the welcome message
        message = \
            "This is the new and experimental version of the GUI - "\
            "The Graphical User Interface, of {:s}. This version is " \
            "based on WxPython version 4.\n\n"\
            "The stable version of the GUI requires WxPython version 3.\n\n" \
            "For any help, see the web page with the installation instructions " \
            "and chapter 2 of the documentation.\n\n"\
            "{:s}".format(sg.__name__, sg.__url__)
        txt = sppasMessageText(self, message)

        # Organize the title and message
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sbmp, 2, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15)
        sizer.Add(st, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 15)
        sizer.Add(txt, 6, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()

        #if key_code == wx.WXK_F5 and cmd_down is False and shift_down is False:
        #    logging.debug('Refresh all the files [F5 keys pressed]')
        #    self.FindWindow("files").RefreshData()

        event.Skip()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        sppasPanel.SetFont(self, font)
        self.FindWindow("title").SetFont(wx.GetApp().settings.header_text_font)
        self.Layout()
