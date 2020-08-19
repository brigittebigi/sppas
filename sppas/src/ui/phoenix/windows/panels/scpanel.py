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

    src.ui.phoenix.windows.panels.scpanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.lib.scrolledpanel as sc

# ---------------------------------------------------------------------------


class sppasScrolledPanel(sc.ScrolledPanel):
    """A panel is a window on which controls are placed.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Possible constructors:

        - sppasScrolledPanel()
        - sppasScrolledPanel(parent, id=ID_ANY, pos=DefaultPosition,
            size=DefaultSize, style=TAB_TRAVERSAL, name=PanelNameStr)

    """

    def __init_(self, *args, **kw):
        super(sppasScrolledPanel, self).__init__(*args, **kw)
        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            pass

    # -----------------------------------------------------------------------

    def ShouldInheritColours(self):
        try:
            wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # -----------------------------------------------------------------------

    def InheritsBackgroundColour(self):
        try:
            wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # -----------------------------------------------------------------------

    def InheritsForegroundColour(self):
        try:
            wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        sc.ScrolledPanel.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        sc.ScrolledPanel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        sc.ScrolledPanel.SetFont(self, font)
        for c in self.GetChildren():
            c.SetFont(font)
        self.Layout()

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_size(value):
        """Return a proportional size value.

        :param value: (int)
        :returns: (int)

        """
        try:
            obj_size = int(float(value) * wx.GetApp().settings.size_coeff)
        except AttributeError:
            obj_size = int(value)
        return obj_size

    # -----------------------------------------------------------------------

    def get_font_height(self):
        """Return the height of the in-use font."""
        try:
            font = wx.GetApp().settings.text_font
        except AttributeError:
            font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))


