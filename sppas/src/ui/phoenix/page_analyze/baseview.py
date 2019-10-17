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

    ui.phoenix.page_analyze.baseview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas import msg
from sppas import paths
from sppas.src.utils import u

from ..windows import sppasCollapsiblePanel
from ..windows import sppasStaticText

# ----------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_NO_CONTENT = _("Displaying a file is not implemented in this view.")

# ----------------------------------------------------------------------------


class sppasBaseViewPanel(sppasCollapsiblePanel):
    """Panel to display the content of a file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="baseview", filename=""):
        super(sppasBaseViewPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            label=filename,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The file this panel is displaying
        self._filename = filename

        # Create the GUI
        self._hicolor = self.GetForegroundColour()
        self._create_content()
        self._setup_events()

        if filename is not None:
            self.load_text()

        self.Layout()

    # -----------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return False

    def load_text(self):
        """Load the file and display it."""
        return False

    def save(self):
        """Save the displayed text into a file."""
        return False

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight something."""
        self._hicolor = color

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content, ie the content of the embedded panel."""
        pane = self.GetPane()
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        line_height = float(font.GetPixelSize()[1])

        txt_msg = sppasStaticText(pane, label=MSG_NO_CONTENT)
        txt_msg.SetMinSize(wx.Size(-1, line_height * 2))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txt_msg, 0, wx.EXPAND | wx.LEFT, sppasCollapsiblePanel.fix_size(34*2))
        pane.SetSizer(sizer)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        pass

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasBaseViewPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, filename=os.path.join(paths.samples, "COPYRIGHT.txt"))
        self.SetBackgroundColour(wx.Colour(128, 128, 128))
