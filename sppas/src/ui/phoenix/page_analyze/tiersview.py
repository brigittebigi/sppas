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

    src.ui.phoenix.page_analyze.tiersview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Each tier is displayed in a ListCtrl.
    Organize the view of each tier in a notebook.

"""

import wx

from sppas.src.ui.phoenix.windows.dialogs import sppasDialog
from sppas.src.ui.phoenix.windows.book import sppasNotebook
from sppas.src.ui.phoenix.panel_shared.tierlist import sppasTierListCtrl

# ---------------------------------------------------------------------------


class sppasTiersViewDialog(sppasDialog):
    """A dialog with a notebook to display each tier in a listctrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Returns wx.ID_OK if ShowModal().

    """

    def __init__(self, parent, tiers, title="Tiers View"):
        """Create a dialog to display tiers.

        :param parent: (wx.Window)
        :param tiers: (List of sppasTier)

        """
        super(sppasTiersViewDialog, self).__init__(
            parent=parent,
            title=title,
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="tiersview_dialog")

        self._create_content(tiers)
        self.CreateActions([wx.ID_OK])

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn()

    # -----------------------------------------------------------------------

    def _create_content(self, tiers):
        """Create the content of the message dialog."""
        # Make the notebook and an image list
        notebook = sppasNotebook(self, name="content")
        for tier in tiers:
            page = sppasTierListCtrl(notebook, tier, "")
            notebook.AddPage(page, tier.get_name())
        self.SetContent(notebook)
