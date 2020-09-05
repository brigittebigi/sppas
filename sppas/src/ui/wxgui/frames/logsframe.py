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

    ui.wxgui.logsframe.py
    ~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import wx.lib.newevent
import logging

from sppas.src.utils.datatype import sppasTime
from sppas.src.config.logs import sppasLogFile

# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------


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


class sppasLogWindow(wx.Dialog):
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
            title='SPPAS Logging messages',
            style=wx.DEFAULT_FRAME_STYLE & ~wx.CLOSE_BOX)

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
        self.Show(True)

    # ------------------------------------------------------------------------
    # Private methods to create the GUI and initialize members
    # ------------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the log frame.

        Set the title, the icon and the properties of the frame.

        """
        # Fix frame properties
        self.SetMinSize(wx.Size(480, 420))
        self.SetSize(wx.Size(480, 420))
        self.SetName('sppaslog')

    # ------------------------------------------------------------------------

    def _create_content(self):
        """Organize all sub-anz_panels into a main panel and return it."""

        sizer = wx.BoxSizer(wx.VERTICAL)

        # add a panel for the messages
        msg_panel = sppasLogMessagePanel(
            parent=self,
            header=self.log_file.get_header())
        msg_panel.SetName('content')
        sizer.Add(msg_panel, 3, wx.EXPAND, 0)
        self.txt = msg_panel.txt

        # Layout the content
        self.SetSizer(sizer)
        self.Layout()

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
    # Events
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind the log event
        self.Bind(EVT_WX_LOG_EVENT, self.on_log_event)

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
        levels[event.record.levelname](event.record.message)
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
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        s = font.GetPointSize()
        mono_font = wx.Font(int(s * 0.9),  # point size
                            wx.FONTFAMILY_MODERN,  # family,
                            wx.FONTSTYLE_NORMAL,  # style,
                            wx.FONTWEIGHT_NORMAL,  # weight,
                            underline=False,
                            encoding=wx.FONTENCODING_SYSTEM)

        # Fix Look&Feel for the new text to be added
        self.default = wx.TextAttr()
        self.default.SetTextColour(wx.BLACK)
        self.default.SetBackgroundColour(wx.WHITE)
        self.default.SetFont(mono_font)
        self.SetDefaultStyle(self.default)

        # Fix Look&Feel for errors
        self.error = wx.TextAttr()
        self.error.SetTextColour(wx.RED)
        self.error.SetBackgroundColour(wx.WHITE)
        self.error.SetFont(mono_font)

        # Fix Look&Feel for warnings
        self.warning = wx.TextAttr()
        self.warning.SetTextColour(wx.GREEN)
        self.warning.SetBackgroundColour(wx.WHITE)
        self.warning.SetFont(mono_font)

        # Fix Look&Feel for debug messages
        self.debug = wx.TextAttr()
        self.debug.SetTextColour(wx.LIGHT_GREY)
        self.debug.SetBackgroundColour(wx.WHITE)
        self.debug.SetFont(mono_font)

# ---------------------------------------------------------------------------


class sppasLogMessagePanel(wx.Panel):
    """Create the panel to display log messages.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, header=""):
        super(sppasLogMessagePanel, self).__init__(
            parent=parent,
            style=wx.TAB_TRAVERSAL | wx.BORDER_NONE | wx.CLIP_CHILDREN,
            name="content")

        # create a log message, i.e. a wx textctrl
        self.txt = sppasMessageTextCtrl(self, value="")
        self.txt.AppendText(header)

        # put the text in a sizer to expand it
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.txt, 1, wx.ALL | wx.EXPAND, border=10)

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


class FrameTest(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, title="Test Frame")

        # Create the log window of the application and show it.
        self.log_window = sppasLogWindow(self, 0)

        self.Centre()
        self.Enable()
        self.SetFocus()
        self.Show(True)

# ---------------------------------------------------------------------------


if __name__ == '__main__':
    app = wx.App(redirect=False, useBestVisual=True, clearSigInt=True)

    # Fix language and translation
    lang = wx.LANGUAGE_DEFAULT
    locale = wx.Locale(lang)

    frame = FrameTest()
    app.MainLoop()
