#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: CustomListCtrl.py
# ----------------------------------------------------------------------------

import wx

from sppas.src.ui.wxgui.cutils.imageutils import GrayOut
from sppas.src.ui.wxgui.cutils.imageutils import GetCheckedBitmap, GetCheckedImage, GetNotCheckedBitmap, GetNotCheckedImage

# -------------------------------------------------------------------------


class CheckListCtrl(wx.ListCtrl):
    """
    @author:  Brigitte Bigi
    @contact: contact@sppas.org
    @license: GPL, v3
    @summary: A ListCtrl with check-able buttons in the first column.

    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name="CheckListCtrl"):
        """
        Initialize a new ListCtlr instance.

        @param parent: Parent window. Must not be None.
        @param id:     CheckListCtrl identifier. A value of -1 indicates a default value.
        @param pos:    CheckListCtrl position. If the position (-1, -1) is specified
                       then a default position is chosen.
        @param size:   CheckListCtrl size. If the default size (-1, -1) is specified
                       then a default size is chosen.
        @param style:  often LC_REPORT
        @param validator: Window validator.
        @param name:      Window name.

        """
        style = wx.LC_REPORT | wx.NO_BORDER | wx.FULL_REPAINT_ON_RESIZE | wx.LC_ALIGN_TOP
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)

        # Create a list of selected items:
        # it is required to mimic the behaviors of a checklist.
        # The use of the standard selection list is then canceled, and replaced by this one.
        self.sel = []          # the list of checked items (list of index)
        self.colcheck = False  # the whole column was checked

        # Create image list and assign to this list
        self.__initializeBitmaps()
        il = self.__createImageList()
        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)

        # Bind some events to manage properly the list of selected files
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,    self.OnItemSelected,   self)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED,  self.OnItemDeselected, self)
        self.Bind(wx.EVT_LIST_COL_CLICK,        self.OnColumnClick,    self)

    # ---------------------------------------------------------------------
    # Private methods to init
    # ---------------------------------------------------------------------

    def __initializeBitmaps(self):
        """
        Initializes the check bitmaps.
        We keep 4 bitmaps for checking, depending on:
           - the checking state (Checked/UnCkecked) and
           - the control state (Enabled/Disabled).

        It is supposed that the methods return bitmaps in (16,16) size.

        """
        self._bitmaps = {"CheckedEnable":    GetCheckedBitmap(not self.HasFlag( wx.LC_SINGLE_SEL )),
                         "UnCheckedEnable":  GetNotCheckedBitmap(not self.HasFlag( wx.LC_SINGLE_SEL )),
                         "CheckedDisable":   GrayOut(GetCheckedImage(not self.HasFlag( wx.LC_SINGLE_SEL ))).ConvertToBitmap(),
                         "UnCheckedDisable": GrayOut(GetNotCheckedImage(not self.HasFlag( wx.LC_SINGLE_SEL ))).ConvertToBitmap()}

    # ---------------------------------------------------------------------

    def __createImageList(self):
        """Load some images into an image list."""

        il = wx.ImageList(16, 16, True)

        # Enabled = True, Check = False
        self.UNCHECK = il.Add(self.__getBitmap(True, False))

        # Enabled = True, Check = True
        self.CHECK = il.Add(self.__getBitmap(True, True))

        # Enabled = False, Check = False
        il.Add(self.__getBitmap(False, False))

        # Enabled = False, Check = True
        il.Add(self.__getBitmap(False, True))

        return il

    # ---------------------------------------------------------------------

    def __getBitmap(self, enabled, checked):
        """
        Returns the appropriated bitmap depending on the checking state
        (Checked/UnCkecked) and the control state (Enabled/Disabled).

        """
        if enabled:
            # So we are Enabled
            if checked:
                # We are Checked
                return self._bitmaps["CheckedEnable"]
            else:
                # We are UnChecked
                return self._bitmaps["UnCheckedEnable"]
        else:
            # Poor Check Button, disabled and ignored!
            if checked:
                return self._bitmaps["CheckedDisable"]
            else:
                return self._bitmaps["UnCheckedDisable"]

    # ---------------------------------------------------------------------
    # Override methods of wx.ListCtrl
    # ---------------------------------------------------------------------

    def InsertColumn(self, colnum, colname):
        """
        Override. Insert a new column.

        1. create a column with a check button if we create a column for the first time,
        2. create the expected column

        """
        if colnum == 0:
            # insert a first column, with check buttons
            wx.ListCtrl.InsertColumn(self, 0, "", wx.LIST_FORMAT_CENTRE)
            if not self.HasFlag( wx.LC_SINGLE_SEL ):
                self.SetColumnImage(0, self.UNCHECK)

        wx.ListCtrl.InsertColumn(self, colnum+1, colname)

    # ---------------------------------------------------------------------

    def InsertStringItem(self, index, label):
        """
        Override.
        Create a row, add the ckeckable button, add content of the first column.
        Shift the selection of items if necessary.

        """
        self.InsertImageStringItem(index, "", self.UNCHECK)
        item = self.GetItem(index,0)
        item.SetAlign(wx.ALIGN_CENTER)
        item.SetMask(item.GetMask() | wx.LIST_MASK_FORMAT)

        # we want to add somewhere in the list (and not append)...
        # shift the index of selected items (for items that are after the new one)
        if index < self.GetItemCount():
            for i in range(len(self.sel)):
                if self.sel[i] >= index:
                    self.sel[i] = self.sel[i]+1

        return wx.ListCtrl.SetStringItem(self, index, 1, label)

    # ---------------------------------------------------------------------

    def SetColumnWidth(self, col, width):
        """
        Override.
        Fix column width. Fix also the first column (with check buttons).

        """
        wx.ListCtrl.SetColumnWidth(self, 0, wx.LIST_AUTOSIZE_USEHEADER)
        wx.ListCtrl.SetColumnWidth(self, col+1, width)

    # ---------------------------------------------------------------------

    def SetStringItem(self, index, col, label):
        """
        Override.
        Set the string of an item: the column number must be changed to be
        efficient; and alternate background colors (just for the list to be
        easier to read).

        """
        # we added a column the user does not know!
        wx.ListCtrl.SetStringItem(self, index, col+1, label)
        # just to look nice:
        if index % 2:
            self.SetItemBackgroundColour(index, wx.Colour(245,245,240))
        else:
            self.SetItemBackgroundColour(index, wx.WHITE)

    # ---------------------------------------------------------------------

    def DeleteItem(self, index):
        """
        Override.
        Delete an item in the list. Must be overriden to also remove it of the
        selected list (if appropriate).

        """
        if index in self.sel:
            self.sel.remove(index)

        # we want to del somewhere in the list (and not append)...
        # shift the index of selected items (for items that are after)
        for i in range(len(self.sel)):
            if self.sel[i] >= index:
                self.sel[i] = self.sel[i] - 1

        wx.ListCtrl.DeleteItem(self, index)

    # ---------------------------------------------------------------------
    # Override selection of items.
    # Create our own list of selected items, and do not use the default one.
    # ---------------------------------------------------------------------

    def Select(self, index, on=1):
        """
        Override.

        """
        # if single selection, de-select current item (except if it is the asked one).
        if self.HasFlag( wx.LC_SINGLE_SEL ) and len(self.sel) > 0:
            i = self.sel[0]
            if i != index:
                self.sel.remove(i)
                self.SetItemColumnImage( i, 0, self.UNCHECK )

        # we're ready to select or deselect
        if on:
            if index not in self.sel:
                self.sel.append( index )
                self.SetItemColumnImage( index, 0, self.CHECK )
        else:
            if index in self.sel:
                self.sel.remove( index )
                self.SetItemColumnImage( index, 0, self.UNCHECK )

    # ---------------------------------------------------------------------

    def GetFirstSelected(self):
        """
        Override.

        """
        if not len(self.sel):
            return -1
        return self.sel[0]

    # ---------------------------------------------------------------------

    def GetNextSelected(self, item):
        """
        Override.

        """
        s = sorted(self.sel)
        i = self.GetNextItem( item )
        while (i != -1):
            if i in s:
                return i
            i = self.GetNextItem( i )
        return -1

    # ---------------------------------------------------------------------

    def GetSelectedItemCount(self):
        """
        Override.

        """
        return len(self.sel)

    # ---------------------------------------------------------------------

    def IsSelected(self, index):
        """
        Override.
        Return True if the item is checked.

        """
        return index in self.sel

    # ---------------------------------------------------------------------
    # Callbacks
    # ---------------------------------------------------------------------

    def OnColumnClick(self, evt):
        """
        Callback.
        A column was clicked.
        If it's our column with check buttons: select-all, or unselect-all

        """
        col = evt.GetColumn()
        if col == 0 and not self.HasFlag( wx.LC_SINGLE_SEL ):
            if self.colcheck is True:
                self.DeSelectAll()
            else:
                self.SelectAll()
        evt.Skip()

    # ---------------------------------------------------------------------

    def OnItemSelected(self, evt):
        """
        Callback.

        """
        item = evt.GetItem()
        wx.ListCtrl.Select(self, item.GetId(), on=0)

        # Mimic the checklist: check/uncheck if click on the same row
        if item.GetId() in self.sel:
            # De-select it!
            self.sel.remove( item.GetId() )
            self.SetItemColumnImage(item.GetId(), 0, self.UNCHECK)
        else:
            if self.HasFlag( wx.LC_SINGLE_SEL ):
                self.DeSelectAll()
            self.sel.append( item.GetId() )
            self.SetItemColumnImage(item.GetId(), 0, self.CHECK)

        evt.Skip()

    # ---------------------------------------------------------------------

    def OnItemDeselected(self, evt):
        """
        Callback.

        """
        item = evt.GetItem()
        wx.ListCtrl.Select(self, item.GetId(), on=0)

        if not self.HasFlag( wx.LC_SINGLE_SEL ):
            if item.GetId() in self.sel:
                # Re-select it!
                #self.sel.append( item.GetId() )
                self.SetItemColumnImage(item.GetId(), 0, self.CHECK)
        else:
            if item.GetId() in self.sel:
                self.sel.remove( item.GetId() )
                self.SetItemColumnImage(item.GetId(), 0, self.UNCHECK)

        evt.Skip()

    # ---------------------------------------------------------------------
    # Methods we add for convenience!
    # ---------------------------------------------------------------------

    def SelectAll(self):
        """
        Select (i.e. check) all items in the list.
        """
        if not self.HasFlag( wx.LC_SINGLE_SEL ):
            self.SetColumnImage(0, self.CHECK)
            self.colcheck = True
            for index in range(self.GetItemCount()):
                self.Select(index, True)

    # ---------------------------------------------------------------------

    def DeSelectAll(self):
        """
        Un-Select (i.e. uncheck) all items in the list.
        """
        if not self.HasFlag( wx.LC_SINGLE_SEL ):
            self.SetColumnImage(0, self.UNCHECK)
            self.colcheck = False
        for index in sorted(self.sel):
            self.SetItemColumnImage(index, 0, self.UNCHECK)
        self.sel = list()

# -------------------------------------------------------------------------


class LineListCtrl( wx.ListCtrl ):
    """
    @author:  Brigitte Bigi
    @contact: contact@sppas.org
    @license: GPL, v3
    @summary: A ListCtrl with line numbers in the first column.

    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name="LineListCtrl",):
        """
        Initialize a new ListCtlr instance.

        @param parent: Parent window. Must not be None.
        @param id:     CheckListCtrl identifier. A value of -1 indicates a default value.
        @param pos:    CheckListCtrl position. If the position (-1, -1) is specified
                       then a default position is chosen.
        @param size:   CheckListCtrl size. If the default size (-1, -1) is specified
                       then a default size is chosen.
        @param style:  often LC_REPORT
        @param validator: Window validator.
        @param name:      Window name.

        """
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)

    # ---------------------------------------------------------------------
    # Override methods of wx.ListCtrl
    # ---------------------------------------------------------------------

    def InsertColumn(self, colnum, colname):
        """
        Override.
        Insert a new column:
            1. create a column with the line number if we create a column for the first time,
            2. create the expected column

        """
        if colnum == 0:
            # insert a first column, with check buttons
            wx.ListCtrl.InsertColumn(self, 0, " "*16, wx.LIST_FORMAT_CENTRE)

        wx.ListCtrl.InsertColumn(self, colnum+1, colname)


    def InsertStringItem(self, index, label):
        """
        Override.
        Create a row, add the line number, add content of the first column.
        Shift the selection of items if necessary.

        """
        wx.ListCtrl.InsertStringItem(self, index, " -- "+str(index+1)+" -- ")
        item = self.GetItem(index,0)
        item.SetAlign(wx.ALIGN_CENTER)
        #item.SetMask(item.GetMask() | wx.LIST_MASK_FORMAT)
        #item.SetBackgroundColour(wx.Colour(200,220,200))   # not efficient
        #item.SetTextColour(wx.Colour(70,100,70))           # not efficient

        # we want to add somewhere in the list (and not append)...
        # shift the line numbers items (for items that are after the new one)
        for i in range(index,self.GetItemCount()):
            wx.ListCtrl.SetStringItem(self, i, 0, " -- "+str(i+1)+" -- ")
            if i % 2:
                self.SetItemBackgroundColour(i, wx.Colour(245,245,240))
            else:
                self.SetItemBackgroundColour(i, wx.WHITE)

        return wx.ListCtrl.SetStringItem(self, index, 1, label)


    def SetColumnWidth(self, col, width):
        """
        Override.
        Fix column width. Fix also the first column (with check buttons).

        """
        wx.ListCtrl.SetColumnWidth(self, 0, wx.LIST_AUTOSIZE_USEHEADER)
        wx.ListCtrl.SetColumnWidth(self, col+1, width)


    def SetStringItem(self, index, col, label):
        """
        Override.
        Set the string of an item: the column number must be changed to be
        efficient; and alternate background colors (just for the list to be
        easier to read).

        """
        # we added a column the user does not know!
        wx.ListCtrl.SetStringItem(self, index, col+1, label)
        # just to look nice:
        if index % 2:
            self.SetItemBackgroundColour(index, wx.Colour(245,245,240))
        else:
            self.SetItemBackgroundColour(index, wx.WHITE)


    def DeleteItem(self, index):
        """
        Override.
        Delete an item in the list. Must be overriden to update line numbers.

        """
        wx.ListCtrl.DeleteItem(self,index)
        for i in range(index,self.GetItemCount()):
            wx.ListCtrl.SetStringItem(self, i, 0, " -- "+str(i+1)+" -- ")
            if i % 2:
                self.SetItemBackgroundColour(i, wx.Colour(245,245,240))
            else:
                self.SetItemBackgroundColour(i, wx.WHITE)

