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

    src.ui.phoenix.panels.tiers.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from ..windows import sppasPanel
from ..windows import sppasSplitterWindow
from ..windows import LineListCtrl
from sppas.src.config import msg
from sppas.src.utils import u


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

# --------------------------------------------------------------------------


class sppasTierListCtrl(LineListCtrl):
    """List-view of a tier.

    """

    tag_types = {
        "str": "String",
        "int": "Integer",
        "float": "Float",
        "bool": "Boolean"
    }

    def __init__(self, parent, tier):
        super(sppasTierListCtrl, self).__init__(parent=parent, style=wx.LC_REPORT | wx.NO_BORDER)
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
            if label_type not in sppasTierListCtrl.tag_types:
                lt = "Unknown"
            else:
                lt = sppasTierListCtrl.tag_types[a.get_label_type()]
            self.SetItem(i, labeli+2, lt)

        self.SetColumnWidth(cols.index(MSG_LABELS), -1)

# ----------------------------------------------------------------------------


class sppasTiersEditWindow(sppasSplitterWindow):
    """

    """

    def __init__(self, parent, name="tiers_edit_splitter"):
        super(sppasTiersEditWindow, self).__init__(
            parent, id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.SP_LIVE_UPDATE | wx.NO_BORDER | wx.SP_3D,
            name=name)

        # Window 1 of the splitter: tier view
        p1 = sppasPanel(self)   #, style=wx.BORDER_SIMPLE)

        # Window 2 of the splitter: annotation editor
        p2 = sppasPanel(self)   #, style=wx.BORDER_SIMPLE)

        # Fix size&layout
        self.SetMinimumPaneSize(sppasPanel.fix_size(128))
        self.SplitHorizontally(p1, p2, sppasPanel.fix_size(512))
        self.SetSashGravity(0.9)


# --------------------------------------------------------------------------


