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

    ui.phoenix.page_convert.convert.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.dataview

from sppas import sppasTypeError
from sppas.src.files import FileData, States

from ..main_events import DataChangedEvent, EVT_DATA_CHANGED
from ..dialogs import Error, Information
from ..windows import sppasScrolledPanel
from ..windows import BitmapTextButton, CheckButton
from .finfos import sppasFormatInfos

# ---------------------------------------------------------------------------


class sppasConvertPanel(sppasScrolledPanel):
    """Create a panel to analyze the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasConvertPanel, self).__init__(
            parent=parent,
            name="page_convert",
            style=wx.BORDER_NONE
        )

        # The data all tabs are working on
        self.__data = FileData()

        # Construct the GUI
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # Organize items and fix a size for each of them
        self.Layout()
        self.SetupScrolling(scroll_x=True, scroll_y=True)

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (FileData) data of the files-viewer model.

        """
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        self.__data = data

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # The list of file formats, to select one of them
        pinfo = sppasFormatInfos(self)

        # The button to perform conversion
        self.btn_run = self.__create_convert_btn("Perform the conversion")
        self.btn_run.SetName("convert")
        self.btn_run.SetImage("convert")
        self.btn_run.Enable(False)
        self.btn_run.BorderColour = wx.Colour(228, 24, 24, 128)

        # The list of converted files
        self.dvlc = wx.dataview.DataViewListCtrl(
            self,
            style=wx.dataview.DV_SINGLE | wx.dataview.DV_NO_HEADER | wx.dataview.DV_HORIZ_RULES | wx.NO_BORDER)
        self.dvlc.SetName("dvlc_files")
        self.dvlc.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self.__cancel_selected)
        self.dvlc.AppendTextColumn("filename", width=sppasScrolledPanel.fix_size(300))
        self.dvlc.AppendTextColumn("convert", width=sppasScrolledPanel.fix_size(300))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(pinfo, 2, wx.EXPAND, 0)
        sizer.Add(self.btn_run, 0, wx.ALIGN_CENTRE, 4)
        sizer.Add(self.dvlc, 1, wx.EXPAND, 0)

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __cancel_selected(self):
        """"""
        self.dvlc.UnselectRow(self.dvlc.GetSelectedRow())

    # ------------------------------------------------------------------------

    def __create_convert_btn(self, label):
        """"""
        w = sppasScrolledPanel.fix_size(196)
        h = sppasScrolledPanel.fix_size(42)

        btn = BitmapTextButton(self, label=label)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = 12
        btn.BorderWidth = 2
        btn.BorderColour = wx.Colour(128, 128, 128, 128)
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(w, h))
        return btn

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """The parent has to be informed of a change of content."""
        evt = DataChangedEvent(data=self.__data)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # The data have changed.
        # This event is sent by the tabs manager or by the parent
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

        # There's only one button in this page
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other panels.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            data = event.data
        except AttributeError:
            wx.LogError('Data were not sent in the event emitted by {:s}'
                        '.'.format(emitted.GetName()))
            return
        self.__data = data

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "convert":
            self._process_convert()

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_convert(self):
        """Convert checked files."""
        # Remove all rows currently displayed
        self.dvlc.DeleteAllItems()

        # Get the list of checked FileName() instances
        checked = self.__data.get_filename_from_state(States().CHECKED)
        if len(checked) == 0:
            Information("No file(s) selected to be converted.")
            return

        # Convert the list of FileName() instances into a list of filenames
        checked_fns = [f.get_id() for f in checked]

        # Add each file into the 1st column of the list
        for f in checked_fns:
            self.dvlc.AppendItem([f, "to do"])

        # Get the file extension we want to convert to
        ext = self.FindWindow("page_format_infos").get_extension()
        wx.LogDebug("Convert files into {:s}".format(ext))
