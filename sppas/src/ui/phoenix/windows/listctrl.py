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

    src.ui.phoenix.windows.listctrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import logging

# ---------------------------------------------------------------------------


class sppasListCtrl(wx.ListCtrl):
    """A ListCtrl with the same look&feel on each platform.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The default is a multiple selection of items. Use wx.LC_SINGLE_SEL style
    for single selection with wx.LC_REPORT style.

    """

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER | wx.LC_REPORT,
                 validator=wx.DefaultValidator, name="listctrl"):
        """Initialize a new ListCtrl instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param validator: Window validator.
        :param name:      Window name.

        """
        super(sppasListCtrl, self).__init__(
            parent, id, pos, size, style, validator, name)

        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetTextColour(settings.fg_color)
            self.SetFont(settings.text_font)
            # Attributes of the header are not set: Not implemented by wx.ListCtrl.
        except AttributeError:
            self.InheritAttributes()

        # List of selected items
        self._selected = list()

        # Bind some events to manage properly the list of selected items
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self)

    # ---------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        wx.ListCtrl.SetBackgroundColour(self, colour)
        if not self.GetWindowStyleFlag() & wx.LC_HRULES:
            self.RecolorizeBackground(-1)

    # ---------------------------------------------------------------------

    def RecolorizeBackground(self, index=-1):
        """Set background color of items.

        :param index: (int) Item to set the bg color. -1 to set all items.

        """
        bg = self.GetBackgroundColour()
        r, g, b, a = bg.Red(), bg.Green(), bg.Blue(), bg.Alpha()
        if (r + g + b) > 384:
            alt_bg = wx.Colour(r, g, b, a).ChangeLightness(80)
        else:
            alt_bg = wx.Colour(r, g, b, a).ChangeLightness(110)

        if index == -1:
            for i in range(self.GetItemCount()):
                if i % 2:
                    self.SetItemBackgroundColour(i, bg)
                else:
                    self.SetItemBackgroundColour(i, alt_bg)
        else:
            if index % 2:
                self.SetItemBackgroundColour(index, bg)
            else:
                self.SetItemBackgroundColour(index, alt_bg)

    # -----------------------------------------------------------------------

    def InsertItem(self, index, label):
        """Override. Create a row and insert label.

        Create a row.
        Shift the selection of items if necessary.

        """
        sel = False
        if self.GetItemCount() == 0:
            sel = True
        idx = wx.ListCtrl.InsertItem(self, index, label)

        if sel is False:
            if index < self.GetItemCount():
                for i in range(len(self._selected)):
                    if self._selected[i] >= index:
                        self._selected[i] = self._selected[i] + 1
        else:
            # de-select the first item. Under MacOS, the first item
            # is systematically selected but not under the other platforms.
            self.Select(0, on=0)

        if not self.GetWindowStyleFlag() & wx.LC_HRULES:
            for i in range(index, self.GetItemCount()):
                self.RecolorizeBackground(i)

        return idx

    # -----------------------------------------------------------------------

    def SetItem(self, index, col, label, imageId=-1):
        """Override. Set the string of an item.

        The column number must be changed to be efficient; and alternate
        background colors (just for the list to be easier to read).

        """
        wx.ListCtrl.SetItem(self, index, col, label, imageId)
        if not self.GetWindowStyleFlag() & wx.LC_HRULES:
            self.RecolorizeBackground(index)

    # ---------------------------------------------------------------------

    def DeleteItem(self, index):
        """Override.

        Delete an item in the list. Must be overridden to also remove it of the
        selected list (if appropriate) and update selected item indexes.

        """
        if index in self._selected:
            self._selected.remove(index)

        for i in range(len(self._selected)):
            if self._selected[i] >= index:
                self._selected[i] = self._selected[i] - 1

        wx.ListCtrl.DeleteItem(self, index)

        if not self.GetWindowStyleFlag() & wx.LC_HRULES:
            for i in range(index, self.GetItemCount()):
                self.RecolorizeBackground(index)

    # ---------------------------------------------------------------------

    def GetFirstSelected(self, *args):
        """Returns the first selected item, or -1 when none is selected.

        :return: (int) -1 if no item selected

        """
        if len(self._selected) == 0:
            return -1
        return self._selected[0]

    # ---------------------------------------------------------------------

    def GetNextSelected(self, item):
        """Override.

        """
        s = sorted(self._selected)
        i = self.GetNextItem(item)
        while i != -1:
            if i in s:
                return i
            i = self.GetNextItem(i)
        return -1

    # ---------------------------------------------------------------------

    def GetSelectedItemCount(self):
        """Override.

        """
        return len(self._selected)

    # ---------------------------------------------------------------------

    def IsSelected(self, index):
        """Override. Return True if the item is checked."""
        return index in self._selected

    # ---------------------------------------------------------------------

    def Select(self, idx, on=1):
        """Override. Selects/deselects an item.

        Highlight the selected item with a Bigger & Bold font (the native
        system can't be disabled and is different on each system).

        :param idx: (int) Index of an annotation/item in the tier/list
        :param on: (int/bool) 0 to deselect, 1 to select

        """
        assert 0 <= idx < self.GetItemCount()

        font = self.GetFont()
        # if single selection, de-select current item
        # (except if it is the asked one).
        if on == 1 and self.HasFlag(wx.LC_SINGLE_SEL) and len(self._selected) > 0:
            i = self._selected[0]
            if i != idx:
                self._selected = list()
                self.SetItemFont(i, font)
                # Create the event
                # evt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_ITEM_DESELECTED)
                # evt.SetId(self.GetId())
                # evt.SetIndex(i)
                # evt.SetItem(self.GetItem(i))
                # Post the event
                # wx.PostEvent(self.GetParent(), evt)

        if on == 0:
            # De-select the given index
            if idx in self._selected:
                self._selected.remove(idx)
                self.SetItemFont(idx, font)
        else:
            # Select the given index
            if idx not in self._selected:
                self._selected.append(idx)
            bold = wx.Font(int(float(font.GetPointSize())*1.2),
                           font.GetFamily(),
                           font.GetStyle(),
                           wx.FONTWEIGHT_BOLD,  # weight,
                           underline=False,
                           faceName=font.GetFaceName(),
                           encoding=wx.FONTENCODING_SYSTEM)
            self.SetItemFont(idx, bold)

    # ---------------------------------------------------------------------
    # Callbacks
    # ---------------------------------------------------------------------

    def OnItemSelected(self, evt):
        """Callback.

        """
        item = evt.GetItem()
        item_index = item.GetId()

        # cancel the selection managed by wx.ListCtrl
        wx.ListCtrl.Select(self, item_index, on=0)
        # manage our own selection
        self.Select(item_index, on=1)

        evt.Skip()

    # ---------------------------------------------------------------------

    def OnItemDeselected(self, evt):
        """Callback.

        The item index is the selected one.

        """
        item = evt.GetItem()
        item_index = item.GetId()

        if item_index in self._selected:
            wx.ListCtrl.Select(self, item_index, on=0)
            self.Select(item_index, on=0)
            evt.Skip()
        else:
            # send the event with the de-selected item,
            # and not the selected one
            if self.HasFlag(wx.LC_SINGLE_SEL) and len(self._selected) > 0:
                i = self._selected[0]
                if i != item_index:
                    evt.SetIndex(i)
                    evt.SetItem(self.GetItem(i))
                    evt.Skip()

