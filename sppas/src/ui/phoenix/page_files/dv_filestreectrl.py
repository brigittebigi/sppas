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

    src.ui.lib.filestreectrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Deprecated. Because dataview is:
        - not supported undex Linux;
        - several problems under MacOS;
        - Expand/Collapse does not work as expected.

"""

import wx
import wx.dataview

from sppas.src.files.filedata import FileData

from .dv_filesviewmodel import FilesTreeViewModel
from ..windows.baseviewctrl import BaseTreeViewCtrl

# ----------------------------------------------------------------------------
# Control to display the data matching the model
# ----------------------------------------------------------------------------


class FilesTreeViewCtrl(BaseTreeViewCtrl):
    """A control to display data files in a tree-spreadsheet style.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Columns of this class are defined by the model and created by the
    constructor. No parent nor children will have the possibility to 
    Append/Insert/Prepend/Delete columns: such methods are disabled.

    """

    def __init__(self, parent, name=wx.PanelNameStr):
        """Constructor of the FileTreeCtrl.

        :ram parent: (wx.Window)
        :param name: (str)

        """
        super(FilesTreeViewCtrl, self).__init__(parent, name)

        # Create an instance of our model and associate to the view.
        self._model = FilesTreeViewModel(FileData())
        self.AssociateModel(self._model)
        self._model.DecRef()

        # Create the columns that the model wants in the view.
        for i in range(self._model.GetColumnCount()):
            col = BaseTreeViewCtrl._create_column(self._model, i)
            if i == self._model.GetExpanderColumn():
                self.SetExpanderColumn(col)
            wx.dataview.DataViewCtrl.AppendColumn(self, col)

        # Bind events.
        # Used to remember the expend/collapse status of items after a refresh.
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_EXPANDED, self._on_item_expanded)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_COLLAPSED, self._on_item_collapsed)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self._on_item_activated)
        self.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self._on_item_selection_changed)

    # ------------------------------------------------------------------------

    def __create_model(self, data):
        """Create an instance of our model and associate to the view."""
        self._model = FilesTreeViewModel(data)
        self.AssociateModel(self._model)
        self._model.DecRef()

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data of the model."""
        return self._model.get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Set the data of the model."""
        ret = self._model.set_data(data)
        if ret is False:
            del self._model
            self.__create_model(data)

        self.__restore_expanders()

    # ------------------------------------------------------------------------

    def AddFiles(self, entries):
        """Add a list of files or folders in the model.
        
        The given filenames must include their absolute path.

        :param entries: (list of str) Filename or folder with absolute path.
        :return: (int) Number of items added in the tree

        """
        items = self._model.add_files(entries)
        nb = len(items)
        if len(items) > 0:
            self.__restore_expanders()
        return nb

    # ------------------------------------------------------------------------

    def RemoveCheckedFiles(self):
        """Remove all checked files."""
        nb = self._model.remove_checked_files()
        if nb > 0:
            self.__restore_expanders()
            return True
        return False

    # ------------------------------------------------------------------------

    def DeleteCheckedFiles(self):
        """Delete all checked files."""
        nb = self._model.delete_checked_files()
        if nb > 0:
            self.__restore_expanders()
            return True
        return False

    # ------------------------------------------------------------------------

    def GetCheckedFiles(self):
        """Return the list of checked files.

        :returns: List of FileName

        """
        return self._model.get_checked_files()

    # ------------------------------------------------------------------------

    def LockFiles(self, entries):
        """Lock a list of files.

        Entries are a list of filenames with absolute path or FileName
        instances or both.

        :param entries: (list of str/FileName)

        """
        self._model.lock(entries)

    # ------------------------------------------------------------------------

    def update_data(self):
        """Overridden. Update the currently displayed data."""
        self._model.update()
        self.__restore_expanders()

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _on_item_expanded(self, evt):
        """Happens when the user cliched a '+' button of the tree.

        We have to update the corresponding object 'expand' value to True.

        """
        self._model.expand(True, evt.GetItem())

    # ------------------------------------------------------------------------

    def _on_item_collapsed(self, evt):
        """Happens when the user cliched a '-' button of the tree.

        We have to update the corresponding object 'expand' value to False.

        """
        self._model.expand(False, evt.GetItem())

    # ------------------------------------------------------------------------

    def _on_item_activated(self, event):
        """Happens when the user activated a cell (double-click).

        This event is triggered by double clicking an item or pressing some
        special key (usually "Enter") when it is focused.

        """
        item = event.GetItem()
        if item is not None:
            self._model.change_value(event.GetColumn(), item)

    # ------------------------------------------------------------------------

    def _on_item_selection_changed(self, event):
        """Happens when the user simple-click a cell.

        """
        item = event.GetItem()
        if item is not None:
            self._model.change_value(event.GetColumn(), item)

    # ------------------------------------------------------------------------

    def __restore_expanders(self):
        for item in self._model.get_expanded_items(True):
            self.Expand(item)
        for item in self._model.get_expanded_items(False):
            self.Collapse(item)

