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

    ui.phoenix.page_files.files.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    One of the main pages of the wx4-based GUI of SPPAS.

    It manages:
        - the set of workspaces,
        - the list of files of a workspace,
        - the list of references of a workspace, and
        - the actions to perform on both of them.

"""

import wx

from sppas.src.files import FileData, States
from sppas import sppasTypeError

from ..windows import sppasPanel
from ..windows import sppasStaticLine
from ..main_events import DataChangedEvent, EVT_DATA_CHANGED

from .wksmanager import WorkspacesManager
from .filesmanager import FilesManager
from .refsmanager import ReferencesManager
from .associate import AssociatePanel

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

        # Construct the GUI
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # Organize items and fix a size for each of them
        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (FileData) data of the files-viewer model.

        """
        return self.FindWindow("filesview").get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to display to this page.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        wx.LogDebug('New data to set in the files page. '
                      'Id={:s}'.format(data.id))
        # Set to all children.
        self.__send_data(self.GetParent(), data)

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
        sizer.Add(wp, 1, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(fm, 5, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(ap, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(cm, 3, wx.EXPAND, 0)

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_vline(self):
        """Create a vertical line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(2, -1))
        line.SetSize(wx.Size(2, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(2)
        # line.SetForegroundColour(wx.Colour(128, 128, 128, 128))
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
        # This event is sent by any of the children or by the parent
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        wx.LogDebug('Files book page received a key event. '
                      'key_code={:d}'.format(key_code))

        if key_code == wx.WXK_F5 and cmd_down is False and shift_down is False:
            wx.LogDebug(' ... [F5] key pressed')

        # CMD+S: Pin&Save the workspace
        elif key_code == 83 and cmd_down is True:
            wx.LogDebug('Key event: Pin&Save the workspace')
            self.FindWindow("workspaces").pin_save()

        else:
            wx.LogDebug('Key event skipped by the files book page.')
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

        self.__send_data(emitted, data)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __send_data(self, emitted, data):
        """Set a change of data to the children, send to the parent.

        :param emitted: (wx.Window) The panel the data are coming from
        :param data: (FileData)

        """
        # Set the data to appropriate children panels
        for panel in self.GetChildren():
            if panel.GetName() in ("workspaces", "filesview", "associate", "references"):
                if emitted != panel:
                    panel.set_data(data)

        # Send the data to the parent
        pm = self.GetParent()
        if pm is not None and emitted != pm:
            data.set_state(States().CHECKED)
            evt = DataChangedEvent(data=data)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)
