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

    ui.phoenix.page_analyze.listview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ListViewPanel displays the content of a file as a list ctrl.

"""

import os
import wx
import wx.dataview

from sppas import sg
from sppas import paths
from sppas import u
from sppas import msg

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasHierarchy
from sppas.src.anndata import sppasCtrlVocab
from sppas.src.anndata import sppasMetaData
from sppas.src.config import ui_translation

from ..main_events import ViewEvent
from ..windows import sppasPanel
from ..windows import sppasCollapsiblePanel
from ..windows.baseviewctrl import BaseTreeViewCtrl
from ..windows.baseviewctrl import ColumnProperties
from ..windows.baseviewctrl import ToggledIconRenderer

# ---------------------------------------------------------------------------


class TrsViewCtrl(BaseTreeViewCtrl):
    """A control to display the content of a sppasTranscription as a list.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Columns of this class are defined by the model and created by the
    constructor.

    """

    def __init__(self, parent, filename="", name="listview-ctrl"):
        """Constructor of the TrsViewCtrl.

        :param parent: (wx.Window)
        :param name: (str)

        """
        super(TrsViewCtrl, self).__init__(parent, name)

        # Create an instance of our model and associate to the view.
        self._model = TrsViewModel(filename)
        self.AssociateModel(self._model)
        self._model.DecRef()

        # Create the columns that the model wants in the view.
        for i in range(self._model.GetColumnCount()):
            col = BaseTreeViewCtrl._create_column(self._model, i)
            wx.dataview.DataViewCtrl.AppendColumn(self, col)

        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self._on_item_activated)
        self.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self._on_item_selection_changed)

        h = self.get_line_height() * 2
        h *= self._model.get_nb_lines()
        self.SetMinSize(wx.Size(-1, h))

    # ------------------------------------------------------------------------

    def Layout(self):
        h = self.get_line_height() * 2
        h *= self._model.get_nb_lines()
        self.SetMinSize(wx.Size(-1, h))
        wx.Window.Layout(self)

    # ------------------------------------------------------------------------

    def _on_item_activated(self, event):
        """Happens when the user activated a cell (double-click).

        This event is triggered by double clicking an item or pressing some
        special key (usually "Enter") when it is focused.

        """
        item = event.GetItem()
        if item is not None:
            self._model.check(event.GetColumn(), item)
            self.Unselect(item)

    # ------------------------------------------------------------------------

    def _on_item_selection_changed(self, event):
        """Happens when the user simple-click a cell.

        """
        item = event.GetItem()
        if item is not None:
            self._model.check(event.GetColumn(), item)
            self.Unselect(item)

    # -----------------------------------------------------------------------

    def get_line_height(self):
        font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))

# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------


class TrsViewModel(wx.dataview.PyDataViewModel):
    """A class that is a DataViewModel combined with an object mapper.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, filename):
        """Constructor of a TrsViewModel.

        """
        wx.dataview.PyDataViewModel.__init__(self)

        self.__nb_lines = 1
        self._data = sppasTranscription()
        self.set_data(filename)

        # Map between the displayed columns and the workspace data
        self.__mapper = dict()
        self.__mapper[0] = TrsViewModel.__create_col("", "icon")
        self.__mapper[1] = TrsViewModel.__create_col(ui_translation.gettext('Data type'), "type")
        self.__mapper[2] = TrsViewModel.__create_col(ui_translation.gettext('Name'), "name")
        self.__mapper[3] = TrsViewModel.__create_col(ui_translation.gettext('Size'), "size")

        # GUI information which can be managed by the mapper
        self._bgcolor = wx.BLACK
        self._fgcolor = wx.WHITE

    # -----------------------------------------------------------------------

    def get_nb_lines(self):
        return self.__nb_lines
    
    # -----------------------------------------------------------------------
    # Manage the data
    # -----------------------------------------------------------------------

    def set_data(self, filename):
        parser = sppasRW(filename)
        self.__nb_lines = 2
        self._data = parser.read()
        self._data.set_meta("checked", "False")
        # self._data.get_hierarchy().set_meta("checked", "False")
        for tier in self._data.get_tier_list():
            tier.set_meta("checked", "False")
            self.__nb_lines += 1
        for media in self._data.get_media_list():
            media.set_meta("checked", "False")
            self.__nb_lines += 1
        for vocab in self._data.get_ctrl_vocab_list():
            vocab.set_meta("checked", "False")
            self.__nb_lines += 1

    # -----------------------------------------------------------------------

    def check(self, col, item):
        """Change state value.

        :param col: (int) Column index.
        :param item: (wx.dataview.DataViewItem)

        """
        try:
            if item is None:
                return
            node = self.ItemToObject(item)
            if node is None:
                return
        except:
            return
        cur_state = TrsViewModel.str_to_bool(node.get_meta("checked", "False"))

        cur_state = not cur_state
        try:
            node.set_meta("checked", str(cur_state))
            self.ItemChanged(item)
        except Exception as e:
            wx.LogMessage('Value not modified for node {:s}'.format(node))
            wx.LogError(str(e))

    # -----------------------------------------------------------------------

    @staticmethod
    def str_to_bool(value):
        if value.lower() == "true":
            return True
        try:
            if value.isdigit() and int(value) > 0:
                return True
        except AttributeError:
            pass
        return False

    # -----------------------------------------------------------------------
    # Manage column properties
    # -----------------------------------------------------------------------

    def get_col_idx(self, name):
        for c in self.__mapper:
            if self.__mapper[c].get_id() == name:
                return c
        return -1

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        self._bgcolor = color
        wx.LogDebug("* * * * * * * * New bgcolor = {:s}".format(str(color)))

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        self._fgcolor = color
        wx.LogDebug("ListView * * * * * * * * New fgcolor = {:s}".format(str(color)))

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
            children.append(self.ObjectToItem(self._data))
            i = 1
            for tier in self._data.get_tier_list():
                children.append(self.ObjectToItem(tier))
                i += 1
            for media in self._data.get_media_list():
                children.append(self.ObjectToItem(media))
                i += 1
            for vocab in self._data.get_ctrl_vocab_list():
                children.append(self.ObjectToItem(vocab))
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
        node = self.ItemToObject(item)
        checked = node.get_meta("checked", "False")
        if checked == "True":
            attr.SetBold(True)

        # default colors for foreground and background
        attr.SetColour(self._fgcolor)
        attr.SetBackgroundColour(self._bgcolor)

        return True

    # -----------------------------------------------------------------------
    # Manage the items
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
        col_id = self.__mapper[col].get_id()

        if col_id == "icon":
            value = node.get_meta("checked", "False")
            if value == "True":
                value = True
            else:
                value = False

        elif col_id == "type":
            t = str(type(node))
            t = t.split('.')[-1]
            t = t.replace("sppas", "")
            t = t[:-2]
            return t

        elif col_id == "size":
            if isinstance(node, sppasTier):
                # number of annotations
                value = str(len(node))
            else:
                value = ""

        else:
            value = "Metadata"
            if node != self._data:
                # Get the value of the object
                value = str(self.__mapper[col].get_value(node))

        return value

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_col(title, name):
        if name == "icon":
            col = ColumnProperties(title, name, "wxBitmap")
            col.width = sppasPanel.fix_size(30)
            col.align = wx.ALIGN_CENTRE
            col.renderer = ToggledIconRenderer()

        elif name == "name":
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(180)
            col.align = wx.ALIGN_LEFT
            col.add_fct_name(sppasTier, "get_name")
            col.add_fct_name(sppasMedia, "get_filename")
            col.add_fct_name(sppasCtrlVocab, "get_name")

        else:
            # type (=tier/ctrlvocab/media/metadata...)
            col = ColumnProperties(title, name)
            col.width = sppasPanel.fix_size(80)
            col.align = wx.ALIGN_CENTER
            # col.add_fct_name(FileFormatProperty, "get_support", name)

        return col

# ---------------------------------------------------------------------------


class TrsViewPanel(sppasCollapsiblePanel):
    """A panel to display the content of a sppasTranscription as a list.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, filename, name="listview-panel"):
        super(TrsViewPanel, self).__init__(parent, label=filename, name=name)

        self.SetPane(TrsViewCtrl(self, filename=filename))
        self.Expand()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-salign.xra")
        p1 = TrsViewPanel(self, f1)
        p2 = TrsViewPanel(self, f2)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p1)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.EXPAND)
        sizer.Add(p2, 0, wx.EXPAND)

        self.SetBackgroundColour(wx.Colour(28, 28, 28))
        self.SetForegroundColour(wx.Colour(228, 228, 228))

        self.SetSizerAndFit(sizer)
        self.Layout()
        self.SetAutoLayout(True)

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
