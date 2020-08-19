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

    src.wxgui.anz_panels.buttons.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      This is a base class for buttons.

"""
import wx

from sppas.src.ui.wxgui.cutils.imageutils import spBitmap
from sppas.src.ui.wxgui.cutils.ctrlutils import CreateGenButton

from sppas.src.ui.wxgui.sp_icons import CLOSE_ICON
from sppas.src.ui.wxgui.sp_icons import CANCEL_ICON
from sppas.src.ui.wxgui.sp_icons import SAVE_FILE
from sppas.src.ui.wxgui.sp_icons import YES_ICON
from sppas.src.ui.wxgui.sp_icons import NO_ICON
from sppas.src.ui.wxgui.sp_icons import OKAY_ICON

# ---------------------------------------------------------------------------


class ButtonCreator(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      Create buttons.

    """
    def __init__(self, preferences):
        self.preferences = preferences

    # -----------------------------------------------------------------------

    def CreateButton(self, parent, icon, text, tooltip="", btnid=None):
        """
        Create a button and return it.

        :param icon: (str) Path to the icon file name.
        :param text: (str) Short text to print into the button.
        :param tooltip: (str) Long text to show when mouse is entering into the button.
        :param btnid: (wx.ID) A unique ID assigned to the button.

        """
        if btnid is None:
            btnid = wx.NewId()

        bmp = spBitmap(icon,
                       size=self.preferences.GetValue('M_BUTTON_ICONSIZE'),
                       theme=self.preferences.GetValue('M_ICON_THEME'))

        btn = CreateGenButton(parent, btnid, bmp, text=text, tooltip=tooltip, colour=None)
        btn.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        btn.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        btn.SetFont(self.preferences.GetValue('M_FONT'))

        return btn

    # -----------------------------------------------------------------------

    def CreateSaveButton(self, parent, tooltip="Save"):
        return self.CreateButton(parent, SAVE_FILE, "Save", tooltip, btnid=wx.ID_SAVE)

    def CreateCancelButton(self, parent, tooltip="Cancel"):
        return self.CreateButton(parent, CANCEL_ICON, "Cancel", tooltip, btnid=wx.ID_CANCEL)

    def CreateCloseButton(self, parent, tooltip="Close"):
        return self.CreateButton(parent, CLOSE_ICON, "Close", tooltip, btnid=wx.ID_CLOSE)

    def CreateOkayButton(self, parent, tooltip="Okay"):
        return self.CreateButton(parent, OKAY_ICON, " OK ", tooltip, btnid=wx.ID_OK)

    def CreateYesButton(self, parent, tooltip="Yes"):
        return self.CreateButton(parent, YES_ICON, " Yes ", tooltip, btnid=wx.ID_YES)

    def CreateNoButton(self, parent, tooltip="No"):
        return self.CreateButton(parent, NO_ICON, " No ", tooltip, btnid=wx.ID_NO)

# ---------------------------------------------------------------------------


