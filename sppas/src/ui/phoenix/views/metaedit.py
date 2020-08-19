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

    src.ui.phoenix.views.metaedit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Edit a sppasMetadata() of anndata package: add/remove/modify entries.

"""

import wx
import logging

from sppas.src.config import msg
from sppas.src.utils import u
from sppas.src.anndata import sppasMetaData

from src.ui.phoenix.windows.panel import sppasPanel
from src.ui.phoenix.windows.toolbar import sppasToolbar
from src.ui.phoenix.windows.listctrl import sppasListCtrl
from src.ui.phoenix.windows.line import sppasStaticLine
from src.ui.phoenix.windows.text import sppasTextCtrl, sppasStaticText
from src.ui.phoenix.windows.book import sppasSimplebook
from src.ui.phoenix.windows.buttons import BitmapButton

from src.ui.phoenix.windows.dialogs.messages import Error
from src.ui.phoenix.windows.dialogs.dialog import sppasDialog

# ---------------------------------------------------------------------------

MSG_HEADER_META = u(msg("Metadata", "ui"))
MSG_SETS = u(msg("Trusted sets:"))

# ----------------------------------------------------------------------------


class sppasMetaDataEditDialog(sppasDialog):
    """Dialog to edit sppasMetaData instances.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Returns either wx.ID_CANCEL or wx.ID_OK if ShowModal().

    """

    def __init__(self, parent, meta_objects=()):
        """Create a dialog to fix edit metadata.

        :param parent: (wx.Window)
        :param meta_objects: (list of sppasMetaData())

        """
        super(sppasMetaDataEditDialog, self).__init__(
            parent=parent,
            title="MetaDataEdit",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP)

        self._meta = dict()      # key=panel, value=sppasMetaData() [modifiable]
        self._back_up = dict()   # key=id, value=sppasMetaData() [non-modifiable]
        self.__backup_metadata(meta_objects)

        self.CreateHeader(MSG_HEADER_META, "tags")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        # Add metadata instances in the book
        if len(meta_objects) == 0:
            self.add_metadata(sppasMetaData())
        else:
            for meta in meta_objects:
                self.add_metadata(meta)

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_cancel)
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_deselected_item)

        self.LayoutComponents()
        self.CenterOnParent()
        self.GetSizer().Fit(self)
        self.FadeIn()

    # -----------------------------------------------------------------------

    def add_metadata(self, meta_obj):
        """Create a page of the book with the given metadata.

        :param meta_obj: (sppasMetaData)

        """
        page = self.__create_list(self._book, meta_obj)
        self._meta[page] = meta_obj

        if len(self._meta) == 1:
            self._book.ShowNewPage(page)
        else:
            self._book.AddPage(page, text="")

    # -----------------------------------------------------------------------
    # Create the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the dialog."""
        panel = sppasPanel(self, name="content")
        bp = self.__create_book(panel)
        entries = self.__create_entries_panel(panel)
        tb2 = self.__create_toolbar_groups(panel)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(bp, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        s.Add(entries, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(s, 1, wx.EXPAND | wx.LEFT, 2)
        main_sizer.Add(self.__create_vline(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        main_sizer.Add(tb2, 0, wx.EXPAND | wx.RIGHT | wx.BOTTOM, 2)
        panel.SetSizer(main_sizer)
        panel.Layout()
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def __create_book(self, parent):
        """Create the simple book to manage the several pages of the frame."""
        pb = sppasPanel(parent, name="book_panel")
        btn_left = BitmapButton(pb, name="arrow_left")
        btn_left.SetFocusWidth(0)
        btn_left.SetMinSize(wx.Size(sppasPanel.fix_size(32), -1))
        btn_right = BitmapButton(pb, name="arrow_right")
        btn_right.SetFocusWidth(0)
        btn_right.SetMinSize(wx.Size(sppasPanel.fix_size(32), -1))

        book = sppasSimplebook(
            parent=pb,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS,
            name="book_list"
        )
        book.SetEffectsTimeouts(150, 200)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(btn_left, 0, wx.EXPAND)
        sizer.Add(book, 1, wx.EXPAND)
        sizer.Add(btn_right, 0, wx.EXPAND)
        pb.SetSizer(sizer)

        return pb

    # ------------------------------------------------------------------------

    def __create_entries_panel(self, parent):
        """Create a panel to edit an entry: key and value."""
        p = sppasPanel(parent, name="entries_panel")

        txt1 = sppasStaticText(p, label="Key: ")
        txt2 = sppasStaticText(p, label="Value: ")
        txt_key = sppasTextCtrl(p, name="entry_key")
        txt_val = sppasTextCtrl(p, name="entry_val")

        fgs = wx.FlexGridSizer(2, 2, 10, 10)
        fgs.AddMany([(txt1), (txt_key, 1, wx.EXPAND), (txt2), (txt_val, 1, wx.EXPAND)])
        fgs.AddGrowableCol(1, 1)

        tb = self.__create_toolbar(p)

        s = wx.BoxSizer(wx.HORIZONTAL)
        s.AddStretchSpacer(1)
        s.Add(fgs, 2, wx.EXPAND)
        s.Add(tb, 1, wx.EXPAND | wx.LEFT, 2)
        s.AddStretchSpacer(1)
        p.SetSizer(s)
        return p

    # ------------------------------------------------------------------------

    def __create_toolbar(self, parent):
        """Create a toolbar for actions on an entry."""
        tb = sppasToolbar(parent, orient=wx.HORIZONTAL)
        b = tb.AddButton("tag_add")
        b.SetBorderWidth(1)
        b = tb.AddButton("tag_del")
        b.SetBorderWidth(1)
        return tb

    # ------------------------------------------------------------------------

    def __create_toolbar_groups(self, parent):
        """Create a toolbar to add groups of entries."""
        tb = sppasToolbar(parent, orient=wx.VERTICAL)
        tb.SetMinSize(wx.Size(sppasPanel.fix_size(120), -1))

        b = tb.AddButton("restore", "Restore")
        b.SetBorderWidth(1)

        tb.AddTitleText("Trusted sets:")
        b = tb.AddTextButton("add_annotator", "Annotator")
        b.SetBorderWidth(1)
        b = tb.AddTextButton("add_project", "Project")
        b.SetBorderWidth(1)
        b = tb.AddTextButton("add_language", "Language")
        b.SetBorderWidth(1)
        b = tb.AddTextButton("add_software", "Software")
        b.SetBorderWidth(1)
        b = tb.AddTextButton("add_license", "License")
        b.SetBorderWidth(1)

        return tb

    # -----------------------------------------------------------------------

    def __create_vline(self, parent):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(parent, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(5, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(1)
        return line

    # ------------------------------------------------------------------------

    def __create_list(self, parent, meta_object):
        """Create a page of the book: list of key/value of a sppasMetadata."""
        lst = sppasListCtrl(parent,
                            style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
                            name="lstctrl")

        lst.AppendColumn("Key", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(120))
        lst.AppendColumn("Value", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(400))

        for key in meta_object.get_meta_keys():
            value = meta_object.get_meta(key)
            idx = lst.InsertItem(lst.GetItemCount(), key)
            lst.SetItem(idx, 1, value)

        return lst

    # -----------------------------------------------------------------------

    @property
    def _book(self):
        return self.FindWindow("book_list")

    @property
    def _page(self):
        page_index = self._book.GetSelection()
        if page_index == -1:
            return None
        return self._book.GetPage(page_index)

    @property
    def _lstctrl(self):
        return self._page.FindWindow("lstctrl")

    @property
    def _entry_key(self):
        return self.FindWindow("entry_key")

    @property
    def _entry_val(self):
        return self.FindWindow("entry_val")

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "cancel":
            self.on_cancel(event)

        elif event_name == "tag_add":
            self.set_meta()

        elif event_name == "tag_del":
            self.delete_selected()

        elif event_name.startswith("add_"):
            self.set_meta_group(event_name[4:])

        elif event_name == "arrow_left":
            self._show_page(-1)

        elif event_name == "arrow_right":
            self._show_page(1)

        elif event_name == "restore":
            meta_obj = self._meta[self._page]
            for i in reversed(range(len(meta_obj.get_meta_keys()))):
                self._lstctrl.DeleteItem(i)
            self.restore(meta_obj)
            for key in meta_obj.get_meta_keys():
                value = meta_obj.get_meta(key)
                idx = self._lstctrl.InsertItem(self._lstctrl.GetItemCount(), key)
                self._lstctrl.SetItem(idx, 1, value)
            self._entry_key.SetValue("")
            self._entry_val.SetValue("")

        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def _show_page(self, direction):
        """Show next or previous page."""
        page_index = self._book.GetSelection()
        if page_index == -1:
            return None
        if direction == 0:
            return
        elif direction > 0:
            next_page_index = (page_index + 1) % len(self._meta)
            self._book.SetEffects(
                showEffect=wx.SHOW_EFFECT_SLIDE_TO_LEFT,
                hideEffect=wx.SHOW_EFFECT_SLIDE_TO_LEFT)
        elif direction < 0:
            next_page_index = (page_index - 1) % len(self._meta)
            self._book.SetEffects(
                showEffect=wx.SHOW_EFFECT_SLIDE_TO_RIGHT,
                hideEffect=wx.SHOW_EFFECT_SLIDE_TO_RIGHT)

        # then change to the page
        self._book.ChangeSelection(next_page_index)

        # We'll keep the same Key/Value in the entry fields
        # (it allows to copy it from a meta to another one)
        idx = self._lstctrl.GetFirstSelected()
        if idx != -1:
            self._lstctrl.Select(idx, on=0)
        self.Layout()
        self.Refresh()

    # ------------------------------------------------------------------------

    def on_cancel(self, event):
        """Restore initial settings and close dialog."""
        self.restore_all()
        # close the dialog with a wx.ID_CANCEL response
        self.SetReturnCode(wx.ID_CANCEL)
        event.Skip()

    # ------------------------------------------------------------------------

    def _on_selected_item(self, evt):
        idx = evt.GetIndex()
        key = self._lstctrl.GetItemText(idx, 0)
        if key.startswith("private_") is False:
            self._entry_key.SetValue(key)
            self._entry_val.SetValue(self._lstctrl.GetItemText(idx, 1))
        else:
            wx.LogMessage("Private keys can't be edited.")

    # ------------------------------------------------------------------------

    def _on_deselected_item(self, evt):
        self._entry_key.SetValue("")
        self._entry_val.SetValue("")

    # ------------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------------

    def __backup_metadata(self, meta_objects):
        """Copy all metadata in a backup."""
        self._back_up = dict()
        for meta in meta_objects:
            svd = sppasMetaData()
            for key in meta.get_meta_keys():
                svd.set_meta(key, meta.get_meta(key))
            self._back_up[svd.get_meta("id")] = svd

    # -----------------------------------------------------------------------

    def set_meta(self):
        """Add or modify an entry of the metadata."""
        key = self._entry_key.GetValue().strip()
        if len(key) == 0:
            wx.LogWarning("A key must be defined to add an entry in the metadata.")
        else:
            val = self._entry_val.GetValue()
            if self._meta[self._page].is_meta_key(key):
                # The key is already in the list (but which item?)
                idx = 0
                while self._lstctrl.GetItemText(idx, 0) != key:
                    idx += 1
                    if idx > self._lstctrl.GetItemCount():
                        wx.LogError("Key {} not found...")
                        return
                self._meta[self._page].set_meta(key, val)
                value = self._meta[self._page].get_meta(key)
                self._lstctrl.SetItem(idx, 1, value)
                self._lstctrl.Select(idx, on=1)

            else:
                # The key is unknown. Add a new entry
                self._meta[self._page].set_meta(key, val)
                value = self._meta[self._page].get_meta(key)
                idx = self._lstctrl.InsertItem(self._lstctrl.GetItemCount(), key)
                self._lstctrl.SetItem(idx, 1, value)
                self._lstctrl.Select(idx, on=1)

    # -----------------------------------------------------------------------

    def set_meta_group(self, group_name):
        """Add a group of trusted metadata."""
        if group_name == "license":
            self._meta[self._page].add_license_metadata(0)

        elif group_name == "language":
            self._meta[self._page].add_language_metadata()

        elif group_name == "software":
            self._meta[self._page].add_software_metadata()

        elif group_name == "project":
            self._meta[self._page].add_project_metadata()

        elif group_name == "annotator":
            self._meta[self._page].add_annotator_metadata()

        # Update the listctrl
        listctrl_keys = [self._lstctrl.GetItemText(i, 0) for i in range(self._lstctrl.GetItemCount())]
        for key in self._meta[self._page].get_meta_keys():
            if key not in listctrl_keys:
                value = self._meta[self._page].get_meta(key)
                idx = self._lstctrl.InsertItem(self._lstctrl.GetItemCount(), key)
                self._lstctrl.SetItem(idx, 1, value)

    # -----------------------------------------------------------------------

    def delete_selected(self):
        """Delete the currently selected metadata, except if 'id'."""
        item = self._lstctrl.GetFirstSelected()
        if item == -1:
            wx.LogWarning("No selected entry in the list to delete.")
        else:
            try:
                self._meta[self._page].pop_meta(self._lstctrl.GetItemText(item, 0))
            except ValueError as e:
                Error(str(e))
                item = -1
            else:
                self._entry_key.SetValue("")
                self._entry_val.SetValue("")
                self._lstctrl.DeleteItem(item)

        return item

    # -----------------------------------------------------------------------

    def restore_all(self):
        """Restore backup to metadata of all pages."""
        for page in self._meta:
            meta_obj = self._meta[page]
            self.restore(meta_obj)

    # -----------------------------------------------------------------------

    def restore(self, meta_obj):
        """Restore backup to metadata."""
        # remove entries of the given metadata if there are not in the backup
        keys = list()
        # find the backup and the corresponding metadata to restore
        meta_id = meta_obj.get_meta("id")
        meta_back_up = self._back_up[meta_id]

        for key in meta_obj.get_meta_keys():
            if meta_back_up.is_meta_key(key) is False:
                keys.append(key)
        for key in reversed(keys):
            try:
                meta_obj.pop_meta(key)
            except ValueError:
                pass

        # add keys/values of the backup or modify the value
        for key in meta_back_up.get_meta_keys():
            meta_obj.set_meta(key, meta_back_up.get_meta(key))

# -------------------------------------------------------------------------


def MetaDataEdit(parent, meta_object=None):
    """Display a dialog to edit metadata.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :param parent: (wx.Window)
    :param meta_object: (sppasMetaData)
    :returns: the response

    wx.ID_CANCEL is returned if the dialog is destroyed or if no e-mail
    was sent.

    """
    dialog = sppasMetaDataEditDialog(parent, meta_object)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response
