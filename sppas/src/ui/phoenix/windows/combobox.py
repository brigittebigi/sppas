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

        sizer = wx.BoxSizer()

        tglbox = sppasToggleBoxPanel(self, choices=choices, majorDimension=1, name="togglebox")
        tglbox.SetVGap(0)
        tglbox.SetHGap(0)
        sizer.Add(tglbox, 1, wx.EXPAND | wx.LEFT, sppasPanel.fix_size(4))

        # Look&feel
        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.SetMinSize(tglbox.GetSize())
        self.SetSizerAndFit(sizer)
        wx.CallAfter(self.Refresh)

    @property
    def tglbox(self):
        return self.FindWindow("togglebox")

    # ------------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        wx.Dialog.SetForegroundColour(self, color)
        self.tglbox.SetForegroundColour(color)

    def SetForegroundColour(self, color):
        wx.Dialog.SetBackgroundColour(self, color)
        self.tglbox.SetBackgroundColour(color)

    def SetFont(self, font):
        wx.Dialog.SetFont(self, font)
        self.tglbox.SetFont(font)

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

    def SetBackgroundColour(self, color):
        wx.Panel.SetForegroundColour(self, color)
        self._txtbtn.SetBackgroundColour(color)
        self._arrowbtn.SetForegroundColour(color)

    def SetForegroundColour(self, color):
        wx.Panel.SetBackgroundColour(self, color)
        self._txtbtn.SetForegroundColour(color)
        self._arrowbtn.SetBackgroundColour(color)

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
        sizer.Add(txtbtn, 1, wx.EXPAND | wx.ALL, sppasPanel.fix_size(1))
        sizer.Add(arrowbtn, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, sppasPanel.fix_size(1))
        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    @property
    def _arrowbtn(self):
        return self.FindWindow("arrow_combo")

    # ------------------------------------------------------------------------

    @property
    def _txtbtn(self):
        return self.FindWindow("txtbtn")

    # ------------------------------------------------------------------------

    def GetSelection(self):
        return self.popup.tglbox.GetSelection()

    # ------------------------------------------------------------------------

    def SetSelection(self, idx=-1):
        """"""
        self.popup.tglbox.SetSelection(idx)
        s = self.popup.tglbox.GetStringSelection()
        self._txtbtn.SetLabel(s)

    # ------------------------------------------------------------------------

    def GetValue(self):
        return self.popup.tglbox.GetStringSelection()

    # ------------------------------------------------------------------------

    def GetItems(self):
        """Return the list of all string items."""
        return self.popup.tglbox.GetItems()

    # ------------------------------------------------------------------------

    def FindString(self, str):
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def _process_selection_change(self, event):
        obj = event.GetEventObject()
        sel = obj.GetStringSelection()
        wx.LogDebug('* * * RadioBox Event by {:s} * * *'.format(obj.GetName()))
        wx.LogDebug(" --> selection index {:d}".format(obj.GetSelection()))
        wx.LogDebug(" --> selection {:s}".format(sel))
        self._txtbtn.SetLabel(sel)
        self.popup.Hide()
        self.Notify()

    # ------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_COMBOBOX event to the listener (if any)."""
        evt = wx.PyCommandEvent(wx.wxEVT_COMMAND_COMBOBOX_SELECTED, self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

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
        c1.SetSelection(2)  # tomatoes should be selected

        c2 = sppasComboBox(self,
                           choices=["item "+str(i) for i in range(100)],
                           name="c2")
        c2.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        c3 = sppasComboBox(self,
                           choices=[],
                           name="c3")
        c3.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(c1, 0, wx.ALL, 2)
        s.Add(c2, 0, wx.ALL, 2)
        s.Add(c3, 0, wx.ALL, 2)
        self.SetSizer(s)

        self.Bind(wx.EVT_COMBOBOX, self._process_combobox)

    def _process_combobox(self, event):
        wx.LogMessage("ComboBox event received. Sender: {:s}. Selection: {:d}"
                      "".format(event.GetEventObject().GetName(), event.GetEventObject().GetSelection()))
