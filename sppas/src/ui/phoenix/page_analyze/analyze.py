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

    ui.phoenix.page_analyze.analyze.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    One of the main pages of the wx4-based GUI of SPPAS.

    It manages:

        - a set of tabs,
        - a book (each page is matching a tab),
        - a toolbar.

    Checked files of the workspace are opened in the active page, ie the
    checked tab, then they are locked (so that they can't be un-checked
    in the file manager).

"""

import logging
import wx

from sppas import sppasTypeError
from sppas import msg
from sppas.src.utils import u
from sppas.src.files import FileData, States

from ..main_events import DataChangedEvent, EVT_DATA_CHANGED
from ..main_events import EVT_TAB_CHANGE

from ..windows import sppasPanel
from ..windows import sppasStaticLine
from ..windows.book import sppasSimplebook
from ..windows import sppasToolbar

from .anz_tabs import TabsManager
from .anz_baseviews import BaseViewFilesPanel
from .anz_textviews import TextViewFilesPanel

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


VIEW_TITLE = _("Views: ")
VIEW_LIST = _("Summary")
VIEW_TIME = _("Time line")
VIEW_TEXT = _("Text edit")
VIEW_GRID = _("Grid details")
VIEW_STAT = _("Statistics")

# ---------------------------------------------------------------------------


class sppasAnalyzePanel(sppasPanel):
    """Create a panel to analyze the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    The panel is made of 3 areas:

        - a toolbar to switch to the expected analyze view,
        - a list of tabs,
        - a book.

    Each tab is matching a page of the book. It contains some of the checked
    files of the data. The page displays such files depending on the selected
    view of the toolbar.

    """

    HIGHLIGHT_COLOUR = wx.Colour(196, 96, 196, 196)
    VIEWS = {
        "data-view-list": VIEW_LIST,
        "data-view-timeline": VIEW_TIME,
        "data-view-text": VIEW_TEXT,
        "data-view-grid": VIEW_GRID,
        "data-view-stats": VIEW_STAT
    }

    def __init__(self, parent):
        super(sppasAnalyzePanel, self).__init__(
            parent=parent,
            name="page_analyze",
            style=wx.BORDER_NONE
        )

        # Initial view
        self._viewname = "data-view-list"

        # The data all tabs are working on
        self.__data = FileData()

        # Construct the GUI
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # Organize items and fix a size for each of them
        self.Layout()

        # Add a first empty tab and page
        self.FindWindow("tabs").append_tab()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (FileData) data of the files-viewer model.

        """
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (FileData)

        """
        if isinstance(data, FileData) is False:
            raise sppasTypeError("FileData", type(data))
        logging.debug('New data in the analyze page. '
                      'Id={:s}'.format(data.id))
        self.__data = data

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # Create all the panels
        tm = TabsManager(self, name="tabs")
        p = sppasPanel(self)
        tb = self.__create_toolbar(p)
        bk = sppasSimplebook(p, name="content")

        # Organize all the panels, separated by 2px grey lines.
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(tb, 0, wx.EXPAND, 0)
        s.Add(bk, 1, wx.EXPAND, 0)
        p.SetSizer(s)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(tm, 1, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(p, 8, wx.EXPAND, 0)

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_toolbar(self, parent):
        """Create the toolbar."""
        tb = sppasToolbar(parent)
        tb.set_focus_color(sppasAnalyzePanel.HIGHLIGHT_COLOUR)

        # Add toggle buttons to switch the view
        tb.AddTitleText("Views: ", color=sppasAnalyzePanel.HIGHLIGHT_COLOUR)
        for view_name in sppasAnalyzePanel.VIEWS:
            btn = tb.AddToggleButton(
                view_name,
                sppasAnalyzePanel.VIEWS[view_name],
                value=False,
                group_name="views")

            # Set the default view
            if view_name == self._viewname:
                btn.SetValue(True)

        return tb

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

    def __create_book(self):
        """Create the simple book to manage the opened files in tabs."""
        book = sppasSimplebook(
            parent=self,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS,
            name="content"
        )
        book.SetEffectsTimeouts(100, 150)
        return book

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self):
        """The parent is informed of changes of the workspace."""
        evt = DataChangedEvent(data=self.__data)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate an handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # The data have changed.
        # This event is sent by the tabs manager or by the parent
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

        # The active tab has changed. The book must do the same.
        # This event is sent by the tabs manager
        self.Bind(EVT_TAB_CHANGE, self._process_tab_change)

        # The user clicked a button of the toolbar
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_event)
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()
        logging.debug('Analyze page received a key event. key_code={:d}'.format(key_code))

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
            logging.error('Data were not sent in the event emitted by {:s}'
                          '.'.format(emitted.GetName()))
            return
        self.__data = data

    # -----------------------------------------------------------------------

    def _process_tab_change(self, event):
        """Process a change of page.

        A tab is matching a page of the book. When the tab changed, the page
        displaying the files has to be changed too.

        :param event: (wx.Event)

        """
        logging.debug("Process tab change, one of (open/append/remove).")
        emitted = event.GetEventObject()
        try:
            action = event.action
            cur_page_name = event.cur_tab
            dest_page_name = event.dest_tab
        except:
            wx.LogError('Malformed event emitted by {:s}'
                        '.'.format(emitted.GetName()))
            return

        book = self.FindWindow("content")

        if action == "open":
            w = book.FindWindow(cur_page_name)
            if w is None:
                wx.LogError("No page with name {:s}.".format(cur_page_name))
                return
            self._open_files(w)

        elif action == "append":
            color = event.color
            self._append_page(cur_page_name, color)

        elif action == "remove":
            w = book.FindWindow(cur_page_name)
            if w is None:
                wx.LogError("No page with name {:s}".format(cur_page_name))
                return
            self._remove_page(w)

        # Show a page of the book
        if dest_page_name is not None:
            if dest_page_name != cur_page_name:
                self._show_page(dest_page_name)

    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of event.

        :param event: (wx.Event)

        """
        event_name = event.GetButtonObj().GetName()
        if event_name.startswith("data-view-"):
            if self._viewname != event_name:
                self._switch_page_to_view(event_name)

        event.Skip()

    # -----------------------------------------------------------------------
    # Management of the book
    # -----------------------------------------------------------------------

    def _open_files(self, page):
        """Open the checked files in the given page.

        :param page: (ViewFilesPanel)

        """
        checked = self.__data.get_filename_from_state(States().CHECKED)
        i = 0
        for fn in checked:
            try:
                page.append_file(fn.get_id())
                self.__data.set_object_state(States().LOCKED, fn)
                i += 1
            except Exception as e:
                wx.LogError(str(e))

        # send data to the parent
        if i > 0:
            wx.LogMessage("{:d} files opened in page {:s}."
                          "".format(i, page.GetName()))
            self.notify()
        else:
            wx.LogMessage("No file opened in page {:s}.".format(page.GetName()))

    # -----------------------------------------------------------------------

    def _append_page(self, page_name, color=None, files=()):
        """Append a page to the content panel.

        Attention: does not add the tab corresponding to this page.

        :param page_name: (str)
        :param color: (wx.Colour)
        :param files: (list) List of filenames

        """
        logging.debug("Create page {:s}".format(page_name))
        book = self.FindWindow("content")

        if self._viewname == "data-view-text":
            wx.LogMessage("New empty text-view page created.")
            new_page = TextViewFilesPanel(book, name=page_name, files=files)
        else:
            wx.LogWarning("{:s} view is not currently supported."
                          "".format(self._viewname))
            new_page = BaseViewFilesPanel(book, name=page_name, files=files)

        if color is not None:
            new_page.SetHighLightColor(color)

        book.AddPage(new_page, text="")
        # self.Refresh()
        return new_page

    # -----------------------------------------------------------------------

    def _remove_page(self, page):
        """Remove a page of the content panel.

        Attention: does not remove the tab corresponding to this page.

        :param page: (ViewFilesPanel)

        """
        logging.debug("Remove page {:s}".format(page.GetName()))
        # Unlock files
        fns = [self.__data.get_object(fname) for fname in page.get_files()]
        try:
            i = self.__data.unlock(fns)
        except Exception as e:
            wx.LogError(str(e))
            return

        # Delete the page then the associated window
        book = self.FindWindow("content")
        p = book.FindPage(page)
        if p != wx.NOT_FOUND:
            book.RemovePage(p)
        page.Destroy()
        # self.Refresh()

        if i > 0:
            wx.LogMessage("{:d} files closed by page {:s}."
                          "".format(i, page.GetName()))
            self.notify()
        else:
            wx.LogMessage("No file closed by page {:s}.".format(page.GetName()))

    # -----------------------------------------------------------------------

    def _show_page(self, page_name):
        """Show a page of the content panel.

        Attention: does not select the tab corresponding to this page.

        :param page_name: (str)

        """
        book = self.FindWindow("content")

        # the current page number
        c = book.FindPage(book.GetCurrentPage())

        # the page number to switch on
        page = book.FindWindow(page_name)
        if page is None:
            logging.error("No page with name {:s} found in the book."
                          "".format(page_name))
            return
        p = book.FindPage(page)
        if p == wx.NOT_FOUND:
            return

        # assign the effect
        if c == p:
            return
        elif c < p:
            book.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP)
        else:
            book.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM)

        # then change the current tab
        book.ChangeSelection(p)
        self.Refresh()

    # -----------------------------------------------------------------------

    def _switch_page_to_view(self, view_name):
        """Switch the current page to the view with the given name.

        :param view_name: (str) Name of the view to switch to.

        """
        if view_name == self._viewname:
            return

        logging.debug("Switch to view {:s}".format(view_name))
        book = self.FindWindow("content")
        page = book.GetCurrentPage()
        if page is None:
            wx.LogMessage("Attempted to switch to view {:s} without "
                          "opened page...".format(view_name))
            return

        # delete the current page
        page_name = page.GetName()
        page_color = page.GetHighLightColor()
        page_files = page.get_files()
        page_index = book.FindPage(page)
        book.RemovePage(page_index)
        page.Destroy()
        logging.debug("Page {:s} deleted (to create a new one with the new view). ".format(page_name))
        logging.debug("  -> page files = {!s:s}".format(str(page_files)))

        # Set the name of the new view
        self._viewname = view_name

        # Create and append the page with the appropriate new view
        new_page = self._append_page(page_name, page_color, page_files)

        page_index = book.FindPage(new_page)
        book.ChangeSelection(page_index)
        self.Refresh()
