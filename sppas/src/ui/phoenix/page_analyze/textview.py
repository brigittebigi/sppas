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

    ViewPanel to display the content of a file as a simple ASCII text.

"""

import os
import codecs
import wx

from sppas import sg
from sppas import paths

from ..main_events import ViewEvent

from ..windows import sppasPanel
from ..windows import sppasTextCtrl
from ..windows import sppasToolbar
from ..windows import sppasStaticLine

from .baseview import sppasBaseViewPanel

# ----------------------------------------------------------------------------


class TextViewPanel(sppasBaseViewPanel):
    """Display the content of a file into an editable TextCtrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="textview", filename=""):
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
        
        # Search the height of the text
        self.__lines = len(lines)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(320),
                                self._eval_height()))

        self.__txtview.SetModified(False)

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
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        line1 = self.__create_hline()
        line1.SetName("line1")
        sizer.Add(line1, 0, wx.EXPAND | wx.ALL, 2)
        tb = self.__create_toolbar(self)
        sizer.Add(tb, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.__create_hline(), 0, wx.EXPAND | wx.ALL, 2)

        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | wx.TE_PROCESS_ENTER | wx.TE_BESTWRAP | wx.TE_NO_VSCROLL
        self.__txtview = sppasTextCtrl(self, style=style, name="textctrl")
        self.__txtview.SetFont(wx.GetApp().settings.mono_text_font)
        self.__txtview.SetEditable(True)
        self.__txtview.SetModified(False)

        sizer.Add(self.__txtview, 1, wx.EXPAND | wx.LEFT, sppasPanel.fix_size(34))
        self.SetMinSize(wx.Size(sppasPanel.fix_size(320),
                                sppasPanel.fix_size(40)))

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_toolbar(self, parent):
        """Create the toolbar."""
        tb = sppasToolbar(parent, name="textview-toolbar")
        tb.set_focus_color(self._hicolor)
        tb.AddTitleText(self._filename,
                        color=self._hicolor,
                        name="tb-title-text")
        tb.AddButton("eye_hide", "Show/Hide")
        tb.AddButton("save", "Save")
        tb.AddButton("close", "Close")
        return tb

    # ------------------------------------------------------------------------

    def __create_hline(self):
        """Create a vertical line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, 2))
        line.SetSize(wx.Size(-1, 2))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(2)
        line.SetForegroundColour(self._hicolor)
        return line

    # -----------------------------------------------------------------------

    def _eval_height(self):
        """Return the optimal height of this panel."""
        tb_height = sppasPanel.fix_size(32)
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
            self.notify("close")

        elif event_name == "save":
            self.save()

        elif event_name == "eye_show":
            self.__txtview.Show(True)
            event_obj.SetImage('eye_hide')
            event_obj.SetName("eye_hide")
            self.__lines = self.__txtview.GetNumberOfLines()
            self.SetMinSize(wx.Size(-1, self._eval_height()))
            self.SetSize(wx.Size(-1, self._eval_height()))
            self.Layout()
            self.Refresh()
            self.notify("size")

        elif event_name == "eye_hide":
            self.__txtview.Show(False)
            event_obj.SetImage('eye_show')
            event_obj.SetName("eye_show")
            self.__lines = 1
            self.SetMinSize(wx.Size(-1, self._eval_height()))
            self.SetSize(wx.Size(-1, self._eval_height()))
            self.Layout()
            self.Refresh()
            self.notify("size")

        event.Skip()


# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(TextViewPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, filename=os.path.join(paths.samples, "COPYRIGHT.txt"))
        self.SetBackgroundColour(wx.Colour(128, 128, 128))
