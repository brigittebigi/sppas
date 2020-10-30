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

    ui.phoenix.install_window.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import logging
import webbrowser
import traceback
import sys

from sppas.src.config import sg, paths, cfg
from sppas.src.config import msg, info
from sppas.src.preinstall import sppasInstallerDeps

from .windows import sppasStaticLine
from .windows import BitmapTextButton, TextButton
from .windows import sppasPanel, sppasScrolledPanel, sppasImagePanel
from .windows import sppasTitleText, sppasStaticText, sppasMessageText, sppasTextCtrl
from .windows import CheckListCtrl
from .windows.book import sppasSimplebook

from .windows.frame import sppasTopFrame
from .windows.dialogs import sppasProgressDialog

from .windows import YesNoQuestion
from .main_log import sppasLogWindow

# ---------------------------------------------------------------------------


MSG_HEADER = msg("InstallWizard of {soft} {version}."
                 "".format(soft=sg.__name__, version=sg.__version__),
                 "install")
MSG_PAGE = msg("Page ({page}/{total})", "install")
MSG_ACTION_BACK = msg('Back', "install")
MSG_ACTION_NEXT = msg('Next', "install")
MSG_ACTION_INSTALL = msg('Install', "install")
MSG_ACTION_CANCEL = msg('Cancel', "install")
MSG_ACTION_EXIT = msg('Exit', "install")
MSG_ACTION_VIEWLOGS = msg("View logs", "install")
MSG_CONFIRM = msg("Confirm exit?", "install")
MSG_FEAT = msg("Feature:", "install")
MSG_DESCR = msg("Description:", "install")

INFO_WELCOME = info(500, "install")
INFO_LICENSE = info(502, "install")
INFO_FEATURES = info(504, "install")
INFO_READY = info(506, "install")
INFO_SHARE = info(508, "install")
INFO_INSTALL_FINISHED = info(560, "install")
INFO_SEE_LOGS = info(512, "install")

INFO_FEATURES_DEPS = info(514, "install")
INFO_FEATURES_LANG = info(524, "install")
INFO_FEATURES_ANNOT = info(534, "install")
INFO_FEATURES_ALL = info(544, "install")

# A short license text in case the file of the GPL can't be read.
LICENSE = """
SPPAS is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of
the License, or (at your option) any later version.

SPPAS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with SPPAS; if not, write to the Free Software Foundation,
Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

------------------------------------------------------------
"""

# -----------------------------------------------------------------------


