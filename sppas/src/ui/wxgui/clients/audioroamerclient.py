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
# File: audioroamerclient.py
# ----------------------------------------------------------------------------

import datetime
import codecs
import wx
import wx.lib.scrolledpanel as scrolled

from sppas.src.config import sg

from sppas.src.ui.wxgui.ui.CustomEvents import NotebookClosePageEvent
from sppas.src.ui.wxgui.ui.CustomEvents import FileWanderEvent, spEVT_FILE_WANDER
from sppas.src.ui.wxgui.ui.CustomEvents import spEVT_SETTINGS

from sppas.src.ui.wxgui.panels.sndplayer import SndPlayer
from sppas.src.ui.wxgui.panels.audioinfo import AudioInfo
from sppas.src.ui.wxgui.structs.prefs import Preferences
from sppas.src.ui.wxgui.structs.theme import sppasTheme

from sppas.src.ui.wxgui.cutils.imageutils import spBitmap
from sppas.src.ui.wxgui.cutils.ctrlutils import CreateGenButton
from sppas.src.ui.wxgui.cutils.textutils import TextAsNumericValidator

from sppas.src.ui.wxgui.sp_icons import AUDIOROAMER_APP_ICON
from sppas.src.ui.wxgui.sp_icons import SAVE_FILE
from sppas.src.ui.wxgui.sp_icons import SAVE_AS_FILE

from sppas.src.ui.wxgui.sp_consts import INFO_COLOUR
from sppas.src.ui.wxgui.sp_consts import MIN_PANEL_W
from sppas.src.ui.wxgui.sp_consts import MIN_PANEL_H

from sppas.src.ui.wxgui.dialogs.filedialogs import SaveAsAudioFile, SaveAsAnyFile
from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation, ShowYesNoQuestion
from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog
from sppas.src.ui.wxgui.dialogs.choosers import PeriodChooser

import sppas.src.audiodata.aio
from sppas.src.audiodata.channelsilence import sppasChannelSilence
from sppas.src.audiodata.channelformatter import sppasChannelFormatter
from sppas.src.audiodata.audioframes import sppasAudioFrames
from sppas.src.audiodata.audio import sppasAudioPCM
from sppas.src.audiodata.audioconvert import sppasAudioConverter

from .baseclient import BaseClient

# ----------------------------------------------------------------------------

ID_DIALOG_AUDIOROAMER  = wx.NewId()

# ----------------------------------------------------------------------------


