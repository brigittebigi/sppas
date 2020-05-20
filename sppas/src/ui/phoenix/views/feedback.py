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

    src.ui.phoenix.views.feedback.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import webbrowser
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

from sppas.src.config import sg
from sppas.src.config import msg
from sppas.src.utils import u

from ..windows import BitmapTextButton
from ..windows import sppasTextCtrl
from ..windows import sppasPanel
from ..windows import sppasDialog
from ..windows import Information

# -------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


DESCRIBE_TEXT = _("Write the message here")
SEND_WITH_OTHER = _(
    "Copy and paste the message into your favorite email client and "
    "send it from there.")

MSG_HEADER_FEEDBACK = _("Send e-mail")
MSG_EMAIL_TO = _("To: ")
MSG_EMAIL_SUBJECT = _("Subject: ")
MSG_EMAIL_BODY = _("Body: ")
MSG_EMAIL_SEND_WITH = _("Send with: ")
MSG_ACTION_OTHER = _("Other")
MSG_ACTION_CLOSE = _("Close")

# ----------------------------------------------------------------------------


class sppasFeedbackDialog(sppasDialog):
    """Dialog to send a message by e-mail to the author.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        """Create a feedback dialog.

        :param parent: (wx.Window)

        """
        super(sppasFeedbackDialog, self).__init__(
            parent=parent,
            title='{:s} Feedback'.format(sg.__name__),
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX |
                  wx.MAXIMIZE_BOX | wx.STAY_ON_TOP)

        self.CreateHeader(MSG_HEADER_FEEDBACK, icon_name="mail-at")
        self._create_content()
        self.CreateActions([wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.SetMinSize(wx.Size(sppasDialog.fix_size(480),
                                sppasDialog.fix_size(320)))
        self.LayoutComponents()
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        panel = sppasPanel(self, name="content")

        to = wx.StaticText(panel, label=MSG_EMAIL_TO)
        self.to_text = wx.StaticText(
            parent=panel,
            label=sg.__contact__)

        subject = wx.StaticText(panel, label=MSG_EMAIL_SUBJECT)
        self.subject_text = wx.StaticText(
            parent=panel,
            label=sg.__name__ + " " + sg.__version__ + " - Feedback...")

        body = wx.StaticText(panel, label=MSG_EMAIL_BODY)
        body_style = wx.TAB_TRAVERSAL | wx.TE_BESTWRAP |\
                     wx.TE_MULTILINE | wx.BORDER_STATIC
        self.body_text = sppasTextCtrl(
            parent=panel,
            value=DESCRIBE_TEXT,
            style=body_style)
        self.body_text.SetSelection(0, len(DESCRIBE_TEXT))
        self.body_text.Bind(wx.EVT_CHAR, self._on_char, self.body_text)

        grid = wx.FlexGridSizer(4, 2, 5, 5)
        grid.AddGrowableCol(1)
        grid.AddGrowableRow(2)

        grid.Add(to, 0, wx.LEFT, 4)
        grid.Add(self.to_text, 0, flag=wx.EXPAND)

        grid.Add(subject, 0, wx.LEFT, 4)
        grid.Add(self.subject_text, 0, flag=wx.EXPAND)

        grid.Add(body, 0, wx.TOP | wx.LEFT, 4)
        grid.Add(self.body_text, 2, flag=wx.EXPAND)

        s = wx.StaticText(panel, label=MSG_EMAIL_SEND_WITH)
        grid.Add(s, 0, wx.LEFT | wx.BOTTOM, 4)
        send_panel = self._create_send_buttons(panel)
        grid.Add(send_panel, 0, wx.LEFT | wx.BOTTOM, 4)

        panel.SetAutoLayout(True)
        panel.SetSizer(grid)
        self.SetContent(panel)

    # -----------------------------------------------------------------------

    def _create_send_buttons(self, parent):
        """Create the buttons."""
        panel = sppasPanel(parent, name="send_panel")
        panel.SetMinSize(wx.Size(-1, wx.GetApp().settings.action_height))

        # Create the buttons
        gmail_btn = self._create_button(panel, "Gmail", "gmail")
        default_btn = self._create_button(panel, "E-mail", "window-email")
        other_btn = self._create_button(panel, MSG_ACTION_OTHER, "at")

        # Organize buttons in a sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(gmail_btn, 1, wx.EXPAND | wx.LEFT, panel.fix_size(6))
        sizer.Add(default_btn, 1, wx.EXPAND | wx.LEFT, panel.fix_size(6))
        sizer.Add(other_btn, 1, wx.EXPAND | wx.LEFT, panel.fix_size(6))

        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def _create_button(self, parent, text, icon):
        btn = BitmapTextButton(parent, label=text, name=icon)

        # Get the font height for the header
        h = parent.get_font_height()

        btn.SetLabelPosition(wx.RIGHT)
        btn.SetFocusStyle(wx.PENSTYLE_SOLID)
        btn.SetFocusWidth(h//4)
        btn.SetFocusColour(wx.Colour(128, 128, 128, 128))
        btn.SetSpacing(sppasPanel.fix_size(h//2))
        btn.SetBorderWidth(1)
        btn.SetBitmapColour(self.GetForegroundColour())
        btn.SetMinSize(wx.Size(h*10, h*2))

        return btn

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind close event from the close dialog 'x' on the frame
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "window-email":
            self.SendWithDefault()

        elif event_name == "gmail":
            self.SendWithGmail()

        elif event_name == "at":
            Information("Copy and paste the message into your favorite email "
                        "client and send it from there.")
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _on_char(self, evt):

        if self.body_text.GetValue().strip() == DESCRIBE_TEXT:
            self.body_text.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.body_text.SetValue('')

        if evt.ControlDown() and evt.KeyCode == 1:
            # Ctrl+A
            self.body_text.SelectAll()

        else:
            evt.Skip()

    # ------------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------------

    def GetToText(self):
        return self.to_text.GetLabelText()

    def GetSubjectText(self):
        return self.subject_text.GetLabelText()

    def GetBodyText(self):
        return self.body_text.GetValue()

    # -----------------------------------------------------------------------

    def SetBodyText(self, text):
        self.body_text.WriteText(text)
        self.body_text.SetInsertionPoint(0)

    # -----------------------------------------------------------------------

    def SendWithDefault(self):
        text = self.GetBodyText().strip()
        webbrowser.open(
            "mailto:{to}?subject={subject}&body={body}".format(
                to=quote(self.GetToText()),
                subject=quote(self.GetSubjectText()),
                body=quote(text.encode('utf-8'))))

    # -----------------------------------------------------------------------

    def SendWithGmail(self):
        text = self.GetBodyText()
        text = text.strip()
        webbrowser.open(
            "https://mail.google.com/mail/?compose=1&view=cm&fs=1&to=%s&su=%s&body=%s" % (
            quote(self.GetToText()),
            quote(self.GetSubjectText()),
            quote(text))
        )

# -------------------------------------------------------------------------


def Feedback(parent, text=None):
    """Display a dialog to send feedback.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    :param parent: (wx.Window)
    :param text: (str) the text to send in the body of the e-mail.
    :returns: the response

    wx.ID_CANCEL is returned if the dialog is destroyed or if no e-mail
    was sent.

    """
    dialog = sppasFeedbackDialog(parent)
    if text is not None:
        dialog.SetBodyText(text)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response