# -------------------------------------------------------------------------


# -------------------------------------------------------------------------

class SortListCtrl( wx.ListCtrl ):
    """
    @author:  Brigitte Bigi
    @contact: contact@sppas.org
    @license: GPL, v3
    @summary: A ListCtrl with sorted columns.

    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name="SortListCtrl",):
        """
        Initialize a new ListCtlr instance.

        @param parent: Parent window. Must not be None.
        @param id:     CheckListCtrl identifier. A value of -1 indicates a default value.
        @param pos:    CheckListCtrl position. If the position (-1, -1) is specified
                       then a default position is chosen.
        @param size:   CheckListCtrl size. If the default size (-1, -1) is specified
                       then a default size is chosen.
        @param style:  often LC_REPORT
        @param validator: Window validator.
        @param name:      Window name.

        """
        style = wx.LC_REPORT|wx.LC_VRULES|wx.LC_AUTOARRANGE|wx.LC_SORT_ASCENDING
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)

        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumnClick, self)

    # ---------------------------------------------------------------------
    # Override methods of wx.ListCtrl
    # ---------------------------------------------------------------------

    def InsertStringItem(self, index, label):
        """
        Override.

        """
        ret = wx.ListCtrl.InsertStringItem(self, index, label)
        for i in range(self.GetItemCount()):
            if i % 2:
                self.SetItemBackgroundColour(i, wx.Colour(245,245,240))
            else:
                self.SetItemBackgroundColour(i, wx.WHITE)
        return ret


    def SetStringItem(self, index, col, label):
        """
        Override.
        Set the string of an item.
        """
        # we added a column the user does not know!
        wx.ListCtrl.SetStringItem(self, index, col, label)
        if index % 2:
            self.SetItemBackgroundColour(index, wx.Colour(245,245,240))
        else:
            self.SetItemBackgroundColour(index, wx.WHITE)


    def DeleteItem(self, index):
        """
        Override.
        Delete an item in the list.

        """
        wx.ListCtrl.DeleteItem(self,index)
        for i in range(index,self.GetItemCount()):
            if i % 2:
                self.SetItemBackgroundColour(i, wx.Colour(245,245,240))
            else:
                self.SetItemBackgroundColour(i, wx.WHITE)

    # ---------------------------------------------------------------------
    # Callback
    # ---------------------------------------------------------------------

    def OnColumnClick(self, evt):
        """
        Callback.
        A column was clicked.

        """
        col = evt.GetColumn()
        evt.Skip()

# -------------------------------------------------------------------------
