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

    src.ui.phoenix.views.messages.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.config import msg
from sppas.src.utils import u

from ..text import sppasMessageText
from ..panel import sppasPanel
from .dialog import sppasDialog

# ----------------------------------------------------------------------------

MSG_HEADER_ERROR = u(msg("Error", "ui"))
MSG_HEADER_WARNING = u(msg("Warning", "ui"))
MSG_HEADER_QUESTION = u(msg("Question", "ui"))
MSG_HEADER_INFO = u(msg("Information", "ui"))
MSG_MESSAGE = u(msg("Message", "ui"))

# ----------------------------------------------------------------------------


class sppasBaseMessageDialog(sppasDialog):
    """Base class to create message views.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, message, title=None, style=wx.ICON_INFORMATION, **kwargs):
        """Create a dialog with a message.

        :param parent: (wx.Window)
        :param message: (str) the file to display in this frame.
        :param title: (str) a title to display in the header. Default is the icon one.
        :param style: ONE of wx.ICON_INFORMATION, wx.ICON_ERROR, wx.ICON_EXCLAMATION, wx.YES_NO

        """
        super(sppasBaseMessageDialog, self).__init__(
            parent=parent,
            title=MSG_MESSAGE,
            style=wx.CAPTION | wx.FRAME_TOOL_WINDOW | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.STAY_ON_TOP)

        self._create_header(style, title)
        self._create_content(message, **kwargs)
        self._create_buttons()

        # Capture all key events
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # Fix frame properties
        self.SetMinSize(wx.Size(sppasDialog.fix_size(256),
                                sppasDialog.fix_size(164)))
        self.LayoutComponents()
        self.CenterOnParent()
        self.GetSizer().Fit(self)
        self.FadeIn(deltaN=-4)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process any kind of key events. To be overridden.

        :param event: (wx.Event)

        """
        event.Skip()

    # -----------------------------------------------------------------------

    def _create_header(self, style, title):
        """Create the header of the message dialog."""
        # Create the header
        if style == wx.ICON_ERROR:
            icon = "error"
            if title is None:
                title = MSG_HEADER_ERROR

        elif style == wx.ICON_WARNING:
            icon = "warning"
            if title is None:
                title = MSG_HEADER_WARNING

        elif style == wx.YES_NO:
            icon = "question"
            if title is None:
                title = MSG_HEADER_QUESTION

        else:
            icon = "information"
            if title is None:
                title = MSG_HEADER_INFO

        self.CreateHeader(title, icon_name=icon)

    # -----------------------------------------------------------------------

    def _create_content(self, message, **kwargs):
        """Create the content of the message dialog."""
        p = sppasPanel(self, style=wx.NO_BORDER | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)
        h = p.get_font_height()
        s = wx.BoxSizer(wx.HORIZONTAL)
        txt = sppasMessageText(p, message)
        s.Add(txt, 1, wx.ALL | wx.EXPAND, sppasPanel.fix_size(8))
        p.SetSizer(s)
        # p.SetName("content")
        p.SetMinSize(wx.Size(-1, h*4))
        self.SetContent(p)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        """Override to create the buttons and bind events."""
        raise NotImplementedError

# ---------------------------------------------------------------------------
# Message views
# ---------------------------------------------------------------------------


class sppasYesNoDialog(sppasBaseMessageDialog):
    """Create a message in a wx.Dialog with a yes-no question.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    wx.ID_YES or wx.ID_NO is returned if a button is clicked.
    wx.ID_CANCEL is returned if the dialog is destroyed or if escape key is
    pressed.

    >>> dialog = sppasYesNoDialog("Really exit?")
    >>> response = dialog.ShowModal()
    >>> dialog.Destroy()
    >>> if response == wx.ID_YES:
    >>>     # do something here

    """

    def __init__(self, message, title=None):
        super(sppasYesNoDialog, self).__init__(
            parent=None,
            message=message,
            title=title,
            style=wx.YES_NO)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_NO, wx.ID_YES])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_YES)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_NO:
            self.EndModal(wx.ID_NO)
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        if key_code == 78:
            self.EndModal(wx.ID_NO)
        elif key_code == 89:
            self.EndModal(wx.ID_YES)
        elif key_code == 27:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

# ---------------------------------------------------------------------------


class sppasConfirmDialog(sppasBaseMessageDialog):
    """Create a message in a wx.Dialog to confirm an action after an error.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    wx.ID_YES is returned if 'yes' is clicked.
    wx.ID_CANCEL is returned if the dialog is destroyed or cancel is clicked.

    >>> dialog = sppasConfirmDialog("Confirm..."))
    >>> response = dialog.ShowModal()
    >>> dialog.Destroy()
    >>> if response == wx.ID_YES:
    >>>     # do something here

    """

    def __init__(self, message, title=None):
        super(sppasConfirmDialog, self).__init__(
            parent=None,
            message=message,
            title=title,
            style=wx.ICON_ERROR)

    # -----------------------------------------------------------------------

    def cancel(self):
        self.EndModal(wx.ID_CANCEL)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_CANCEL, wx.ID_YES])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_YES)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_CANCEL:
            self.cancel()
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        if key_code == 27:
            self.cancel()
        elif key_code == 13:
            self.EndModal(wx.ID_YES)
        else:
            event.Skip()

# ---------------------------------------------------------------------------


