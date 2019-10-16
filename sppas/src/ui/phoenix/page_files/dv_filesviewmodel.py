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

    src.ui.phoenix.page_files.filesviewmodel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This model acts as a bridge between a DataViewCtrl and a FileData.

"""

import unittest
import os
import wx
import wx.dataview

from sppas import sppasTypeError
from sppas.src.anndata import sppasRW
from sppas.src.files import States, FileName, FileRoot, FilePath, FileData

from sppas.src.ui.trash import sppasTrash
from ..tools import sppasSwissKnife
from ..windows.baseviewctrl import ColumnProperties
from ..windows.baseviewctrl import StateIconRenderer

# ---------------------------------------------------------------------------

   
class FileAnnotIcon(object):
    """Represents the link between a file extension and an icon name.
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    All supported file formats of 'anndata' are linked to an icon file.
    All 'wav' files are linked to an icon file.

    """

    def __init__(self):
        """Constructor of a FileAnnotIcon.

        Set the name of the icon for all known extensions of annotations.

        Create a dictionary linking a file extension to the name of the
        software it comes from. It is supposed this name is matching an
        an icon in PNG format.

        """
        self.__exticon = dict()
        self.__exticon['.WAV'] = "Audio"
        self.__exticon['.WAVE'] = "Audio"

        for ext in sppasRW.TRANSCRIPTION_TYPES:
            software = sppasRW.TRANSCRIPTION_TYPES[ext]().software
            if ext.startswith(".") is False:
                ext = "." + ext
            self.__exticon[ext.upper()] = software

    # -----------------------------------------------------------------------

    def get_icon_name(self, ext):
        """Return the name of the icon matching the given extension.

        :param ext: (str) An extension of an annotated or an audio file.
        :returns: (str) Name of an icon

        """
        if ext.startswith(".") is False:
            ext = "." + ext
        return self.__exticon.get(ext.upper(), "")

# ---------------------------------------------------------------------------


class FileIconRenderer(wx.dataview.DataViewCustomRenderer):
    """Draw an icon matching a known file extension.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self,
                 varianttype="wxBitmap",
                 mode=wx.dataview.DATAVIEW_CELL_INERT,
                 align=wx.dataview.DVR_DEFAULT_ALIGNMENT):
        super(FileIconRenderer, self).__init__(varianttype, mode, align)
        self.value = ""

    def SetValue(self, value):
        self.value = value
        return True

    def GetValue(self):
        return self.value

    def GetSize(self):
        """Return the size needed to display the value."""
        size = self.GetTextExtent('TT')
        return size[1]*2, size[1]*2

    def Render(self, rect, dc, state):
        """Draw the bitmap, adjusting its size. """
        if self.value == "":
            return False

        x, y, w, h = rect
        s = min(w, h)
        s = int(0.8 * s)

        bmp = sppasSwissKnife.get_bmp_icon(self.value, s)
        dc.DrawBitmap(bmp, x + (w-s)//2, y + (h-s)//2)

        return True

# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------


class FilesTreeViewModel(wx.dataview.PyDataViewModel):
    """A class that is a DataViewModel combined with an object mapper.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This model mapper provides these data columns identifiers:

        icon:     wxBitmap
        file:     string
        state:    int (one of the States() class)
        type:     string
        refs:     string
        data:     string
        size:     string

    """

    COLUMNS = ['file', 'icon', 'state', 'type', 'refs', 'date', 'size']

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

        # The icons to display depending on the file extension
        self.exticon = FileAnnotIcon()

        # Map between the displayed columns and the workspace data
        self.__mapper = dict()
        for i, c in enumerate(FilesTreeViewModel.COLUMNS):
            self.__mapper[i] = FilesTreeViewModel.__create_col(c)

        # GUI information which can be managed by the mapper
        self._bgcolor = None
        self._fgcolor = None

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
        wx.LogDebug('New data to set in the files panel. '
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
        """Returns column which have to contain the expanders.

        On MacOS it must be the first one (ie index = 0) because of the
        strange position of the expander symbol, but 1 is still "acceptable".

        """
        return FilesTreeViewModel.COLUMNS.index('file')

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
            for fp in self.__data:
                children.append(self.ObjectToItem(fp))
            return len(self.__data)

        # Otherwise we'll fetch the python object associated with the parent
        # item and make DV items for each of its child objects.
        node = self.ItemToObject(parent)
        if isinstance(node, (FilePath, FileRoot)):
            for f in node:
                children.append(self.ObjectToItem(f))
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
        if isinstance(node, (FilePath, FileRoot)):
            return True

        # but everything else (the file objects) are not
        return False

    # -----------------------------------------------------------------------

    def GetParent(self, item):
        """Return the item which is this item's parent.

        :param item: (wx.dataview.DataViewItem)

        """
        # The hidden root does not have a parent
        if item is None:
            return wx.dataview.NullDataViewItem

        node = self.ItemToObject(item)

        # A FilePath does not have a parent
        if isinstance(node, FilePath):
            return wx.dataview.NullDataViewItem

        # A FileRoot has a FilePath parent
        elif isinstance(node, FileRoot):
            for fp in self.__data:
                if node in fp:
                    return self.ObjectToItem(fp)

        # A FileName has a FileRoot parent
        elif isinstance(node, FileName):
            for fp in self.__data:
                for fr in fp:
                    #  if fp.get_id() == node.folder():
                    if node in fr:
                        return self.ObjectToItem(fr)

        return wx.dataview.NullDataViewItem

    # -----------------------------------------------------------------------
    # Manage the values to display
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
        if isinstance(node, (FileName, FileRoot, FilePath)) is False:
            raise RuntimeError("Unknown node type {:s}".format(type(node)))

        if self.__mapper[col].get_id() == "icon":
            if isinstance(node, FileName) is True:
                ext = node.get_extension()
                icon_name = self.exticon.get_icon_name(ext)
                return icon_name
            return ""

        if self.__mapper[col].get_id() == "refs":
            if isinstance(node, FileRoot) is True:
                # convert the list of FileReference instances into a string
                refs_ids = [ref.id for ref in node.get_references()]
                return " ".join(sorted(refs_ids))
            return ""

        return self.__mapper[col].get_value(node)

    # -----------------------------------------------------------------------

    def HasContainerColumns(self, item):
        """Overridden.

        :param item: (wx.dataview.DataViewItem)

        We override this method to indicate if a container item merely acts
        as a headline (or for categorisation) or if it also acts a normal
        item with entries for further columns.

        """
        node = self.ItemToObject(item)
        if isinstance(node, FileRoot):
            return True
        if isinstance(node, FilePath):
            return True
        return False

    # -----------------------------------------------------------------------

    def SetValue(self, value, item, col):
        """Overridden.

        :param value:
        :param item: (wx.dataview.DataViewItem)
        :param col: (int)

        """
        node = self.ItemToObject(item)
        if isinstance(node, (FileName, FileRoot, FilePath)) is False:
            raise RuntimeError("Unknown node type {:s}".format(type(node)))

        if self.__mapper[col].get_id() == "state":
            if isinstance(value, (States, int)):
                v = value
            else:
                wx.LogError("Can't set state {:d} to object {:s}".format(value, node))
                return False

            self.__data.set_object_state(v, node)

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

        if isinstance(node, FilePath):
            attr.SetBold(True)
            return True

        if isinstance(node, FileRoot):
            attr.SetItalic(True)
            return True

        if isinstance(node, FileName):
            # parent_root = self.GetParent(item)
            # parent_path = self.GetParent(parent_root)
            # if node.lock:
            #    attr.SetColour(wx.Colour(128, 128, 128))
            return True

        return False

    # -----------------------------------------------------------------------
    # Manage the data
    # -----------------------------------------------------------------------

    def change_value(self, col, item):
        """Change state value.

        :param col: (int) Column index.
        :param item: (wx.dataview.DataViewItem)

        """
        try:
            node = self.ItemToObject(item)
        except Exception as e:
            wx.LogWarning("No node is matching the item to change its state "
                          "value: {:s}.".format(str(e)))
            return
        cur_state = node.get_state()
        if cur_state in (States().UNUSED, States().AT_LEAST_ONE_CHECKED, States().AT_LEAST_ONE_LOCKED):
            try:
                modified = self.__data.set_object_state(States().CHECKED, node)
                if modified is False and cur_state == States().AT_LEAST_ONE_LOCKED:
                    modified = self.__data.set_object_state(States().UNUSED, node)
                if modified:
                    self.__item_changed(item)

            except Exception as e:
                wx.LogMessage('Value not modified for node {:s}'.format(node))
                wx.LogError(str(e))

        elif cur_state == States().CHECKED:
            try:
                self.__data.set_object_state(States().UNUSED, node)
                self.__item_changed(self.ObjectToItem(node))
            except Exception as e:
                wx.LogMessage('Value not modified for node {:s}'.format(node))
                wx.LogError(str(e))

        else:
            wx.LogWarning("{:s} is locked. It's state can't be changed "
                          "until it is un-locked.".format(node))

    # -----------------------------------------------------------------------

    def __item_changed(self, item):
        node = self.ItemToObject(item)
        self.ItemChanged(item)
        if isinstance(node, FileName):
            parent_item = self.GetParent(item)
            self.ItemChanged(parent_item)
            self.ItemChanged(self.GetParent(parent_item))
        if isinstance(node, FileRoot):
            self.ItemChanged(self.GetParent(item))
            for fn in node:
                self.ItemChanged(self.ObjectToItem(fn))
        if isinstance(node, FilePath):
            for fr in node:
                self.ItemChanged(self.ObjectToItem(fr))
                for fn in fr:
                    self.ItemChanged(self.ObjectToItem(fn))

    # -----------------------------------------------------------------------

    def update(self):
        """Update the data and refresh the tree."""
        self.__data.update()
        self.Cleared()

    # -----------------------------------------------------------------------

    def add_files(self, entries):
        """Add a set of files or folders in the data.

        :param entries: (list of str) FileName or folder with absolute path.

        """
        added_files = list()
        for entry in entries:
            fns = self.__add(entry)
            if len(fns) > 0:
                added_files.extend(fns)

        added_items = list()
        if len(added_files) > 0:
            self.update()
            for f in added_files:
                added_items.append(self.ObjectToItem(f))

        return added_items

    # -----------------------------------------------------------------------

    def __add(self, entry):
        """Add a file or a folder in the data.

        :param entry: (str)

        """
        fns = list()
        if os.path.isdir(entry):
            for f in sorted(os.listdir(entry)):
                fullname = os.path.join(entry, f)
                try:
                    new_fns = self.__data.add_file(fullname)
                    if new_fns is not None:
                        fns.extend(new_fns)
                        wx.LogDebug('{:s} added in workspace.'.format(entry))
                except OSError as e:
                    wx.LogError('{:s} not added in workspace: {:s}'
                                ''.format(fullname, str(e)))

        elif os.path.isfile(entry):
            try:
                new_fns = self.__data.add_file(entry, brothers=True)
                if new_fns is not None:
                    fns.extend(new_fns)
                    wx.LogDebug('{:s} added.\n{:d} brother files added in '
                                'workspace.'.format(entry, len(new_fns)))
            except Exception as e:
                wx.LogError('{:s} not added in workspace: {:s}.'
                            ''.format(entry, str(e)))

        else:
            wx.LogError('{:s} not added in workspace (not a regular file'
                        'nor a directory).'.format(entry))

        return fns

    # -----------------------------------------------------------------------

    def remove_checked_files(self):
        """Remove all FileName with state CHECKED."""
        nb_removed = self.__data.remove_files(States().CHECKED)
        if nb_removed > 0:
            self.update()
        return nb_removed

    # -----------------------------------------------------------------------

    def delete_checked_files(self):
        """Delete all FileName with state CHECKED."""
        checked = self.__data.get_filename_from_state(States().CHECKED)
        if len(checked) == 0:
            return

        nb_deleted = 0
        for fn in checked:
            try:
                # move the file into the trash of SPPAS
                sppasTrash().put_file_into(fn.id)
                nb_deleted += 1

            except Exception as e:
                wx.LogError("File {!s:s} can't be deleted due to the "
                            "following error: {:s}.".format(fn.id, str(e)))

        if nb_deleted > 0:
            self.update()
            wx.LogMessage('{:d} files moved into the trash.'
                          ''.format(nb_deleted))

        return nb_deleted

    # -----------------------------------------------------------------------

    def get_checked_files(self):
        """Return the list of FileName with state CHECKED."""
        return self.__data.get_filename_from_state(States().CHECKED)

    # -----------------------------------------------------------------------

    def lock(self, entries):
        """Change state to LOCKED of a list of entries.

        :param entries: (list of FileBase)

        """
        for entry in entries:
            if isinstance(entry, FileName) is False:
                node = self.__data.get_object(entry)
            else:
                node = entry
            self.__data.set_object_state(States().LOCKED, node)
            self.ItemChanged(self.ObjectToItem(node))

    # -----------------------------------------------------------------------

    def set_state(self, value=States().CHECKED, entry=None):
        """Check or uncheck all or any file.

        :param value: (int) One of the States()
        :param entry: (str) Absolute or relative name of a file or a file root

        """
        self.__data.set_object_state(value, entry)
        self.update()

    # -----------------------------------------------------------------------

    def expand(self, value=True, item=None):
        """Set the expand value to the object matching the item or to all.

        :param value: (bool) Expanded (True) or Collapsed (False)
        :param item: (wx.dataview.DataViewItem or None)

        """
        if item is None:
            for fp in self.__data:
                if fp.subjoined is None:
                    fp.subjoined = dict()
                fp.subjoined['expand'] = bool(value)

                for fr in fp:
                    if fr.subjoined is None:
                        fr.subjoined = dict()
                    fr.subjoined['expand'] = bool(value)

        else:
            obj = self.ItemToObject(item)
            if isinstance(obj, (FileRoot, FilePath)):
                if obj.subjoined is None:
                    obj.subjoined = dict()
                obj.subjoined['expand'] = bool(value)

    # -----------------------------------------------------------------------

    def get_expanded_items(self, value=True):
        """Return the list of expanded or collapsed items.

        :param value: (bool) True represents Expanded.

        """
        items = list()
        for fp in self.__data:
            if fp.subjoined is not None:
                if 'expand' in fp.subjoined:
                    if fp.subjoined['expand'] is value:
                        items.append(self.ObjectToItem(fp))
                else:
                    # we don't know if collapsed or expanded.
                    if value is False:
                        items.append(self.ObjectToItem(fp))

            for fr in fp:
                if fr.subjoined is not None:
                    if 'expand' in fr.subjoined:
                        if fr.subjoined['expand'] is value:
                            items.append(self.ObjectToItem(fr))
                else:
                    # we don't know if collapsed or expanded.
                    if value is False:
                        items.append(self.ObjectToItem(fp))

        return items

    # -----------------------------------------------------------------------

    def FileToItem(self, entry):
        """Return the item matching the given entry name.

        :param entry: (str) Absolute or relative name of a file or a file root or a file path

        """
        obj = self.__data.get_object(entry)
        if obj is None:
            return wx.dataview.NullDataViewItem
        return self.ObjectToItem(obj)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    @staticmethod
    def __create_col(name):
        if name == "icon":
            col = ColumnProperties(" ", name, "wxBitmap")
            col.width = 36
            col.align = wx.ALIGN_CENTRE
            col.renderer = FileIconRenderer()
            return col

        if name == "file":
            col_file = ColumnProperties("Path Root Name", name)
            col_file.add_fct_name(FilePath, "get_id")
            col_file.add_fct_name(FileRoot, "get_id")
            col_file.add_fct_name(FileName, "get_name")
            col_file.width = 320
            return col_file

        if name == "state":
            col = ColumnProperties("State", name, "wxBitmap")
            col.width = 36
            col.align = wx.ALIGN_CENTRE
            col.renderer = StateIconRenderer()
            col.add_fct_name(FileName, "get_state")
            col.add_fct_name(FileRoot, "get_state")
            col.add_fct_name(FilePath, "get_state")
            return col

        if name == "type":
            col = ColumnProperties("Type", name)
            col.add_fct_name(FileName, "get_extension")
            col.width = 100
            return col

        if name == "refs":
            col = ColumnProperties("Ref.", name)
            # col.add_fct_name(FileRoot, "get_references")
            col.width = 80
            col.align = wx.ALIGN_LEFT
            return col

        if name == "date":
            col = ColumnProperties("Modified", name)
            col.add_fct_name(FileName, "get_date")
            col.width = 140
            col.align = wx.ALIGN_CENTRE
            return col

        if name == "size":
            col = ColumnProperties("Size", name)
            col.add_fct_name(FileName, "get_size")
            col.width = 80
            col.align = wx.ALIGN_RIGHT
            return col

        col = ColumnProperties("", name)
        col.width = 200
        return col

# ---------------------------------------------------------------------------


class TestFileAnnotIcon(unittest.TestCase):

    def test_init(self):
        f = FileAnnotIcon()
        self.assertEqual("SPPAS.png", f.get_icon_name(".xra"))
        self.assertEqual("praat.png", f.get_icon_name(".TextGrid"))
