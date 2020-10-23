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

    src.ui.phoenix.windows.media.audioctrl.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires simpleaudio library to play the audio file stream.

"""

import os
import wx
import threading
import time

from sppas.src.config import paths
from sppas.src.config import MediaState

import sppas.src.audiodata.aio
from sppas.src.audiodata import sppasAudioPCM
from sppas.src.audiodata.audioplayer import sppasSimpleAudioPlayer

from sppas.src.ui.phoenix.windows.panels import sppasPanel
from sppas.src.ui.phoenix.windows.datactrls import sppasWaveformWindow
from sppas.src.ui.phoenix.windows.media.mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class AudioViewProperties(object):
    """Represent the possible views of an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    """

    INFOS_HEIGHT = 20
    WAVEFORM_HEIGHT = 100
    SPECTRAL_HEIGHT = 100
    LEVEL_HEIGHT = 30

    # -----------------------------------------------------------------------

    def __init__(self, parent, audio_filename):
        """Create the AudioViewProperties.

        :param parent: (wx.Window) Must not be None.
        :param audio_filename: (str)

        """
        self.__parent = parent
        # All possible views and value (enabled=True, disabled=False)
        self.__infos = True
        self.__waveform = None
        self.__spectral = False
        self.__level = False
        self.__samples = (0., 0., None)

        # The audio PCM
        try:
            self.__audio = sppas.src.audiodata.aio.open(audio_filename)
        except Exception as e:
            wx.LogError("View of the audio file {:s} is un-available: "
                        "{:s}".format(audio_filename, str(e)))
            self.__audio = sppasAudioPCM()

    # -----------------------------------------------------------------------
    # Getters for audio infos
    # -----------------------------------------------------------------------

    def GetNumberChannels(self):
        return self.__audio.get_nchannels()

    nchannels = property(fget=GetNumberChannels)

    # -----------------------------------------------------------------------

    def GetSampWidth(self):
        return self.__audio.get_sampwidth()

    sampwidth = property(fget=GetSampWidth)

    # -----------------------------------------------------------------------

    def GetFramerate(self):
        return self.__audio.get_framerate()

    framerate = property(fget=GetFramerate)

    # -----------------------------------------------------------------------

    def GetDuration(self):
        return self.__audio.get_duration()

    duration = property(fget=GetDuration)

    # -----------------------------------------------------------------------
    # Enable/Disable views
    # -----------------------------------------------------------------------

    def get_infos(self):
        return self.__infos

    def EnableInfos(self, value):
        """Enable the view of the infos.

        Cant be disabled if the audio failed to be loaded.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audio.get_nchannels() > 0:
            self.__infos = True
            return True

        self.__infos = False
        return False

    # -----------------------------------------------------------------------

    def get_waveform(self):
        return self.__waveform

    def EnableWaveform(self, value):
        """Enable the view of the waveform.

        Can't be enabled if the audio has more than 1 channel.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audio.get_nchannels() == 1:
            self.__waveform = sppasWaveformWindow(self.__parent)
            return True

        self.__waveform = None
        return False

    # -----------------------------------------------------------------------

    def EnableSpectral(self, value):
        """Enable the view of the spectrogram.

        Can't be enabled if the audio has more than 1 channel.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audio.get_nchannels() == 1:
            self.__spectral = True
            return True

        self.__spectral = False
        return False

    # -----------------------------------------------------------------------

    def EnableLevel(self, value):
        """Enable the view of the level.

        Can't be enabled if the audio has more than 1 channel.

        :param value: (bool)
        :return: (bool)

        """
        value = bool(value)
        if value is True and self.__audio.get_nchannels() == 1:
            self.__level = True
            return True

        self.__level = False
        return False

    # -----------------------------------------------------------------------
    # Height of views
    # -----------------------------------------------------------------------

    def GetWaveformHeight(self):
        """Return the height required to draw the Waveform."""
        h = AudioViewProperties.WAVEFORM_HEIGHT
        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def GetInfosHeight(self):
        """Return the height required to draw the audio information."""
        h = AudioViewProperties.INFOS_HEIGHT
        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def GetLevelHeight(self):
        """Return the height required to draw the audio volume level."""
        h = AudioViewProperties.LEVEL_HEIGHT
        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def GetSpectralHeight(self):
        """Return the height required to draw the audio spectrum."""
        h = AudioViewProperties.SPECTRAL_HEIGHT
        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass
        return h

    # -----------------------------------------------------------------------

    def GetMinHeight(self):
        """Return the min height required to draw all views."""
        h = 0
        if self.__infos is True:
            h += AudioViewProperties.INFOS_HEIGHT
        if self.__waveform is not None:
            h += AudioViewProperties.WAVEFORM_HEIGHT
        if self.__level is True:
            h += AudioViewProperties.LEVEL_HEIGHT
        if self.__spectral is True:
            h += AudioViewProperties.SPECTRAL_HEIGHT

        try:
            h = self.__parent.fix_size(h)
        except AttributeError:
            pass

        return h

    # -----------------------------------------------------------------------

    def DrawWaveform(self, pos, size, start_time, end_time):
        self.__waveform.SetPosition(pos)
        self.__waveform.SetSize(size)

        # If we have to draw the same data, there's no need to read them again
        if start_time == self.__samples[0] and end_time == self.__samples[1]:
            self.__waveform.SetData([self.__samples[2], self.__audio.get_sampwidth()])
        else:
            nframes = int((end_time - start_time) * self.__audio.get_framerate())
            self.__audio.seek(int(start_time * float(self.__audio.get_framerate())))
            # read samples of all channels. Channel 0 is data[0]
            data = self.__audio.read_samples(nframes)
            self.__waveform.SetData([data[0], self.__audio.get_sampwidth()])

            # store data to eventually re-draw
            self.__samples = (start_time, end_time, data[0])


