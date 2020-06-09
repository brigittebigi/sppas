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

    src.ui.phoenix.page_files.filesmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main panel to manage the tree of files.

"""

import os
import wx

from sppas.src.config import paths

from sppas.src.config import msg
from sppas.src.wkps.workspace import States

from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import sppasStaticLine
from ..windows import YesNoQuestion, Information
from ..windows import sppasFileDialog
from ..main_events import DataChangedEvent, EVT_DATA_CHANGED

from .filesviewctrl import FileTreeView

# ---------------------------------------------------------------------------
# List of displayed messages:

FLS_TITLE = msg("Files: ", "ui")
FLS_ACT_ADD = msg("Add", "ui")
FLS_ACT_REM = msg("Remove checked", "ui")
FLS_ACT_DEL = msg("Delete checked", "ui")
FLS_ACT_MISS = msg("Edit missing", "ui")

FLS_MSG_CONFIRM_DEL = msg("Are you sure you want to delete {:d} files?")

# ----------------------------------------------------------------------------


class FilesManager(sppasPanel):
    """Manage the tree of files and actions to perform on them.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    HIGHLIGHT_COLOUR = wx.Colour(228, 128, 128, 196)

    def __init__(self, parent, name=wx.PanelNameStr):
        super(FilesManager, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN,
            name=name)

        self.__current_dir = paths.samples
        self._create_content()
        self._setup_events()

        self.SetMinSize(wx.Size(sppasPanel.fix_size(320), -1))
        self.SetAutoLayout(True)
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to access the data
    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data like they are currently stored into the model."""
        return self._filestree.get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign a new data instance to display to this panel.

        :param data: (sppasWorkspace)

        """
        self._filestree.set_data(data)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        tb = self.__create_toolbar()
        fv = FileTreeView(self, name="filestree")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(self.__create_hline(), 0, wx.EXPAND, 0)
        sizer.Add(fv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    @property
    def _filestree(self):
        return self.FindWindow("filestree")

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        """Create the toolbar."""
        tb = sppasToolbar(self)
        tb.set_focus_color(FilesManager.HIGHLIGHT_COLOUR)
        tb.AddTitleText(FLS_TITLE, FilesManager.HIGHLIGHT_COLOUR)
        tb.AddButton("files-add", FLS_ACT_ADD)
        tb.AddButton("files-remove", FLS_ACT_REM)
        tb.AddButton("files-delete", FLS_ACT_DEL)
        btn = tb.AddButton("files-missing", FLS_ACT_MISS)
        btn.Enable(False)
        return tb

    # -----------------------------------------------------------------------

    def __create_hline(self):
        """Create an horizontal line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        return line

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # The user pressed a key of its keyboard
        self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)

        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # Changes occurred in the child files tree
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

    # ------------------------------------------------------------------------

    def notify(self):
        """Send the EVT_DATA_CHANGED to the parent."""
        if self.GetParent() is not None:
            data = self._filestree.get_data()
            evt = DataChangedEvent(data=data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _process_data_changed(self, event):
        sender = event.GetEventObject()
        if sender is self._filestree:
            self.notify()

    # ------------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        wx.LogDebug("Files manager. Key pressed: {:d}".format(key_code))

        # Ctrl+a
        if key_code == 65 and cmd_down is True:
            self._add()
        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action of a button.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()

        if name == "files-add":
            self._add()

        elif name == "files-remove":
            self._remove()

        elif name == "files-delete":
            self._delete()

        elif name == "files-missing":
            self._edit_missing()

        event.Skip()

    # ------------------------------------------------------------------------
    # GUI methods to perform actions on the data
    # ------------------------------------------------------------------------

    def _add(self):
        """Add user-selected files into the files viewer."""
        filenames = list()
        dlg = sppasFileDialog(self)
        if os.path.exists(self.__current_dir):
            dlg.SetDirectory(self.__current_dir)
        if dlg.ShowModal() == wx.ID_OK:
            filenames = dlg.GetPaths()
        dlg.Destroy()

        if len(filenames) > 0:
            added = self._filestree.AddFiles(filenames)
            if added > 0:
                self.__current_dir = os.path.dirname(filenames[0])
                self.notify()

    # ------------------------------------------------------------------------

    def _remove(self):
        """Remove the checked files of the fileviewer."""
        data = self.get_data()
        if data.is_empty():
            wx.LogMessage('No files in data. Nothing to remove.')
            return

        removed = self._filestree.RemoveCheckedFiles()
        if removed:
            self.notify()

    # ------------------------------------------------------------------------

    def _delete(self):
        """Move into the trash the checked files of the fileviewer."""
        data = self.get_data()
        if data.is_empty():
            wx.LogMessage('No files in data. Nothing to delete.')
            return

        checked_files = self._filestree.GetCheckedFiles()
        if len(checked_files) == 0:
            Information('None of the files are selected to be deleted.')
            return

        # User must confirm to really delete files
        message = FLS_MSG_CONFIRM_DEL.format(len(checked_files))
        response = YesNoQuestion(message)
        if response == wx.ID_YES:
            deleted = self._filestree.DeleteCheckedFiles()
            if deleted:
                self.notify()
        elif response == wx.ID_NO:
            wx.LogMessage('Response is no. No file deleted.')

    # ------------------------------------------------------------------------

    def _edit_missing(self):
        """Open a dialog to take decisions about missing files of the data."""
        Information("In a future version, you'll be able to remove or rename "
                    "unknown paths and filenames of the list.")

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(FilesManager):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.SetBackgroundColour(wx.Colour(50, 50, 50))
        self.SetForegroundColour(wx.Colour(250, 250, 250))
        self.add_one_test_data()

    # ------------------------------------------------------------------------

    def add_one_test_data(self):
        self._filestree.AddFiles([os.path.abspath(__file__)])

    # ------------------------------------------------------------------------

    def add_test_data(self):
        here = os.path.abspath(os.path.dirname(__file__))
        self._filestree.AddFiles([os.path.abspath(__file__)])
        self._filestree.LockFiles([os.path.abspath(__file__)])

        for f in os.listdir(here):
            fullname = os.path.join(here, f)
            if os.path.isfile(fullname):
                wx.LogMessage('Add {:s}'.format(fullname))
                nb = self._filestree.AddFiles([fullname])
                wx.LogMessage(" --> {:d} files added.".format(nb))
