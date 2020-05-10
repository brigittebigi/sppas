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

    ui.phoenix.main_window.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.config import sg, sppasAppConfig
from sppas.src.config import msg
from sppas.src.utils import u

from .windows import sppasStaticLine
from .windows import BitmapTextButton
from .windows import ToggleButton
from .windows import sppasPanel
from .windows import sppasDialog
from .windows.book import sppasSimplebook

from .page_home import sppasHomePanel
from .page_files import sppasFilesPanel
from .page_annotate import sppasAnnotatePanel
from .page_analyze import sppasAnalyzePanel
from .page_convert import sppasConvertPanel
from .page_plugins import sppasPluginsPanel

from .windows import YesNoQuestion
from .views import About
from .views import Settings
from .main_log import sppasLogWindow
from .main_events import DataChangedEvent, EVT_DATA_CHANGED

# ---------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_ACTION_HOME = _('Home')
MSG_ACTION_FILES = _('Files')
MSG_ACTION_ANNOTATE = _('Annotate')
MSG_ACTION_ANALYZE = _('Analyze')
MSG_ACTION_CONVERT = _('Convert')
MSG_ACTION_PLUGINS = _('Plugins')
MSG_ACTION_EXIT = _('Exit')
MSG_ACTION_ABOUT = _('About')
MSG_ACTION_SETTINGS = _('Settings')
MSG_ACTION_VIEWLOGS = _('View logs')

MSG_CONFIRM = _("Confirm exit?")

# -----------------------------------------------------------------------


