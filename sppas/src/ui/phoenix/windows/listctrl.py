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


# ---------------------------------------------------------------------------


class LineListCtrl(wx.ListCtrl):
    """A ListCtrl with line numbers in the first column.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name="LineListCtrl",):
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
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)

    # ---------------------------------------------------------------------

    def RecolorizeBackground(self, index=-1):
        """Set background color of items.

        :param index: (int) Item to set the bg color. -1 to set all items.

        """
        bg = self.GetBackgroundColour()
        r, g, b = bg.Red(), bg.Green(), bg.Blue()
        delta = 10
        if (r + g + b) > 384:
            alt_bg = wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)
        else:
            alt_bg = wx.Colour(r, g, b, 50).ChangeLightness(delta)

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
            wx.ListCtrl.InsertColumn(self, 0, " "*16, wx.LIST_FORMAT_CENTRE)

        wx.ListCtrl.InsertColumn(self, colnum+1, colname)

    # -----------------------------------------------------------------------

    def InsertItem(self, index, label):
        """Override. Create a row and insert label.

        Create a row, add the line number, add content of the first column.
        Shift the selection of items if necessary.

        """
        wx.ListCtrl.InsertItem(self, index, self._num_to_str(index+1))
        item = self.GetItem(index,0)
        item.SetAlign(wx.LIST_FORMAT_CENTER)
        #item.SetMask(item.GetMask() | wx.LIST_MASK_FORMAT)
        #item.SetBackgroundColour(wx.Colour(200,220,200))   # not efficient
        #item.SetTextColour(wx.Colour(70,100,70))           # not efficient

        # we want to add somewhere in the list (and not append)...
        # shift the line numbers items (for items that are after the new one)
        for i in range(index, self.GetItemCount()):
            wx.ListCtrl.SetItem(self, i, 0, self._num_to_str(i+1))
            self.RecolorizeBackground(i)

        return wx.ListCtrl.SetItem(self, index, 1, label)

    # -----------------------------------------------------------------------

    def SetColumnWidth(self, col, width):
        """Override. Fix column width.

        Fix also the first column.

        """
        wx.ListCtrl.SetColumnWidth(self, 0, wx.LIST_AUTOSIZE_USEHEADER)
        wx.ListCtrl.SetColumnWidth(self, col+1, width)

    # -----------------------------------------------------------------------

    def SetItem(self, index, col, label):
        """Override. Set the string of an item.

        The column number must be changed to be efficient; and alternate
        background colors (just for the list to be easier to read).

        """
        # we added a column the user does not know!
        wx.ListCtrl.SetItem(self, index, col+1, label)
        # and to look nice:
        self.RecolorizeBackground(index)

    # -----------------------------------------------------------------------

    def DeleteItem(self, index):
        """Override. Delete an item in the list.

        It must be overridden to update line numbers.

        """
        wx.ListCtrl.DeleteItem(self,index)
        for i in range(index, self.GetItemCount()):
            wx.ListCtrl.SetItem(self, i, 0, self._num_to_str(i+1))
            self.RecolorizeBackground(index)

    # -----------------------------------------------------------------------

    @staticmethod
    def _num_to_str(num):
        return " -- " + str(num) + " -- "


