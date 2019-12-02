#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: mainbuttons.py
# ----------------------------------------------------------------------------

import wx
import webbrowser

from sppas import msg
from sppas import u
from sppas import sg

from sppas.src.ui.tips import sppasTips
from sppas.src.ui.wxgui.panels.buttons import ButtonPanel, \
    ButtonMenuPanel, ImgPanel, ButtonCreator, ButtonToolbarPanel

from sppas.src.ui.wxgui.sp_icons import ANNOTATIONS_ICON
from sppas.src.ui.wxgui.sp_icons import COMPONENTS_ICON
from sppas.src.ui.wxgui.sp_icons import PLUGINS_ICON
from sppas.src.ui.wxgui.sp_icons import ABOUT_ICON
from sppas.src.ui.wxgui.sp_icons import HELP_ICON
from sppas.src.ui.wxgui.sp_icons import SETTINGS_ICON

from sppas.src.ui.wxgui.sp_icons import MENU_EXIT_ICON
from sppas.src.ui.wxgui.sp_icons import MENU_BUG_ICON
from sppas.src.ui.wxgui.sp_icons import MENU_FEEDBACK_ICON
from sppas.src.ui.wxgui.sp_icons import MENU_BACK_ICON
from sppas.src.ui.wxgui.sp_icons import MENU_CLOSE_ICON
from sppas.src.ui.wxgui.sp_icons import FORWARD_ICON

from sppas.src.ui.wxgui.sp_consts import ID_ANNOTATIONS
from sppas.src.ui.wxgui.sp_consts import ID_COMPONENTS
from sppas.src.ui.wxgui.sp_consts import ID_PLUGINS
from sppas.src.ui.wxgui.sp_consts import ID_FEEDBACK
from sppas.src.ui.wxgui.sp_consts import ID_EXT_BUG
from sppas.src.ui.wxgui.sp_consts import ID_ACTIONS
from sppas.src.ui.wxgui.sp_consts import ID_FILES

from sppas.src.ui.wxgui.views.feedback import ShowFeedbackDialog

# ----------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))

# -----------------------------------------------------------------------


