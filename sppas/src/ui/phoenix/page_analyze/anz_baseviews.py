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

from sppas import msg
from sppas.src.utils import u

from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..main_events import ViewEvent, EVT_VIEW
from ..dialogs import Confirm
from .errview import ErrorViewPanel

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


CLOSE = _("Close")
CLOSE_CONFIRM = _("The file contains not saved work that will be lost."
                  "Are you sure you want to close?")

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
            style=wx.BORDER_NONE | wx.VSCROLL | wx.HSCROLL | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The files of this panel (key=name, value=wx.SizerItem)
        self._files = dict()
        self._hicolor = wx.Colour(200, 200, 180)

        self._create_content(files)
        self._setup_events()

        # Look&feel
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        for f in files:
            self.append_file(f)

        self.Layout()

    # -----------------------------------------------------------------------
    # Colours & Fonts
    # -----------------------------------------------------------------------

    def SetFont(self, font):
        sppasPanel.SetFont(self, font)
        f = wx.Font(int(font.GetPointSize() * 0.65),
                    wx.FONTFAMILY_SWISS,   # family,
                    wx.FONTSTYLE_NORMAL,   # style,
                    wx.FONTWEIGHT_BOLD,    # weight,
                    underline=False,
                    faceName=font.GetFaceName(),
                    encoding=wx.FONTENCODING_SYSTEM)
        self.FindWindow("toolbar_views").SetFont(f)

    # -----------------------------------------------------------------------

    def GetHighLightColor(self):
        """Get the color to highlight buttons."""
        return self._hicolor

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self._hicolor = color

    # -----------------------------------------------------------------------
    # Manage the set of files
    # -----------------------------------------------------------------------

    def get_files(self):
        """Return the list of filenames this panel is displaying."""
        return list(self._files.keys())

    # -----------------------------------------------------------------------
    # Manage a given file
    # -----------------------------------------------------------------------

    def can_edit(self):
        """Return True if this view can modify/save the file content.

        Can be overridden.

        If True, the methods 'is_modified' and 'save' should be implemented
        in the view panel of each file.

        """
        return False

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

    def append_file(self, name):
        """Add a file and display its content.

        Do not refresh/layout the GUI.

        :param name: (str)
        :raise: ValueError

        """
        if name in self._files:
            wx.LogError('Name {:s} is already in the list of files.')
            raise ValueError('Name {:s} is already in the list of files.')

        try:
            panel = self._show_file(name)
        except Exception as e:
            panel = ErrorViewPanel(self.GetScrolledPanel(), name)
            panel.set_error_message(str(e))
            self.GetScrolledSizer().Add(panel, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 20)
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)

        self._files[name] = panel

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
            for i, child in enumerate(self.GetScrolledChildren()):
                if child == page:
                    self.GetScrolledSizer().Remove(i)
                    break
                for c in child.GetChildren():
                    if c == page:
                        self.GetScrolledSizer().Remove(i)
                        break

            page.Destroy()

            # Delete of the list
            self._files.pop(name)
            return True

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
                    wx.LogMessage("File {:s} saved successfully.".format(name))
            except Exception as e:
                saved = False
                wx.LogError("Error while saving file {:s}: {:s}"
                            "".format(name, str(e)))

        return saved

    # -----------------------------------------------------------------------
    # Manage a given file and its page
    # -----------------------------------------------------------------------

    def close_page(self, filename):
        """Close the page matching the given filename.

        :param filename: (str)
        :return: (bool) The page was closed.

        """
        if filename not in self._files:
            return False
        page = self._files[filename]

        if page.is_modified() is True:
            wx.LogWarning("File contains not saved changes.")
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(CLOSE_CONFIRM, CLOSE)
            if response == wx.ID_CANCEL:
                return False

        removed = self.remove_file(filename, force=True)
        if removed is True:
            self.Layout()
            self.Refresh()

            # The parent will unlock the file in the workspace
            self.notify(action="close", filename=filename)
            return True

        return False

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
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        toolbar = self._create_toolbar()
        scrolled = self._create_scrolled_content()
        main_sizer.Add(toolbar, 0, wx.EXPAND, 0)
        main_sizer.Add(scrolled, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)

    # -----------------------------------------------------------------------

    def _create_toolbar(self):
        """Create the main toolbar.

        :return: (sppasPanel, wx.Panel, sppasToolbar, ...)

        """
        return sppasPanel(self, name="toolbar_views")

    # -----------------------------------------------------------------------

    def _create_scrolled_content(self):
        content_panel = sppasScrolledPanel(self, name="scrolled_views")
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_panel.SetupScrolling(scroll_x=True, scroll_y=True)
        content_panel.SetSizer(content_sizer)
        min_height = sppasPanel.fix_size(48)*len(self._files)
        content_panel.SetMinSize(wx.Size(sppasPanel.fix_size(420), min_height))

        return content_panel

    # -----------------------------------------------------------------------

    def GetScrolledPanel(self):
        return self.FindWindow("scrolled_views")

    # -----------------------------------------------------------------------

    def GetScrolledSizer(self):
        return self.FindWindow("scrolled_views").GetSizer()

    # -----------------------------------------------------------------------

    def GetScrolledChildren(self):
        return self.FindWindow("scrolled_views").GetChildren()

    # -----------------------------------------------------------------------

    def ScrollChildIntoView(self, panel):
        self.FindWindow("scrolled_views").ScrollChildIntoView(panel)

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

        """
        self.GetScrolledPanel().Bind(EVT_VIEW, self._process_view_event)

    # -----------------------------------------------------------------------

    def _process_view_event(self, event):
        """Process a view event: an action has to be performed.

        :param event: (wx.Event)

        """
        wx.LogDebug("View Event received by {:s}".format(self.GetName()))
        try:
            panel = event.GetEventObject()
            panel_name = panel.GetName()

            action = event.action
            fn = None
            for filename in self._files:
                p = self._files[filename]
                if p == panel:
                    fn = filename
                    break
            if fn is None:
                raise Exception("Unknown {:s} panel in ViewEvent."
                                "".format(panel_name))
        except Exception as e:
            wx.LogError(str(e))
            return

        if action == "save":
            self.save_file(fn)

        elif action == "close":
            self.close_page(fn)

    # -----------------------------------------------------------------------

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.ScrollChildIntoView(panel)
        self.Layout()