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

    ui.phoenix.main_log.py
    ~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.lib.newevent
import logging

from sppas.src.config import sg
from sppas.src.config import msg
from sppas.src.utils import u
from sppas.src.utils import sppasTime

from ..logs import sppasLogFile

from .tools import sppasSwissKnife
from .windows import sppasStaticLine
from .windows import sppasPanel
from .windows import sppasStaticText
from .windows import BitmapTextButton
from .dialogs import Feedback

# ----------------------------------------------------------------------------


# event used to send a logging record to a wx object
wxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()

# match between wx log levels and python log level names
match_levels = {
    wx.LOG_FatalError: 'CRITICAL',
    wx.LOG_Error: 'ERROR',
    wx.LOG_Warning: 'WARNING',
    wx.LOG_Info: 'INFO',
    wx.LOG_Message: 'INFO',
    wx.LOG_Debug: 'DEBUG'
}

# ----------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_HEADER_LOG = _("Log Window")
MSG_ACTION_CLEAR = _("Clear")
MSG_ACTION_SAVE = _("Save")
MSG_ACTION_SEND = _("Send feedback")
MSG_ADD_COMMENT = _("Add comments here")

# ----------------------------------------------------------------------------


def log_level_to_wx(log_level):
    """Convert a python logging log level to a wx one.

    From python logging log levels:

        50 - CRITICAL
        40 - ERROR
        30 - WARNING
        20 - INFO
        10 - DEBUG
        0 - NOTSET

    To wx log levels:

        0 - LOG_FatalError 	program can’t continue, abort immediately
        1 - LOG_Error 	a serious error, user must be informed about it
        2 - LOG_Warning user is normally informed about it but may be ignored
        3 - LOG_Message normal message (i.e. normal output of a non GUI app)
        4 - LOG_Status 	informational: might go to the status line of GUI app
        5 - LOG_Info 	informational message (a.k.a. ‘Verbose’)
        6 - LOG_Debug 	never shown to the user, disabled in release mode
        7 - LOG_Trace 	trace messages are also only enabled in debug mode
        8 - LOG_Progress 	used for progress indicator (not yet)
        100 - LOG_User 	user defined levels start here
        10000 LOG_Max

    :param log_level: (int) python logging log level
    :returns: (int) wx log level

    """
    if log_level == logging.CRITICAL:
        return wx.LOG_Message
    if log_level <= 10:
        return wx.LOG_Debug
    if log_level <= 20:
        return wx.LOG_Info
    if log_level <= 30:
        return wx.LOG_Warning
    if log_level <= 40:
        return wx.LOG_Error
    return wx.LOG_FatalError

# ---------------------------------------------------------------------------


