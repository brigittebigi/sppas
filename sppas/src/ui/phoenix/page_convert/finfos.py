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
import wx.dataview

from sppas.src.config import ui_translation
from sppas.src.anndata import sppasRW

from ..windows import sppasPanel
from ..windows import sppasStaticText

# ---------------------------------------------------------------------------


class sppasFormatInfos(sppasPanel):
    """Create the list of file formats with their capabilities.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    # Name of the method <-> text to display
    cols = {
        "metadata_support": ui_translation.gettext('Metadata'),
        "point_support": ui_translation.gettext('Point'),
        "interval_support": ui_translation.gettext('Interval'),
        "alternative_localization_support": ui_translation.gettext('Alt. loc'),
        "alternative_tag_support": ui_translation.gettext('Alt. tag'),
        "radius_support": ui_translation.gettext('Vagueness'),
        "gaps_support": ui_translation.gettext('Gaps'),
        "overlaps_support": ui_translation.gettext('Overlaps'),
        "multi_tiers_support": ui_translation.gettext('Multi tiers'),
        "no_tiers_support": ui_translation.gettext('No tier'),
        "hierarchy_support": ui_translation.gettext('Hierarchy'),
        "ctrl_vocab_support": ui_translation.gettext('Ctrl vocab'),
        "media_support": ui_translation.gettext('Media'),
    }

    # -----------------------------------------------------------------------

    def __init__(self, parent, name="page_format_infos"):
        super(sppasFormatInfos, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE,
            name=name
        )

        self.extensions = sppasRW.TRANSCRIPTION_TYPES.keys()
        self._create_content()
        self.Layout()

    # -----------------------------------------------------------------------

    def get_extension(self):
        """Return the selected file extension."""
        # get the index of the selected row
        selected = self.FindWindow("dvlc").GetSelectedRow()
        return self.extensions[selected]

    # -----------------------------------------------------------------------
    # Create and manage the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        info_txt = sppasStaticText(
            self,
            label="Select the file type to convert to: ")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(info_txt, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(self._create_table(), 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def _create_table(self):
        """Create the table to display information on each format."""
        # Each column is a property of a file format.
        dvlc = wx.dataview.DataViewListCtrl(
            self,
            style=wx.dataview.DV_SINGLE | wx.dataview.DV_HORIZ_RULES | wx.NO_BORDER)
        dvlc.SetName("dvlc")

        w = sppasPanel.fix_size(60)
        # Give it some columns about the file format.
        dvlc.AppendTextColumn(ui_translation.gettext('Extension'),
                              width=int(1.3*w)),
        dvlc.AppendTextColumn(ui_translation.gettext('Software'),
                              width=int(1.7*w),
                              align=wx.ALIGN_CENTER)
        dvlc.AppendTextColumn(ui_translation.gettext('Reader'),
                              width=w, align=wx.ALIGN_CENTER)
        dvlc.AppendTextColumn(ui_translation.gettext('Writer'),
                              width=w, align=wx.ALIGN_CENTER)

        # Properties of the format.
        for c in sppasFormatInfos.cols:
            dvlc.AppendTextColumn(sppasFormatInfos.cols[c],
                                  width=w, align=wx.ALIGN_CENTER)

        # Load the data. Each item (row) is added as a sequence of values
        # whose order matches the columns.
        for extension in self.extensions:
            items = [""]*(4+len(sppasFormatInfos.cols))
            items[0] = " ." + extension
            instance = sppasRW.TRANSCRIPTION_TYPES[extension]()
            items[1] = instance.software
            try:
                instance.read("")
            except NotImplementedError:
                items[2] = ""
            except Exception:
                items[2] = "X"
            try:
                instance.write("")
            except NotImplementedError:
                items[3] = ""
            except Exception:
                items[3] = "X"

            for i, method in enumerate(sppasFormatInfos.cols):
                support = getattr(instance, method)()
                if support is True:
                    items[i+4] = "X"

            dvlc.AppendItem(items)
        dvlc.SelectRow(0)

        return dvlc
