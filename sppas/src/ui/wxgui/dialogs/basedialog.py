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

    src.wxgui.views.basedialogs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      This is a base class for views.

"""
import wx

from sppas.src.ui.wxgui.sp_icons import APP_ICON
from sppas.src.ui.wxgui.sp_consts import DIALOG_STYLE
from sppas.src.ui.wxgui.sp_consts import FRAME_TITLE

from sppas.src.ui.wxgui.cutils.imageutils import spBitmap
from sppas.src.ui.wxgui.panels.buttons import ButtonCreator
import sppas.src.ui.wxgui.structs.prefs

# ----------------------------------------------------------------------------


class spBaseDialog(wx.Dialog):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      Base class for views in SPPAS.

    """
    def __init__(self, parent, preferences=None, title=""):
        """
        Constructor.

        :param parent: a wx window.
        :param preferences: (Preferences) a set of properties.
        :param title: String to append to the title of the dialog frame.

        """
        wx.Dialog.__init__(self, parent, -1, title=FRAME_TITLE+title, style=DIALOG_STYLE)

        if preferences is None:
            preferences = sppas.src.ui.wxgui.structs.prefs.Preferences()
        self.preferences = preferences

        # menu and toolbar
        self.toolbar = None
        self.btncreator = ButtonCreator(self.preferences)

        # icon
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(spBitmap(APP_ICON))
        self.SetIcon(_icon)

        # colors
        self.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        self.SetFont(self.preferences.GetValue('M_FONT'))

        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def CreateTitle(self, title_icon=APP_ICON, title_text="It's coffee time!"):
        """Create a layout including a nice bold-title with an icon.

        :param title_icon: (str) Name of the icon.
        :param title_text: (str) The title
        :returns: wx.Panel of a customized header title

        """
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        bitmap = spBitmap(title_icon, self.preferences.GetValue('M_BUTTON_ICONSIZE'), theme=self.preferences.GetValue('M_ICON_THEME'))
        sBmp = wx.StaticBitmap(panel, wx.ID_ANY, bitmap)

        paneltext = wx.Panel(self, -1, style=wx.NO_BORDER)
        paneltext.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        sizertext = wx.BoxSizer()
        text = wx.StaticText(paneltext, label=title_text, style=wx.ALIGN_CENTER)
        text.SetFont(self.preferences.GetValue('M_HEADER_FONT'))
        text.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        text.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        sizertext.Add(text, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        paneltext.SetSizer(sizertext)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sBmp, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=4)
        sizer.Add(paneltext, proportion=1, flag=wx.EXPAND | wx.ALL, border=4)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)

        return panel

    # -----------------------------------------------------------------------

    def CreateButton(self, icon, text, tooltip="", btnid=None):
        """
        Create a button and return it.

        :param icon: (str) Path to the icon file name.
        :param text: (str) Short text to print into the button.
        :param tooltip: (str) Long text to show when mouse is entering into the button.
        :param btnid: (wx.ID) A unique ID assigned to the button.

        """
        return self.btncreator.CreateButton(self, icon, text, tooltip, btnid)

    # -----------------------------------------------------------------------

    def CreateSaveButton(self, tooltip="Save"):
        return self.btncreator.CreateSaveButton(self, tooltip)

    def CreateCancelButton(self, tooltip="Cancel"):
        btn = self.btncreator.CreateCancelButton(self, tooltip)
        self.SetAffirmativeId(wx.ID_CANCEL)
        return btn

    def CreateCloseButton(self, tooltip="Close"):
        btn = self.btncreator.CreateCloseButton(self, tooltip)
        btn.SetDefault()
        btn.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        return btn

    def CreateOkayButton(self, tooltip="Okay"):
        btn = self.btncreator.CreateOkayButton(self, tooltip)
        btn.SetDefault()
        btn.SetFocus()
        self.SetAffirmativeId(wx.ID_OK)
        return btn

    def CreateYesButton(self, tooltip="Yes"):
        btn = self.btncreator.CreateYesButton(self, tooltip)
        btn.SetDefault()
        return btn

    def CreateNoButton(self, tooltip="No"):
        return self.btncreator.CreateNoButton(self, tooltip)

    # -----------------------------------------------------------------------

    def CreateButtonBox(self, leftbuttons=[],rightbuttons=[]):
        """
        Create a button box, with buttons to put at left and others at right.

        :param leftbuttons (list)
        :param rightbuttons (list)
        :returns: Sizer.

        """
        button_box = wx.BoxSizer(wx.HORIZONTAL)

        if len(leftbuttons)>0:
            for button in leftbuttons:
                button_box.Add(button, flag=wx.LEFT, border=2)

        if len(rightbuttons)>0:
            button_box.AddStretchSpacer()
            for button in rightbuttons:
                button_box.Add(button, flag=wx.RIGHT, border=2)

        return button_box

    # -----------------------------------------------------------------------

    def CreateTextCtrl(self, text, style=wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_NO_VSCROLL | wx.TE_WORDWRAP):
        """
        Return a wx.TextCtrl with appropriate font and style.

        """
        txt = wx.TextCtrl(self, wx.ID_ANY, value=text, style=style)
        font = self.preferences.GetValue('M_FONT')
        txt.SetFont(font)
        txt.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        txt.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))

        return txt

    # -----------------------------------------------------------------------

    def AddToolbar(self, leftobjects,rightobjects):
        """
        Add a toolbar to the dialog.

        :param leftobjects (list)
        :param rightobjects (list)

        """
        if len(leftobjects+rightobjects) == 0: return

        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)

        if len(leftobjects) > 0:
            for button in leftobjects:
                self.toolbar.Add(button, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=2)
            if len(rightobjects)>0:
                self.toolbar.AddStretchSpacer()

        if len(rightobjects) > 0:
            for button in rightobjects:
                self.toolbar.Add(button, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=2)

    # -----------------------------------------------------------------------

    def LayoutComponents(self, title, content, buttonbox=None):
        """Layout the components of the dialog.

            - title at the top
            - then eventually the toolbar
            - then the content
            - and eventually a button box at the bottom.

        """
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(title, 0, flag=wx.ALL | wx.EXPAND, border=2)
        if self.toolbar is not None:
            vbox.Add(self.toolbar, 0, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=2)
        vbox.Add(content, 2, flag=wx.ALL | wx.EXPAND, border=2)
        if buttonbox is not None:
            vbox.Add(buttonbox, 0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=2)
        self.SetSizerAndFit(vbox)

# ---------------------------------------------------------------------------


def DemoBaseDialog(parent, preferences=None):

    frame = spBaseDialog(parent, preferences)
    title = frame.CreateTitle(APP_ICON, "This is a BaseDialog frame...")
    btnclose = frame.CreateCloseButton()
    btnbox = frame.CreateButtonBox([], [btnclose])
    frame.AddToolbar([wx.StaticText(frame, label="toolbar is here", style=wx.ALIGN_CENTER)], [])
    frame.LayoutComponents(title, wx.Panel(frame, -1, size=(320, 200)), btnbox)
    frame.ShowModal()
    frame.Destroy()

# ---------------------------------------------------------------------------

if __name__ == "__main__":

    app = wx.PySimpleApp()
    DemoBaseDialog(None)
    app.MainLoop()

# ---------------------------------------------------------------------------
