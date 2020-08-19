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

    src.ui.phoenix.windows.combobox.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from .panels import sppasPanel
from .buttons import BitmapButton
from .buttons import TextButton
from .buttonbox import sppasToggleBoxPanel

# ---------------------------------------------------------------------------


class PopupToggleBox(wx.Dialog):
    def __init__(self, parent, choices, name="popup"):
        """Constructor"""
        super(PopupToggleBox, self).__init__(
            parent,
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.RESIZE_BORDER | wx.SIMPLE_BORDER,
            name=name)

        tglbox = sppasToggleBoxPanel(self, choices=choices, majorDimension=1, name="togglebox")
        tglbox.SetVGap(0)
        tglbox.SetHGap(0)

        # Look&feel
        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            self.InheritAttributes()

        wx.CallAfter(self.Refresh)

# ---------------------------------------------------------------------------


class sppasComboBox(sppasPanel):
    """A combo box is a panel opening a list of mutually exclusive toggle buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The parent can bind wx.EVT_COMBOBOX.
    The parent can Bind the wx.EVT_COLLAPSIBLEPANE_CHANGED.

    """

    def __init__(self, parent, id=wx.ID_ANY, choices=(), pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="combobox"):
        """Create a sppasComboBox.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param choices: (list of str) List of choice strings
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        """
        super(sppasComboBox, self).__init__(
            parent, id, pos, size, style, name=name)

        self.popup = PopupToggleBox(self.GetTopLevelParent(), choices, name="popup")
        self._create_content(choices)

        # Look&feel
        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.popup.Bind(wx.EVT_RADIOBOX, self._process_selection_change)
        self.Bind(wx.EVT_BUTTON, self._process_rise)

    # ------------------------------------------------------------------------

    def _create_content(self, choices):
        """Create the content."""
        h = int(float(self.get_font_height()*1.5))
        if len(choices) == 0:
            label = ""
        else:
            label = str(choices[0])

        txtbtn = TextButton(self, label=label, name="txtbtn")
        txtbtn.SetAlign(wx.ALIGN_LEFT)
        txtbtn.SetMinSize(wx.Size(-1, h))
        txtbtn.Enable(False)
        arrowbtn = BitmapButton(self, name="arrow_combo")
        arrowbtn.SetMinSize(wx.Size(h, h))
        arrowbtn.SetFocusWidth(0)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(txtbtn, 1, wx.EXPAND | wx.ALL, sppasPanel.fix_size(4))
        sizer.Add(arrowbtn, 0, wx.EXPAND, 0)
        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    @property
    def _txtbtn(self):
        return self.FindWindow("txtbtn")

    # ------------------------------------------------------------------------

    def _process_selection_change(self, event):
        obj = event.GetEventObject()
        sel = obj.GetStringSelection()
        wx.LogDebug('* * * RadioBox Event by {:s} * * *'.format(obj.GetName()))
        wx.LogDebug(" --> selection index {:d}".format(obj.GetSelection()))
        wx.LogDebug(" --> selection {:s}".format(sel))
        self._txtbtn.SetLabel(sel)
        self.popup.Hide()

    def _process_rise(self, event):
        if self.popup.IsShown() is True:
            self.popup.Hide()
        else:
            (w, h) = self.GetClientSize()
            # Get the absolute position of this panel
            (x, y) = self.GetScreenPosition()
            # Show the togglebox at an appropriate place
            self.popup.SetSize(wx.Size(w, -1))
            self.popup.SetPosition(wx.Point(x, y+h))
            self.popup.Layout()
            self.popup.Show()

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelComboBox(wx.Panel):

    def __init__(self, parent):
        super(TestPanelComboBox, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test ComboBox")

        c1 = sppasComboBox(self,
                           choices=["bananas", "pears", "tomatoes", "apples", "pineapples"],
                           name="c1")
        c1.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        p2 = sppasPanel(self, size=(100, 100))
        p2.SetBackgroundColour(wx.RED)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(c1, 0, wx.ALL, 0)
        s.Add(p2, 0, wx.EXPAND, 0)
        self.SetSizer(s)
