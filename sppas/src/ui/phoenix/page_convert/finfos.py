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

import logging
import wx
import wx.lib.newevent
import wx.dataview

from sppas.src.config import ui_translation
from sppas.src.anndata import sppasRW

from ..windows import sppasPanel
from ..windows import sppasStaticText
from ..windows.baseviewctrl import BaseTreeViewCtrl
from ..windows.baseviewctrl import SelectedIconRenderer
from ..windows.baseviewctrl import ColumnProperties

# ---------------------------------------------------------------------------
# Internal use of an event, when a format is selected

FormatChangedEvent, EVT_FORMAT_CHANGED = wx.lib.newevent.NewEvent()
FormatChangedCommandEvent, EVT_FORMAT_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


class FileSupports:

    supports = {
        "metadata_support": ui_translation.gettext('Metadata'),
        "point_support": ui_translation.gettext('Point'),
        "interval_support": ui_translation.gettext('Interval'),
        "alternative_localization_support": ui_translation.gettext('Alt. loc'),
        "alternative_tag_support": ui_translation.gettext('Alt. tag'),
        "radius_support": ui_translation.gettext('Vagueness'),
        "gaps_support": ui_translation.gettext('Gaps'),
        "overlaps_support": ui_translation.gettext('Overlaps'),
        "multi_tiers_support": ui_translation.gettext('Multi tiers'),
        "no_tiers_support": ui_translation.gettext('No tier'),
        "hierarchy_support": ui_translation.gettext('Hierarchy'),
        "ctrl_vocab_support": ui_translation.gettext('Ctrl vocab'),
        "media_support": ui_translation.gettext('Media'),
    }

# ---------------------------------------------------------------------------