class sppasHandlerToWx(logging.Handler):
    """Logging handler class which sends log strings to a wx object.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, wx_dest=None):
        """Initialize the handler.

        :param wx_dest: (wx.Window) destination object to post the event to

        """
        super(sppasHandlerToWx, self).__init__()

        if isinstance(wx_dest, wx.Window) is False:
            raise TypeError('Expected a wx.Window but got {} instead.'
                            ''.format(type(wx_dest)))
        self.wx_dest = wx_dest

    # -----------------------------------------------------------------------

    def flush(self):
        """Override. Do nothing for this handler."""
        pass

    # -----------------------------------------------------------------------

    def emit(self, record):
        """Override. Emit a record.

        :param record: (logging.LogRecord)

        """
        try:
            # the log event sends the record to the destination wx object
            event = wxLogEvent(record=record)
            wx.PostEvent(self.wx_dest, event)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

# ---------------------------------------------------------------------------


class sppasLogWindow(wx.TopLevelWindow):
    """Create a log window for SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    A background log window: it collects all log messages in the log
    frame which it manages but also collect them from the log target
    which was active at the moment of its creation.

    This window does not receive EVT_CLOSE.

    """

    def __init__(self, parent, log_level=0):
        """Create the frame to display log messages.

        :param parent: (wx.Window)
        :param log_level: (int)

        Log levels:

            - CRITICAL 	50
            - ERROR 	40
            - WARNING 	30
            - INFO 	    20
            - DEBUG 	10
            - NOTSET 	0

        """
        super(sppasLogWindow, self).__init__(
            parent=parent,
            title='{:s} Log'.format(sg.__name__),
            style=wx.CAPTION | wx.RESIZE_BORDER)

        # To fade-in and fade-out the opacity
        self.opacity_in = 0
        self.opacity_out = 255
        self.deltaN = -3

        # Members
        self.handler = sppasHandlerToWx(self)
        self.txt = None
        self.log_file = sppasLogFile()
        self._init_infos()

        # Fix frame content and actions
        self._create_content()
        self._setup_wx_logging(log_level)
        self._setup_events()
        self.SetAutoLayout(True)
        self._fade_in()
        self.Show(True)

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the log frame.

        Set the title, the icon and the properties of the frame.

        """
        settings = wx.GetApp().settings

        # Fix frame properties
        self.SetMinSize(wx.Size(320, 200))
        w = int(settings.frame_size[0] * 0.7)
        h = int(settings.frame_size[1] * 0.7)
        self.SetSize(wx.Size(w, h))
        self.SetName('sppas_log_frm')

        # icon
        _icon = wx.Icon()
        bmp = sppasSwissKnife.get_bmp_icon("sppas_64", height=64)
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

        # colors & font
        try:
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the frame.

        Content is made of a title, the log textctrl and action buttons.

        """
        # create a sizer to add and organize objects
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        # add a customized title and separate title and the rest with a line
        title = sppasLogTitlePanel(self)
        title.SetName('header')
        top_sizer.Add(title, 0, wx.EXPAND, 0)
        top_sizer.Add(self.HorizLine(self), 0, wx.ALL | wx.EXPAND, 0)

        # add a panel for the messages
        msg_panel = sppasLogMessagePanel(
            parent=self,
            header=self.log_file.get_header())
        msg_panel.SetName('content')
        top_sizer.Add(msg_panel, 3, wx.EXPAND, 0)
        self.txt = msg_panel.txt

        # separate top and the rest with a line
        top_sizer.Add(self.HorizLine(self), 0, wx.ALL | wx.EXPAND, 0)

        # add some action buttons
        actions = sppasLogActionPanel(self)
        actions.SetName('actions')
        top_sizer.Add(actions, 0, wx.EXPAND, 0)

        # Layout the content
        self.SetSizer(top_sizer)
        self.Layout()

    # ------------------------------------------------------------------------

    def HorizLine(self, parent, depth=3):
        """Return an horizontal static line."""
        line = sppasStaticLine(parent, orient=wx.LI_HORIZONTAL)
        line.SetMinSize(wx.Size(-1, depth))
        line.SetSize(wx.Size(-1, depth))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        return line

    # -----------------------------------------------------------------------

    def _setup_wx_logging(self, log_level):
        """Setup the logging.

        Fix the level of messages and where to redirect them.

        :param log_level: (int) Python logging log level.

        """
        # python log level
        self.handler.setLevel(log_level)

        # fix wx log messages
        wx.Log.EnableLogging(True)
        wx.Log.SetLogLevel(log_level_to_wx(log_level))
        wx.Log.SetActiveTarget(sppasLogTextCtrl(self.txt))

        # redirect python logging messages to wx.Log
        self.redirect_logging()

        # test if everything is ok
        logging.debug('This is how a debug message looks like. ')
        logging.info('This is how an information message looks like.')
        logging.warning('This is how a warning message looks like.')
        logging.error('This is how an error message looks like.')

    # -----------------------------------------------------------------------

    def _fade_in(self):
        """Fade-in opacity."""
        self.SetTransparent(self.opacity_in)
        self.timer1 = wx.Timer(self, -1)
        self.timer1.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_in, self.timer1)

    # ---------------------------------------------------------------------------

    def __alpha_cycle_in(self, *args):
        """Fade-in opacity of the dialog."""
        self.opacity_in += self.deltaN
        if self.opacity_in <= 0:
            self.deltaN = -self.deltaN
            self.opacity_in = 0

        if self.opacity_in >= 255:
            self.deltaN = -self.deltaN
            self.opacity_in = 255
            self.timer1.Stop()

        self.SetTransparent(self.opacity_in)

    # -----------------------------------------------------------------------
    # Events
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind close event from the close dialog 'x' on the frame
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Bind the log event
        self.Bind(EVT_WX_LOG_EVENT, self.on_log_event)

        # Bind all events from our buttons
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()
        event_id = event_obj.GetId()

        wx.LogMessage("Log frame received event id {:d} of {:s}"
                      "".format(event_id, event_name))

        if event_name == "save_log":
            self.save()

        elif event_name == "broom":
            self.clear()

        elif event_name == "mail-at":
            self.feedback()

        else:
            event.Skip()

    # -----------------------------------------------------------------------
    # Callbacks to events
    # -----------------------------------------------------------------------

    def on_close(self, event):
        """Cancel the availability to close the frame, iconize instead.

        :param event: (wxEvent) unused

        """
        wx.LogMessage("Attempt to close {:s}.".format(self.GetName()))
        self.Iconize(True)
        event.StopPropagation()

    # -----------------------------------------------------------------------

    def on_log_event(self, event):
        """Add event.message to the textctrl.

        :param event: (wxLogEvent)

        """
        levels = {
            'DEBUG': wx.LogDebug,
            'INFO': wx.LogMessage,
            'WARNING': wx.LogWarning,
            'ERROR': wx.LogError,
            'CRITICAL': wx.LogFatalError
        }
        try:
            levels[event.record.levelname](event.record.message)
        except AttributeError:
            # we received a log record without message...
            pass
        event.Skip()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def redirect_logging(self, redirect=True):
        """Stop/Start the python logging redirection to this frame.

        :param redirect: (bool) redirect python logging to wx, or not

        """
        if redirect is False:
            logging.getLogger().removeHandler(self.handler)
            logging.info('Python logging messages are directed to stderr.')
        else:
            logging.getLogger().addHandler(self.handler)
            logging.info('Python logging messages are redirected to wxLog.')

    # -----------------------------------------------------------------------

    def focus(self):
        """Assign the focus to the log frame."""
        if self.IsIconized():
            self.Iconize(False)
        self.SetFocus()
        self.Raise()

    # -----------------------------------------------------------------------

    def save(self):
        """Save the messages in the current log file."""
        self.txt.SaveFile(self.log_file.get_filename())
        self.clear()
        self.txt.AppendText('Previous messages were saved in : {:s}\n'
                            ''.format(self.log_file.get_filename()))
        self.log_file.increment()

    # -----------------------------------------------------------------------

    def clear(self):
        """Clear all messages (irreversible, the messages are deleted)."""
        self.txt.Clear()
        self.txt.AppendText(self.log_file.get_header())

    # -----------------------------------------------------------------------

    def feedback(self):
        """Send log messages to the author."""
        text = MSG_ADD_COMMENT + "\n\n" + self.txt.GetValue()
        Feedback(self, text)

    # -----------------------------------------------------------------------
    # GUI
    # -----------------------------------------------------------------------

    def UpdateUI(self):
        """Apply settings to all panels and refresh."""
        # apply new (or not) 'wx' values to content.
        p = self.FindWindow("content")
        p.SetBackgroundColour(wx.GetApp().settings.bg_color)
        p.SetForegroundColour(wx.GetApp().settings.fg_color)
        p.SetFont(wx.GetApp().settings.text_font)

        # apply new (or not) 'wx' values to header.
        p = self.FindWindow("header")
        p.SetBackgroundColour(wx.GetApp().settings.header_bg_color)
        p.SetForegroundColour(wx.GetApp().settings.header_fg_color)
        p.SetFont(wx.GetApp().settings.header_text_font)

        # apply new (or not) 'wx' values to actions.
        p = self.FindWindow("actions")
        p.SetBackgroundColour(wx.GetApp().settings.action_bg_color)
        p.SetForegroundColour(wx.GetApp().settings.action_fg_color)
        p.SetFont(wx.GetApp().settings.action_text_font)

        self.Refresh()

# ---------------------------------------------------------------------------


class sppasLogTextCtrl(wx.LogTextCtrl):
    """Create a textctrl to display log messages.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, textctrl):
        """Initialize a sppasLogTextCtrl.

        :param textctrl: (sppasMessageTextCtrl) a wx.TextCtrl with
        some specific styles to display logs.

        """
        super(sppasLogTextCtrl, self).__init__(textctrl)
        self.textctrl = textctrl

    # -----------------------------------------------------------------------

    def DoLogRecord(self, level, msg, info=None):
        """Override. Called to log a new record.

        :param level: (wx.LogLevel)
        :param msg: (string)
        :param info: (wx.LogRecordInfo)

        Display the message with colors.

        """
        if not self:
            return
        # Display time with the default color
        self.textctrl.SetDefaultStyle(self.textctrl.default)
        self.textctrl.write("{:s} ".format(sppasTime().now[:-6]))

        # Display the log level name and message with colors
        if level == wx.LOG_Error or level == wx.LOG_FatalError:
            self.textctrl.SetDefaultStyle(self.textctrl.error)

        elif level == wx.LOG_Warning:
            self.textctrl.SetDefaultStyle(self.textctrl.warning)

        elif level in (wx.LOG_Info, wx.LOG_Message, wx.LOG_Status):
            self.textctrl.SetDefaultStyle(self.textctrl.default)

        else:
            self.textctrl.SetDefaultStyle(self.textctrl.debug)

        level_name = "[{:s}]".format(match_levels[level])
        self.textctrl.write("{0: <10}".format(level_name))
        self.textctrl.write("{:s}\n".format(msg))

# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------


class sppasLogTitlePanel(sppasPanel):
    """Create a panel to include the frame title.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasLogTitlePanel, self).__init__(
            parent,
            style=wx.TAB_TRAVERSAL | wx.BORDER_NONE | wx.CLIP_CHILDREN)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetMinSize(wx.Size(-1, settings.title_height))
        self.SetBackgroundColour(wx.GetApp().settings.header_bg_color)
        self.SetForegroundColour(wx.GetApp().settings.header_fg_color)
        self.SetFont(wx.GetApp().settings.header_text_font)

        # Create the title
        st = wx.StaticText(self, label=MSG_HEADER_LOG)

        # Put the title in a sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(st, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)

        self.SetSizer(sizer)

# ---------------------------------------------------------------------------


class sppasMessageTextCtrl(wx.TextCtrl):
    """Create a static text.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font, foreground and background are taken from the application settings.

    """

    text_style = wx.TAB_TRAVERSAL | \
                 wx.TE_MULTILINE | \
                 wx.TE_READONLY | \
                 wx.TE_BESTWRAP | \
                 wx.TE_AUTO_URL | \
                 wx.NO_BORDER | wx.TE_RICH

    def __init__(self, parent, value):
        super(sppasMessageTextCtrl, self).__init__(
            parent=parent,
            value=value,
            style=sppasMessageTextCtrl.text_style
        )
        self.default = wx.TextAttr()
        self.error = wx.TextAttr()
        self.warning = wx.TextAttr()
        self.debug = wx.TextAttr()

        self.ResetStyles()

        if wx.Platform == "__WXMAC__":
            self.MacCheckSpelling(False)

    # -----------------------------------------------------------------------

    def ResetStyles(self):
        # here we could create various styles (one for debug messages, one
        # for information, one for errors, etc).
        settings = wx.GetApp().settings

        # Fix Look&Feel for the new text to be added
        self.default = wx.TextAttr()
        self.default.SetTextColour(settings.fg_color)
        self.default.SetBackgroundColour(settings.bg_color)
        self.default.SetFont(settings.mono_text_font)
        self.SetDefaultStyle(self.default)

        # Fix Look&Feel for errors
        self.error = wx.TextAttr()
        self.error.SetTextColour(wx.RED)
        self.error.SetBackgroundColour(settings.bg_color)
        self.error.SetFont(settings.mono_text_font)

        # Fix Look&Feel for warnings
        self.warning = wx.TextAttr()
        self.warning.SetTextColour(wx.Colour(250, 150, 40))  # orange
        self.warning.SetBackgroundColour(settings.bg_color)
        self.warning.SetFont(settings.mono_text_font)

        # Fix Look&Feel for debug messages
        self.debug = wx.TextAttr()
        self.debug.SetTextColour(wx.LIGHT_GREY)
        self.debug.SetBackgroundColour(settings.bg_color)
        self.debug.SetFont(settings.mono_text_font)

# ---------------------------------------------------------------------------


class sppasLogMessagePanel(sppasPanel):
    """Create the panel to display log messages.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent, header=""):
        super(sppasLogMessagePanel, self).__init__(
            parent=parent,
            style=wx.TAB_TRAVERSAL | wx.BORDER_NONE | wx.CLIP_CHILDREN,
            name="content")

        settings = wx.GetApp().settings

        # create a log message, i.e. a wx textctrl
        self.txt = sppasMessageTextCtrl(self, value="")
        self.txt.AppendText(header)

        # put the text in a sizer to expand it
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.txt, 1, wx.ALL | wx.EXPAND, border=10)

        # fix this panel look&feel
        self.SetBackgroundColour(settings.bg_color)
        self.SetForegroundColour(settings.fg_color)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override. Do nothing."""
        pass

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        # reset the existing styles...
        self.txt.ResetStyles()
        self.txt.SetStyle(0, len(self.txt.GetValue()),
                          self.txt.GetDefaultStyle())

# ---------------------------------------------------------------------------


class sppasLogActionPanel(sppasPanel):
    """Create a panel with some action buttons to manage log messages.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasLogActionPanel, self).__init__(
            parent,
            style=wx.TAB_TRAVERSAL | wx.BORDER_NONE | \
                  wx.WANTS_CHARS | wx.CLIP_CHILDREN)

        # fix this panel look&feel
        settings = wx.GetApp().settings
        self.SetMinSize((-1, settings.action_height))

        # create action buttons
        clear_btn = self._create_button(MSG_ACTION_CLEAR, "broom")
        save_btn = self._create_button(MSG_ACTION_SAVE, "save_log")
        send_btn = self._create_button(MSG_ACTION_SEND, "mail-at")

        # organize buttons in a sizer
        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer.Add(clear_btn, 2, wx.ALL | wx.EXPAND, 1)
        action_sizer.Add(self.VertLine(), 0, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(save_btn, 2, wx.ALL | wx.EXPAND, 1)
        action_sizer.Add(self.VertLine(), 0, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(send_btn, 2, wx.ALL | wx.EXPAND, 1)

        self.SetBackgroundColour(wx.GetApp().settings.action_bg_color)
        self.SetForegroundColour(wx.GetApp().settings.action_fg_color)
        self.SetFont(wx.GetApp().settings.action_text_font)

        self.SetSizer(action_sizer)

    # -----------------------------------------------------------------------

    def _create_button(self, text, icon):
        btn = BitmapTextButton(self, label=text, name=icon)

        # Get the font height for the header
        h = self.get_font_height()

        btn.LabelPosition = wx.RIGHT
        btn.FocusStyle = wx.PENSTYLE_SOLID
        btn.FocusWidth = h//4
        btn.FocusColour = wx.Colour(128, 128, 128, 128)
        btn.Spacing = sppasPanel.fix_size(h//2)
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(h*10, h*2))

        return btn

    # ------------------------------------------------------------------------

    def VertLine(self):
        """Return a vertical static line."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(1, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(1)
        return line
