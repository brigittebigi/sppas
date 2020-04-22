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
# File: msgdialogs.py
# ---------------------------------------------------------------------------
import sys
import os
import wx

sppas=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
sys.path.append(sppas)


from sppas.src.ui.wxgui.sp_icons import MESSAGE_ICON
from sppas.src.ui.wxgui.sp_icons import DLG_INFO_ICON
from sppas.src.ui.wxgui.sp_icons import DLG_WARN_ICON
from sppas.src.ui.wxgui.sp_icons import DLG_ERR_ICON
from sppas.src.ui.wxgui.sp_icons import DLG_QUEST_ICON

from .basedialog import spBaseDialog

# ----------------------------------------------------------------------------


class spBaseMessageDialog(spBaseDialog):

    def __init__(self, parent, preferences, contentmsg, style=wx.ICON_INFORMATION):
        """
        Constructor.

        @param parent is the parent wx object.
        @param preferences (Preferences)
        @param filename (str) the file to display in this frame.
        @param style: ONE of wx.ICON_INFORMATION, wx.ICON_ERROR, wx.ICON_EXCLAMATION, wx.YES_NO

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Message")
        wx.GetApp().SetAppName("question")

        if style == wx.ICON_ERROR:
            titlebox = self.CreateTitle(DLG_ERR_ICON, "Error")

        elif style == wx.ICON_WARNING:
            titlebox = self.CreateTitle(DLG_WARN_ICON, "Warning")

        elif style == wx.YES_NO:
            titlebox = self.CreateTitle(DLG_QUEST_ICON, "Question")

        else:
            titlebox = self.CreateTitle(DLG_INFO_ICON, "Information")

        contentbox = self._create_content(contentmsg)
        buttonbox = self._create_buttons()

        self.LayoutComponents(titlebox,
                               contentbox,
                               buttonbox)

    def _create_content(self, message):
        txt = self.CreateTextCtrl(message)
        txt.SetMinSize((300, -1))
        return txt

    def _create_buttons(self):
        raise NotImplementedError

# ---------------------------------------------------------------------------


class YesNoQuestion(spBaseMessageDialog):

    def __init__(self, parent, preferences, contentmsg):
        spBaseMessageDialog.__init__(self, parent, preferences, contentmsg, style=wx.YES_NO)

    def _create_buttons(self):
        yes = self.CreateYesButton()
        no = self.CreateNoButton()
        no.Bind(wx.EVT_BUTTON, self._on_no, no)
        self.SetAffirmativeId(wx.ID_YES)
        return self.CreateButtonBox([no], [yes])

    def _on_no(self, evt):
        # self.Destroy() # does not work on MacOS
        self.Close()
        self.SetReturnCode(wx.ID_NO)

# ---------------------------------------------------------------------------


class Information(spBaseMessageDialog):

    def __init__(self, parent, preferences, contentmsg, style=wx.YES_NO):
        spBaseMessageDialog.__init__(self, parent, preferences, contentmsg, style)

    def _create_buttons(self):
        okay = self.CreateOkayButton()
        self.SetAffirmativeId(wx.ID_OK)
        return self.CreateButtonBox([],[okay])

# ---------------------------------------------------------------------------


class Choice(spBaseDialog):

    def __init__(self, parent, preferences, contentmsg, choices):
        """
        Constructor.

        @param parent is the parent wx object.
        @param preferences (Preferences)
        @param filename (str) the file to display in this frame.
        @param style: ONE of wx.ICON_INFORMATION, wx.ICON_ERROR, wx.ICON_EXCLAMATION, wx.YES_NO

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Choice")
        wx.GetApp().SetAppName("question")

        titlebox   = self.CreateTitle(DLG_QUEST_ICON, "Question")
        contentbox = self._create_content(contentmsg,choices)
        buttonbox  = self._create_buttons()

        self.LayoutComponents(titlebox,
                               contentbox,
                               buttonbox)

    def _create_content(self,message,choices):
        sizer = wx.BoxSizer(wx.VERTICAL)
        txt = wx.TextCtrl(self, wx.ID_ANY, value=message, style=wx.TE_READONLY|wx.NO_BORDER)
        font = self.preferences.GetValue('M_FONT')
        txt.SetFont(font)
        txt.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        txt.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        txt.SetMinSize((300,-1))

        self.choicectrl = wx.ListBox(self, -1, choices=choices)
        self.choicectrl.SetSelection(0)
        self.choicectrl.SetBackgroundColour(self.preferences.GetValue('M_BG_COLOUR'))
        self.choicectrl.SetForegroundColour(self.preferences.GetValue('M_FG_COLOUR'))
        self.choicectrl.SetFont(font)

        sizer.Add(txt, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.choicectrl, 1, wx.ALL | wx.EXPAND, 10)

        return sizer

    def _create_buttons(self):
        okay = self.CreateOkayButton()
        cancel = self.CreateCancelButton()
        cancel.Bind(wx.EVT_BUTTON, self._on_cancel, cancel)
        self.SetAffirmativeId(wx.ID_OK)
        return self.CreateButtonBox([cancel],[okay])

    def _on_cancel(self, evt):
        #self.Destroy() # does not work on MacOS
        self.Close()
        self.SetReturnCode(wx.ID_CANCEL)

    def SetSelection(self, idx):
        self.choicectrl.SetSelection(idx)

    def GetSelection(self):
        return self.choicectrl.GetSelection()

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


