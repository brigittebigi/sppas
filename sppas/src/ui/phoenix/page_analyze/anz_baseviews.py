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

    ui.phoenix.page_analyze.anz_views.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx

from ..windows import sppasPanel
from ..windows import sppasStaticText

# ----------------------------------------------------------------------------


class BaseViewFilesPanel(sppasPanel):
    """Panel to display the list of opened files and their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="viewfiles", files=tuple()):
        super(BaseViewFilesPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The files of this panel (key=name, value=wx.SizerItem)
        self._files = list()
        self._hicolor = self.GetForegroundColour()

        self._create_content(files)
        self.Layout()

    # -----------------------------------------------------------------------

    def GetHighLightColor(self):
        """Get the color to highlight buttons."""
        return self._hicolor

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self._hicolor = color

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return self._files

    # -----------------------------------------------------------------------

    def append_file(self, name):
        """Add a file and display its content.

        :param name: (str)

        """
        logging.debug('Append file {:s}'.format(name))
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            raise ValueError('Name {:s} is already in the list of files.')

        self._files.append(name)
        logging.debug("current list of files: {!s:s}".format(str(self._files)))
        self._show_file(name)

        # Update the gui
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def remove_file(self, name):
        """Remove a panel corresponding to the name of a file.

        :param name: (str)

        """
        # Remove of the object
        self._del_file(name)
        # Delete of the list
        self._files.pop(name)

        # Update the gui
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self, files):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        for f in files:
            self.append_file(f)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(420),
                                sppasPanel.fix_size(48)*len(self._files)))

    # -----------------------------------------------------------------------

    def _show_file(self, name):
        """Display the file."""
        logging.warning("Displaying file is not implemented in this view mode.")
        panel = sppasStaticText(self, label=name)
        self.GetSizer().Add(panel, 1, wx.EXPAND)

    # -----------------------------------------------------------------------

    def _del_file(self, name):
        """Remove the file."""
        # Get the index of the file in the list
        idx = self._files.index(name)
        item = self.GetSizer().GetItem(idx)
        # Get and delete the panel
        item.DeleteWindows()

        # Remove of the sizer
        self.GetSizer().Remove(item)
