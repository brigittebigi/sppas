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

    src.ui.phoenix.windows.popup.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

# ---------------------------------------------------------------------------


class LabelPopup(wx.PopupWindow):
    """A popup window to display a simple text.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, style, label):
        wx.PopupWindow.__init__(self, parent, style)
        pnl = wx.Panel(self, name="main_panel")

        try:
            s = wx.GetApp().settings
            self.SetFont(s.text_font)
        except AttributeError:
            self.InheritAttributes()

        pnl.SetBackgroundColour("YELLOW")
        pnl.SetForegroundColour("BLACK")

        border = LabelPopup.fix_size(10)

        st = wx.StaticText(pnl, -1, label, pos=(border//2, border//2))
        sz = st.GetBestSize()
        self.SetSize((sz.width + border, sz.height + border))
        pnl.SetSize((sz.width + border, sz.height + border))

        pnl.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
        pnl.Bind(wx.EVT_RIGHT_UP, self._on_mouse_up)
        st.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
        st.Bind(wx.EVT_RIGHT_UP, self._on_mouse_up)

        wx.CallAfter(self.Refresh)

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

    @property
    def _pnl(self):
        return self.FindWindow("main_panel")

    # -----------------------------------------------------------------------

    def _on_mouse_up(self, evt):
        self.Show(False)
        wx.CallAfter(self.Destroy)
