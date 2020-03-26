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

from sppas.src.config import msg
from sppas.src.utils import u
from sppas.src.anndata import sppasMetaData

from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasListCtrl

# ---------------------------------------------------------------------------

MSG_HEADER_META = u(msg("Metadata", "ui"))

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
        self._backup_metadata(meta_object)
        self._meta = meta_object

        self.CreateHeader(MSG_HEADER_META, "tag")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_cancel)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.LayoutComponents()
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------

    def _backup_metadata(self, meta_object):
        """Copy metadata in a backup."""
        self._back_up = sppasMetaData()
        for key in meta_object.get_meta_keys():
            self._back_up.set_meta(key, meta_object.get_meta(key))

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the dialog."""
        p = sppasPanel(self, name="content")
        tb = self.__create_toolbar(p)
        lst = sppasListCtrl(p)
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(tb, 0, wx.EXPAND)
        s.Add(lst, 1, wx.EXPAND)
        p.SetSizer(s)
        p.Layout()
        self.SetContent(p)

    # ------------------------------------------------------------------------

    def __create_toolbar(self, parent):
        tb = sppasToolbar(parent, orient=wx.VERTICAL)
        tb.SetMinSize(wx.Size(sppasPanel.fix_size(140), -1))

        tb.AddButton("tag_add", "Add tag")
        tb.AddButton("tags", "Annotator tags")
        tb.AddButton("tags", "Project tags")
        tb.AddButton("tags", "Language tags")
        tb.AddButton("tags", "Software tags")
        tb.AddButton("tags", "License tags")
        tb.AddSpacer(1)
        tb.AddButton("tag_del", "Remove")
        tb.AddSpacer(1)
        tb.AddButton("backup", "Restore all")

        return tb

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

    def _restore(self):
        """Restore initial key/values of metadata."""
        # remove all entries of the given metadata
        for key in self._meta.get_meta_keys():
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