class ImgPanel(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Simple panel with an image.

    """
    def __init__(self, parent, bmpsize, bmpname, prefsIO):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(parent.GetBackgroundColour())

        bitmap = spBitmap(bmpname, size=bmpsize, theme=prefsIO.GetValue('M_ICON_THEME'))
        sBmp = wx.StaticBitmap(self, wx.ID_ANY, bitmap)
        sBmp.SetBackgroundColour(parent.GetBackgroundColour())

        sizer = wx.BoxSizer()
        sizer.Add(sBmp, 1, wx.ALIGN_CENTER, 0)
        self.SetSizerAndFit(sizer)

        sBmp.Bind(wx.EVT_LEFT_UP,      self.ProcessEvent)
        sBmp.Bind(wx.EVT_ENTER_WINDOW, self.ProcessEvent)

    def ProcessEvent(self, evt):
        #evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)
        return False

# ---------------------------------------------------------------------------


class ButtonPanel(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      Panel imitating behaviors of a complex button.

    """
    def __init__(self, parent, idb, preferences, bmp, text, subtext=None, tooltip=None, activated=True):
        wx.Panel.__init__(self, parent, idb, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BGD_COLOUR'))
        self.SetFont(preferences.GetValue('M_FONT'))

        self._prefs = preferences
        self.activated = activated
        self.childenter = False

        self.contentpanel = self.create_content(bmp, text, subtext)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.contentpanel, 1, wx.EXPAND | wx.ALIGN_CENTER)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.FitInside()
        if tooltip is not None:
            self.SetToolTipString(tooltip)

    def create_content(self, bmpname, textstr, subtextstr=None):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(self._prefs.GetValue('M_BGD_COLOUR'))
        sizer = wx.BoxSizer(wx.VERTICAL)

        font = self.GetFont()
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_CENTER | \
                     wx.NO_BORDER
        if bmpname is not None:
            bmp = ImgPanel(panel, self._prefs.GetValue('M_BUTTON_ICONSIZE'), bmpname, self._prefs)
            sizer.Add(bmp, 1, flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER, border=4)

        text = wx.TextCtrl(panel, value="", style=text_style)
        font.SetWeight(wx.BOLD)
        text.SetFont(font)
        text.SetBackgroundColour(self._prefs.GetValue('M_BGD_COLOUR'))
        text.SetForegroundColour(self._prefs.GetValue('M_FG_COLOUR'))
        text.SetValue(textstr)
        text.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
        text.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
        sizer.Add(text, 1, flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER, border=4)

        font.SetWeight(wx.NORMAL)
        if subtextstr is not None:
            tabtexts = subtextstr.split(',')
            for i, t in enumerate(tabtexts):
                subtext = wx.TextCtrl(panel, value="", style=text_style)
                subtext.SetBackgroundColour(self._prefs.GetValue('M_BGD_COLOUR'))
                subtext.SetForegroundColour(self._prefs.GetValue('M_FGD_COLOUR'))
                subtext.SetFont(font)
                subtext.SetValue(t)
                subtext.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
                subtext.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
                sizer.Add(subtext, 0, flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER, border=2)

        panel.SetSizer(sizer)
        panel.SetMinSize(wx.Size(128, 128))

        panel.Bind(wx.EVT_LEFT_UP,      self.OnButtonLeftUp)
        panel.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
        panel.Bind(wx.EVT_LEAVE_WINDOW, self.OnButtonLeave)

        return panel

    def OnButtonEnter(self, event):
        if self.activated is True:
            ide = event.GetEventObject().GetId()
            if (wx.Platform == "__WXMSW__" and ide == self.contentpanel.GetId()) or wx.Platform != "__WXMSW__":
                self.SetBackgroundColour(self._prefs.GetValue('M_FGD_COLOUR'))
                self.Refresh()
                self.childenter = False
            else:
                self.childenter = True

    def OnButtonLeave(self, event):
        if self.activated is True:
            if (wx.Platform == "__WXMSW__" and self.childenter is False) or wx.Platform != "__WXMSW__":
                self.SetBackgroundColour(self._prefs.GetValue('M_BGD_COLOUR'))
                self.Refresh()

    def OnButtonLeftUp(self, event):
        if self.activated is True:
            self.SetBackgroundColour(self._prefs.GetValue('M_BGD_COLOUR'))
            self.Refresh()
            evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------


class ButtonToolbarPanel(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    :summary:      Panel imitating behaviors of a complex button.

    """
    def __init__(self, parent, idb, preferences, bmp, text, tooltip=None, activated=True):
        wx.Panel.__init__(self, parent, idb, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))
        self.SetFont(preferences.GetValue('M_FONT'))

        self._prefs = preferences
        self.activated = activated
        self.childenter = False

        self.contentpanel = self.create_content(bmp, text)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.contentpanel, flag=wx.EXPAND|wx.BOTTOM|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, border=2)
        self.SetSizer(sizer)

        self.FitInside()
        if tooltip is not None:
            self.SetToolTipString(tooltip)

    def create_content(self, bmpname, textstr):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(self._prefs.GetValue('M_BG_COLOUR'))
        sizer = wx.BoxSizer(wx.VERTICAL)

        if bmpname is not None:
            bmp = ImgPanel(panel, self._prefs.GetValue('M_TOOLBAR_ICONSIZE'), bmpname, self._prefs)
            sizer.Add(bmp, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=8)

        font = self._prefs.GetValue('M_TOOLBAR_FONT')
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_CENTER | \
                     wx.NO_BORDER
        text = wx.TextCtrl(panel, value="", style=text_style)
        text.SetBackgroundColour(self._prefs.GetValue('M_BG_COLOUR'))
        text.SetForegroundColour(self._prefs.GetValue('M_FG_COLOUR'))
        text.SetFont(font)
        text.SetValue(textstr)
        text.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
        text.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
        sizer.Add(text, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=2)

        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)

        panel.Bind(wx.EVT_LEFT_UP,      self.OnButtonLeftUp)
        panel.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
        panel.Bind(wx.EVT_LEAVE_WINDOW, self.OnButtonLeave)
        panel.SetMinSize((48,64))

        return panel


    def OnButtonEnter(self, event):
        if self.activated is True:
            ide = event.GetEventObject().GetId()
            if (wx.Platform == "__WXMSW__" and ide == self.contentpanel.GetId()) or wx.Platform != "__WXMSW__":
                self.SetBackgroundColour(self._prefs.GetValue('M_FGD_COLOUR'))
                self.Refresh()
                self.childenter = False
            else:
                self.childenter = True

    def OnButtonLeave(self, event):
        if self.activated is True:
            if (wx.Platform == "__WXMSW__" and self.childenter is False) or wx.Platform != "__WXMSW__":
                self.SetBackgroundColour(self._prefs.GetValue('M_BG_COLOUR'))
                self.Refresh()

    def OnButtonLeftUp(self, event):
        if self.activated is True:
            self.SetBackgroundColour(self._prefs.GetValue('M_BG_COLOUR'))
            self.Refresh()
            evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    def Enable(self, value):
        self.activated = value
        self.SetBackgroundColour(self._prefs.GetValue('M_BG_COLOUR'))
        self.Refresh()

    def SetPrefs(self, prefs):
        self._prefs = prefs
        self.Refresh()

# ---------------------------------------------------------------------------


class ButtonMenuPanel(wx.Panel):
    """
    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL
    @summary: Panel imitating behaviors of a menu button.

    """
    def __init__(self, parent, idb, preferences, bmpname, textstr):
        wx.Panel.__init__(self, parent, idb, style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BGM_COLOUR'))

        self._prefs = preferences

        sizer = wx.BoxSizer(wx.VERTICAL)
        if bmpname is not None:
            bmp = ImgPanel(self, preferences.GetValue('M_MENU_ICONSIZE'), bmpname, self._prefs)
            bmp.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
            sizer.Add(bmp, flag=wx.ALIGN_CENTER_HORIZONTAL, border=0)

        if textstr is not None:
            text_style = wx.TAB_TRAVERSAL | \
                         wx.TE_READONLY | \
                         wx.TE_BESTWRAP | \
                         wx.TE_CENTER | \
                         wx.NO_BORDER
            text = wx.TextCtrl(self, value="", style=text_style)
            text.SetBackgroundColour(self.GetBackgroundColour())
            text.SetForegroundColour(preferences.GetValue('M_FGM_COLOUR'))
            text.SetValue(textstr)
            text.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
            sizer.Add(text, flag=wx.ALL|wx.ALIGN_CENTER, border=2)

        self.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)


    def OnButtonLeftUp(self, event):
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------
