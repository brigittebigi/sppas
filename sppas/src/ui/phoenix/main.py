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

    ui.phoenix.main.py
    ~~~~~~~~~~~~~~~~~~

This is the main application for SPPAS, based on the Phoenix API.
Create and run the application:

>>> app = sppasApp()
>>> app.run()

"""
import wx
import logging
from os import path, getcwd
from argparse import ArgumentParser

from sppas.src.config import sg
from sppas.src.config import sppasBaseSettings

# ---------------------------------------------------------------------------
# Wx global settings
# ---------------------------------------------------------------------------


class WxAppConfig(sppasBaseSettings):
    """Manage the application global settings.

    Config is represented in a non-iterable dictionary.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self):
        """Create the dictionary of wx settings."""
        super(WxAppConfig, self).__init__()

        self.__dict__ = dict(
            name=sg.__name__ + " " + sg.__version__,
            log_level=15,
            log_file=None,
        )

    def set(self, key, value):
        """Set a new value to a key."""
        self.__dict__[key] = value

# ---------------------------------------------------------------------------


class WxAppSettings(sppasBaseSettings):
    """Manage the application global settings for look&feel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self):
        """Create the dictionary of settings."""
        super(WxAppSettings, self).__init__()

    # -----------------------------------------------------------------------

    def load(self):
        """Load the dictionary of settings from a json file."""
        self.reset()

    # -----------------------------------------------------------------------

    def reset(self):
        """Fill the dictionary with the default values."""
        title_font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        title_font = title_font.Bold()
        title_font = title_font.Scale(2.)

        button_font = wx.Font(12,  # point size
                              wx.FONTFAMILY_DEFAULT,  # family,
                              wx.FONTSTYLE_NORMAL,    # style,
                              wx.FONTWEIGHT_NORMAL,   # weight,
                              underline=False,
                              faceName="Calibri",
                              encoding=wx.FONTENCODING_SYSTEM)

        self.__dict__ = dict(
            frame_style=wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX,
            frame_width=640,
            frame_height=480,
            fg_color=wx.Colour(250, 250, 240, alpha=wx.ALPHA_OPAQUE),
            bg_color=wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE),
            title_height=64,
            title_fg_color=wx.Colour(95, 95, 90, alpha=wx.ALPHA_OPAQUE),
            title_bg_color=wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE),
            title_text_font=title_font,
            button_text_font=button_font,
            button_fg_color=wx.Colour(250, 250, 240, alpha=wx.ALPHA_OPAQUE),
            button_bg_color=wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE),
            text_font=wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        )

# ---------------------------------------------------------------------------


class sppasFrame(wx.Frame):
    """Create my own frame. Inherited from the wx.Frame."""

    def __init__(self):
        wx.Frame.__init__(self,
                          None,
                          title=wx.GetApp().GetAppDisplayName(),
                          style=wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX)
        self.SetMinSize((300, 200))
        self.SetSize(wx.Size(640, 480))

        # create a sizer to add and organize objects
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        # add a customized menu (instead of a traditional menu+toolbar)
        menus = sppasMenuPanel(self)
        top_sizer.Add(menus, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # separate menu and the rest with a line
        line_top = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line_top, 0, wx.ALL | wx.EXPAND, 0)

        # add a panel for the message
        msg_panel = sppasMessagePanel(self)
        top_sizer.Add(msg_panel, 3, wx.ALL | wx.EXPAND, 0)

        # separate top and the rest with a line
        line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line, 0, wx.ALL | wx.EXPAND, 0)

        # add some action buttons
        actions = sppasActionPanel(self)
        top_sizer.Add(actions, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Associate a handler function with the EVT_BUTTON event.
        # That means that when a button is clicked then the process
        # handler function will be called.
        self.Bind(wx.EVT_BUTTON, self.process_event)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        self.SetAutoLayout(True)
        self.SetSizer(top_sizer)
        self.Layout()

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()
        event_id = event_obj.GetId()

        wx.LogMessage("Received event id {:d} of {:s}"
                      "".format(event_id, event_name))

        if event_name == "exit":
            self.exit()
        elif event_name == "log":
            self.enable_log(event_obj)
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def enable_log(self, button):
        """Show/Hide the log frame.

        :param button: (wx.Button) Action button to show/hide the log window

        """
        if button.GetLabel() == "Show Log":
            button.SetLabel("Hide Log")
            button.Refresh()
            wx.GetApp().log_window.Show(True)
        else:
            button.SetLabel("Show Log")
            button.Refresh()
            wx.GetApp().log_window.Show(False)

    # -----------------------------------------------------------------------

    def exit(self):
        """Close the frame, terminating the application."""
        self.Close(True)

# ---------------------------------------------------------------------------


class sppasTitleText(wx.StaticText):
    """Create a title."""
    def __init__(self, parent, label):
        super(sppasTitleText, self).__init__(parent, label=label, style=wx.ALIGN_CENTER)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetFont(settings.title_text_font)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetForegroundColour(settings.title_fg_color)

# ---------------------------------------------------------------------------


class sppasMenuPanel(wx.Panel):
    """Create my own menu panel with several action buttons.
    It aims to replace the old-style menus.

    """
    def __init__(self, parent):
        super(sppasMenuPanel, self).__init__(parent)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.title_bg_color)
        self.SetMinSize((-1, settings.title_height))

        menu_sizer = wx.BoxSizer(wx.HORIZONTAL)
        st = sppasTitleText(self, "Installation error...")
        menu_sizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=10)

        self.SetSizer(menu_sizer)
        self.SetAutoLayout(True)
        self.Show(True)

# ---------------------------------------------------------------------------


class sppasMessagePanel(wx.Panel):
    """Create my own panel to work with files.

    """
    def __init__(self, parent):
        super(sppasMessagePanel, self).__init__(parent)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.bg_color)

        message = \
            "Welcome to {:s}!\n\n"\
            "{:s} requires wxpython version 3 but version 4 is installed.\n"\
            "The Graphical User Interface can't work. See the installation "\
            "web page for details: {:s}." \
            "".format(sg.__longname__, sg.__name__, sg.__url__)
        text_style = wx.TAB_TRAVERSAL|\
                     wx.TE_MULTILINE|\
                     wx.TE_READONLY|\
                     wx.TE_BESTWRAP|\
                     wx.TE_AUTO_URL|\
                     wx.NO_BORDER
        txt = wx.TextCtrl(self, wx.ID_ANY,
                          value=message,
                          style=text_style)
        font = settings.text_font
        txt.SetFont(font)
        txt.SetForegroundColour(settings.fg_color)
        txt.SetBackgroundColour(settings.bg_color)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(txt, 1, wx.ALL|wx.EXPAND, border=10)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Show(True)

# ---------------------------------------------------------------------------


class sppasButton(wx.Button):
    """Create a button. Inherited from the wx.Button."""
    def __init__(self, parent, label, name):

        wx.Button.__init__(self,
                           parent,
                           wx.ID_ANY,
                           label,
                           style=wx.BORDER_NONE,
                           name=name)

        settings = wx.GetApp().settings
        # Fix Look&Feel
        self.SetForegroundColour(settings.button_fg_color)
        self.SetBackgroundColour(settings.button_bg_color)
        self.SetFont(settings.button_text_font)

# ---------------------------------------------------------------------------


class sppasActionPanel(wx.Panel):
    """Create my own panel with some action buttons.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        settings = wx.GetApp().settings
        self.SetMinSize((-1, 32))
        self.SetBackgroundColour(settings.bg_color)

        exit_btn = sppasButton(self, "Exit", name="exit")
        log_btn = sppasButton(self, "Show Log", name="log")

        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer.Add(exit_btn, 4, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(log_btn, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(action_sizer)

        self.Bind(wx.EVT_BUTTON, self.OnAction, exit_btn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, log_btn)

    # -----------------------------------------------------------------------

    def OnAction(self, event):
        """A button was clicked.

        Here we just send the event to the parent.

        """
        wx.PostEvent(self.GetTopLevelParent(), event)

# ---------------------------------------------------------------------------


class sppasLogTarget(wx.Log):
    """Allows to manage wx log targets.

    wx.Log messages are also printed in the python logging console.

    """
    WXLOG_TO_PYLOG = {
        wx.LOG_FatalError: logging.critical,
        wx.LOG_Error: logging.error,
        wx.LOG_Warning: logging.warning,
        wx.LOG_Message: logging.info,
        wx.LOG_Status: logging.info,
        wx.LOG_Info: logging.info,
        wx.LOG_Debug: logging.debug,
    }

    def DoLogRecord(self, level, msg, info=None):
        sppasLogTarget.WXLOG_TO_PYLOG[level]('[wx] ' + msg)

# ---------------------------------------------------------------------------


class sppasLogFrame(wx.Frame):
    """Create my own log frame. Inherited from the wx.Frame."""

    def __init__(self, parent, title):
        super(sppasLogFrame, self).__init__(
            parent,
            title=title,
            style=wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX)
        self.SetMinSize((300, 200))
        self.SetSize(wx.Size(640, 480))

        settings = wx.GetApp().settings
        text_style = wx.TAB_TRAVERSAL|\
                     wx.TE_MULTILINE|\
                     wx.TE_READONLY|\
                     wx.TE_BESTWRAP|\
                     wx.TE_AUTO_URL|\
                     wx.NO_BORDER
        self.txt = wx.TextCtrl(self, wx.ID_ANY, value="",
                               style=text_style)
        font = settings.text_font
        self.txt.SetFont(font)
        self.txt.SetForegroundColour(settings.fg_color)
        self.txt.SetBackgroundColour(settings.bg_color)

        # Associate a handler function with the EVT_BUTTON event.
        # That means that when a button is clicked then the process
        # handler function will be called.
        self.Bind(wx.EVT_CLOSE, self.on_exit)
        self.Show(False)

    def get_logtextctrl(self):
        return self.txt

    def on_exit(self, event):
        pass

class sppasLogTextCtrl(wx.LogTextCtrl):
    WXLOG_TO_PYLOG = {
        wx.LOG_FatalError: logging.critical,
        wx.LOG_Error: logging.error,
        wx.LOG_Warning: logging.warning,
        wx.LOG_Message: logging.info,
        wx.LOG_Status: logging.info,
        wx.LOG_Info: logging.info,
        wx.LOG_Debug: logging.debug,
    }

    def __init__(self, textctrl):
        super(sppasLogTextCtrl, self).__init__(textctrl)

    def DoLogRecord(self, level, msg, info=None):
        """Override."""
        # Send the message to the python logging
        msg = '[wxPython] ' + msg
        sppasLogTextCtrl.WXLOG_TO_PYLOG[level](msg)
        # Show the message into the wx.TextCtrl
        wx.LogTextCtrl.DoLogRecord(self, level, msg, info)

# ---------------------------------------------------------------------------


class sppasApp(wx.App):
    """Create the SPPAS Phoenix application."""

    def __init__(self):

        # Create members
        self.cfg = WxAppConfig()
        self.settings = None
        self.log_window = None
        self.frame = None

        # Initialize the wx application
        wx.App.__init__(self,
                        redirect=False,
                        filename=self.cfg.log_file,
                        useBestVisual=True,
                        clearSigInt=True)

        self.SetAppName(self.cfg.name)
        self.SetAppDisplayName(self.cfg.name)

        # Fix language and translation
        lang = wx.LANGUAGE_DEFAULT
        self.locale = wx.Locale(lang)

        # Fix wx settings and logging
        self.settings = WxAppSettings()
        self.process_command_line_args()
        self.setup_logging()

    # -----------------------------------------------------------------------

    def process_command_line_args(self):
        """Process the command line...

        This is an opportunity for users to fix some args: a list of files.

        """
        # create a parser for the command-line arguments
        parser = ArgumentParser(
            usage="{:s}".format(path.basename(__file__)),
            description="... " + sg.__longname__)

        # add arguments here
        parser.add_argument("files", nargs="*", help='Input audio file name(s)')
        parser.add_argument("-l", "--log_level",
                            required=False,
                            type=int,
                            default=self.cfg.log_level,
                            help='Log level (default=15).')

        # then parse
        args = parser.parse_args()

        # and do things with arguments
        if args.log_level:
            self.cfg.set('log_level', args.log_level)

        filenames = []
        for f in args.files:
            p, b = path.split(f)
            if not p:
                p = getcwd()
            filenames.append(path.abspath(path.join(p, b)))

        return filenames

    # -----------------------------------------------------------------------

    def setup_logging(self):
        """Setup the logging.

        Fix the level of messages and where to redirect them.

        """
        # Fix the format of the messages
        formatmsg = "%(asctime)s [%(levelname)s] %(message)s"

        # Setup logging to stderr
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(formatmsg))
        handler.setLevel(self.cfg.log_level)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(self.cfg.log_level)

        # Show a welcome!
        logging.info("Logging set up level={:d}".format(self.cfg.log_level))

        # Fix wx log messages
        wx.Log.EnableLogging(True)
        wx.Log.SetLogLevel(self.cfg.log_level)

        # a background log window: it collects all log messages in the log
        # frame which it manages but also passes them on to the log target
        # which was active at the moment of its creation.
        self.log_window = sppasLogFrame(None,
                                        '{:s} Log Window'.format(sg.__name__))
        wx.Log.SetActiveTarget(sppasLogTextCtrl(self.log_window.get_logtextctrl()))

    # -----------------------------------------------------------------------

    def run(self):
        # here we could fix things like:
        #  - is first launch? No? so create config! and/or display a welcome msg!
        #  - fix config dir,
        #  - etc
        self.create_application()
        self.MainLoop()

    # -----------------------------------------------------------------------

    def create_application(self):
        """Create the main frame of the application and show it."""
        self.frame = sppasFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show(True)

    # -----------------------------------------------------------------------

    def OnExit(self):
        """Optional. Override the already existing method to kill the app.

        This method is invoked when the user:

            - clicks on the [X] button of the frame manager
            - does "ALT-F4" (Windows) or CTRL+X (Unix)

        """
        logging.debug('OnExit the wx.App.')
        # then it will exit. Nothing special to do. Return the exit status.
        return 0
