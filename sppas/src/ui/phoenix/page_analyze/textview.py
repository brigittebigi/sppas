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

import logging
import os
import codecs
import wx

from sppas import sg
from sppas import paths

from ..windows import sppasPanel
from ..windows import CheckButton
from ..windows import sppasTextCtrl

# ----------------------------------------------------------------------------

BRACKET_COLOUR = wx.Colour(196, 48, 48)
PARENTHESIS_COLOUR = wx.Colour(48, 196, 48)
BRACES_COLOUR = wx.Colour(48, 48, 196)
TAG_COLOUR = wx.Colour(48, 196, 196)

# ----------------------------------------------------------------------------


class TextViewPanel(sppasPanel):
    """Display the content of a file into a TextCtrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="baseview", filename=""):
        super(TextViewPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The file this panel is displaying
        self.__filename = filename
        self.__hicolor = self.GetForegroundColour()
        self.__txtview = None
        self.__modified = False

        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.mono_text_font)

        if filename is not None:
            self.load_text()
        else:
            self.SetMinSize(wx.Size(sppasPanel.fix_size(320),
                                    sppasPanel.fix_size(32)))

        self.Layout()

    # -----------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self.__modified

    # -----------------------------------------------------------------------

    def load_text(self):
        """Load the file and display it."""
        # TODO: progress bar while loading
        try:
            with codecs.open(self.__filename, 'r', sg.__encoding__) as fp:
                lines = fp.readlines()
        except Exception as e:
            lines = ["The file can't be loaded.",
                     "Error is: %s" % str(e)]

        content = "".join(lines)
        txtctrl = self.FindWindow("textctrl")
        txtctrl.SetValue(content)
        self.__modified = False

        # required under Windows
        txtctrl.SetStyle(0, len(content), txtctrl.GetDefaultStyle())
        
        # Search the height of the text
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        line_height = int(float(font.GetPixelSize()[1]) * 1.5)  # line spacing
        self.SetMinSize(wx.Size(sppasPanel.fix_size(320),
                                line_height*len(lines)))

    # -----------------------------------------------------------------------

    def save_text(self):
        """Save the displayed text into a file."""
        txtctrl = self.FindWindow("textctrl")
        content = txtctrl.GetValue()
        try:
            with codecs.open(self.__filename, 'w', sg.__encoding__) as fp:
                fp.write(content)
        except Exception as e:
            wx.LogError(str(e))
            raise

        self.__modified = False

    # -----------------------------------------------------------------------

    def is_checked(self):
        """Return True if this file is checked."""
        return self.FindWindow("checkbtn").GetValue()

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self.__hicolor = color
        for child in self.GetChildren():
            if isinstance(child, CheckButton):
                if child.GetValue() is False:
                    child.FocusColour = self.__hicolor

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

        btn = CheckButton(self, label=self.__filename, name="checkbtn")
        btn.SetSpacing(sppasPanel.fix_size(12))
        btn.SetMinSize(wx.Size(-1, sppasPanel.fix_size(32)))
        btn.SetSize(wx.Size(-1, sppasPanel.fix_size(32)))
        btn.SetValue(True)
        self.__set_active_btn_style(btn)
        sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 2)

        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | wx.TE_PROCESS_ENTER | wx.TE_BESTWRAP | wx.TE_NO_VSCROLL
        self.__txtview = sppasTextCtrl(self, style=style, name="textctrl")
        self.__txtview.SetFont(wx.GetApp().settings.mono_text_font)

        sizer.Add(self.__txtview, 1, wx.EXPAND | wx.LEFT, sppasPanel.fix_size(34))

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __set_normal_btn_style(self, button):
        """Set a normal style to a button."""
        button.BorderWidth = 0
        button.BorderColour = self.GetForegroundColour()
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = self.__hicolor
        button.SetForegroundColour(self.__hicolor)

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set a special style to the button."""
        button.BorderWidth = 0
        button.BorderColour = self.__hicolor
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = self.GetForegroundColour()
        button.SetForegroundColour(self.__hicolor)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_BUTTON, self.__process_checked)
        self.Bind(wx.EVT_TEXT, self.__process_text_modified)

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

    # -----------------------------------------------------------------------

    def __process_text_modified(self, event):
        """Process a text enter event.
        
        We then suppose the text was modified.
        
        :param event: (wx.Event)

        """
        self.__modified = True

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(TextViewPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, filename=os.path.join(paths.samples, "COPYRIGHT.txt"))
        self.SetBackgroundColour(wx.Colour(128, 128, 128))
