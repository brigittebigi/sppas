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

    src.ui.phoenix.views.tiersview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Each tier is displayed in a ListCtrl.
    Organize the view of each tier in a notebook.

"""

import wx

from sppas.src.anndata import sppasTier
from sppas.src.config import msg
from sppas.src.utils import u

from ..windows.dialogs import sppasDialog
from ..windows.dialogs import Information
from ..windows.book import sppasNotebook
from ..panels import sppasTierListCtrl

# ---------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_HEADER_TIERSVIEW = _("View annotations of tiers")
MSG_NO_TIER = _("No tier to view.")

# ---------------------------------------------------------------------------


class sppasTiersViewDialog(sppasDialog):
    """A dialog with a notebook to display each tier in a listctrl.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Returns wx.ID_OK if ShowModal().

    """

    def __init__(self, parent, tiers):
        """Create a dialog to display tiers.

        :param parent: (wx.Window)
        :param tiers: (List of sppasTier)

        """
        super(sppasTiersViewDialog, self).__init__(
            parent=parent,
            title="Tiers View",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="tiersview-dialog")

        self.CreateHeader(MSG_HEADER_TIERSVIEW, "tier_ann_view")
        self._create_content(tiers)
        self.CreateActions([wx.ID_OK])

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------

    def _create_content(self, tiers):
        """Create the content of the message dialog."""
        # Make the notebook and an image list
        notebook = sppasNotebook(self, name="content")
        for tier in tiers:
            page = sppasTierListCtrl(notebook, tier, "")
            notebook.AddPage(page, tier.get_name())
        self.SetContent(notebook)

# ---------------------------------------------------------------------------


def TiersView(parent, tiers):
    """Open a dialog to display the content of a list of tiers.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    :param parent: (wx.Window)
    :param tiers: (list of sppasTier)
    :returns: wx.ID_OK

    """
    view = list()
    for t in tiers:
        if isinstance(t, sppasTier) is True:
            view.append(t)
        else:
            wx.LogError("{} is not of type sppasTier".format(t))
    if len(view) == 0:
        Information(MSG_NO_TIER)
        return wx.ID_OK

    dialog = sppasTiersViewDialog(parent, view)
    response = dialog.ShowModal()
    dialog.DestroyFadeOut()
    return response
