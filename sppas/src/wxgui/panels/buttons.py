#!/usr/bin/env python2
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
# File: buttons.py
# ----------------------------------------------------------------------------

import wx

from wxgui.cutils.imageutils import spBitmap
from wxgui.cutils.ctrlutils  import CreateGenButton
from wxgui.cutils.colorutils import LightenColor

from wxgui.sp_consts import BUTTON_ICONSIZE, MENU_ICONSIZE, TB_ICONSIZE

from wxgui.sp_icons import CLOSE_ICON
from wxgui.sp_icons import APPLY_ICON
from wxgui.sp_icons import CANCEL_ICON
from wxgui.sp_icons import SAVE_FILE
from wxgui.sp_icons import YES_ICON
from wxgui.sp_icons import NO_ICON
from wxgui.sp_icons import OKAY_ICON

# ---------------------------------------------------------------------------

class ButtonCreator:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Create buttons.

    """
    def __init__(self, preferences):
        self.preferences = preferences

    # -----------------------------------------------------------------------

    def CreateButton(self, parent, icon, text, tooltip="", btnid=None):
        """
        Create a button and return it.

        @param icon (str) Path to the icon file name.
        @param text (str) Short text to print into the button.
        @param tooltip (str) Long text to show when mouse is entering into the button.
        @param btnid (wx.ID) A unique ID assigned to the button.

        """
        if btnid is None:
            btnid = wx.NewId()
        bmp = spBitmap(icon, BUTTON_ICONSIZE, theme=self.preferences.GetValue('M_ICON_THEME'))
        btn = CreateGenButton(parent, btnid, bmp, text=text, tooltip=tooltip, colour=None)
        btn.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        btn.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        btn.SetFont( self.preferences.GetValue('M_FONT') )

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

class ImgPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Simple panel with an image.

    """
    def __init__(self, parent, bmpsize, bmpname):
        wx.Panel.__init__(self, parent)

        bitmap = spBitmap( bmpname, size=bmpsize )
        sBmp = wx.StaticBitmap(self, wx.ID_ANY, bitmap)

        sizer = wx.BoxSizer()
        sizer.Add(sBmp, proportion=1, flag=wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, border=0)
        self.SetBackgroundColour( parent.GetBackgroundColour() )
        self.SetSizerAndFit(sizer)

        sBmp.Bind(wx.EVT_LEFT_UP, self.OnEvent)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEvent)

    def OnEvent(self, evt):
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------

class ButtonPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Panel imitating behaviors of a complex button.

    """
    def __init__(self, parent, idb, preferences, bmp, text, subtext=None, tooltip=None, activated=True):
        wx.Panel.__init__(self, parent, idb, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BGD_COLOUR') )
        self.SetFont( preferences.GetValue('M_FONT') )

        self._prefs = preferences
        self.activated = activated

        content = self.create_content(bmp, text, subtext)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(content, flag=wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, border=2)
        self.SetSizer(sizer)
        self.FitInside()
        #self.SetAutoLayout( True )
        if tooltip is not None:
            self.SetToolTipString( tooltip )

    def create_content(self, bmpname, textstr, subtextstr=None):
        panel = wx.Panel(self)
        panel.SetBackgroundColour( self._prefs.GetValue('M_BGD_COLOUR') )
        sizer = wx.BoxSizer(wx.VERTICAL)

        font = self.GetFont()

        if bmpname is not None:
            bmp = ImgPanel(panel, BUTTON_ICONSIZE, bmpname)
            sizer.Add(bmp, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=8)

        text = wx.StaticText(panel, -1, textstr)
        font.SetWeight(wx.BOLD)
        text.SetFont( font )
        text.SetBackgroundColour( self._prefs.GetValue('M_BGD_COLOUR') )
        text.SetForegroundColour( self._prefs.GetValue('M_FG_COLOUR') )

        text.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
        sizer.Add(text, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=2)

        font.SetWeight(wx.NORMAL)
        if subtextstr is not None:
            tabtexts = subtextstr.split(',')
            for i,t in enumerate(tabtexts):
                if (i+1)<len(tabtexts):
                    subtext = wx.StaticText(panel, -1, t+",")
                else:
                    subtext = wx.StaticText(panel, -1, t)
                subtext.SetBackgroundColour( self._prefs.GetValue('M_BGD_COLOUR') )
                subtext.SetForegroundColour( self._prefs.GetValue('M_FGD_COLOUR') )
                subtext.SetFont( font )
                subtext.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
                sizer.Add(subtext, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=2)

        panel.SetSizer(sizer)
        panel.SetAutoLayout( True )

        panel.Bind(wx.EVT_LEFT_UP,      self.OnButtonLeftUp)
        panel.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
        panel.Bind(wx.EVT_LEAVE_WINDOW, self.OnButtonLeave)
        panel.SetMinSize((128,128))

        return panel


    def OnButtonEnter(self, event):
        if self.activated is True:
            self.SetBackgroundColour( self._prefs.GetValue('M_FGD_COLOUR') )
            self.Refresh()

    def OnButtonLeave(self, event):
        if self.activated is True:
            self.SetBackgroundColour( self._prefs.GetValue('M_BGD_COLOUR') )
            self.Refresh()

    def OnButtonLeftUp(self, event):
        if self.activated is True:
            self.SetBackgroundColour( self._prefs.GetValue('M_BGD_COLOUR') )
            self.Refresh()
            evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------

class ButtonToolbarPanel( wx.Panel ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Panel imitating behaviors of a complex button.

    """
    def __init__(self, parent, idb, preferences, bmp, text, tooltip=None, activated=True):
        wx.Panel.__init__(self, parent, idb, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BG_COLOUR') )
        self.SetFont( preferences.GetValue('M_FONT') )

        self._prefs = preferences
        self.activated = activated

        content = self.create_content(bmp, text)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(content, flag=wx.EXPAND|wx.BOTTOM|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, border=2)
        self.SetSizer(sizer)
        self.FitInside()
        if tooltip is not None:
            self.SetToolTipString( tooltip )

    def create_content(self, bmpname, textstr):
        panel = wx.Panel(self)
        panel.SetBackgroundColour( self._prefs.GetValue('M_BG_COLOUR') )
        sizer = wx.BoxSizer(wx.VERTICAL)

        if bmpname is not None:
            bmp = ImgPanel(panel, TB_ICONSIZE, bmpname)
            sizer.Add(bmp, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=8)
            bmp.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
            bmp.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)

        text = wx.StaticText(panel, -1, textstr)
        text.SetBackgroundColour( self._prefs.GetValue('M_BG_COLOUR') )
        text.SetForegroundColour( self._prefs.GetValue('M_FG_COLOUR') )
        text.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
        text.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
        sizer.Add(text, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=2)

        panel.SetSizer(sizer)
        panel.SetAutoLayout( True )

        panel.Bind(wx.EVT_LEFT_UP,      self.OnButtonLeftUp)
        panel.Bind(wx.EVT_ENTER_WINDOW, self.OnButtonEnter)
        panel.Bind(wx.EVT_LEAVE_WINDOW, self.OnButtonLeave)
        panel.SetMinSize((48,64))

        return panel


    def OnButtonEnter(self, event):
        if self.activated is True:
            self.SetBackgroundColour( self._prefs.GetValue('M_FGD_COLOUR') )
            self.Refresh()

    def OnButtonLeave(self, event):
        if self.activated is True:
            self.SetBackgroundColour( self._prefs.GetValue('M_BG_COLOUR') )
            self.Refresh()

    def OnButtonLeftUp(self, event):
        if self.activated is True:
            self.SetBackgroundColour( self._prefs.GetValue('M_BG_COLOUR') )
            self.Refresh()
            evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent(), evt)

    def Enable(self, value):
        self.activated = value
        self.SetBackgroundColour( self._prefs.GetValue('M_BG_COLOUR') )
        self.Refresh()

    def SetPrefs(self, prefs):
        self._prefs = prefs
        self.Refresh()

# ---------------------------------------------------------------------------

class ButtonMenuPanel( wx.Panel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Panel imitating behaviors of a menu button.

    """
    def __init__(self, parent, idb, preferences, bmpname, textstr):
        wx.Panel.__init__(self, parent, idb, style=wx.NO_BORDER)
        self.SetBackgroundColour( preferences.GetValue('M_BGM_COLOUR') )

        self._prefs = preferences

        sizer = wx.BoxSizer(wx.VERTICAL)
        if bmpname is not None:
            bmp = ImgPanel(self, MENU_ICONSIZE, bmpname)
            bmp.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
            sizer.Add(bmp, flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER, border=0)

        if textstr is not None:
            text = wx.StaticText(self, -1, textstr)
            text.SetBackgroundColour( self.GetBackgroundColour() )
            text.SetForegroundColour( preferences.GetValue('M_FGM_COLOUR') )
            text.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)
            sizer.Add(text, flag=wx.ALL|wx.ALIGN_CENTER, border=2)

        self.Bind(wx.EVT_LEFT_UP, self.OnButtonLeftUp)

        self.SetSizer(sizer)
        self.SetAutoLayout( True )


    def OnButtonLeftUp(self, event):
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------