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

    ui.phoenix.page_editor.editor.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas.src.config import msg
from sppas.src.config import paths
from sppas.src.exceptions import sppasTypeError
from sppas.src.utils import u
from sppas.src.wkps import sppasWorkspace, States

from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasStaticLine
from ..windows.dialogs import Confirm
from ..windows.dialogs import sppasProgressDialog
from ..main_events import DataChangedEvent, EVT_DATA_CHANGED

from .timedit import TimeEditPanel

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


MSG_OPEN = _("Open files")
MSG_SAVE = _("Save all")
MSG_CLOSE = _("Close all")

CLOSE_CONFIRM = _("At least a file contains not saved work that will be "
                  "lost. Are you sure you want to close?")

# ---------------------------------------------------------------------------


class sppasEditorPanel(sppasPanel):
    """Create a panel to view&edit the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    HIGHLIGHT_COLOUR = wx.Colour(128, 128, 196, 196)

    # ------------------------------------------------------------------------

    def __init__(self, parent):
        super(sppasEditorPanel, self).__init__(
            parent=parent,
            name="page_editor",
            style=wx.BORDER_NONE
        )

        # The data we are working on
        self.__data = sppasWorkspace()

        # Construct the GUI
        self._create_content()
        self._setup_events()

        # Look&feel
        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (sppasWorkspace) data of the files-viewer model.

        """
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (sppasWorkspace)

        """
        if isinstance(data, sppasWorkspace) is False:
            raise sppasTypeError("sppasWorkspace", type(data))
        self.__data = data

    # -----------------------------------------------------------------------
    # Colours & Fonts
    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. """
        wx.Panel.SetFont(self, font)
        for c in self.GetChildren():
            if c.GetName() != "edit_toolbar":
                c.SetFont(font)
            else:
                # a smaller font for the toolbar
                f = wx.Font(int(font.GetPointSize() * 0.65),
                            wx.FONTFAMILY_SWISS,   # family,
                            wx.FONTSTYLE_NORMAL,   # style,
                            wx.FONTWEIGHT_BOLD,    # weight,
                            underline=False,
                            faceName=font.GetFaceName(),
                            encoding=wx.FONTENCODING_SYSTEM)
                c.SetFont(f)

        self.Layout()

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. """
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            if c.GetName() != "hline":
                c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def open_checked_files(self):
        """Add the checked files and display their content.

        Lock the files that are successfully opened and notify parent.

        """
        # Add checked files to the page
        checked = self.__data.get_filename_from_state(States().CHECKED)
        success = 0
        total = len(checked)
        progress = sppasProgressDialog()
        progress.set_new()
        progress.set_header(MSG_OPEN + "...")
        progress.set_fraction(0)
        wx.BeginBusyCursor()
        for i, fn in enumerate(sorted(checked)):
            try:
                fraction = float((i+1)) / float(total)
                message = os.path.basename(fn.get_id())
                progress.update(fraction, message)
                self._timepanel.append_file(fn.get_id())
                self.__data.set_object_state(States().LOCKED, fn)
                success += 1
            except Exception as e:
                wx.LogError(str(e))
        wx.EndBusyCursor()
        progress.set_fraction(1)
        progress.close()

        # send data to the parent
        if success > 0:
            self._timepanel.Layout()
            self._timepanel.Refresh()
            wx.LogMessage("{:d} files opened.".format(success))
            self.notify()

    # ------------------------------------------------------------------------

    def save_files(self):
        """Save the files on disk."""
        saved = list()
        for filename in self._timepanel.get_files():
            s = self._timepanel.save_file(filename)
            if s is True:
                saved += 1

        if len(saved) > 0:
            wx.LogMessage("{:d} files saved.".format(saved))

    # ------------------------------------------------------------------------

    def close_files(self):
        """Close the opened files.

        Unlock the closed files and notify parent.

        """
        if self._timepanel.is_modified() is True:
            wx.LogWarning("At least one file contains not saved changes.")
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(CLOSE_CONFIRM, MSG_CLOSE)
            if response == wx.ID_CANCEL:
                return

        closed = list()
        for filename in self._timepanel.get_files():
            removed = self._timepanel.remove_file(filename, force=True)
            if removed is True:
                closed.append(filename)
                fn = self.__data.get_object(filename)
                self.__data.set_object_state(States().CHECKED, fn)

        if len(closed) > 0:
            wx.LogMessage("{:d} files closed.".format(len(closed)))
            self._timepanel.Layout()
            self.Refresh()
            self.notify()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        content_panel = TimeEditPanel(self, name="timeedit_panel")
        main_sizer.Add(self._create_toolbar(), 0, wx.EXPAND, 0)
        main_sizer.Add(self._create_hline(), 0, wx.EXPAND, 0)
        main_sizer.Add(content_panel, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create the main toolbar.

        :return: (sppasToolbar)

        """
        tb = sppasToolbar(self, name="edit_toolbar")
        tb.set_focus_color(sppasEditorPanel.HIGHLIGHT_COLOUR)

        tb.AddButton("open", MSG_OPEN)
        tb.AddButton("save_all", MSG_SAVE)
        tb.AddButton("close", MSG_CLOSE)

        return tb

    # -----------------------------------------------------------------------

    def _create_hline(self):
        """Create an horizontal line, used to separate the anz_panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL, name="hline")
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        line.SetForegroundColour(self.HIGHLIGHT_COLOUR)
        return line

    # -----------------------------------------------------------------------

    @property
    def _timepanel(self):
        return self.FindWindow("timeedit_panel")

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

        # The buttons in this page
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if event.AltDown() is True:
            if key_code == 78:  # alt+o Open the checked files
                self.open_checked_files()
            elif key_code == 83:  # alt+s Save the files
                self.save_files()
            elif key_code == 87:  # alt+w Close the files
                self.close_files()

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other anz_panels.

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

        if event_name == "open":
            self.open_checked_files()

        elif event_name == "save_all":
            self.save_files()

        elif event_name == "close":
            self.close_files()

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def get_checked_filenames(self):
        """Return the list of checked filenames in data."""
        # Get the list of checked FileName() instances
        checked = self.__data.get_filename_from_state(States().CHECKED)
        if len(checked) == 0:
            return list()

        # Convert the list of FileName() instances into a list of filenames
        return [f.get_id() for f in checked]

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(sppasEditorPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        f1 = os.path.join(paths.samples, "annotation-results", "samples-fra",
                          "F_F_B003-P8-palign.xra")
        f2 = os.path.join(paths.samples, "annotation-results", "samples-fra",
                          "F_F_B003-P9-palign.xra")
        f3 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")

        data = sppasWorkspace()
        fn1 = data.add_file(f1)
        data.set_object_state(States().CHECKED, fn1[0])
        fn2 = data.add_file(f2)
        data.set_object_state(States().CHECKED, fn2[0])
        fn3 = data.add_file(f3)
        data.set_object_state(States().CHECKED, fn3[0])
        self.set_data(data)
        self.open_checked_files()

