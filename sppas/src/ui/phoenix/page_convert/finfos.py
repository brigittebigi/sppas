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

from sppas.src.config import ui_translation
from sppas.src.anndata import sppasRW


from ..tools import sppasSwissKnife
from ..windows.image import ColorizeImage
from ..windows import sppasPanel
from ..windows import sppasStaticText

# ---------------------------------------------------------------------------
# Internal use of an event, when a format is selected

FormatChangedEvent, EVT_FORMAT_CHANGED = wx.lib.newevent.NewEvent()
FormatChangedCommandEvent, EVT_FORMAT_CHANGED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------


class SelectedIconRenderer(wx.dataview.DataViewCustomRenderer):
    """Draw an icon matching the state of a row (select/unselect).

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    ICON_NAMES = {
        True: "radio_checked",
        False: "radio_unchecked",
    }

    def __init__(self):
        super(SelectedIconRenderer, self).__init__(
            varianttype="wxBitmap",
            mode=wx.dataview.DATAVIEW_CELL_INERT,
            align=wx.dataview.DVR_DEFAULT_ALIGNMENT)
        self.value = False

    def SetValue(self, value):
        """Assign a boolean value."""
        self.value = bool(value)
        return True

    def GetValue(self):
        """Return the boolean value."""
        return self.value

    def GetSize(self):
        """Return the size needed to display the value."""
        size = self.GetTextExtent('TT')
        return size[1]*2, size[1]*2

    def Render(self, rect, dc, state):
        """Draw the bitmap, adjusting its size. """
        if self.value == "":
            return False

        x, y, w, h = rect
        s = min(w, h)
        s = int(0.7 * s)

        if self.value in SelectedIconRenderer.ICON_NAMES:
            icon_value = SelectedIconRenderer.ICON_NAMES[self.value]

            # get the image from its name
            img = sppasSwissKnife.get_image(icon_value)
            # re-scale the image to the expected size
            sppasSwissKnife.rescale_image(img, s)
            # re-colorize
            ColorizeImage(img, wx.BLACK, wx.Colour(128, 128, 128, 128))
            # convert to bitmap
            bitmap = wx.Bitmap(img)
            # render it at the center
            dc.DrawBitmap(bitmap, x + (w-s)//2, y + (h-s)//2)

        return True

# ---------------------------------------------------------------------------


class sppasFormatInfos(sppasPanel):
    """Create the list of file formats with their capabilities.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    # Name of the method <-> header to display for the column
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

    def __init__(self, parent, name="panel_format_infos"):
        super(sppasFormatInfos, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE,
            name=name
        )

        self.__extensions = list(sppasRW.TRANSCRIPTION_TYPES.keys())
        self.__selected = -1
        self._create_content()
        self.Layout()

    # -----------------------------------------------------------------------

    def CancelSelected(self):
        """Unselect the currently selected format."""
        # We already had a selected row
        if self.__selected != -1:
            self.FindWindow("dvlc").SetValue(False, self.__selected, 0)

        # OK. No selected row.
        self.__selected = -1

    # -----------------------------------------------------------------------
    # Create and manage the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        info_txt = sppasStaticText(
            self,
            label="Select the file type to convert to: ")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(info_txt, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer.Add(self._create_table(), 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def _create_table(self):
        """Create the table to display information on each format."""
        dvlc = wx.dataview.DataViewListCtrl(
            self,
            style=wx.dataview.DV_SINGLE | wx.dataview.DV_HORIZ_RULES | wx.NO_BORDER)
        dvlc.SetName("dvlc")

        # Append the required columns
        self.__append_selection_column(dvlc)
        self.__append_format_columns(dvlc)
        # Optional columns are properties of each file format.
        self.__append_property_columns(dvlc)

        # Load the data.
        self.__fill_rows(dvlc)

        dvlc.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED,
                  self.__set_selected)
        return dvlc

    # -----------------------------------------------------------------------

    @staticmethod
    def __append_selection_column(dvlc):
        """Append the selection column to the table at given index."""
        col = wx.dataview.DataViewColumn(
            title="",
            renderer=SelectedIconRenderer(),
            model_column=0,
            width=sppasPanel.fix_size(30))
        dvlc.AppendColumn(col, varianttype="bool")

    # -----------------------------------------------------------------------

    @staticmethod
    def __append_format_columns(dvlc):
        """Append the columns to indicate the format."""
        w = sppasPanel.fix_size(60)
        dvlc.AppendTextColumn(ui_translation.gettext('Extension'),
                              width=int(1.3*w)),
        dvlc.AppendTextColumn(ui_translation.gettext('Software'),
                              width=int(1.7*w),
                              align=wx.ALIGN_CENTER)
        dvlc.AppendTextColumn(ui_translation.gettext('Reader'),
                              width=w, align=wx.ALIGN_CENTER)
        dvlc.AppendTextColumn(ui_translation.gettext('Writer'),
                              width=w, align=wx.ALIGN_CENTER)

    # -----------------------------------------------------------------------

    @staticmethod
    def __append_property_columns(dvlc):
        """Append the columns to indicate the properties of a format."""
        w = sppasPanel.fix_size(60)
        for c in sppasFormatInfos.cols:
            dvlc.AppendTextColumn(
                sppasFormatInfos.cols[c],
                width=w, align=wx.ALIGN_CENTER)

    # -----------------------------------------------------------------------

    def __fill_rows(self, dvlc):
        """"""
        # Each item (row) is added as a sequence of values
        # whose order matches the columns.
        for extension in self.__extensions:
            items = [""]*(5+len(sppasFormatInfos.cols))
            items[1] = " ." + extension
            instance = sppasRW.TRANSCRIPTION_TYPES[extension]()
            items[2] = instance.software
            try:
                instance.read("")
            except NotImplementedError:
                items[3] = ""
            except Exception:
                items[3] = "X"
            try:
                instance.write("")
            except NotImplementedError:
                items[4] = ""
            except Exception:
                items[4] = "X"

            for i, method in enumerate(sppasFormatInfos.cols):
                support = getattr(instance, method)()
                if support is True:
                    items[i+5] = "X"

            dvlc.AppendItem(items)

    # -----------------------------------------------------------------------

    def __set_selected(self, event):
        dvlc = self.FindWindow("dvlc")
        selected = dvlc.GetSelectedRow()
        if selected == self.__selected:
            return

        # We already had a selected row
        if self.__selected != -1:
            dvlc.SetValue(False, self.__selected, 0)

        # Set the new selected row
        self.__selected = selected
        dvlc.SetValue(True, self.__selected, 0)

        # Unselect the row in the dataview to remove the "highlighted" color
        dvlc.UnselectRow(selected)

        # the parent will decide what to exactly do with this change
        evt = FormatChangedEvent(extension=self.__extensions[self.__selected])
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

