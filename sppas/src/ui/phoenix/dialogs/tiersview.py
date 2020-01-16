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

    src.ui.phoenix.dialogs.tiersview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.anndata import sppasTier
from sppas.src.config import msg
from sppas.src.utils import u

from ..windows import sppasDialog
from ..dialogs import Information
from ..windows.book import sppasNotebook

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DARK_GRAY = wx.Colour(35, 35, 35)
LIGHT_GRAY = wx.Colour(245, 245, 240)
LIGHT_BLUE = wx.Colour(230, 230, 250)
LIGHT_RED = wx.Colour(250, 230, 230)

UNLABELLED_FG_COLOUR = wx.Colour(190, 45, 45)
SILENCE_FG_COLOUR = wx.Colour(45, 45, 190)
SILENCE_BG_COLOUR = wx.Colour(230, 230, 250)
LAUGH_FG_COLOUR = wx.Colour(210, 150, 50)
LAUGH_BG_COLOUR = wx.Colour(250, 230, 230)
NOISE_FG_COLOUR = wx.Colour(45, 190, 45)
NOISE_BG_COLOUR = wx.Colour(230, 250, 230)

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_HEADER_TIERSVIEW = _("View annotations of tiers")
MSG_NO_TIER = _("No tier to view.")
MSG_BEGIN = _("Begin")
MSG_END = _("End")
MSG_LABELS = _("Serialized list of labels with alternative tags")
MSG_POINT = _("Midpoint")
MSG_RADIUS = _("Radius")
MSG_NB = _("Nb")
MSG_TYPE = _("Type")

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
        """Create a dialog to fix settings.

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
            page = TierAsListPanel(notebook, tier)
            notebook.AddPage(page, tier.get_name())
        self.SetContent(notebook)

# ---------------------------------------------------------------------------


class LineListCtrl(wx.ListCtrl):
    """A ListCtrl with line numbers in the first column.

    """
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name="LineListCtrl",):
        """
        Initialize a new ListCtlr instance.

        :param parent: Parent window. Must not be None.
        :param id:     CheckListCtrl identifier. A value of -1 indicates a default value.
        :param pos:    CheckListCtrl position. If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   CheckListCtrl size. If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param validator: Window validator.
        :param name:      Window name.

        """
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)

    # ---------------------------------------------------------------------

    def RecolorizeBackground(self, index=-1):
        """Set background color of items.

        :param index: (int) Item to set the bg color. -1 to set all items.

        """
        bg = self.GetBackgroundColour()
        r, g, b = bg.Red(), bg.Green(), bg.Blue()
        delta = 10
        if (r + g + b) > 384:
            alt_bg = wx.Colour(r, g, b, 50).ChangeLightness(100 - delta)
        else:
            alt_bg = wx.Colour(r, g, b, 50).ChangeLightness(delta)

        if index == -1:
            for i in range(self.GetItemCount()):
                if i % 2:
                    self.SetItemBackgroundColour(i, bg)
                else:
                    self.SetItemBackgroundColour(i, alt_bg)
        else:
            if index % 2:
                self.SetItemBackgroundColour(index, bg)
            else:
                self.SetItemBackgroundColour(index, alt_bg)

    # -----------------------------------------------------------------------
    # Override methods of wx.ListCtrl
    # -----------------------------------------------------------------------

    def InsertColumn(self, colnum, colname):
        """Override.

        Insert a new column:
            1. create a column with the line number if we create a column
               for the first time,
            2. create the expected column

        """
        if colnum == 0:
            # insert a first column, with whitespace
            wx.ListCtrl.InsertColumn(self, 0, " "*16, wx.LIST_FORMAT_CENTRE)

        wx.ListCtrl.InsertColumn(self, colnum+1, colname)

    # -----------------------------------------------------------------------

    def InsertItem(self, index, label):
        """Override.

        Create a row, add the line number, add content of the first column.
        Shift the selection of items if necessary.

        """
        wx.ListCtrl.InsertItem(self, index, self._num_to_str(index+1))
        item = self.GetItem(index,0)
        item.SetAlign(wx.LIST_FORMAT_CENTER)
        #item.SetMask(item.GetMask() | wx.LIST_MASK_FORMAT)
        #item.SetBackgroundColour(wx.Colour(200,220,200))   # not efficient
        #item.SetTextColour(wx.Colour(70,100,70))           # not efficient

        # we want to add somewhere in the list (and not append)...
        # shift the line numbers items (for items that are after the new one)
        for i in range(index, self.GetItemCount()):
            wx.ListCtrl.SetItem(self, i, 0, self._num_to_str(i+1))
            self.RecolorizeBackground(i)

        return wx.ListCtrl.SetItem(self, index, 1, label)

    # -----------------------------------------------------------------------

    def SetColumnWidth(self, col, width):
        """Override.

        Fix column width. Fix also the first column (with check buttons).

        """
        wx.ListCtrl.SetColumnWidth(self, 0, wx.LIST_AUTOSIZE_USEHEADER)
        wx.ListCtrl.SetColumnWidth(self, col+1, width)

    # -----------------------------------------------------------------------

    def SetItem(self, index, col, label):
        """Override.

        Set the string of an item: the column number must be changed to be
        efficient; and alternate background colors (just for the list to be
        easier to read).

        """
        # we added a column the user does not know!
        wx.ListCtrl.SetItem(self, index, col+1, label)
        # and to look nice:
        self.RecolorizeBackground(index)

    # -----------------------------------------------------------------------

    def DeleteItem(self, index):
        """Override.

        Delete an item in the list. Must be overridden to update line numbers.

        """
        wx.ListCtrl.DeleteItem(self,index)
        for i in range(index, self.GetItemCount()):
            wx.ListCtrl.SetItem(self, i, 0, self._num_to_str(i+1))
            self.RecolorizeBackground(index)

    # -----------------------------------------------------------------------

    @staticmethod
    def _num_to_str(num):
        return " -- " + str(num) + " -- "

# ---------------------------------------------------------------------------


class TierAsListPanel(LineListCtrl):
    """List-view of a tier.

    """

    tag_types = {
        "str": "String",
        "int": "Integer",
        "float": "Float",
        "bool": "Boolean"
    }

    def __init__(self, parent, tier):
        super(TierAsListPanel, self).__init__(parent=parent, style=wx.LC_REPORT)
        self._create_content(tier)

    # -----------------------------------------------------------------------

    def _create_content(self, tier):
        """Show a tier in a listctrl.

        """
        # create columns
        is_point_tier = tier.is_point()
        if not is_point_tier:
            cols = (MSG_BEGIN, MSG_END, MSG_LABELS, MSG_NB, MSG_TYPE)
        else:
            cols = (MSG_POINT, MSG_LABELS, MSG_NB, MSG_TYPE)
        for i, col in enumerate(cols):
            self.InsertColumn(i, col)
            self.SetColumnWidth(i, 100)

        # fill rows
        for i, a in enumerate(tier):

            # fix location
            if not is_point_tier:
                self.InsertItem(i, str(a.get_lowest_localization().get_midpoint()))
                self.SetItem(i, 1, str(a.get_highest_localization().get_midpoint()))
                labeli = 2
            else:
                self.InsertItem(i, str(a.get_highest_localization().get_midpoint()))
                labeli = 1

            # fix label
            if a.is_labelled():
                label_str = a.serialize_labels(separator=" - ")
                self.SetItem(i, labeli, label_str)

                # customize label look
                if label_str in ['#', 'sil']:
                    self.SetItemTextColour(i, SILENCE_FG_COLOUR)
                    self.SetItemBackgroundColour(i, SILENCE_BG_COLOUR)
                if label_str == '+':
                    self.SetItemTextColour(i, SILENCE_FG_COLOUR)
                if label_str in ['@', '@@', 'lg', 'laugh']:
                    self.SetItemTextColour(i, LAUGH_FG_COLOUR)
                    self.SetItemBackgroundColour(i, LAUGH_BG_COLOUR)
                if label_str in ['*', 'gb', 'noise', 'dummy']:
                    self.SetItemTextColour(i, NOISE_FG_COLOUR)
                    self.SetItemBackgroundColour(i, NOISE_BG_COLOUR)
            else:
                self.SetItemTextColour(i, UNLABELLED_FG_COLOUR)

            # properties of the labels
            self.SetItem(i, labeli+1, str(len(a.get_labels())))
            label_type = a.get_label_type()
            if label_type not in TierAsListPanel.tag_types:
                lt = "Unknown"
            else:
                lt = TierAsListPanel.tag_types[a.get_label_type()]
            self.SetItem(i, labeli+2, lt)

        self.SetColumnWidth(cols.index(MSG_LABELS), -1)

# ---------------------------------------------------------------------------


def TiersView(parent, tiers):
    """Display a dialog to display the content of a list of tiers.

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
