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

    src.ui.phoenix.page_files.filestreectrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.lib.agw.hypertreelist as HTL

from sppas import sppasTypeError
from sppas.src.anndata import sppasRW
from sppas.src.files import States, FileName, FileRoot, FilePath, FileData

from ..windows import sppasPanel
from ..windows.image import ColorizeImage
from ..tools import sppasSwissKnife

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


class BitmapWindow(wx.Window):

    def __init__(self, name):
        super(BitmapWindow, self).__init__()
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        size = dc.GetTextExtent('TT')
        w, h = size[1] * 2, size[1] * 2
        s = min(w, h)
        s = int(0.8 * s)
        self.bmp = sppasSwissKnife.get_bmp_icon(name, s)

    def get_window(self):
        return self.bmp

# ---------------------------------------------------------------------------


class StateWindow(wx.Window):

    ICON_NAMES = {
        States().UNUSED: "choice_checkbox",
        States().CHECKED: "choice_checked",
        States().LOCKED: "locked",
        States().AT_LEAST_ONE_CHECKED: "choice_pos",
        States().AT_LEAST_ONE_LOCKED: "choice_neg"
    }

    def __init__(self, state):
        super(StateWindow, self).__init__()
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        size = dc.GetTextExtent('TT')
        w, h = size[1] * 2, size[1] * 2
        s = min(w, h)
        s = int(0.9 * s)

        if state in StateWindow.ICON_NAMES:
            icon_value = StateWindow.ICON_NAMES[state]
            # get the image from its name
            img = sppasSwissKnife.get_image(icon_value)
            # re-scale the image to the expected size
            sppasSwissKnife.rescale_image(img, s)
            # re-colorize
            ColorizeImage(img, wx.BLACK, wx.Colour(128, 128, 128, 128))
            # convert to bitmap
            self.bmp = wx.Bitmap(img)
        else:
            try:  # wx4
                self.bmp = wx.Bitmap(s, s, 32)
            except TypeError:  # wx3
                self.bmp = wx.EmptyBitmap(s, s)

    def get_window(self):
        return self.bmp

# ---------------------------------------------------------------------------


