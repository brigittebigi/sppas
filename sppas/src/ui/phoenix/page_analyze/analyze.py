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

import os
import random
import wx

from sppas.src.config import paths
from sppas.src.config import msg
from sppas.src.exceptions import sppasTypeError
from sppas.src.utils import u
from sppas.src.wkps import sppasWorkspace, States
from sppas.src.anndata import sppasRW, FileFormatProperty

from ..main_events import DataChangedEvent, EVT_DATA_CHANGED
from ..main_events import EVT_TAB_CHANGE
from ..main_events import EVT_VIEW

from ..windows.dialogs import Information, Confirm, Error
from ..windows.dialogs import sppasFileDialog
from ..windows.dialogs import sppasProgressDialog
from ..windows import sppasPanel
from ..windows import sppasStaticLine
from ..windows.book import sppasSimplebook
from ..windows import sppasToolbar

from .anz_tabs import TabsManager
from .anz_textviews import TextViewFilesPanel
from .anz_listviews import ListViewFilesPanel
from .anz_timeviews import TimeViewFilesPanel
from .anz_defaultviews import DefaultViewFilesPanel

# ---------------------------------------------------------------------------
# List of displayed messages:


def _(message):
    return u(msg(message, "ui"))


VIEW_TITLE = _("Views: ")
VIEW_LIST = _("Detailed list")
VIEW_TEXT = _("Text editor")
VIEW_TIME = _("Multi-Player")
CLOSE = _("Close")

TAB_MSG_NO_SELECT = _("No tab is currently checked.")
TAB_MSG_CONFIRM_SWITCH = _("Confirm switch of tab?")
VIEW_MSG_CONFIRM_SWITCH = _("Confirm switch of view?")
TAB_MSG_CONFIRM = _("The current tab contains not saved work that "
                    "will be lost. Are you sure you want to change tab?")
VIEW_MSG_CONFIRM = _("The current view contains not saved work that "
                     "will be lost. Are you sure you want to change view?")

TAB_ACT_CREATE = _("Create file")
TAB_ACT_SAVEALL = _("Save all")
TAB_ACT_SAVECURRENT_ERROR = _(
    "Files of the current tab can not be saved due to "
    "the following error: {:s}\nConfirm you still want to switch tab?")
VIEW_ACT_SAVECURRENT_ERROR = _(
    "Files of the current view can not be saved due to "
    "the following error: {:s}\nConfirm you still want to switch view?")

CLOSE_CONFIRM = _("The file contains not saved work that will be lost. "
                  "Are you sure you want to close?")

# ---------------------------------------------------------------------------


class TabParam(object):
    """Data structure of the parameters of a tab.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create the TabParam instance of the given index."""
        self.view_name = "data-view-list"
        self.hicolor = wx.Colour(random.randint(60, 230),
                                 random.randint(60, 230),
                                 random.randint(60, 230))

# ---------------------------------------------------------------------------


