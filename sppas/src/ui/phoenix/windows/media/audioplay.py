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

    src.ui.phoenix.windows.media.audioplay.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires simpleaudio library to play the audio file stream.

"""

import os
import wx
import threading

from sppas.src.config import paths
from sppas.src.config import MediaState

from sppas.src.audiodata import sppasSimpleAudioPlayer

from sppas.src.ui.phoenix.windows.media.mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class sppasAudioPlayer(sppasSimpleAudioPlayer, wx.Timer):
    """An audio player based on simpleaudio library and a timer.

    :author:       Nicolas Chazeau, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is inheriting of a Timer in order to update the position
    in the stream and thus to implement the 'tell' method.
    This class is using a thread to load the frames of the audio file.

    Events emitted by this class:

        - wx.EVT_TIMER when the audio is playing
        - MediaEvents.EVT_MEDIA_LOADED when the frames were loaded
        - MediaEvents.EVT_MEDIA_NOT_LOADED when an error occurred

    The timer delay is fixed to 10ms but I observed a real delay of:
       - about 15 ms under Windows;
       - about XX under MacOS;
       - about 10 ms under Linux.
    The wx.Timer documentation indicates that its precision is
    platform-dependent, but in general will not be better than 1ms
    nor worse than 1s...

    """

    # Delay in seconds to update the position value in the stream.
    TIMER_DELAY = 0.0010

    # -----------------------------------------------------------------------

    def __init__(self, owner):
        """Create an instance of sppasAudioPlayer.

        :param owner: (wx.Window) Owner of this class.

        """
        wx.Timer.__init__(self, owner)
        sppasSimpleAudioPlayer.__init__(self)
        self.__th = None

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Override. Load the file that filename refers to.

        :param filename: (str)
        :return: (bool) Always returns False

        """
        # Create a Thread with a function with args
        self.__th = threading.Thread(target=self.__threading_load, args=(filename,))
        # Start the thread
        self.__th.start()

    # -----------------------------------------------------------------------

    def __del__(self):
        self.Stop()
        try:
            if self._audio is not None:
                self._audio.close()
            if self.__th is not None:
                if self.__th.is_alive():
                    del self.__th
        except:
            pass

    # -----------------------------------------------------------------------

    def reset(self):
        """Override. Re-initialize all known data."""
        self.Stop()
        sppasSimpleAudioPlayer.reset(self)

    # -----------------------------------------------------------------------

    def play(self):
        """Override. Start to play the audio stream from the current position.

        :return: (bool) True if the action of playing was performed

        """
        played = sppasSimpleAudioPlayer.play(self)
        if played is True:
            self.Start(int(sppasAudioPlayer.TIMER_DELAY * 1000.))

        return played

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the audio.

        :return: (bool) True if the action of stopping was performed

        """
        stopped = sppasSimpleAudioPlayer.stop(self)
        if stopped is True:
            self.Stop()

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the audio stream (float)."""
        offset = self._audio.tell()
        return float(offset) / float(self._audio.get_framerate())

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def Notify(self):
        """Override. Manage the current position in the audio stream."""
        if self._ms == MediaState().playing:
            # the audio stream is currently playing
            if self._sa_play.is_playing() is True:
                self._reposition()
            # the audio stream reached the end of the stream and it stopped
            else:
                self.stop()
            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)

    # -----------------------------------------------------------------------

    def __threading_load(self, filename):
        """Really load the file that filename refers to.

        Send an event when load is finished.

        :param filename: (str)

        """
        self._ms = MediaState().loading
        value = sppasSimpleAudioPlayer.load(self, filename)
        if value is True:
            evt = MediaEvents.MediaLoadedEvent()
        else:
            evt = MediaEvents.MediaNotLoadedEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        self._ms = MediaState().stopped

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="AudioPlayer")

        # The player!
        self.ap = sppasAudioPlayer(owner=self)

        # Actions to perform with the player
        btn2 = wx.Button(self, -1, "Play", name="btn_play")
        btn2.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._on_play_ap, btn2)
        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self._on_pause_ap, btn3)
        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self._on_stop_ap, btn4)
        sizer = wx.BoxSizer()
        sizer.Add(btn2, 0, wx.ALL, 4)
        sizer.Add(btn3, 0, wx.ALL, 4)
        sizer.Add(btn4, 0, wx.ALL, 4)

        # a slider to display the current position
        self.slider = wx.Slider(self, -1, 0, 0, 10, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.slider.SetMinSize(wx.Size(250, -1))
        self.Bind(wx.EVT_SLIDER, self._on_seek_slider, self.slider)

        # Organize items
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(sizer, 1, wx.EXPAND)
        main_sizer.Add(self.slider, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        # Events
        # Custom event to inform the media is loaded
        self.ap.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.ap.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        # Event received every 10ms (in theory) when the audio is playing
        self.ap.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        self.ap.load(os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        wx.LogDebug("Audio file loaded successfully")
        self.FindWindow("btn_play").Enable(True)
        duration = self.ap.duration()
        self.slider.SetRange(0, int(duration * 1000.))

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        wx.LogError("Audio file not loaded")
        self.FindWindow("btn_play").Enable(False)
        self.slider.SetRange(0, 0)

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        self.ap.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        self.ap.pause()

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        self.ap.stop()
        self.slider.SetValue(0)

    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))
        event.Skip()

    # ----------------------------------------------------------------------

    def _on_seek_slider(self, event):
        time_pos_ms = self.slider.GetValue()
        self.ap.seek(float(time_pos_ms) / 1000.)