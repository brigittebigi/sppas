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

import os
import wx

from sppas import msg
from sppas.src.exc import sppasTypeError
from sppas.src.utils import u
from sppas.src.files import FileData, States
from sppas.src.anndata import sppasRW

from ..main_events import DataChangedEvent, EVT_DATA_CHANGED
from ..dialogs import Warn
from ..windows import sppasStaticText
from ..windows import sppasScrolledPanel
from ..windows import BitmapTextButton, CheckButton
from .finfos import FormatsViewCtrl, EVT_FORMAT_CHANGED

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_CONVERT_SELECT = _("Select the file type to convert into: ")
MSG_OPT_OVERRIDE = _("Override if the output file already exists.")
MSG_OPT_HEURISTIC = _("If the extension of the input file is unknown, "
                      "try to automatically detect the format.")
MSG_PERFORM = _("Perform the conversion")
MSG_NO_FILE = _("No file(s) selected to be converted.")

MSG_PROCESS_TODO = _("To do")
MSG_PROCESS_IGNORED = _("File is already existing. Ignored.")
MSG_PROCESS_READING = _("Reading...")
MSG_PROCESS_WRITING = _("Writing...")
MSG_PROCESS_DONE = _("Done")

# ---------------------------------------------------------------------------


class sppasConvertPanel(sppasScrolledPanel):
    """Create a panel to convert the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasConvertPanel, self).__init__(
            parent=parent,
            name="page_convert",
            style=wx.BORDER_NONE
        )

        # The data we are working on
        self.__data = FileData()

        # Construct the GUI
        self._create_content()
        self._setup_events()

        # Look&feel
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # Organize items and fix a size for each of them
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.Layout()

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
        txt_select = sppasStaticText(self, label=MSG_CONVERT_SELECT)
        dvlc_formats = FormatsViewCtrl(self, name="dvlc_formats")

        # The button to perform conversion
        self.btn_run = self.__create_convert_btn(MSG_PERFORM)
        self.__set_run_disabled()

        # The list of converted files
        dvlc = self.__create_viewctrl_converted()

        # Options to convert files
        opt_force = CheckButton(self, label=MSG_OPT_OVERRIDE, name="override")
        opt_force.SetValue(False)
        opt_heuristic = CheckButton(self, label=MSG_OPT_HEURISTIC, name="heuristic")
        opt_heuristic.SetValue(False)

        # Organize all objects into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txt_select, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(dvlc_formats, 1, wx.EXPAND | wx.ALL, 4)
        sizer.Add(opt_force, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(opt_heuristic, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(self.btn_run, 0, wx.ALIGN_CENTRE | wx.ALL, 4)
        sizer.Add(dvlc, 1, wx.EXPAND | wx.ALL, 4)

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_viewctrl_converted(self):
        """Create a dataview.listctrl to display converted files."""
        style = wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.LC_HRULES
        dvlc = wx.ListCtrl(self, style=style, name="dvlc_files")

        dvlc.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__cancel_selected)
        dvlc.AppendColumn("filename",
                          format=wx.LIST_FORMAT_LEFT,
                          width=sppasScrolledPanel.fix_size(340))
        dvlc.AppendColumn("convert",
                          format=wx.LIST_FORMAT_LEFT,
                          width=sppasScrolledPanel.fix_size(200))
        return dvlc

    # ------------------------------------------------------------------------

    def __cancel_selected(self, event):
        """"""
        dvlc = self.FindWindow("dvlc_files")
        dvlc.UnselectRow(dvlc.GetSelectedRow())

    # ------------------------------------------------------------------------

    def __create_convert_btn(self, label):
        """"""
        w = sppasScrolledPanel.fix_size(196)
        h = sppasScrolledPanel.fix_size(42)

        btn = BitmapTextButton(self, label=label)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = sppasScrolledPanel.fix_size(8)
        btn.BorderWidth = 2
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(w, h))

        btn.SetName("convert")
        btn.SetImage("convert")

        return btn

    # -----------------------------------------------------------------------

    def __set_run_enabled(self):
        """Enable the run button."""
        self.btn_run.Enable(True)
        self.btn_run.BorderColour = wx.Colour(24, 228, 24, 128)

    def __set_run_disabled(self):
        """Disable the run button."""
        self.btn_run.Enable(False)
        self.btn_run.BorderColour = wx.Colour(228, 24, 24, 128)

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

        # The selected format has changed.
        # This event is sent by the 'sppasFormatInfos' child window.
        self.Bind(EVT_FORMAT_CHANGED, self._process_format_changed)

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

    def _process_format_changed(self, event):
        """Process a change of file format to convert to.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            ext = event.extension
        except AttributeError:
            wx.LogError('Extension were not sent in the event emitted by {:s}'
                        '.'.format(emitted.GetName()))
            return
        # we did not had already a format, but now we have one so we can
        # enable conversion.
        self.__set_run_enabled()

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
        dvlc = self.FindWindow("dvlc_files")
        dvlc_formats = self.FindWindow("dvlc_formats")
        out_ext = dvlc_formats.GetExtension()
        if out_ext is None:
            # this should never occur because the run button is disabled
            # if no extension is selected.
            wx.LogError("A file format must be selected before convert.")
            return
        # Remove all rows currently displayed
        dvlc.DeleteAllItems()
        # Disable run button
        self.__set_run_disabled()
        # Cancel the currently selected file format
        dvlc_formats.CancelSelected()

        # Add each file into the 1st column of the list
        checked_fns = self.get_checked_filenames()
        if len(checked_fns) == 0:
            Warn(MSG_NO_FILE)
            return
        for f in checked_fns:
            dvlc.Append([f, MSG_PROCESS_TODO])

        try:
            nb_rows = 2 + len(checked_fns)
            font = wx.GetApp().settings.text_font
            font_height = font.GetPointSize()
            h = font_height * 2 * nb_rows
            dvlc.SetMinSize(wx.Size(-1, h))
            dvlc.SetSize(wx.Size(-1, h))
        except:
            dvlc.SetMinSize(wx.Size(-1, 200))
            dvlc.SetSize(wx.Size(-1, 200))

        self.Layout()
        self.Refresh()
        dvlc.Refresh()

        # Get options
        override = self.FindWindow("override").GetValue()
        heuristic = self.FindWindow("heuristic").GetValue()

        # Convert each file.
        changed = False
        for i, f in enumerate(checked_fns):

            # Fix output filename
            fname, fext = os.path.splitext(f)
            out_fname = fname + out_ext
            dvlc.SetItem(i, 1, "")
            dvlc.RefreshItem(i)

            # Do not override an existing file
            if override is False and os.path.exists(out_fname) is True:
                dvlc.SetItem(i, 0, out_fname)
                dvlc.SetItem(i, 1, MSG_PROCESS_IGNORED)
                dvlc.RefreshItem(i)
                continue

            # Read input file
            try:
                dvlc.SetItem(i, 1, MSG_PROCESS_READING)
                parser = sppasRW(f)
                trs = parser.read(heuristic=heuristic)
            except Exception as e:
                dvlc.SetItem(i, 1, str(e))
                continue

            # Write output file
            try:
                dvlc.SetItem(i, 0, out_fname)
                dvlc.SetItem(i, 1, MSG_PROCESS_WRITING)
                dvlc.RefreshItem(i)

                parser = sppasRW(out_fname)
                parser.write(trs)
                dvlc.SetItem(i, 1, MSG_PROCESS_DONE)
                self.__data.add_file(out_fname, brothers=False)
                changed = True

            except Exception as e:
                dvlc.SetItem(i, 1, str(e))

        # Notify the parent that the workspace changed.
        if changed is True:
            self.notify()

    # -----------------------------------------------------------------------

    def get_checked_filenames(self):
        """Return the list of checked filenames in data."""
        # Get the list of checked FileName() instances
        checked = self.__data.get_filename_from_state(States().CHECKED)
        if len(checked) == 0:
            return list()

        # Convert the list of FileName() instances into a list of filenames
        return [f.get_id() for f in checked]