class sppasInformationDialog(sppasBaseMessageDialog):
    """Create a message in a wx.Dialog with an information.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    wx.ID_OK is returned when the button is clicked or ENTER key is pressed.
    wx.ID_CANCEL is returned if the escape button is pressed.

    >>> dialog = sppasInformationDialog("you are here")
    >>> dialog.ShowModal()
    >>> dialog.Destroy()

    """

    def __init__(self, message):
        super(sppasInformationDialog, self).__init__(
            parent=None,
            message=message,
            style=wx.ICON_INFORMATION)

    # -----------------------------------------------------------------------

    def cancel(self):
        self.EndModal(wx.ID_CANCEL)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_OK])
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        if key_code == 27:
            self.cancel()
        elif key_code == 13:
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

# ---------------------------------------------------------------------------


class sppasWarnDialog(sppasBaseMessageDialog):
    """Create a message in a wx.Dialog with a warn message.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    wx.ID_OK is returned when the button is clicked or ENTER key is pressed.
    wx.ID_CANCEL is returned if ESC key is pressed.

    >>> dialog = sppasWarnDialog("there's something wrong...")
    >>> dialog.ShowModal()
    >>> dialog.Destroy()

    """

    def __init__(self, message):
        super(sppasWarnDialog, self).__init__(
            parent=None,
            message=message,
            style=wx.ICON_WARNING)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_OK])
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        if key_code == 27:
            self.EndModal(wx.ID_CANCEL)
        elif key_code == 13:
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

# ---------------------------------------------------------------------------


class sppasErrorDialog(sppasBaseMessageDialog):
    """Create a message in a wx.Dialog with a error message.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    wx.ID_OK is returned when the button is clicked or ENTER key is pressed.
    wx.ID_CANCEL is returned if ESC key is pressed.

    >>> dialog = sppasErrorDialog("an error occurred")
    >>> dialog.ShowModal()
    >>> dialog.Destroy()

    """

    def __init__(self, message, title=None):
        super(sppasErrorDialog, self).__init__(
            parent=None,
            message=message,
            title=title,
            style=wx.ICON_ERROR)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_OK])
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        if key_code == 27:
            self.EndModal(wx.ID_CANCEL)
        elif key_code == 13:
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

# ---------------------------------------------------------------------------
# Ready-to-use functions to display messages
# ---------------------------------------------------------------------------


def YesNoQuestion(message):
    """Display a yes-no question.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :param message: (str) The question to ask
    :returns: the response

    wx.ID_YES or wx.ID_NO is returned if a button is clicked.
    wx.ID_CANCEL is returned if the dialog is destroyed.

    """
    wx.LogMessage(message)
    dialog = sppasYesNoDialog(message)
    response = dialog.ShowModal()
    dialog.Destroy()
    wx.LogMessage("User clicked yes" if response == wx.ID_YES else "User clicked no")
    return response

# ---------------------------------------------------------------------------


def Confirm(message, title=None):
    """Display a confirmation after an error.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :param message: (str) The error and confirmation question
    :param title: (str) Title of the dialog window
    :returns: the response

    wx.ID_YES if ok button is clicked.
    wx.ID_CANCEL is returned if the dialog is destroyed or cancel clicked.

    """
    wx.LogMessage(message)
    dialog = sppasConfirmDialog(message, title)
    response = dialog.ShowModal()
    dialog.Destroy()
    wx.LogMessage("Confirmed by user." if response == wx.ID_YES else "User cancelled.")
    return response

# ---------------------------------------------------------------------------


def Error(message):
    """Display a error message.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    :param message: (str) The question to ask
    :returns: the response

    wx.ID_OK is returned if a button is clicked.

    """
    wx.LogError(message)
    dialog = sppasErrorDialog(message, title=None)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response

# ---------------------------------------------------------------------------


def Information(message):
    """Display an information message.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :param message: (str) The information to display
    :returns: wx.ID_OK

    """
    wx.LogMessage(message)
    dialog = sppasInformationDialog(message)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response

# ---------------------------------------------------------------------------


def Warn(message):
    """Display a warn message.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :param message: (str) The message to display
    :returns: wx.ID_OK

    """
    wx.LogWarning(message)
    dialog = sppasWarnDialog(message)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelMessageDialog(wx.Panel):

    def __init__(self, parent):
        super(TestPanelMessageDialog, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test Message Dialogs")

        wx.Button(self, label="Confirm", pos=(10, 10), size=(128, 64),
                  name="btn_confirm")
        wx.Button(self, label="Yes - No", pos=(210, 10), size=(128, 64),
                  name="btn_yesno")
        wx.Button(self, label="Information", pos=(10, 100), size=(128, 64),
                  name="btn_info")
        wx.Button(self, label="Warning", pos=(10, 200), size=(128, 64),
                  name="btn_warn")
        wx.Button(self, label="Error", pos=(210, 200), size=(128, 64),
                  name="btn_error")
        self.Bind(wx.EVT_BUTTON, self.process_event)

    # -----------------------------------------------------------------------

    def process_event(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "btn_confirm":
            response = Confirm("Message to ask confirmation?")
            wx.LogMessage("Response of confirm dialog: {:d}".format(response))
        elif name == "btn_yesno":
            response = YesNoQuestion("Message to ask a yes-no question?")
            wx.LogMessage("Response of yes-no dialog: {:d}".format(response))
        elif name == "btn_info":
            response = Information("Message to inform...")
            wx.LogMessage("Response of information dialog: {:d}".format(response))
        elif name == "btn_warn":
            response = Warn("Message to warn...")
            wx.LogMessage("Response of warn dialog: {:d}".format(response))
        elif name == "btn_error":
            response = Error("Message of an error...")
            wx.LogMessage("Response of error dialog: {:d}".format(response))

