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

    src.ui.phoenix.page_editor.listanns.tiersanns.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import os
import wx

from sppas.src.config import msg
from sppas.src.config import paths
from sppas.src.utils import u
from sppas.src.anndata import sppasRW

from sppas.src.ui.phoenix.views.metaedit import MetaDataEdit
from sppas.src.ui.phoenix.windows.panels import sppasPanel
from sppas.src.ui.phoenix.windows.splitter import sppasSplitterWindow
from sppas.src.ui.phoenix.windows.dialogs import Confirm, Error
from sppas.src.ui.phoenix.windows.combobox import sppasComboBox
from sppas.src.ui.phoenix.windows.toolbar import sppasToolbar

from .listevents import ListannsViewEvent
from .annlabels import sppasAnnLabelsCtrl
from .tiersbook import sppasTiersBook

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

MSG_ANNS = _("Annotations: ")

METADATA = _("Edit metadata of the annotation")
RESTORE = _("Restore the label of the annotation")
DELETE = _("Delete the annotation")
MERGE_PREVIOUS = _("Merge with the previous annotation")
MERGE_NEXT = _("Merge with the next annotation")
SPLIT_ONE = _("Split annotation into 2 and put content to the first")
SPLIT_TWO = _("Split annotation into 2 and put content to the second")
ADD_BEFORE = _("Add an annotation in the hole before")
ADD_AFTER = _("Add an annotation in the hole after")
LABEL_TEXT = _("Edit label in TEXT mode")
LABEL_XML = _("Edit label in XML mode")
LABEL_JSON = _("Edit label in JSON mode")

# ----------------------------------------------------------------------------


