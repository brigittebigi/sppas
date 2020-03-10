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

import logging
import os
import wx

from sppas.src.config import msg
from sppas.src.config import paths
from sppas.src.utils import u
from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasLocation, sppasInterval

from ..windows import sppasPanel
from ..windows import sppasSplitterWindow
from ..windows import LineListCtrl
from ..windows.dialogs import Confirm, Error
from ..windows.book import sppasNotebook
from ..main_events import ViewEvent, EVT_VIEW

from .ann import sppasAnnEditPanel

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

    A ListCtrl to represent annotations of a tier.
     - Only the best localization is displayed.
     - Labels are serialized.

    """

    tag_types = {
        "str": "String",
        "int": "Integer",
        "float": "Float",
        "bool": "Boolean"
    }

    # -----------------------------------------------------------------------

    def __init__(self, parent, tier, filename):
        """Create a sppasTierListCtrl and select the first annotation.

        :param parent: (wx.Window)
        :param tier: (sppasTier)
        :param filename: (str) The file this tier was extracted from.

        """
        super(sppasTierListCtrl, self).__init__(
            parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.NO_BORDER)

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
            self.SetColumnWidth(i, 100)

        # Fill rows
        for i, a in enumerate(self._tier):
            self.SetItemAnnotation(i)

        # Columns with optimal width (estimated depending on its content)
        self.SetColumnWidth(self._cols.index(MSG_LABELS), -1)
        self.SetColumnWidth(self._cols.index(MSG_ID), -1)
        self.SetColumnWidth(self._cols.index(MSG_META), -1)

    # ---------------------------------------------------------------------

    def SetItemAnnotation(self, idx):
        """Update list item of the annotation at the given index.

        :param idx: (int) Index of an annotation/item in the tier/list

        """
        assert 0 <= idx <= len(self._tier)
        ann = self._tier[idx]
        self.InsertItem(idx, "")

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
            label_str = ann.serialize_labels(separator=" ")
            self.SetItem(row, col, label_str)

            # customize label look
            if label_str in ['#', 'sil', 'silence']:
                self.SetItemTextColour(row, SILENCE_FG_COLOUR)
                self.SetItemBackgroundColour(row, SILENCE_BG_COLOUR)
            elif label_str in ['+', 'sp', 'pause']:
                self.SetItemTextColour(row, SILENCE_FG_COLOUR)
            elif label_str in ['@', '@@', 'lg', 'laugh', 'laughter']:
                self.SetItemTextColour(row, LAUGH_FG_COLOUR)
                self.SetItemBackgroundColour(row, LAUGH_BG_COLOUR)
            elif label_str in ['*', 'gb', 'noise', 'dummy']:
                self.SetItemTextColour(row, NOISE_FG_COLOUR)
                self.SetItemBackgroundColour(row, NOISE_BG_COLOUR)
            else:
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

# ----------------------------------------------------------------------------


class sppasTiersEditWindow(sppasSplitterWindow):
    """View tiers and edit annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, name="tiers_edit_splitter"):
        super(sppasTiersEditWindow, self).__init__(parent, name=name)
        self._create_content()
        self._setup_events()

        # Currently selected annotation index
        self.__cur_page = 0      # page index in the notebook
        self.__cur_index = -1    # item index in the listctrl
        self.__can_select = True

    # -----------------------------------------------------------------------
    # Public methods to manage files and tiers
    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the name of the file of the current page."""
        if self.__listctrl is not None:
            return self.__listctrl.get_filename()
        return ""

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        """Return the name of the tier of the current page."""
        if self.__listctrl is not None:
            return self.__listctrl.get_tiername()
        return ""

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, filename, tier_name):
        """Change page selection of the notebook to match given data.

        :return: (bool)

        """
        start = end = 0

        # De-select the currently selected annotation.
        if self.__cur_index != -1:
            c = self.__cur_index
            self.__can_select = self.__annotation_deselected(self.__cur_index)
            self.__listctrl.Select(c, on=1)

        # Select requested tier (... and an annotation)
        if self.__can_select is True:
            for i in range(self.__notebook.GetPageCount()):
                page = self.__notebook.GetPage(i)
                if page.get_filename() == filename and page.get_tiername() == tier_name:
                    self.__notebook.ChangeSelection(i)
                    self.__cur_page = i
                    listctrl = self.__notebook.GetPage(i)
                    self.__cur_index = listctrl.GetFirstSelected()
                    if self.__cur_index == -1:
                        self.__cur_index = 0
                    ann = self.__listctrl.get_selected_annotation()
                    self.__annpanel.set_ann(ann)
                    self._notify(action="ann_selected", value=self.__cur_index)
                    self.__annotation_selected(self.__cur_index)
                    break

        return self.__can_select

    # -----------------------------------------------------------------------

    def add_tiers(self, filename, tiers):
        """Add a set of tiers of the file.

        If no annotation was previously selected, select the first annotation
        of the first given tier and notify parent.

        :param filename: (str)
        :param tiers: (list of sppasTier)

        """
        sel_tier = None
        for tier in tiers:
            if len(tier) > 0:
                page = sppasTierListCtrl(self.__notebook, tier, filename)
                self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_annotation_selected, page)
                self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_annotation_deselected, page)
                self.__notebook.AddPage(page, tier.get_name())
                if sel_tier is None:
                    sel_tier = tier
            else:
                wx.LogError("Page not created. "
                            "No annotation in tier: {:s}".format(tier.get_name()))

        # no tier was previously added and we added at least a non-empty one
        if self.__listctrl is None and sel_tier is not None:
            self.__cur_index = self.__listctrl.GetFirstSelected()
            if self.__cur_index == -1:
                changed = self.set_selected_tiername(filename, sel_tier)
                if changed is True:
                    self.__annotation_selected(self.__cur_index)

        self.Layout()

    # -----------------------------------------------------------------------

    def remove_tiers(self, filename, tiers):
        """Remove a set of tiers of the file.

        :param filename: (str)
        :param tiers: (list of sppasTier)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Public methods to manage annotations
    # -----------------------------------------------------------------------

    def set_selected_annotation(self, idx):
        """Change the selected annotation.

        :param idx: (int) Index of the annotation to select.
        :return: (bool)

        """
        if self.__listctrl is None:
            return 0, 0

        valid = True
        if self.__cur_index != -1:
            # An annotation is already selected
            valid = self.__annotation_validator(self.__cur_index)

        if valid is True:
            self.__cur_index = idx
            self.__annotation_selected(idx)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content of the window.

        - Window 1 of the splitter: a ListCtrl of each tier in a notebook;
        - Window 2 of the splitter: an annotation editor.

        """
        w1 = sppasNotebook(self, style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL, name="tiers_notebook")
        w2 = sppasAnnEditPanel(self, ann=None, name="annedit_panel")

        # Fix size&layout
        self.SetMinimumPaneSize(sppasPanel.fix_size(128))
        self.SplitHorizontally(w1, w2, sppasPanel.fix_size(512))
        self.SetSashGravity(0.9)

    # -----------------------------------------------------------------------

    def swap_top_down_panels(self):
        """Swap the panels of the splitter."""
        win_1 = self.GetWindow1()
        win_2 = self.GetWindow2()
        w, h = win_2.GetSize()
        self.Unsplit(toRemove=win_1)
        self.Unsplit(toRemove=win_2)
        self.SplitHorizontally(win_2, win_1, h)

        if win_1 == self.__notebook:
            self.SetSashGravity(0.9)
        else:
            self.SetSashGravity(0.1)

        self.UpdateSize()

    # -----------------------------------------------------------------------
    # A private/quick access to children windows
    # -----------------------------------------------------------------------

    @property
    def __notebook(self):
        return self.FindWindow("tiers_notebook")

    @property
    def __listctrl(self):
        page_index = self.__notebook.GetSelection()
        if page_index == -1:
            return None
        return self.__notebook.GetPage(page_index)

    @property
    def __annpanel(self):
        return self.FindWindow("annedit_panel")

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _notify(self, action, value):
        """Send an EVT_VIEW event to the listener (if any).

        :param action: (str) Name of the action to perform
        :param value: (any) Any value to attach to the event/action

        """
        evt = ViewEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)
        wx.LogDebug("Notify parent {:s} of view event".format(
            self.GetParent().GetName()))

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Capture some of the events our controls are emitting.

        """
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_page_changing)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_page_changed)
        
        self.Bind(wx.EVT_BUTTON, self._process_toolbar_event)
        # self.Bind(wx.EVT_TOGGLEBUTTON, self._process_toolbar_event)

        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        logging.debug("Key event skipped by the TiersEdit panel {}".format(key_code))
        event.Skip()

    # -----------------------------------------------------------------------

    def _process_toolbar_event(self, event):
        """Process a button of the toolbar event.

        :param event: (wx.Event)

        """
        wx.LogDebug("Toolbar Event received by {:s}".format(self.GetName()))
        btn = event.GetEventObject()
        btn_name = btn.GetName()

        if btn_name == "way_up_down":
            self.swap_top_down_panels()

        elif btn_name == "cell_delete":
            self.__delete_annotation()

        elif btn_name == "cell_merge_previous":
            self.__merge_annotation(-1)

        elif btn_name == "cell_merge_next":
            self.__merge_annotation(1)

        elif btn_name == "cell_split":
            self.__split_annotation(0)

        elif btn_name == "cell_split_next":
            self.__split_annotation(1)

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _on_annotation_deselected(self, evt):
        """An annotation is de-selected in the list.

        If the content was modified, we have to push the text content into
        the annotation of the tier.

        """
        self.__can_select = self.__annotation_deselected(evt.GetIndex())

    # -----------------------------------------------------------------------

    def _on_annotation_selected(self, evt):
        """An annotation is selected in the list.

        Normally, no item is already selected.
        The event ITEM_SELECTED occurs after an ITEM_DESELECTED event.
        But if the user cancelled the de-selection, an item is still
        selected.

        """
        if self.__can_select is True:
            self.__annotation_selected(evt.GetIndex())
        else:
            # restore the selected
            self.__listctrl.Select(self.__cur_index, on=1)

    # -----------------------------------------------------------------------

    def _on_page_changing(self, evt):
        """The notebook is being to change page.

        Current annotation is de-selected.

        """
        if self.__listctrl is not None:
            if self.__cur_index != -1:
                c = self.__cur_index
                self.__can_select = self.__annotation_deselected(self.__cur_index)
                self.__listctrl.Select(c, on=1)

    # -----------------------------------------------------------------------

    def _on_page_changed(self, evt):
        """The notebook changed its page.

        A new tier is selected, so a new annotation too.

        """
        if self.__can_select is True:
            self._notify(action="tier_selected", value=None)
            self.__cur_index = self.__listctrl.GetFirstSelected()
            if self.__cur_index == -1:
                logging.debug("No annotation was previously selected in {}"
                              "".format(self.get_selected_tiername()))
                self.__cur_index = 0

            self.__annotation_selected(self.__cur_index)
            self.__cur_page = self.__notebook.GetSelection()
        else:
            # go back to the cur_page
            self.__notebook.ChangeSelection(self.__cur_page)
            self.__listctrl.Select(self.__cur_index, on=1)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __delete_annotation(self):
        """Delete the currently selected annotation."""
        try:
            self.__listctrl.delete_annotation(self.__cur_index)
        except Exception as e:
            Error("Annotation can't be deleted: {:s}".format(str(e)))
        else:
            # OK. The annotation was deleted is the listctrl.
            self._notify(action="ann_deleted", value=self.__cur_index)

            # new selected annotation
            self.__cur_index = self.__listctrl.GetFirstSelected()
            if self.__cur_index != -1:
                self.__annotation_selected(self.__cur_index)
            else:
                # clear the annotation editor if no new selected ann
                self.__annpanel.set_ann(ann=None)

    # -----------------------------------------------------------------------

    def __merge_annotation(self, direction):
        """Merge the currently selected annotation.

        :param direction: (int) Positive to merge with next, Negative with prev

        """
        try:
            merged = self.__listctrl.merge_annotation(self.__cur_index, direction)
        except Exception as e:
            Error("Annotation can't be merged: {:s}".format(str(e)))
        else:
            if merged is True:
                # OK. The annotation was merged in the listctrl.
                if direction > 0:
                    self._notify(action="ann_deleted", value=self.__cur_index+1)
                else:
                    self._notify(action="ann_deleted", value=self.__cur_index-1)
                self._notify(action="ann_modified", value=self.__cur_index)
                ann = self.__listctrl.get_selected_annotation()
                self.__annpanel.set_ann(ann)

    # -----------------------------------------------------------------------

    def __split_annotation(self, direction):
        """Split the currently selected annotation.

        :param direction: (int) Positive to transport labels to next

        """
        try:
            self.__listctrl.split_annotation(self.__cur_index, direction)
        except Exception as e:
            Error("Annotation can't be splitted: {:s}".format(str(e)))
        else:
            # OK. The annotation was splitted in the listctrl.
            self._notify(action="ann_created", value=self.__cur_index+1)
            self._notify(action="ann_modified", value=self.__cur_index)
            ann = self.__listctrl.get_selected_annotation()
            self.__annpanel.set_ann(ann)

    # -----------------------------------------------------------------------

    def __annotation_deselected(self, idx):
        """De-select the annotation of given index in our controls.

        :return: True if annotation was de-selected.

        """
        if self.__listctrl is None:
            return False

        valid = self.__annotation_validator(idx)
        if valid is True:
            # deselect the annotation at the given index
            self.__cur_index = -1
            self.__listctrl.Select(idx, on=0)
            # clear the annotation editor
            self.__annpanel.set_ann(ann=None)
        else:
            self.__cur_index = idx
            self.__listctrl.Select(idx, on=1)

        self._notify(action="ann_selected", value=self.__cur_index)
        return valid

    # -----------------------------------------------------------------------

    def __annotation_selected(self, idx):
        """Select the annotation of given index in our controls.

        """
        if self.__listctrl is None:
            return 0, 0

        self.__listctrl.Select(idx, on=1)
        ann = self.__listctrl.get_selected_annotation()
        self.__annpanel.set_ann(ann)
        self.__cur_index = idx
        self._notify(action="ann_selected", value=self.__cur_index)

    # -----------------------------------------------------------------------

    def __annotation_validator(self, idx):
        """

        :param idx:
        :return: (bool)

        """
        modif = self.__annpanel.text_modified()

        # The annotation labels were not modified.
        if modif == 0:
            return True

        # The annotation labels were modified but labels can't be created.
        elif modif == -1:
            # The labels can't be set to the annotation.
            # Ask to continue editing or to cancel changes.
            msg = ERR_ANN_SET_LABELS + "\n" + MSG_CANCEL
            response = Confirm(msg)
            if response == wx.ID_CANCEL:
                # The user accepted to cancel changes.
                ann = self.__listctrl.get_annotation(idx)
                self.__annpanel.set_ann(ann)
                return True
            else:
                # The user asked to continue editing it.
                return False

        # The annotation labels were modified properly
        else:
            new_labels = self.__annpanel.text_labels()
            # set the new labels to the annotation
            self.__listctrl.set_annotation_labels(idx, new_labels)
            # set the modified annotation to the annotation editor panel
            ann = self.__listctrl.get_annotation(idx)
            self.__annpanel.set_ann(ann)
            # notify parent we modified the tier at index idx
            self._notify(action="ann_modified", value=idx)
            return True

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        p = sppasTiersEditWindow(self)
        self.Bind(EVT_VIEW, self._process_view_event)

        s = wx.BoxSizer()
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

        f1 = os.path.join(paths.samples, "annotation-results",
                          "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results",
                          "samples-fra", "F_F_B003-P8-phon.xra")

        parser = sppasRW(f1)
        trs1 = parser.read()
        parser.set_filename(f2)
        trs2 = parser.read()
        p.add_tiers(f2, trs2.get_tier_list())
        p.add_tiers(f1, trs1.get_tier_list())

    # -----------------------------------------------------------------------

    def _process_view_event(self, evt):
        logging.debug("Received action {} with value {}"
                      "".format(evt.action, str(evt.value)))

