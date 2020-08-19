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
# File: sppaseditclient.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (develop@sppas.org)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import wx.media
import logging

from sppas.src.ui.wxgui.sp_icons import TIER_CHECK
from sppas.src.ui.wxgui.sp_icons import TIER_CHECK_DISABLED

from sppas.src.ui.wxgui.sp_icons import NAV_GO_START_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_GO_PREVIOUS_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_GO_NEXT_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_GO_END_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_FIT_SELECTION_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_PERIOD_ZOOM_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_PERIOD_ZOOM_IN_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_PERIOD_ZOOM_OUT_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_VIEW_ZOOM_IN_ICON
from sppas.src.ui.wxgui.sp_icons import NAV_VIEW_ZOOM_OUT_ICON

from sppas.src.ui.wxgui.structs.files import xFiles

from sppas.src.ui.wxgui.ui.CustomEvents import FileWanderEvent,spEVT_FILE_WANDER
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_SETTINGS
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_OBJECT_SELECTED

from sppas.src.ui.wxgui.ui.displayctrl import DisplayCtrl
from sppas.src.ui.wxgui.ui.trsctrl import TranscriptionCtrl
from sppas.src.ui.wxgui.ui.wavectrl import WaveCtrl

from sppas.src.ui.wxgui.dialogs.choosers import PeriodChooser
from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation

from sppas.src.ui.wxgui.panels.sndplayer import SndPlayer
from sppas.src.ui.wxgui.structs.theme import sppasTheme
from sppas.src.ui.wxgui.structs.prefs import Preferences

from sppas.src.ui.wxgui.cutils.ctrlutils import CreateButton
from sppas.src.ui.wxgui.cutils.imageutils import spBitmap

from .baseclient import BaseClient

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

ZOOM_IN_ID = wx.NewId()
ZOOM_OUT_ID = wx.NewId()

# ----------------------------------------------------------------------------
# Main class that manage the notebook
# ----------------------------------------------------------------------------


class SppasEditClient(BaseClient):
    """This class manages the pages of a notebook with all opened files.

    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL, v3

    Each page (except if empty...) contains an instance of a SppasEdit.

    """

    def __init__(self, parent, prefsIO):
        BaseClient.__init__(self, parent, prefsIO)
        self._update_members()

    # ------------------------------------------------------------------------

    def _update_members(self):
        """
        Update members.
        """
        self._multiplefiles = True
        # Quick and dirty solution to communicate with the file manager:
        self._prefsIO.SetValue('F_CCB_MULTIPLE', t='bool', v=True, text='')

    # ------------------------------------------------------------------------

    def CreateComponent(self, parent, prefsIO):
        return SppasEdit(parent, prefsIO)

# ----------------------------------------------------------------------------
# The Component is the content of one page of the notebook.
# ----------------------------------------------------------------------------


