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

    src.ui.phoenix.dialogs.metaedit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Edit a sppasMetadata() of anndata package: add/remove/modify entries.

"""

import wx
import logging

from sppas.src.config import msg
from sppas.src.utils import u
from sppas.src.anndata import sppasMetaData

from ..panel import sppasPanel
from ..toolbar import sppasToolbar
from ..listctrl import sppasListCtrl
from ..line import sppasStaticLine
from ..text import sppasTextCtrl, sppasStaticText

from .messages import Error
from .dialog import sppasDialog

# ---------------------------------------------------------------------------

MSG_HEADER_META = u(msg("Metadata", "ui"))
MSG_SETS = u(msg("Trusted sets:"))

# ----------------------------------------------------------------------------


class sppasMetaDataEditDialog(sppasDialog):
    """Settings dialogs.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Returns either wx.ID_CANCEL or wx.ID_OK if ShowModal().

    """

    def __init__(self, parent, meta_object):
        """Create a dialog to fix edit metadata.

        :param parent: (wx.Window)

        """
        super(sppasMetaDataEditDialog, self).__init__(
            parent=parent,
            title="MetaDataEdit",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP)

        self._back_up = sppasMetaData()
        self.__backup_metadata(meta_object)
        self._meta = meta_object

        self.CreateHeader(MSG_HEADER_META, "tag")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_cancel)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.LayoutComponents()
        self.CenterOnParent()
        self.GetSizer().Fit(self)
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------
    # Create the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the dialog."""
        panel = sppasPanel(self, name="content")
        entries = self.__create_entries_panel(panel)
        lst = self.__create_list(panel)
        tb2 = self.__create_toolbar_groups(panel)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(lst, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, sppasPanel.fix_size(8))
        s.Add(entries, 0, wx.EXPAND)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(s, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        main_sizer.Add(self.__create_vline(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        main_sizer.Add(tb2, 0, wx.EXPAND | wx.BOTTOM, sppasPanel.fix_size(8))
        panel.SetSizer(main_sizer)
        panel.Layout()
        self.SetContent(panel)

    # ------------------------------------------------------------------------

    def __create_entries_panel(self, parent):
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
        s.Add(fgs, 3, wx.EXPAND)
        s.Add(tb, 2, wx.EXPAND | wx.LEFT, 2)
        p.SetSizer(s)
        return p

    # ------------------------------------------------------------------------

    def __create_toolbar(self, parent):
        tb = sppasToolbar(parent, orient=wx.HORIZONTAL)
        b = tb.AddButton("tag_add")
        b.SetBorderWidth(1)
        b = tb.AddButton("tag_del")
        b.SetBorderWidth(1)
        return tb

    # ------------------------------------------------------------------------

    def __create_toolbar_groups(self, parent):
        tb = sppasToolbar(parent, orient=wx.VERTICAL)
        tb.SetMinSize(wx.Size(sppasPanel.fix_size(120), -1))

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

    # ------------------------------------------------------------------------

    def __create_list(self, parent):
        lst = sppasListCtrl(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, name="lstctrl")
        lst.SetMinSize(wx.Size(sppasPanel.fix_size(400), -1))

        lst.AppendColumn("Key", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(120))
        lst.AppendColumn("Value", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(500))

        for key in self._meta.get_meta_keys():
            value = self._meta.get_meta(key)
            idx = lst.InsertItem(lst.GetItemCount(), key)
            lst.SetItem(idx, 1, value)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_deselected_item)

        return lst

    # -----------------------------------------------------------------------

    def __create_vline(self, parent):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(parent, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(7, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(1)
        return line

    # -----------------------------------------------------------------------

    @property
    def _lstctrl(self):
        return self.FindWindow("lstctrl")

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

        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def on_cancel(self, event):
        """Restore initial settings and close dialog."""
        self.restore()
        # close the dialog with a wx.ID_CANCEL response
        self.SetReturnCode(wx.ID_CANCEL)
        event.Skip()

    # ------------------------------------------------------------------------

    def _on_selected_item(self, evt):
        idx = evt.GetIndex()
        self._entry_key.SetValue(self._lstctrl.GetItemText(idx, 0))
        self._entry_val.SetValue(self._lstctrl.GetItemText(idx, 1))

    # ------------------------------------------------------------------------

    def _on_deselected_item(self, evt):
        self._entry_key.SetValue("")
        self._entry_val.SetValue("")

    # ------------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------------

    def __backup_metadata(self, meta_object):
        """Copy metadata in a backup."""
        self._back_up = sppasMetaData()
        for key in meta_object.get_meta_keys():
            self._back_up.set_meta(key, meta_object.get_meta(key))

    # -----------------------------------------------------------------------

    def set_meta(self):
        """Add or modify an entry of the metadata."""
        key = self._entry_key.GetValue().strip()
        if len(key) == 0:
            wx.LogWarning("A key must be defined to add an entry in the metadata.")
        else:
            val = self._entry_val.GetValue()
            if self._meta.is_meta_key(key):
                # The key is already in the list (but which item?)
                idx = 0
                while self._lstctrl.GetItemText(idx, 0) != key:
                    idx += 1
                    if idx > self._lstctrl.GetItemCount():
                        wx.LogError("Key {} not found...")
                        return
                self._meta.set_meta(key, val)
                value = self._meta.get_meta(key)
                self._lstctrl.SetItem(idx, 1, value)
                self._lstctrl.Select(idx, on=1)

            else:
                # The key is unknown. Add a new entry
                self._meta.set_meta(key, val)
                value = self._meta.get_meta(key)
                idx = self._lstctrl.InsertItem(self._lstctrl.GetItemCount(), key)
                self._lstctrl.SetItem(idx, 1, value)
                self._lstctrl.Select(idx, on=1)

    # -----------------------------------------------------------------------

    def set_meta_group(self, group_name):
        """Add a group of trusted metadata."""
        if group_name == "license":
            self._meta.add_license_metadata(0)

        elif group_name == "language":
            self._meta.add_language_metadata()

        elif group_name == "software":
            self._meta.add_software_metadata()

        elif group_name == "project":
            self._meta.add_project_metadata()

        elif group_name == "annotator":
            self._meta.add_annotator_metadata()

        # Update the listctrl
        listctrl_keys = [self._lstctrl.GetItemText(i, 0) for i in range(self._lstctrl.GetItemCount())]
        for key in self._meta.get_meta_keys():
            if key not in listctrl_keys:
                value = self._meta.get_meta(key)
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
                self._meta.pop_meta(self._lstctrl.GetItemText(item, 0))
            except ValueError as e:
                Error(str(e))
                item = -1
            else:
                self._entry_key.SetValue("")
                self._entry_val.SetValue("")
                self._lstctrl.DeleteItem(item)

        return item

    # -----------------------------------------------------------------------

    def restore(self):
        """Restore backup to metadata."""
        # remove entries of the given metadata if there are not in the backup
        keys = list()
        for key in self._meta.get_meta_keys():
            if self._back_up.is_meta_key(key) is False:
                keys.append(key)
        for key in reversed(keys):
            try:
                self._meta.pop_meta(key)
            except ValueError:
                pass

        # add keys/values of the backup or modify the value
        for key in self._back_up.get_meta_keys():
            self._meta.set_meta(key, self._back_up.get_meta(key))

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
