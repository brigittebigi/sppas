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

    src.ui.phoenix.dialogs.file.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
from ..windows import sppasDialog

# ----------------------------------------------------------------------------


class sppasFileDialog(sppasDialog):
    """Dialog class to select files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent,
                 title="Files and directories selection",
                 style=wx.FC_OPEN | wx.FC_MULTIPLE | wx.FC_NOSHOWHIDDEN):
        """Create a dialog with a file chooser.

        :param parent: (wx.Window)
        :param style: (int)

        This class supports the following styles:

            - wx.FC_DEFAULT_STYLE: The default style: wx.FC_OPEN
            - wx.FC_OPEN: Creates a file control suitable for opening files. Cannot be combined with wx.FC_SAVE.
            - wx.FC_SAVE: Creates a file control suitable for saving files. Cannot be combined with wx.FC_OPEN.
            - wx.FC_MULTIPLE: For open control only, Allows selecting multiple files. Cannot be combined with wx.FC_SAVE
            - wx.FC_NOSHOWHIDDEN: Hides the "Show Hidden Files" checkbox (Generic only)

        """
        super(sppasFileDialog, self).__init__(
            parent=parent,
            title=title,
            style=wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.STAY_ON_TOP)

        self._create_content(style)
        self._create_buttons()

        # Fix frame properties
        self.SetMinSize(wx.Size(sppasDialog.fix_size(320),
                                sppasDialog.fix_size(200)))
        self.LayoutComponents()
        self.CenterOnParent()
        self.GetSizer().Fit(self)
        self.FadeIn(deltaN=-10)

    # -----------------------------------------------------------------------
    # Public methods to manage filenames
    # -----------------------------------------------------------------------

    def GetFilename(self):
        """Return the currently selected filename."""
        return self.FindWindow("content").GetFilename()

    # -----------------------------------------------------------------------

    def GetFilenames(self):
        """Return a list of filenames selected in the control."""
        return self.FindWindow("content").GetFilenames()

    # -----------------------------------------------------------------------

    def GetPaths(self):
        """Return a list of the full paths (directory and filename) of the files."""
        return self.FindWindow("content").GetPaths()

    # -----------------------------------------------------------------------

    def GetPath(self):
        """Return the full path (directory and filename) of the currently selected file."""
        return self.FindWindow("content").GetPath()

    # -----------------------------------------------------------------------

    def GetFilterIndex(self):
        """Return the zero-based index of the currently selected filter."""
        return self.FindWindow("content").GetFilterIndex()

    # -----------------------------------------------------------------------

    def GetWildcard(self):
        """Return the current wildcard."""
        return self.FindWindow("content").GetWildcard()

    # -----------------------------------------------------------------------

    def SetWildcard(self, wild_card):
        return self.FindWindow("content").SetWildcard(wild_card)

    # -----------------------------------------------------------------------

    def SetPath(self, path):
        return self.FindWindow("content").SetPath(path)

    # -----------------------------------------------------------------------

    def SetDirectory(self, directory):
        """Set (change) the current directory displayed in the control."""
        return self.FindWindow("content").SetDirectory(directory)

    # -----------------------------------------------------------------------

    def ShowHidden(self, show):
        """Set whether hidden files and folders are shown or not."""
        return self.FindWindow("content").ShowHidden(show)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self, style):
        """Create the content of the file dialog."""
        fc = wx.FileCtrl(self, style=style)
        fc.SetMinSize(wx.Size(sppasDialog.fix_size(480),
                              sppasDialog.fix_size(320)))
        fc.SetBackgroundColour(self.GetBackgroundColour())
        fc.SetForegroundColour(self.GetForegroundColour())
        fc.SetFont(self.GetFont())
        fc.SetName("content")
        for c in fc.GetChildren():
            c.SetBackgroundColour(self.GetBackgroundColour())
            c.SetForegroundColour(self.GetForegroundColour())
            c.SetFont(self.GetFont())

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_CANCEL:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()
        else:
            event.Skip()
