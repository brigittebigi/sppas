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

    ui.phoenix.page_convert.finfos.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Display information about annotated file formats.

"""

import wx
import wx.lib.newevent
import wx.dataview

from sppas.src.config import msg
from sppas.src.utils import u
from sppas.src.anndata import sppasRW
from sppas.src.anndata import FileFormatProperty

from ..windows import sppasPanel
from ..windows import CheckListCtrl

# ---------------------------------------------------------------------------
# Internal use of an event, when a format is selected

FormatChangedEvent, EVT_FORMAT_CHANGED = wx.lib.newevent.NewEvent()
FormatChangedCommandEvent, EVT_FORMAT_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))

# ---------------------------------------------------------------------------


class FileSupports:

    supports = {
        "metadata_support": _('Metadata'),
        "multi_tiers_support": _('Multi tiers'),
        "no_tiers_support": _('No tier'),
        "point_support": _('Point'),
        "interval_support": _('Interval'),
        "gaps_support": _('Gaps'),
        "overlaps_support": _('Overlaps'),
        "hierarchy_support": _('Hierarchy'),
        "ctrl_vocab_support": _('Ctrl vocab'),
        "media_support": _('Media'),
        "radius_support": _('Vagueness'),
        "alternative_localization_support": _('Alt. loc'),
        "alternative_tag_support": _('Alt. tag'),
    }

# ---------------------------------------------------------------------------


class FileFormatPropertySupport(FileFormatProperty):
    """Represent one format and its properties.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, extension):
        """Create a FileFormatProperty instance.

        :param extension: (str) File name extension.

        """
        super(FileFormatPropertySupport, self).__init__(extension)

    # -----------------------------------------------------------------------

    def get_support(self, name):
        if name in list(FileSupports.supports.keys()):
            return getattr(self._instance, name)()
        return False

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __str__(self):
        return 'FileFormatProperty() of extension {!s:s}' \
               ''.format(self._extension)

# ---------------------------------------------------------------------------


class FormatsViewCtrl(sppasPanel):

    def __init__(self, parent, name="list_panel"):
        super(sppasPanel, self).__init__(parent, name=name)
        self.__extensions = list()
        ext = sppasRW.extensions()
        for e in ext:
            self.__extensions.append(sppasRW.TRANSCRIPTION_TYPES[e]().default_extension)
        self._create_content()
        self.__set_pane_size()
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        f = wx.Font(font.GetPointSize(),
                    font.GetFamily(),
                    wx.FONTSTYLE_ITALIC,
                    wx.FONTWEIGHT_NORMAL,
                    font.GetUnderlined(),
                    font.GetFaceName())
        wx.Panel.SetFont(self, f)
        self._listctrl.SetFont(f)

        # The change of font implies to re-draw all proportional objects
        self.__set_pane_size()
        self.Layout()

    # -----------------------------------------------------------------------
    # Manage the data
    # -----------------------------------------------------------------------

    def GetExtension(self):
        """Return the selected file extension or None."""
        selected = self._listctrl.GetFirstSelected()
        if selected == -1:
            return None
        return "." + self.__extensions[selected]

    # -----------------------------------------------------------------------

    def CancelSelected(self):
        """Un-check the selected item."""
        selected = self._listctrl.GetFirstSelected()
        if selected != -1:
            self._listctrl.Select(selected, on=False)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def _create_content(self):
        style = wx.BORDER_NONE | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES
        lst = CheckListCtrl(self, style=style, name="listctrl")

        lst.AppendColumn("Extension",
                         format=wx.LIST_FORMAT_LEFT,
                         width=sppasPanel.fix_size(60))
        lst.AppendColumn("Software",
                         format=wx.LIST_FORMAT_CENTER,
                         width=sppasPanel.fix_size(80))
        lst.AppendColumn("reader",
                         format=wx.LIST_FORMAT_CENTER,
                         width=sppasPanel.fix_size(40))
        lst.AppendColumn("writer",
                         format=wx.LIST_FORMAT_CENTER,
                         width=sppasPanel.fix_size(40))
        for i, c in enumerate(FileSupports.supports):
            t = FileSupports.supports[c]
            lst.AppendColumn(t,
                             format=wx.LIST_FORMAT_CENTER,
                             width=sppasPanel.fix_size(40))

        # Fill rows
        for i, ext in enumerate(self.__extensions):
            ext_object = FileFormatPropertySupport(ext)
            lst.InsertItem(i, ext)
            lst.SetItem(i, 1, ext_object.get_software())
            self.__set_bool_item(i, 2, ext_object.get_reader())
            self.__set_bool_item(i, 3, ext_object.get_writer())
            for j, c in enumerate(FileSupports.supports):
                self.__set_bool_item(i, 4 + j, ext_object.get_support(c))

        sizer = wx.BoxSizer()
        sizer.Add(lst, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __set_bool_item(self, row, col, value):
        if value is True:
            self._listctrl.SetItem(row, col, 'X')
        else:
            self._listctrl.SetItem(row, col, '-')

    # -----------------------------------------------------------------------

    @property
    def _listctrl(self):
        return self.FindWindow("listctrl")

    # -----------------------------------------------------------------------

    def __set_pane_size(self):
        """Fix the size of the child panel."""
        # The listctrl can have an horizontal scrollbar
        bar = 14

        n = self._listctrl.GetItemCount()
        h = int(self.GetFont().GetPixelSize()[1] * 2.)
        self._listctrl.SetMinSize(wx.Size(-1, (n * h) + bar))
        self._listctrl.SetMaxSize(wx.Size(-1, (n * h) + bar + 2))

    # -----------------------------------------------------------------------
    # Events
    # -----------------------------------------------------------------------

    def _on_selected_item(self, evt):
        ext = self.GetExtension()
        evt = FormatChangedEvent(extension=ext)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(FormatsViewCtrl):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
