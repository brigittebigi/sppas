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

    ui.phoenix.page_convert.finfos.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Display information about annotated file formats.

"""

import wx
import wx.lib.newevent
import wx.dataview

from sppas.src.config import ui_translation
from sppas.src.anndata import sppasRW
from sppas.src.anndata import FileFormatProperty

from ..windows import sppasPanel
from ..windows.baseviewctrl import BaseTreeViewCtrl
from ..windows.baseviewctrl import SelectedIconRenderer
from ..windows.baseviewctrl import YesNoIconRenderer
from ..windows.baseviewctrl import ColumnProperties

# ---------------------------------------------------------------------------
# Internal use of an event, when a format is selected

FormatChangedEvent, EVT_FORMAT_CHANGED = wx.lib.newevent.NewEvent()
FormatChangedCommandEvent, EVT_FORMAT_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


class FileSupports:

    supports = {
        "metadata_support": ui_translation.gettext('Metadata'),
        "multi_tiers_support": ui_translation.gettext('Multi tiers'),
        "no_tiers_support": ui_translation.gettext('No tier'),
        "point_support": ui_translation.gettext('Point'),
        "interval_support": ui_translation.gettext('Interval'),
        "gaps_support": ui_translation.gettext('Gaps'),
        "overlaps_support": ui_translation.gettext('Overlaps'),
        "hierarchy_support": ui_translation.gettext('Hierarchy'),
        "ctrl_vocab_support": ui_translation.gettext('Ctrl vocab'),
        "media_support": ui_translation.gettext('Media'),
        "radius_support": ui_translation.gettext('Vagueness'),
        "alternative_localization_support": ui_translation.gettext('Alt. loc'),
        "alternative_tag_support": ui_translation.gettext('Alt. tag'),
    }

# ---------------------------------------------------------------------------


class FileFormatPropertySupport(FileFormatProperty):
    """Represent one format and its properties.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, extension):
        """Create a FileFormatProperty instance.

        :param extension: (str) File name extension.

        """
        super(FileFormatPropertySupport, self).__init__(extension)

    # -----------------------------------------------------------------------

    def get_support(self, name):
        if name in list(FileSupports.supports.keys()):
            return getattr(self._instance, name)()
        return False

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __str__(self):
        return 'FileFormatProperty() of extension {!s:s}' \
               ''.format(self._extension)

# ---------------------------------------------------------------------------
# The DataViewCtrl to display the list of file formats and to select one.
# ---------------------------------------------------------------------------


