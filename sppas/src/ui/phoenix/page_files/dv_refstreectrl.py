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

    src.ui.phoenix..page_files.refstreectrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx
import wx.dataview

from sppas.src.files.filedata import FileData

from ..windows.baseviewctrl import BaseTreeViewCtrl
from .dv_refsviewmodel import ReferencesTreeViewModel

# ----------------------------------------------------------------------------
# Control to store the data matching the model
# ----------------------------------------------------------------------------


class ReferencesTreeViewCtrl(BaseTreeViewCtrl):
    """A control to display references in a tree-spreadsheet style.

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
        """Constructor of the ReferencesTreeViewCtrl.

        :param parent: (wx.Window)

        """
        super(ReferencesTreeViewCtrl, self).__init__(parent, name)

        # Create an instance of our model and associate to the view.
        self._model = None
        self.__create_model(FileData())

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
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_EDITING_DONE, self._on_item_edited)

    # ------------------------------------------------------------------------

    def __create_model(self, data):
        """Create an instance of our model and associate to the view."""
        self._model = ReferencesTreeViewModel(data)
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
        ret = self._model.set_data(data)
        if ret is False:
            del self._model
            self.__create_model(data)

        self.__restore_expanders()

    # ------------------------------------------------------------------------

    def GetCheckedRefs(self):
        """Return checked references."""
        return self._model.get_checked_refs()

    # ------------------------------------------------------------------------

    def HasCheckedRefs(self):
        """Return True if at least one reference is checked."""
        return self._model.has_checked_refs()

    # ------------------------------------------------------------------------

    def CreateRef(self, ref_name, ref_type):
        """Create a new reference and add it into the tree.

        :param ref_name: (str)
        :param ref_type: (str) On of the accepted type of references
        :raise: Exception

        """
        item = self._model.create_ref(ref_name, ref_type)
        if item is None:
            raise Exception("An unexpected error occurred.")
        logging.info('Reference created successfully: {:s}, {:d}'
                     ''.format(ref_name, ref_type))

    # ------------------------------------------------------------------------

    def AddRefs(self, entries):
        """Add a list of references into the model.

        :param entries: (str) List of references.

        """
        nb = self._model.add_refs(entries)
        if nb > 0:
            logging.debug('Added {:d} references in the data.'.format(len(entries)))
            self.__restore_expanders()
        return nb

    # ------------------------------------------------------------------------

    def RemoveCheckedRefs(self):
        """Remove all checked references."""
        nb = self._model.remove_checked_refs()
        if nb > 0:
            logging.info('Removed {:d} references.'.format(nb))
            self.__restore_expanders()
        return nb

    # ------------------------------------------------------------------------

    def RemoveAttribute(self, identifier):
        """Remove an attribute from the checked references.

        :param identifier: (str)
        :returns: Number of references in which the attribute were removed.

        """
        nb = self._model.remove_attribute(identifier)
        logging.info('Identifier {:s} removed of {:d} references.'
                     ''.format(identifier, nb))
        if nb > 0:
            self.__restore_expanders()
        return nb

    # ------------------------------------------------------------------------

    def EditAttribute(self, identifier, value, att_type, description):
        """Add or modify an attribute into the checked references.

        :param identifier: (str)
        :param value: (str)
        :param att_type: (str)
        :param description: (str)
        :returns: Number of references in which the attribute were added.

        """
        nb = self._model.edit_attribute(identifier, value, att_type, description)
        logging.info('Identifier {:s} added into {:d} references.'
                     ''.format(identifier, nb))
        if nb > 0:
            self.__restore_expanders()
        return nb

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _on_item_expanded(self, evt):
        """Happens when the user checked the 1st column of the tree.

        We have to update the corresponding object 'expand' value to True.

        """
        self._model.expand(True, evt.GetItem())

    # ------------------------------------------------------------------------

    def _on_item_collapsed(self, evt):
        """Happens when the user checked the 1st column of the tree.

        We have to update the corresponding object 'expand' value to False.

        """
        self._model.expand(False, evt.GetItem())

    # ------------------------------------------------------------------------

    def _on_item_activated(self, event):
        """Happens when the user activated a cell (double-click).

        This event is triggered by double clicking an item or pressing some
        special key (usually "Enter") when it is focused.

        """
        self._model.change_value(event.GetItem())

    # ------------------------------------------------------------------------

    def _on_item_selection_changed(self, event):
        """Happens when the user simple-click a cell.

        """
        self._model.change_value(event.GetItem())

    # ------------------------------------------------------------------------

    def _on_item_edited(self, event):
        """Happens when the user modified the content of an editable cell.

        Notice that on MacOS, the event.GetValue() method returns None, so
        that the value can not be changed in that way. Use SetValue() of
        the model instead.

        """
        if wx.Platform != "__WXMAC__":
            self._model.change_value(event.GetItem(),
                                     event.GetColumn(),
                                     event.GetValue())

    # ------------------------------------------------------------------------

    def __restore_expanders(self):
        for item in self._model.get_expanded_items(True):
            self.Expand(item)
        for item in self._model.get_expanded_items(False):
            self.Collapse(item)
