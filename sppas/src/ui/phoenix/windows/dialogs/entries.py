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

    src.ui.phoenix.windows.entries.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
try:
    from agw import floatspin as FS
except ImportError:
    import wx.lib.agw.floatspin as FS

from ..panels import sppasPanel
from ..text import sppasMessageText, sppasStaticText, sppasTextCtrl
from ..combobox import sppasComboBox
from .dialog import sppasDialog
from .messages import sppasBaseMessageDialog

# ---------------------------------------------------------------------------


class sppasChoiceDialog(sppasBaseMessageDialog):
    """Create a message and a list of choices.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    wx.ID_OK is returned if the button is clicked.
    wx.ID_CANCEL is returned if the dialog is destroyed.

    >>> dialog = sppasChoiceDialog("a message", choices=["apples", "pears"])
    >>> dialog.ShowModal()
    >>> dialog.Destroy()

    Bug: Keys are never captured.

    """

    def __init__(self, message="", title=None, **kwargs):
        super(sppasChoiceDialog, self).__init__(
            parent=None,
            message=message,
            title=title,
            style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL | wx.ICON_QUESTION | wx.CAPTION | wx.FRAME_TOOL_WINDOW | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.STAY_ON_TOP,
            **kwargs)

    # -----------------------------------------------------------------------

    def GetSelection(self):
        return self.FindWindow("choices").GetSelection()

    # -----------------------------------------------------------------------

    def GetStringSelection(self):
        return self.FindWindow("choices").GetStringSelection()

    # -----------------------------------------------------------------------

    def _create_content(self, message, **kwargs):
        """Overridden. Create the content of the message dialog."""
        c = ["None"]
        if "choices" in kwargs:
            c = kwargs["choices"]

        p = sppasPanel(self)
        txt = sppasMessageText(p, message)
        choice = sppasComboBox(p, choices=c, name="choices")
        choice.SetMinSize(wx.Size(-1, sppasPanel.fix_size(self.get_font_height()*2)))

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(txt, 0, wx.ALL | wx.EXPAND, sppasPanel.fix_size(8))
        s.Add(choice, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, sppasPanel.fix_size(4))

        h = p.get_font_height()
        p.SetSizer(s)
        p.SetMinSize(wx.Size(-1, (len(c)+2) * h * 2))
        self.SetContent(p)

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        panel = self.CreateActions([wx.ID_CANCEL, wx.ID_OK])
        panel.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        """
        if event.GetKeyCode() == 13:  # ENTER
            self.EndModal(wx.ID_CANCEL)
        elif event.GetKeyCode() == 27:  # ESC
            self.EndModal(wx.ID_OK)
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_CANCEL:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

# ----------------------------------------------------------------------------


class sppasTextEntryDialog(sppasDialog):
    """A dialog that requests a one-line text string from the user.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    >>> dlg = sppasTextEntryDialog("The message", value="The default entry")
    >>> resp = dlg.ShowModal()
    >>> value = dlg.GetValue()
    >>>> dlg.DestroyFadeOut()

    """

    def __init__(self, message="", caption=wx.GetTextFromUserPromptStr, value=""):
        """Create a dialog with a text entry.

        :param message: (str)
        :param value: (str) Default text value

        """
        super(sppasTextEntryDialog, self).__init__(
            parent=None,
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
        self.FadeIn()

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
        s.Add(txt, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT, sppasDialog.fix_size(10))

        entry = sppasTextCtrl(p, value=value, validator=self.__validator, name="text_value")
        s.Add(entry, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT, sppasDialog.fix_size(4))

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


class sppasFloatEntryDialog(sppasDialog):
    """A dialog that requests a float value from the user.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    >>> dlg = sppasFloatEntryDialog("The message", value=0.01, min_value=0., max_value=1.)
    >>> resp = dlg.ShowModal()
    >>> value = dlg.GetValue()
    >>>> dlg.DestroyFadeOut()

    """

    def __init__(self, message="", caption=wx.GetTextFromUserPromptStr, value=0., min_value=0., max_value=1.):
        """Create a dialog with a float entry.

        :param message: (str)
        :param value: (float) Default float value
        :param min_value: (float) Min float value
        :param max_value: (float) Max float value

        """
        super(sppasFloatEntryDialog, self).__init__(
            parent=None,
            title=caption,
            style=wx.FRAME_TOOL_WINDOW | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.STAY_ON_TOP)

        self._create_content(message, value, min_value, max_value)
        self._create_buttons()

        # Fix frame properties
        self.SetMinSize(wx.Size(sppasDialog.fix_size(256),
                                sppasDialog.fix_size(128)))
        self.LayoutComponents()
        self.CenterOnParent()
        self.GetSizer().Fit(self)
        self.FadeIn()

    # -----------------------------------------------------------------------
    # Manage the text value
    # -----------------------------------------------------------------------

    def GetValue(self):
        """"""
        return self.FindWindow("spin_value").GetValue()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self, message, value, min_value, max_value):
        """Create the content of the message dialog."""
        p = sppasPanel(self)
        s = wx.BoxSizer(wx.VERTICAL)

        txt = sppasStaticText(p, label=message)
        s.Add(txt, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT, sppasDialog.fix_size(10))

        inc = round((max_value - min_value) / 20., 3)
        entry = FS.FloatSpin(p, min_val=min_value, max_val=max_value, increment=inc,
                             value=value, digits=3, name="spin_value")
        s.Add(entry, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT, sppasDialog.fix_size(4))

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

# ----------------------------------------------------------------------------


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
            text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        text_ctrl.Refresh()
        return True

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelEntriesDialog(wx.Panel):

    def __init__(self, parent):
        super(TestPanelEntriesDialog, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test Entries Dialogs")

        wx.Button(self, label="Choice (empty)", pos=(10, 10), size=(128, 64),
                  name="btn_empty_choice")
        wx.Button(self, label="Choice list", pos=(10, 210), size=(128, 64),
                  name="btn_choice")
        wx.Button(self, label="TextEntry", pos=(210, 10), size=(128, 64),
                  name="btn_textentry")
        wx.Button(self, label="FloatEntry", pos=(210, 210), size=(128, 64),
                  name="btn_floatentry")

        self.Bind(wx.EVT_BUTTON, self.process_event)

    # -----------------------------------------------------------------------

    def process_event(self, event):
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "btn_empty_choice":
            dlg = sppasChoiceDialog("An empty list of choices:")
            response = dlg.ShowModal()
            value = dlg.GetStringSelection()
            dlg.Destroy()
            wx.LogMessage("Response of dialog: {:d}. Selected: {:s}".format(response, value))

        elif name == "btn_choice":
            dlg = sppasChoiceDialog("An item list of choices:", choices=["apples", "peers", "figs"])
            response = dlg.ShowModal()
            value = dlg.GetStringSelection()
            dlg.DestroyFadeOut()
            wx.LogMessage("Response of dialog: {:d}. Selected: {:s}".format(response, value))

        elif name == "btn_textentry":
            dlg = sppasTextEntryDialog("A text to ask an entry:")
            response = dlg.ShowModal()
            entry = dlg.GetValue()
            dlg.DestroyFadeOut()
            wx.LogMessage("Response of dialog: {:d}. Text value: {:s}".format(response, entry))

        elif name == "btn_floatentry":
            dlg = sppasFloatEntryDialog("A text to ask an entry:", value=0.01, min_value=0., max_value=1.)
            response = dlg.ShowModal()
            entry = dlg.GetValue()
            dlg.DestroyFadeOut()
            wx.LogMessage("Response of dialog: {:d}. Float value: {:f}".format(response, entry))