class sppasAnalyzePanel(sppasPanel):
    """Create a panel to analyze the selected files.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The panel is made of 3 areas:

        - a list of tabs
        - a toolbar to switch to the expected view
        - a book matching the tabs

    Each tab is matching a page of the book. It contains some of the checked
    files of the data. The page displays such files depending on the selected
    view of the toolbar.

    """

    HIGHLIGHT_COLOUR = wx.Colour(96, 196, 196, 196)

    VIEWS = {
        "data-view-list": VIEW_LIST,
        "data-view-timeline": VIEW_TIME,
        "data-view-text": VIEW_TEXT
    }

    # ------------------------------------------------------------------------

    def __init__(self, parent):
        super(sppasAnalyzePanel, self).__init__(
            parent=parent,
            name="page_analyze",
            style=wx.BORDER_NONE
        )

        # Parameters related to each of the tabs/pages like the view, etc.
        self._params = list()

        # The data all tabs are working on
        self.__data = sppasWorkspace()

        # Construct the GUI
        self._create_content()
        self._setup_events()

        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        # Organize items and fix a size for each of them
        self.Layout()

        # Add a first empty tab and page
        self.append()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (sppasWorkspace) data of the files-viewer model.

        """
        return self.__data

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (sppasWorkspace)

        """
        if isinstance(data, sppasWorkspace) is False:
            raise sppasTypeError("sppasWorkspace", type(data))

        self.__data = data

    # ------------------------------------------------------------------------
    # Manage the content
    # ------------------------------------------------------------------------

    def open_files(self):
        """Open the checked files in the current page.

        Opened files are locked and parent is notified.

        """
        tabs = self.FindWindow("tabs")

        # Get the index of the currently selected tab and the page
        cur_index = tabs.get_selected_tab()
        if cur_index == -1:
            Information(TAB_MSG_NO_SELECT)
            return
        book = self.FindWindow("content")
        page = book.GetCurrentPage()

        # Add checked files to the page
        checked = self.__data.get_filename_from_state(States().CHECKED)
        success = 0
        total = len(checked)
        progress = sppasProgressDialog()
        progress.set_new()
        progress.set_header("Open files...")
        progress.set_fraction(0)
        wx.BeginBusyCursor()
        for i, fn in enumerate(sorted(checked)):
            try:
                fraction = float((i+1)) / float(total)
                message = os.path.basename(fn.get_id())
                progress.update(fraction, message)
                page.append_file(fn.get_id())
                page.Layout()
                self.__data.set_object_state(States().LOCKED, fn)
                success += 1
            except Exception as e:
                wx.LogError(str(e))
        wx.EndBusyCursor()
        progress.set_fraction(1)
        progress.close()

        if page is None:
            return

        # send data to the parent
        if success > 0:
            self.Layout()
            self.Refresh()
            wx.LogMessage("{:d} files opened in page {:s}."
                          "".format(success, page.GetName()))
            self.notify()
        else:
            wx.LogMessage("No file opened in page {:s}.".format(page.GetName()))

    # ------------------------------------------------------------------------

    def save_files(self):
        """Save the files of the selected page (if modified).

        Ask the page to save each of its files.

        """
        tabs = self.FindWindow("tabs")
        cur_index = tabs.get_selected_tab()
        if cur_index == -1:
            Information(TAB_MSG_NO_SELECT)
            return

        book = self.FindWindow("content")
        page = book.GetPage(cur_index)
        if page.is_modified() is False:
            wx.LogMessage("None of the files was modified. Nothing to do.")
            return

        n = 0
        for filename in page.get_files():
            saved = page.save_file(filename)
            if saved:
                n += 1

        if n > 0:
            wx.LogMessage("{:d} files saved.".format(n))
        else:
            wx.LogMessage("No saved files.")

    # ------------------------------------------------------------------------

    def create_file(self):
        """Open a dialog to fix a filename and add the corresponding panel."""
        # Which tab is currently selected to add the new file?
        tabs = self.FindWindow("tabs")
        cur_index = tabs.get_selected_tab()
        if cur_index == -1:
            Information(TAB_MSG_NO_SELECT)
            return

        dlg = sppasFileDialog(self,
                              title="Path and name of a new file",
                              style=wx.FC_SAVE | wx.FC_NOSHOWHIDDEN)
        dlg.SetDirectory(paths.samples)
        wildcard = list()
        extensions = list()
        for e in sppasRW.extensions():
            f = FileFormatProperty(e)
            if f.get_writer() is True:
                wildcard.append(f.get_software() + " files (" + e + ")|*." + e)
                extensions.append(e)
        dlg.SetWildcard("|".join(wildcard))

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            fn, fe = os.path.splitext(filename)
            if len(fn) > 0:
                if len(fe) == 0:
                    filename += "." + extensions[dlg.GetFilterIndex()]

                if os.path.exists(filename) is True:
                    Error("Filename {:s} is already existing.".format(filename))
                else:
                    book = self.FindWindow("content")
                    page = book.GetPage(cur_index)
                    try:
                        page.create_file(filename)
                    except Exception as e:
                        Error(str(e))
        dlg.Destroy()

    # ------------------------------------------------------------------------

    def append(self):
        """Append a tab/page/param to manage some of the data.

        """
        # Append a new set of default parameters
        self._params.append(TabParam())

        # Append a tab to the TabsManager
        tabs = self.FindWindow("tabs")
        i = tabs.append_tab()
        tabs.set_tab_color(i, self._params[i].hicolor)

        # Append a page to the book
        book = self.FindWindow("content")
        new_page = self._create_view(self._params[i].view_name)
        new_page.SetHighLightColor(self._params[i].hicolor)
        new_page.SetName("anz_page_panel_{:d}".format(i))
        book.AddPage(new_page, text="")

        # If it is the first page, we switch on it.
        if i == 0:
            self.switch_to(0)

    # ------------------------------------------------------------------------

    def remove(self):
        """Remove a tab/page which managed some of the data.

        """
        # Check if a tab is selected
        tabs = self.FindWindow("tabs")
        cur_index = tabs.get_selected_tab()
        if cur_index == -1:
            Information("No tab is currently checked to be closed.")
            return

        # Remove the page of the book (if authorized...)
        r = self._remove_page(cur_index)
        if r is True:
            # Remove the tab of the TabsManager
            tabs.remove_tab(cur_index)

            # And remove the corresponding parameters
            self._params.pop(cur_index)
            self._default_toolbar()

            # The book switched automatically to another page!
            book = self.FindWindow("content")
            page_index = book.FindPage(book.GetCurrentPage())
            if page_index != wx.NOT_FOUND:
                self.switch_to(page_index)

    # -----------------------------------------------------------------------

    def switch_to(self, page_index):
        """Show another page/tab.

        :param page_index: (int) Index of the tab/page to display.

        """
        book = self.FindWindow("content")
        tabs = self.FindWindow("tabs")
        toolbar = self.FindWindow("analyze-toolbar")

        # check if a page is existing at the given index
        p = book.GetPage(page_index)
        if p == wx.NOT_FOUND:
            wx.LogError("Switch to... No page is existing at index {:d}"
                        "".format(page_index))
            return

        # the index of the currently selected page
        #  -- cur_index should match with c but the book is automatically
        #     changing its selected page when removing...
        # cur_index = book.FindPage(book.GetCurrentPage())
        c = tabs.get_selected_tab()

        # assign the effect
        if c != -1:
            if c == page_index:
                # nothing to do... we're already on the right page!
                return

            if c < page_index:
                book.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP,
                                hideEffect=wx.SHOW_EFFECT_SLIDE_TO_TOP)
            else:
                book.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM,
                                hideEffect=wx.SHOW_EFFECT_SLIDE_TO_BOTTOM)
            # disable the current button of the view
            self._update_toolbar(False, c)

        # then change the current page/tab
        book.ChangeSelection(page_index)
        tabs = self.FindWindow("tabs")
        tabs.switch_to_tab(page_index)

        # enable the button of the view
        self._update_toolbar(True, page_index)

        self.Refresh()

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
        tb = sppasToolbar(parent, name="analyze-toolbar")
        tb.set_focus_color(sppasAnalyzePanel.HIGHLIGHT_COLOUR)

        tb.AddTitleText(VIEW_TITLE,
                        color=sppasAnalyzePanel.HIGHLIGHT_COLOUR,
                        name="view-title-text")

        # Add toggle buttons to switch the view
        for view_name in sppasAnalyzePanel.VIEWS:
            btn = tb.AddToggleButton(
                view_name,
                sppasAnalyzePanel.VIEWS[view_name],
                value=False,
                group_name="views")
            btn.SetBorderWidth(2)
            # btn.Enable(False)

        tb.AddSpacer(1)

        # Add button to create a new (empty) file
        create_btn = tb.AddButton("files-new-file", TAB_ACT_CREATE)
        create_btn.LabelPosition = wx.BOTTOM
        create_btn.Spacing = 1

        # Add button to save files of the current tab
        save_btn = tb.AddButton("save_all", TAB_ACT_SAVEALL)
        save_btn.Enable(False)
        save_btn.LabelPosition = wx.BOTTOM
        save_btn.Spacing = 1

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
        # The data have changed.
        # This event is sent by the tabs manager or by the parent
        self.Bind(EVT_DATA_CHANGED, self._process_data_changed)

        # The active tab has changed. The book must do the same.
        # This event is sent by the tabs manager
        self.Bind(EVT_TAB_CHANGE, self._process_tab_change)

        # The user clicked a button of the toolbar
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_event)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        # The view performed an action.
        self.FindWindow("content").Bind(EVT_VIEW, self._process_view_event)

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
        self.__data = data

    # -----------------------------------------------------------------------

    def _process_tab_change(self, event):
        """Process a change of page.

        A tab is matching a page of the book. When the tab changed, the page
        displaying the files has to be changed too.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            action = event.action
            dest_index = event.dest_tab
        except:
            wx.LogError('Malformed event emitted by {:s}'
                        '.'.format(emitted.GetName()))
            return

        if action == "open":
            self.open_files()

        elif action == "append":
            self.append()

        elif action == "remove":
            self.remove()

        elif action == "show":
            self.switch_to(dest_index)

    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of event.

        :param event: (wx.Event)

        """
        event_name = event.GetButtonObj().GetName()

        if event_name.startswith("data-view-"):
            self._switch_page_to_view(event_name)

        elif event_name == "save_all":
            self.save_files()

        elif event_name == "files-new-file":
            self.create_file()

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_view_event(self, event):
        """Process a view event: an action has to be performed.

        :param event: (wx.Event)

        """
        # page = event.GetEventObject()
        try:
            action = event.action
            filename = event.filename
        except Exception as e:
            wx.LogError(str(e))
            return

        if action == "close":
            # Unlock the closed file
            fns = [self.__data.get_object(filename)]
            try:
                self.__data.unlock(fns)
                self.notify()
            except Exception as e:
                wx.LogError(str(e))
                return False

        elif action == "saved":
            # A file was saved by the panel.
            fn = self.__data.get_object(filename)
            if fn is None:
                added = self.__data.add_file(filename)
                if len(added) > 0:
                    self.__data.set_object_state(States().LOCKED, added[0])
                    self.notify()

    # -----------------------------------------------------------------------
    # Management of the book
    # -----------------------------------------------------------------------

    def _create_view(self, view_name, files=()):
        """Create a panel displaying the given files with a view.

        :param view_name: (str)
        :param files: (list) List of filenames
        :return: (BaseViewFilesPanel)

        """
        book = self.FindWindow("content")

        if view_name == "data-view-text":
            new_page = TextViewFilesPanel(book, name="new_page", files=files)

        elif view_name == "data-view-list":
            new_page = ListViewFilesPanel(book, name="new_page", files=files)

        elif view_name == "data-view-timeline":
            new_page = TimeViewFilesPanel(book, name="new_page", files=files)

        else:
            wx.LogWarning("{:s} view is not currently supported."
                          "".format(view_name))
            new_page = DefaultViewFilesPanel(book, name="new_page", files=files)

        return new_page

    # -----------------------------------------------------------------------

    def _remove_page(self, page_index):
        """Remove a page of the content panel.

        Attention: does not remove the tab corresponding to this page.

        :param page_index: (int)

        """
        book = self.FindWindow("content")
        page = book.GetPage(page_index)
        if page == wx.NOT_FOUND:
            return False

        # Ask the page if at least one file has been modified
        if page.is_modified() is True:
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(TAB_MSG_CONFIRM, TAB_MSG_CONFIRM_SWITCH)
            if response == wx.ID_CANCEL:
                return False

        # Unlock files
        fns = [self.__data.get_object(fname) for fname in page.get_files()]
        try:
            i = self.__data.unlock(fns)
        except Exception as e:
            wx.LogError(str(e))
            return False

        # Delete the page then the associated window
        page_name = page.GetName()
        book.RemovePage(page_index)
        page.Destroy()

        if i > 0:
            wx.LogMessage("{:d} files closed by page {:s}."
                          "".format(i, page_name))
            self.Refresh()
            self.notify()
        else:
            wx.LogMessage("No file closed by page {:s}.".format(page_name))

        return True

    # -----------------------------------------------------------------------

    def _switch_page_to_view(self, view_name):
        """Switch the current page to the view with the given name.

        :param view_name: (str) Name of the view to switch to.

        """
        tabs = self.FindWindow("tabs")
        page_index = tabs.get_selected_tab()
        if view_name == self._params[page_index].view_name:
            return False

        book = self.FindWindow("content")
        page = book.GetCurrentPage()
        if page is None:
            wx.LogMessage("Attempted to switch to view {:s} without "
                          "opened page...".format(view_name))
            return False

        # Ask the page if at least one file has been modified
        if page.is_modified() is True:
            # Ask the user to confirm to close (and changes are lost)
            response = Confirm(VIEW_MSG_CONFIRM, VIEW_MSG_CONFIRM_SWITCH)
            if response == wx.ID_CANCEL:
                return False

        # delete the current page
        page_index = book.FindPage(page)
        self._update_toolbar(False, page_index)
        page_name = page.GetName()
        page_color = page.GetHighLightColor()
        page_files = page.get_files()
        book.RemovePage(page_index)
        page.Destroy()

        # Set the name of the new view
        self._params[page_index].view_name = view_name

        # Create and insert the page with the appropriate new view
        new_page = self._create_view(view_name, page_files)
        new_page.SetName(page_name)
        new_page.SetHighLightColor(page_color)
        book.InsertPage(page_index, new_page, text="")
        book.ChangeSelection(page_index)
        self._update_toolbar(True, page_index)

        new_page.Refresh()
        book.Refresh()
        self.Refresh()
        return True

    # -----------------------------------------------------------------------

    def _update_toolbar(self, value, index):
        """Enable or disable the buttons of the toolbar.

        :param value: (bool) True for the selected page
        :param index: (int) Page/tab index

        """
        toolbar = self.FindWindow("analyze-toolbar")
        toolbar.set_focus_color(self._params[index].hicolor)
        btn_view_name = self._params[index].view_name

        btn = toolbar.FindWindow(btn_view_name)
        btn.SetValue(value)

        txt_view = toolbar.FindWindow("view-title-text")
        if value is True:
            btn.BitmapColour = self._params[index].hicolor
            btn.BorderColour = self._params[index].hicolor
            txt_view.SetForegroundColour(self._params[index].hicolor)
        else:
            btn.BitmapColour = btn.GetForegroundColour()
            btn.BorderColour = btn.GetPenForegroundColour()
            txt_view.SetForegroundColour(sppasAnalyzePanel.HIGHLIGHT_COLOUR)

        book = self.FindWindow("content")
        btn_save = toolbar.FindWindow("save_all")
        try:
            page = book.GetPage(index)
            btn_save.Enable(page.can_edit())
        except Exception as e:
            btn_save.Enable(False)
            wx.LogError(str(e))

        toolbar.Refresh()

    # -----------------------------------------------------------------------

    def _default_toolbar(self):
        """Disable the buttons of the toolbar.

        Useful if no page/tab is selected.

        """
        toolbar = self.FindWindow("analyze-toolbar")
        toolbar.set_focus_color(sppasAnalyzePanel.HIGHLIGHT_COLOUR)

        btn_save = toolbar.FindWindow("save_all")
        btn_save.Enable(False)

        for view_name in sppasAnalyzePanel.VIEWS:
            btn = toolbar.FindWindow(view_name)
            btn.SetValue(False)
            btn.BitmapColour = btn.GetForegroundColour()
            btn.BorderColour = btn.GetPenForegroundColour()

        txt_view = toolbar.FindWindow("view-title-text")
        txt_view.SetForegroundColour(sppasAnalyzePanel.HIGHLIGHT_COLOUR)