class AudioRoamerClient(BaseClient):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Manage the opened files in a notebook.

    This class manages the pages of a notebook with all opened files.
    Each page (except if empty...) contains an instance of a SndRoamer.

    """
    def __init__(self, parent, prefsIO):
        BaseClient.__init__(self, parent, prefsIO)

    def CreateComponent(self, parent, prefsIO):
        return SndRoamer(parent, prefsIO)

# ----------------------------------------------------------------------------

class SndRoamer(scrolled.ScrolledPanel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Manage audio files.

    Panel to manage audio files:
        - show information,
        - manage the content of the audio,
        - play.

    """
    def __init__(self, parent, prefsIO):
        """
        SndRoamer Component ScrolledPanel.

        """
        scrolled.ScrolledPanel.__init__(self, parent, -1)

        # members
        self._prefsIO  = self._check_prefs(prefsIO)
        self._filename = None

        # GUI
        sizer = self._create_content()

        # Bind events
        self.Bind(spEVT_FILE_WANDER, self.OnFileWander)
        self.Bind(spEVT_SETTINGS,    self.OnSettings)
        self.GetTopLevelParent().Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

        self.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
        self.SetupScrolling()

    # ----------------------------------------------------------------------

    def _create_content(self):
        """
        GUI design.

        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        # create the panels
        self._propertyPanel = AudioInfo(self, self._prefsIO)
        self._managerPanel  = AudioRoamer(self, self._prefsIO)
        self._playerPanel   = SndPlayer(self, prefsIO=self._prefsIO)

        sizer.Add(self._managerPanel,  proportion=0, flag=wx.CENTRE|wx.ALL, border=2)
        sizer.Add(self._propertyPanel, proportion=0, flag=wx.LEFT|wx.EXPAND|wx.ALL, border=2)
        sizer.Add(self._playerPanel,   proportion=1, flag=wx.CENTRE|wx.ALL, border=2)
        return sizer

    # ----------------------------------------------------------------------

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

        prefs.SetValue('SND_INFO',       'bool', False)
        prefs.SetValue('SND_PLAY',       'bool', True)
        prefs.SetValue('SND_AUTOREPLAY', 'bool', False)
        prefs.SetValue('SND_PAUSE',      'bool', True)
        prefs.SetValue('SND_STOP',       'bool', True)
        prefs.SetValue('SND_NEXT',       'bool', True)
        prefs.SetValue('SND_REWIND',     'bool', True)
        prefs.SetValue('SND_EJECT',      'bool', False) # CRASH. MUST CORRECT THE BUG.

        return prefs

    # ----------------------------------------------------------------------
    # GUI
    # ----------------------------------------------------------------------

    def OnSettings(self, event):
        """
        Set new preferences, then apply them.

        """
        self._prefsIO = self._check_prefs(event.prefsIO)

        # Apply the changes on self
        self.SetBackgroundColour(self._prefsIO.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(self._prefsIO.GetValue('M_FG_COLOUR'))
        self.SetFont(self._prefsIO.GetValue('M_FONT'))

        self._managerPanel.SetPreferences(self._prefsIO)

        self.Layout()
        self.Refresh()

    # ----------------------------------------------------------------------

    def SetFont(self, font):
        """
        Change font of all wx texts.

        """
        wx.Window.SetFont(self, font)
        self._propertyPanel.SetFont(font)
        self._playerPanel.SetFont(font)

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """
        Change background of all texts.

        """
        wx.Window.SetBackgroundColour(self, color)
        self._propertyPanel.SetBackgroundColour(color)
        self._playerPanel.SetBackgroundColour(color)

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """
        Change foreground of all texts.

        """
        wx.Window.SetForegroundColour(self, color)
        self._propertyPanel.SetForegroundColour(color)
        self._playerPanel.SetForegroundColour(color)

    # ----------------------------------------------------------------------
    # Callbacks
    # ----------------------------------------------------------------------

    def OnFileWander(self, event):
        """
        A file was checked/unchecked/ejected somewhere else.

        """
        o = event.GetEventObject()
        if o == self._playerPanel:
            evt = NotebookClosePageEvent()
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent().GetParent().GetParent(),evt)
            self._propertyPanel.FileDeSelected()
            return

        f = event.filename
        s = event.status

        if s is True:
            self._propertyPanel.FileSelected(f)
            self._playerPanel.FileSelected(f)
            self._managerPanel.FileSelected(f)
            self._filename = f
        else:
            self._propertyPanel.FileDeSelected()
            self._playerPanel.FileDeSelected()
            self._managerPanel.FileDeSelected(f)
            evt = FileWanderEvent(filename=self._filename, status=False)
            evt.SetEventObject(self)
            wx.PostEvent(self.GetParent().GetParent().GetParent(), evt)
            self._filename = None

    # ----------------------------------------------------------------------

    def OnKeyPress(self, event):
        """
        Respond to a keypress event.
        """
        keycode = event.GetKeyCode()

        # Media player
        #     TAB -> PLay
        #     F6 -> Rewind
        #     F7 -> Pause/Play
        #     F8 -> Next
        #     F12 -> Eject
        #     ESC -> Stop
        if keycode == wx.WXK_TAB:
            self._playerPanel.onPlay(event)

        elif keycode == wx.WXK_F6:
            self._playerPanel.onRewind(event)

        elif keycode == wx.WXK_F7:
            self._playerPanel.onPause(event)

        elif keycode == wx.WXK_F8:
            self._playerPanel.onNext(event)

        elif keycode == wx.WXK_F12:
            self._playerPanel.onEject(event)

        elif keycode == wx.WXK_ESCAPE:
            self._playerPanel.onStop(event)

        else:
            event.Skip()

# ----------------------------------------------------------------------------


class AudioRoamer(wx.Panel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Propose to manage the content of an audio file.

    """
    def __init__(self, parent, preferences):
        """Create a new AudioRoamer instance.

        :param parent (wxWindow)
        :param preferences (Preferences)

        """
        wx.Panel.__init__(self, parent)
        self._prefs = preferences
        self._filename = None

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        FONT = self._prefs.GetValue('M_FONT')
        bmproamer = spBitmap(AUDIOROAMER_APP_ICON, theme=self._prefs.GetValue('M_ICON_THEME'))
        self.roamerButton = CreateGenButton(self, ID_DIALOG_AUDIOROAMER,
                                            bmproamer,
                                            text=" Want more? ",
                                            tooltip="More information, manage channels, framerate, etc.",
                                            colour=wx.Colour(220, 120, 180),
                                            font=FONT)
        self.Bind(wx.EVT_BUTTON, self.OnAudioRoamer, self.roamerButton, ID_DIALOG_AUDIOROAMER)

        sizer.Add(self.roamerButton)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    def FileSelected(self, filename):
        self._filename = filename
        self.roamerButton.Enable(True)

    def FileDeSelected(self, filename):
        self._filename = None
        self.roamerButton.Enable(False)

    def OnAudioRoamer(self, event):
        if self._filename is not None:
            ShowAudioRoamerDialog(self, self._prefs, self._filename)

    def SetPreferences(self, prefs):
        self._prefs = prefs

