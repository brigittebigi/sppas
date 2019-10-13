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

    src.ui.phoenix.page_files.refsviewmodel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This model acts as a bridge between a DataViewCtrl and a FileData instance.

"""

import logging
import wx
import wx.dataview

from sppas import sppasTypeError
from sppas.src.files.filebase import States
from sppas.src.files.filedata import FileData
from sppas.src.files.fileref import FileReference, sppasAttribute

from sppas.src.ui.phoenix.windows.baseviewctrl import ColumnProperties, StateIconRenderer

# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------


class ReferencesTreeViewModel(wx.dataview.PyDataViewModel):
    """A class that is a DataViewModel combined with an object mapper.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This model mapper provides these data columns identifiers:

        0. state:        wxBitmap
        1. ref/attvalue: string
        2. attvaluetype: string
        3. attdescr:     string

    """

    def __init__(self, data):
        """Constructor of a fileTreeModel.

        No data is given at the initialization.
        Use set_data() method.

        """
        wx.dataview.PyDataViewModel.__init__(self)
        try:  # wx4 only
            self.UseWeakRefs(True)
        except AttributeError:
            pass

        # The workspace to display
        self.__data = FileData()
        self.set_data(data)

        # Map between displayed columns and workspace
        self.__mapper = dict()
        self.__mapper[0] = ReferencesTreeViewModel.__create_col('state')
        self.__mapper[1] = ReferencesTreeViewModel.__create_col('refs')
        self.__mapper[2] = ReferencesTreeViewModel.__create_col('attvalue')
        self.__mapper[3] = ReferencesTreeViewModel.__create_col('attvaluetype')
        self.__mapper[4] = ReferencesTreeViewModel.__create_col('attdescr')

        # GUI information which can be managed by the mapper
        self._bgcolor = None
        self._fgcolor = None

    # -----------------------------------------------------------------------

    def change_value(self, item, col=-1, value=None):
        """Change data content value.

        A column value of '-1' on a FileReference means to change the state.

        :param item: (wx.dataview.DataViewItem)
        :param col: (int) Index of the column changed.
        :param value: A value to set

        """
        try:
            node = self.ItemToObject(item)
        except TypeError:
            # occurs sometimes on mac while clicking elsewhere than a row
            # of the tree
            return

        changed = False
        if isinstance(node, FileReference) and col == -1:
            cur_state = node.get_state()
            if cur_state == States().UNUSED:
                node.set_state(States().CHECKED)
            else:
                node.set_state(States().UNUSED)
            changed = True

        elif isinstance(node, sppasAttribute) and col != -1 and value is not None:
            if self.__mapper[col].get_id() == "attvalue":
                node.set_value(value)
                changed = True
            if self.__mapper[col].get_id() == "attdescr":
                node.set_description(value)
                changed = True

        if changed:
            self.ItemChanged(item)

    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data displayed into the tree."""
        return self.__data

    # -----------------------------------------------------------------------

    def set_data(self, data):
        """Set new data to the model.

        self.Cleared() is not called under Linux. The tree is not updated,
        only the data are updated, because on GTK, the Cleared method will
        erase the displayed items but it won't display the new ones. This
        is a known bug of this method.
        http://wxpython-users.1045709.n5.nabble.com/DataViewModel-Cleared-problem-on-GTK-td5722735.html

        :return: (bool) Successfully set data and cleared the tree.
        This method always returns False under Linux.


        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data to set in the references panel. '
                      'Id={:s}'.format(data.id))
        self.__data = data
        if wx.Platform != "__WXGTK__":
            self.Cleared()
            return True
        else:
            return False

    # -----------------------------------------------------------------------
    # Manage column properties
    # -----------------------------------------------------------------------

    def GetColumnCount(self):
        """Overridden. Report how many columns this model provides data for."""
        return len(self.__mapper)

    # -----------------------------------------------------------------------

    def GetExpanderColumn(self):
        """Returns column which have to contain the expanders."""
        return 1

    # -----------------------------------------------------------------------

    def GetColumnType(self, col):
        """Override. Map the data column number to the data type.

        :param col: (int) Column index.

        """
        return self.__mapper[col].stype

    # -----------------------------------------------------------------------

    def GetColumnName(self, col):
        """Map the data column number to the data name.

        :param col: (int) Column index.

        """
        return self.__mapper[col].name

    # -----------------------------------------------------------------------

    def GetColumnMode(self, col):
        """Map the data column number to the cell mode.

        :param col: (int) Column index.

        """
        return self.__mapper[col].mode

    # -----------------------------------------------------------------------

    def GetColumnWidth(self, col):
        """Map the data column number to the col width.

        :param col: (int) Column index.

        """
        return self.__mapper[col].width

    # -----------------------------------------------------------------------

    def GetColumnRenderer(self, col):
        """Map the data column numbers to the col renderer.

        :param col: (int) Column index.

        """
        return self.__mapper[col].renderer

    # -----------------------------------------------------------------------

    def GetColumnAlign(self, col):
        """Map the data column numbers to the col alignment.

        :param col: (int) Column index.

        """
        return self.__mapper[col].align

    # -----------------------------------------------------------------------
    # Manage the tree
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        self._bgcolor = color

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        self._fgcolor = color

    # -----------------------------------------------------------------------

    def GetChildren(self, parent, children):
        """The view calls this method to find the children of any node.

        There is an implicit hidden root node, and the top level
        item(s) should be reported as children of this node.

        """
        if not parent:
            for ref in self.__data.get_refs():
                children.append(self.ObjectToItem(ref))
            return len(self.__data.get_refs())

        # Otherwise we'll fetch the python object associated with the parent
        # item and make DV items for each of its child objects.
        node = self.ItemToObject(parent)
        if isinstance(node, FileReference):
            for child_node in node:
                # child_node is a sppasAttribute
                children.append(self.ObjectToItem(child_node))
            return len(node)

        return 0

    # -----------------------------------------------------------------------

    def IsContainer(self, item):
        """Return True if the item has children, False otherwise.

        :param item: (wx.dataview.DataViewItem)

        """
        # The hidden root is a container
        if not item:
            return True

        # In this model the path and root objects are containers
        node = self.ItemToObject(item)
        if isinstance(node, FileReference):
            return True

        # but everything else are not
        return False

    # -----------------------------------------------------------------------

    def GetParent(self, item):
        """Return the item which is this item's parent.

        :param item: (wx.dataview.DataViewItem)

        """
        node = self.ItemToObject(item)

        # Attribute has a FileReference parent
        if isinstance(node, sppasAttribute):
            for ref in self.__data.get_refs():
                if node in ref:
                    return self.ObjectToItem(ref)

        # The hidden root does not have a parent
        # A FileReference does not have a parent
        return wx.dataview.NullDataViewItem

    # -----------------------------------------------------------------------
    # Manage the values to display
    # -----------------------------------------------------------------------

    def HasValue(self, item, col):
        """Overridden.

        Return True if there is a value in the given column of this item.

        """
        # Fetch the data object for this item.
        node = self.ItemToObject(item)

        if self.__mapper[col].get_id() == "state":
            if isinstance(node, sppasAttribute) is True:
                return False
        return True

    # -----------------------------------------------------------------------

    def GetValue(self, item, col):
        """Return the value to be displayed for this item and column.

        :param item: (wx.dataview.DataViewItem)
        :param col: (int) Column index.

        Pull the values from the data objects we associated with the items
        in GetChildren.

        """
        # Fetch the data object for this item.
        node = self.ItemToObject(item)

        if isinstance(node, (FileReference, sppasAttribute)) is False:
            raise RuntimeError("Unknown node type {:s}".format(type(node)))

        value = self.__mapper[col].get_value(node)
        return value

    # -----------------------------------------------------------------------

    def HasContainerColumns(self, item):
        """Overridden.

        :param item: (wx.dataview.DataViewItem)

        We override this method to indicate if a container item merely acts
        as a headline (or for categorisation) or if it also acts a normal
        item with entries for further columns.

        """
        node = self.ItemToObject(item)
        if isinstance(node, FileReference):
            return True
        return False

    # -----------------------------------------------------------------------

    def SetValue(self, value, item, col):
        """Overridden.

        :param value:
        :param item: (wx.dataview.DataViewItem)
        :param col: (int)

        """
        logging.debug("SetValue: %s\n" % value)

        node = self.ItemToObject(item)
        if isinstance(node, (FileReference, sppasAttribute)) is False:
            raise RuntimeError("Unknown node type {:s}".format(type(node)))

        if isinstance(node, FileReference):
            if self.__mapper[col].get_id() == "state":
                if isinstance(value, (States, int)):
                    v = value
                else:
                    logging.error("Can't set state {:d} to object {:s}".format(value, node))
                    return False

                self.__data.set_object_state(v, node)

        if isinstance(node, sppasAttribute):
            if self.__mapper[col].get_id() == "attvalue":
                node.set_value(value)
            if self.__mapper[col].get_id() == "attdescr":
                node.set_description(value)

        return True

    # -----------------------------------------------------------------------

    def GetAttr(self, item, col, attr):
        """Overridden. Indicate that the item has special font attributes.

        This only affects the DataViewTextRendererText renderer.

        :param item: (wx.dataview.DataViewItem) – The item for which the attribute is requested.
        :param col: (int) – The column of the item for which the attribute is requested.
        :param attr: (wx.dataview.DataViewItemAttr) – The attribute to be filled in if the function returns True.
        :returns: (bool) True if this item has an attribute or False otherwise.

        """
        node = self.ItemToObject(item)

        # default colors for foreground and background
        if self._fgcolor is not None:
            attr.SetColour(self._fgcolor)
        if self._bgcolor is not None:
            attr.SetBackgroundColour(self._bgcolor)

        if isinstance(node, FileReference):
            attr.SetBold(True)
            return True

        if isinstance(node, sppasAttribute):
            return True

        return False

    # -----------------------------------------------------------------------
    # Manage the data
    # -----------------------------------------------------------------------

    def update(self):
        """Update the data and refresh the tree."""
        self.__data.update()
        self.Cleared()

    # -----------------------------------------------------------------------

    def create_ref(self, ref_name, ref_type):
        """Create a new Reference and add it into the data.

        :param ref_name: (str)
        :param ref_type: (str or int)

        """
        r = FileReference(ref_name)
        r.set_type(ref_type)
        self.__data.add_ref(r)
        item = self.ObjectToItem(r)
        self.Cleared()
        return item

    # -----------------------------------------------------------------------

    def add_refs(self, entries):
        """Add a set of refs in the data.

        :param entries: (list of FileReference)

        """
        added_refs = list()
        for entry in entries:
            try:
                self.__add(entry)
                added_refs.append(entry)
            except ValueError as e:
                logging.error(' ... reference {:s} not added: {:s}.'.format(entry, str(e)))

        if len(added_refs) > 0:
            self.Cleared()
        return len(added_refs)

    # -----------------------------------------------------------------------

    def __add(self, entry):
        if isinstance(entry, FileReference):
            return self.__data.add_ref(entry)
        else:
            logging.error('{!s:s} not added.'.format(str(entry)))

        return False

    # -----------------------------------------------------------------------

    def has_checked_refs(self):
        """Return True if at least one reference is checked."""
        return len(self.__data.get_reference_from_state(States().CHECKED)) > 0

    # -----------------------------------------------------------------------

    def get_checked_refs(self):
        """Return checked references."""
        return self.__data.get_reference_from_state(States().CHECKED)

    # -----------------------------------------------------------------------

    def remove_checked_refs(self):
        """Remove all FileReference with state CHECKED."""
        nb_removed = self.__data.remove_refs(States().CHECKED)
        if nb_removed > 0:
            self.__data.update()
            self.Cleared()
        return nb_removed

    # -----------------------------------------------------------------------

    def remove_attribute(self, identifier):
        """Remove an attribute from the checked references.

        :param identifier: (str)

        """
        nb = 0
        for ref in self.__data.get_refs():
            if ref.state == States().CHECKED and identifier in ref:
                item = self.ObjectToItem(ref.att(identifier))
                ref.pop(identifier)
                self.ItemDeleted(self.ObjectToItem(ref), item)
                nb += 1
        return nb

    # -----------------------------------------------------------------------

    def edit_attribute(self, identifier, value, att_type, description):
        """Append or modify an attribute of the checked references.

        :param identifier: (str)
        :param value: (str)
        :param att_type: (str)
        :param description: (str)

        """
        nb = 0
        if len(value.strip()) == 0:
            value = None
        if len(description.strip()) == 0:
            description = None
        for ref in self.__data.get_refs():
            if ref.state == States().CHECKED:
                att = ref.att(identifier)
                if att is None:
                    att = sppasAttribute(identifier, value, att_type, description)
                    ref.append(att)
                    item = self.ObjectToItem(att)
                    self.ItemAdded(self.ObjectToItem(ref), item)
                else:
                    item = self.ObjectToItem(att)
                    att.set_value(value)
                    att.set_value_type(att_type)
                    att.set_description(description)
                    self.ItemChanged(item)

                nb += 1
                if ref.subjoined is None:
                    ref.subjoined = dict()
                ref.subjoined['expand'] = True

        return nb

    # -----------------------------------------------------------------------

    def expand(self, value=True, item=None):
        """Set the expand value to the object matching the item or to all.

        :param value: (bool) Expanded (True) or Collapsed (False)
        :param item: (wx.dataview.DataViewItem or None)

        """
        if item is None:
            for fc in self.__data.get_refs():
                if fc.subjoined is None:
                    fc.subjoined = dict()
                fc.subjoined['expand'] = bool(value)

        else:
            obj = self.ItemToObject(item)
            if isinstance(obj, FileReference):
                if obj.subjoined is None:
                    obj.subjoined = dict()
                obj.subjoined['expand'] = bool(value)

    # -----------------------------------------------------------------------

    def get_expanded_items(self, value=True):
        """Return the list of expanded or collapsed items.

        :param value: (bool)

        """
        items = list()
        for fc in self.__data.get_refs():
            if fc.subjoined is not None:
                if 'expand' in fc.subjoined:
                    if fc.subjoined['expand'] is value:
                        items.append(self.ObjectToItem(fc))

        return items

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    @staticmethod
    def __create_col(name):
        if name == "state":
            col = ColumnProperties(" ", name, "wxBitmap")
            col.add_fct_name(FileReference, "get_state")
            col.width = 36
            col.align = wx.ALIGN_CENTRE
            col.renderer = StateIconRenderer()
            return col

        if name == "refs":
            col = ColumnProperties("Ref. Id.", name)
            col.add_fct_name(sppasAttribute, "get_id")
            col.add_fct_name(FileReference, "get_id")
            col.width = 120
            return col

        if name == "attvalue":
            col = ColumnProperties("Value", name)
            col.add_fct_name(sppasAttribute, "get_value")
            col.width = 100
            col.align = wx.ALIGN_LEFT
            col.mode = wx.dataview.DATAVIEW_CELL_EDITABLE
            return col

        if name == "attvaluetype":
            col = ColumnProperties("Type", name)
            col.add_fct_name(sppasAttribute, "get_description")
            col.add_fct_name(FileReference, "get_type")
            col.add_fct_name(sppasAttribute, "get_value_type")
            col.width = 80
            col.align = wx.ALIGN_LEFT
            return col

        if name == "attdescr":
            col = ColumnProperties("Description", name)
            col.add_fct_name(sppasAttribute, "get_description")
            col.width = 200
            col.align = wx.ALIGN_LEFT
            col.mode = wx.dataview.DATAVIEW_CELL_EDITABLE
            return col

        col = ColumnProperties("", name)
        col.width = 80
        return col
