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

from ..windows import sppasScrolledPanel
from ..windows import sppasTextCtrl

from .baseview import sppasBaseViewPanel

# ---------------------------------------------------------------------------


class TextViewPanel(sppasBaseViewPanel):
    """Display the content of a file into an editable TextCtrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The object this class is displaying is a list of lines.

    """

    def __init__(self, parent, filename, name="textview-panel"):
        self._object = list()
        super(TextViewPanel, self).__init__(parent, filename, name)

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self.GetPane().IsModified()

    # -----------------------------------------------------------------------

    def get_object(self):
        """Return the object created from the opened file.

        Notice that it corresponds to the initially loaded content.

        :return: (List of loaded lines)

        """
        return self._object

    # ------------------------------------------------------------------------

    def load_text(self):
        """Load the file content into an object.

        :raises: IOError, UnicodeDecodeError, ...

        """
        wx.LogMessage("Load text of file {:s}".format(self._filename))
        with codecs.open(self._filename, 'r', sg.__encoding__) as fp:
            self._object = fp.readlines()
        wx.LogMessage("Text loaded: {:d} lines.".format(len(self._object)))

    # -----------------------------------------------------------------------

    def save(self):
        """Save the displayed text into a file."""
        content = self.GetPane().GetValue()
        with codecs.open(self._filename, 'w', sg.__encoding__) as fp:
            fp.write(content)

        self.GetPane().SetModified(False)
        return True

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        self.AddButton("save")
        self.AddButton("backup")
        self.AddButton("close")
        self._create_child_panel()
        self.Collapse(True)

    # -----------------------------------------------------------------------

    def _create_child_panel(self):
        """Override. Create the child panel."""
        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | \
                wx.TE_PROCESS_ENTER | wx.TE_BESTWRAP | wx.TE_NO_VSCROLL
        txtview = sppasTextCtrl(self, style=style)
        txtview.SetFont(wx.GetApp().settings.mono_text_font)
        txtview.SetEditable(True)
        txtview.SetModified(False)
        self.SetPane(txtview)
        self.__set_text_content()

    # -----------------------------------------------------------------------

    def __set_text_content(self):
        txtview = self.GetPane()
        content = "".join(self._object)
        txtview.SetValue(content)

        # required under Windows
        txtview.SetStyle(0, len(content), txtview.GetDefaultStyle())

        # Search for the height of the text
        nblines = len(self._object) + 1
        view_height = float(self.get_line_height()) * 1.1 * nblines
        txtview.SetMinSize(wx.Size(sppasScrolledPanel.fix_size(420), view_height))
        txtview.SetModified(False)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of event.

        :param event: (wx.Event)

        """
        event_obj = event.GetButtonObj()
        event_name = event_obj.GetName()

        if event_name == "backup":
            self.__set_text_content()
            self.Layout()
            self.Refresh()

        else:
            sppasBaseViewPanel._process_event(self, event)

    # -----------------------------------------------------------------------

    def _eval_height(self):
        """Return the optimal height of the textctrl."""
        view_height = float(sppasBaseViewPanel.get_line_height()) \
                      * 1.3 \
                      * len(self._object)
        return int(view_height) + 6

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TestPanel-textview" )

        f0 = os.path.join(paths.samples, "COPYRIGHT.txt")
        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-salign.xra")
        p0 = TextViewPanel(self, f0)
        p1 = TextViewPanel(self, f1)
        p2 = TextViewPanel(self, f2)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p0)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p1)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p0, 0, wx.EXPAND)
        sizer.Add(p1, 0, wx.EXPAND)
        sizer.Add(p2, 0, wx.EXPAND)

        self.SetBackgroundColour(wx.Colour(28, 28, 28))
        self.SetForegroundColour(wx.Colour(228, 228, 228))

        self.SetSizer(sizer)
        # self.FitInside()
        self.SetAutoLayout(True)
        self.Layout()
        self.SetupScrolling(scroll_x=True, scroll_y=True)

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.Layout()
