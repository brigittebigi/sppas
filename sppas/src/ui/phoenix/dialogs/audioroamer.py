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

    src.ui.phoenix.dialogs.audioroamer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import datetime

from sppas.src.audiodata import sppasAudioPCM
from sppas.src.audiodata.channelsilence import sppasChannelSilence
from sppas.src.audiodata.channelformatter import sppasChannelFormatter
from sppas.src.audiodata.audioframes import sppasAudioFrames
from sppas.src.audiodata.audio import sppasAudioPCM
from sppas.src.audiodata.audioconvert import sppasAudioConverter

from sppas.src.config import msg
from sppas.src.config import sg
from sppas.src.utils import u

from ..windows import sppasDialog
from ..dialogs import Information
from ..windows.book import sppasNotebook
from ..windows import sppasPanel
from ..windows import BitmapTextButton

# --------------------------------------------------------------------------


def _(message):
    return u(msg(message, "ui"))


MSG_HEADER_AUDIOROAMER = _("Audio roamer")
MSG_ACTION_SAVE_CHANNEL = _("Save channel as")
MSG_ACTION_SAVE_FRAGMENT = _("Save fragment channel as")
MSG_ACTION_SAVE_INFOS = _("Save information as")
OKAY = _("Okay")

INFO_COLOUR = wx.Colour(55, 30, 200, 128)

# ---------------------------------------------------------------------------


class sppasTiersViewDialog(sppasDialog):
    """A dialog with a notebook to manage each channel information.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Returns wx.ID_OK if ShowModal().

    """

    def __init__(self, parent, audio):
        """Create a dialog to fix settings.

        :param parent: (wx.Window)
        :param audio: (sppasAudioPCM)

        """
        super(sppasTiersViewDialog, self).__init__(
            parent=parent,
            title="Audio roamer",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="audioroamer-dialog")

        self.CreateHeader(MSG_HEADER_AUDIOROAMER, "audio_roamer")
        self._create_content(audio)
        self.CreateActions([], [wx.ID_OK])

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)
        self.Refresh()

    # -----------------------------------------------------------------------

    def _create_content(self, audio):
        """Create the content of the dialog."""
        # Make the notebook and an image list
        notebook = sppasNotebook(self, name="content")
        for i in range(audio.get_nchannels()):
            idx = audio.extract_channel(i)
            channel = audio.get_channel(idx)
            page = ChannelInfosPanel(notebook, channel)
            notebook.AddPage(page, "Channel {:d}".format(idx))

        self.ShowPage(0)
        notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_page_changed)
        self.SetContent(notebook)

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _on_page_changed(self, event):
        old_selection = event.GetOldSelection()
        new_selection = event.GetSelection()
        if old_selection != new_selection:
            self.ShowPage(new_selection)

    # ------------------------------------------------------------------------

    def ShowPage(self, idx):
        page = self.FindWindow("content").GetPage(idx)
        page.ShowInfo()

# ---------------------------------------------------------------------------


