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

    ui.phoenix.page_files.files.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    One of the main pages of the wx4-based GUI of SPPAS.

    It manages the workspaces:

        - the list of files,
        - the list of references, and
        - the actions to perform on both of them.

"""

import wx
import logging

from ..windows import sppasPanel
from ..windows import sppasStaticLine

from .wksmanager import WorkspacesManager
from .filesmanager import FilesManager
from .refsmanager import ReferencesManager
from .associate import AssociatePanel

from .filesevent import EVT_DATA_CHANGED

# ---------------------------------------------------------------------------


class sppasFilesPanel(sppasPanel):
    """Main panel to browse and select workspaces and their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    This panel is managing 4 areas:

        1. the workspaces;
        2. the tree-view of files;
        3. an association toolbar to link files and references;
        4. the references.

    """

    def __init__(self, parent):
        super(sppasFilesPanel, self).__init__(
            parent=parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
            name="page_files"
        )
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed.

        :return: (FileData) data of the files-viewer model.

        """
        fm = self.FindWindow("filesview")
        return fm.get_data()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # Create all the panels
        wp = WorkspacesManager(self, name='workspaces')
        fm = FilesManager(self, name="filesview")
        ap = AssociatePanel(self, name="associate")
        cm = ReferencesManager(self, name="references")

        # Organize all the panels vertically, separated by 2px grey lines.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wp, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(fm, 2, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(ap, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(cm, 1, wx.EXPAND, 0)

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_vline(self):
        """Create a vertical line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(2, -1))
        line.SetSize(wx.Size(2, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(2)
        line.SetForegroundColour(wx.Colour(128, 128, 128, 128))
        return line

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # The data have changed.
        # This event is sent by any of the children
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        logging.debug('Files book page received a key event. key_code={:d}'.format(key_code))

        if key_code == wx.WXK_F5 and cmd_down is False and shift_down is False:
            logging.debug(' ... [F5] key pressed')

        # CMD+S: Pin&Save the workspace
        elif key_code == 83 and cmd_down is True:
            logging.debug('Key event: Pin&Save the workspace')
            self.FindWindow("workspaces").pin_save()

        else:
            logging.debug('Key event skipped by the files book page.')
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
            logging.error('Data were not sent in the event.')
            return

        wp = self.FindWindow("workspaces")
        if emitted != wp:
            wp.set_data(data)

        fm = self.FindWindow("filesview")
        if emitted != fm:
            fm.set_data(data)

        ap = self.FindWindow("associate")
        if emitted != ap:
            ap.set_data(data)

        cm = self.FindWindow("references")
        if emitted != cm:
            cm.set_data(data)