class sppasTiersEditWindow(sppasSplitterWindow):
    """View tiers and edit annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    ANN_COLOUR = wx.Colour(200, 180, 120, 128)

    def __init__(self, parent, orient=wx.VERTICAL, name="tiers_edit_splitter"):
        super(sppasTiersEditWindow, self).__init__(parent, name=name)

        self.__orient = orient
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
        if self.__tierctrl is not None:
            return self.__tierctrl.get_filename()
        return ""

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        """Return the name of the tier of the current page."""
        if self.__tierctrl is not None:
            return self.__tierctrl.get_tiername()
        return ""

    # -----------------------------------------------------------------------

    def set_selected_index(self, page_index):
        """Change page selection of the book to match given page index.

        :return: (bool)

        """
        if page_index < 0 or page_index >= self.__tiersbook.GetPageCount():
            return

        # De-select the currently selected annotation.
        if self.__cur_index != -1:
            c = self.__cur_index
            self.__can_select = self.__annotation_deselected(self.__cur_index, to_notify=False)
            self.__tierctrl.Select(c, on=1)

        # Select requested tier (... and an annotation)
        if self.__can_select is True:
            self.__tiersbook.show_page(page_index)
            self.__cur_page = page_index
            listctrl = self.__tiersbook.GetPage(page_index)
            self.__cur_index = listctrl.GetFirstSelected()
            if self.__cur_index == -1:
                self.__cur_index = 0
            ann = self.__tierctrl.get_selected_annotation()
            self.__annctrl.set_ann(ann)
            self.__annotation_selected(self.__cur_index, to_notify=True)

        combo = self.FindWindow("tiers_combo")
        combo.SetSelection(self.__tiersbook.GetSelection())

        return self.__can_select

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, filename, tier_name, ann_index=-1):
        """Change page selection of the book to match given data.

        :param filename: (str)
        :param tier_name: (str) Name of the newly selected tier
        :param ann_index: (int) The index of an annotation to select
        :return: (bool)

        """
        # De-select the currently selected annotation.
        if self.__cur_index != -1:
            c = self.__cur_index
            self.__can_select = self.__annotation_deselected(self.__cur_index, to_notify=False)
            self.__tierctrl.Select(c, on=1)

        # Select requested tier (... and an annotation)
        if self.__can_select is True:
            for i in range(self.__tiersbook.GetPageCount()):
                page = self.__tiersbook.GetPage(i)
                if page.get_filename() == filename and page.get_tiername() == tier_name:
                    self.__tiersbook.show_page(i)
                    self.__cur_page = i

                    # Then, select an annotation in the newly selected tier
                    # Either get the given one, or the lastly selected one, or the first one.
                    if ann_index != -1:
                        self.set_selected_annotation(ann_index)
                    else:
                        listctrl = self.__tiersbook.GetPage(i)
                        self.__cur_index = listctrl.GetFirstSelected()
                        if self.__cur_index == -1:
                            self.__cur_index = 0
                        ann = self.__tierctrl.get_selected_annotation()
                        self.__annctrl.set_ann(ann)
                        self.__annotation_selected(self.__cur_index, to_notify=True)
                    break

        combo = self.FindWindow("tiers_combo")
        combo.SetSelection(self.__tiersbook.GetSelection())

        return self.__can_select

    # -----------------------------------------------------------------------

    def add_tiers(self, filename, tiers):
        """Add a set of tiers of the file.

        If no annotation was previously selected, select the first annotation
        of the first given tier and notify parent.

        :param filename: (str)
        :param tiers: (list of sppasTier)

        """
        # add tiers into the book
        sel_changed = self.__tiersbook.add_tiers(filename, tiers)
        self.__cur_page = self.__tiersbook.GetSelection()

        # add tier names into the combo
        combo = self.FindWindow("tiers_combo")
        for tier in tiers:
            combo.Append(tier.get_name())
        combo.SetSelection(self.__tiersbook.GetSelection())

        # no tier was previously added and we added at least a non-empty one
        if sel_changed is True:
            sel_filename = self.__tiersbook.get_selected_filename()
            sel_tiername = self.__tiersbook.get_selected_tiername()
            self.notify(action="select_tier", filename=sel_filename, value=sel_tiername)
            self.__cur_index = self.__tierctrl.GetFirstSelected()
            if self.__cur_index == -1:
                changed = self.set_selected_tiername(filename, sel_tiername)
                if changed is True:
                    self.__annotation_selected(self.__cur_index, to_notify=False)

        self.Layout()

    # -----------------------------------------------------------------------

    def __synchro_combo(self):
        """Delete and re-create the list of tiers of the combo to match the book."""
        combo = self.FindWindow("tiers_combo")
        combo.DeleteAll()
        for i in range(self.__tiersbook.GetPageCount()):
            page = self.__tiersbook.GetPage(i)
            combo.Append(page.get_tiername())
        combo.SetSelection(self.__tiersbook.GetSelection())

    # -----------------------------------------------------------------------

    def remove_tiers(self, filename, tiers):
        """Remove a set of tiers of the file.

        :param filename: (str)
        :param tiers: (list of sppasTier)

        """
        removed = self.__tiersbook.remove_tiers(filename, tiers)
        self.__synchro_combo()
        self.__annctrl.set_ann(None)

        # no remaining page in the book
        self.__cur_page = self.__tiersbook.GetSelection()
        if self.__cur_page == wx.NOT_FOUND:
            self.__cur_index = -1

        else:
            # we have to update the selected file/tier/ann
            if removed is True:
                sel_filename = self.__tiersbook.get_selected_filename()
                sel_tiername = self.__tiersbook.get_selected_tiername()
                if sel_tiername is not None:
                    self.notify(action="select_tier", filename=sel_filename, value=sel_tiername)

                    self.__cur_index = self.__tierctrl.GetFirstSelected()
                    if self.__cur_index == -1:
                        changed = self.set_selected_tiername(filename, sel_tiername)
                        if changed is True:
                            self.__annotation_selected(self.__cur_index, to_notify=True)

        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to manage annotations
    # -----------------------------------------------------------------------

    def get_selected_annotation(self):
        """Return the index of the selected annotation, or -1."""
        return self.__cur_index

    # -----------------------------------------------------------------------

    def set_selected_annotation(self, idx):
        """Change the selected annotation.

        :param idx: (int) Index of the annotation to select.
        :return: (bool)

        """
        if self.__tierctrl is None:
            return 0, 0

        valid = True
        if self.__cur_index != -1:
            # An annotation is already selected
            valid = self.__annotation_validator(self.__cur_index)

        if valid is True:
            self.__cur_index = idx
            self.__annotation_selected(idx, to_notify=False)

    # -----------------------------------------------------------------------

    def update(self):
        """Update ui of the current ann."""
        if self.__cur_index != -1:
            self.__tierctrl.UpdateItem(self.__cur_index)
            ann = self.__tierctrl.get_selected_annotation()
            self.__annctrl.set_ann(ann)

    # -----------------------------------------------------------------------

    def delete_annotation(self):
        """Delete the currently selected annotation.

        :return: (int) Index of the deleted annotation. or -1.

        """
        deleted_idx = -1
        if self.__cur_index == -1:
            wx.LogWarning("No annotation is selected.")
        else:

            try:
                self.__tierctrl.delete_annotation(self.__cur_index)
            except Exception as e:
                Error("Annotation can't be deleted: {:s}".format(str(e)))
            else:
                # OK. The annotation was deleted is the listctrl.
                deleted_idx = self.__cur_index

                # new selected annotation
                self.__cur_index = self.__tierctrl.GetFirstSelected()
                self.notify(action="ann_selected", filename=self.get_filename(), value=self.__cur_index)
                if self.__cur_index != -1:
                    self.__annotation_selected(self.__cur_index, to_notify=False)
                else:
                    # clear the annotation editor if no new selected ann
                    self.__annctrl.set_ann(ann=None)

        return deleted_idx

    # -----------------------------------------------------------------------

    def merge_annotation(self, direction):
        """Merge the currently selected annotation.

        :param direction: (int) Positive to merge with next, Negative with prev
        :return: (int, int) Index of the deleted annotation, index of the modified one. or (-1, -1)

        """
        delete_idx = -1
        modified_idx = -1
        if self.__cur_index == -1:
            wx.LogWarning("No annotation is selected.")
        else:

            try:
                merged = self.__tierctrl.merge_annotation(self.__cur_index, direction)
            except Exception as e:
                Error("Annotation can't be merged: {:s}".format(str(e)))
            else:
                if merged is True:
                    # OK. The annotation was merged in the listctrl.
                    if direction > 0:
                        delete_idx = self.__cur_index + 1
                    else:
                        delete_idx = self.__cur_index - 1
                    modified_idx = self.__cur_index
                    ann = self.__tierctrl.get_selected_annotation()
                    self.__annctrl.set_ann(ann)
                    self.notify(action="ann_selected", filename=self.get_filename(), value=self.__cur_index)

        return delete_idx, modified_idx

    # -----------------------------------------------------------------------

    def split_annotation(self, direction):
        """Split the currently selected annotation.

        :param direction: (int) Positive to transport labels to next
        :return: (int, int) Index of the created annotation, index of the modified one. or (-1, -1)

        """
        created_idx = -1
        modified_idx = -1
        if self.__cur_index == -1:
            wx.LogWarning("No annotation is selected.")
        else:

            try:
                self.__tierctrl.split_annotation(self.__cur_index, direction)
            except Exception as e:
                Error("Annotation can't be split: {:s}".format(str(e)))
            else:
                # OK. The annotation was split in the listctrl.
                created_idx = self.__cur_index + 1
                modified_idx = self.__cur_index
                ann = self.__tierctrl.get_selected_annotation()
                self.__annctrl.set_ann(ann)
                self.notify(action="ann_selected", filename=self.get_filename(), value=self.__cur_index)

        return created_idx, modified_idx

    # -----------------------------------------------------------------------

    def add_annotation(self, direction):
        """Add an annotation after/before the currently selected annotation.

        :param direction: (int) Positive add after. Negative to add before.
        :return: (int) Index of the created annotation. or -1

        """
        if self.__cur_index == -1:
            wx.LogWarning("No annotation is selected.")
            return -1

        created_idx = -1
        try:
            added = self.__tierctrl.add_annotation(self.__cur_index, direction)
            if added is True:
                # OK. The annotation was added in the listctrl.
                if direction > 0:
                    created_idx = self.__cur_index + 1
                else:
                    created_idx = self.__cur_index

        except Exception as e:
            Error("Annotation can't be added: {:s}".format(str(e)))

        return created_idx

    # -----------------------------------------------------------------------

    def edit_annotation_metadata(self):
        if self.__cur_index == -1:
            wx.LogWarning("No annotation is selected.")
        else:
            ann = self.__tierctrl.get_selected_annotation()
            MetaDataEdit(self, meta_object=[ann])
            self.update()

        return self.__cur_index

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content of the window.

        - Window 1 of the splitter: a ListCtrl of each tier in a notebook;
        - Window 2 of the splitter: an annotation editor.

        """
        w1 = sppasPanel(self)
        w2 = sppasTiersBook(self, name="tiers_book")

        t1 = self.__create_toolbar1(w1)
        t2 = self.__create_toolbar2(w1)
        a = sppasAnnLabelsCtrl(w1, ann=None, name="annlabels_textctrl")
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(t1, 0, wx.EXPAND)
        s.Add(t2, 0, wx.EXPAND)
        s.Add(a, 1, wx.EXPAND)
        w1.SetSizer(s)

        # Fix size&layout
        if self.__orient == wx.VERTICAL:
            self.SetMinimumPaneSize(sppasPanel.fix_size(128))
            self.SplitHorizontally(w1, w2, sppasPanel.fix_size(256))
        else:
            self.SetMinimumPaneSize(sppasPanel.fix_size(128))
            self.SplitVertically(w1, w2, sppasPanel.fix_size(256))

        self.SetSashGravity(0.4)

    # -----------------------------------------------------------------------

    def __create_toolbar1(self, parent):
        """Create a toolbar for actions on annotations. """
        tb = sppasToolbar(parent, name="anns1_toolbar")
        tb.set_height(24)   # default is 32
        tb.set_focus_color(sppasTiersEditWindow.ANN_COLOUR)

        bcs = tb.AddToggleButton("code_review", value=True, group_name="view_mode")
        bcs.SetToolTip(LABEL_TEXT)
        bcx = tb.AddToggleButton("code_xml", group_name="view_mode")
        bcx.SetToolTip(LABEL_XML)
        bcj = tb.AddToggleButton("code_json", group_name="view_mode")
        bcj.SetToolTip(LABEL_JSON)
        br = tb.AddButton("restore")
        br.SetToolTip(RESTORE)

        tb.AddSpacer(1)

        c = sppasComboBox(tb, choices=list(), name="tiers_combo")
        c.SetMinSize(wx.Size(sppasPanel.fix_size(100), sppasPanel.fix_size(16)))
        c.SetMaxSize(wx.Size(sppasPanel.fix_size(100), sppasPanel.fix_size(16)))
        c.Bind(wx.EVT_COMBOBOX, self._on_combotier_change)
        tb.AddWidget(c)

        return tb

    # -----------------------------------------------------------------------

    def __create_toolbar2(self, parent):
        """Create a toolbar for actions on annotations. """
        tb = sppasToolbar(parent, name="anns1_toolbar")
        tb.set_height(24)  # default is 32
        tb.set_focus_color(sppasTiersEditWindow.ANN_COLOUR)

        meta = tb.AddButton("tags")
        meta.SetToolTip(METADATA)

        bd = tb.AddButton("cell_delete")
        bd.SetToolTip(DELETE)
        bmp = tb.AddButton("cell_merge_previous")
        bmp.SetToolTip(MERGE_PREVIOUS)
        bmn = tb.AddButton("cell_merge_next")
        bmn.SetToolTip(MERGE_NEXT)
        bsp = tb.AddButton("cell_split")
        bsp.SetToolTip(SPLIT_ONE)
        bsn = tb.AddButton("cell_split_next")
        bsn.SetToolTip(SPLIT_TWO)
        bab = tb.AddButton("cell_add_before")
        bab.SetToolTip(ADD_BEFORE)
        baa = tb.AddButton("cell_add_after")
        baa.SetToolTip(ADD_AFTER)

        return tb

    # -----------------------------------------------------------------------

    def swap_panels(self):
        """Swap the panels of the splitter."""
        win_1 = self.GetWindow1()
        win_2 = self.GetWindow2()
        w, h = win_2.GetSize()

        self.Unsplit(toRemove=win_1)
        self.Unsplit(toRemove=win_2)
        if self.__orient == wx.VERTICAL:
            self.SplitHorizontally(win_2, win_1, h)
        else:
            self.SplitVertically(win_2, win_1, w)

        self.SetSashGravity(0.4)
        self.UpdateSize()

    # -----------------------------------------------------------------------
    # A private/quick access to children windows
    # -----------------------------------------------------------------------

    @property
    def __annctrl(self):
        return self.FindWindow("annlabels_textctrl")

    @property
    def __tiersbook(self):
        return self.FindWindow("tiers_book")

    @property
    def __tierctrl(self):
        page_index = self.__tiersbook.GetSelection()
        if page_index == -1:
            return None
        return self.__tiersbook.GetPage(page_index)

    # -----------------------------------------------------------------------

    def switch_ann_mode(self, mode):
        """Change the annotation edit mode to the given one.

        :param mode: (str) One of the accepted modes.
        :return: (bool)

        """
        return self.__annctrl.switch_view(mode)

    # -----------------------------------------------------------------------

    def restore_ann(self):
        """Restore the original annotation."""
        self.__annctrl.update()

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action, filename, value=None):
        """Send an event to the listener (if any).

        :param action: (str) Name of the action to perform
        :param filename: (str) Name of the file
        :param value: (any) Any value to attach to the event/action

        """
        wx.LogDebug("{:s} notifies its parent {:s} of action {:s}."
                    "".format(self.GetName(), self.GetParent().GetName(), action))
        evt = ListannsViewEvent(action=action, filename=filename, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)
        wx.LogDebug("Notify parent {:s} of view event".format(self.GetParent().GetName()))

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Capture some of the events our controls are emitting.

        """
        # Change of page -- the tier currently displayed into the list
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self._on_page_changing)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._on_page_changed)

        # Change of annotation - the line selected into the current list
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_annotation_selected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_annotation_deselected)

        # Toolbar events
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _on_annotation_deselected(self, evt):
        """An annotation is de-selected in the list.

        If the content was modified, we have to push the text content into
        the annotation of the tier.

        """
        self.__can_select = self.__annotation_deselected(evt.GetIndex(), to_notify=False)

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
            self.__tierctrl.Select(self.__cur_index, on=1)

    # -----------------------------------------------------------------------

    def _on_page_changing(self, evt):
        """The book is being to change page.

        Current annotation is de-selected.

        """
        if self.__tierctrl is not None:
            if self.__cur_index != -1:
                c = self.__cur_index
                self.__can_select = self.__annotation_deselected(self.__cur_index)
                self.__tierctrl.Select(c, on=1)

    # -----------------------------------------------------------------------

    def _on_page_changed(self, evt):
        """The book changed its page.

        A new tier is selected, so a new annotation too.

        """
        if self.__can_select is True:
            # self._notify(action="tier_selected", value=None)
            self.__cur_index = self.__tierctrl.GetFirstSelected()
            if self.__cur_index == -1:
                self.__cur_index = 0

            self.__annotation_selected(self.__cur_index)
            self.__cur_page = self.__tiersbook.GetSelection()

        else:
            # go back to the cur_page
            self.__tiersbook.ChangeSelection(self.__cur_page)
            self.__tierctrl.Select(self.__cur_index, on=1)

        page = self.__tiersbook.GetPage(self.__cur_page)

    # -----------------------------------------------------------------------

    def _on_combotier_change(self, event):
        """Switch page..."""
        combo = event.GetEventObject()
        idx = combo.GetSelection()
        self.set_selected_index(idx)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of event.

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "tags":
            self.edit_annotation_metadata()

        elif name in ("code_review", "code_xml", "code_json"):
            self.switch_ann_mode(name)

        elif name == "restore":
            self.restore_ann()

        elif name == "cell_delete":
            idx = self.delete_annotation()
            self.notify(action="ann_delete", filename=self.get_filename(), value=idx)

        elif name == "cell_merge_previous":
            del_idx, modif_idx = self.merge_annotation(-1)
            self.notify(action="ann_delete", filename=self.get_filename(), value=del_idx)
            self.notify(action="ann_update", filename=self.get_filename(), value=modif_idx)

        elif name == "cell_merge_next":
            del_idx, modif_idx = self.merge_annotation(1)
            self.notify(action="ann_delete", filename=self.get_filename(), value=del_idx)
            self.notify(action="ann_update", filename=self.get_filename(), value=modif_idx)

        elif name == "cell_split":
            new_idx, modif_idx = self.split_annotation(0)
            self.notify(action="ann_create", filename=self.get_filename(), value=new_idx)
            self.notify(action="ann_update", filename=self.get_filename(), value=modif_idx)

        elif name == "cell_split_next":
            new_idx, modif_idx = self.split_annotation(1)
            self.notify(action="ann_create", filename=self.get_filename(), value=new_idx)
            self.notify(action="ann_update", filename=self.get_filename(), value=modif_idx)

        elif name == "cell_add_before":
            new_idx = self.add_annotation(-1)
            self.notify(action="ann_create", filename=self.get_filename(), value=new_idx)

        elif name == "cell_add_after":
            new_idx = self.add_annotation(1)
            self.notify(action="ann_create", filename=self.get_filename(), value=new_idx)

        else:
            event.Skip()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __annotation_deselected(self, idx, to_notify=True):
        """De-select the annotation of given index in our controls.

        :return: True if annotation was de-selected.

        """
        if self.__tierctrl is None:
            return False

        valid = self.__annotation_validator(idx)
        if valid is True:
            # deselect the annotation at the given index
            self.__cur_index = -1
            self.__tierctrl.Select(idx, on=0)
            # clear the annotation editor
            self.__annctrl.set_ann(ann=None)
        else:
            self.__cur_index = idx
            self.__tierctrl.Select(idx, on=1)

        if to_notify is True:
            self.notify(action="ann_selected", filename=self.get_filename(), value=self.__cur_index)
        return valid

    # -----------------------------------------------------------------------

    def __annotation_selected(self, idx, to_notify=True):
        """Select the annotation of given index in our controls.

        """
        if self.__tierctrl is None:
            self.__cur_index = -1
            return False

        if self.__tierctrl.GetItemCount() == 0:
            self.__cur_index = -1
            return False

        # On some platform, the listctrl does not support to not select an item
        # so we have to force to select one.
        if idx == -1:
            idx = 0

        self.__tierctrl.Select(idx, on=1)
        ann = self.__tierctrl.get_selected_annotation()
        self.__annctrl.set_ann(ann)
        self.__cur_index = idx
        if to_notify is True:
            self.notify(action="ann_selected", filename=self.get_filename(), value=self.__cur_index)
        return True

    # -----------------------------------------------------------------------

    def __annotation_validator(self, idx):
        """

        :param idx:
        :return: (bool)

        """
        modif = self.__annctrl.text_modified()

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
                ann = self.__tierctrl.get_annotation(idx)
                self.__annctrl.set_ann(ann)
                return True
            else:
                # The user asked to continue editing it.
                return False

        # The annotation labels were modified properly
        else:
            new_labels = self.__annctrl.text_labels()
            # set the new labels to the annotation
            self.__tierctrl.set_annotation_labels(idx, new_labels)
            # set the modified annotation to the annotation editor panel
            ann = self.__tierctrl.get_annotation(idx)
            self.__annctrl.set_ann(ann)
            # notify parent we modified the tier at index idx
            self.notify(action="ann_update", filename=self.get_filename(), value=idx)
            return True

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test Annot Tiers Editor")

        p = sppasTiersEditWindow(self, orient=wx.HORIZONTAL)

        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-phon.xra")

        parser = sppasRW(f1)
        trs1 = parser.read()
        p.add_tiers(f1, trs1.get_tier_list())

        parser.set_filename(f2)
        trs2 = parser.read()
        p.add_tiers(f2, trs2.get_tier_list())

        p.remove_tiers(f1, trs1.get_tier_list())
        p.add_tiers(f1, trs1.get_tier_list())

        t = sppasToolbar(self)
        t.AddSpacer(1)
        t.AddButton("way_up_down")
        t.AddSpacer(1)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(t, 0, wx.EXPAND)
        s.Add(p, 1, wx.EXPAND)
        self.SetSizer(s)

    # -----------------------------------------------------------------------

    def _process_view_event(self, evt):
        logging.debug("Received action {} with value {}"
                      "".format(evt.action, str(evt.value)))
