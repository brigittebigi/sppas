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

from ..windows import sppasScrolledPanel
from ..windows import sppasStaticText

# ----------------------------------------------------------------------------


class BaseViewFilesPanel(sppasScrolledPanel):
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
        self._files = dict()
        self._hicolor = self.GetForegroundColour()

        self._create_content(files)
        self.Layout()

    # -----------------------------------------------------------------------
    # Colours
    # -----------------------------------------------------------------------

    def GetHighLightColor(self):
        """Get the color to highlight buttons."""
        return self._hicolor

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self._hicolor = color

    # -----------------------------------------------------------------------
    # Manage the files
    # -----------------------------------------------------------------------

    def is_modified(self, name=None):
        """Return True if the content of the or all files has been changed.

        :param name: (str) Name of a file

        """
        logging.debug("Page is modified ?????????????????????????????")
        if name is not None:
            logging.debug("  name = {:s}".format(name))
            page = self._files.get(name, None)
            try:
                changed = page.is_modified()
            except Exception as e:
                logging.debug(" ... error: {:s}".format(str(e)))
                changed = False

            return changed

        # All files
        for name in self._files:
            logging.debug("  - name = {:s}".format(name))
            page = self._files.get(name, None)
            try:
                if page.is_modified() is True:
                    return True
                else:
                    logging.debug("  not modified")

            except Exception as e:
                logging.debug(" ... error: {:s}".format(str(e)))
                pass

        return False

    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self._files.keys())

    # -----------------------------------------------------------------------

    def append_file(self, name):
        """Add a file and display its content.

        :param name: (str)
        :raise: ValueError

        """
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            raise ValueError('Name {:s} is already in the list of files.')

        self._files[name] = self._show_file(name)

    # -----------------------------------------------------------------------

    def remove_file(self, name, force=True):
        """Remove a panel corresponding to the name of a file.

        Do not update the GUI.

        :param name: (str)
        :return: (bool) The file was removed or not

        """
        changed = self.is_modified(name)
        if changed is True or force is True:
            # Remove of the object
            self._del_file(name)
            # Delete of the list
            self._files.pop(name)
            return True

        return False

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self, files):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        for f in files:
            self.append_file(f)
        self.SetMinSize(wx.Size(sppasScrolledPanel.fix_size(420),
                                sppasScrolledPanel.fix_size(48)*len(self._files)))

    # -----------------------------------------------------------------------

    def _show_file(self, name):
        """Display the file."""
        wx.LogWarning("Displaying file is not implemented in this view mode.")
        panel = sppasStaticText(self, label=name)
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        line_height = float(font.GetPixelSize()[1])
        panel.SetMinSize(wx.Size(-1, line_height * 2))
        self.GetSizer().Add(panel, 0, wx.EXPAND)
        return panel

    # -----------------------------------------------------------------------

    def _del_file(self, name):
        """Remove the file."""
        page = self._files.get(name, None)
        if page is None:
            wx.LogError("There's no file with name {:s}".format(name))

        # Get and delete the panel
        page.Destroy()

        # Remove of the sizer
        self.GetSizer().Remove(page)