class FormatsViewCtrl(BaseTreeViewCtrl):
    """A control to display data file formats and their properties.

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
        """Constructor of the FormatsViewCtrl.

        :param parent: (wx.Window)
        :param name: (str)

        """
        super(FormatsViewCtrl, self).__init__(parent, name=name)

        # Create an instance of our model and associate to the view.
        self._model = FormatsViewModel()
        self.AssociateModel(self._model)
        self._model.DecRef()

        # Create the columns that the model wants in the view.
        for i in range(self._model.GetColumnCount()):
            col = BaseTreeViewCtrl._create_column(self._model, i)
            wx.dataview.DataViewCtrl.AppendColumn(self, col)

        # Bind events.
        # Used to select/unselect one of the displayed file formats
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED,
                  self._on_item_activated)
        self.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED,
                  self._on_item_selection_changed)

        # Ensure the whole table is visible (no scrollbar)
        try:
            nb_rows = 2 + len(sppasRW.TRANSCRIPTION_TYPES.keys())
            font = wx.GetApp().settings.text_font
            font_height = font.GetPointSize()
            self.SetRowHeight(font_height * 2)
            h = font_height * 2 * nb_rows
            self.SetMinSize(wx.Size(-1, h))
        except:
            self.SetMinSize(wx.Size(-1, 200))

    # ------------------------------------------------------------------------

    def _on_item_activated(self, event):
        """Happens when the user activated a cell (double-click).

        This event is triggered by double clicking an item or pressing some
        special key (usually "Enter") when it is focused.

        """
        item = event.GetItem()
        if item is not None:
            changed = self._model.change_value(item)
            if changed is True:
                # the parent will decide what to exactly do with this change
                evt = FormatChangedEvent(extension=self._model.get_selected())
                evt.SetEventObject(self)
                wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def _on_item_selection_changed(self, event):
        """Happens when the user simple-click a cell.

        """
        item = event.GetItem()
        if item is not None:
            changed = self._model.change_value(item)
            if changed is True:
                # the parent will decide what to exactly do with this change
                evt = FormatChangedEvent(extension=self._model.get_selected())
                evt.SetEventObject(self)
                wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def CancelSelected(self):
        self._model.cancel_selected()

    # ------------------------------------------------------------------------

    def GetExtension(self):
        return self._model.get_selected()

# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------


class FormatsViewModel(wx.dataview.PyDataViewModel):
    """A class that is a DataViewModel combined with an object mapper.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Constructor of a FormatsViewModel.

        """
        wx.dataview.PyDataViewModel.__init__(self)

        # Map between the displayed columns and the workspace data
        self.__mapper = dict()
        self.__mapper[0] = FormatsViewModel.__create_col("", "icon")
        self.__mapper[1] = FormatsViewModel.__create_col(ui_translation.gettext('Extension'), "extension")
        self.__mapper[2] = FormatsViewModel.__create_col(ui_translation.gettext('Software'), "software")
        self.__mapper[3] = FormatsViewModel.__create_col(ui_translation.gettext('Reader'), 'reader')
        self.__mapper[4] = FormatsViewModel.__create_col(ui_translation.gettext('Writer'), 'writer')
        for i, c in enumerate(FileSupports.supports):
            t = FileSupports.supports[c]
            self.__mapper[i+5] = FormatsViewModel.__create_col(t, c)

        # GUI information which can be managed by the mapper
        self._bgcolor = None
        self._fgcolor = None

        # The items to display
        self.__extensions = list(sppasRW.TRANSCRIPTION_TYPES.keys())
        self.__selected = None

    # -----------------------------------------------------------------------
    # Manage the data
    # -----------------------------------------------------------------------

    def change_value(self, item):
        """Change state value.

        :param item: (wx.dataview.DataViewItem)

        """
        if item is None:
            return
        node = self.ItemToObject(item)
        # Node is a FileFormatProperty
        if node.get_extension() != self.__selected:
            self.__selected = node.get_extension()
            # self.Cleared() --> does not work with WXGTK. Replaced by:
            self.ValueChanged(item, self.get_col_idx("icon"))
            return True
        return False

    # -----------------------------------------------------------------------

    def get_selected(self):
        return self.__selected

    # -----------------------------------------------------------------------

    def cancel_selected(self):
        if self.__selected is not None:
            item = self.ObjectToItem(self.__selected)
            self.__selected = None
            # self.Cleared()  --> does not work with WXGTK. Replaced by:
            self.ValueChanged(item, self.get_col_idx("icon"))

    # -----------------------------------------------------------------------
    # Manage column properties
    # -----------------------------------------------------------------------

    def get_col_idx(self, name):
        for c in self.__mapper:
            if self.__mapper[c].get_id() == name:
                return c
        return -1

    # -----------------------------------------------------------------------

    def GetColumnCount(self):
        """Overridden. Report how many columns this model provides data for."""
        return len(self.__mapper)

    # -----------------------------------------------------------------------

    def GetColumnType(self, col):
        """Overridden. Map the data column number to the data type.

        :param col: (int)FileData()

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

    def GetChildren(self, parent, children):
        """The view calls this method to find the children of any node.

        There is an implicit hidden root node, and the top level
        item(s) should be reported as children of this node.

        """
        if not parent:
            i = 0
            for ext in self.__extensions:
                ext_object = FileFormatPropertySupport(ext)
                children.append(self.ObjectToItem(ext_object))
                i += 1
            return i

        # Otherwise we'll fetch the python object associated with the parent
        # item and make DV items for each of its child objects.
        return 0

    # -----------------------------------------------------------------------

    def GetParent(self, item):
        """Return the item which is this item's parent.

        :param item: (wx.dataview.DataViewItem)

        """
        return wx.dataview.NullDataViewItem

    # -----------------------------------------------------------------------

    def IsContainer(self, item):
        """Return True if the item has children, False otherwise.

        :param item: (wx.dataview.DataViewItem)

        """
        # The hidden root is a container
        if not item:
            return True

        # but everything else are not
        return False

    # -----------------------------------------------------------------------

    def GetAttr(self, item, col, attr):
        """Overridden. Indicate that the item has special font attributes.

        This only affects the DataViewTextRendererText renderer.

        :param item: (wx.dataview.DataViewItem) – The item for which the attribute is requested.
        :param col: (int) – The column of the item for which the attribute is requested.
        :param attr: (wx.dataview.DataViewItemAttr) – The attribute to be filled in if the function returns True.
        :returns: (bool) True if this item has an attribute or False otherwise.

        """
        if self._fgcolor is not None:
            attr.SetColour(self._fgcolor)
        if self._bgcolor is not None:
            attr.SetBackgroundColour(self._bgcolor)

        if self.__mapper[col].get_id() == "extension":
            attr.SetBold(True)

        return True

    # -----------------------------------------------------------------------
    # Manage the items
    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        self._bgcolor = color

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        self._fgcolor = color

    # -----------------------------------------------------------------------

    def HasValue(self, item, col):
        """Overridden.

        Return True if there is a value in the given column of this item.

        """
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

        if self.__mapper[col].get_id() == "icon":
            if self.__selected == node.get_extension():
                return True
            return False

        # Get the value of the object
        if self.__mapper[col].get_id() == "extension":
            return node.get_extension()

        elif self.__mapper[col].get_id() == "software":
            return node.get_software()

        else:
            value = self.__mapper[col].get_value(node)

        return value

    # -----------------------------------------------------------------------

    def SetValue(self, value, item, col):
        """Overridden.

        :param value:
        :param item: (wx.dataview.DataViewItem)
        :param col: (int)

        """
        wx.LogDebug("SetValue of col={:d}".format(col))
        node = self.ItemToObject(item)
        wx.LogDebug("Set value to node: {:s}".format(str(node)))
        node[col] = value

        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_col(title, name):
        if name == "icon":
            col = ColumnProperties(title, name, "wxBitmap")
            col.width = sppasPanel.fix_size(30)
            col.align = wx.ALIGN_CENTRE
            col.renderer = SelectedIconRenderer()

        elif name == "extension":
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(60)

        elif name == "software":
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(80)
            col.align = wx.ALIGN_CENTRE

        elif name in ["reader", "writer"]:
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(40)
            col.align = wx.ALIGN_CENTRE
            col.add_fct_name(FileFormatPropertySupport, "get_"+name)
            col.renderer = YesNoIconRenderer()

        else:
            # Only boolean values are displayed in the other columns
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(40)
            col.align = wx.ALIGN_CENTRE
            col.add_fct_name(FileFormatPropertySupport, "get_support", name)
            col.renderer = YesNoIconRenderer()

        return col