class sppasInstallWindow(sppasTopFrame):
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
    pages = ("page_home", "page_license",
             "page_features_deps", "page_ready", "page_terminate")

    def __init__(self):
        super(sppasInstallWindow, self).__init__(
            parent=None,
            title=wx.GetApp().GetAppDisplayName(),
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.CAPTION |
                  wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX |
                  wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT,
            name="sppas_install_dlg")

        # Create the log window of the application and show it.
        self.log_window = sppasLogWindow(self, cfg.log_level)
        self.log_window.EnableClear(False)

        # Members
        self._init_infos()
        try:
            self.__installer = sppasInstallerDeps()
        except Exception as e:
            logging.error("No installation will be performed. The installer "
                          "wasn't created due to the following error: {}"
                          "".format(str(e)))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            self.__installer = None

        # Fix this frame content
        self._create_content()
        self._setup_events()
        self.UpdateUI()

        # Fix this frame properties
        self.Enable()
        self.CenterOnScreen(wx.BOTH)
        self.FadeIn()
        self.Show(True)

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_infos(self):
        """Overridden. Initialize the frame.

        Set the title, the icon and the properties of the frame.

        """
        sppasTopFrame._init_infos(self)

        # Fix some frame properties
        self.SetMinSize(wx.Size(sppasPanel.fix_size(320), sppasPanel.fix_size(200)))
        w = int(wx.GetApp().settings.frame_size[0] * 0.8)
        h = int(wx.GetApp().settings.frame_size[1] * 0.8)
        self.SetSize(wx.Size(w, h))

        self.SetName('{:s}'.format(sg.__name__))

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the frame.

        Content is made of a menu, an area for anz_panels and action buttons.

        """
        # add a customized header
        header = sppasHeaderInstallPanel(self)
        self.SetHeader(header)

        # the content of this main frame is organized in a simple book:
        # the active page is shown and others are hidden
        book = self._create_book()
        self.SetContent(book)

        # add some action buttons
        actions = sppasActionsInstallPanel(self)
        self.SetActions(actions)

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
        book.SetEffectsTimeouts(100, 150)

        # 1st page: a panel with a welcome message
        book.ShowNewPage(sppasHomeInstallPanel(book))

        # 2nd: license agreement
        book.AddPage(sppasLicenseInstallPanel(book), text="")

        # 3rd-5th: select the features to be installed
        book.AddPage(sppasFeaturesInstallDepsPanel(book, installer=self.__installer), text="")

        # 6th: ready to process install
        book.AddPage(sppasReadyInstallPanel(book), text="")

        # 7th: ready to process install
        book.AddPage(sppasTerminatedInstallPanel(book), text="")

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

        # Bind all events from our buttons (including 'cancel')
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self._process_event)

        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "cancel":
            self.exit()

        elif event_name == "arrow_right":
            self.show_next_page(1)

        elif event_name == "arrow_left":
            self.show_next_page(-1)

        elif event_name == "view_log":
            self.log_window.focus()

        elif event_name == "install":
            self.process_install()

        elif event_name in sppasInstallWindow.pages:
            self.show_page(event_name)

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if key_code == wx.WXK_F4 and event.AltDown() and wx.Platform == "__WXMSW__":
            # ALT+F4 on Windows to exit with confirmation
            self.on_exit(event)

        elif key_code == 87 and event.ControlDown() and wx.Platform != "__WXMSW__":
            # CMD+w on MacOS / Ctrl+w on Linux to exit with confirmation
            self.on_exit(event)

        elif key_code == 81 and event.ControlDown() and wx.Platform != "__WXMSW__":
            # CMD+q on MacOS / Ctrl+q on Linux to force exit
            self.exit()

        elif key_code == 72 and event.ControlDown():
            # CMD+h
            self.header.enable("page_home")
            self.show_page("page_home")

        elif key_code == wx.WXK_LEFT and event.CmdDown():
            self.show_next_page(direction=-1)

        elif key_code == wx.WXK_RIGHT and event.CmdDown():
            self.show_next_page(direction=1)

        elif key_code == wx.WXK_UP and event.CmdDown():
            page_name = sppasInstallWindow.pages[0]
            self.header.enable(page_name)
            self.show_page(page_name)

        elif key_code == wx.WXK_DOWN and event.CmdDown():
            page_name = sppasInstallWindow.pages[-1]
            self.header.enable(page_name)
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
    # Public methods
    # -----------------------------------------------------------------------

    def exit(self):
        """Destroy the frame, terminating the application."""
        # Stop redirecting logging to this application
        self.log_window.redirect_logging(False)
        # Terminate all frames
        if wx.Platform == "__WXMSW__":
            self.DestroyChildren()
        self.DestroyFadeOut()

    # -----------------------------------------------------------------------

    def show_next_page(self, direction=1):
        """Show the next page of the content panel, except the last one.

        :param direction: (int) Positive=Next; Negative=Prev

        """
        book = self.FindWindow("content")
        c = book.GetSelection()
        if direction > 0:
            nextc = (c+1)
            if nextc == (len(sppasInstallWindow.pages)-1):  # cant access to the last page
                return
        elif direction < 0:
            nextc = (c-1)
            if nextc < 0:
                return
        else:
            return

        next_page_name = sppasInstallWindow.pages[nextc]
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

        # fix actions of the new page
        if page_name == "page_home":
            self.actions.EnableBack(False)
        else:
            self.actions.EnableBack(True)

        if page_name == "page_ready":
            self.actions.EnableNext(False)
            self.actions.EnableInstall(True)
        else:
            self.actions.EnableNext(True)
            self.actions.EnableInstall(False)

        self.header.SetPageNumber(sppasInstallWindow.pages.index(page_name)+1)

        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def process_install(self):
        """Installation process is here."""
        progress = sppasProgressDialog()
        progress.set_new()
        wx.BeginBusyCursor()
        self.__installer.set_progress(progress)
        errors = self.__installer.install("deps")
        wx.EndBusyCursor()
        progress.close()

        msg = INFO_INSTALL_FINISHED
        if len(errors) > 0:
            msg += "\n"
            # msg += error(500, "install").format("\n".join(errors))
            msg += "\n"
        msg += INFO_SEE_LOGS

        self.actions.CancelToExit()
        self.header.SetPageNumber(sppasInstallWindow.pages.index("page_terminate")+1)
        self.actions.EnableBack(False)
        self.actions.EnableNext(False)
        self.actions.EnableInstall(False)

        # then change to the page
        book = self.FindWindow("content")
        w = book.FindWindow("page_terminate")
        w.SetMessage(msg)
        p = book.FindPage(w)
        book.ChangeSelection(p)
        w.SetFocus()

# ---------------------------------------------------------------------------


class sppasHeaderInstallPanel(sppasPanel):
    """Create a custom panel with an header title and subtitle.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasHeaderInstallPanel, self).__init__(
            parent=parent,
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.NO_BORDER,
            name="header")

        settings = wx.GetApp().settings
        self.SetMinSize(wx.Size(-1, (settings.title_height*2)))

        sizer = wx.BoxSizer(wx.VERTICAL)
        min_height = int(float(wx.GetApp().settings.title_height)*0.8)

        # Under Windows the splash image is not transparent...
        img = os.path.join(paths.etc, "images", "splash.png")
        img_panel = sppasImagePanel(self, image=img, name="splash_header_panel")
        img_panel.SetMinSize(wx.Size(-1, min_height))

        title_panel = self.__title_header()
        title_panel.SetMinSize(wx.Size(-1, min_height))

        sizer.Add(title_panel, 1, wx.EXPAND, border=0)
        sizer.Add(img_panel, 1, wx.EXPAND, border=0)
        self.SetSizer(sizer)
        self.SetPageNumber(1)
        self.Layout()

    # -----------------------------------------------------------------------

    @property
    def _page(self):
        return self.FindWindow("page_txt")

    @property
    def _title(self):
        return self.FindWindow("title_txt")

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        sppasPanel.SetFont(self, font)
        self._title.SetFont(wx.GetApp().settings.header_text_font)
        self._page.SetFont(wx.GetApp().settings.header_text_font)
        self.Layout()

    # -----------------------------------------------------------------------

    def SetPageNumber(self, nb):
        text = MSG_PAGE.format(page=nb, total=len(sppasInstallWindow.pages))
        self._page.SetValue(text)

    # -----------------------------------------------------------------------

    def __title_header(self):
        min_height = int(float(wx.GetApp().settings.title_height)*0.8)
        # Create the title header panel and sizer
        panel = sppasPanel(self, name="title_header")

        # Add the icon, at left, with its title
        static_bmp = BitmapTextButton(panel, name="sppas_64")
        static_bmp.SetBorderWidth(0)
        static_bmp.SetFocusWidth(0)
        static_bmp.SetMinSize(wx.Size(min_height, min_height))

        title = sppasTitleText(panel, value=MSG_HEADER, name="title_txt")
        title.SetMinSize(wx.Size(sppasPanel.fix_size(220), min_height))

        page = sppasTitleText(panel, value=MSG_HEADER, name="page_txt")
        page.SetMinSize(wx.Size(sppasPanel.fix_size(100), min_height))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(static_bmp, 0, wx.ALIGN_CENTER | wx.LEFT, 8)
        sizer.Add(title, 1, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 8)
        sizer.Add(page, 0, wx.ALIGN_CENTER | wx.RIGHT, 8)
        panel.SetSizer(sizer)

        return panel