class ChannelInfosPanel(sppasPanel):
    """Open a dialog to display information about 1 channel of an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    FRAMERATES = ["16000", "32000", "48000"]
    SAMPWIDTH = ["8", "16", "32"]
    INFO_LABELS = {"framerate": ("  Frame rate (Hz): ", FRAMERATES[0]),
                   "sampwidth": ("  Samp. width (bits): ", SAMPWIDTH[0]),
                   "mul": ("  Multiply values by: ", "1.0"),
                   "bias": ("  Add bias value: ", "0"),
                   "offset": ("  Remove offset value: ", False),
                   "nframes": ("  Number of frames: ", " ... "),
                   "minmax": ("  Min/Max values: ", " ... "),
                   "cross": ("  Zero crossings: ", " ... "),
                   "volmin": ("  Volume min: ", " ... "),
                   "volmax": ("  Volume max: ", " ... "),
                   "volavg": ("  Volume mean: ", " ... "),
                   "volsil": ("  Threshold volume: ", " ... "),
                   "nbipus": ("  Number of IPUs: ", " ... "),
                   "duripus": ("  Nb frames of IPUs: ", " ... ")
                   }

    def __init__(self, parent, channel):
        """Create a ChannelInfosPanel.

        :param parent: (wx.Window)
        :param channel: (sppasChannel)

        """
        super(ChannelInfosPanel, self).__init__(parent)
        self._channel  = channel  # Channel
        self._filename = None     # Fixed when "Save as" is clicked
        self._cv = None           # sppasChannelSilence, fixed by ShowInfos
        self._tracks = None       # the IPUs we found automatically
        self._ca = None           # sppasAudioFrames with only this channel, fixed by ShowInfos
        self._wxobj = {}          # Dict of wx objects
        self._prefs = None

        sizer = self._create_content()

        self.MODIFIABLES = {}
        for key in ["framerate", "sampwidth", "mul", "bias", "offset"]:
            self.MODIFIABLES[key] = ChannelInfosPanel.INFO_LABELS[key][1]

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    # -----------------------------------------------------------------------
    # Private methods to show information about the channel into the GUI.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main sizer, add content then return it."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        top_panel = sppasPanel(self)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        info = self._create_content_infos()
        clip = self._create_content_clipping()
        ipus = self._create_content_ipus()
        top_sizer.Add(info, 1, wx.EXPAND, 0)
        top_sizer.Add(clip, 1, wx.EXPAND | wx.ALL, 4)
        top_sizer.Add(ipus, 1, wx.EXPAND, 0)
        top_panel.SetSizerAndFit(top_sizer)

        buttons = self._create_buttons()
        self.Bind(wx.EVT_BUTTON, self._process_event)

        sizer.Add(top_panel, 1, wx.EXPAND, 4)
        sizer.Add(buttons, 0, wx.EXPAND, 4)

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

        cfm = wx.ComboBox(self, -1, choices=ChannelInfosPanel.FRAMERATES, style=wx.CB_READONLY)
        cfm.SetMinSize((120,24))
        self.__add_modifiable(self, gbs, cfm, "framerate", 5)
        self.Bind(wx.EVT_COMBOBOX, self.OnModif, cfm)

        csp = wx.ComboBox(self, -1, choices=ChannelInfosPanel.SAMPWIDTH, style=wx.CB_READONLY)
        csp.SetMinSize((120,24))
        self.__add_modifiable(self, gbs, csp, "sampwidth", 6)
        self.Bind(wx.EVT_COMBOBOX, self.OnModif, csp)

        txm = wx.TextCtrl(self, -1, ChannelInfosPanel.INFO_LABELS["mul"][1])  #, validator=TextAsNumericValidator())
        txm.SetInsertionPoint(0)
        self.__add_modifiable(self, gbs, txm, "mul", 7)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnModif, txm)

        txb = wx.TextCtrl(self, -1, ChannelInfosPanel.INFO_LABELS["bias"][1])  #, validator=TextAsNumericValidator())
        txb.SetInsertionPoint(0)
        self.__add_modifiable(self, gbs, txb, "bias", 8)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnModif, txb)

        cb = wx.CheckBox(self, -1, style=wx.NO_BORDER)
        cb.SetValue(ChannelInfosPanel.INFO_LABELS["offset"][1])
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

    def _create_buttons(self):
        """Create the buttons and bind events."""
        panel = sppasPanel(self, name="channel_actions")
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the buttons
        save_channel_btn = self.__create_action_button(panel, MSG_ACTION_SAVE_CHANNEL, "save")
        save_fragment_btn = self.__create_action_button(panel, MSG_ACTION_SAVE_FRAGMENT, "save")
        save_info_btn = self.__create_action_button(panel, MSG_ACTION_SAVE_INFOS, "save")

        sizer.Add(save_channel_btn, 1, wx.ALL | wx.EXPAND, 10)
        sizer.Add(save_fragment_btn, 1, wx.ALL | wx.EXPAND, 10)
        sizer.Add(save_info_btn, 1, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(sizer)
        return panel

    # -----------------------------------------------------------------------

    def __create_action_button(self, parent, text, icon):
        btn = BitmapTextButton(parent, label=text, name=icon)
        btn.LabelPosition = wx.RIGHT
        btn.Spacing = sppasDialog.fix_size(12)
        btn.BorderWidth = 1
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(sppasDialog.fix_size(32),
                               sppasDialog.fix_size(32)))

        return btn

    # -----------------------------------------------------------------------
    # Callbacks to events
    # -----------------------------------------------------------------------

    def OnModif(self, evt):
        """Callback on a modifiable object: adapt foreground color.

        :param evt: (wx.event)

        """
        evtobj = evt.GetEventObject()
        evtvalue = evtobj.GetValue()
        for key, defaultvalue in self.MODIFIABLES.items():
            (tx, obj) = self._wxobj[key]
            if evtobj == obj:
                if evtvalue == defaultvalue:
                    obj.SetForegroundColour(self.GetForegroundColour())
                    tx.SetForegroundColour(self.GetForegroundColour())
                else:
                    obj.SetForegroundColour(INFO_COLOUR)
                    tx.SetForegroundColour(INFO_COLOUR)
                obj.Refresh()
                tx.Refresh()
                return

    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        event.Skip()

    # -----------------------------------------------------------------------
    # Setters for GUI
    # ----------------------------------------------------------------------

    def SetFont(self, font):
        """Change font of all wx texts.

        :param font: (wx.Font)

        """
        wx.Panel.SetFont(self, font)
        for (tx, obj) in self._wxobj.values():
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
        for (tx, obj) in self._wxobj.values():
            tx.SetBackgroundColour(color)
            if obj is not None:
                obj.SetBackgroundColour(color)

    # ----------------------------------------------------------------------

    def SetForegroundColour(self, color):
        """Change foreground of all texts.

        :param color: (wx.Color)

        """
        wx.Window.SetForegroundColour(self, color)
        for (tx, obj) in self._wxobj.values():
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
                # ShowInformation(self, self._prefs, "Error: %s"%str(e))
                return

        # Amplitude
        self._wxobj["nframes"][1].ChangeValue(" "+str(self._channel.get_nframes())+" ")
        self._wxobj["minmax"][1].ChangeValue(" "+str(self._ca.minmax())+" ")
        self._wxobj["cross"][1].ChangeValue(" "+str(self._ca.cross())+" ")

        # Modifiable
        fm = str(self._channel.get_framerate())
        if fm not in ChannelInfosPanel.FRAMERATES:
            self._wxobj["framerate"][1].Append(fm)
        self._wxobj["framerate"][1].SetStringSelection(fm)
        self.MODIFIABLES["framerate"] = fm

        sp = str(self._channel.get_sampwidth()*8)
        if sp not in ChannelInfosPanel.SAMPWIDTH:
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
        d = sum([(e-s) for (s, e) in self._tracks])
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
        self._cv.search_silences()                # threshold=0, mintrackdur=0.08
        self._cv.filter_silences()                # minsildur=0.2
        self._tracks = self._cv.extract_tracks()  # mintrackdur=0.3

        # b.Destroy()
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
        fm = int(self._wxobj["framerate"][1].GetValue())
        sp = int(int(self._wxobj["sampwidth"][1].GetValue())/8)
        mul = float(self._wxobj["mul"][1].GetValue())
        bias = int(self._wxobj["bias"][1].GetValue())
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
            # b.Destroy()
            b = None
            wx.EndBusyCursor()

        if dirty is True:
            return channel
        return None

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
        content += self.__line(ChannelInfosPanel.INFO_LABELS["nframes"][0]+self._wxobj["nframes"][1].GetValue())
        content += self.__line(ChannelInfosPanel.INFO_LABELS["minmax"][0]+self._wxobj["minmax"][1].GetValue())
        content += self.__line(ChannelInfosPanel.INFO_LABELS["cross"][0]+self._wxobj["cross"][1].GetValue())

        # Clipping
        content += self.__section("Amplitude clipping")
        for i in range(1,10):
            f = self._ca.clipping_rate(float(i)/10.) * 100.
            content += self.__item("  factor "+str(float(i)/10.)+": "+str(round(f, 2))+"%")

        # Volume
        content += self.__section("Root-mean square")
        content += self.__line(ChannelInfosPanel.INFO_LABELS["volmin"][0]+self._wxobj["volmin"][1].GetValue())
        content += self.__line(ChannelInfosPanel.INFO_LABELS["volmax"][0]+self._wxobj["volmax"][1].GetValue())
        content += self.__line(ChannelInfosPanel.INFO_LABELS["volavg"][0]+self._wxobj["volavg"][1].GetValue())

        # IPUs
        content += self.__section("Inter-Pausal Units automatic segmentation")
        content += self.__line(ChannelInfosPanel.INFO_LABELS["volsil"][0]+self._wxobj["volsil"][1].GetValue())
        content += self.__line(ChannelInfosPanel.INFO_LABELS["nbipus"][0]+self._wxobj["nbipus"][1].GetValue())
        content += self.__line(ChannelInfosPanel.INFO_LABELS["duripus"][0]+self._wxobj["duripus"][1].GetValue())
        content += self.__newline()
        content += self.__separator()

        return content

    # -----------------------------------------------------------------------
    # Private methods.
    # -----------------------------------------------------------------------

    def __add_info(self, parent, gbs, key, row):
        """Private method to add an info into the GridBagSizer."""
        static_tx = wx.StaticText(parent, -1, ChannelInfosPanel.INFO_LABELS[key][0])
        gbs.Add(static_tx, (row, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
        tx = wx.TextCtrl(parent, -1, ChannelInfosPanel.INFO_LABELS[key][1], style=wx.TE_READONLY)
        tx.SetMinSize(wx.Size(120, 24))
        gbs.Add(tx, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border=2)
        self._wxobj[key] = (static_tx, tx)

    def __add_clip(self, parent, gbs, i):
        """Private method to add a clipping value in a GridBagSizer."""
        static_tx = wx.StaticText(parent, -1, "  factor "+str(float(i)/10.)+": ")
        gbs.Add(static_tx, (i, 0), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=2)
        tx = wx.TextCtrl(parent, -1, " ... ", style=wx.TE_READONLY | wx.TE_RIGHT)
        gbs.Add(tx, (i, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=2)
        self._wxobj["clip"+str(i)] = (static_tx, tx)

    def __add_modifiable(self, parent, gbs, obj, key, row):
        static_tx = wx.StaticText(parent, -1, ChannelInfosPanel.INFO_LABELS[key][0])
        #static_tx =  wx.TextCtrl(parent, -1, AudioRoamerPanel.INFO_LABELS[key][0], style=wx.TE_READONLY|wx.TE_LEFT|wx.NO_BORDER)
        gbs.Add(static_tx, (row, 0), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=2)
        gbs.Add(obj, (row, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=2)
        self._wxobj[key] = (static_tx, obj)

    # -----------------------------------------------------------------------

    def __section(self, title):
        """Private method to make to look like a title."""
        text = self.__newline()
        text += self.__separator()
        text += self.__line(title)
        text += self.__separator()
        text += self.__newline()
        return text

    def __line(self, msg):
        """Private method to make a text as a simple line."""
        text = msg.strip()
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
        text = "-----------------------------------------------------------------"
        text += self.__newline()
        return text

# ---------------------------------------------------------------------------


def AudioRoamer(parent, audio):
    """Open a dialog to display information about channels of an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    :param parent: (wx.Window)
    :param audio: (sppasAudioPCM)
    :returns: wx.ID_OK

    """
    if isinstance(audio, sppasAudioPCM) is False:
        wx.LogError("{} is not of type sppasAudioPCM".format(audio))

    dialog = sppasTiersViewDialog(parent, audio)
    response = dialog.ShowModal()
    dialog.DestroyFadeOut()
    return response
