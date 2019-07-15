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

from .baseview import BaseViewPanel

# ----------------------------------------------------------------------------


class ViewFilesPanel(sppasPanel):
    """Panel to display the list of opened files and their content.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="viewfiles", files=tuple()):
        super(ViewFilesPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The files of this panel (key=name, value=wx.SizerItem)
        self.__files = dict()
        self.__hicolor = self.GetForegroundColour()

        self._create_content(files)
        self.Layout()

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self.__hicolor = color

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def append(self, name):
        """Add a panel corresponding to the name of a file.

        :param name: (str)
        :returns: index of the newly created button

        """
        logging.debug('APPEND FILE {:s}'.format(name))
        if name in self.__files:
            raise ValueError('Name {:s} is already in the list of files.')

        panel = BaseViewPanel(self, filename=name)
        panel.SetHighLightColor(self.__hicolor)
        item = self.GetSizer().Add(panel, 1, wx.EXPAND)
        self.__files[name] = item
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def remove(self, name):
        """Remove a panel corresponding to the name of a file.

        :param name: (str)

        """
        # Get and delete the panel
        item = self.__files[name]
        item.DeleteWindows()

        # Remove of the sizer
        self.GetSizer().Remove(item)
        self.Layout()
        self.Refresh()

        # Delete of the list
        self.__files.pop(name)

    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self.__files.keys())

    # -----------------------------------------------------------------------

    def get_checked_files(self):
        """Return the list of the checked filenames."""
        checked = list()
        for name in self.__files:
            item = self.__files[name]
            window = item.GetWindow()
            if window.is_checked() is True:
                checked.append(name)
        return checked

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self, files):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        for f in files:
            self.append(f)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(128),
                                sppasPanel.fix_size(32)*len(self.__files)))