class ColumnProperties(object):
    """Represents the properties of any column.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, name, idt):
        """Constructor of a ColumnProperties.

        Some members of this class are associated to the wx.dataview package.

        All members are private so that the get/set methods are always called
        and they have properties in order to be able to access them in a
        simplest way. These members can't be modified by inheritance.

        The properties of a column are:

            - an identifier: an integer to represent the column number,
            - a name of the column,
            - the initial width of the column,
            - the edit mode of the cell (editable or not),
            - a renderer,
            - an alignment,
            - the functions to get values in the data of the model.

        :param name: (str) Name of the column

        """
        self.__id = idt
        self.__name = ""
        self.set_name(name)

        self.__width = 40
        self.__renderer = None
        self.__edit = False
        self.__align = wx.ALIGN_LEFT
        self.__fct = dict()       # functions to get values
        self.__fct_args = dict()  # args of the function to get values

    # -----------------------------------------------------------------------

    def get_id(self):
        return self.__id

    # -----------------------------------------------------------------------

    def get_name(self):
        return self.__name

    def set_name(self, value):
        self.__name = str(value)

    # -----------------------------------------------------------------------

    def get_width(self):
        return self.__width

    def set_width(self, value):
        value = int(value)
        value = min(max(40, value), 400)
        self.__width = value

    # -----------------------------------------------------------------------
    # Edit mode (editable or not)
    # -----------------------------------------------------------------------

    def get_edit(self):
        """Get the edit mode of the cells. """
        return self.__edit

    # -----------------------------------------------------------------------

    def set_edit(self, value):
        """Fix the edit mode of the cells.

        :param value: (bool) True if editable

        """
        self.__edit = bool(value)

    # -----------------------------------------------------------------------

    def get_renderer(self):
        return self.__renderer

    def set_renderer(self, r):
        self.__renderer = r

    # -----------------------------------------------------------------------

    def get_align(self):
        return self.__align

    def set_align(self, value):
        aligns = (
            wx.ALIGN_LEFT,
            wx.ALIGN_RIGHT,
            wx.ALIGN_CENTRE)
        if value is None or value not in aligns:
            value = aligns[0]
        self.__align = value

    # -----------------------------------------------------------------------

    def add_fct_name(self, key, fct_name, fct_arg=None):
        """key is a data type."""
        self.__fct[key] = fct_name
        self.__fct_args[key] = fct_arg

    # -----------------------------------------------------------------------

    def get_value(self, data):
        for key in self.__fct:
            if key == type(data):
                if self.__fct_args[key] is None:
                    return getattr(data, self.__fct[key])()
                else:
                    return getattr(data, self.__fct[key])(self.__fct_args[key])
        return ""

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    id = property(get_id, None)
    name = property(get_name, set_name)
    edit = property(get_edit, set_edit)
    width = property(get_width, set_width)
    renderer = property(get_renderer, set_renderer)
    align = property(get_align, set_align)

# ---------------------------------------------------------------------------


class FileTreeView(sppasPanel):
    """A control to display data files in a tree-spreadsheet style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name=wx.PanelNameStr):
        """Constructor of the FileTreeCtrl.

        :param parent: (wx.Window)
        :param name: (str)

        """
        super(FileTreeView, self).__init__(parent, name=name)

        self.tree = HTL.HyperTreeList(self, style=wx.BORDER_NONE | HTL.TR_NO_BUTTONS | HTL.TR_SINGLE | HTL.TR_HIDE_ROOT | HTL.TR_COLUMN_LINES, name="content")

        # The workspace to display
        self.__data = FileData()
        self.__column_names = ['icon', 'file', 'state', 'type', 'refs', 'date', 'size']
        self.__mapper = dict()

        # The icons to display depending on the file extension
        self.exticon = FileAnnotIcon()

        # Create the columns
        for i, c in enumerate(self.__column_names):
            self.__mapper[i] = FileTreeView.__create_col_properties(c)
            self.__create_col(self.__mapper[i])

        self.root = self.tree.AddRoot("")
        self.tree.Expand(self.root)
        self.tree.SetMainColumn(1)

        sizer = wx.BoxSizer()
        sizer.Add(self.tree, 1, wx.EXPAND)
        self.SetSizer(sizer)
        sizer.Layout()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data."""
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Set the data."""
        self.__data = data
        self.__refresh()

    # ------------------------------------------------------------------------

    def AddFiles(self, entries):
        """Add a list of files or folders.

        The given filenames must include their absolute path.

        :param entries: (list of str) Filename or folder with absolute path.
        :return: (int) Number of items added in the tree

        """
        wx.LogDebug('Add files: {:s}'.format(str(entries)))
        items = self.__add_files(entries)
        nb = len(items)
        if len(items) > 0:
            self.__refresh()
        return nb

    # -----------------------------------------------------------------------
    # Management of the tree
    # -----------------------------------------------------------------------

    @staticmethod
    def __create_col_properties(name):
        if name == "icon":
            col = ColumnProperties(" ", name)
            col.width = 36
            col.align = wx.ALIGN_CENTRE
            col.renderer = BitmapWindow("")
            return col

        if name == "file":
            col_file = ColumnProperties("Path Root Name", name)
            col_file.add_fct_name(FilePath, "get_id")
            col_file.add_fct_name(FileRoot, "get_id")
            col_file.add_fct_name(FileName, "get_name")
            col_file.width = 320
            return col_file

        if name == "state":
            col = ColumnProperties("State", name)
            col.width = 36
            col.align = wx.ALIGN_CENTRE
            col.renderer = StateWindow(0)
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

    def __create_col(self, col):
        self.tree.AddColumn(
            col.name,
            col.width,
            col.align,
            image=-1,
            shown=True,
            colour=None,
            edit=col.edit
        )

    # ------------------------------------------------------------------------

    def __refresh(self):
        pass

    # -----------------------------------------------------------------------

    def update(self):
        """Update the data and refresh the tree."""
        wx.LogDebug("Data update...")
        self.__data.update()
        wx.LogDebug("Clear the tree...")
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("")
        self.tree.Expand(self.root)
        for fp in self.__data:
            wx.LogDebug(" - add item {:s}".format(fp.get_id()))
            fp_item = self.__append_item(fp, parent=self.root)
            for fr in fp:
                fr_item = self.__append_item(fr, parent=fp_item)
                for fn in fr:
                    self.__append_item(fn, parent=fr_item)
        self.tree.Refresh()

    # -----------------------------------------------------------------------

    def __append_item(self, fb, parent=None):
        """Create an item matching a FileBase."""
        item = self.tree.AppendItem(parent, "", data=fb)
        if isinstance(fb, (FileRoot, FilePath)):
            if fb.subjoined is None:
                fb.subjoined = dict()
                fb.subjoined["expand"] = True
            if fb.subjoined.get('expand', False) is True:
                self.tree.Expand(item)
                wx.LogDebug(" expand item {:s} ".format(fb.get_id()))
        for i in self.__mapper:
            value = self.GetValue(item, i)
            if value is None:
                wx.LogError("None value for item={:s}, col={:d}".format(fb.get_id(), i))
                return
            wx.LogDebug(" value={:s}".format(str(value)))
            renderer = self.__mapper[i].renderer
            if renderer is None or len(str(value)) == 0:
                item.SetText(i, str(value))
            else:
                # item.SetWindow(value, i)
                wx.LogDebug('Not implemented: custom renderer.')
        return item

    # -----------------------------------------------------------------------

    def __add_files(self, entries):
        """Add a set of files or folders in the data and in the tree.

        :param entries: (list of str) FileName or folder with absolute path.

        """
        added_files = list()
        for entry in entries:
            fns = self.__add(entry)
            if len(fns) > 0:
                added_files.extend(fns)

        if len(added_files) > 0:
            self.update()

        return added_files

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

    def GetValue(self, item, col):
        """Return the value to be displayed for this item and column.

        :param item: (wx.dataview.DataViewItem)
        :param col: (int) Column index.

        Pull the values from the data objects we associated with the items
        in GetChildren.

        """
        # Fetch the data object for this item.
        node = item.GetData()
        if isinstance(node, (FileName, FileRoot, FilePath)) is False:
            raise RuntimeError("Unknown node type {:s}".format(type(node)))

        if self.__mapper[col].get_id() == "state":
            return StateWindow(self.__mapper[col].get_value(node))

        if self.__mapper[col].get_id() == "icon":
            if isinstance(node, FileName) is True:
                ext = node.get_extension()
                icon_name = self.exticon.get_icon_name(ext)
                return BitmapWindow(icon_name)
            return ""

        if self.__mapper[col].get_id() == "refs":
            if isinstance(node, FileRoot) is True:
                # convert the list of FileReference instances into a string
                refs_ids = [ref.id for ref in node.get_references()]
                return " ".join(sorted(refs_ids))
            return ""

        return self.__mapper[col].get_value(node)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(FileTreeView):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.AddFiles([os.path.abspath(__file__)])