class SppasEdit(wx.Panel):
    """used to display all opened files.

    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL, v3

    """
    def __init__(self, parent, prefsIO):
        """
        Constructor.
        """
        wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # members
        self._prefsIO = self._check_prefs(prefsIO)
        self._xfiles = xFiles()

        # the display panel
        dp = self._set_display()
        # the navigation bar: a set of anz_panels: self._trans, self._media, self._navig
        sp = self._set_navigation()

        # put the anz_panels in a sizer
        sizer.Add(dp, 1, wx.TOP|wx.EXPAND, border=0)
        sizer.Add(sp, 0, wx.BOTTOM|wx.EXPAND, border=0)

        # events

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.GetTopLevelParent().Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

        self.Bind(spEVT_FILE_WANDER, self.OnFileWander)
        self.Bind(spEVT_SETTINGS, self.OnSettings)
        self.Bind(spEVT_OBJECT_SELECTED, self.OnObjectSelected)

        self.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    # ------------------------------------------------------------------------
    # GUI construction
    # ------------------------------------------------------------------------

    def _set_display(self):
        """Set the display panel."""

        self._displayctrl = DisplayCtrl(self, id=-1, pos=(10, 80), size=wx.Size(400, 160), prefsIO=self._prefsIO)
        return self._displayctrl


    def _set_navigation(self):
        """Set all anz_panels: transcription, media and navigate."""

        sp = wx.BoxSizer(wx.HORIZONTAL)

        self._trans = TrsPanel(self, self._prefsIO)
        self._media = MediaPanel(self, self._prefsIO)
        self._navig = NavigatePanel(self, self._prefsIO)

        sp.Add(self._trans, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, border=2)
        sp.AddStretchSpacer(1)

        sp.Add(self._media, 0, wx.EXPAND, border=2)
        sp.AddStretchSpacer(1)

        sp.Add(self._navig, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, border=2)

        self._trans.SetDisplay(self._displayctrl)
        self._media.SetDisplay(self._displayctrl)
        self._navig.SetDisplay(self._displayctrl)

        return sp

    # ------------------------------------------------------------------------

    def _check_prefs(self, prefs):
        """
        Check if preferences are set properly. Set new ones if required.
        Return the new version.
        """
        if prefs is None:
            prefs = Preferences(sppasTheme())
        else:
            try:
                prefs.GetValue('M_BG_COLOUR')
                prefs.GetValue('M_FG_COLOUR')
                prefs.GetValue('M_FONT')
                prefs.GetValue('M_ICON_THEME')
            except Exception:
                self._prefsIO.SetTheme(sppasTheme())
                prefs = self._prefsIO

        prefs.SetValue('SND_INFO',       'bool', True)
        prefs.SetValue('SND_PLAY',       'bool', True)
        prefs.SetValue('SND_AUTOREPLAY', 'bool', False)
        prefs.SetValue('SND_PAUSE',      'bool', True)
        prefs.SetValue('SND_STOP',       'bool', False)
        prefs.SetValue('SND_NEXT',       'bool', False)
        prefs.SetValue('SND_REWIND',     'bool', False)
        prefs.SetValue('SND_EJECT',      'bool', False)

        return prefs

    # ------------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------------

    def OnSettings(self, event):
        """
        Set new preferences, then apply them.
        """

        self._prefsIO = event.prefsIO

        # Apply the changes on self
        wx.Window.SetBackgroundColour(self, self._prefsIO.GetValue('M_BG_COLOUR'))
        wx.Window.SetForegroundColour(self, self._prefsIO.GetValue('M_FG_COLOUR'))
        wx.Window.SetFont(self, self._prefsIO.GetValue('M_FONT'))

        # Apply on anz_panels of self
        self._trans.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        self._media.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        self._navig.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))

        self._displayctrl.SetPreferences(self._prefsIO)

    # ------------------------------------------------------------------------
    # Callbacks to keyboard events
    # ------------------------------------------------------------------------

    def OnKeyPress(self, event):
        """
        Respond to a keypress event.
        """
        keycode = event.GetKeyCode()
        logging.debug('SppasEdit-Client panel. Key code = %d'%keycode)

        # Zoom In: Ctrl+I
        # Zoom Out: Ctrl+O
        if keycode == ord('I') and event.ControlDown():
            self._navig.onViewZoomIn(event)
        elif keycode == ord('O') and event.ControlDown():
            self._navig.onViewZoomOut(event)

        # OTHER keys require that an object is selected: media or transcription

        selected = self._displayctrl.GetSelectedObject()
        if selected is None:
            event.Skip()
            return

        # Transcription
        # CTRL+F -> Search
        # if keycode == ord('F') and event.ControlDown():
        #     self._trans.onSearch(event)
        # elif keycode == ord('G') and event.ControlDown():
        #     self._trans.onSearch(event)

        # Media player
        # TAB -> PLay
        # Shift+TAB -> Forward
        # Ctrl+TAB -> Rewind
        # F1 -> Pause
        # ESC -> Stop
        elif keycode == wx.WXK_TAB and event.ShiftDown():
            self._media.onNext(event)
        elif keycode == wx.WXK_TAB and event.ControlDown():
            self._media.onRewind(event)
        elif keycode == wx.WXK_TAB:
            self._media.onPlay(event)
        elif keycode == wx.WXK_F1:
            self._media.onPause(event)
        elif keycode == wx.WXK_ESCAPE:
            self._media.onStop(event)

        event.Skip()

    # ------------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------------

    def OnFileWander(self, event):
        """
        Add/Remove data.
        """
        f = event.filename
        s = event.status

        if s is True:
            try:
                self._displayctrl.SetData(event.filename)
            except Exception as e:
                #import traceback
                #print(traceback.format_exc())
                logging.info(' ** WARNING **: Got exception %s '%(str(e)))
                pass
        else:
            self._displayctrl.UnsetData(f)
            self._media.SetMedia()   # if the file was a sound...
            self._trans.SetTrs()     # if the file was a trs...
            self.Refresh()
            evt = FileWanderEvent(filename=f, status=False)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent().GetParent().GetParent(), evt)

    # ------------------------------------------------------------------------

    def OnObjectSelected(self, event):
        """
        Update anz_panels when the selected object has changed.
        """
        selobj = event.object
        fname  = event.string

        # anz_panels that must be adapted (Set or Unset).
        # (they will get the object with their own displayctrl access)
        self._media.SetMedia()
        self._trans.SetTrs()

    # ------------------------------------------------------------------------

    def OnSize(self, event):
        """
        Called by the parent when the frame is resized
        and lays out the client window.
        """

        self.Layout()
        self.Refresh()

    # ------------------------------------------------------------------------

    def GetNavigPanel(self):
        return self._navig

    def GetTransPanel(self):
        return self._trans

    def GetMediaPanel(self):
        return self._media

