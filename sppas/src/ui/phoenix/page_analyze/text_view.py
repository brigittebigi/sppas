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
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import logging
import wx
import codecs

from sppas import sg
from ..windows import sppasScrolledPanel
from ..windows import sppasPanel
from ..windows import sppasTextCtrl

# ----------------------------------------------------------------------------

BRACKET_COLOUR = wx.Colour(196, 48, 48)
PARENTHESIS_COLOUR = wx.Colour(48, 196, 48)
BRACES_COLOUR = wx.Colour(48, 48, 196)
TAG_COLOUR = wx.Colour(48, 196, 196)

# ----------------------------------------------------------------------------


class TextViewPanel(sppasPanel):
    """Display the content of one file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="textview", filename=None):
        super(TextViewPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The file this panel is displaying
        self.__filename = filename

        self._create_content()
        # self._setup_events()

        if filename is not None:
            self.load_text()

        self.Layout()

    # -----------------------------------------------------------------------

    def load_text(self):
        """ """
        try:
            with codecs.open(self.__filename, 'r', sg.__encoding__) as fp:
                lines = fp.readlines()
        except Exception as e:
            lines = ["The file can't be loaded.",
                     "Error is: %s" % str(e)]

        content = "".join(lines)
        txtctrl = self.FindWindow("textctrl")
        txtctrl.SetValue(content)

        # required under Windows
        txtctrl.SetStyle(0, len(content), txtctrl.GetDefaultStyle())

        # Highlight some special chars
        self.__highlight(txtctrl, content, "(", PARENTHESIS_COLOUR)
        self.__highlight(txtctrl, content, ")", PARENTHESIS_COLOUR)
        self.__highlight(txtctrl, content, "[", BRACKET_COLOUR)
        self.__highlight(txtctrl, content, "]", BRACKET_COLOUR)
        self.__highlight(txtctrl, content, "{", BRACES_COLOUR)
        self.__highlight(txtctrl, content, "}", BRACES_COLOUR)
        self.__highlight(txtctrl, content, "<", TAG_COLOUR)
        self.__highlight(txtctrl, content, ">", TAG_COLOUR)

    # -----------------------------------------------------------------------

    @staticmethod
    def __highlight(txtctrl, content, characters, color):
        i = content.find(characters, 0)
        while i != -1:
            print(i)
            txtctrl.SetStyle(i, i + 1, wx.TextAttr(color))
            i = content.find(characters, i+1)

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_AUTO_URL | wx.NO_BORDER
        txtctrl = sppasTextCtrl(self, style=style, name="textctrl")
        txtctrl.SetFont(wx.GetApp().settings.mono_text_font)

        sizer = wx.BoxSizer()
        sizer.Add(txtctrl, 1, wx.EXPAND)
        self.SetSizer(sizer)
        # self.SetMinSize(wx.Size(sppasScrolledPanel.fix_size(512),
        #                         sppasScrolledPanel.fix_size(512)))

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(TextViewPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, filename=os.path.abspath(__file__))
