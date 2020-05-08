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

from sppas.src.config import sg, paths
from sppas.src.config import msg

from .windows import sppasStaticLine
from .windows import BitmapTextButton, TextButton
from .windows import ToggleButton
from .windows import sppasPanel, sppasScrolledPanel, sppasImgBgPanel
from .windows import sppasDialog
from .windows import sppasTitleText, sppasStaticText, sppasMessageText
from .windows.book import sppasSimplebook

from .windows import YesNoQuestion
from .views import About
from .main_log import sppasLogWindow

# ---------------------------------------------------------------------------


def _(message):
    return msg(message, "ui")


MSG_HEADER_INSTALL_WIZARD = _("InstallWizard of SPPAS")

MSG_ACTION_BACK = _('Back')
MSG_ACTION_NEXT = _('Next')
MSG_ACTION_INSTALL = _('Install')
MSG_ACTION_CANCEL = _('Cancel')
MSG_ACTION_VIEWLOGS = _('View logs')

MSG_CONFIRM = _("Confirm exit?")

MSG_WELCOME = _("SPPAS is a scientific computer software package developed "
                "by Brigitte Bigi, CNRS researcher at 'Laboratoire Parole et "
                "Langage', Aix-en-Provence, France.\n\n"
                "The InstallWizard will install on your computer other programs "
                "SPPAS is requiring.\nTo continue, click Next.")
MSG_LICENSE = _("Please read the following license agreement. Click Next to accept.")
MSG_FEATURES = _("Check the boxes in the list below to enable a feature installation:")
MSG_READY = _("Click Install button to begin the installation.\n\n"
              "If you want to review or change any of your installation settings, "
              "click Back. Click Cancel to exit the wizard without installing.")

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


