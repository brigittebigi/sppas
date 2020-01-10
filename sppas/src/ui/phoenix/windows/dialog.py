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

    src.ui.phoenix.windows.dialog.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.config import sg
from sppas.src.config import ui_translation

from ..tools import sppasSwissKnife
from . import sppasBitmapTextButton
from . import sppasStaticBitmap
from . import sppasStaticLine
from . import sppasTitleText
from . import sppasPanel

# ----------------------------------------------------------------------------

MSG_ACTION_OK = ui_translation.gettext("Okay")
MSG_ACTION_CANCEL = ui_translation.gettext("Cancel")
MSG_ACTION_YES = ui_translation.gettext("Yes")
MSG_ACTION_NO = ui_translation.gettext("No")
MSG_ACTION_APPLY = ui_translation.gettext("Apply")
MSG_ACTION_CLOSE = ui_translation.gettext("Close")
MSG_ACTION_SAVE = ui_translation.gettext("Save")

# ----------------------------------------------------------------------------


class sppasDialog(wx.Dialog):
    """Base class for dialogs in SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, *args, **kw):
        """Create a dialog.

        Possible constructors:

            - sppasDialog()
            - sppasDialog(parent, id=ID_ANY, title="", pos=DefaultPosition,
                     size=DefaultSize, style=DEFAULT_DIALOG_STYLE,
                     name=DialogNameStr)

        A sppasDialog is made of 3 (optional) wx.Window() with name:

            - at top: "header"
            - at middle: "content"
            - at bottom: "actions"

        """
        super(sppasDialog, self).__init__(*args, **kw)
        self._init_infos()
        self.SetAutoLayout(True)

        # To fade-in and fade-out the opacity
        self.opacity_in = 0
        self.opacity_out = 255
        self.deltaN = -10
        self.timer1 = None
        self.timer2 = None

    # -----------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        settings = wx.GetApp().settings

        # Fix minimum frame size
        self.SetMinSize(wx.Size(320, 200))

        # Fix frame name
        self.SetName('{:s}-{:d}'.format(sg.__name__, self.GetId()))

        # icon
        _icon = wx.Icon()
        bmp = sppasSwissKnife.get_bmp_icon("sppas_32", height=64)
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------
    # Fade-in at start-up and Fade-out at close
    # -----------------------------------------------------------------------

    def FadeIn(self, deltaN=-10):
        """Fade-in opacity."""
        self.deltaN = int(deltaN)
        self.SetTransparent(self.opacity_in)
        self.timer1 = wx.Timer(self, -1)
        self.timer1.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_in, self.timer1)

    def DestroyFadeOut(self, deltaN=-10):
        """Destroy with a fade-out opacity."""
        self.deltaN = int(deltaN)
        self.timer2 = wx.Timer(self, -1)
        self.timer2.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_out, self.timer2)

    # -----------------------------------------------------------------------
    # Override existing but un-useful methods
    # -----------------------------------------------------------------------

    def CreateButtonSizer(self, flags):
        """Overridden to disable."""
        pass

    def CreateSeparatedButtonSizer(self, flags):
        """Overridden to disable."""
        pass

    def CreateSeparatedSizer(self, sizer):
        """Overridden to disable."""
        pass

    def CreateStdDialogButtonSizer(self, flags):
        """Overridden to disable."""
        pass

    def CreateTextSizer(self, message):
        """Overridden to disable."""
        pass

    # -----------------------------------------------------------------------

    def GetContentWindow(self):
        """Overridden.

        Return a window containing the main content of the dialog.

        """
        return self.FindWindow("content")

    # -----------------------------------------------------------------------
    # Methods to add/set the header, content, actions
    # -----------------------------------------------------------------------

    def CreateEmptyHeader(self):
        """Create an empty panel for an header.

        """
        # Create the header panel and sizer
        panel = sppasPanel(self, name="header")
        panel.SetMinSize((-1, wx.GetApp().settings.title_height))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # This header panel properties
        panel.SetSizer(sizer)
        self.SetHeader(panel)

    # -----------------------------------------------------------------------

    def CreateHeader(self, title, icon_name=None):
        """Create a panel including a title with an optional icon.

        :param title: (str) The message in the header
        :param icon_name: (str) Base name of the icon.

        """
        spacing = self.fix_size(10)
        # Create the header panel and sizer
        panel = sppasPanel(self, name="header")
        panel.SetMinSize(wx.Size(-1, wx.GetApp().settings.title_height))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add the icon, at left, with its title
        if icon_name is not None:
            static_bmp = sppasStaticBitmap(panel, icon_name)
            sizer.Add(static_bmp, 0,
                      wx.LEFT | wx.ALIGN_CENTER_VERTICAL, spacing)

        txt = sppasTitleText(panel, value=title)
        txt.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        sizer.Add(txt, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, spacing)

        # This header panel properties
        panel.SetSizer(sizer)
        self.SetHeader(panel)

    # -----------------------------------------------------------------------

    def SetHeader(self, window):
        """Assign the header window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("header")
        window.SetBackgroundColour(wx.GetApp().settings.header_bg_color)
        window.SetForegroundColour(wx.GetApp().settings.header_fg_color)
        window.SetFont(wx.GetApp().settings.header_text_font)

    # -----------------------------------------------------------------------

    def SetContent(self, window):
        """Assign the content window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("content")
        window.SetBackgroundColour(wx.GetApp().settings.bg_color)
        window.SetForegroundColour(wx.GetApp().settings.fg_color)
        window.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------

    def CreateActions(self, left_flags, right_flags=()):
        """Create the actions panel.

        Flags is a bit list of the following flags:
            - wx.ID_OK,
            - wx.ID_CANCEL,
            - wx.ID_YES,
            - wx.ID_NO,
            - wx.ID_APPLY,
            - wx.ID_CLOSE,
            - wx.ID_SAVE.

        :param left_flags: (list) Buttons to put at left
        :param right_flags: (list) Buttons to put at right

        """
        # Create the action panel and sizer
        panel = sppasPanel(self, name="actions")
        panel.SetMinSize(wx.Size(-1, wx.GetApp().settings.action_height))

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        if len(left_flags) > 0:
            for i, flag in enumerate(left_flags):
                button = self.__create_button(panel, flag)
                sizer.Add(button, 2, wx.LEFT | wx.EXPAND, 0)
                if len(right_flags) > 0 or i+1 < len(left_flags):
                    sizer.Add(self.VertLine(panel), 0, wx.EXPAND, 0)

        if len(right_flags) > 0:
            if len(left_flags) > 0:
                sizer.AddStretchSpacer(1)

            for flag in right_flags:
                button = self.__create_button(panel, flag)
                sizer.Add(self.VertLine(panel), 0, wx.EXPAND, 0)
                sizer.Add(button, 2, wx.RIGHT | wx.EXPAND, 0)

        # This action panel properties
        panel.SetSizer(sizer)
        self.SetActions(panel)

    # -----------------------------------------------------------------------

    def SetActions(self, window):
        """Assign the actions window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("actions")
        window.SetBackgroundColour(wx.GetApp().settings.action_bg_color)
        window.SetForegroundColour(wx.GetApp().settings.action_fg_color)
        window.SetFont(wx.GetApp().settings.action_text_font)

    # ------------------------------------------------------------------------

    def VertLine(self, parent, depth=1):
        """Return a vertical static line."""
        line = sppasStaticLine(parent, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(depth, -1))
        line.SetSize(wx.Size(depth, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        return line

    # ------------------------------------------------------------------------

    def HorizLine(self, parent, depth=2):
        """Return an horizontal static line."""
        nid = wx.NewId()
        line = sppasStaticLine(parent, nid, orient=wx.LI_HORIZONTAL,
                               name="line"+str(nid))
        line.SetMinSize(wx.Size(-1, depth))
        line.SetSize(wx.Size(-1, depth))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(depth)
        return line

    # ---------------------------------------------------------------------------
    # Put the whole content of the dialog in a sizer
    # ---------------------------------------------------------------------------

    def LayoutComponents(self):
        """Create the sizer and layout the components of the dialog."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add header
        header = self.FindWindow("header")
        if header is not None:
            sizer.Add(header, 0, wx.EXPAND, 0)
            sizer.Add(self.HorizLine(self), 0, wx.ALL | wx.EXPAND, 0)

        # Add content
        content = self.FindWindow("content")
        if content is not None:
            sizer.Add(content, 1, wx.EXPAND, 0)
        else:
            sizer.AddSpacer(1)

        # Add action buttons
        actions = self.FindWindow("actions")
        if actions is not None:
            sizer.Add(self.HorizLine(self), 0, wx.ALL | wx.EXPAND, 0)
            # proportion is 0 to ask the sizer to never hide the buttons
            sizer.Add(actions, 0, wx.EXPAND, 0)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        self.SetSizer(sizer)
        self.Layout()

    # -----------------------------------------------------------------------

    def UpdateUI(self):
        """Assign settings to self and children, then refresh."""
        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        for w in self.GetChildren():
            name = w.GetName()
            if name == "header":
                w.SetBackgroundColour(wx.GetApp().settings.header_bg_color)
                w.SetForegroundColour(wx.GetApp().settings.header_fg_color)
                w.SetFont(wx.GetApp().settings.header_text_font)
            elif name == "actions":
                w.SetBackgroundColour(wx.GetApp().settings.action_bg_color)
                w.SetForegroundColour(wx.GetApp().settings.action_fg_color)
                w.SetFont(wx.GetApp().settings.action_text_font)
            else:
                w.SetBackgroundColour(wx.GetApp().settings.bg_color)
                w.SetForegroundColour(wx.GetApp().settings.fg_color)
                w.SetFont(wx.GetApp().settings.text_font)
            w.Layout()
            w.Refresh()

        self.Layout()
        self.Refresh()

    # ---------------------------------------------------------------------------
    # Private

    def __create_button(self, parent, flag):
        """Create a button from a flag and return it.

        :param parent: (wx.Window)
        :param flag: (int)

        """
        btns = {
            wx.ID_OK: (MSG_ACTION_OK, "ok"),
            wx.ID_CANCEL: (MSG_ACTION_CANCEL, "cancel"),
            wx.ID_YES: (MSG_ACTION_YES, "yes"),
            wx.ID_NO: (MSG_ACTION_NO, "no"),
            wx.ID_APPLY: (MSG_ACTION_APPLY, "window-apply"),
            wx.ID_CLOSE: (MSG_ACTION_CLOSE, "window-close"),
            wx.ID_SAVE: (MSG_ACTION_SAVE, "save"),
        }
        btn = sppasBitmapTextButton(parent, label=btns[flag][0], name=btns[flag][1])
        btn.SetId(flag)

        if flag == wx.CANCEL:
            self.SetAffirmativeId(wx.ID_CANCEL)

        elif flag in (wx.CLOSE, wx.OK):
            btn.SetDefault()
            btn.SetFocus()
            self.SetAffirmativeId(flag)

        elif flag == wx.YES:
            self.SetAffirmativeId(wx.ID_YES)

        elif flag == wx.OK:
            btn.SetDefault()

        return btn

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

    # ---------------------------------------------------------------------------

    def __alpha_cycle_out(self, *args):
        """Fade-out opacity of the dialog."""
        self.opacity_out += self.deltaN
        if self.opacity_out >= 255:
            self.deltaN = -self.deltaN
            self.opacity_out = 255

            self.timer2.Stop()

        if self.opacity_out <= 0:
            self.deltaN = -self.deltaN
            self.opacity_out = 0
            wx.CallAfter(self.Destroy)

        self.SetTransparent(self.opacity_out)

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_size(value):
        """Return a proportional size value.

        :param value: (int)
        :returns: (int)

        """
        try:
            obj_size = int(float(value) * wx.GetApp().settings.size_coeff)
        except AttributeError:
            obj_size = int(value)
        return obj_size


