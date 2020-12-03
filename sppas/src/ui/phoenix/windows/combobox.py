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


class PopupToggleBox(wx.PopupWindow):
    """A dialog embedding a sppasToggleBoxPanel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The parent can bind wx.EVT_COMBOBOX.
    The sppasComboBox is not editable.

    """

    def __init__(self, parent, choices, name="popup"):
        """Constructor"""
        wx.PopupWindow.__init__(self, parent)

        sizer = wx.BoxSizer()
        tglbox = sppasToggleBoxPanel(self, choices=choices, majorDimension=1, name="togglebox")
        tglbox.SetVGap(0)
        tglbox.SetHGap(0)
        sizer.Add(tglbox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, sppasPanel.fix_size(2))

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

    # ------------------------------------------------------------------------
    
    @property
    def tglbox(self):
        return self.FindWindow("togglebox")

    # ------------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        wx.Dialog.SetBackgroundColour(self, color)
        self.tglbox.SetBackgroundColour(color)

    def SetForegroundColour(self, color):
        wx.Dialog.SetForegroundColour(self, color)
        self.tglbox.SetForegroundColour(color)

    def SetFont(self, font):
        wx.Dialog.SetFont(self, font)
        self.tglbox.SetFont(font)

    # ------------------------------------------------------------------------

    def UpdateSize(self):
        size = self.tglbox.GetSize()
        self.SetSize(size)

# ---------------------------------------------------------------------------


