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
import wx.lib.mixins.listctrl as listmix
import logging
import operator

from ..tools import sppasSwissKnife
from .image import ColorizeImage

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

    Known bug of wx.ListCtrl:

    - If the list is defined as a page of a wx.Notebook, under Windows only,
      DeleteItem() returns the following error message:
      listctrl.cpp(2614) in wxListCtrl::MSWOnNotify(): invalid internal data pointer?
      A solution is to use a simplebook, a choicebook, a listbook or a
      toolbook instead!
    - Items can't be edited. The events (begin/end edit label) are never sent.
      The wxDemo "ListCtrl_edit" does not work, clicking or double clicking
      on items does.... nothing.

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
        if style & wx.LC_EDIT_LABELS:
            style &= ~wx.LC_EDIT_LABELS

        super(sppasListCtrl, self).__init__(
            parent, id, pos, size, style, validator, name)

        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetTextColour(settings.fg_color)
            self.SetFont(settings.text_font)
            self._bg_color = settings.bg_color
            # Attributes of the header are not set: Not implemented by wx.ListCtrl.
        except AttributeError:
            self.InheritAttributes()
            self._bg_color = self.GetParent().GetBackgroundColour()

        # List of selected items
        self._selected = list()

        # Bind some events to manage properly the list of selected items
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self)

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
        font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))

    # ---------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        wx.Window.SetBackgroundColour(self, colour)
        self._bg_color = colour
        if not self.GetWindowStyleFlag() & wx.LC_HRULES:
            self.RecolorizeBackground(-1)

    # ---------------------------------------------------------------------

    def RecolorizeBackground(self, index=-1):
        """Set background color of items.

        :param index: (int) Item to set the bg color. -1 to set all items.

        """
        bg = self._bg_color
        r, g, b, a = bg.Red(), bg.Green(), bg.Blue(), bg.Alpha()
        if (r + g + b) > 384:
            alt_bg = wx.Colour(r, g, b, a).ChangeLightness(92)
        else:
            alt_bg = wx.Colour(r, g, b, a).ChangeLightness(108)

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
                self.RecolorizeBackground(i)

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
        wx.ListCtrl.Select(self, idx, on=0)

        # if single selection, de-select current item
        # (except if it is the asked one).
        if on == 1 and self.HasFlag(wx.LC_SINGLE_SEL) and len(self._selected) > 0:
            i = self._selected[0]
            if i != idx:
                self._remove_of_selected(i)

        if on == 0:
            # De-select the given index
            self._remove_of_selected(idx)
        else:
            self._add_to_selected(idx)

    # ---------------------------------------------------------------------

    def _remove_of_selected(self, idx):
        if idx in self._selected:
            self._selected.remove(idx)
            font = self.GetFont()
            self.SetItemFont(idx, font)

    # ---------------------------------------------------------------------

    def _add_to_selected(self, idx):
        if idx not in self._selected:
            self._selected.append(idx)
        font = self.GetFont()
        bold = wx.Font(int(float(font.GetPointSize()) * 1.2),
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
        """Override base class.

        """
        item = evt.GetItem()
        item_index = item.GetId()

        # cancel the selection managed by wx.ListCtrl
        wx.ListCtrl.Select(self, item_index, on=0)

        # manage our own selection
        if self.HasFlag(wx.LC_SINGLE_SEL):
            self.Select(item_index, on=1)
            evt.Skip()
        else:
            if item_index in self._selected:
                self.Select(item_index, on=0)
                nex_evt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_ITEM_DESELECTED, self.GetId())
                nex_evt.SetEventObject(self)
                nex_evt.SetItem(item)
                nex_evt.SetIndex(item_index)
                nex_evt.SetColumn(evt.GetColumn())
                wx.PostEvent(self.GetParent(), nex_evt)
            else:
                self.Select(item_index, on=1)
                evt.Skip()

    # ---------------------------------------------------------------------

    def OnItemDeselected(self, evt):
        """Override base class.

        """
        item = evt.GetItem()
        item_index = item.GetId()
        wx.ListCtrl.Select(self, item_index, on=0)

        if self.HasFlag(wx.LC_SINGLE_SEL):
            if item_index in self._selected:
                self.Select(item_index, on=0)

            # re-send the event with the de-selected item,
            # and not the selected one
            if len(self._selected) > 0:
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

    def InsertColumn(self, colnum, colname, format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE):
        """Override. Insert a new column.

        1. create a column with the line number if we create a column
           for the first time
        2. create the expected column

        """
        if colnum == 0:
            # insert a first column, with whitespace
            sppasListCtrl.InsertColumn(self, 0,
                                       heading=" "*16,
                                       format=wx.LIST_FORMAT_CENTRE,
                                       width=sppasListCtrl.fix_size(80))

        sppasListCtrl.InsertColumn(self, colnum+1, colname, format, width)

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
        sppasListCtrl.SetColumnWidth(self, col+1, width)

    # -----------------------------------------------------------------------

    def SetItem(self, index, col, label, imageId=-1):
        """Override. Set the string of an item.

        """
        sppasListCtrl.SetItem(self, index, col+1, label, imageId)

    # -----------------------------------------------------------------------

    def DeleteItem(self, index):
        """Override. Delete an item in the list.

        It must be overridden to update line numbers.

        """
        sppasListCtrl.DeleteItem(self, index)
        for idx in range(index, self.GetItemCount()):
            wx.ListCtrl.SetItem(self, idx, 0, self._num_to_str(idx + 1))

    # -----------------------------------------------------------------------

    @staticmethod
    def _num_to_str(num):
        return " -- " + str(num) + " -- "

