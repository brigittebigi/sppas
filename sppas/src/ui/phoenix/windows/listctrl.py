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
    The default is to add an header. Use wx.LC_NO_HEADER to disable header.

    Known bug of wx.ListCtrl:

    - If the list is the child of a page of a wx.Notebook, under Windows only,
      DeleteItem() returns the following error message:
      listctrl.cpp(2614) in wxListCtrl::MSWOnNotify(): invalid internal data pointer?
      It does not occur with the use of a simplebook, a choicebook, a listbook or a
      toolbook instead!
    - Items can't be edited because the events (begin/end edit label) are
      never sent. The wxDemo "ListCtrl_edit" does not work, clicking or double
      clicking on items does.... nothing.

    Limitations:

    - with our customized header, the click on a column header will emit the
      EVT_LIST_COL_CLICK but *** WITHOUT *** the index of the column.
      Use _ForceSystemHeader() to disable this custom header. No other event
      is emitted (right click, etc).

    """

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER | wx.LC_REPORT,
                 validator=wx.DefaultValidator, name="listctrl"):
        """Initialize a new sppasListCtrl instance.

        :param parent: (wx.Window) Parent window, must not be None.
        :param id: (int) A value of -1 indicates a default value.
        :param pos: (wx.Point) or (-1, -1) for the default position.
        :param size: (wx.Size) or (-1, -1) for the default size.
        :param style: (int) often LC_REPORT
        :param validator: Window validator.
        :param name: (str) Window name.

        """
        if style & wx.LC_VRULES:
            style &= ~wx.LC_VRULES

        if style & wx.LC_EDIT_LABELS:
            style &= ~wx.LC_EDIT_LABELS
        if style & wx.LC_NO_HEADER:
            self._header = 0
        else:
            self._header = 1
            style |= wx.LC_NO_HEADER
        self._colnames = dict()

        super(sppasListCtrl, self).__init__(
            parent, id, pos, size, style, validator, name)
        if self.GetWindowStyleFlag() & wx.LC_HRULES:
            self._altcolors = False
        else:
            self._altcolors = True

        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetTextColour(settings.fg_color)
            self.SetFont(settings.text_font)
            self._bg_color = settings.bg_color
            # Attributes of the header are not set: because it's not
            # implemented by wx.ListCtrl.
        except AttributeError:
            self.InheritAttributes()
            self._bg_color = self.GetParent().GetBackgroundColour()

        # List of selected items
        self._selected = list()

        # Bind some events to manage properly the list of selected items
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self)

    # -----------------------------------------------------------------------
    # Added methods
    # -----------------------------------------------------------------------

    def ForceSystemHeader(self):
        """Force to use the header of wx instead of our customized one."""
        self._header = 0
        style = self.GetWindowStyleFlag()
        style &= ~wx.LC_NO_HEADER
        self.SetWindowStyle(style)

    # -----------------------------------------------------------------------

    def SetAlternateRowColour(self, value=True):
        """Override. Highlight one line over two with a different bg color."""
        self._altcolors = bool(value)

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
        """Return the height of the current font."""
        font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))

    # ---------------------------------------------------------------------

    def RecolorizeBackground(self, index=-1):
        """Set background color of given item or from given index.

        :param index: (int) Item to set the bg color. -1 to set all items.

        """
        bg = self._bg_color
        r, g, b, a = bg.Red(), bg.Green(), bg.Blue(), bg.Alpha()
        if (r + g + b) > 384:
            alt_bg = wx.Colour(r, g, b, a).ChangeLightness(95)
        else:
            alt_bg = wx.Colour(r, g, b, a).ChangeLightness(105)

        if index == -1:
            for i in range(self._header, self.GetItemCount()):
                if i % 2:
                    wx.ListCtrl.SetItemBackgroundColour(self, i, bg)
                else:
                    wx.ListCtrl.SetItemBackgroundColour(self, i, alt_bg)
        else:
            index += self._header
            if index % 2:
                wx.ListCtrl.SetItemBackgroundColour(self, index, bg)
            else:
                wx.ListCtrl.SetItemBackgroundColour(self, index, alt_bg)

    # -----------------------------------------------------------------------
    # Overridden methods to enable our customized header
    # -----------------------------------------------------------------------

    def IsEmpty(self):
        """Return True if list is empty, i.e. does not contain rows."""
        return self.GetItemCount() == 0

    def GetItemCount(self):
        """Return the number of rows."""
        return max(wx.ListCtrl.GetItemCount(self) - self._header, 0)

    def EditLabel(self, item):
        wx.ListCtrl.EditLabel(self, item+self._header)

    def EnsureVisible(self, item):
        wx.ListCtrl.EnsureVisible(self, item+self._header)

    def FindItem(self, *args, **kw):
        idx = wx.ListCtrl.FindItem(self, *args, **kw)
        if idx == -1:
            return -1
        return idx - self._header

    def Focus(self, idx):
        idx += self._header
        wx.ListCtrl.Focus(self, idx)

    def GetFocusedItem(self):
        return wx.ListCtrl.GetFocusedItem(self) - self._header

    def GetItem(self, item, col=0):
        return wx.ListCtrl.GetItem(self, item+self._header, col)

    def GetItemBackgroundColour(self, item):
        return wx.ListCtrl.GetItemBackgroundColour(self, item+self._header)

    def GetItemData(self, item):
        return wx.ListCtrl.GetItemData(self, item+self._header)

    def GetItemFont(self, item):
        return wx.ListCtrl.GetItemFont(self, item+self._header)

    def GetItemPosition(self, item):
        return wx.ListCtrl.GetItemPosition(self, item+self._header)

    def GetItemRect(self, item, code=wx.LIST_RECT_BOUNDS):
        return wx.ListCtrl.GetItemRect(self, item, code)

    def GetItemState(self, item, stateMask):
        return wx.ListCtrl.GetItemState(self, item+self._header, stateMask)

    def GetItemText(self, item, col=0):
        return wx.ListCtrl.GetItemText(self, item+self._header, col)

    def GetNextItem(self, item, geometry=wx.LIST_NEXT_ALL, state=wx.LIST_STATE_DONTCARE):
        item += self._header
        wx.ListCtrl.GetNextItem(self, item, geometry, state)

    def GetTopItem(self):
        return wx.ListCtrl.GetTopItem(self) - self._header

    def GetSubItemRect(self, item, subItem, rect, code=wx.LIST_RECT_BOUNDS):
        return wx.ListCtrl.GetSubItemRect(self, item+self._header, subItem, rect, code)

    def RefreshItem(self, item):
        item += self._header
        wx.ListCtrl.RefreshItem(self, item)

    def RefreshItems(self, itemFrom, itemTo):
        itemFrom += self._header
        itemTo += self._header
        wx.ListCtrl.RefreshItems(self, itemFrom, itemTo)

    def SetItemBackgroundColour(self, item, color):
        item += self._header
        wx.ListCtrl.SetItemBackgroundColour(self, item, color)

    def SetItemColumnImage(self, item, column, image):
        item += self._header
        wx.ListCtrl.SetItemColumnImage(self, item, column, image)

    def SetItemCount(self, count):
        count += self._header
        wx.ListCtrl.SetItemCount(self, count)

    def SetItemData(self, item, data):
        item += self._header
        wx.ListCtrl.SetItemData(self, item, data)

    def SetItemFont(self, item, font):
        """Override.

        Bug of wx.ListCtrl under MacOS:
        Python[7425:2394291] CoreText note: Client requested name
        ".SFNS-Regular", it will get Times-Roman rather than the intended
        font. All system UI font access should be through proper APIs such
        as CTFontCreateUIFontForLanguage() or +[NSFont systemFontOfSize:].

        """
        item += self._header
        wx.ListCtrl.SetItemFont(self, item, font)

    def SetItemImage(self, item, image, selImage=-1):
        item += self._header
        wx.ListCtrl.SetItemImage(self, item, image, selImage)

    def SetItemPosition(self, item, pos):
        item += self._header
        wx.ListCtrl.SetItemPosition(self, item, pos)

    def SetItemState(self, item, state, stateMask):
        """Change state of the item in the list.

        DO NOT USE this method if our custom header is enabled.
        The problem here is that this method send an event.

        :param item: THE REAL INDEX of the ITEM IN THE LIST = index+header.

        """
        wx.ListCtrl.SetItemState(self, item, state, stateMask)

    def SetItemText(self, item, text):
        item += self._header
        wx.ListCtrl.SetItemText(self, item, text)

    def SetItemTextColour(self, item, col):
        item += self._header
        wx.ListCtrl.SetItemTextColour(self, item, col)

    def SetHeaderAttr(self, attr):
        pass

    # -----------------------------------------------------------------------
    # Overridden methods for our various customizations
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override.

        """
        wx.Window.SetBackgroundColour(self, colour)
        self._bg_color = colour
        if self._altcolors is True:
            self.RecolorizeBackground(-1)

        if self.GetItemCount() > 0:
            for i in range(self._header):
                wx.ListCtrl.SetItemTextColour(self, i, colour)

    # ---------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override.

        """
        wx.Window.SetForegroundColour(self, colour)
        if self.GetItemCount() > 0:
            for i in range(self._header):
                wx.ListCtrl.SetItemBackgroundColour(self, i, colour)

    # -----------------------------------------------------------------------

    def AppendColumn(self, heading, format=wx.LIST_FORMAT_LEFT, width=-1):
        """Override. Insert a new column at end. """
        self.InsertColumn(self.GetColumnCount(), heading, format, width)

    # -----------------------------------------------------------------------

    def InsertColumn(self, *args, **kwargs):
        """Override. Insert a new column.

        1. create a column with its header (if enabled and if colnum==0)
        2. create the expected column

        Future work:
        We could split the heading string with "\n" to add a multi-line header.

        """
        wx.ListCtrl.InsertColumn(self, *args, **kwargs)
        colnum = args[0]
        shift_colnames = dict()
        for col_idx in self._colnames:
            if col_idx >= colnum:
                shift_colnames[col_idx+1] = self._colnames[col_idx]
            else:
                shift_colnames[col_idx] = self._colnames[col_idx]
        self._colnames = shift_colnames

        if "heading" in kwargs:
            self._colnames[colnum] = kwargs["heading"]
        else:
            if isinstance(args[1], wx.ListItem) is False:
                self._colnames[colnum] = args[1]
            else:
                self._colnames[colnum] = ""

    # ---------------------------------------------------------------------

    def InsertItem(self, index, label):
        """Override. Create a row and insert label.

        :param index: (int) Insert item at this position in the list.
        :param label: string or image index.

        Create a row.
        Shift the selection of items if necessary.

        """
        sel = False
        # it is the 1st line inserted.
        if wx.ListCtrl.GetItemCount(self) == 0:
            if self._header > 0:
                col_idx = sorted(list(self._colnames.keys()))
                wx.ListCtrl.InsertItem(self, 0, label=self._colnames[col_idx[0]], imageIndex=-1)
                col_idx.pop(0)
                for idx in col_idx:
                    wx.ListCtrl.SetItem(self, 0, idx, self._colnames[idx])
                wx.ListCtrl.SetItemBackgroundColour(self, 0, self.GetForegroundColour())
                wx.ListCtrl.SetItemTextColour(self, 0, self.GetBackgroundColour())
            sel = True

        index += self._header
        idx = wx.ListCtrl.InsertItem(self, index, label)

        if sel is False:
            if index < self.GetItemCount():
                for i in range(len(self._selected)):
                    if self._selected[i] >= index:
                        self._selected[i] = self._selected[i] + 1
        else:
            # de-select the first item. Under MacOS, the first item
            # is systematically selected but not under the other platforms.
            wx.ListCtrl.Select(self, 0, on=0)

        if self._altcolors is True:
            for i in range(index, self.GetItemCount()):
                self.RecolorizeBackground(i)

        return idx - self._header

    # -----------------------------------------------------------------------

    def SetItem(self, index, col, label, imageId=-1):
        """Override. Set the string of an item.

        The column number must be changed to be efficient; and alternate
        background colors (just for the list to be easier to read).

        """
        index += self._header
        wx.ListCtrl.SetItem(self, index, col, label, imageId)
        if self._altcolors is True:
            self.RecolorizeBackground(index-self._header)

    # ---------------------------------------------------------------------

    def DeleteItem(self, index):
        """Override.

        Delete an item in the list. It is overridden to also remove it of the
        selected list (if appropriate) and update selected item indexes.

        :param index: (int) Index of an item in the data

        """
        index += self._header
        if index in self._selected:
            self._selected.remove(index)

        for i in range(len(self._selected)):
            if self._selected[i] >= index:
                self._selected[i] = self._selected[i] - 1

        wx.ListCtrl.DeleteItem(self, index)

        if self._altcolors is True:
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
        item += self._header
        s = sorted(self._selected)
        i = wx.ListCtrl.GetNextItem(self, item)
        while i != -1:
            if i in s:
                return i
            i = wx.ListCtrl.GetNextItem(self, i)
        return -1

    # ---------------------------------------------------------------------

    def GetSelectedItemCount(self):
        """Override.

        """
        return len(self._selected)

    # ---------------------------------------------------------------------

    def IsSelected(self, index):
        """Override. Return True if the item is checked."""
        index += self._header
        return index in self._selected

    # ---------------------------------------------------------------------

    def Select(self, idx, on=1):
        """Override. Selects/deselects an item.

        Highlight the selected item with a Bigger & Bold font (the native
        system can't be disabled and is different on each system).

        :param idx: (int) Index of an item in the data
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
        """idx is the item index in the data."""
        if idx in self._selected:
            self._selected.remove(idx)
            font = self.GetFont()
            self.SetItemFont(idx, font)

    # ---------------------------------------------------------------------

    def _add_to_selected(self, idx):
        """idx is the item index in the data."""
        if idx not in self._selected:
            self._selected.append(idx)
        font = self.GetFont()
        bold = wx.Font(font.GetPointSize(),
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
        if self._header > 0 and item_index == 0:
            wx.ListCtrl.Select(self, 0, on=0)
            nex_evt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_COL_CLICK, self.GetId())
            nex_evt.SetEventObject(self)
            nex_evt.SetColumn(evt.GetColumn())
            wx.PostEvent(self, nex_evt)
            return

        # cancel the selection managed by wx.ListCtrl
        wx.ListCtrl.Select(self, item_index, on=0)

        item_index -= self._header

        # manage our own selection

        if self.HasFlag(wx.LC_SINGLE_SEL):
            self.Select(item_index, on=1)
            evt.SetIndex(item_index)
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
                evt.SetIndex(item_index)
                evt.Skip()

    # ---------------------------------------------------------------------

    def OnItemDeselected(self, evt):
        """Override base class.

        """
        item = evt.GetItem()
        item_index = item.GetId()
        wx.ListCtrl.Select(self, item_index, on=0)

        if self._header > 0 and item_index == 0:
            nex_evt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_COL_CLICK, self.GetId())
            nex_evt.SetEventObject(self)
            nex_evt.SetColumn(evt.GetColumn())
            wx.PostEvent(self, nex_evt)
            return

        # manage our own selection
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

        :param parent: (wx.Window) Parent window, must not be None.
        :param id: (int) A value of -1 indicates a default value.
        :param pos: (wx.Point) or (-1, -1) for the default position.
        :param size: (wx.Size) or (-1, -1) for the default size.
        :param style: (int) often LC_REPORT
        :param validator: Window validator.
        :param name: (str) Window name.

        """
        super(LineListCtrl, self).__init__(
            parent, id, pos, size, style, validator, name)

    # -----------------------------------------------------------------------
    # Override methods of sppasListCtrl
    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        sppasListCtrl.SetFont(self, font)
        if self.GetColumnCount() > 0:
            sppasListCtrl.SetColumnWidth(self, 0, self.get_font_height() * 4)
        self.Layout()

    # -----------------------------------------------------------------------

    def InsertColumn(self, colnum, heading, format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE):
        """Override. Insert a new column.

        1. create a column with the line number if we create a column
           for the first time
        2. create the expected column

        """
        if colnum == 0:
            w = self.get_font_height() * 4
            # insert a first column, with whitespace
            sppasListCtrl.InsertColumn(self, 0,
                                       heading=" "*16,
                                       format=wx.LIST_FORMAT_CENTRE,
                                       width=w)

        sppasListCtrl.InsertColumn(self, colnum+1, heading, format, width)

    # -----------------------------------------------------------------------

    def InsertItem(self, index, label):
        """Override. Create a row and insert label.

        Create a row, add the line number, add content of the first column.
        Shift the selection of items if necessary.

        """
        idx = sppasListCtrl.InsertItem(self, index, self._num_to_str(index+1))
        item = sppasListCtrl.GetItem(self, index, 0)
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
            sppasListCtrl.SetItem(self, idx, 0, self._num_to_str(idx+1))

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
                 validator=wx.DefaultValidator, name="CheckListCtrl"):
        """Initialize a new CheckListCtrl instance.

        :param parent: (wx.Window) Parent window, must not be None.
        :param id: (int) A value of -1 indicates a default value.
        :param pos: (wx.Point) or (-1, -1) for the default position.
        :param size: (wx.Size) or (-1, -1) for the default size.
        :param style: (int) often LC_REPORT
        :param validator: Window validator.
        :param name: (str) Window name.

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

        # Checkboxes are systematically in the 1st column
        self.__insert_checkboxes()

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """Override."""
        sppasListCtrl.SetForegroundColour(self, color)
        for c in self.GetChildren():
            c.SetForegroundColour(color)
        self.__il = self.__create_image_list()
        self.SetImageList(self.__il, wx.IMAGE_LIST_SMALL)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        # The change of font implies to re-draw all proportional objects
        self.__il = self.__create_image_list()
        self.SetImageList(self.__il, wx.IMAGE_LIST_SMALL)
        if self.GetColumnCount() > 0:
            sppasListCtrl.SetColumnWidth(self, 0, self.get_font_height() * 2)

        sppasListCtrl.SetFont(self, font)
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

    def __insert_checkboxes(self):
        info = wx.ListItem()
        info.SetMask(wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT)
        info.SetImage(-1)
        info.SetAlign(wx.LIST_FORMAT_CENTRE)
        info.SetText("")
        sppasListCtrl.InsertColumn(self, 0, info)
        sppasListCtrl.SetColumnWidth(self, 0, sppasListCtrl.fix_size(self.get_font_height()*2))

    # -----------------------------------------------------------------------

    def AppendColumn(self, heading, format=wx.LIST_FORMAT_LEFT, width=-1):
        sppasListCtrl.InsertColumn(self, self.GetColumnCount(), heading, format, width)

    # -----------------------------------------------------------------------

    def InsertColumn(self, colnum, heading, format=wx.LIST_FORMAT_LEFT, width=wx.LIST_AUTOSIZE):
        """Override. Insert a new column.

        1. create a column with the line number if we create a column
           for the first time
        2. create the expected column

        """
        sppasListCtrl.InsertColumn(self, colnum+1, heading, format, width)

    # -----------------------------------------------------------------------

    def InsertItem(self, index, label):
        """Override. Create a row and insert label.

        Create a row, add content of the first column.
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

    The default header of wx must be used in order to get the events.

    """

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER | wx.LC_REPORT | wx.LC_SORT_ASCENDING,
                 validator=wx.DefaultValidator, name="SortListCtrl"):
        """Initialize a new ListCtrl instance.

        :param parent: (wx.Window) Parent window, must not be None.
        :param id: (int) A value of -1 indicates a default value.
        :param pos: (wx.Point) or (-1, -1) for the default position.
        :param size: (wx.Size) or (-1, -1) for the default size.
        :param style: (int) often LC_REPORT
        :param validator: Window validator.
        :param name: (str) Window name.

        """
        if not (style & wx.LC_SORT_ASCENDING or style & wx.LC_SORT_DESCENDING):
            style |= wx.LC_SORT_ASCENDING
        #if style & wx.LC_NO_HEADER:
        #    style &= ~wx.LC_NO_HEADER
        super(SortListCtrl, self).__init__(parent, id, pos, size, style, validator, name)
        self.ForceSystemHeader()
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
# Test panel (should be extended to test more features)
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
        listctrl.SetAlternateRowColour(True)

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
        wx.LogDebug("Test. Select Linda Ronstadt - Don't Know Much at index=4")
        listctrl.Select(4, on=1)
        wx.LogDebug("Test. Delete Spyro Gyra - End of Romanticism at index=21")
        listctrl.DeleteItem(21)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_deselected_item)
        listctrl.Bind(wx.EVT_KEY_UP, self._on_char)

        # ---------

        checklist = CheckListCtrl(self,
                                  style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
                                  name="checklist")

        checklist.SetAlternateRowColour(False)

        # The simplest way to create columns
        checklist.AppendColumn("Artist")
        checklist.AppendColumn("Title")
        checklist.InsertColumn(0, "Genre")

        # Fill rows
        items = musicdata.items()
        for key, data in items:
            idx = checklist.InsertItem(checklist.GetItemCount(), data[2])
            checklist.SetItem(idx, 1, data[0])
            checklist.SetItem(idx, 2, data[1])
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

