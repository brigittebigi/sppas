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

    ui.phoenix.page_analyze.datalist.baseobjlist.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A base class to display objects like tiers, ctrl vocab...

"""

import wx
import wx.lib.newevent

from sppas.src.ui.phoenix.windows.listctrl import CheckListCtrl


# ---------------------------------------------------------------------------
# Internal use of an event, when an item is clicked.

ItemClickedEvent, EVT_ITEM_CLICKED = wx.lib.newevent.NewEvent()
ItemClickedCommandEvent, EVT_ITEM_CLICKED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


class BaseObjectListCtrl(CheckListCtrl):
    """A panel to display a list of objects.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, objects, name="object_listctrl"):
        super(BaseObjectListCtrl, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.LC_REPORT | wx.LC_NO_HEADER,
            name=name)

        # For convenience, objects identifiers are stored into a list.
        self._trss = list()

        self._create_columns()
        self.SetAlternateRowColour(False)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__item_selected)

        # Fill in the controls with the data
        self.update(objects)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        CheckListCtrl.SetFont(self, font)

        # The change of font implies to re-draw all proportional objects
        self.__set_pane_size()
        self.Layout()

    # ----------------------------------------------------------------------

    def add(self, obj, index=None):
        """Add an object in the listctrl child panel.

        :param obj:
        :param index: Position of the object in the list. If None, append.

        """
        if obj.get_id() in self._trss:
            return False

        self.__add_item(obj, index)
        return True

    # ----------------------------------------------------------------------

    def remove(self, identifier):
        """Remove an item of the listctrl child panel.

        :param identifier: (str)
        :return: (bool)

        """
        if identifier not in self._trss:
            return False

        self.__remove_item(identifier)
        return True

    # ------------------------------------------------------------------------

    def change_state(self, identifier, state):
        """Update the state of the given identifier.

        :param identifier: (str)
        :param state: (str) True or False

        """
        idx = self._trss.index(identifier)
        if state == "True":
            self.Select(idx, on=1)
        else:
            self.Select(idx, on=0)

    # ------------------------------------------------------------------------

    def update(self, lst_obj):
        """Update each object of a given list.

        :param lst_obj: (list of sppasTier)

        """
        for obj in lst_obj:
            if obj.get_id() not in self._trss:
                self.__add_item(obj, index=None)
            else:
                #self.change_state(obj.get_id(), obj.get_state())
                self.update_item(obj)

    # ------------------------------------------------------------------------
    # Construct the GUI
    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create the columns to display the objects."""
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def __set_pane_size(self):
        """Fix the size of the listctrl."""
        pxh = self.get_font_height()
        n = self.GetItemCount()
        h = int(pxh * 2.)
        self.SetMinSize(wx.Size(-1, n * h))
        self.SetMaxSize(wx.Size(-1, (n * h) + pxh))

    # ------------------------------------------------------------------------
    # Management the list of tiers
    # ------------------------------------------------------------------------

    def __add_item(self, obj, index=None):
        """Append an object."""
        if index is None or index < 0 or index > self.GetItemCount():
            # Append
            index = self.InsertItem(self.GetItemCount(), "")
        else:
            # Insert
            index = self.InsertItem(index, "")

        self._trss.insert(index, obj.get_id())
        self.update_item(obj)

        self.__set_pane_size()
        self.Layout()

    # ------------------------------------------------------------------------

    def __remove_item(self, identifier):
        """Remove an object of the listctrl."""
        idx = self._trss.index(identifier)
        self.DeleteItem(idx)

        self._trss.pop(idx)
        self.__set_pane_size()
        self.Layout()

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        raise NotImplementedError

    # ------------------------------------------------------------------------
    # Management of the events
    # ------------------------------------------------------------------------

    def notify(self, identifier):
        """The parent has to be informed of a change of content."""
        evt = ItemClickedEvent(id=identifier)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def __item_selected(self, event):
        index = event.GetIndex()
        self.Select(index, on=False)

        # notify parent to decide what has to be done
        self.notify(self._trss[index])