class sppasMainWindow(sppasDialog):
    """Create the main frame of SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class:

        - does not inherit of wx.TopLevelWindow because we need EVT_CLOSE
        - does not inherit of wx.Frame because we don't need neither a
        status bar, nor a toolbar, nor a menu.

    Styles:

        - wx.CAPTION: Puts a caption on the dialog box
        - wx.RESIZE_BORDER: Display a resizable frame around the window
        - wx.CLOSE_BOX: Displays a close box on the frame
        - wx.MAXIMIZE_BOX: Displays a maximize box on the dialog
        - wx.MINIMIZE_BOX: Displays a minimize box on the dialog
        - wx.DIALOG_NO_PARENT: Create an orphan dialog

    """

    # List of the page names of the main notebook
    pages = ("page_home", "page_files", "page_annotate", "page_analyze",
             "page_convert", "page_plugins")

    def __init__(self):
        super(sppasMainWindow, self).__init__(
            parent=None,
            title=wx.GetApp().GetAppDisplayName(),
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.CAPTION |
                  wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX |
                  wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT,
            name="sppas_main_dlg")

        # Members
        self._init_infos()

        # Create the log window of the application and show it.
        self.log_window = sppasLogWindow(self, sppasAppConfig().log_level)

        # Fix this frame content
        self._create_content()
        self._setup_events()
        self.UpdateUI()

        # Fix this frame properties
        self.Enable()
        self.CenterOnScreen(wx.BOTH)
        self.FadeIn(deltaN=-4)
        self.Show(True)

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_infos(self):
        """Overridden. Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        sppasDialog._init_infos(self)

        # Fix some frame properties
        min_width = sppasPanel.fix_size(620)
        self.SetMinSize(wx.Size(min_width, 480))
        self.SetSize(wx.GetApp().settings.frame_size)
        self.SetName('{:s}'.format(sg.__name__))

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the frame.

        Content is made of a menu, an area for panels and action buttons.

        """
        # add a customized menu (instead of an header+toolbar)
        menus = sppasMenuPanel(self)
        self.SetHeader(menus)

        # The content of this main frame is organized in a book
        book = self._create_book()
        self.SetContent(book)

        # add some action buttons
        actions = sppasActionsPanel(self)
        self.SetActions(actions)

        # organize the content and lays out.
        menus.enable(sppasMainWindow.pages[0])
        self.LayoutComponents()

    # -----------------------------------------------------------------------

    def _create_book(self):
        """Create the simple book to manage the several pages of the frame.

        Names of the pages are: page_welcome, page_files, page_annotate,
        page_analyze, page_convert, and page_plugins.

        """
        book = sppasSimplebook(
            parent=self,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS,
            name="content"
        )
        book.SetEffectsTimeouts(150, 200)

        # 1st page: a panel with a welcome message
        book.ShowNewPage(sppasHomePanel(book))

        # 2nd: file browser
        book.AddPage(sppasFilesPanel(book), text="")

        # 3rd: annotate automatically selected files
        book.AddPage(sppasAnnotatePanel(book), text="")

        # 4th: analyze selected files
        book.AddPage(sppasAnalyzePanel(book), text="")

        # 5th: convert checked files
        book.AddPage(sppasConvertPanel(book), text="")

        # 6th: plugins
        book.AddPage(sppasPluginsPanel(book), text="")

        return book

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind close event from the close dialog 'x' on the frame
        self.Bind(wx.EVT_CLOSE, self.on_exit)

        # Bind all events from our buttons (including 'exit')
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_event)

        # The data have changed.
        # This event was sent by any of the children
        self.FindWindow("content").Bind(EVT_DATA_CHANGED, self._process_data_changed)

        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()
        event_id = event_obj.GetId()

        if event_name == "exit":
            self.exit()

        elif event_name == "view_log":
            self.log_window.focus()

        elif event_name == "about":
            About(self)

        elif event_name == "settings":
            self.on_settings()

        elif event_name in sppasMainWindow.pages:
            self.show_page(event_name)

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other panels.

        :param event: (wx.Event) An event with a sppasWorkspace()

        """
        # The object the event comes from
        emitted = event.GetEventObject()
        try:
            wkp = event.data
        except AttributeError:
            wx.LogError("Workspace wasn't sent in the event emitted by {:s}"
                        "".format(emitted.GetName()))
            return

        # Set the data to appropriate children panels
        book = self.FindWindow('content')
        for i in range(book.GetPageCount()):
            page = book.GetPage(i)
            if emitted != page and page.GetName() in sppasMainWindow.pages:
                page.set_data(wkp)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if key_code == wx.WXK_F4 and event.AltDown() and wx.Platform == "__WXMSW__":
            # ALT+F4 on WindowsInstaller to exit with confirmation
            self.on_exit(event)

        elif key_code == 87 and event.ControlDown() and wx.Platform != "__WXMSW__":
            # CMD+w on MacOS / Ctrl+w on Linux to exit with confirmation
            self.on_exit(event)

        elif key_code == 81 and event.ControlDown() and wx.Platform != "__WXMSW__":
            # CMD+q on MacOS / Ctrl+q on Linux to force exit
            self.exit()

        elif key_code == 70 and event.ControlDown():
            # CMD+f
            self.FindWindow("header").enable("page_files")
            self.show_page("page_files")

        elif key_code == wx.WXK_LEFT and event.CmdDown():
            self.show_next_page(direction=-1)

        elif key_code == wx.WXK_RIGHT and event.CmdDown():
            self.show_next_page(direction=1)

        elif key_code == wx.WXK_UP and event.CmdDown():
            page_name = sppasMainWindow.pages[0]
            self.FindWindow("header").enable(page_name)
            self.show_page(page_name)

        elif key_code == wx.WXK_DOWN and event.CmdDown():
            page_name = sppasMainWindow.pages[-1]
            self.FindWindow("header").enable(page_name)
            self.show_page(page_name)

        else:
            # Keeps on going the event to the current page of the book.
            # wx.LogDebug('Key event skipped by the main window.')
            event.Skip()

    # -----------------------------------------------------------------------
    # Callbacks to events
    # -----------------------------------------------------------------------

    def on_exit(self, event):
        """Makes sure the user was intending to exit the application.

        :param event: (wx.Event) Un-used.

        """
        response = YesNoQuestion(MSG_CONFIRM)
        if response == wx.ID_YES:
            self.exit()

    # -----------------------------------------------------------------------

    def on_settings(self):
        """Open settings dialog and apply changes."""
        response = Settings(self)
        if response == wx.ID_CANCEL:
            return

        self.UpdateUI()
        self.log_window.UpdateUI()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def exit(self):
        """Destroy the frame, terminating the application."""
        # Stop redirecting logging to this application
        self.log_window.redirect_logging(False)
        # Terminate all frames
        if wx.Platform == "__WXMSW__":
            self.DestroyChildren()
        self.DestroyFadeOut(deltaN=-6)

    # -----------------------------------------------------------------------

    def show_next_page(self, direction=1):
        """Show a page of the content panel, the next one.

        :param direction: (int) Positive=Next; Negative=RIGHT

        """
        book = self.FindWindow("content")
        c = book.GetSelection()
        wx.LogDebug("Current page index = {:d}".format(c))
        if direction > 0:
            nextc = (c+1) % len(sppasMainWindow.pages)
        elif direction < 0:
            nextc = (c-1) % len(sppasMainWindow.pages)
        else:
            return
        next_page_name = sppasMainWindow.pages[nextc]
        self.FindWindow("header").enable(next_page_name)
        self.show_page(next_page_name)

    # -----------------------------------------------------------------------

    def show_page(self, page_name):
        """Show a page of the content panel.

        If the page can't be found, the default home page is shown.

        :param page_name: (str) one of 'page_home', 'page_files', ...

        """
        book = self.FindWindow("content")

        # Find the page number to switch on
        w = book.FindWindow(page_name)
        if w is None:
            w = book.FindWindow("page_home")
        p = book.FindPage(w)
        if p == wx.NOT_FOUND:
            p = 0

        # current page number
        c = book.FindPage(book.GetCurrentPage())

        # assign the effect
        if c < p:
            book.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_LEFT,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_LEFT)
        elif c > p:
            book.SetEffects(showEffect=wx.SHOW_EFFECT_SLIDE_TO_RIGHT,
                            hideEffect=wx.SHOW_EFFECT_SLIDE_TO_RIGHT)
        else:
            book.SetEffects(showEffect=wx.SHOW_EFFECT_NONE,
                            hideEffect=wx.SHOW_EFFECT_NONE)

        # then change to the page
        book.ChangeSelection(p)
        w.SetFocus()
        self.Layout()
        self.Refresh()

# ---------------------------------------------------------------------------


class sppasMenuPanel(sppasPanel):
    """Create a custom menu panel with several action buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasMenuPanel, self).__init__(
            parent=parent,
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.NO_BORDER,
            name="header")

        self.SetMinSize(wx.Size(-1, wx.GetApp().settings.title_height))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        bord = sppasPanel.fix_size(6)

        sizer.AddStretchSpacer(2)

        home = self._create_button(MSG_ACTION_HOME, "page_home")
        sizer.Add(home, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=bord)

        files = self._create_button(MSG_ACTION_FILES, "page_files")
        sizer.Add(files, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=bord)

        annotate = self._create_button(MSG_ACTION_ANNOTATE, "page_annotate")
        sizer.Add(annotate, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=bord)

        analyze = self._create_button(MSG_ACTION_ANALYZE, "page_analyze")
        sizer.Add(analyze, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=bord)

        convert = self._create_button(MSG_ACTION_CONVERT, "page_convert")
        sizer.Add(convert, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=bord)

        plugins = self._create_button(MSG_ACTION_PLUGINS, "page_plugins")
        sizer.Add(plugins, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=bord)

        sizer.AddStretchSpacer(2)

        self.Bind(wx.EVT_TOGGLEBUTTON, self.__on_tg_btn_event)
        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def enable(self, btn_name):
        """Enable a given button name.

        :param btn_name: (str) Name of the page to enable the toggle button.

        """
        # Disable all the buttons
        for name in sppasMainWindow.pages:
            self.FindWindow(name).SetValue(False)
        # Enable the expected one
        self.FindWindow(btn_name).SetValue(True)

    # -----------------------------------------------------------------------

    def _create_button(self, text, icon):
        btn = ToggleButton(self, label=text, name=icon)

        # Get the font height for the header
        h = self.get_font_height()

        btn.SetLabelPosition(wx.RIGHT)
        btn.SetFocusStyle(wx.PENSTYLE_SOLID)
        btn.SetFocusWidth(h//4)
        btn.SetFocusColour(wx.Colour(128, 128, 128, 128))
        btn.SetSpacing(sppasPanel.fix_size(h//2))
        btn.SetBitmapColour(self.GetForegroundColour())
        btn.SetMinSize(wx.Size(h*10, h*3))

        return btn

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def __on_tg_btn_event(self, event):
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()
        if event_name in sppasMainWindow.pages:
            self.enable(event_name)
        event.Skip()

# ---------------------------------------------------------------------------


class sppasActionsPanel(sppasPanel):
    """Create my own panel with some action buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """
    def __init__(self, parent):

        super(sppasActionsPanel, self).__init__(
            parent=parent,
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.NO_BORDER,
            name="actions")

        settings = wx.GetApp().settings

        # Create the action panel and sizer
        self.SetMinSize(wx.Size(-1, settings.action_height))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # exit_btn = sppasBitmapTextButton(self, MSG_ACTION_EXIT, "exit")
        exit_btn = self._create_button(MSG_ACTION_EXIT, "exit")
        about_btn = self._create_button(MSG_ACTION_ABOUT, "about")
        settings_btn = self._create_button(MSG_ACTION_SETTINGS, "settings")
        log_btn = self._create_button(MSG_ACTION_VIEWLOGS, "view_log")

        sizer.Add(log_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self.VertLine(), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(settings_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self.VertLine(), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(about_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self.VertLine(), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(exit_btn, 4, wx.ALL | wx.EXPAND, 0)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def _create_button(self, text, icon):
        btn = BitmapTextButton(self, label=text, name=icon)

        # Get the font height for the header
        h = self.get_font_height()

        btn.SetLabelPosition(wx.RIGHT)
        btn.SetFocusStyle(wx.PENSTYLE_SOLID)
        btn.SetFocusWidth(h//4)
        btn.SetFocusColour(wx.Colour(128, 128, 128, 128))
        btn.SetSpacing(sppasPanel.fix_size(h//2))
        btn.SetBitmapColour(self.GetForegroundColour())
        btn.SetMinSize(wx.Size(h*10, h*2))

        return btn

    # ------------------------------------------------------------------------

    def VertLine(self):
        """Return a vertical static line."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(1, -1))
        line.SetSize(wx.Size(1, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(1)
        return line
