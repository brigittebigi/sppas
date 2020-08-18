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

    src.ui.phoenix.windows.buttonbox.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from .buttons import RadioButton
from .buttons import ButtonEvent
from .panel import sppasPanel

# ---------------------------------------------------------------------------


class sppasRadioBoxPanel(sppasPanel):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 choices=[],
                 majorDimension=0,
                 style=wx.RA_SPECIFY_COLS,
                 name=wx.RadioBoxNameStr):
        super(sppasRadioBoxPanel, self).__init__(parent, id, pos, size, name=name)

        self.__buttons = list()
        self.__selection = 0
        self._create_content(style, choices, majorDimension)
        self._setup_events()
        self.Layout()

    # ------------------------------------------------------------------------

    def EnableItem(self, n, enable=True):
        """Enable or disable an individual button in the radiobox.

        :param n: (int) – The zero-based button to enable or disable.
        :param enable: (bool) – True to enable, False to disable.
        :returns: (bool)

        """
        if n > len(self.__buttons):
            return False
        # do not disable the selected button
        if n == self.__selection and enable is False:
            return False

        self.__buttons[n].Enable(enable)
        return True

    # ------------------------------------------------------------------------

    def FindString(self, string, bCase=False):
        """Find a button matching the given string.

        :param string: (string) – The string to find.
        :param bCase: (bool) – Should the search be case-sensitive?

        :returns: (int) the position if found, or -1 if not found.

        """
        found = -1
        for i, c in enumerate(self.__buttons):
            label = c.GetLabel()
            if bCase is False and label.lower() == string.lower():
                found = i
                break
            if bCase is True and label == string:
                found = i
                break
        return found

    # ------------------------------------------------------------------------

    def GetColumnCount(self):
        """Return the number of columns in the radiobox."""
        return self.GetSizer().GetEffectiveColsCount()

    # ------------------------------------------------------------------------

    def GetRowCount(self):
        """Return the number of rows in the radiobox."""
        return self.GetSizer().GetEffectiverowsCount()

    # ------------------------------------------------------------------------

    def GetCount(self):
        """Return the number of items in the control."""
        return len(self.__buttons)

    # ------------------------------------------------------------------------

    def GetSelection(self):
        """Return the index of the selected item or -1 if no item is selected.
    
        :returns: (int) The position of the current selection.
        
        """
        return self.__selection

    # ------------------------------------------------------------------------

    def SetSelection(self, n):
        """Set the selection to the given item.

        :param n: (int) – Index of the item

        """
        if n > len(self.__buttons):
            return
        # do not re-select the current one
        if self.__selection == n:
            return

        btn = self.__buttons[n]
        # do not select a disabled button
        if btn.IsEnabled() is True:
            # un-select the current selected button
            self.__buttons[self.__selection].SetValue(False)
            # select the expected one
            self.__selection = n
            btn.SetValue(True)

    # ------------------------------------------------------------------------

    def GetString(self, n):
        """Return the label of the item with the given index.

        :param n: (int) – The zero-based index.
        :returns: (str) The label of the item or an empty string if the position
        was invalid.

        """
        if n > len(self.__buttons):
            return ""
        return self.__buttons[n].GetLabel()

    # ------------------------------------------------------------------------

    def GetStringSelection(self):
        """Return the label of the selected item.

        :returns: (str) The label of the selected item

        """
        return self.__buttons[self.__selection].GetLabel()

    # ------------------------------------------------------------------------

    def GetItemLabel(self, n):
        """Return the text of the n'th item in the radio box.

        :param n: (int) – The zero-based index.

        """
        self.GetString(n)

    # ------------------------------------------------------------------------

    def IsItemEnabled(self, n):
        """Return True if the item is enabled or False if it was disabled using Enable.

        :param n: (int) – The zero-based index.
        :returns: (bool)

        """
        if n > len(self.__buttons):
            return False
        return self.__buttons[n].IsEnabled(n)

    # ------------------------------------------------------------------------

    def SetItemLabel(self, n, text):
        """Set the text of the n’th item in the radio box.

        :param n: (int) – The zero-based index.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def SetString(self, n, string):
        """Set the label for the given item.

        :param n: (int) – The zero-based item index.
        :param string: (string) – The label to set.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def ShowItem(self, item, show=True):
        """Show or hide individual buttons.

        :param item: (int) – The zero-based position of the button to show or hide.
        :param show: (bool) – True to show, False to hide.
        :returns: (bool) True if the item has been shown or hidden or False
        if nothing was done because it already was in the requested state.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def IsItemShown(self, n):
        """Return True if the item is currently shown or False if it was hidden using Show.

        :param n: (int) – The zero-based item index.
        :returns: (bool)

        """
        if n > len(self.__buttons):
            return False
        return self.__buttons[n].IsShown()

    # ------------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_RADIOBUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.EVT_RADIOBOX.typeId, self.GetId())
        evt.SetButtonObj(self.__buttons[self.__selection])
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self, style, choices, majorDimension):
        """Create the main content."""
        rows = len(choices)
        cols = 1
        if len(choices) > 1:
            if majorDimension > 0:
                if style == wx.RA_SPECIFY_COLS:
                    cols = majorDimension
                    rows = (len(choices)+1) // majorDimension
                elif style == wx.RA_SPECIFY_ROWS:
                    rows = majorDimension
                    cols = (len(choices)+1) // majorDimension

        grid = wx.GridBagSizer(rows, cols)
        if style == wx.RA_SPECIFY_COLS:
            for c in range(cols):
                for r in range(rows):
                    index = (c*rows)+r
                    if index < len(choices):
                        btn = RadioButton(self, label=choices[index], name="radiobutton_%d_%d" % (c, r))
                        btn.SetMinSize(wx.Size(-1, self.get_font_height()*2))
                        grid.Add(btn, pos=(r, c), flag=wx.EXPAND)
                        self.__buttons.append(btn)

        else:
            for r in range(rows):
                for c in range(cols):
                    index = (r*cols)+c
                    if index < len(choices):
                        btn = RadioButton(self, label=choices[index], name="radiobutton_%d_%d" % (r, c))
                        btn.SetMinSize(wx.Size(-1, self.get_font_height()*2))
                        grid.Add(btn, pos=(r, c), flag=wx.EXPAND)
                        self.__buttons.append(btn)

        for c in range(cols):
            grid.AddGrowableCol(c)

        for r in range(rows):
            grid.AddGrowableRow(r)

        self.__buttons[0].SetValue(True)
        self.SetMinSize(wx.Size(
            sppasPanel.fix_size(self.get_font_height()*rows), -1))
        self.SetSizer(grid)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user pressed a key of its keyboard
        # self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked (LeftDown - LeftUp) an action button
        self.Bind(wx.EVT_RADIOBUTTON, self._process_btn_event)

    # ------------------------------------------------------------------------

    def _process_btn_event(self, event):
        """Respond to a button event.

        :param event: (wx.Event)

        """
        evt_btn = event.GetButtonObj()
        new_selected_index = self.__buttons.index(evt_btn)
        self.SetSelection(new_selected_index)
        self.Notify()

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelRadioBox(wx.Panel):

    def __init__(self, parent):
        super(TestPanelRadioBox, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test RadioBox")

        rbc = sppasRadioBoxPanel(
            self,
            pos=(10, 10),
            size=wx.Size(200, 300),
            choices=["bananas", "pears", "tomatoes", "apples", "pineapples"],
            majorDimension=2,
            style=wx.RA_SPECIFY_COLS,
            name="radio_in_cols")
        rbc.Bind(wx.EVT_RADIOBOX, self.on_btn_event)
        # disable apples:
        rbc.EnableItem(3, False)
        # should do return False:
        # assert(rbc.EnableItem(50, True) is False), "Enable Item with index 50:"

        rbr = sppasRadioBoxPanel(
            self,
            pos=(220, 10),
            size=wx.Size(300, 200),
            choices=["bananas", "pears", "tomatoes", "apples", "pineapples"],
            majorDimension=2,
            style=wx.RA_SPECIFY_ROWS,
            name="radio_in_rows")
        rbr.Bind(wx.EVT_RADIOBOX, self.on_btn_event)
        # disable apples
        rbr.EnableItem(3, False)

    # -----------------------------------------------------------------------

    def on_btn_event(self, event):
        obj = event.GetEventObject()
        wx.LogDebug('* * * RadioBox Event by {:s} * * *'.format(obj.GetName()))
        wx.LogDebug(" --> selection {:d}".format(obj.GetSelection()))

# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test ButtonBox")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(TestPanelRadioBox(self), 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        sizer.Add(wx.StaticLine(self))

        self.SetSizer(sizer)