# ---------------------------------------------------------------------------


class sppasMediaCtrl(object):
    """Create an audio control embedded in a panel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Events emitted by this class:

        - MediaEvents.MediaActionEvent
        - MediaEvents.MediaLoadedEvent
        - MediaEvents.MediaNotLoadedEvent

    """

    # -----------------------------------------------------------------------
    # This object size.
    # By default, it is a DFHD aspect ratio (super ultra-wide displays) 32:9
    MIN_WIDTH = 178
    MIN_HEIGHT = 50

    DEFAULT_WIDTH = MIN_WIDTH * 3
    DEFAULT_HEIGHT = MIN_HEIGHT * 3

    # -----------------------------------------------------------------------
    # Delays for loading media files
    LOAD_DELAY = 500
    MAX_LOAD_DELAY = 3000

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="AudioCtrl")

        btn2 = wx.Button(self, -1, "Play", name="btn_play")
        btn2.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._on_play_ap, btn2)

        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self._on_pause_ap, btn3)

        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self._on_stop_ap, btn4)

        self.ap = sppasAudioCtrl(self)

        sizer = wx.BoxSizer()
        sizer.Add(btn2, 0, wx.ALL, 4)
        sizer.Add(btn3, 0, wx.ALL, 4)
        sizer.Add(btn4, 0, wx.ALL, 4)
        self.SetSizer(sizer)

        # wx.CallAfter(self.DoLoadFile)
        self.Bind(wx.EVT_TIMER, self._on_timer)

        # Custom event to inform the media is loaded
        self.ap.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.ap.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)

    # ----------------------------------------------------------------------

    def DoLoadFile(self):
        wx.LogDebug("Start loading media...")
        # self.ac.load(os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))
        wx.LogDebug("Media loaded.")

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        print("media loaded successfully")
        self.FindWindow("btn_play").Enable(True)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        print("media not loaded")
        self.FindWindow("btn_play").Enable(False)

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        self.ap.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        self.ap.pause()

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        self.ap.stop()

    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        print('on timer received by the parent. time={}'.format(str(self.ap.tell())))
        event.Skip()
