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
from .buttons import ToggleButton
from .buttons import ButtonEvent
from .panels import sppasPanel, sppasScrolledPanel

# ---------------------------------------------------------------------------


class sppasRadioBoxPanel(sppasScrolledPanel):
    """A radio box is a list of mutually exclusive radio buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The parent can bind wx.EVT_RADIOBOX.

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 choices=(),
                 majorDimension=0,
                 style=wx.RA_SPECIFY_COLS,
                 name=wx.RadioBoxNameStr):
        super(sppasRadioBoxPanel, self).__init__(parent, id, pos, size, name=name)

        self._buttons = list()
        self.__selection = -1
        gap = sppasPanel.fix_size(2)
        self._major_dimension = majorDimension
        self._style = style
        self._create_content(choices, gap, gap)
        self._setup_events()

        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.Layout()

    # ------------------------------------------------------------------------

    def DoGetBestSize(self):
        if self.GetSizer() is None or len(self._buttons) == 0:
            # min enough values to provide warnings due to the scrollbars
            size = wx.Size(sppasPanel.fix_size(10), sppasPanel.fix_size(20))
        else:
            c = self.GetSizer().GetCols()
            r = self.GetSizer().GetRows()
            min_width = sppasPanel.fix_size(self.get_font_height() * c)
            expected_height = (r * int(float(self.get_font_height() * 1.8))) + (r * self.GetSizer().GetHGap())
            if c == 1:
                min_height = min(expected_height,
                    sppasPanel.fix_size(100)  # SHOULD BE DYNAMICALLY ESTIMATED
                    )
            else:
                min_height = expected_height

            size = wx.Size(min_width, min_height)

        return size

    # ------------------------------------------------------------------------

    def EnableItem(self, n, enable=True):
        """Enable or disable an individual button in the radiobox.

        :param n: (int) The zero-based button to enable or disable.
        :param enable: (bool) True to enable, False to disable.
        :returns: (bool)

        """
        if n < 0:
            return False
        if n > len(self._buttons):
            return False
        # do not disable the selected button
        if n == self.__selection and enable is False:
            return False

        self._buttons[n].Enable(enable)
        return True

    # ------------------------------------------------------------------------

    def FindString(self, string, bCase=False):
        """Find a button matching the given string.

        :param string: (string) – The string to find.
        :param bCase: (bool) – Should the search be case-sensitive?

        :returns: (int) the position if found, or -1 if not found.

        """
        found = -1
        for i, c in enumerate(self._buttons):
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
        return len(self._buttons)

    # ------------------------------------------------------------------------

    def GetSelection(self):
        """Return the index of the selected item or -1 if no item is selected.
    
        :returns: (int) The position of the current selection.
        
        """
        return self.__selection

    # ------------------------------------------------------------------------

    def SetSelection(self, n):
        """Set the selection to the given item.

        :param n: (int) – Index of the item or -1 to disable the current

        """
        if n > len(self._buttons):
            return

        if n >= 0:
            btn = self._buttons[n]
            # do not select a disabled button
            if btn.IsEnabled() is True:
                # un-select the current selected button
                if self.__selection not in (-1, n):
                    self._activate(self.__selection, False)
                # select the expected one
                self.__selection = n
                self._activate(n, True)
                btn.SetValue(True)
        else:
            # un-select the current selected button
            if self.__selection != -1:
                self._activate(self.__selection, False)
            self.__selection = -1

    # ------------------------------------------------------------------------

    def GetString(self, n):
        """Return the label of the item with the given index.

        :param n: (int) – The zero-based index.
        :returns: (str) The label of the item or an empty string if the position
        was invalid.

        """
        if n < 0:
            return ""
        if n > len(self._buttons):
            return ""
        return self._buttons[n].GetLabel()

    # ------------------------------------------------------------------------

    def GetStringSelection(self):
        """Return the label of the selected item.

        :returns: (str) The label of the selected item

        """
        if self.__selection >= 0:
            return self._buttons[self.__selection].GetLabel()
        return ""

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
        if n < 0:
            return False
        if n > len(self._buttons):
            return False
        return self._buttons[n].IsEnabled(n)

    # ------------------------------------------------------------------------

    def SetItemLabel(self, n, text):
        """Set the text of the n'th item in the radio box.

        :param n: (int) The zero-based index.

        """
        if n < 0:
            return False
        if n > len(self._buttons):
            return False
        self._buttons[n].SetLabel(text)
        self._buttons[n].Refresh()
        return True

    # ------------------------------------------------------------------------

    def SetString(self, n, string):
        """Set the label for the given item.

        :param n: (int) The zero-based item index.
        :param string: (string) The label to set.

        """
        return self.SetItemLabel(n, string)

    # ------------------------------------------------------------------------

    def ShowItem(self, item, show=True):
        """Show or hide individual buttons.

        :param item: (int) The zero-based position of the button to show or hide.
        :param show: (bool) True to show, False to hide.
        :return: (bool) True if the item has been shown or hidden or False
        if nothing was done because it already was in the requested state.

        """
        if item > len(self._buttons) or item < 0:
            return False
        btn = self._buttons[item]
        self.GetSizer().Show(btn, show)
        self.GetSizer().Layout()
        return True

    # ------------------------------------------------------------------------

    def IsItemShown(self, n):
        """Return True if the item is currently shown or False if it was hidden using Show.

        :param n: (int) The zero-based item index.
        :returns: (bool)

        """
        if n > len(self._buttons) or n < 0:
            return False
        return self._buttons[n].IsShown()

    # ------------------------------------------------------------------------

    def GetItems(self):
        """Return the list of choices (list of str)."""
        return [btn.GetLabel() for btn in self._buttons]

    # ------------------------------------------------------------------------

    def Notify(self):
        """Sends a wx.EVT_RADIOBUTTON event to the listener (if any)."""
        evt = ButtonEvent(wx.EVT_RADIOBOX.typeId, self.GetId())
        evt.SetButtonObj(self._buttons[self.__selection])
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    # ------------------------------------------------------------------------

    def SetVGap(self, value):
        self.GetSizer().SetVGap(value)

    # ------------------------------------------------------------------------

    def SetHGap(self, value):
        self.GetSizer().SetHGap(value)

    # ------------------------------------------------------------------------

    def Append(self, string):
        hgap = self.GetSizer().GetHGap()
        vgap = self.GetSizer().GetVGap()
        choices = self.GetItems()
        enabled = list()
        showed = list()
        for btn in self._buttons:
            enabled.append(btn.IsEnabled())
            showed.append(btn.IsShown())
            btn.Destroy()
        self._buttons = list()

        choices.append(string)
        enabled.append(True)
        showed.append(True)

        self._create_content(choices, hgap, vgap)
        for i, btn in enumerate(self._buttons):
            btn.Enable(enabled[i])
            self.ShowItem(i, show=showed[i])

        self.SetSelection(self.__selection)
        self.Layout()

        return len(self._buttons) - 1

    # ------------------------------------------------------------------------

    def Delete(self, n):
        hgap = self.GetSizer().GetHGap()
        vgap = self.GetSizer().GetVGap()
        choices = self.GetItems()
        choices.pop(n)
        self._buttons.pop(n)
        enabled = list()
        showed = list()
        if self.__selection == n:
            self.__selection = -1
        elif self.__selection > n:
            self.__selection -= 1
        for btn in self._buttons:
            enabled.append(btn.IsEnabled())
            showed.append(btn.IsShown())
            btn.Destroy()
        self._buttons = list()

        self._create_content(choices, hgap, vgap)
        for i, btn in enumerate(self._buttons):
            btn.Enable(enabled[i])
            self.ShowItem(i, show=showed[i])

        self.SetSelection(self.__selection)
        self.Layout()

    # ------------------------------------------------------------------------

    def get_rows_cols_counts(self, choices):
        """Return the number of rows and cols."""
        rows = 1
        cols = 1
        if len(choices) > 1:
            if self._major_dimension > 1:
                if self._style == wx.RA_SPECIFY_COLS:
                    cols = self._major_dimension
                    rows = (len(choices)+1) // self._major_dimension
                elif self._style == wx.RA_SPECIFY_ROWS:
                    rows = self._major_dimension
                    cols = (len(choices)+1) // self._major_dimension
            else:  # one dimension
                if self._style == wx.RA_SPECIFY_COLS:
                    cols = 1
                    rows = len(choices)
                elif self._style == wx.RA_SPECIFY_ROWS:
                    rows = 1
                    cols = len(choices)
        return rows, cols

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self, choices, hgap=0, vgap=0):
        """Create the main content."""
        rows, cols = self.get_rows_cols_counts(choices)

        grid = wx.GridBagSizer(vgap=vgap, hgap=hgap)
        if self._style == wx.RA_SPECIFY_COLS:
            for c in range(cols):
                for r in range(rows):
                    index = (c*rows)+r
                    if index < len(choices):
                        btn = self._create_button(label=choices[index],
                                                  name="button_%d_%d" % (c, r))
                        grid.Add(btn, pos=(r, c), flag=wx.EXPAND)
                        self._buttons.append(btn)

        else:
            for r in range(rows):
                for c in range(cols):
                    index = (r*cols)+c
                    if index < len(choices):
                        btn = self._create_button(label=choices[index],
                                                  name="button_%d_%d" % (r, c))
                        grid.Add(btn, pos=(r, c), flag=wx.EXPAND)
                        self._buttons.append(btn)

        for c in range(cols):
            grid.AddGrowableCol(c)

        for r in range(rows):
            grid.AddGrowableRow(r)

        if len(choices) > 0:
            self.SetSelection(0)
        self.SetSizer(grid)

    # -----------------------------------------------------------------------

    def _create_button(self, label, name):
        """Create the button to add into the box."""
        btn = RadioButton(self, label=label, name=name)
        btn.Enable(True)
        btn.SetValue(False)
        btn.SetMinSize(wx.Size(-1, self.get_font_height() * 2))
        return btn

    # ------------------------------------------------------------------------

    def _activate(self, n, value):
        """Check/Uncheck the n-th button."""
        btn = self._buttons[n]
        if btn.IsEnabled() is True:
            btn.SetValue(value)

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
        new_selected_index = self._buttons.index(evt_btn)
        self.SetSelection(new_selected_index)
        self.Notify()

# ----------------------------------------------------------------------------


class sppasToggleBoxPanel(sppasRadioBoxPanel):
    """A toggle box is a list of mutually exclusive toggle buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The parent can bind wx.EVT_RADIOBOX.

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 choices=[],
                 majorDimension=0,
                 style=wx.RA_SPECIFY_COLS,
                 name=wx.RadioBoxNameStr):
        super(sppasToggleBoxPanel, self).__init__(
            parent, id, pos, size, choices, majorDimension, style, name)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user pressed a key of its keyboard
        # self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked (LeftDown - LeftUp) an action button
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_btn_event)

    # -----------------------------------------------------------------------

    def _create_button(self, label, name):
        """Create the button to add into the box."""
        btn = ToggleButton(self, label=label, name=name)
        btn.SetImage(None)

        # Get the font height for the header
        h = self.get_font_height()

        btn.SetLabelPosition(wx.LEFT)
        btn.SetFocusStyle(wx.PENSTYLE_SOLID)
        btn.SetFocusWidth(h//4)
        btn.SetSpacing(sppasPanel.fix_size(h))
        btn.SetAlign(wx.ALIGN_LEFT)

        btn.Enable(True)
        btn.SetValue(False)
        btn.SetMinSize(wx.Size(-1, int(float(self.get_font_height()) * 1.8)))
        return btn

    # ------------------------------------------------------------------------

    def _activate(self, n, value):
        """Check/Uncheck the n-th button."""
        btn = self._buttons[n]
        if btn.IsEnabled() is True:
            btn.SetValue(value)
            if value is True:
                btn.SetImage("check_yes")
            else:
                btn.SetImage(None)

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
            majorDimension=1,
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

        tbr = sppasToggleBoxPanel(
            self, pos=(10, 350), size=wx.Size(400, 100),
            choices=["choice 1", "choice 2", "choice 3", "choice 4", "choice 5", "choice 6", "choice 7"],
            majorDimension=3,
            style=wx.RA_SPECIFY_ROWS,
            name="toogle_in_rows"
        )
        tbr.Bind(wx.EVT_RADIOBOX, self.on_btn_event)

        tbc = sppasToggleBoxPanel(
            self, pos=(550, 10), size=wx.Size(110, 200),
            choices=["choice 1", "choice 2", "choice 3", "choice 3--", "choice 4", "choice 5", "choice 6"],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
            name="toogle_in_cols"
        )
        tbc.SetVGap(0)
        tbc.SetHGap(0)
        tbc.EnableItem(3, False)
        tbc.Append("Append 1")
        tbc.Delete(2)
        tbc.Append("Append 2")
        tbc.SetItemLabel(1, "changed 2")
        tbc.Refresh()
        tbc.Bind(wx.EVT_RADIOBOX, self.on_btn_event)

    # -----------------------------------------------------------------------

    def on_btn_event(self, event):
        obj = event.GetEventObject()
        wx.LogDebug('* * * RadioBox Event by {:s} * * *'.format(obj.GetName()))
        wx.LogDebug(" --> selection index {:d}".format(obj.GetSelection()))
        wx.LogDebug(" --> selection {:s}".format(obj.GetStringSelection()))