# ----------------------------------------------------------------------------


class NavigatePanel(wx.Panel):
    """It is used to change the displayed time period.

    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL

    """
    def __init__(self, parent, prefsIO):
        """Constructor."""

        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        gbs = wx.GridBagSizer(hgap=5, vgap=5)

        # members
        self._prefsIO = prefsIO
        self._buttons = {}
        self._display = None
        self._scrollcoef = 75.0 # Time scroll (percentage)
        self._zoomcoef   = 50.0 # Time zoom (percentage)

        # create the buttons
        theme = self._prefsIO.GetValue('M_ICON_THEME')
        bgcolour = self._prefsIO.GetValue('M_BG_COLOUR')
        tbsize = self._prefsIO.GetValue('M_TOOLBAR_ICONSIZE')
        self._buttons['gostart'] = CreateButton(self, spBitmap(NAV_GO_START_ICON, tbsize, theme),    self.onGoStart, gbs, colour=bgcolour)
        self._buttons['goback']  = CreateButton(self, spBitmap(NAV_GO_PREVIOUS_ICON, tbsize, theme), self.onGoBack,  gbs, colour=bgcolour)
        self._buttons['gonext']  = CreateButton(self, spBitmap(NAV_GO_NEXT_ICON, tbsize, theme),     self.onGoNext,  gbs, colour=bgcolour)
        self._buttons['goend']   = CreateButton(self, spBitmap(NAV_GO_END_ICON, tbsize, theme),      self.onGoEnd,   gbs, colour=bgcolour)
        self._buttons['fitsel']  = CreateButton(self, spBitmap(NAV_FIT_SELECTION_ICON, tbsize, theme), self.onFitSelection, gbs, colour=bgcolour)

        self._buttons['hzoom']    = CreateButton(self, spBitmap(NAV_PERIOD_ZOOM_ICON, tbsize, theme),    self.onPeriodZoom, gbs, colour=bgcolour)
        self._buttons['hzoomin']  = CreateButton(self, spBitmap(NAV_PERIOD_ZOOM_IN_ICON, tbsize, theme), self.onPeriodZoomIn, gbs, colour=bgcolour)
        self._buttons['hzoomout'] = CreateButton(self, spBitmap(NAV_PERIOD_ZOOM_OUT_ICON, tbsize, theme),self.onPeriodZoomOut,gbs, colour=bgcolour)
        self._buttons['vzoomin']  = CreateButton(self, spBitmap(NAV_VIEW_ZOOM_IN_ICON, tbsize, theme),   self.onViewZoomIn,   gbs, colour=bgcolour)
        self._buttons['vzoomout'] = CreateButton(self, spBitmap(NAV_VIEW_ZOOM_OUT_ICON, tbsize, theme),  self.onViewZoomOut,  gbs, colour=bgcolour)

        # button placement in the sizer
        gbs.Add(self._buttons['gostart'],(0,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)
        gbs.Add(self._buttons['goback'], (0,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)
        gbs.Add(self._buttons['gonext'], (0,2), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)
        gbs.Add(self._buttons['goend'],  (0,3), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)
        gbs.Add(self._buttons['fitsel'], (0,4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)

        gbs.Add(self._buttons['hzoom'],   (0,5), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)
        gbs.Add(self._buttons['hzoomin'], (0,6), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)
        gbs.Add(self._buttons['hzoomout'],(0,7), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)

        gbs.Add(self._buttons['vzoomin'], (0,8), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)
        gbs.Add(self._buttons['vzoomout'],(0,9), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=1)

        self.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))

        self.SetSizer(gbs)
        self.SetAutoLayout(True)
        self.Layout()

    # ------------------------------------------------------------------------
    # Callbacks for Scrolling...
    # ------------------------------------------------------------------------

    def onGoStart(self, event):
        """
        Go at the beginning (change time period).
        """
        self.SetNewPeriod(1.0, "start")

    # ------------------------------------------------------------------------

    def onGoBack(self, event):
        """
        Go backward (change time period).
        """
        self.SetNewPeriod(1.0 - self._scrollcoef/100.0, "scroll")

    # ------------------------------------------------------------------------

    def onGoNext(self, event):
        """
        Go forward (change time period).
        """
        self.SetNewPeriod(1.0 + self._scrollcoef/100.0, "scroll")

    # ------------------------------------------------------------------------

    def onGoEnd(self, event):
        """
        Go at the end of the drawing (change time period).
        """
        self.SetNewPeriod(1.0, "end")

    # ------------------------------------------------------------------------
    # Callbacks for Zooming...
    # ------------------------------------------------------------------------

    def onPeriodZoom(self, event):
        """
        Open a display dialog to get zoom values.
        """
        if self._display is None: return

        dlg = PeriodChooser(self, self._prefsIO, self._display.GetPeriod().GetStart(), self._display.GetPeriod().GetEnd())
        if dlg.ShowModal() == wx.ID_OK:
            (s, e) = dlg.GetValues()
            try:
                s = float(s)
                e = float(e)
            except Exception:
                logging.info('Zoom cancelled (can not be applied: from %f to %f).'%(s,e))
                return
            (s,e) = self._display.GetPeriod().Check(float(s), float(e))
            self._changedrawingperiod(s,e)

        dlg.Destroy()

    # ------------------------------------------------------------------------

    def onPeriodZoomIn(self, event):
        """
        Reduce the displayed time period of the drawing.
        """
        self.SetNewPeriod(1.0 - self._zoomcoef/100.0, "zoom")

    # ------------------------------------------------------------------------

    def onPeriodZoomOut(self, event):
        """
        Enlarge the displayed time period of the drawing.
        """
        self.SetNewPeriod(1.0 + self._zoomcoef/100.0, "zoom")

    # ------------------------------------------------------------------------

    def onViewZoomIn(self, event):
        """
        Reduce the height of the drawing.
        """
        if self._display is None: return
        self._display.ZoomUp()

    # ------------------------------------------------------------------------

    def onViewZoomOut(self, event):
        """
        Enlarge the height of the drawing.
        """
        if self._display is None: return
        self._display.ZoomDown()

    # ------------------------------------------------------------------------

    def onFitSelection(self, event):
        """
        Fit the period on the selection (selection is indicated by the ruler).
        """
        if self._display is None: return

        ruler = self._display.GetRuler()
        start,end = ruler.GetSelectionIndicatorValues()

        # don't do anything if the period did not changed!
        period = self._display.GetPeriod()
        if start == period.GetStart() and end == period.GetEnd():
            return

        # Check period before changing, then change!
        checkstart,checkend = period.Check(start,end)

        self._changedrawingperiod(checkstart, checkend)
        ruler.SetSelectionIndicatorValues(start, end)

        self._display.Refresh()

    # ------------------------------------------------------------------------

    def OnCenterSelection(self, event):
        """
        Fit the period to place the selection at the middle of the screen
        (selection is indicated by the ruler).
        The delta value of the period is not changed.
        """
        if self._display is None:
            return

        ruler = self._display.GetRuler()
        period = self._display.GetPeriod()

        selstart, selend = ruler.GetSelectionIndicatorValues()
        start, end = period.GetStart(), period.GetEnd()
        delta = period.Delta()

        middle = round(start + (end-start)/2.,           2)
        selmiddle = round(selstart + (selend-selstart)/2.,  2)
        if middle != selmiddle:
            start = selmiddle - delta/2.
            end = selmiddle + delta/2.
            start, end = period.Check(start, end)
            self._changedrawingperiod(start, end)
            self._display.Refresh()

    # ------------------------------------------------------------------------
    # GUI...
    # ------------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """
        Set the background color of this panel.
        """

        wx.Window.SetBackgroundColour(self, colour)
        for b in self._buttons:
            self._buttons[b].SetBackgroundColour(colour)
        self.Refresh()

    # ------------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------------

    def SetNewPeriod(self, coeff, mode):
        """Update the drawing period."""

        if self._display is None: return

        period = self._display.GetPeriod()
        if mode == "zoom":
            start, end = period.Zoom(coeff)
        elif mode == "scroll":
            start, end = period.Scroll(coeff)
        elif mode == "start":
            start, end = period.ScrollToStart()
        elif mode == "end":
            start, end = period.ScrollToEnd()

        self._changedrawingperiod(start, end)

    # ------------------------------------------------------------------------

    def SetDisplay(self, drawing):
        """
        Set a new drawing.
        """
        self._display = drawing

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _changedrawingperiod(self, start, end):
        period = self._display.GetPeriod()
        if start != period.GetStart() or end != period.GetEnd():
            period.Update(start, end)
            self._display.SetPeriod(period)

# ----------------------------------------------------------------------------


class TrsPanel(wx.Panel):
    """This panel is used to manage transcription files.

    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL, v3

    """
    def __init__(self, parent, prefsIO):
        """Create a new instance."""

        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # members
        self._prefsIO = prefsIO
        self._display = None
        self._trsctrl = None
        self._buttons = {}

        # create the buttons bar
        theme = self._prefsIO.GetValue('M_ICON_THEME')
        bgcolour = self._prefsIO.GetValue('M_BG_COLOUR')
        tbsize = self._prefsIO.GetValue('M_TOOLBAR_ICONSIZE')
        self._buttons['tiercheck'] = CreateButton(self, spBitmap(TIER_CHECK_DISABLED, tbsize, theme),
                                                  self.onTierCheck,sizer, colour=bgcolour)

        # sizer
        sizer.Add(self._buttons['tiercheck'], 1, flag=wx.ALL, border=2)

        self.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------

    def onTierCheck(self, event):
        """Fix the list of tiers to Show/Hide."""

        if self._trsctrl is None: return

        # Get the list of tiers' names
        lst = self._trsctrl.GetTierNames()
        if len(lst) == 0: return # hum... just to be sure

        dlg = wx.MultiChoiceDialog(self,
                                   "Check the tiers to show:",
                                   "Tiers to show/hide", lst)
        dlg.SetSelections(self._trsctrl.GetTierIdxChecked())

        if dlg.ShowModal() == wx.ID_OK:
            # get the list of tiers' names that are checked
            selections = dlg.GetSelections()
            checked = [lst[x] for x in selections]

            if len(checked) == 0:
                ShowInformation(self, self._prefsIO, "At least one tier must be checked!", wx.ICON_INFORMATION)
            else:
                # send the list to the trsctrl instance, then redraw
                self._trsctrl.SetTierChecked(checked)

        dlg.Destroy()

    # ------------------------------------------------------------------------
    # Functions...
    # ------------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Change the background of the panel."""

        wx.Window.SetBackgroundColour(self, colour)
        for b in self._buttons:
            self._buttons[b].SetBackgroundColour(colour)
        self.Refresh()

    # ------------------------------------------------------------------------
    # Data management
    # ------------------------------------------------------------------------

    def SetDisplay(self, drawing):
        """
        Set a new displayctrl, then a new trsctrl (if any).
        """

        self._display = drawing
        if self._display is None:
            self.ActivateButtons(False)
            self.EnableButtons(True)
            self._trsctrl = None
        else:
            self.SetTrs()

    # ------------------------------------------------------------------------

    def SetTrs(self):
        """Set a new transcription."""

        self._trsctrl = None
        if self._display is None: return

        self.ActivateButtons(False)
        dcobj = self._display.GetSelectedObject()
        if dcobj is None:
            return
        if not isinstance(dcobj, TranscriptionCtrl):
            return

        self._trsctrl = dcobj
        self.ActivateButtons(True)
        self.Refresh()

    # ------------------------------------------------------------------------

    def UnsetData(self):
        """Unset the current drawing."""

        if self._display is None:
            return

        self._display = None
        self._trsctrl = None

        self.ActivateButtons(False)
        self.EnableButtons(True)

        for k in self._buttons:
            self._buttons[k].Enable(False)

        self.Refresh()

    # ------------------------------------------------------------------------
    # Private...
    # ------------------------------------------------------------------------

    def ActivateButtons(self, value=True):
        self.EnableButtons(False)
        if value is True:
            self._buttons['tiercheck'].SetBitmapLabel(spBitmap(TIER_CHECK))
        else:
            self._buttons['tiercheck'].SetBitmapLabel(spBitmap(TIER_CHECK_DISABLED))

    # ------------------------------------------------------------------------

    def EnableButtons(self, value=True):
        for b in self._buttons:
            self._buttons[b].Enable(not value)

# ----------------------------------------------------------------------------


class MediaPanel(SndPlayer):
    """Display an audio player panel, used to play media files (wave only).

    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL, v3

    """
    def __init__(self, parent, prefsIO):
        """Creates a new MediaPanel instance.

        @param prefsIO (PreferencesIO) Fix preferences for colors, fonts, etc.

        """
        SndPlayer.__init__(self, parent, orient=wx.HORIZONTAL, refreshtimer=10, prefsIO=prefsIO)
        self.ActivateButtons(False)

        # members
        self._display = None
        self.SetBackgroundColour(prefsIO.GetValue('M_BG_COLOUR'))

    # ------------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------------

    def onNext(self, event):
        """Go forward in the music."""

        SndPlayer.onNext(self,event)
        self.UpdateRuler()

    # ------------------------------------------------------------------------

    def onRewind(self, event):
        """Go backward in the music."""

        SndPlayer.onRewind(self,event)
        self.UpdateRuler()

    # ------------------------------------------------------------------------

    def onPause(self, event):
        """Pauses the music."""

        SndPlayer.onPause(self,event)
        self.UpdateRuler()

    # ------------------------------------------------------------------------

    def onPlay(self, event):
        """Fix the period to play then Plays the music."""

        if self._mediaplayer is None and self._display is None:
            return
        if self._mediaplayer is None and self._display is not None:
            self.SetMedia()  # now, a selection?
        if self._dcobj != self._display.GetSelectedObject():
            self.SetMedia()  # selection has changed since last play...

        # The period on screen
        start,end = self._display.GetPeriodValues()
        self.SetOffsetPeriod(int(start*1000.), int(end*1000.))

        # Use the indicator as a slider, then get the value to seek
        v = self._display.GetRuler().GetPlayerIndicatorValue()
        if v is not None:
            offset = int(v*1000.0)
            # is required in some wx versions (bug)
            if offset == 0:
                offset = 1
        else:
            offset = int(start*1000.)
        if offset == -1:
            offset = int(start*1000.)

        self._mediaplayer.Seek(offset, mode=wx.FromStart)
        SndPlayer.onPlay(self, event)

    # ------------------------------------------------------------------------

    def onStop(self, event):
        """Stops the music and resets the play button."""

        if self._mediaplayer is None:
            return

        self._offsets = (0, 0)
        if self._display is not None:
            self._offsets = self._display.GetPeriodValues()

        SndPlayer.onStop(self, event)
        self.UpdateRuler()

    # ------------------------------------------------------------------------

    def onTimer(self, event):
        """Keeps the player updated.

        OVERRIDE because we dont stop at the end of the displayed period fixed
        by self._offsets: instead we update the period and continue to play.

        """
        if self._mediaplayer is None:
            return

        # Get current position
        offset = self._mediaplayer.Tell()
        # Allowed position
        try:
            (s, e) = self._display.GetPeriodValues()
        except Exception:  # PyDeadObjectError (on WindowsInstaller only)
            self._timer.Stop()
            return
        try:
            # Quick and dirty:
            delta = (e-s)*100
            maxoffset = int(e*1000)
            if offset >= (maxoffset - delta) and self._mediaplayer.GetState() != wx.media.MEDIASTATE_STOPPED:
                m = (e-s)/2
                self._display.SetPeriodValues(s+m, e+m)
        except Exception:
            self.onStop(event)

        # Maximum media offset
        if self._mediaplayer.GetState() == wx.media.MEDIASTATE_PLAYING and offset == 0:
            self.onStop(event)

        if self._mediaplayer.GetState() != wx.media.MEDIASTATE_STOPPED:
            self.UpdateRuler()

    # ------------------------------------------------------------------------

    def UpdateRuler(self):
        offset = self._mediaplayer.Tell()
        if self._display:
            self._display.GetRuler().SetPlayerIndicatorValue(float(offset)/1000.0)
            self._display.GetRuler().Refresh()

    # ------------------------------------------------------------------------
    # Data management
    # ------------------------------------------------------------------------

    def SetDisplay(self, d):

        self._display = d
        if self._display is None:
            self.ActivateButtons(False)
            self.EnableButtons(True)
            self._mediaplayer = None
        else:
            self.SetMedia()

    # ------------------------------------------------------------------------

    def SetMedia(self):
        """Set a new mediaplayer."""

        self.onStop(None)
        self._mediaplayer = None
        if self._display is None:
            return

        self._dcobj = self._display.GetSelectedObject()

        if self._dcobj is None:
            self.FileDeSelected()

        if not isinstance(self._dcobj, WaveCtrl):
            self.FileDeSelected()
            return

        filename = self._display.GetSelectionFilename()
        SndPlayer.FileSelected(self, filename)

        self.Refresh()

    # ------------------------------------------------------------------------

    def FileDeSelected(self):
        """Unset the current mediaplayer."""

        if self._display is None: return
        #self._display = None
        SndPlayer.FileDeSelected(self)