# ---------------------------------------------------------------------------


class sppasActionsInstallPanel(sppasPanel):
    """Create a custom panel with some action buttons.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):

        super(sppasActionsInstallPanel, self).__init__(
            parent=parent,
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.NO_BORDER,
            name="actions")

        settings = wx.GetApp().settings

        # Create the action panel and sizer
        self.SetMinSize(wx.Size(-1, settings.action_height))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        log_btn = self._create_button(MSG_ACTION_VIEWLOGS, "view_log")
        back_btn = self._create_button(MSG_ACTION_BACK, "arrow_left")
        back_btn.Enable(False)
        next_btn = self._create_button(MSG_ACTION_NEXT, "arrow_right")
        install_btn = self._create_button(MSG_ACTION_INSTALL, "install")
        install_btn.Enable(False)
        cancel_btn = self._create_button(MSG_ACTION_CANCEL, "cancel")

        sizer.Add(log_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self._vert_line(), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(back_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(next_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(self._vert_line(), 0, wx.ALL | wx.EXPAND, 0)
        sizer.Add(install_btn, 1, wx.ALL | wx.EXPAND, 0)
        sizer.Add(cancel_btn, 1, wx.ALL | wx.EXPAND, 0)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def EnableBack(self, value):
        self.FindWindow("arrow_left").Enable(value)

    def EnableNext(self, value):
        self.FindWindow("arrow_right").Enable(value)

    def EnableInstall(self, value):
        self.FindWindow("install").Enable(value)

    def CancelToExit(self):
        btn = self.FindWindow("cancel")
        btn.SetLabel(MSG_ACTION_EXIT)
        btn.Refresh()

    # -----------------------------------------------------------------------

    def _create_button(self, text, icon):
        btn = BitmapTextButton(self, label=text, name=icon)
        h = self.get_font_height()

        btn.SetLabelPosition(wx.RIGHT)
        btn.SetFocusStyle(wx.PENSTYLE_SOLID)
        btn.SetFocusWidth(h//4)
        btn.SetFocusColour(self.GetForegroundColour())
        btn.SetSpacing(sppasPanel.fix_size(h//2))
        btn.SetMinSize(wx.Size(h*10, h*2))

        return btn

    # ------------------------------------------------------------------------

    def _vert_line(self):
        """Return a vertical static line."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(1, -1))
        line.SetSize(wx.Size(1, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(1)
        return line

# ---------------------------------------------------------------------------


class sppasHomeInstallPanel(sppasPanel):
    """Create a panel to display a welcome message when installing.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasHomeInstallPanel, self).__init__(
            parent=parent,
            name="page_home",
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        sppasPanel.SetFont(self, font)
        self.FindWindow("title").SetFont(wx.GetApp().settings.header_text_font)
        self.Layout()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        h = self.get_font_height()
        title = "{:s} - {:s}".format(sg.__name__, sg.__title__)
        # Create a title
        st = sppasTitleText(self, value=title)
        st.SetName("title")
        st.SetMinSize(wx.Size(len(title)*h*2, h*2))

        # Create the welcome message
        txt = sppasMessageText(self, INFO_WELCOME)

        sppas_logo = TextButton(self, label=sg.__url__, name="sppas_web")
        sppas_logo.SetMinSize(wx.Size(sppasPanel.fix_size(200), -1))
        sppas_logo.SetBorderWidth(0)
        sppas_logo.SetAlign(wx.ALIGN_CENTER)

        # Organize the title and message
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(st, 2, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, h)
        sizer.Add(txt, 3, wx.EXPAND | wx.BOTTOM, h)
        sizer.Add(sppas_logo, 0, wx.ALIGN_CENTER_HORIZONTAL)
        sizer.AddStretchSpacer(1)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events."""
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()

        if event_obj.GetName() == "sppas_web":
            webbrowser.open(sg.__url__)
        else:
            event.Skip()

# ---------------------------------------------------------------------------


class sppasLicenseInstallPanel(sppasPanel):
    """Create a panel to display a welcome message when installing.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasLicenseInstallPanel, self).__init__(
            parent=parent,
            name="page_license",
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self._create_content()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        msg = sppasStaticText(self, label=INFO_LICENSE)
        scp = sppasScrolledPanel(self)

        s = wx.BoxSizer()
        license_text = list()
        try:
            with open(os.path.join(paths.sppas, "COPYRIGHT.txt"), "r") as fp:
                license_text = fp.readlines()
        except Exception as e:
            logging.error(e)
            license_text.append(LICENSE)
        text = sppasMessageText(scp, "".join(license_text))
        s.Add(text, 1, wx.EXPAND)
        scp.SetSizer(s)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(msg, 0, wx.ALL | wx.EXPAND, sppasPanel.fix_size(12))
        sizer.Add(scp, 1, wx.LEFT | wx.TOP | wx.EXPAND, sppasPanel.fix_size(12))
        scp.SetupScrolling(scroll_x=True, scroll_y=True)

        self.SetSizer(sizer)

# ---------------------------------------------------------------------------


class sppasFeaturesInstallPanel(sppasScrolledPanel):
    """Create a panel to select the features to enable.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, name, installer=None, ft=None):
        super(sppasFeaturesInstallPanel, self).__init__(
            parent=parent, name=name,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self.__installer = installer
        self._feat_type = ft
        self._create_content()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)
        self.SetupScrolling(scroll_x=True, scroll_y=True)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selected_item)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_deselected_item)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        if self.__installer is None:
            sppasStaticText(self, label="Error: no installer is defined")
            return

        if self._feat_type == "deps":
            msg1 = sppasStaticText(self, label=INFO_FEATURES_DEPS)
        elif self._feat_type == "lang":
            msg1 = sppasStaticText(self, label=INFO_FEATURES_LANG)
        elif self._feat_type == "annot":
            msg1 = sppasStaticText(self, label=INFO_FEATURES_ANNOT)
        else:
            msg1 = sppasStaticText(self, label=INFO_FEATURES_ALL)

        msg2 = sppasStaticText(self, label=INFO_FEATURES)
        lst, descr = self.__create_feats_list(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(msg1, 0, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        sizer.Add(msg2, 0, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        sizer.Add(lst, 0, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        sizer.Add(descr, 1, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))

        self.SetSizer(sizer)

    def __create_feats_list(self, parent):
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_AUTO_URL | wx.NO_BORDER
        txtctrl = sppasTextCtrl(parent, style=style, name="descr_textctrl")
        lst = CheckListCtrl(parent,
                            style=wx.LC_REPORT | wx.LC_HRULES,
                            name="features_list")
        lst.AppendColumn(MSG_FEAT, wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(80))
        lst.AppendColumn(MSG_DESCR, wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(380))
        nb = 0
        if self.__installer is not None:
            for fid in self.__installer.features_ids(self._feat_type):
                txtctrl.AppendText("\n" + fid + "\n")
                txtctrl.AppendText(self.__installer.description(fid) + "\n")
                idx = lst.InsertItem(lst.GetItemCount(), fid)
                lst.SetItem(idx, 1, self.__installer.brief(fid))
                if self.__installer.enable(fid) is True:
                    lst.Select(idx, on=True)
                nb += 1

        if nb == 0:
            idx = lst.InsertItem(lst.GetItemCount(), " --- ")
            lst.SetItem(idx, 1, "No features of this type are defined")

        return lst, txtctrl

    # ------------------------------------------------------------------------

    @property
    def features_list(self):
        return self.FindWindow("features_list")

    # ------------------------------------------------------------------------

    def _on_selected_item(self, evt):
        index = evt.GetIndex()
        fid = self.features_list.GetItemText(index, 1)
        if self.__installer is not None:
            self.__installer.enable(fid, True)
        logging.info("Installation of feature {} enabled".format(fid))

    def _on_deselected_item(self, evt):
        index = evt.GetIndex()
        fid = self.features_list.GetItemText(index, 1)
        if self.__installer is not None:
            self.__installer.enable(fid, False)
        logging.info("Installation of feature {} disabled".format(fid))

# ---------------------------------------------------------------------------


class sppasFeaturesInstallDepsPanel(sppasFeaturesInstallPanel):
    """Create a panel to select the features of type deps to enable.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, installer=None):
        super(sppasFeaturesInstallDepsPanel, self).__init__(
            parent=parent, name="page_features_deps",
            installer=installer, ft="deps")

# ---------------------------------------------------------------------------


class sppasReadyInstallPanel(sppasPanel):
    """Create a panel to display a welcome message when installing.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasReadyInstallPanel, self).__init__(
            parent=parent,
            name="page_ready",
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self._create_content()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""

        msg = sppasMessageText(self, INFO_READY)
        sizer = wx.BoxSizer()
        sizer.Add(msg, 1, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        self.SetSizer(sizer)

# ---------------------------------------------------------------------------


class sppasTerminatedInstallPanel(sppasPanel):
    """Create a panel to display a welcome message when installing.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, message=INFO_INSTALL_FINISHED):
        super(sppasTerminatedInstallPanel, self).__init__(
            parent=parent,
            name="page_terminate",
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self.__message = message
        self._create_content()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------

    def SetMessage(self, text):
        self.__message = text

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        msg1 = sppasMessageText(self, self.__message)
        msg2 = sppasMessageText(self, INFO_SHARE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(msg1, 1, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        sizer.Add(msg2, 1, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        self.SetSizer(sizer)

