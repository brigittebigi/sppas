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

    src.ui.phoenix.panel_shared.tierlist.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The sppasTierListCtrl() defined in this file is used in both:

    - page_analyze.tiersviews, and
    - page_editor.listanns.tiersbook.

"""

import logging
import os
import wx

from sppas.src.config import msg
from sppas.src.config import paths
from sppas.src.utils import u
from sppas.src.anndata import sppasRW
from sppas.src.anndata.aio.aioutils import serialize_labels

from ..windows import sppasPanel
from ..windows import LineListCtrl
from ..windows.book import sppasChoicebook

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


DARK_GRAY = wx.Colour(35, 35, 35)
LIGHT_GRAY = wx.Colour(245, 245, 240)
LIGHT_BLUE = wx.Colour(230, 230, 250)
LIGHT_RED = wx.Colour(250, 230, 230)

UNLABELLED_FG_COLOUR = wx.Colour(190, 45, 45)
MODIFIED_BG_COLOUR = wx.Colour(35, 35, 35)
SILENCE_FG_COLOUR = wx.Colour(45, 45, 190)
SILENCE_BG_COLOUR = wx.Colour(230, 230, 250)
LAUGH_FG_COLOUR = wx.Colour(210, 150, 50)
LAUGH_BG_COLOUR = wx.Colour(250, 230, 230)
NOISE_FG_COLOUR = wx.Colour(45, 190, 45)
NOISE_BG_COLOUR = wx.Colour(230, 250, 230)

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_NO_TIER = _("No tier to view.")
MSG_BEGIN = _("Begin")
MSG_END = _("End")
MSG_LABELS = _("Serialized list of labels with alternative tags")
MSG_POINT = _("Midpoint")
MSG_RADIUS = _("Radius")
MSG_NB = _("Nb labels")
MSG_TYPE = _("Labels type")
MSG_ID = _("Identifier")
MSG_META = _("Metadata")
ERR_ANN_SET_LABELS = _("Invalid annotation labels.")
MSG_CANCEL = _("Cancel changes or continue editing the annotation?")

# --------------------------------------------------------------------------


class sppasTierListCtrl(LineListCtrl):
    """List-view of annotations of a tier.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    A ListCtrl to represent annotations of a tier:
     - Only the best localization is displayed;
     - Labels are serialized;
     - Metadata are serialized.

    Known bug of wx:
    If the ListCtrl is embedded in a page of a notebook, under Windows only,
    DeleteItem() returns the following error message:
    listctrl.cpp(2614) in wxListCtrl::MSWOnNotify(): invalid internal data pointer?
    A solution is to use a simplebook, a choicebook, a listbook or a
    toolbook instead!

    """

    tag_types = {
        "str": "String",
        "int": "Integer",
        "float": "Float",
        "bool": "Boolean"
    }

    # -----------------------------------------------------------------------

    def __init__(self, parent, tier, filename, style=wx.NO_BORDER, name="tierctrl"):
        """Create a sppasTierListCtrl and select the first annotation.

        :param parent: (wx.Window)
        :param tier: (sppasTier)
        :param filename: (str) The file this tier was extracted from.

        The style of the list is forced to LC_REPORT and LC_SINGLE_SEL.

        """
        if style & wx.LC_LIST:
            style &= ~wx.LC_LIST
        style |= wx.LC_REPORT
        style |= wx.LC_SINGLE_SEL

        super(sppasTierListCtrl, self).__init__(
            parent,
            style=style,
            name=name)

        self._cols = list()
        self._tier = tier
        self.__filename = filename
        self._create_content()

    # -----------------------------------------------------------------------
    # Public methods to access data
    # -----------------------------------------------------------------------

    def get_tiername(self):
        """Return the name of the tier this listctrl is displaying."""
        return self._tier.get_name()

    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the name of the file this listctrl is displaying a tier."""
        return self.__filename

    # -----------------------------------------------------------------------

    def get_selected_annotation(self):
        """Return the annotation matching the selected line in the list.

        :return: (sppasAnnotation) None if no selected item in the list

        """
        selected = self.GetFirstSelected()
        if selected == -1:
            return None
        return self._tier[selected]

    # -----------------------------------------------------------------------

    def get_annotation(self, idx):
        """Return the annotation at given index.

        :param idx: (int) Index of the annotation in the list
        :return: (sppasAnnotation)

        """
        assert 0 <= idx < len(self._tier)
        return self._tier[idx]

    # -----------------------------------------------------------------------

    def delete_annotation(self, idx):
        """Delete the annotation at given index.

        If idx was selected and no annotation is selected after deletion,
        next annotation is selected.

        :param idx: (int) Index of the annotation in the list
        :raise: Exception if annotation can't be deleted of the tier

        """
        assert 0 <= idx < len(self._tier)
        self._tier.pop(idx)
        self.DeleteItem(idx)

        selected = self.GetFirstSelected()
        if selected == -1 and self.GetItemCount() > 0:
            if idx == self.GetItemCount():
                idx = idx - 1

            self.Select(idx, on=1)

    # -----------------------------------------------------------------------

    def merge_annotation(self, idx, direction=1):
        """Merge the annotation at given index with next or previous one.

        if direction > 0:
            ann_idx:  [begin_idx, end_idx, labels_idx]
            next_ann: [begin_n, end_n, labels_n]
            result:   [begin_idx, end_n, labels_idx + labels_n]

        if direction < 0:
            prev_ann: [begin_p, end_p, labels_p]
            ann_idx:  [begin_idx, end_idx, labels_idx]
            result:   [begin_p, end_idx, labels_p + labels_idx]

        :param idx: (int) Index of the annotation in the list
        :param direction: (int) Positive for next, Negative for previous
        :return: (bool) False if direction does not match with index
        :raise: Exception if merged annotation can't be deleted of the tier

        """
        assert 0 <= idx < len(self._tier)

        # Merge annotation into the tier
        merged = self._tier.merge(idx, direction)
        if merged is True:

            # Update the list
            if direction > 0:
                self.__set_item_localization(idx)
                self.__set_item_label(idx)
                self.DeleteItem(idx+1)
            else:
                self.__set_item_localization(idx-1)
                self.__set_item_label(idx-1)
                self.DeleteItem(idx)

        return merged

    # -----------------------------------------------------------------------

    def split_annotation(self, idx, direction=1):
        """Split the annotation at given index.

        Transport the label to the next if direction > 0.

        if direction <= 0:
            ann_idx:  [begin_idx, end_idx, labels_idx]
            result:   [begin_idx, middle, labels_idx]
                      [middle, end_idx, ]

        if direction > 0:
            ann_idx:  [begin_idx, end_idx, labels_idx]
            result:   [begin_idx, middle, ]
                      [middle, end_idx, labels_idx]

        :param idx: (int) Index of the annotation in the list
        :param direction: (int) Positive for label in next
        :return: (bool) False if direction does not match with index
        :raise: Exception if annotation can't be splitted

        """
        assert 0 <= idx < len(self._tier)

        # Split annotation into the tier
        self._tier.split(idx)

        # Update the list
        self.__set_item_localization(idx)
        self.SetItemAnnotation(idx+1)

        # Move (or not) labels
        if direction > 0:
            labels = [l.copy() for l in self._tier[idx].get_labels()]
            self.set_annotation_labels(idx, list())
            logging.debug("Ann at index {}: {}".format(idx, self._tier[idx]))
            self.set_annotation_labels(idx+1, labels)

    # -----------------------------------------------------------------------

    def add_annotation(self, idx, direction):
        """Create an annotation before or after the given one.

        :param idx: (int) Index of the annotation in the list
        :param direction: (int) Positive for after, Negative for before
        :return: (bool) False if direction does not match with index
        :raise: Exception if annotation can't be created

        """
        assert 0 <= idx < len(self._tier)

        if direction == 0:
            return False
        elif direction > 0:
            self._tier.create_annotation_after(idx)
            self.SetItemAnnotation(idx+1)
        else:
            self._tier.create_annotation_before(idx)
            self.SetItemAnnotation(idx)
        return True

    # -----------------------------------------------------------------------

    def set_annotation_labels(self, idx, labels):
        """Set the labels of an annotation.

        :param idx: (int) Index of the annotation in the list
        :param labels: (list) List of labels

        """
        annotation = self._tier[idx]
        cur_labels = annotation.get_labels()
        try:
            annotation.set_labels(labels)
            self.__set_item_label(idx)
        except Exception as e:
            wx.LogError("Labels {} can't be set to annotation {}. {}"
                        "".format(str(labels), annotation, str(e)))
            # Restore properly the labels and the item before raising
            annotation.set_labels(cur_labels)
            self.__set_item_label(idx)
            raise

    # -----------------------------------------------------------------------

    def set_annotation_localization(self, idx, localization):
        """Set the localization of an annotation.

        :param idx: (int) Index of the annotation in the list
        :param localization: (sppasLocalization)

        """
        annotation = self._tier[idx]
        annotation.set_best_localization(localization)
        self.__set_item_localization(idx)

    # -----------------------------------------------------------------------
    # Construct the window
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Show a tier in a listctrl.

        """
        # Create columns
        if self._tier.is_point() is False:
            self._cols = (MSG_BEGIN, MSG_END, MSG_LABELS, MSG_NB, MSG_TYPE, MSG_ID, MSG_META)
        else:
            self._cols = (MSG_POINT, MSG_LABELS, MSG_NB, MSG_TYPE, MSG_ID, MSG_META)
        for i, col in enumerate(self._cols):
            self.InsertColumn(i, col)
            self.SetColumnWidth(i, sppasPanel.fix_size(90))

        # Fill rows
        for i, a in enumerate(self._tier):
            self.SetItemAnnotation(i)

        # Columns with optimal width (estimated depending on its content)
        self.SetColumnWidth(self._cols.index(MSG_LABELS), -1)
        self.SetColumnWidth(self._cols.index(MSG_ID), sppasPanel.fix_size(280))
        self.SetColumnWidth(self._cols.index(MSG_META), sppasPanel.fix_size(300))

    # ---------------------------------------------------------------------

    def SetItemAnnotation(self, idx):
        """Insert list item of the annotation at the given index.

        :param idx: (int) Index of an annotation/item in the tier/list

        """
        assert 0 <= idx <= len(self._tier)
        ann = self._tier[idx]
        self.InsertItem(idx, "")
        self.UpdateItem(idx)

    # ---------------------------------------------------------------------

    def UpdateItem(self, idx):
        """Reset list item of the annotation at the given index.

        :param idx: (int) Index of an annotation/item in the tier/list

        """
        assert 0 <= idx <= len(self._tier)
        ann = self._tier[idx]

        # fix location
        self.__set_item_localization(idx)

        # fix label
        self.__set_item_label(idx)

        # All metadata, but 'id' in a separated column.
        self.SetItem(idx, self._cols.index(MSG_ID), ann.get_meta("id"))
        meta_list = list()
        for key in ann.get_meta_keys():
            if key != 'id':
                value = ann.get_meta(key)
                meta_list.append(key + "=" + value)
        self.SetItem(idx, self._cols.index(MSG_META), ", ".join(meta_list))

    # ---------------------------------------------------------------------

    def __set_item_localization(self, row):
        """Fill the row-th col-th item with the annotation localization.

        """
        ann = self._tier[row]
        if self._tier.is_point() is False:
            col = self._cols.index(MSG_BEGIN)
            self.SetItem(row, col, str(ann.get_lowest_localization().get_midpoint()))
            col = self._cols.index(MSG_END)
            self.SetItem(row, col, str(ann.get_highest_localization().get_midpoint()))
        else:
            col = self._cols.index(MSG_POINT)
            self.SetItem(row, col, str(ann.get_highest_localization().get_midpoint()))

    # ---------------------------------------------------------------------

    def __set_item_label(self, row):
        """Fill the row-th item with the annotation labels.

        """
        col = self._cols.index(MSG_LABELS)
        ann = self._tier[row]
        if ann.is_labelled():
            label_str = serialize_labels(ann.get_labels(), separator=" ")
            self.SetItem(row, col, label_str)

            # customize label look
            # if label_str in ['#', 'sil', 'silence']:
            #     self.SetItemTextColour(row, SILENCE_FG_COLOUR)
            #     self.SetItemBackgroundColour(row, SILENCE_BG_COLOUR)
            # elif label_str in ['+', 'sp', 'pause']:
            #     self.SetItemTextColour(row, SILENCE_FG_COLOUR)
            # elif label_str in ['@', '@@', 'lg', 'laugh', 'laughter']:
            #     self.SetItemTextColour(row, LAUGH_FG_COLOUR)
            #     self.SetItemBackgroundColour(row, LAUGH_BG_COLOUR)
            # elif label_str in ['*', 'gb', 'noise', 'dummy']:
            #     self.SetItemTextColour(row, NOISE_FG_COLOUR)
            #     self.SetItemBackgroundColour(row, NOISE_BG_COLOUR)
            # else:
            #     self.SetItemTextColour(row, self.GetForegroundColour())
            self.SetItemTextColour(row, self.GetForegroundColour())

        else:
            self.SetItem(row, col, "")

        # properties of the labels (nb/type)
        self.SetItem(row, self._cols.index(MSG_NB), str(len(ann.get_labels())))

        label_type = ann.get_label_type()
        if label_type not in sppasTierListCtrl.tag_types:
            lt = "Unknown"
        else:
            lt = sppasTierListCtrl.tag_types[ann.get_label_type()]
        self.SetItem(row, self._cols.index(MSG_TYPE), lt)

# ---------------------------------------------------------------------------


class sppasTiersbook(sppasChoicebook):
    """A book with a bunch of tiers displayed in a ListCtrl.

    Any book is ok, except notebook for which there's a bug in wx.

    """

    def __init__(self, parent):
        super(sppasTiersbook, self).__init__(parent,
                                             style=wx.TAB_TRAVERSAL,
                                             name="tiers_book")

    # -----------------------------------------------------------------------

    def add_tiers(self, filename, tiers):
        """Add a set of tiers of the file.

        If no tier was previously selected, select the first one.

        :param filename: (str)
        :param tiers: (list of sppasTier)
        :return: selected tier name

        """
        if self.GetPageCount() > 0:
            # A page is already selected
            sel_tier = ""
        else:
            sel_tier = None

        for tier in tiers:
            if len(tier) > 0:
                page = sppasTierListCtrl(self, tier, filename, style=wx.BORDER_SIMPLE)

                self.AddPage(page, tier.get_name())
                if sel_tier is None:
                    sel_tier = tier.get_name()
            else:
                wx.LogError("Page not created. "
                            "No annotation in tier: {:s}".format(tier.get_name()))

        if sel_tier is None:
            return ""
        return sel_tier

    # -----------------------------------------------------------------------

    def remove_tiers(self, filename, tiers):
        """Remove a set of tiers of the file.

        If the selected tier is among the removed one, select another one.

        :param filename: (str)
        :param tiers: (list of sppasTier)
        :return: selected tier name

        """
        tier_names = [tier.get_name() for tier in tiers]
        for page_index in reversed(range(self.GetPageCount())):
            page = self.GetPage(page_index)
            if page.get_filename() == filename:
                if page.get_tiername() in tier_names:
                    self.DeletePage(page_index)

        page_sel = self.GetSelection()
        if page_sel == wx.NOT_FOUND:
            return ""

        return self.GetPage(page_sel).get_tiername()

    # -----------------------------------------------------------------------

    @property
    def tierctrl(self):
        page_index = self.GetSelection()
        if page_index == -1:
            return None
        return self.GetPage(page_index)


# ---------------------------------------------------------------------------
# Panel tested
# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):
    """
    """

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test ListCtrl Tier View")

        # Create content
        self.__book = sppasTiersbook(self)
        s = wx.BoxSizer()
        s.Add(self.__book, 1, wx.EXPAND)
        self.SetSizer(s)

        # Setup events
        self.__book.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self._on_page_changing)
        self.__book.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._on_page_changed)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_deselected_item)

        # Add data
        f1 = os.path.join(paths.samples, "annotation-results",
                          "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results",
                          "samples-fra", "F_F_B003-P8-phon.xra")

        parser = sppasRW(f1)
        trs1 = parser.read()
        parser.set_filename(f2)
        trs2 = parser.read()
        self.__book.add_tiers(f1, trs2.get_tier_list())
        self.__book.add_tiers(f2, trs1.get_tier_list())
        # trs1.get_hierarchy().remove_tier(trs1[0])
        page = self.__book.GetPage(self.__book.GetSelection())
        page.Bind(wx.EVT_KEY_UP, self._on_char, page)
        page.Select(0, on=1)

    # -----------------------------------------------------------------------

    @property
    def __tierctrl(self):
        return self.__book.tierctrl

    # -----------------------------------------------------------------------

    def _on_page_changing(self, evt):
        """The book is being to change page."""
        logging.debug("Test panel received page changing event.")

    # -----------------------------------------------------------------------

    def _on_page_changed(self, evt):
        """The book changed its page. """
        logging.debug("Test panel received page changed event.")
        page = self.__book.GetPage(self.__book.GetSelection())
        page.Bind(wx.EVT_KEY_UP, self._on_char, page)

    # -----------------------------------------------------------------------

    def _on_selected_item(self, evt):
        logging.debug("Test panel received selected item event. Id={}. Index={}"
                      "".format(evt.GetItem().GetId(), evt.GetIndex()))

    # -----------------------------------------------------------------------

    def _on_deselected_item(self, evt):
        logging.debug("Test panel received de-selected item event. Index {}"
                      "".format(evt.GetIndex()))

    # -----------------------------------------------------------------------

    def _on_char(self, evt):
        kc = evt.GetKeyCode()
        char = chr(kc)
        if kc in (8, 127):
            selected = self.__tierctrl.GetFirstSelected()
            if selected != -1:
                self.__tierctrl.delete_annotation(selected)
