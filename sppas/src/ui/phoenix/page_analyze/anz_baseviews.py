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

    ui.phoenix.page_analyze.anz_baseviews.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from ..windows import sppasScrolledPanel
from ..windows import sppasToolbar
from ..main_events import ViewEvent

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
            style=wx.BORDER_NONE | wx.VSCROLL | wx.HSCROLL | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The files of this panel (key=name, value=wx.SizerItem)
        self._files = dict()
        self._hicolor = self.GetForegroundColour()

        self._create_content(files)
        self._setup_events()

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
        """Return True if the content of the file has been changed.

        :param name: (str) Name of a file. None for all files.

        """
        if name is not None:
            page = self._files.get(name, None)
            try:
                changed = page.is_modified()
                return changed
            except:
                return False

        # All files
        for name in self._files:
            page = self._files.get(name, None)
            try:
                if page.is_modified() is True:
                    return True
            except:
                pass

        return False

    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self._files.keys())

    # -----------------------------------------------------------------------

    def append_file(self, name):
        """Add a file and display its content.

        Do not refresh/layout the GUI.

        :param name: (str)
        :raise: ValueError

        """
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            raise ValueError('Name {:s} is already in the list of files.')

        self._files[name] = self._show_file(name)

    # -----------------------------------------------------------------------

    def remove_file(self, name, force=False):
        """Remove a panel corresponding to the name of a file.

        Do not refresh/layout the GUI.

        :param name: (str)
        :param force: (bool) Force to remove, even if a file is modified
        :return: (bool) The file was removed or not

        """
        if force is True or self.is_modified(name) is False:

            # Remove of the object
            page = self._files.get(name, None)
            if page is None:
                wx.LogError("There's no file with name {:s}".format(name))
                return False

            # Destroy the panel and remove of the sizer
            for i, child in enumerate(self.GetChildren()):
                if child == page:
                    self.GetSizer().Remove(i)
                    break
                for c in child.GetChildren():
                    if c == page:
                        self.GetSizer().Remove(i)
                        break

            page.Destroy()

            # Delete of the list
            self._files.pop(name)
            return True

        return False

    # -----------------------------------------------------------------------

    def can_edit(self):
        """Return True if this view can modify/save the file content.

        Can be overridden.

        If True, the methods 'is_modified' and 'save' should be implemented
        in the view panel of each file.

        """
        return False

    # -----------------------------------------------------------------------

    def save_file(self, name):
        """Save a file.

        :param name: (str)
        :return: (bool) The file was saved or not

        """
        panel = self._files.get(name, None)
        saved = False
        if panel.is_modified() is True:
            try:
                saved = panel.save()
                if saved is True:
                    wx.LogMessage("File {:s} saved.".format(name))
            except Exception as e:
                saved = False
                wx.LogError("Error while saving file {:s}: {:s}"
                            "".format(name, str(e)))

        return saved

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _show_file(self, name):
        """Create a panel to display a single file.

        Must be overridden.

        :return: (sppasBaseViewPanel)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _create_content(self, files):
        """Create the main content.

        :param files: (list) List of filenames

        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        for f in files:
            self.append_file(f)
        min_height = sppasScrolledPanel.fix_size(48)*len(self._files)
        self.SetMinSize(wx.Size(sppasScrolledPanel.fix_size(420), min_height))

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action, filename):
        """Notify the parent of a ViewEvent.

        :param action: (str) the action to perform
        :param filename: (str) name of the file to perform the action

        """
        evt = ViewEvent(action=action, filename=filename)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate an handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.
        To be overridden.

        """
        pass

