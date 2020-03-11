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

from ..windows import sppasPanel
from ..windows import sppasSplitterWindow
from ..windows.dialogs import Confirm, Error
from ..windows.book import sppasNotebook
from ..main_events import ViewEvent, EVT_VIEW

from .ann import sppasAnnEditPanel
from .tierctrl import sppasTierListCtrl

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

    def set_selected_tiername(self, filename, tier_name):
        """Change page selection of the notebook to match given data.

        :return: (bool)

        """
        # De-select the currently selected annotation.
        if self.__cur_index != -1:
            c = self.__cur_index
            self.__can_select = self.__annotation_deselected(self.__cur_index)
            self.__tierctrl.Select(c, on=1)

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
                    ann = self.__tierctrl.get_selected_annotation()
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
                page = sppasTierListCtrl(self.__notebook, tier, filename, style=wx.BORDER_SIMPLE)
                page.Bind(wx.EVT_KEY_UP, self._on_char)

                self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_annotation_selected, page)
                self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_annotation_deselected, page)
                self.__notebook.AddPage(page, tier.get_name())
                if sel_tier is None:
                    sel_tier = tier
            else:
                wx.LogError("Page not created. "
                            "No annotation in tier: {:s}".format(tier.get_name()))

        # no tier was previously added and we added at least a non-empty one
        if self.__tierctrl is None and sel_tier is not None:
            self.__cur_index = self.__tierctrl.GetFirstSelected()
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
        if self.__tierctrl is None:
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
        # w1 = sppasNotebook(self, style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL, name="tiers_notebook")
        w1 = wx.Choicebook(self, style=wx.TAB_TRAVERSAL, name="tiers_notebook")
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
    def __tierctrl(self):
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
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self._on_page_changing)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._on_page_changed)
        
        self.Bind(wx.EVT_BUTTON, self._process_toolbar_event)

        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

    # -----------------------------------------------------------------------

    def _on_char(self, evt):
        kc = evt.GetKeyCode()
        if kc in (8, 127):  # Suppr or Del
            self.__delete_annotation()
        elif kc == 43:
            if evt.ControlDown() is False:
                self.__add_annotation(1)
            else:
                self.__add_annotation(-1)
        else:
            evt.Skip()

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

        elif btn_name == "cell_add_before":
            self.__add_annotation(-1)

        elif btn_name == "cell_add_after":
            self.__add_annotation(1)

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
            self.__tierctrl.Select(self.__cur_index, on=1)

    # -----------------------------------------------------------------------

    def _on_page_changing(self, evt):
        """The notebook is being to change page.

        Current annotation is de-selected.

        """
        if self.__tierctrl is not None:
            if self.__cur_index != -1:
                c = self.__cur_index
                self.__can_select = self.__annotation_deselected(self.__cur_index)
                self.__tierctrl.Select(c, on=1)

    # -----------------------------------------------------------------------

    def _on_page_changed(self, evt):
        """The notebook changed its page.

        A new tier is selected, so a new annotation too.

        """
        if self.__can_select is True:
            self._notify(action="tier_selected", value=None)
            self.__cur_index = self.__tierctrl.GetFirstSelected()
            if self.__cur_index == -1:
                logging.debug("No annotation was previously selected in {}"
                              "".format(self.get_selected_tiername()))
                self.__cur_index = 0

            self.__annotation_selected(self.__cur_index)
            self.__cur_page = self.__notebook.GetSelection()
        else:
            # go back to the cur_page
            self.__notebook.ChangeSelection(self.__cur_page)
            self.__tierctrl.Select(self.__cur_index, on=1)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __delete_annotation(self):
        """Delete the currently selected annotation."""
        if self.__cur_index == -1:
            return

        try:
            self.__tierctrl.delete_annotation(self.__cur_index)
        except Exception as e:
            Error("Annotation can't be deleted: {:s}".format(str(e)))
        else:
            # OK. The annotation was deleted is the listctrl.
            self._notify(action="ann_deleted", value=self.__cur_index)

            # new selected annotation
            self.__cur_index = self.__tierctrl.GetFirstSelected()
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
        if self.__cur_index == -1:
            return

        try:
            merged = self.__tierctrl.merge_annotation(self.__cur_index, direction)
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
                ann = self.__tierctrl.get_selected_annotation()
                self.__annpanel.set_ann(ann)

    # -----------------------------------------------------------------------

    def __split_annotation(self, direction):
        """Split the currently selected annotation.

        :param direction: (int) Positive to transport labels to next

        """
        if self.__cur_index == -1:
            return

        try:
            self.__tierctrl.split_annotation(self.__cur_index, direction)
        except Exception as e:
            Error("Annotation can't be split: {:s}".format(str(e)))
        else:
            # OK. The annotation was split in the listctrl.
            self._notify(action="ann_created", value=self.__cur_index+1)
            self._notify(action="ann_modified", value=self.__cur_index)
            ann = self.__tierctrl.get_selected_annotation()
            self.__annpanel.set_ann(ann)

    # -----------------------------------------------------------------------

    def __add_annotation(self, direction):
        """Add an annotation after/before the currently selected annotation.

        :param direction: (int) Positive add after. Negative to add before.

        """
        if self.__cur_index == -1:
            return

        try:
            added = self.__tierctrl.add_annotation(self.__cur_index, direction)
        except Exception as e:
            Error("Annotation can't be added: {:s}".format(str(e)))
        else:
            if added is True:
                # OK. The annotation was added in the listctrl.
                if direction > 0:
                    self._notify(action="ann_created", value=self.__cur_index+1)
                else:
                    self._notify(action="ann_created", value=self.__cur_index)
                    self.__cur_index += 1

    # -----------------------------------------------------------------------

    def __annotation_deselected(self, idx):
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
            self.__annpanel.set_ann(ann=None)
        else:
            self.__cur_index = idx
            self.__tierctrl.Select(idx, on=1)

        self._notify(action="ann_selected", value=self.__cur_index)
        return valid

    # -----------------------------------------------------------------------

    def __annotation_selected(self, idx):
        """Select the annotation of given index in our controls.

        """
        if self.__tierctrl is None:
            return 0, 0

        self.__tierctrl.Select(idx, on=1)
        ann = self.__tierctrl.get_selected_annotation()
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
                ann = self.__tierctrl.get_annotation(idx)
                self.__annpanel.set_ann(ann)
                return True
            else:
                # The user asked to continue editing it.
                return False

        # The annotation labels were modified properly
        else:
            new_labels = self.__annpanel.text_labels()
            # set the new labels to the annotation
            self.__tierctrl.set_annotation_labels(idx, new_labels)
            # set the modified annotation to the annotation editor panel
            ann = self.__tierctrl.get_annotation(idx)
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