# ---------------------------------------------------------------------------


class LineListCtrl(sppasListCtrl):
    """A ListCtrl with line numbers in the first column.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER | wx.LC_REPORT,
                 validator=wx.DefaultValidator, name="LineListCtrl"):
        """Initialize a new ListCtrl instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param validator: Window validator.
        :param name:      Window name.

        """
        super(LineListCtrl, self).__init__(
            parent, id, pos, size, style, validator, name)

    # -----------------------------------------------------------------------
    # Override methods of wx.ListCtrl
    # -----------------------------------------------------------------------

    def InsertColumn(self, colnum, colname):
        """Override. Insert a new column.

        1. create a column with the line number if we create a column
           for the first time,
        2. create the expected column

        """
        if colnum == 0:
            # insert a first column, with whitespace
            sppasListCtrl.InsertColumn(self, 0, " "*16, wx.LIST_FORMAT_CENTRE)

        sppasListCtrl.InsertColumn(self, colnum+1, colname)

    # -----------------------------------------------------------------------

    def InsertItem(self, index, label):
        """Override. Create a row and insert label.

        Create a row, add the line number, add content of the first column.
        Shift the selection of items if necessary.

        """
        idx = sppasListCtrl.InsertItem(self, index, self._num_to_str(index+1))
        item = self.GetItem(index, 0)
        item.SetAlign(wx.LIST_FORMAT_CENTER)
        #item.SetMask(item.GetMask() | wx.LIST_MASK_FORMAT)

        # we want to add somewhere in the list (and not append)...
        # shift the line numbers items (for items that are after the new one)
        for i in range(index, self.GetItemCount()):
            sppasListCtrl.SetItem(self, i, 0, self._num_to_str(i+1))

        sppasListCtrl.SetItem(self, index, 1, label)
        return idx

    # -----------------------------------------------------------------------

    def SetColumnWidth(self, col, width):
        """Override. Fix column width.

        Fix also the first column.

        """
        sppasListCtrl.SetColumnWidth(self, 0, wx.LIST_AUTOSIZE_USEHEADER)
        sppasListCtrl.SetColumnWidth(self, col+1, width)

    # -----------------------------------------------------------------------

    def SetItem(self, index, col, label, imageId=-1):
        """Override. Set the string of an item.

        The column number must be changed to be efficient; and alternate
        background colors (just for the list to be easier to read).

        """
        sppasListCtrl.SetItem(self, index, col+1, label, imageId)

    # -----------------------------------------------------------------------

    def DeleteItem(self, index):
        """Override. Delete an item in the list.

        It must be overridden to update line numbers.

        """
        # sppasListCtrl.DeleteItem(self, index)
        sppasListCtrl.DeleteItem(self, index)
        for i in range(index, self.GetItemCount()):
            self.SetItem(i, 0, self._num_to_str(i+1))

    # -----------------------------------------------------------------------

    @staticmethod
    def _num_to_str(num):
        return " -- " + str(num) + " -- "

# ---------------------------------------------------------------------------
# Test panel (should be extended to test more functions)
# ---------------------------------------------------------------------------


musicdata = {
    1: ("Bad English", "The Price Of Love", "Rock"),
    2: ("DNA featuring Suzanne Vega", "Tom's Diner", "Rock"),
    3: ("George Michael", "Praying For Time", "Rock"),
    4: ("Gloria Estefan", "Here We Are", "Rock"),
    5: ("Linda Ronstadt", "Don't Know Much", "Rock"),
    6: ("Michael Bolton", "How Am I Supposed To Live Without You", "Blues"),
    7: ("Paul Young", "Oh Girl", "Rock"),
    8: ("Paula Abdul", "Opposites Attract", "Rock"),
    9: ("Richard Marx", "Should've Known Better", "Rock"),
    10: ("Rod Stewart", "Forever Young", "Rock"),
    11: ("Roxette", "Dangerous", "Rock"),
    12: ("Sheena Easton", "The Lover In Me", "Rock"),
    13: ("Sinead O'Connor", "Nothing Compares 2 U", "Rock"),
    14: ("Stevie B.", "Because I Love You", "Rock"),
    15: ("Taylor Dayne", "Love Will Lead You Back", "Rock"),
    16: ("The Bangles", "Eternal Flame", "Rock"),
    17: ("Wilson Phillips", "Release Me", "Rock"),
    18: ("Billy Joel", "Blonde Over Blue", "Rock"),
    19: ("Billy Joel", "Famous Last Words", "Rock"),
    20: ("Janet Jackson", "State Of The World", "Rock"),
    21: ("Janet Jackson", "The Knowledge", "Rock"),
    22: ("Spyro Gyra", "End of Romanticism", "Jazz"),
    23: ("Spyro Gyra", "Heliopolis", "Jazz"),
    24: ("Spyro Gyra", "Jubilee", "Jazz"),
    25: ("Spyro Gyra", "Little Linda", "Jazz"),
    26: ("Spyro Gyra", "Morning Dance", "Jazz"),
    27: ("Spyro Gyra", "Song for Lorraine", "Jazz"),
    28: ("Yes", "Owner Of A Lonely Heart", "Rock"),
    29: ("Yes", "Rhythm Of Love", "Rock"),
    30: ("Billy Joel", "Lullabye (Goodnight, My Angel)", "Rock"),
    31: ("Billy Joel", "The River Of Dreams", "Rock"),
    32: ("Billy Joel", "Two Thousand Years", "Rock"),
    33: ("Janet Jackson", "Alright", "Rock"),
    34: ("Janet Jackson", "Black Cat", "Rock"),
    35: ("Janet Jackson", "Come Back To Me", "Rock"),
    36: ("Janet Jackson", "Escapade", "Rock"),
    37: ("Janet Jackson", "Love Will Never Do (Without You)", "Rock"),
    38: ("Janet Jackson", "Miss You Much", "Rock"),
    39: ("Janet Jackson", "Rhythm Nation", "Rock"),
    40: ("Cusco", "Dream Catcher", "New Age"),
    41: ("Cusco", "Geronimos Laughter", "New Age"),
    42: ("Cusco", "Ghost Dance", "New Age"),
    43: ("Blue Man Group", "Drumbone", "New Age"),
    44: ("Blue Man Group", "Endless Column", "New Age"),
    45: ("Blue Man Group", "Klein Mandelbrot", "New Age"),
    46: ("Kenny G", "Silhouette", "Jazz"),
    47: ("Sade", "Smooth Operator", "Jazz"),
    48: ("David Arkenstone", "Papillon (On The Wings Of The Butterfly)", "New Age"),
    49: ("David Arkenstone", "Stepping Stars", "New Age"),
    50: ("David Arkenstone", "Carnation Lily Lily Rose", "New Age"),
    51: ("David Lanz", "Behind The Waterfall", "New Age"),
    52: ("David Lanz", "Cristofori's Dream", "New Age"),
    53: ("David Lanz", "Heartsounds", "New Age"),
    54: ("David Lanz", "Leaves on the Seine", "New Age"),
}

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="test_panel")
        listctrl = LineListCtrl(self,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
            name="listctrl")

        # The simplest way to create columns
        listctrl.InsertColumn(0, "Artist")
        listctrl.InsertColumn(1, "Title")
        listctrl.InsertColumn(2, "Genre")

        # Fill rows
        items = musicdata.items()
        for key, data in items:
            idx = listctrl.InsertItem(listctrl.GetItemCount(), data[0])
            listctrl.SetItem(idx, 1, data[1])
            listctrl.SetItem(idx, 2, data[2])
            # self.SetItemData(idx, key)

        # Adjust columns width
        listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        listctrl.SetColumnWidth(2, 100)

        # show how to select an item with events (like if we clicked on it)
        listctrl.SetItemState(5, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        s = wx.BoxSizer()
        s.Add(listctrl, 1, wx.EXPAND)
        self.SetSizer(s)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_deselected_item)
        listctrl.Bind(wx.EVT_KEY_UP, self._on_char)
        listctrl.SetForegroundColour(wx.Colour(25, 35, 45))
        listctrl.SetBackgroundColour(wx.Colour(225, 235, 245))

    def _on_selected_item(self, evt):
        logging.debug("Parent received selected item event. Index {}"
                      "".format(evt.GetIndex()))

    def _on_deselected_item(self, evt):
        logging.debug("Parent received de-selected item event. Index {}"
                      "".format(evt.GetIndex()))

    def _on_char(self, evt):
        kc = evt.GetKeyCode()
        wx.LogMessage(str(kc))
        char = chr(kc)
        if kc == 127:
            lst = self.FindWindow("listctrl")
            selected = lst.GetFirstSelected()
            if selected != -1:
                lst.DeleteItem(selected)
