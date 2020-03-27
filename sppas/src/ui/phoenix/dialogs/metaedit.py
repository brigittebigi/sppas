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

from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasListCtrl
from ..windows import sppasStaticLine

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
        p = sppasPanel(self, name="content")
        tb1 = self.__create_toolbar(p)
        lst = self.__create_list(p)
        tb2 = self.__create_toolbar_groups(p)
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(tb1, 0, wx.EXPAND)
        s.Add(lst, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, sppasPanel.fix_size(12))
        s.Add(tb2, 0, wx.EXPAND)
        p.SetSizer(s)
        p.Layout()
        self.SetContent(p)

    # ------------------------------------------------------------------------

    def __create_toolbar(self, parent):
        tb = sppasToolbar(parent, orient=wx.VERTICAL)
        tb.SetMinSize(wx.Size(sppasPanel.fix_size(120), -1))

        tb.AddSpacer(1)
        b = tb.AddButton("tag_add", "Add tag")
        b.SetBorderWidth(1)
        b = tb.AddButton("tag_del", "Remove")
        b.SetBorderWidth(1)
        b = tb.AddButton("backup", "Restore")
        b.SetBorderWidth(1)
        tb.AddSpacer(1)

        return tb

    # ------------------------------------------------------------------------

    def __create_toolbar_groups(self, parent):
        tb = sppasToolbar(parent, orient=wx.VERTICAL)
        tb.SetMinSize(wx.Size(sppasPanel.fix_size(120), -1))

        tb.AddTitleText("Trusted sets:")
        b = tb.AddButton("tags", "Annotator")
        b.SetBorderWidth(1)
        b = tb.AddButton("tags", "Project")
        b.SetBorderWidth(1)
        b = tb.AddButton("tags", "Language")
        b.SetBorderWidth(1)
        b = tb.AddButton("tags", "Software")
        b.SetBorderWidth(1)
        b = tb.AddButton("tags", "License")
        b.SetBorderWidth(1)

        return tb

    # ------------------------------------------------------------------------

    def __create_list(self, parent):
        lst = sppasListCtrl(parent, style=wx.LC_REPORT | wx.LC_EDIT_LABELS)
        lst.SetMinSize(wx.Size(sppasPanel.fix_size(240), -1))

        lst.AppendColumn("Key", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(120))
        lst.AppendColumn("Value", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(400))

        for key in self._meta.get_meta_keys():
            value = self._meta.get_meta(key)
            idx = lst.InsertItem(lst.GetItemCount(), key)
            lst.SetItem(idx, 1, value)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_deselected_item)

        return lst

    # -----------------------------------------------------------------------

    def __create_vline(self):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(6, -1))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        return line

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
        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def on_cancel(self, event):
        """Restore initial settings and close dialog."""
        self._restore()
        # close the dialog with a wx.ID_CANCEL response
        self.SetReturnCode(wx.ID_CANCEL)
        event.Skip()

    # ------------------------------------------------------------------------

    def _on_selected_item(self, evt):
        logging.debug("Parent received selected item event. Index {}"
                      "".format(evt.GetIndex()))

    # ------------------------------------------------------------------------

    def _on_deselected_item(self, evt):
        logging.debug("Parent received de-selected item event. Index {}"
                      "".format(evt.GetIndex()))

    # ------------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------------

    def __backup_metadata(self, meta_object):
        """Copy metadata in a backup."""
        self._back_up = sppasMetaData()
        for key in meta_object.get_meta_keys():
            self._back_up.set_meta(key, meta_object.get_meta(key))

    # -----------------------------------------------------------------------

    def _restore(self):
        """Restore backup to metadata."""
        # remove all entries of the given metadata
        keys = list()
        for key in self._meta.get_meta_keys():
            keys.append(key)
        for key in reversed(keys):
            self._meta.pop_meta(key)
        # add keys and values of the backup
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
