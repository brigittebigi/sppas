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

    src.ui.phoenix.page_files.basectrls.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Base classes to manage a workspace and some utilities.

"""

import wx
import wx.dataview
import logging

from sppas.src.files.filebase import States
from sppas.src.files.fileexc import FileAttributeError

from ..tools import sppasSwissKnife
from ..windows.image import ColorizeImage

# ----------------------------------------------------------------------------


default_renderers = {
    "string": wx.dataview.DataViewTextRenderer,
    "bool": wx.dataview.DataViewToggleRenderer,
    "datetime": wx.dataview.DataViewDateRenderer,
    "wxBitmap": wx.dataview.DataViewBitmapRenderer,
    "wxDataViewIconText": wx.dataview.DataViewIconTextRenderer
}

# ---------------------------------------------------------------------------


class StateIconRenderer(wx.dataview.DataViewCustomRenderer):
    """Draw an icon matching a state of a file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    ICON_NAMES = {
        States().UNUSED: "choice_checkbox",
        States().CHECKED: "choice_checked",
        States().LOCKED: "locked",
        States().AT_LEAST_ONE_CHECKED: "choice_pos",
        States().AT_LEAST_ONE_LOCKED: "choice_neg"
    }

    def __init__(self,
                 varianttype="wxBitmap",
                 mode=wx.dataview.DATAVIEW_CELL_INERT,
                 align=wx.dataview.DVR_DEFAULT_ALIGNMENT):
        super(StateIconRenderer, self).__init__(varianttype, mode, align)
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
        s = int(0.9 * s)

        if self.value in StateIconRenderer.ICON_NAMES:
            icon_value = StateIconRenderer.ICON_NAMES[self.value]

            # get the image from its name
            img = sppasSwissKnife.get_image(icon_value)
            # re-scale the image to the expected size
            sppasSwissKnife.rescale_image(img, s)
            # re-colorize
            ColorizeImage(img, wx.BLACK, wx.Colour(128, 128, 128, 128))
            # convert to bitmap
            bitmap = wx.Bitmap(img)
            # render it at the center
            dc.DrawBitmap(bitmap, x + (w-s)//2, y + (h-s)//2)

        return True

# ---------------------------------------------------------------------------


class ColumnProperties(object):
    """Represents the properties of any column of a wx.dataview.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, name, idt, stype="string"):
        """Constructor of a ColumnProperties.

        Some members of this class are associated to the wx.dataview package.

        All members are private so that the get/set methods are always called
        and they have properties in order to be able to access them in a
        simplest way. These members can't be modified by inheritance.

        The properties of a column are:

            - an identifier: an integer to represent the column number,
            - a name of the column,
            - the type of the data to be displayed in the column,
            - the initial width of the column,
            - the mode of the cell (inert, activatable, editable),
            - a renderer,
            - an alignment,
            - the functions to get values in the data of the model.

        :param name: (str) Name of the column
        :param stype: (str) String representing the type of the data

        """
        try:  # wx4
            bmp = wx.Bitmap(16, 16, 32)
        except TypeError:  # wx3
            bmp = wx.EmptyBitmap(16, 16)

        # The data types and their default values
        self.default = {
            "string": "",
            "bool": False,
            "datetime": "",
            "wxBitmap": bmp,
            "wxDataViewIconText": ""
        }

        self.__id = idt
        self.__name = ""
        self.set_name(name)
        self.__stype = ""
        self.set_stype(stype)

        self.__width = 40
        self.__mode = wx.dataview.DATAVIEW_CELL_INERT
        self.__renderer = None
        self.__align = wx.ALIGN_LEFT
        self.__fct = dict()  # functions to get values

    # -----------------------------------------------------------------------

    def get_id(self):
        return self.__id

    # -----------------------------------------------------------------------

    def get_name(self):
        return self.__name

    def set_name(self, value):
        self.__name = str(value)

    # -----------------------------------------------------------------------

    def get_stype(self):
        return self.__stype

    def set_stype(self, value):
        if value is None or value not in self.default:
            value = "string"
        self.__stype = value

    # -----------------------------------------------------------------------

    def get_width(self):
        return self.__width

    def set_width(self, value):
        value = int(value)
        value = min(max(40, value), 400)
        self.__width = value

    # -----------------------------------------------------------------------
    # wx.dataview.DataViewCellMode
    # -----------------------------------------------------------------------

    def get_mode(self):
        """Get the mode of the cells. """
        return self.__mode

    # -----------------------------------------------------------------------

    def set_mode(self, value):
        """Fix the mode of the cells.

        :param value:

            - wx.dataview.DATAVIEW_CELL_INERT
            The cell only displays information and cannot be manipulated or
            otherwise interacted with in any way.
            - wx.dataview.DATAVIEW_CELL_ACTIVATABLE
            Indicates that the cell can be activated by clicking it or using
            keyboard.
            - wx.dataview.DATAVIEW_CELL_EDITABLE
            Indicates that the user can edit the data in-place in an inline
            editor control that will show up when the user wants to edit the cell.

        """
        modes = (
            wx.dataview.DATAVIEW_CELL_INERT,
            wx.dataview.DATAVIEW_CELL_ACTIVATABLE,
            wx.dataview.DATAVIEW_CELL_EDITABLE)
        if value is None or value not in modes:
            value = modes[0]
        self.__mode = value

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

    def add_fct_name(self, key, fct_name):
        self.__fct[key] = fct_name

    # -----------------------------------------------------------------------

    def get_value(self, data):
        for key in self.__fct:
            if key == type(data):
                return getattr(data, self.__fct[key])()
        # return the default value of this column type
        return self.default[self.__stype]

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    id = property(get_id, None)
    name = property(get_name, set_name)
    stype = property(get_stype, set_stype)
    mode = property(get_mode, set_mode)
    width = property(get_width, set_width)
    renderer = property(get_renderer, set_renderer)
    align = property(get_align, set_align)


# ----------------------------------------------------------------------------
# Control to store the data matching the model
# ----------------------------------------------------------------------------


class BaseTreeViewCtrl(wx.dataview.DataViewCtrl):
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

        :param parent: (wx.Window)
        :param name: (str)

        """
        super(BaseTreeViewCtrl, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.dataview.DV_MULTIPLE,  # | wx.dataview.DV_NO_HEADER,  # wx.dataview.DV_VERT_RULES
            name=name
        )

        # Create an instance of our model and associate to the view.
        self._model = None

        # Colors&font
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetForegroundColour(parent.GetForegroundColour())

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def set_data(self, data):
        if self._model is not None:
            self._model.set_data(data)

    # ------------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        wx.Window.SetBackgroundColour(self, color)
        if self._model is not None:
            self._model.SetBackgroundColour(color)

    # ------------------------------------------------------------------------

    def SetForegroundColour(self, color):
        wx.Window.SetForegroundColour(self, color)
        if self._model is not None:
            self._model.SetForegroundColour(color)

    # ------------------------------------------------------------------------

    def update_data(self):
        """To be overridden. Update the currently displayed data."""
        return

    # ------------------------------------------------------------------------
    # For sub-classes only (private)
    # ------------------------------------------------------------------------

    @staticmethod
    def _create_column(model, index):
        """Return the DataViewColumn matching the given index in the model.

        :param model:
        :param index: (int) Index of the column to create. It must match an
        existing column number of the model.
        :returns: (wx.dataview.DataViewColumn)

        """
        logging.debug('Create column: {:d} {:s}'
                      ''.format(index, model.GetColumnName(index)))

        stype = model.GetColumnType(index)
        render = model.GetColumnRenderer(index)
        if render is None:
            if stype not in default_renderers:
                stype = "string"
            render = default_renderers[stype](
                varianttype=stype,
                mode=model.GetColumnMode(index),
                align=model.GetColumnAlign(index))

        col = wx.dataview.DataViewColumn(
            model.GetColumnName(index),
            render,
            index,
            width=model.GetColumnWidth(index))
        col.Reorderable = True
        col.Sortable = False
        if stype in ("string", "datetime"):
            col.Sortable = True

        return col

    # ------------------------------------------------------------------------
    # Override methods to manage columns. No parent nor children will have the
    # possibility to Append/Insert/Prepend/Delete columns.
    # ------------------------------------------------------------------------

    def DeleteColumn(self, column):
        raise FileAttributeError(self.__class__.__format__, "DeleteColumn")

    def ClearColumns(self):
        raise FileAttributeError(self.__class__.__format__, "ClearColumns")

    def AppendColumn(self, col):
        raise FileAttributeError(self.__class__.__format__, "AppendColumn")

    def AppendBitmapColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendBitmapColumn")

    def AppendDateColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendDateColumn")

    def AppendIconTextColumn(self,*args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendIconTextColumn")

    def AppendProgressColumn(self,*args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendProgressColumn")

    def AppendTextColumn(self,*args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendTextColumn")

    def AppendToggleColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "AppendToggleColumn")

    def InsertColumn(self, pos, col):
        raise FileAttributeError(self.__class__.__format__, "InsertColumn")

    def PrependBitmapColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependBitmapColumn")

    def PrependColumn(self, col):
        raise FileAttributeError(self.__class__.__format__, "PrependColumn")

    def PrependDateColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependDateColumn")

    def PrependIconTextColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependIconTextColumn")

    def PrependProgressColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependProgressColumn")

    def PrependTextColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependTextColumn")

    def PrependToggleColumn(self, *args, **kw):
        raise FileAttributeError(self.__class__.__format__, "PrependToggleColumn")

