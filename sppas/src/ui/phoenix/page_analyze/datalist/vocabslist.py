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

    ui.phoenix.page_analyze.datalist.vocabslist.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A class to display a summary of a list of controlled vocabularies.

"""

import wx

from sppas.src.ui.phoenix.windows.panels import sppasPanel
from .baseobjlist import BaseObjectListCtrl

# ---------------------------------------------------------------------------


class CtrlVocabListCtrl(BaseObjectListCtrl):
    """A panel to display a list of controlled vocabs.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, objects):
        super(CtrlVocabListCtrl, self).__init__(
            parent,
            objects,
            name="vocabs_listctrl")

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create columns to display the tiers."""
        self.AppendColumn("type", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(40))
        self.AppendColumn("name", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(200))
        self.AppendColumn("description", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(80))
        self.AppendColumn("id", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(220))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        if obj.get_id() in self._trss:
            index = self._trss.index(obj.get_id())
            self.SetItem(index, 0, "Vocab")
            self.SetItem(index, 1, obj.get_name())
            self.SetItem(index, 2, obj.get_description())
            self.SetItem(index, 3, obj.get_id())
            self.RefreshItem(index)

    # ------------------------------------------------------------------------

    def __item_selected(self, event):
        index = event.GetIndex()
        self.Select(index, on=False)
