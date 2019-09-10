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

"""

import os
import codecs
import wx

from sppas import sg
from sppas import paths

from ..windows import sppasPanel
from ..windows import CheckButton
from ..windows import sppasTextCtrl

from .baseview import sppasBaseViewPanel

# ----------------------------------------------------------------------------

BRACKET_COLOUR = wx.Colour(196, 48, 48)
PARENTHESIS_COLOUR = wx.Colour(48, 196, 48)
BRACES_COLOUR = wx.Colour(48, 48, 196)
TAG_COLOUR = wx.Colour(48, 196, 196)

# ----------------------------------------------------------------------------


class TextViewPanel(sppasBaseViewPanel):
    """Display the content of a file into a TextCtrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="textview", filename=""):
        super(TextViewPanel, self).__init__(parent, name, filename)

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
        line_height = float(self.get_line_height()) * 1.3  # line spacing
        height = sppasPanel.fix_size(32) + int(line_height*len(lines)) + 4
        self.SetMinSize(wx.Size(sppasPanel.fix_size(320), height))

        self.__txtview.SetModified(False)

    # -----------------------------------------------------------------------

    def save(self):
        """Save the displayed text into a file."""
        content = self.__txtview.GetValue()
        with codecs.open(self._filename, 'w', sg.__encoding__) as fp:
            fp.write(content)
            # fp.close()

        self.__txtview.SetModified(False)
        return True

    # -----------------------------------------------------------------------

    def is_checked(self):
        """Return True if this file is checked."""
        return self.FindWindow("checkbtn").GetValue()

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    @staticmethod
    def __highlight(txtctrl, content, characters, color):
        i = content.find(characters, 0)
        while i != -1:
            print(i)
            txtctrl.SetStyle(i, i + 1, wx.TextAttr(color))
            i = content.find(characters, i+1)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        btn = CheckButton(self, label=self._filename, name="checkbtn")
        btn.SetSpacing(sppasPanel.fix_size(12))
        btn.SetMinSize(wx.Size(-1, sppasPanel.fix_size(32)))
        btn.SetSize(wx.Size(-1, sppasPanel.fix_size(32)))
        btn.SetValue(True)
        self.__set_active_btn_style(btn)
        sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 2)

        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | wx.TE_PROCESS_ENTER | wx.TE_BESTWRAP | wx.TE_NO_VSCROLL
        self.__txtview = sppasTextCtrl(self, style=style, name="textctrl")
        self.__txtview.SetFont(wx.GetApp().settings.mono_text_font)
        self.__txtview.SetEditable(True)
        self.__txtview.SetModified(False)

        sizer.Add(self.__txtview, 1, wx.EXPAND | wx.LEFT, sppasPanel.fix_size(34))
        self.SetMinSize(wx.Size(sppasPanel.fix_size(320),
                                sppasPanel.fix_size(34)))

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __set_normal_btn_style(self, button):
        """Set a normal style to a button."""
        button.BorderWidth = 0
        button.BorderColour = self.GetForegroundColour()
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = self._hicolor
        button.SetForegroundColour(self._hicolor)

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set a special style to the button."""
        button.BorderWidth = 0
        button.BorderColour = self._hicolor
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = self.GetForegroundColour()
        button.SetForegroundColour(self._hicolor)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_BUTTON, self.__process_checked)

    # -----------------------------------------------------------------------

    def __process_checked(self, event):
        """Process a checkbox event.

        Skip the event in order to allow the parent to handle it: it's to
        update the other windows with data of the new selected workspace.

        :param event: (wx.Event)

        """
        # the button we want to switch on
        btn = event.GetButtonObj()
        state = btn.GetValue()
        if state is True:
            self.__set_active_btn_style(btn)
            self.__txtview.Show()
        else:
            self.__set_normal_btn_style(btn)
            self.__txtview.Hide()
        btn.SetValue(state)
        self.Refresh()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(TextViewPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, filename=os.path.join(paths.samples, "COPYRIGHT.txt"))
        self.SetBackgroundColour(wx.Colour(128, 128, 128))