class MainMenuPanel(wx.Panel):
    """Main frame menu panel.

    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BGM_COLOUR'))
        self.preferences = preferences
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.AddButton(wx.ID_EXIT, MENU_EXIT_ICON)
        self.sizer.AddStretchSpacer(20)
        self.AddButton(ID_EXT_BUG, MENU_BUG_ICON)
        self.AddButton(ID_FEEDBACK, MENU_FEEDBACK_ICON)

        self.SetSizer(self.sizer)
        self.SetMinSize((preferences.GetValue('M_MENU_ICONSIZE')+8, -1))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick)

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        ide = evt.GetId()

        if ide == ID_FEEDBACK:
            ShowFeedbackDialog(self, preferences=self.preferences)

        elif ide == ID_EXT_BUG:
            wx.BeginBusyCursor()
            try:
                webbrowser.open("https://github.com/brigittebigi/sppas/issues/", 1)
            except:
                pass
            wx.EndBusyCursor()

        else:
            obj = evt.GetEventObject()
            evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, obj.GetId())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def AddButton(self, idb, icon):
        btn = ButtonMenuPanel(self, idb, self.preferences, icon, None)
        self.sizer.Add(btn, proportion=0, flag=wx.ALL, border=4)

    def AddSpacer(self):
        self.sizer.AddStretchSpacer(1)

# ---------------------------------------------------------------------------


class MainTitlePanel(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      Main frame header panel.

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BGD_COLOUR'))

        s = wx.BoxSizer()
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_CENTER | \
                     wx.NO_BORDER
        text = wx.TextCtrl(self, value="", style=text_style)
        text.SetFont(preferences.GetValue('M_HEADER_FONT'))
        text.SetForegroundColour(preferences.GetValue('M_FG_COLOUR'))
        text.SetBackgroundColour(preferences.GetValue('M_BGD_COLOUR'))
        text.SetValue(sg.__name__ + " - " + sg.__title__)
        text.Bind(wx.EVT_LEFT_UP, self.OnButtonClick)
        s.Add(text, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)

        self.SetSizer(s)
        self.SetMinSize((-1, preferences.GetValue('M_MENU_ICONSIZE')+8))

        self.Bind(wx.EVT_LEFT_UP, self.OnButtonClick)

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        wx.BeginBusyCursor()
        try:
            webbrowser.open(sg.__url__, 1)
        except:
            pass
        wx.EndBusyCursor()

# ----------------------------------------------------------------------------


class MainToolbarPanel(wx.Panel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main toolbar panel.

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))

        self.preferences = preferences
        self.buttons = []
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetSizer(self.sizer)
        self.SetMinSize((preferences.GetValue('M_TOOLBAR_ICONSIZE')+8, -1))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick)

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        obj = evt.GetEventObject()
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, obj.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    def AddButton(self, idb, icon, text, tooltip=None, activated=True):
        btn = ButtonToolbarPanel(self, idb, self.preferences, icon, text, tooltip, activated)
        self.sizer.Add(btn, proportion=1, flag=wx.ALL, border=2)
        self.buttons.append(btn)
        self.Layout()

    def AddSpacer(self):
        self.sizer.AddStretchSpacer(1)

    # -----------------------------------------------------------------------

    def SetPrefs(self, prefs):
        self.preferences = prefs
        self.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        for btn in self.buttons:
            btn.SetPrefs(self.preferences)

# ----------------------------------------------------------------------------


class MainActionsPanel(wx.Panel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main frame buttons panel.

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))
        self._prefs = preferences

        content = self.__create_buttons()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(content, proportion=1, flag=wx.EXPAND | wx.ALL, border=0)

        self.Bind(wx.EVT_BUTTON, self.OnButtonClick)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def __create_buttons(self):
        """Create buttons to call tools."""

        annotateButton = ButtonPanel(self, ID_ANNOTATIONS,
                                     self._prefs,
                                     ANNOTATIONS_ICON,
                                     _(" Annotate "),
                                     "Create automatically,annotations")

        analyzeButton = ButtonPanel(self, ID_COMPONENTS,
                                    self._prefs,
                                    COMPONENTS_ICON,
                                    _(" Analyze "),
                                    "Manage any,annotated data")

        pluginsButton = ButtonPanel(self, ID_PLUGINS,
                                    self._prefs,
                                    PLUGINS_ICON,
                                    _(" Plugins "),
                                    "Extended,features",
                                    activated=True)

        settingsButton = ButtonPanel(self, wx.ID_PREFERENCES,
                                     self._prefs,
                                     SETTINGS_ICON,
                                     _(" Settings "),
                                     "Customization")

        helpButton = ButtonPanel(self, wx.ID_HELP,
                                 self._prefs,
                                 HELP_ICON,
                                 _(" Help "),
                                 "Documentation")

        aboutButton = ButtonPanel(self, wx.ID_ABOUT,
                                  self._prefs,
                                  ABOUT_ICON,
                                  _(" About "),
                                  "Know more")

        _box = wx.GridBagSizer()
        _box.Add(annotateButton, pos=(0, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add(pluginsButton,  pos=(1, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add(analyzeButton,  pos=(0, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add(settingsButton, pos=(1, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add(aboutButton,    pos=(2, 0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)
        _box.Add(helpButton,     pos=(2, 1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, border=2)

        _box.AddGrowableCol(0)
        _box.AddGrowableCol(1)
        _box.AddGrowableRow(0)
        _box.AddGrowableRow(1)
        _box.AddGrowableRow(2)

        return _box

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        obj = evt.GetEventObject()
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, obj.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------


class MainActionsMenuPanel(wx.Panel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main actions menu panel.

    """
    def __init__(self, parent, preferences, icon=MENU_BACK_ICON):
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BGM_COLOUR'))
        self._prefs = preferences

        self.backButton = ImgPanel(self, preferences.GetValue('M_MENU_ICONSIZE'), icon, self._prefs)
        font = preferences.GetValue('M_FONT')

        paneltext = wx.Panel(self, -1, style=wx.NO_BORDER)
        paneltext.SetBackgroundColour(preferences.GetValue('M_BGM_COLOUR'))
        sizertext = wx.BoxSizer()
        self.text = wx.TextCtrl(paneltext, -1, style=wx.NO_BORDER)
        self.text.SetEditable(False)
        font.SetWeight(wx.BOLD)
        self.text.SetFont(font)
        self.text.SetBackgroundColour(preferences.GetValue('M_BGM_COLOUR'))
        self.text.SetForegroundColour(wx.WHITE)
        self.text.SetMinSize((200, -1))
        sizertext.Add(self.text, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        paneltext.SetSizer(sizertext)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.backButton, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=2)
        sizer.Add(paneltext, proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
        self.SetSizer(sizer)
        self.SetMinSize((-1, preferences.GetValue('M_MENU_ICONSIZE')+4))

        self.Bind(wx.EVT_LEFT_UP, self.OnButtonClick)

    # -----------------------------------------------------------------------

    def OnButtonClick(self, evt):
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_ACTIONS)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def ShowBack(self, state=True, text=""):
        self.text.SetValue(text)
        if state is True:
            self.backButton.Show()
        else:
            self.backButton.Hide()
        self.Refresh()

# ----------------------------------------------------------------------------


class MainTooltips(wx.Panel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Main tooltips panel.

    """
    def __init__(self, parent, preferences):
        wx.Panel.__init__(self, parent, -1, style=wx.RAISED_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BGD_COLOUR'))
        self._prefs = preferences
        self.tips = sppasTips()

        menu = self._create_menu()
        self.text = self._create_content()
        button = self._create_button()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(menu, proportion=0, flag=wx.EXPAND, border=0)
        sizer.Add(self.text, proportion=2, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=10)
        sizer.Add(button, proportion=0, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=2)
        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnClose)

    # -----------------------------------------------------------------------

    def _create_menu(self):
        return MainActionsMenuPanel(self, self._prefs, icon=MENU_CLOSE_ICON)

    def _create_content(self):
        txt = wx.TextCtrl(self, wx.ID_ANY,
                          value=self.tips.get_message(),
                          style=wx.TE_READONLY | wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_NO_VSCROLL | wx.TE_WORDWRAP)
        font = self._prefs.GetValue('M_FONT')
        txt.SetFont(font)
        txt.SetForegroundColour(self._prefs.GetValue('M_FG_COLOUR'))
        txt.SetBackgroundColour(self._prefs.GetValue('M_BGD_COLOUR'))
        txt.SetMinSize((300, 48))
        return txt

    def _create_button(self):
        btncreator = ButtonCreator(self._prefs)
        btn = btncreator.CreateButton(self, FORWARD_ICON, " Next tip", "Show a random tip", wx.NewId())
        btn.SetBackgroundColour(self._prefs.GetValue('M_BG_COLOUR'))
        btn.Bind(wx.EVT_BUTTON, self.OnNext)
        return btn

    # -----------------------------------------------------------------------

    def OnClose(self, event):
        self.Hide()
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_FILES)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def OnNext(self, event):
        self.text.SetValue(self.tips.get_message())
        self.Refresh()