class sppasComboBox(sppasPanel):
    """A combo box is a panel opening a list of mutually exclusive toggle buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The parent can bind wx.EVT_COMBOBOX.
    The sppasComboBox is not editable.

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

        self._popup = PopupToggleBox(self.GetTopLevelParent(), choices, name="popup")
        self._create_content(choices)

        # Look&feel
        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            self.InheritAttributes()

        self._popup.Bind(wx.EVT_RADIOBOX, self._process_selection_change)
        self._popup.Bind(wx.EVT_MOUSE_EVENTS, self._process_mouse_event)
        self.Bind(wx.EVT_BUTTON, self._process_rise)

    # ------------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        wx.Panel.SetForegroundColour(self, color)
        self._txtbtn.SetBackgroundColour(color)
        self._arrowbtn.SetForegroundColour(color)
        self._popup.SetBackgroundColour(color)

    # ------------------------------------------------------------------------
    
    def SetForegroundColour(self, color):
        wx.Panel.SetBackgroundColour(self, color)
        self._txtbtn.SetForegroundColour(color)
        self._arrowbtn.SetBackgroundColour(color)
        self._popup.SetForegroundColour(color)

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
        txtbtn.SetFocusWidth(0)

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
    # Public methods to manage the combo box
    # ------------------------------------------------------------------------

    def GetSelection(self):
        """Return the item being selected or -1 if no item is selected."""
        return self._popup.tglbox.GetSelection()

    # ------------------------------------------------------------------------

    def SetSelection(self, idx=-1):
        """Set the selection to the given item.

        :param idx: (int) The string position to select, starting from zero.

        """
        self._popup.tglbox.SetSelection(idx)
        s = self._popup.tglbox.GetStringSelection()
        self._txtbtn.SetLabel(s)
        self._txtbtn.Refresh()

    # ------------------------------------------------------------------------

    def GetValue(self):
        return self._popup.tglbox.GetStringSelection()

    # ------------------------------------------------------------------------

    def GetString(self, idx):
        """Return the label of the item with the given index.

        :param idx: (int) The zero-based index.

        """
        items = self._popup.tglbox.GetItems()
        if 0 < len(items) < idx:
            return items[idx]        
        return ""

    # ------------------------------------------------------------------------

    def GetStringSelection(self):
        """Return the label of the selected item. """
        return self._popup.tglbox.GetStringSelection()

    # ------------------------------------------------------------------------

    def GetItems(self):
        """Return the list of all string items."""
        return self._popup.tglbox.GetItems()

    # ------------------------------------------------------------------------

    def FindString(self, string, case_sensitive=False):
        """Find an item whose label matches the given string.

        :param string: (str) String to find.
        :param case_sensitive: (bool) Whether search is case sensitive
        :return: (int) Index of the first item matching the string or -1
        
        """
        for i, label in enumerate(self._popup.tglbox.GetItems()):
            if case_sensitive is True and label == string:
                return i
            if case_sensitive is False and label.lower() == string.lower():
                return i
        return -1

    # ------------------------------------------------------------------------

    def IsListEmpty(self):
        """Return True if the list of combobox choices is empty."""
        return len(self._popup.tglbox.GetItems()) == 0

    # ------------------------------------------------------------------------

    def GetCount(self):
        """Return the number of items in the control."""
        return len(self._popup.tglbox.GetItems())

    # ------------------------------------------------------------------------

    def EnableItem(self, n, enable=True):
        """Enable or disable an individual item.

        :param n: (int) The zero-based item to enable or disable.
        :param enable: (bool) True to enable, False to disable.
        :returns: (bool)

        """
        return self._popup.tglbox.EnableItem(n, enable)

    # ------------------------------------------------------------------------

    def Append(self, string):
        """Append a new entry into the list."""
        idx = self._popup.tglbox.Append(string)
        self._popup.UpdateSize()
        return idx

    # ------------------------------------------------------------------------

    def Delete(self, n):
        """Remove entry at index n of the list."""
        self._popup.tglbox.Delete(n)
        self._popup.UpdateSize()

    # ------------------------------------------------------------------------

    def DeleteAll(self):
        self._popup.tglbox.DeleteAll()
        self._popup.UpdateSize()

    # ------------------------------------------------------------------------
    # Events management
    # ------------------------------------------------------------------------

    def _process_selection_change(self, event):
        obj = event.GetEventObject()
        sel = obj.GetStringSelection()
        self._txtbtn.SetLabel(sel)
        self._txtbtn.Refresh()
        self._popup.Hide()
        self.Notify()

    # ------------------------------------------------------------------------

    def _process_mouse_event(self, event):
        if event.Leaving():
            self._popup.Hide()
        event.Skip()

    # ------------------------------------------------------------------------

    def _process_rise(self, event):
        if self._popup.IsShown() is True:
            self._popup.Hide()
        else:
            (w, h) = self.GetClientSize()
            # Get the absolute position of this panel
            (x, y) = self.GetScreenPosition()
            # Show the togglebox at an appropriate place
            # SHOULD ESTIMATE IF ENOUGH ROOM AT BOTTOM AND DISPLAY AT TOP IF NOT...
            pw, ph = self._popup.tglbox.DoGetBestSize()
            self._popup.SetSize(wx.Size(w, ph))
            self._popup.SetPosition(wx.Point(x, y+h))
            self._popup.Layout()
            self._popup.Show()
            self._popup.SetFocus()
            self._popup.Raise()

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

        c3 = sppasComboBox(self, choices=[], name="c3")
        c3.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))

        c4 = sppasComboBox(self, choices=list(), name="c4")
        c4.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))
        c4.Append("** A 1")
        c4.Append("** A 2")
        c4.Append("** A 3")
        c4.Append("** A 4")
        c4.Delete(3)
        c4.Delete(1)
        c4.SetSelection(1)

        c5 = sppasComboBox(self, choices=list(), name="c5")
        c5.SetMinSize(wx.Size(sppasPanel.fix_size(80), -1))
        for i in range(5):
            c5.Append("Appended %d" % i)
        c5.SetSelection(1)
        for i in reversed(range(5)):
            c5.Delete(i)
        c5.SetSelection(-1)

        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(c1, 0, wx.ALL, 2)
        s.Add(c2, 0, wx.ALL, 2)
        s.Add(c3, 0, wx.ALL, 2)
        s.Add(c4, 0, wx.ALL, 2)
        s.Add(c5, 0, wx.ALL, 2)
        self.SetSizer(s)

        self.Bind(wx.EVT_COMBOBOX, self._process_combobox)

    # ------------------------------------------------------------------------

    def _process_combobox(self, event):
        wx.LogMessage("ComboBox event received. Sender: {:s}. Selection: {:d}"
                      "".format(event.GetEventObject().GetName(), event.GetEventObject().GetSelection()))