def ShowYesNoQuestion(parent, preferences, contentmsg):
    dlg = YesNoQuestion(parent, preferences, contentmsg)
    return dlg.ShowModal()

# ---------------------------------------------------------------------------


def ShowInformation(parent, preferences, contentmsg, style=wx.ICON_INFORMATION):
    dlg = Information(parent, preferences, contentmsg, style)
    return dlg.ShowModal()

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


def DemoBaseDialog(parent, preferences=None):
    """A simple demonstration of SPPAS message views."""

    def _on_yesno(evt):
        dlg = YesNoQuestion(frame, preferences, "This is the message to show.")
        #res = ShowYesNoQuestion(frame, preferences,)
        res = dlg.ShowModal()
        if res == wx.ID_YES:
            ShowInformation(frame, preferences, "You clicked the ""Yes"" button")
        elif res == wx.ID_NO:
            ShowInformation(frame, preferences, "You clicked the ""No"" button")
        else:
            print("there's a bug! return value is " + res)
        dlg.Destroy()

    def _on_choice(evt):
        dlg = Choice(frame, preferences,"This is the message to describe choices:", ['choice 0','choice 1','choice 2'])
        if dlg.ShowModal() == wx.ID_OK:
            c = dlg.GetSelection()
            ShowInformation(frame, preferences, "Your choice is: %d" % c)
        else:
            ShowInformation(frame, preferences, "You clicked the ""Cancel"" button")
        dlg.Destroy()

    def _on_info(evt):
        ShowInformation(frame, preferences, "This is an information message with non-UTF8 characters: éàçù.", style=wx.ICON_INFORMATION)

    def _on_error(evt):
        ShowInformation(frame, preferences, "This is an error message.", style=wx.ICON_ERROR)

    def _on_warning(evt):
        ShowInformation(frame, preferences, "This is a warning message.", style=wx.ICON_WARNING)

    frame = spBaseDialog(parent, preferences)
    title = frame.CreateTitle(MESSAGE_ICON, "Message views demonstration")
    btninfo   = frame.CreateButton(DLG_INFO_ICON,"Test info", "This is a tooltip!", btnid=wx.NewId())
    btnyesno  = frame.CreateButton(DLG_QUEST_ICON,"Test yes-no", "This is a tooltip!", btnid=wx.NewId())
    btnerror  = frame.CreateButton(DLG_ERR_ICON,"Test error", "This is a tooltip!", btnid=wx.NewId())
    btnwarn   = frame.CreateButton(DLG_WARN_ICON,"Test warning", "This is a tooltip!", btnid=wx.NewId())
    btnchoice = frame.CreateButton(DLG_QUEST_ICON,"Test choice", "This is a tooltip!", btnid=wx.NewId())

    btnclose  = frame.CreateCloseButton()
    btnbox    = frame.CreateButtonBox([btnyesno,btninfo,btnwarn,btnerror,btnchoice], [btnclose])

    frame.LayoutComponents(title, wx.Panel(frame, -1, size=(320,200)), btnbox)

    btninfo.Bind(wx.EVT_BUTTON, _on_info)
    btnyesno.Bind(wx.EVT_BUTTON, _on_yesno)
    btnerror.Bind(wx.EVT_BUTTON, _on_error)
    btnwarn.Bind(wx.EVT_BUTTON, _on_warning)
    btnchoice.Bind(wx.EVT_BUTTON, _on_choice)

    frame.ShowModal()
    frame.Destroy()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.PySimpleApp()
    DemoBaseDialog(None)
    app.MainLoop()

# ---------------------------------------------------------------------------
