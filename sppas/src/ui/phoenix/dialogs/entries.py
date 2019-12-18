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

    src.ui.phoenix.dialogs.entries.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import logging

from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import sppasStaticText
from ..windows import sppasTextCtrl

# ----------------------------------------------------------------------------


class sppasTextEntryDialog(sppasDialog):
    """A dialog that requests a one-line text string from the user.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, message, caption=wx.GetTextFromUserPromptStr, value=""):
        """Create a dialog with a text entry.

        The dialog has a small title bar which does not appear in the taskbar
        under Windows or GTK+.

        :param parent: (wx.Window)

        """
        super(sppasTextEntryDialog, self).__init__(
            parent=parent,
            title=caption,
            style=wx.FRAME_TOOL_WINDOW | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.STAY_ON_TOP)

        self.__validator = LengthTextValidator()
        self.__validator.SetMaxLength(20)
        self._create_content(message, value)
        self._create_buttons()

        # Fix frame properties
        self.SetMinSize(wx.Size(sppasDialog.fix_size(256),
                                sppasDialog.fix_size(128)))
        self.LayoutComponents()
        self.CenterOnParent()
        self.GetSizer().Fit(self)
        self.FadeIn(deltaN=-10)

    # -----------------------------------------------------------------------
    # Manage the text value
    # -----------------------------------------------------------------------

    def GetValue(self):
        """"""
        return self.FindWindow("text_value").GetValue()

    # -----------------------------------------------------------------------

    def SetMaxLength(self, value):
        """Sets the maximum number of characters the user can enter."""
        self.__validator.SetMaxLength(value)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self, message, value):
        """Create the content of the message dialog."""
        p = sppasPanel(self)
        s = wx.BoxSizer(wx.VERTICAL)

        txt = sppasStaticText(p, label=message)
        s.Add(txt, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 10)

        entry = sppasTextCtrl(p, value=value, validator=self.__validator, name="text_value")
        s.Add(entry, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 10)

        p.SetSizer(s)
        p.SetName("content")
        p.SetMinSize(wx.Size(-1, sppasDialog.fix_size(96)))

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_CANCEL:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()
        else:
            event.Skip()

# ---------------------------------------------------------------------------


class LengthTextValidator(wx.Validator):
    """Check if the TextCtrl is valid for an identifier.

    If the TextCtrl is not valid, the background becomes pinky.

    """

    def __init__(self):
        super(LengthTextValidator, self).__init__()
        self.__max_length = 128
        self.__min_length = 2

    def SetMinLength(self, value):
        self.__min_length = int(value)

    def SetMaxLength(self, value):
        self.__max_length = int(value)

    def Clone(self):
        # Required method for validator
        return LengthTextValidator()

    def TransferToWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def TransferFromWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def Validate(self, win=None):
        text_ctrl = self.GetWindow()
        text = text_ctrl.GetValue().strip()
        if self.__min_length < len(text) > self.__max_length:
            text_ctrl.SetBackgroundColour("pink")
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False

        try:
            text_ctrl.SetBackgroundColour(wx.GetApp().settings.bg_color)
        except:
            logging.debug('Error: Application settings not defined.')
            text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        text_ctrl.Refresh()
        return True