# ----------------------------------------------------------------------------


class AudioRoamerDialog(spBaseDialog):
    """
    @author:  Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL
    @summary: Frame allowing to show details of a tier.

    """
    def __init__(self, parent, preferences, filename):
        """
        Constructor.

        @param parent is a wx.Window or wx.Frame or wx.Dialog
        @param preferences (Preferences or Preferences_IO)
        @param filename

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - AudioRoamer")
        wx.GetApp().SetAppName("audio")
        self._filename = filename

        titlebox   = self.CreateTitle(AUDIOROAMER_APP_ICON,"Audio Data Manager")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents(titlebox,
                               contentbox,
                               buttonbox)

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_close = self.CreateCloseButton()

        btn_save_channel  = self.CreateButton(SAVE_FILE, "Save as...", "Save the channel in an audio file.", btnid=wx.ID_SAVE)
        btn_save_channel.Bind(wx.EVT_BUTTON, self._on_save_channel)

        btn_save_fragment = self.CreateButton(SAVE_FILE, "Save a portion as...", "Save a portion of this channel in an audio file.", btnid=wx.ID_SAVE)
        btn_save_fragment.Bind(wx.EVT_BUTTON, self._on_save_fragment)

        btn_save_info = self.CreateButton(SAVE_AS_FILE, "Save info as...", "Save the displayed information in a text file.", btnid=wx.ID_SAVE)
        btn_save_info.Bind(wx.EVT_BUTTON, self._on_save_info)

        return self.CreateButtonBox([btn_save_channel,btn_save_fragment,btn_save_info],[btn_close])

    def _create_content(self):
        audio = sppas.src.audiodata.aio.open(self._filename)
        nchannels = audio.get_nchannels()
        audio.extract_channels()
        audio.close()

        self.notebook = wx.Notebook(self)
        self.pages = []
        for i in range(nchannels):
            page = AudioRoamerPanel(self.notebook, self.preferences, audio.get_channel(i))
            # add the pages to the notebook with the label to show on the tab
            self.notebook.AddPage(page, "Channel %d"%i)

        self.ShowPage(0)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_notebook_page_changed)
        return self.notebook

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _on_notebook_page_changed(self, event):
        oldselection = event.GetOldSelection()
        newselection = event.GetSelection()
        if oldselection != newselection:
            self.ShowPage(newselection)

    def _on_save_channel(self, event):
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.SaveChannel(self._filename, period=False)

    def _on_save_fragment(self, event):
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.SaveChannel(self._filename, period=True)

    def _on_save_info(self, event):
        page = self.notebook.GetPage(self.notebook.GetSelection())
        page.SaveInfos(self._filename)

    # ------------------------------------------------------------------------

    def ShowPage(self, idx):
        page = self.notebook.GetPage(idx)
        page.ShowInfo()


# ----------------------------------------------------------------------------
# The panel that is really doing the job is here:
# ---------------------------------------------------------------------------

class AudioRoamerPanel(wx.Panel):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Display info about a channel. Allows to save.

    This panel display all information about a channel:
      - amplitudes: nb of frames, min/max values, zero crossing,
      - clipping rates
      - volumes: min/max/mean
      - silence/speech automatic segmentation.

    Methods allow to save:
      - the channel or a fragment of the channel, in an audio file;
      - the information in a text file.

    """
    FRAMERATES = ["16000", "32000", "48000"]
    SAMPWIDTH  = ["8", "16", "32"]
    INFO_LABELS = {"framerate": ("  Frame rate (Hz): ", FRAMERATES[0]),
                   "sampwidth": ("  Samp. width (bits): ", SAMPWIDTH[0]),
                   "mul":      ("  Multiply values by: ", "1.0"),
                   "bias":     ("  Add bias value: ", "0"),
                   "offset":   ("  Remove offset value: ", False),
                   "nframes":  ("  Number of frames: ", " ... "),
                   "minmax":   ("  Min/Max values: ", " ... "),
                   "cross":    ("  Zero crossings: ", " ... "),
                   "volmin":   ("  Volume min: ", " ... "),
                   "volmax":   ("  Volume max: ", " ... "),
                   "volavg":   ("  Volume mean: ", " ... "),
                   "volsil":   ("  Threshold volume: ", " ... "),
                   "nbipus":   ("  Number of IPUs: ", " ... "),
                   "duripus":  ("  Nb frames of IPUs: ", " ... ")
                   }

    def __init__(self, parent, preferences, channel):
        """Create a new AudioRoamerPanel instance.

        :param parent: (wxWindow)
        :param preferences: (structs.Preferences)
        :param channel: (audiodata.Channel)

        """
        wx.Panel.__init__(self, parent)
        self._channel  = channel  # Channel
        self._filename = None     # Fixed when "Save as" is clicked
        self._cv = None           # sppasChannelSilence, fixed by ShowInfos
        self._tracks = None       # the IPUs we found automatically
        self._ca = None           # sppasAudioFrames with only this channel, fixed by ShowInfos
        self._wxobj = {}          # Dict of wx objects
        self._prefs = None

        sizer = self._create_content()

        self.MODIFIABLES = {}
        for key in ["framerate","sampwidth","mul","bias","offset"]:
            self.MODIFIABLES[key] = AudioRoamerPanel.INFO_LABELS[key][1]

        self.SetPreferences(preferences)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetMinSize((MIN_PANEL_W,MIN_PANEL_H))
        self.Layout()

    # -----------------------------------------------------------------------
    # Private methods to show information about the channel into the GUI.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main sizer, add content then return it."""

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        info = self._create_content_infos()
        clip = self._create_content_clipping()
        ipus = self._create_content_ipus()

        sizer.AddSpacer(5)
        sizer.Add(info, 1, wx.EXPAND, 0)
        sizer.AddSpacer(10)
        sizer.Add(clip, 0, wx.ALL, 0)
        sizer.AddSpacer(10)
        sizer.Add(ipus, 1, wx.EXPAND, 0)
        sizer.AddSpacer(5)

        return sizer

    # -----------------------------------------------------------------------

    def _create_content_infos(self):
        """GUI design for amplitude and volume information."""

        gbs = wx.GridBagSizer(10, 2)

        static_tx = wx.StaticText(self, -1, "Amplitude values: ")
        gbs.Add(static_tx, (0, 0), (1, 2), flag=wx.LEFT, border=2)
        self._wxobj["titleamplitude"] = (static_tx, None)

        self.__add_info(self, gbs, "nframes", 1)
        self.__add_info(self, gbs, "minmax",  2)
        self.__add_info(self, gbs, "cross",   3)

        static_tx = wx.StaticText(self, -1, "")
        gbs.Add(static_tx, (4, 0), (1, 2), flag=wx.LEFT, border=2)

        cfm = wx.ComboBox(self, -1, choices=AudioRoamerPanel.FRAMERATES, style=wx.CB_READONLY)
        cfm.SetMinSize((120,24))
        self.__add_modifiable(self, gbs, cfm, "framerate", 5)
        self.Bind(wx.EVT_COMBOBOX, self.OnModif, cfm)

        csp = wx.ComboBox(self, -1, choices=AudioRoamerPanel.SAMPWIDTH, style=wx.CB_READONLY)
        csp.SetMinSize((120,24))
        self.__add_modifiable(self, gbs, csp, "sampwidth", 6)
        self.Bind(wx.EVT_COMBOBOX, self.OnModif, csp)

        txm = wx.TextCtrl(self, -1, AudioRoamerPanel.INFO_LABELS["mul"][1], validator=TextAsNumericValidator())
        txm.SetInsertionPoint(0)
        self.__add_modifiable(self, gbs, txm, "mul", 7)
        self.Bind(wx.EVT_TEXT_ENTER , self.OnModif, txm)

        txb = wx.TextCtrl(self, -1, AudioRoamerPanel.INFO_LABELS["bias"][1], validator=TextAsNumericValidator())
        txb.SetInsertionPoint(0)
        self.__add_modifiable(self, gbs, txb, "bias", 8)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnModif, txb)

        cb = wx.CheckBox(self, -1, style=wx.NO_BORDER)
        cb.SetValue(AudioRoamerPanel.INFO_LABELS["offset"][1])
        self.__add_modifiable(self, gbs, cb, "offset", 9)
        self.Bind(wx.EVT_CHECKBOX, self.OnModif, cb)

        gbs.AddGrowableCol(1)

        border = wx.BoxSizer()
        border.Add(gbs, 1, wx.ALL | wx.EXPAND, 10)
        return border

    # -----------------------------------------------------------------------

    def _create_content_clipping(self):
        """GUI design for clipping information."""

        gbs = wx.GridBagSizer(11, 2)

        static_tx = wx.StaticText(self, -1, "Clipping rates:")
        gbs.Add(static_tx, (0, 0), (1, 2), flag=wx.LEFT, border=2)
        self._wxobj["titleclipping"] = (static_tx, None)

        for i in range(1,10):
            self.__add_clip(self, gbs, i)

        border = wx.BoxSizer()
        border.Add(gbs, 1, wx.ALL | wx.EXPAND, 10)
        return border

    # -----------------------------------------------------------------------

    def _create_content_ipus(self):
        """GUI design for information about an IPUs segmentation..."""

        gbs = wx.GridBagSizer(9, 2)

        static_tx = wx.StaticText(self, -1, "Root-mean square:")
        gbs.Add(static_tx, (0, 0), (1, 2), flag=wx.LEFT, border=2)
        self._wxobj["titlevolume"] = (static_tx, None)

        self.__add_info(self, gbs, "volmin", 1)
        self.__add_info(self, gbs, "volmax", 2)
        self.__add_info(self, gbs, "volavg", 3)

        static_tx = wx.StaticText(self, -1, "")
        gbs.Add(static_tx, (4, 0), (1, 2), flag=wx.LEFT, border=2)

        static_tx = wx.StaticText(self, -1, "Automatic detection of IPUs (by default):")
        gbs.Add(static_tx, (5, 0), (1, 2), flag=wx.LEFT, border=2)
        self._wxobj["titleipus"] = (static_tx, None)

        self.__add_info(self, gbs, "volsil",  6)
        self.__add_info(self, gbs, "nbipus",  7)
        self.__add_info(self, gbs, "duripus", 8)

        border = wx.BoxSizer()
        border.Add(gbs, 1, wx.ALL | wx.EXPAND, 10)
        return border

    # -----------------------------------------------------------------------
    # Callbacks to events
    # -----------------------------------------------------------------------

    def OnModif(self, evt):
        """Callback on a modifiable object: adapt foreground color.

        :param evt: (wx.event)

        """
        evtobj   = evt.GetEventObject()
        evtvalue = evtobj.GetValue()
        for key, defaultvalue in self.MODIFIABLES.items():
            (tx,obj) = self._wxobj[key]
            if evtobj == obj:
                if evtvalue == defaultvalue:
                    obj.SetForegroundColour(self._prefs.GetValue('M_FG_COLOUR'))
                    tx.SetForegroundColour(self._prefs.GetValue('M_FG_COLOUR'))
                else:
                    obj.SetForegroundColour(INFO_COLOUR)
                    tx.SetForegroundColour(INFO_COLOUR)
                obj.Refresh()
                tx.Refresh()
                return

    # -----------------------------------------------------------------------
    # Setters for GUI
    # ----------------------------------------------------------------------

    def SetPreferences(self, prefs):
        """Set new preferences. Refresh GUI.

        :param prefs: (structs.Preferences)

        """
        self._prefs = prefs
        self.SetFont(prefs.GetValue('M_FONT'))
        self.SetBackgroundColour(prefs.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(prefs.GetValue('M_FG_COLOUR'))
        self.Refresh()

    # ----------------------------------------------------------------------

    def SetFont(self, font):
        """Change font of all wx texts.

        :param font: (wx.Font)

        """
        wx.Window.SetFont(self, font)
        for (tx,obj) in self._wxobj.values():
            tx.SetFont(font)
            if obj is not None:
                obj.SetFont(font)
            else:
                # a title (make it bold)
                new_font = wx.Font(font.GetPointSize(),
                                   font.GetFamily(),
                                   font.GetStyle(),
                                   wx.BOLD,
                                   False,
                                   font.GetFaceName(),
                                   font.GetEncoding())
                tx.SetFont(new_font)

    # ----------------------------------------------------------------------

    def SetBackgroundColour(self, color):
        """Change background of all texts.

        :param color: (wx.Color)

        """
        wx.Window.SetBackgroundColour(self, color)
        for (tx,obj) in self._wxobj.values():
            tx.SetBackgroundColour(color)
            if obj is not None:
                obj.SetBackgroundColour(color)

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """Change foreground of all texts.

        :param color: (wx.Color)

        """
        wx.Window.SetForegroundColour(self, color)
        for (tx,obj) in self._wxobj.values():
            tx.SetForegroundColour(color)
            if obj is not None:
                obj.SetForegroundColour(color)

    # ----------------------------------------------------------------------
    # Methods of the workers
    # ----------------------------------------------------------------------

    def ShowInfo(self):
        """Estimate all values then display the information."""

        # we never estimated values. we have to do it!
        if self._cv is None:
            try:
                self.SetChannel(self._channel)
            except Exception as e:
                ShowInformation(self, self._prefs, "Error: %s"%str(e))
                return

        # Amplitude
        self._wxobj["nframes"][1].ChangeValue(" "+str(self._channel.get_nframes())+" ")
        self._wxobj["minmax"][1].ChangeValue(" "+str(self._ca.minmax())+" ")
        self._wxobj["cross"][1].ChangeValue(" "+str(self._ca.cross())+" ")

        # Modifiable
        fm = str(self._channel.get_framerate())
        if not fm in AudioRoamerPanel.FRAMERATES:
            self._wxobj["framerate"][1].Append(fm)
        self._wxobj["framerate"][1].SetStringSelection(fm)
        self.MODIFIABLES["framerate"] = fm

        sp = str(self._channel.get_sampwidth()*8)
        if not sp in AudioRoamerPanel.SAMPWIDTH:
            self._wxobj["sampwidth"][1].Append(sp)
        self._wxobj["sampwidth"][1].SetStringSelection(sp)
        self.MODIFIABLES["sampwidth"] = sp

        # Clipping
        for i in range(1,10):
            cr = self._ca.clipping_rate(float(i)/10.) * 100.
            self._wxobj["clip"+str(i)][1].ChangeValue(" "+str(round(cr,2))+"% ")

        # Volumes / Silences
        vmin = self._cv.get_volstats().min()
        vmax = self._cv.get_volstats().max()
        vavg = self._cv.get_volstats().mean()
        vmin_db = sppasAudioConverter().amp2db(vmin)
        vmax_db = sppasAudioConverter().amp2db(vmax)
        vavg_db = sppasAudioConverter().amp2db(vavg)
        self._wxobj["volmin"][1].ChangeValue(" "+str(vmin)+" ("+str(vmin_db)+" dB) ")
        self._wxobj["volmax"][1].ChangeValue(" "+str(vmax)+" ("+str(vmax_db)+" dB) ")
        self._wxobj["volavg"][1].ChangeValue(" "+str(int(vavg))+" ("+str(vavg_db)+" dB) ")
        self._wxobj["volsil"][1].ChangeValue(" "+str(self._cv.search_threshold_vol())+" ")
        self._wxobj["nbipus"][1].ChangeValue(" "+str(len(self._tracks))+" ")
        d = sum([(e-s) for (s,e) in self._tracks])
        self._wxobj["duripus"][1].ChangeValue(" "+str(d)+" ")

    # -----------------------------------------------------------------------

    def SetChannel(self, new_channel):
        """Set a new channel, estimates the values to be displayed.

        :param new_channel: (sppasChannel)

        """
        # Set the channel
        self._channel = new_channel

        wx.BeginBusyCursor()
        b = wx.BusyInfo("Please wait while loading and analyzing data...")

        # To estimate values related to amplitude
        frames = self._channel.get_frames(self._channel.get_nframes())
        self._ca = sppasAudioFrames(frames, self._channel.get_sampwidth(), 1)

        # Estimates the RMS (=volume), then find where are silences, then IPUs
        self._cv = sppasChannelSilence(self._channel)
        self._cv.search_silences()               # threshold=0, mintrackdur=0.08
        self._cv.filter_silences()               # minsildur=0.2
        self._tracks = self._cv.extract_tracks() # mintrackdur=0.3

        b.Destroy()
        b = None
        wx.EndBusyCursor()

    # -----------------------------------------------------------------------

    def ApplyChanges(self, from_time=None, to_time=None):
        """Return a channel with changed applied.

        :param from_time: (float)
        :param to_time: (float)
        :returns: (sppasChannel) new channel or None if nothing changed

        """
        # Get the list of modifiable values from wx objects
        fm     = int(self._wxobj["framerate"][1].GetValue())
        sp     = int(int(self._wxobj["sampwidth"][1].GetValue())/8)
        mul    = float(self._wxobj["mul"][1].GetValue())
        bias   = int(self._wxobj["bias"][1].GetValue())
        offset = self._wxobj["offset"][1].GetValue()

        dirty = False
        if from_time is None:
            from_frame = 0
        else:
            from_frame = int(from_time * fm)
            dirty = True
        if to_time is None:
            to_frame = self._channel.get_nframes()
        else:
            dirty = True
            to_frame = int(to_time * fm)

        channel = self._channel.extract_fragment(from_frame,to_frame)

        # If something changed, apply this/these change-s to the channel
        if fm != self._channel.get_framerate() or sp != self._channel.get_sampwidth() or mul != 1. or bias != 0 or offset is True:
            wx.BeginBusyCursor()
            b = wx.BusyInfo("Please wait while formatting data...")
            channelfmt = sppasChannelFormatter(channel)
            channelfmt.set_framerate(fm)
            channelfmt.set_sampwidth(sp)
            channelfmt.convert()
            channelfmt.mul(mul)
            channelfmt.bias(bias)
            if offset is True:
                channelfmt.remove_offset()
            channel = channelfmt.get_channel()
            dirty = True
            b.Destroy()
            b = None
            wx.EndBusyCursor()

        if dirty is True:
            return channel
        return None

    # -----------------------------------------------------------------------

    def SaveChannel(self, parent_filename, period=False):
        """Save the channel in an audio file.

        :param parent_filename: (str)
        :param period: (bool) Save a portion of the channel only

        """
        s = None
        e = None
        if period is True:
            dlg = PeriodChooser(self, self._prefs, 0., float(self._channel.get_nframes())/float(self._channel.get_framerate()))
            answer = dlg.ShowModal()
            if answer == wx.ID_OK:
                (s, e) = dlg.GetValues()
                try:
                    s = float(s)
                    e = float(e)
                    if e < s:
                        raise Exception
                except Exception:
                    ShowInformation(self, self._prefs, "Error in the definition of the portion of time.", style=wx.ICON_ERROR)
                    return
            dlg.Destroy()
            if answer != wx.ID_OK:
                return

        new_filename = SaveAsAudioFile()

        # If it is the OK response, process the data.
        if new_filename is not None:
            if new_filename == parent_filename:
                ShowInformation(self, self._prefs, "Assigning the current file name is forbidden. Choose a new file name.", style=wx.ICON_ERROR)
                return

            # Create a formatted channel
            try:
                channel = self.ApplyChanges(s, e)
            except Exception as e:
                ShowInformation(self, self._prefs, "Error while formatting the channel: %s" % str(e), style=wx.ICON_ERROR)
                return

            message = "File {:s} saved successfully.".format(new_filename)
            if channel is None:
                channel = self._channel
            else:
                message += "\nYou can now open it with AudioRoamer to see your changes!"

            # Save the channel
            try:
                audio = sppasAudioPCM()
                audio.append_channel(channel)
                sppas.src.audiodata.aio.save(new_filename, audio)
            except Exception as e:
                message = "File not saved. Error: {:s}".format(str(e))
            else:
                # Update members
                self._filename = new_filename

            ShowInformation(self, self._prefs, message, style=wx.ICON_INFORMATION)

    # -----------------------------------------------------------------------

    def SaveInfos(self, parent_filename):
        """Ask for a filename then save all displayed information.

        :param parent_filename: (str)

        """
        new_filename = SaveAsAnyFile()
        # If it is the OK response, process the data.
        if new_filename is not None:
            content = self._infos_content(parent_filename)
            with codecs.open(new_filename, "w", sg.__encoding__) as fp:
                fp.write(content)

    # -----------------------------------------------------------------------
    # Private methods to list information in a "formatted" text.
    # -----------------------------------------------------------------------

    def _infos_content(self, parent_filename):
        content = ""
        content += self.__separator()
        content += self.__line(sg.__name__ + ' - Version ' + sg.__version__)
        content += self.__line(sg.__copyright__)
        content += self.__line("Web site: " + sg.__url__)
        content += self.__line("Contact: " + sg.__author__ + "(" + sg.__contact__ + ")")
        content += self.__separator()
        content += self.__newline()
        content += self.__line("Date: " + str(datetime.datetime.now()))

        # General information
        content += self.__section("General information")
        content += self.__line("Channel filename: %s"%self._filename)
        content += self.__line("Channel extracted from file: "+parent_filename)
        content += self.__line("Duration: %s sec."%self._channel.get_duration())
        content += self.__line("Framerate: %d Hz"%self._channel.get_framerate())
        content += self.__line("Samp. width: %d bits" % (int(self._channel.get_sampwidth())*8))

        # Amplitude
        content += self.__section("Amplitude")
        content += self.__line(AudioRoamerPanel.INFO_LABELS["nframes"][0]+self._wxobj["nframes"][1].GetValue())
        content += self.__line(AudioRoamerPanel.INFO_LABELS["minmax"][0]+self._wxobj["minmax"][1].GetValue())
        content += self.__line(AudioRoamerPanel.INFO_LABELS["cross"][0]+self._wxobj["cross"][1].GetValue())

        # Clipping
        content += self.__section("Amplitude clipping")
        for i in range(1,10):
            f = self._ca.clipping_rate(float(i)/10.) * 100.
            content += self.__item("  factor "+str(float(i)/10.)+": "+str(round(f, 2))+"%")

        # Volume
        content += self.__section("Root-mean square")
        content += self.__line(AudioRoamerPanel.INFO_LABELS["volmin"][0]+self._wxobj["volmin"][1].GetValue())
        content += self.__line(AudioRoamerPanel.INFO_LABELS["volmax"][0]+self._wxobj["volmax"][1].GetValue())
        content += self.__line(AudioRoamerPanel.INFO_LABELS["volavg"][0]+self._wxobj["volavg"][1].GetValue())

        # IPUs
        content += self.__section("Inter-Pausal Units automatic segmentation")
        content += self.__line(AudioRoamerPanel.INFO_LABELS["volsil"][0]+self._wxobj["volsil"][1].GetValue())
        content += self.__line(AudioRoamerPanel.INFO_LABELS["nbipus"][0]+self._wxobj["nbipus"][1].GetValue())
        content += self.__line(AudioRoamerPanel.INFO_LABELS["duripus"][0]+self._wxobj["duripus"][1].GetValue())
        content += self.__newline()
        content += self.__separator()

        return content

    # -----------------------------------------------------------------------
    # Private methods.
    # -----------------------------------------------------------------------

    def __add_info(self, parent, gbs, key, row):
        """Private method to add an info into the GridBagSizer."""
        static_tx = wx.StaticText(parent, -1, AudioRoamerPanel.INFO_LABELS[key][0])
        gbs.Add(static_tx, (row, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
        tx = wx.TextCtrl(parent, -1, AudioRoamerPanel.INFO_LABELS[key][1], style=wx.TE_READONLY)
        tx.SetMinSize((120,24))
        gbs.Add(tx, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
        self._wxobj[key] = (static_tx,tx)

    def __add_clip(self, parent, gbs, i):
        """Private method to add a clipping value in a GridBagSizer."""
        static_tx = wx.StaticText(parent, -1, "  factor "+str(float(i)/10.)+": ")
        gbs.Add(static_tx, (i, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
        tx = wx.TextCtrl(parent, -1, " ... ", style=wx.TE_READONLY|wx.TE_RIGHT)
        gbs.Add(tx, (i, 1), flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=2)
        self._wxobj["clip"+str(i)] = (static_tx,tx)

    def __add_modifiable(self, parent, gbs, obj, key, row):
        static_tx = wx.StaticText(parent, -1, AudioRoamerPanel.INFO_LABELS[key][0])
        #static_tx =  wx.TextCtrl(parent, -1, AudioRoamerPanel.INFO_LABELS[key][0], style=wx.TE_READONLY|wx.TE_LEFT|wx.NO_BORDER)
        gbs.Add(static_tx, (row, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
        gbs.Add(obj, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
        self._wxobj[key] = (static_tx,obj)

    # -----------------------------------------------------------------------

    def __section(self, title):
        """Private method to make to look like a title."""
        text  = self.__newline()
        text += self.__separator()
        text += self.__line(title)
        text += self.__separator()
        text += self.__newline()
        return text

    def __line(self, msg):
        """Private method to make a text as a simple line."""
        text  = msg.strip()
        text += self.__newline()
        return text

    def __item(self, msg):
        """Private method to make a text as a simple item."""
        text  = "  - "
        text += self.__line(msg)
        return text

    def __newline(self):
        """Private method to return a new empty line."""
        if wx.Platform == '__WXMAC__' or wx.Platform == '__WXGTK__':
            return "\n"
        return "\r\n"

    def __separator(self):
        """Private method to return a separator line."""
        text  = "-----------------------------------------------------------------"
        text += self.__newline()
        return text

# ----------------------------------------------------------------------------


def ShowAudioRoamerDialog(parent, preferences, filename):
    audio = sppas.src.audiodata.aio.open(filename)
    if audio.get_nframes() > 15000000:
        userChoice = ShowYesNoQuestion(None, preferences, "Audio file is very large. "
                                                          "Showing more will take a while "
                                                          "and could generate a memory error. "
                                                          "Really want more?")
        if userChoice == wx.ID_NO:
            return
    audio.close()
    dialog = AudioRoamerDialog(parent, preferences, filename)
    dialog.ShowModal()
    dialog.Destroy()