class sppasInstallWindow(sppasDialog):
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
    pages = ("page_home", "page_license", "page_features", "page_ready")

    def __init__(self):
        super(sppasInstallWindow, self).__init__(
            parent=None,
            title=wx.GetApp().GetAppDisplayName(),
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.CAPTION |
                  wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX |
                  wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT,
            name="sppas_install_dlg")

        # Members
        self._init_infos()

        # Create the log window of the application and show it.
        self.log_window = sppasLogWindow(self, wx.GetApp().get_log_level())
        self.log_window.EnableClear(False)

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
        """Overridden. Initialize the frame.

        Set the title, the icon and the properties of the frame.

        """
        sppasDialog._init_infos(self)

        # Fix some frame properties
        self.SetMinSize(wx.Size(sppasPanel.fix_size(320), sppasPanel.fix_size(200)))
        w = int(wx.GetApp().settings.frame_size[0] * 0.8)
        h = int(wx.GetApp().settings.frame_size[1] * 0.8)
        self.SetSize(wx.Size(w, h))

        self.SetName('{:s}'.format(sg.__name__))

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the frame.

        Content is made of a menu, an area for panels and action buttons.

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
        book.SetEffectsTimeouts(150, 200)

        # 1st page: a panel with a welcome message
        book.ShowNewPage(sppasHomeInstallPanel(book))

        # 2nd: license agreement
        book.AddPage(sppasLicenseInstallPanel(book), text="")

        # 3rd: select the features to be installed
        book.AddPage(sppasFeaturesInstallPanel(book), text="")

        # 4th: ready to process install
        book.AddPage(sppasReadyInstallPanel(book), text="")

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
        event_id = event_obj.GetId()

        if event_name == "cancel":
            self.exit()

        elif event_name == "arrow_right":
            self.show_next_page(1)

        elif event_name == "arrow_left":
            self.show_next_page(-1)

        elif event_name == "view_log":
            self.log_window.focus()

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
            page_name = sppasInstallWindow.pages[0]
            self.FindWindow("header").enable(page_name)
            self.show_page(page_name)

        elif key_code == wx.WXK_DOWN and event.CmdDown():
            page_name = sppasInstallWindow.pages[-1]
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

        :param direction: (int) Positive=Next; Negative=Prev

        """
        book = self.FindWindow("content")
        c = book.GetSelection()
        wx.LogDebug("Current page index = {:d}".format(c))
        if direction > 0:
            nextc = (c+1)
            if nextc == len(sppasInstallWindow.pages):
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

        # fix actions of the new page
        if page_name == "page_home":
            self.FindWindow("actions").EnableBack(False)
        else:
            self.FindWindow("actions").EnableBack(True)

        if page_name == "page_ready":
            self.FindWindow("actions").EnableNext(False)
            self.FindWindow("actions").EnableInstall(True)
        else:
            self.FindWindow("actions").EnableNext(True)
            self.FindWindow("actions").EnableInstall(False)

        # then change to the page
        book.ChangeSelection(p)
        w.SetFocus()
        self.Layout()
        self.Refresh()

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

        img_panel = sppasImgBgPanel(self, img_name="splash_transparent", name="splash_header")
        img_panel.SetMinSize(wx.Size(-1, min_height))

        title_panel = self.__title_header()
        title_panel.SetMinSize(wx.Size(-1, min_height))

        sizer.Add(title_panel, 1, wx.EXPAND, border=0)
        sizer.Add(img_panel, 1, wx.EXPAND, border=0)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        sppasPanel.SetFont(self, font)
        self.FindWindow("title_txt").SetFont(wx.GetApp().settings.header_text_font)
        self.Layout()

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

        title = sppasTitleText(panel, value="InstallWizard of SPPAS...", name="title_txt")
        title.SetMinSize(wx.Size(sppasPanel.fix_size(280), min_height))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(static_bmp, 0, wx.ALIGN_CENTER)
        sizer.Add(title, 1, wx.ALIGN_CENTER | wx.LEFT, 8)
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

    # -----------------------------------------------------------------------

    def _create_button(self, text, icon):
        btn = BitmapTextButton(self, label=text, name=icon)
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
        txt = sppasMessageText(self, MSG_WELCOME)

        sppas_logo = TextButton(self, label="http://www.sppas.org/", name="sppas_web")
        sppas_logo.SetMinSize(wx.Size(sppasPanel.fix_size(64), -1))
        sppas_logo.SetBorderWidth(0)
        sppas_logo.SetLabelPosition(wx.TOP)

        # Organize the title and message
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(st, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, h)
        sizer.Add(txt, 1, wx.EXPAND)
        sizer.Add(sppas_logo, 1, wx.ALIGN_CENTER_HORIZONTAL)
        sizer.AddStretchSpacer(2)

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
        msg = sppasStaticText(self, label=MSG_LICENSE)
        scp = sppasScrolledPanel(self)

        s = wx.BoxSizer()
        license_text = list()
        try:
            with open(os.path.join(paths.etc, "gpl-3.0.txt"), "r") as fp:
                license_text = fp.readlines()
        except Exception as e:
            logging.error(e)
            license_text.append(LICENSE)
        text = sppasMessageText(scp, "\n".join(license_text))
        s.Add(text, 1, wx.EXPAND)
        scp.SetSizer(s)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(msg, 0, wx.ALL | wx.EXPAND, sppasPanel.fix_size(12))
        sizer.Add(scp, 1, wx.LEFT | wx.TOP | wx.EXPAND, sppasPanel.fix_size(12))
        scp.SetupScrolling(scroll_x=True, scroll_y=True)

        self.SetSizer(sizer)

# ---------------------------------------------------------------------------


class sppasFeaturesInstallPanel(sppasPanel):
    """Create a panel to display a welcome message when installing.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, installer=None):
        super(sppasFeaturesInstallPanel, self).__init__(
            parent=parent,
            name="page_features",
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self.__installer = installer
        self._create_content()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        if self.__installer is None:
            sppasStaticText(self, label="Error: no installer is defined")
            return

        feats_panel = sppasPanel(self, name="feats_panel")
        feats_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left = self.__create_feats_list(feats_panel)
        right = self.__create_descr_panel(feats_panel)
        feats_sizer.Add(left, 1, wx.EXPAND)
        feats_sizer.Add(right, 1, wx.EXPAND)
        feats_panel.SetSizer(feats_sizer)

        sizer = wx.BoxSizer(wx.VERTICAL)
        msg = sppasStaticText(self, label=MSG_FEATURES)
        sizer.Add(msg, 0, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        sizer.Add(feats_panel, 1, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        self.SetSizer(sizer)

    def __create_feats_list(self, parent):
        panel = sppasPanel(parent)
        return panel

    def __create_descr_panel(self, parent):
        panel = sppasPanel(parent)
        return panel

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
        msg = sppasMessageText(self, MSG_READY)
        sizer = wx.BoxSizer()
        sizer.Add(msg, 1, wx.ALL | wx.EXPAND, border=sppasPanel.fix_size(12))
        self.SetSizer(sizer)

