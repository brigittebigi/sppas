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

    src.ui.phoenix.filespck.filesmanager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Main panel to manage the tree of files.

"""

import logging
import os
import wx

from sppas.src.ui.phoenix.windows.panel import sppasPanel
from ..dialogs import YesNoQuestion, Information
from .filestreectrl import FilesTreeViewCtrl
from .btntxttoolbar import BitmapTextToolbar
from .filesevent import DataChangedEvent

# ----------------------------------------------------------------------------


class FilesManager(sppasPanel):
    """Manage the tree of files and actions to perform on them.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name=wx.PanelNameStr):
        super(FilesManager, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN,
            name=name)

        self._create_content()
        self._setup_events()
        self.Layout()

    # -----------------------------------------------------------------------
    # Public methods to access the data
    # -----------------------------------------------------------------------

    def get_data(self):
        """Return the data like they are currently stored into the model."""
        fv = self.FindWindow("filestree")
        return fv.get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign a new data instance to display to this panel.

        :param data: (FileData)

        """
        fv = self.FindWindow("filestree")
        fv.set_data(data)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        tb = self.__create_toolbar()
        fv = FilesTreeViewCtrl(self, name="filestree")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(fv, proportion=1, flag=wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize((320, 200))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        """Create the toolbar."""
        tb = BitmapTextToolbar(self)
        tb.set_focus_color(wx.Colour(196, 96, 96, 128))
        tb.AddText("Files: ")
        tb.AddButton("files-add", "Add")
        tb.AddButton("files-remove", "Remove checked")
        tb.AddButton("files-delete", "Delete checked")
        return tb

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

    # ------------------------------------------------------------------------

    def notify(self):
        """Send the EVT_DATA_CHANGED to the parent."""
        if self.GetParent() is not None:
            evt = DataChangedEvent(data=self.FindWindow("filestree").get_data())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        logging.debug('Files manager received the key event {:d}'
                      ''.format(key_code))

        #if key_code == wx.WXK_F5 and cmd_down is False and shift_down is False:
        #    loggingFindWindow.debug('Refresh all the files [F5 keys pressed]')
        #    self.("filestree").update_data()
        #    self.notify()

        event.Skip()

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action of a button.

        :param event: (wx.Event)

        """
        name = event.GetButtonObj().GetName()
        logging.debug("Event received of button: {:s}".format(name))

        if name == "files-add":
            self._add()

        elif name == "files-remove":
            self._remove()

        elif name == "files-delete":
            self._delete()

        event.Skip()

    # ------------------------------------------------------------------------
    # GUI methods to perform actions on the data
    # ------------------------------------------------------------------------

    def _add(self):
        """Add user-selected files into the files viewer."""
        filenames = list()
        with wx.Dialog(self, style=wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.STAY_ON_TOP, size=(640, 480)) as dlg:
            fc = wx.FileCtrl(dlg,  # defaultDirectory="", defaultFilename="", wildCard="",
                             style=wx.FC_OPEN | wx.FC_MULTIPLE | wx.FC_NOSHOWHIDDEN)
            fc.SetSize((500, 350))
            # fc.SetBackgroundColour(self.GetBackgroundColour())
            # fc.SetForegroundColour(self.GetForegroundColour())
            fc.SetFont(self.GetFont())

            ok = wx.Button(dlg, id=wx.ID_OK, label='OK')
            dlg.SetAffirmativeId(wx.ID_OK)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(fc, 1, wx.EXPAND, 0)
            sizer.Add(ok, 0, wx.ALL | wx.EXPAND, 4)
            dlg.SetSizer(sizer)

            if dlg.ShowModal() == wx.ID_OK:
                filenames = fc.GetPaths()

        if len(filenames) > 0:
            added = self.FindWindow("filestree").AddFiles(filenames)
            if added:
                self.notify()

    # ------------------------------------------------------------------------

    def _remove(self):
        """Remove the checked files of the fileviewer."""
        data = self.get_data()
        if data.is_empty():
            logging.info('No files in data. Nothing to remove.')
            return

        removed = self.FindWindow("filestree").RemoveCheckedFiles()
        if removed:
            self.notify()

    # ------------------------------------------------------------------------

    def _delete(self):
        """Move into the trash the checked files of the fileviewer."""
        data = self.get_data()
        if data.is_empty():
            logging.info('No files in data. Nothing to delete.')
            return

        checked_files = self.FindWindow("filestree").GetCheckedFiles()
        if len(checked_files) == 0:
            Information('None of the files are selected to be deleted.')
            return

        # User must confirm to really delete files
        title = "Confirm delete of files?"
        message = "Are you sure you want to delete {:d} files?" \
                  "".format(len(checked_files))
        response = YesNoQuestion(message)
        if response == wx.ID_NO:
            return

        deleted = self.FindWindow("filestree").DeleteCheckedFiles()
        if deleted:
            self.notify()

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(FilesManager):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)
        self.add_test_data()

    # ------------------------------------------------------------------------

    def add_test_data(self):
        here = os.path.abspath(os.path.dirname(__file__))
        self.FindWindow("filestree").AddFiles([os.path.abspath(__file__)])
        self.FindWindow("filestree").LockFiles([os.path.abspath(__file__)])

        for f in os.listdir(here):
            fullname = os.path.join(here, f)
            logging.info('add {:s}'.format(fullname))
            if os.path.isfile(fullname):
                self.FindWindow("filestree").AddFiles([fullname])