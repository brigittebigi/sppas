import wx

from ..panel import sppasPanel
from ..text import sppasMessageText, sppasStaticText, sppasTextCtrl
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

    """

    def __init__(self, message, title=None, **kwargs):
        super(sppasChoiceDialog, self).__init__(
            parent=None,
            message=message,
            title=title,
            style=wx.ICON_QUESTION,
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
        choice = wx.Choice(p, choices=c, name="choices")
        choice.SetSelection(0)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(txt, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 10)
        s.Add(choice, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 10)

        h = p.get_font_height()
        p.SetSizer(s)
        p.SetMinSize(wx.Size(-1, (len(c)+2) * h * 2))
        self.SetContent(p)

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
        s.Add(txt, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, sppasDialog.fix_size(10))

        entry = sppasTextCtrl(p, value=value, validator=self.__validator, name="text_value")
        s.Add(entry, 0, wx.ALL | wx.EXPAND | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, sppasDialog.fix_size(10))

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
            text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        text_ctrl.Refresh()
        return True