# ---------------------------------------------------------------------------


class CheckListCtrl(sppasListCtrl):
    """A ListCtrl with a check button in the first column.

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
        super(CheckListCtrl, self).__init__(
            parent, id, pos, size, style, validator, name)

        if style & wx.LC_SINGLE_SEL:
            self.STATES_ICON_NAMES = {
                "False": "radio_unchecked",
                "True": "radio_checked",
            }
        else:
            self.STATES_ICON_NAMES = {
                "False": "choice_checkbox",
                "True": "choice_checked",
            }
        self._ils = list()
        self.__il = self.__create_image_list()
        self.SetImageList(self.__il, wx.IMAGE_LIST_SMALL)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """Override."""
        wx.ListCtrl.SetForegroundColour(self, color)
        for c in self.GetChildren():
            c.SetForegroundColour(color)
        self.__il = self.__create_image_list()
        self.SetImageList(self.__il, wx.IMAGE_LIST_SMALL)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.ListCtrl.SetFont(self, font)

        # The change of font implies to re-draw all proportional objects
        self.__il = self.__create_image_list()
        self.SetImageList(self.__il, wx.IMAGE_LIST_SMALL)
        self.Layout()

    # ------------------------------------------------------------------------

    def __create_image_list(self):
        """Create a list of images to be displayed in the listctrl.

        :return: (wx.ImageList)

        """
        lh = self.get_font_height()
        icon_size = int(float(lh * 1.4))

        il = wx.ImageList(icon_size, icon_size)
        self._ils = list()

        icon_name = self.STATES_ICON_NAMES["True"]
        bitmap = sppasSwissKnife.get_bmp_icon(icon_name, icon_size)
        img = bitmap.ConvertToImage()
        ColorizeImage(img, wx.BLACK, self.GetForegroundColour())
        il.Add(wx.Bitmap(img))
        self._ils.append(icon_name)

        icon_name = self.STATES_ICON_NAMES["False"]
        bitmap = sppasSwissKnife.get_bmp_icon(icon_name, icon_size)
        img = bitmap.ConvertToImage()
        ColorizeImage(img, wx.BLACK, self.GetForegroundColour())
        il.Add(wx.Bitmap(img))
        self._ils.append(icon_name)

        return il

    # -----------------------------------------------------------------------
    # Override methods of wx.ListCtrl
    # -----------------------------------------------------------------------
    def AppendColumn(self, heading, format=wx.LIST_FORMAT_LEFT, width=-1):
        self.InsertColumn(self.GetColumnCount(), heading, format, width)

    # -----------------------------------------------------------------------

    def InsertColumn(self, colnum, colname, format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE):
        """Override. Insert a new column.

        1. create a column with the line number if we create a column
           for the first time
        2. create the expected column

        """
        if colnum == 0:
            info = wx.ListItem()
            info.Mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
            info.Image = -1
            info.Align = 0
            wx.ListCtrl.InsertColumn(self, 0, info)
            wx.ListCtrl.SetColumnWidth(self, 0, sppasListCtrl.fix_size(24))

        sppasListCtrl.InsertColumn(self, colnum+1, colname, format, width)

    # -----------------------------------------------------------------------

    def InsertItem(self, index, label):
        """Override. Create a row and insert label.

        Create a row, add the line number, add content of the first column.
        Shift the selection of items if necessary.

        """
        icon_name = self.STATES_ICON_NAMES["False"]
        img_index = self._ils.index(icon_name)
        idx = sppasListCtrl.InsertItem(self, index, img_index)

        item = self.GetItem(index, 0)
        item.SetAlign(wx.LIST_FORMAT_CENTER)

        sppasListCtrl.SetItem(self, index, 1, label)
        return idx

    # -----------------------------------------------------------------------

    def SetColumnWidth(self, col, width):
        """Override. Fix column width.

        Fix also the first column.

        """
        sppasListCtrl.SetColumnWidth(self, col+1, width)

    # -----------------------------------------------------------------------

    def SetItem(self, index, col, label, imageId=-1):
        """Override. Set the string of an item.

        """
        sppasListCtrl.SetItem(self, index, col+1, label, imageId)

    # ---------------------------------------------------------------------

    def _remove_of_selected(self, idx):
        sppasListCtrl._remove_of_selected(self, idx)
        icon_name = self.STATES_ICON_NAMES["False"]
        sppasListCtrl.SetItem(self, idx, 0, "", imageId=self._ils.index(icon_name))

    # ---------------------------------------------------------------------

    def _add_to_selected(self, idx):
        sppasListCtrl._add_to_selected(self, idx)
        icon_name = self.STATES_ICON_NAMES["True"]
        sppasListCtrl.SetItem(self, idx, 0, "", imageId=self._ils.index(icon_name))

# ---------------------------------------------------------------------------


class SortListCtrl(sppasListCtrl):
    """ListCtrl with sortable columns.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER | wx.LC_REPORT | wx.LC_SORT_ASCENDING,
                 validator=wx.DefaultValidator, name="SortListCtrl"):
        """Initialize a new ListCtrl instance.

        :param parent: Parent window. Must not be None.
        :param id:     ListCtrl identifier. A value of -1 indicates a default value.
        :param pos:    ListCtrl position. If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   ListCtrl size. If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param validator: Window validator.
        :param name:      Window name.

        """
        if not (style & wx.LC_SORT_ASCENDING or style & wx.LC_SORT_DESCENDING):
            style |= wx.LC_SORT_ASCENDING
        if style & wx.LC_NO_HEADER:
            style &= ~wx.LC_NO_HEADER

        super(SortListCtrl, self).__init__(parent, id, pos, size, style, validator, name)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.__col_clicked)

    # ---------------------------------------------------------------------

    def __col_clicked(self, event):
        """Sort the data by the clicked column."""
        col = event.GetColumn()
        wx.LogMessage("Sort table alphabetically by column {}".format(col))
        data = list()
        for i in range(self.GetItemCount()):
            data_col = list()
            for c in range(self.GetColumnCount()):
                data_col.append(self.GetItemText(i, c))
            data.append(data_col)

        data.sort(key=lambda tup: tup[col])

        self.DeleteAllItems()
        for data_item in data:
            self.Append(data_item)

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
            style=wx.LC_REPORT,  #  | wx.LC_SINGLE_SEL,
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

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_deselected_item)
        listctrl.Bind(wx.EVT_KEY_UP, self._on_char)

        # ---------

        checklist = CheckListCtrl(self,
                                  style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_SINGLE_SEL,
                                  name="checklist")

        # The simplest way to create columns
        checklist.InsertColumn(0, "Artist")
        checklist.InsertColumn(1, "Title")
        checklist.InsertColumn(2, "Genre")

        # Fill rows
        items = musicdata.items()
        for key, data in items:
            idx = checklist.InsertItem(checklist.GetItemCount(), data[0])
            checklist.SetItem(idx, 1, data[1])
            checklist.SetItem(idx, 2, data[2])
            # self.SetItemData(idx, key)

        # Adjust columns width
        checklist.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        checklist.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        checklist.SetColumnWidth(2, 100)

        # ---------

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(listctrl, 1, wx.EXPAND | wx.BOTTOM, 10)
        s.Add(checklist, 1, wx.EXPAND)
        self.SetSizer(s)

    # -----------------------------------------------------------------------

    def _on_selected_item(self, evt):
        logging.debug("Parent received selected item event. Index {}"
                      "".format(evt.GetIndex()))

    def _on_deselected_item(self, evt):
        logging.debug("Parent received de-selected item event. Index {}"
                      "".format(evt.GetIndex()))

    def _on_char(self, evt):
        kc = evt.GetKeyCode()
        char = chr(kc)
        if kc in (8, 127):
            lst = self.FindWindow("listctrl")
            selected = lst.GetFirstSelected()
            if selected != -1:
                lst.DeleteItem(selected)
        evt.Skip()

    def _on_edit_starts(self, evt):
        logging.debug("Parent received LABEL BEGIN EDIT item event. Index {}"
                      "".format(evt.GetIndex()))

