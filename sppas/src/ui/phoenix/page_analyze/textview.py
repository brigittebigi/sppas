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

    ui.phoenix.page_analyze.textview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TextViewPanel to display the content of a file as a simple ASCII text.

"""

import os
import codecs
import wx

from sppas import sg
from sppas import paths
from sppas import u
from sppas import msg

from ..main_events import ViewEvent

from ..windows import sppasPanel
from ..windows import sppasTextCtrl
from ..windows import sppasToolbar
from ..windows import sppasStaticLine

from .baseview import sppasBaseViewPanel

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


SHOWHIDE_MSG = _("Show/Hide")
SAVE_MSG = _("Save")
CLOSE_MSG = _("Close")

# ---------------------------------------------------------------------------


class TextViewPanel(sppasBaseViewPanel):
    """Display the content of a file into an editable TextCtrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="textview-panel", filename=""):
        self.__lines = 0
        super(TextViewPanel, self).__init__(parent, name, filename)

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self.__txtview.IsModified()

    # -----------------------------------------------------------------------

    def load_text(self):
        """Load the file and display it."""
        # TODO: progress bar while loading
        wx.LogMessage("Load text of file {:s}".format(self._filename))
        try:
            with codecs.open(self._filename, 'r', sg.__encoding__) as fp:
                lines = fp.readlines()
        except Exception as e:
            lines = ["The file can't be loaded by this view. ",
                     "Error is: %s" % str(e)]

        content = "".join(lines)
        txtctrl = self.FindWindow("textctrl")
        txtctrl.SetValue(content)

        # required under Windows
        txtctrl.SetStyle(0, len(content), txtctrl.GetDefaultStyle())

        # Search for the height of the text
        self.__lines = len(lines) + 1
        view_height = float(self.get_line_height()) * 1.1 * self.__lines
        txtctrl.SetMinSize(wx.Size(sppasPanel.fix_size(320), view_height))

        self.__txtview.SetModified(False)
        wx.LogMessage("Text loaded: {:d} lines.".format(self.__lines))

    # -----------------------------------------------------------------------

    def save(self):
        """Save the displayed text into a file."""
        content = self.__txtview.GetValue()
        with codecs.open(self._filename, 'w', sg.__encoding__) as fp:
            fp.write(content)

        self.__txtview.SetModified(False)
        return True

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content, ie the content of the embedded panel."""
        line1 = self.__create_hline(self)
        line1.SetName("line1")
        tb = self.__create_toolbar(self)
        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | \
                wx.TE_PROCESS_ENTER | wx.TE_BESTWRAP | wx.TE_NO_VSCROLL
        self.__txtview = sppasTextCtrl(self, style=style, name="textctrl")
        self.__txtview.SetFont(wx.GetApp().settings.mono_text_font)
        self.__txtview.SetEditable(True)
        self.__txtview.SetModified(False)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(line1, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(tb, 0, wx.EXPAND)
        sizer.Add(self.__create_hline(self), 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.__txtview, 1, wx.EXPAND)
        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_toolbar(self, parent):
        """Create the toolbar."""
        tb = sppasToolbar(parent, name="textview-toolbar")
        tb.set_height(16)
        tb.set_focus_color(self._hicolor)
        tb.AddButton("save", SAVE_MSG)
        tb.AddButton("close", CLOSE_MSG)
        return tb

    # ------------------------------------------------------------------------

    def __create_hline(self, parent):
        """Create a vertical line, used to separate the panels."""
        line = sppasStaticLine(parent, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, 2))
        line.SetSize(wx.Size(-1, 2))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(2)
        line.SetForegroundColour(self._hicolor)
        return line

    # -----------------------------------------------------------------------

    def get_line_height(self):
        font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))

    # -----------------------------------------------------------------------

    def _eval_height(self):
        """Return the optimal height of the textctrl."""
        tb_height = self.FindWindow("textview-toolbar").get_height()
        lines_height = 4
        view_height = float(self.get_line_height()) * 1.3 * self.__lines
        return tb_height + lines_height + int(view_height) + 6

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action):
        evt = ViewEvent(action=action)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of event.

        :param event: (wx.Event)

        """
        event_obj = event.GetButtonObj()
        event_name = event_obj.GetName()

        if event_name == "close":
            wx.LogDebug("Parent is notified to close")
            self.notify("close")

        elif event_name == "save":
            if self.is_modified() is True:
                wx.LogDebug("Parent is notified to save")
                self.notify("save")
            else:
                wx.LogDebug("File wasn't modified. Nothing to do.")

        else:
            event.Skip()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(TextViewPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, filename=os.path.join(paths.samples, "COPYRIGHT.txt"))
        #self.SetBackgroundColour(wx.Colour(128, 128, 128))
