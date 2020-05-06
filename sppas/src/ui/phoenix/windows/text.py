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

    src.ui.phoenix.windows.text.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import re
import wx

# ---------------------------------------------------------------------------


class sppasStaticText(wx.StaticText):
    """Create a static text.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font, foreground and background are taken from the application settings.

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 label="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE,
                 name=wx.StaticTextNameStr):
        """Create a static text for a content panel.

        Possible constructors:
            - sppasStaticText()
            - sppasStaticText(parent, id=ID_ANY, label="",
                pos=DefaultPosition, size=DefaultSize, style=0,
                name=StaticTextNameStr)

        A StaticText that only updates the label if it has changed, to
        help reduce potential flicker since its control would be
        updated very frequently otherwise.

        """
        # always turn off auto resize
        style |= wx.ST_NO_AUTORESIZE

        # and turn off any border styles
        style &= ~wx.BORDER_MASK
        style |= wx.BORDER_NONE

        super(sppasStaticText, self).__init__(
            parent, id, label, pos, size, style, name)

        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        # Set the label after we defined the font
        self.SetLabel(label)

    # -----------------------------------------------------------------------

    def SetLabel(self, label):
        """Update the label if it has changed.

        Help reduce potential flicker since these controls would be updated
        very frequently otherwise.

        :param label: (str)

        """
        if label != self.GetLabel():
            wx.StaticText.SetLabel(self, label)
            self.__set_min_size()

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.Window.SetFont(self, font)
        self.__set_min_size()

    # -----------------------------------------------------------------------

    def GetWindowHeight(self):
        """Return the height assigned to the text."""
        return int(float(self.get_font_height()) * 1.6)

    # -----------------------------------------------------------------------

    def get_font_height(self):
        font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))

    # -----------------------------------------------------------------------

    def __set_min_size(self):
        """Estimate the min size in a proper way!"""
        (w, h) = self.DoGetBestSize()
        h = self.GetWindowHeight()
        try:
            c = wx.GetApp().settings.size_coeff
        except AttributeError:
            c = 1.

        self.SetMinSize(wx.Size(int(float(w) * c), h))

# ---------------------------------------------------------------------------


class sppasTextCtrl(wx.TextCtrl):
    """A text control allows text to be displayed and edited.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Possible constructors:
        - sppasTextCtrl()
        - sppasTextCtrl(parent, id=ID_ANY, value="", pos=DefaultPosition,
                 size=DefaultSize, style=0, validator=DefaultValidator,
                 name=TextCtrlNameStr)

    Existing shortcuts in a textctrl (tested under WindowsInstaller):
        - Ctrl+a - select all
        - Ctrl+c - copy
        - Ctrl+h - del previous char or selection
        - Ctrl+i - Insert tab
        - Ctrl+j - Enter (which means to create a new label)
        - Ctrl+m - like ctrl+j - Enter
        - Ctrl+v - paste
        - Ctrl+x - cut
        - Ctrl+z - undo

    Font, foreground and background are taken from the application settings.

    """

    def __init__(self, parent, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name=wx.TextCtrlNameStr):
        super(sppasTextCtrl, self).__init__(
            parent, id, value="", pos=pos, size=size, style=style,
            validator=validator, name=name)

        # Fix Look&Feel
        try:
            settings = wx.GetApp().settings
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
            self.SetBackgroundColour(settings.bg_color)
        except:
            self.InheritAttributes()

        # the message is not send to the base class when init but after
        # in order to apply the appropriate colors&font
        self.SetValue(value)

    def SetForegroundColour(self, colour):
        wx.Window.SetForegroundColour(self, colour)
        attr = wx.TextAttr()
        attr.SetTextColour(colour)
        attr.SetBackgroundColour(self.GetBackgroundColour())
        attr.SetFont(self.GetFont())
        self.SetDefaultStyle(attr)
        self.SetStyle(0, len(self.GetValue()), attr)

    def SetBackgroundColour(self, colour):
        wx.Window.SetBackgroundColour(self, colour)
        attr = wx.TextAttr()
        attr.SetTextColour(self.GetForegroundColour())
        attr.SetBackgroundColour(colour)
        attr.SetFont(self.GetFont())
        self.SetDefaultStyle(attr)
        self.SetStyle(0, len(self.GetValue()), attr)

    def SetFont(self, font):
        wx.Window.SetFont(self, font)
        attr = wx.TextAttr()
        # attr.SetTextColour(wx.GetApp().settings.fg_color)
        attr.SetTextColour(self.GetForegroundColour())
        attr.SetBackgroundColour(self.GetBackgroundColour())
        attr.SetFont(font)
        self.SetDefaultStyle(attr)
        self.SetStyle(0, len(self.GetValue()), attr)

# ---------------------------------------------------------------------------


class sppasTitleText(wx.TextCtrl):
    """Create a static title.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Font, foreground and background are taken from the application settings.

    Possible constructors:
        - sppasTitleText()
        - sppasTitleText(parent, id=ID_ANY, value="", name=TextCtrlNameStr)

    """

    text_style = wx.TAB_TRAVERSAL | \
                 wx.TE_READONLY | \
                 wx.TE_BESTWRAP | \
                 wx.TE_CENTRE | \
                 wx.NO_BORDER

    def __init__(self, parent, id=wx.ID_ANY, value="", name=wx.TextCtrlNameStr):
        super(sppasTitleText, self).__init__(
            parent, id,
            value=" ",
            style=sppasTitleText.text_style,
            name=name)

        self.align = wx.TEXT_ALIGNMENT_LEFT
        # Fix Look&Feel
        try:
            settings = wx.GetApp().settings
            self.SetForegroundColour(settings.header_fg_color)
            self.SetFont(settings.header_text_font)
            self.SetBackgroundColour(settings.header_bg_color)
        except:
            wx.LogWarning("Settings not set to construct sppasTitleText.")
            pass

        # the message is not send to the base class when init but after
        # in order to apply the appropriate colors&font&size
        self.SetValue(value)
        self.Layout()

    def AcceptsFocus(self):
        return False

    def SetForegroundColour(self, colour):
        wx.Window.SetForegroundColour(self, colour)
        attr = wx.TextAttr()
        attr.SetTextColour(colour)
        attr.SetBackgroundColour(self.GetBackgroundColour())
        attr.SetFont(self.GetFont())
        attr.SetAlignment(self.align)
        self.SetDefaultStyle(attr)
        self.SetStyle(0, len(self.GetValue()), attr)

    def SetBackgroundColour(self, colour):
        wx.Window.SetBackgroundColour(self, colour)
        attr = wx.TextAttr()
        attr.SetTextColour(self.GetForegroundColour())
        attr.SetBackgroundColour(colour)
        attr.SetFont(self.GetFont())
        attr.SetAlignment(self.align)
        self.SetDefaultStyle(attr)
        self.SetStyle(0, len(self.GetValue()), attr)

    def SetFont(self, font):
        wx.Window.SetFont(self, font)
        attr = wx.TextAttr()
        attr.SetTextColour(self.GetForegroundColour())
        attr.SetBackgroundColour(self.GetBackgroundColour())
        attr.SetFont(font)
        attr.SetAlignment(self.align)
        self.SetDefaultStyle(attr)
        self.SetStyle(0, len(self.GetValue()), attr)

    def SetAlignment(self, align):
        """Align is a wx.TextAttrAlignment."""
        if align != self.align:
            self.align = align
            attr = wx.TextAttr()
            attr.SetTextColour(self.GetForegroundColour())
            attr.SetBackgroundColour(self.GetBackgroundColour())
            attr.SetFont(self.GetFont())
            attr.SetAlignment(align)
            self.SetDefaultStyle(attr)
            self.SetStyle(0, len(self.GetValue()), attr)
            self.Refresh()

# ---------------------------------------------------------------------------


class sppasMessageText(sppasTextCtrl):
    """Create a multi-lines message text, centered.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font, foreground and background are taken from the application settings.

    Possible constructors:
        - sppasMessageText()
        - sppasMessageText(parent, id=ID_ANY, value="", name=TextCtrlNameStr)

    """

    text_style = wx.TAB_TRAVERSAL | \
                 wx.TE_READONLY | \
                 wx.TE_BESTWRAP | \
                 wx.TE_CENTRE | \
                 wx.NO_BORDER | \
                 wx.TE_MULTILINE
                 # wx.TE_AUTO_URL | \
                 # wx.TE_RICH

    def __init__(self, parent, message, name=wx.TextCtrlNameStr):
        super(sppasMessageText, self).__init__(
            parent=parent,
            value="",
            style=sppasMessageText.text_style,
            name=name)
        # the message is not send to the base class when init but after
        # in order to apply the appropriate colors
        self.SetValue(message)

    def AcceptsFocus(self):
        """Can this window be given focus by mouse click?"""
        return False

# ---------------------------------------------------------------------------


class sppasSimpleText(sppasTextCtrl):
    """Create a single-line left-justified message text.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Font, foreground and background are taken from the application settings.

    Possible constructors:
        - sppasMessageText()
        - sppasMessageText(parent, id=ID_ANY, value="", name=TextCtrlNameStr)

    """

    text_style = wx.TAB_TRAVERSAL | \
                 wx.TE_READONLY | \
                 wx.TE_BESTWRAP | \
                 wx.TE_LEFT | \
                 wx.NO_BORDER

    def __init__(self, parent, message, name=wx.TextCtrlNameStr):
        super(sppasSimpleText, self).__init__(
            parent=parent,
            value="",
            style=sppasSimpleText.text_style,
            name=name)
        # the message is not send to the base class when init but after
        # in order to apply the appropriate colors
        self.SetValue(message)

# ---------------------------------------------------------------------------
# Validators for a sppasTextCtrl or wx.TextCtrl.
# ---------------------------------------------------------------------------


class NotEmptyTextValidator(wx.Validator):
    """Check if the TextCtrl contains characters.

    If the TextCtrl does not contains characters, the background becomes
    pinky, Either, it is set to the system background colour.

    """

    def __init__(self):
        super(NotEmptyTextValidator, self).__init__()

    def Clone(self):
        # Required method for validator
        return NotEmptyTextValidator()

    def TransferToWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def TransferFromWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def Validate(self, win=None):
        text_ctrl = self.GetWindow()
        text = text_ctrl.GetValue().strip()
        if len(text) == 0:
            text_ctrl.SetBackgroundColour("pink")
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False

        try:
            text_ctrl.SetBackgroundColour(wx.GetApp().settings.bg_colour)
        except:
            text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        text_ctrl.Refresh()
        return True

# ---------------------------------------------------------------------------


class ASCIITextValidator(wx.Validator):
    """Check if the TextCtrl contains only ASCII characters.

    If the TextCtrl does not contains characters, the background becomes
    pinky, Either, it is set to the system background colour.

    """

    def __init__(self):
        super(ASCIITextValidator, self).__init__()

    def Clone(self):
        # Required method for validator
        return ASCIITextValidator()

    def TransferToWindow(self):
        # Prevent wxDialog from complaining.
        return True

    def TransferFromWindow(self):
        # Prevent wxDialog from complaining.
        return True

    @staticmethod
    def is_restricted_ascii(text):
        # change any other character than a to z and underscore in the key
        ra = re.sub(r'[^a-zA-Z0-9_]', '*', text)
        return text == ra

    def Validate(self, win=None):
        text_ctrl = self.GetWindow()
        text = text_ctrl.GetValue().strip()
        if ASCIITextValidator.is_restricted_ascii(text) is False:
            text_ctrl.SetBackgroundColour("pink")
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False

        try:
            text_ctrl.SetBackgroundColour(wx.GetApp().settings.bg_colour)
        except:
            text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

        text_ctrl.Refresh()
        return True