class FileFormatProperty:

    def __init__(self, extension):

        self.extension = "." + extension
        self.instance = sppasRW.TRANSCRIPTION_TYPES[extension]()
        self.software = self.instance.software

        try:
            self.instance.read("")
        except NotImplementedError:
            self.reader = False
        except Exception:
            self.reader = True
        try:
            self.instance.write("")
        except NotImplementedError:
            self.writer = False
        except Exception:
            self.writer = True

    def get_extension(self):
        return self.extension

    def get_software(self):
        return self.software

    def get_reader(self):
        return self.reader

    def get_writer(self):
        return self.writer

    def get_support(self, name):
        if name in FileSupports.supports:
            return getattr(self.instance, name)()
        return False

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __str__(self):
        return 'FileFormatProperty of extension {!s:s}'.format(self.extension)

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
        super(FormatsViewCtrl, self).__init__(parent, name)

        # Create an instance of our model and associate to the view.
        self._model = FormatsViewModel()
        self.AssociateModel(self._model)
        self._model.DecRef()

        # Create the columns that the model wants in the view.
        for i in range(self._model.GetColumnCount()):
            col = BaseTreeViewCtrl._create_column(self._model, i)
            wx.dataview.DataViewCtrl.AppendColumn(self, col)

        # Bind events.
        # Used to remember the expend/collapse status of items after a refresh.
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self._on_item_activated)
        self.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self._on_item_selection_changed)

    # ------------------------------------------------------------------------

    def _on_item_activated(self, event):
        """Happens when the user activated a cell (double-click).

        This event is triggered by double clicking an item or pressing some
        special key (usually "Enter") when it is focused.

        """
        item = event.GetItem()
        if item is not None:
            self._model.change_value(item)

    # ------------------------------------------------------------------------

    def _on_item_selection_changed(self, event):
        """Happens when the user simple-click a cell.

        """
        item = event.GetItem()
        if item is not None:
            self._model.change_value(item)

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

    This model mapper provides these data columns identifiers:

        0. radio:      wxBitmap
        1. ext:        string
        2. software:   string
        3. reader:     string
        4. writer:     string
        5- all supported properties

    """

    def __init__(self):
        """Constructor of a FormatsViewModel.

        """
        wx.dataview.PyDataViewModel.__init__(self)

        # Map between the displayed columns and the workspace data
        self.__mapper = dict()
        self.__mapper[0] = FormatsViewModel.__create_col("", "icon")
        self.__mapper[1] = FormatsViewModel.__create_col(ui_translation.gettext('Extension'), "get_extension")
        self.__mapper[2] = FormatsViewModel.__create_col(ui_translation.gettext('Software'), "get_software")
        self.__mapper[3] = FormatsViewModel.__create_col(ui_translation.gettext('Reader'), 'get_reader')
        self.__mapper[4] = FormatsViewModel.__create_col(ui_translation.gettext('Writer'), 'get_writer')
        for i, c in enumerate(FileSupports.supports):
            t = FileSupports.supports[c]
            self.__mapper[i+5] = FormatsViewModel.__create_col(t, c)

        # GUI information which can be managed by the mapper
        self._bgcolor = None
        self._fgcolor = None

        # The items to display
        self.__extensions = list(sppasRW.TRANSCRIPTION_TYPES.keys())

    # -----------------------------------------------------------------------
    # Manage the data
    # -----------------------------------------------------------------------

    def change_value(self, item):
        """Change state value.

        :param item: (wx.dataview.DataViewItem)

        """
        logging.debug("CHANGE VALUE")
        if item is None:
            return
        node = self.ItemToObject(item)
        # Node is a FileFormatProperty
        logging.debug("CHANGE VALUE for NODE {:s}".format(node))

        self.Cleared()

    # -----------------------------------------------------------------------
    # Manage column properties
    # -----------------------------------------------------------------------

    def GetColumnCount(self):
        """Overridden. Report how many columns this model provides data for."""
        logging.debug("GetColumnCount")
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
        logging.debug("GetChildren")
        if not parent:
            i = 0
            for ext in self.__extensions:
                ext_object = FileFormatProperty(ext)
                children.append(self.ObjectToItem(ext_object))
                i += 1
            return i
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
        if self.__mapper[col].get_id() == "icon":
            return False

        else:
            # Fetch the data object for this item.
            node = self.ItemToObject(item)
            value = str(self.__mapper[col].get_value(node))
            if value == "true":
                value = "X"
            elif value == "false":
                value = ""
            # Return the value of the function we defined when column was created
        logging.debug("GetValue of col={:d} = {:s}".format(col, value))

        return value

    # -----------------------------------------------------------------------

    def SetValue(self, value, item, col):
        """Overridden.

        :param value:
        :param item: (wx.dataview.DataViewItem)
        :param col: (int)

        """
        logging.debug("SetValue of col={:d}".format(col))
        node = self.ItemToObject(item)
        logging.debug("Set value to node: {:s}".format(str(node)))
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
            col.width = sppasPanel.fix_size(50)
            col.add_fct_name("string", "get_extension")

        elif name == "software":
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(80)
            col.add_fct_name("string", "get_software")

        elif name in ["reader", "writer"]:
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(80)
            col.add_fct_name("bool", "get_"+name)

        else:
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(60)
            col.add_fct_name("bool", "get_support", name)

        return col

# ---------------------------------------------------------------------------


class sppasFormatInfos(sppasPanel):
    """Create the list of file formats with their capabilities.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="panel_format_infos"):
        super(sppasFormatInfos, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE,
            name=name
        )

        self.__selected = -1
        self._create_content()
        self.Layout()

    # -----------------------------------------------------------------------

    def CancelSelected(self):
        """Unselect the currently selected format."""
        # We already had a selected row
        if self.__selected != -1:
            self.FindWindow("dvlc").SetValue(False, self.__selected, 0)

        # OK. No selected row.
        self.__selected = -1

    # -----------------------------------------------------------------------
    # Create and manage the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        info_txt = sppasStaticText(
            self,
            label="Select the file type to convert to: ")
        dvlc = FormatsViewCtrl(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(info_txt, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer.Add(dvlc, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __set_selected(self, event):
        dvlc = self.FindWindow("dvlc")
        selected = dvlc.GetSelectedRow()
        if selected == self.__selected:
            return

        # We already had a selected row
        if self.__selected != -1:
            #dvlc.SetValue(False, self.__selected, 0)
            pass

        # Set the new selected row
        self.__selected = selected
        #dvlc.SetValue(True, self.__selected, 0)

        # Unselect the row in the dataview to remove the "highlighted" color
        dvlc.UnselectRow(selected)

        # the parent will decide what to exactly do with this change
        evt = FormatChangedEvent(extension=self.__extensions[self.__selected])
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

