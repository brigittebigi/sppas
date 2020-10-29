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

    Requires simpleaudio library to play the audio file stream. Raise a
    FeatureException at init if 'audioplay' feature is not enabled.

"""

import os
import wx
import threading

from sppas.src.config import paths
from sppas.src.config import MediaState
from sppas.src.utils import b

from sppas.src.audiodata import sppasSimpleAudioPlayer

from sppas.src.ui.phoenix.windows.media.mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class sppasAudioPlayer(sppasSimpleAudioPlayer, wx.Timer):
    """An audio player based on simpleaudio library and a timer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is inheriting of a Timer in order to update the position
    in the stream and thus to implement the 'tell' method.
    This class is using a thread to load the frames of the audio file.

    Events emitted by this class:

        - wx.EVT_TIMER when the audio is playing every TIMER_DELAY seconds
        - MediaEvents.EVT_MEDIA_LOADED when the frames were loaded
        - MediaEvents.EVT_MEDIA_NOT_LOADED when an error occurred

    The wx.Timer documentation indicates that its precision is
    platform-dependent, but in general will not be better than 1ms
    nor worse than 1s...

    When the timer delay is fixed to 10ms, the observed delays are:
       - about 15 ms under Windows;
       - 10 ms under MacOS;
       - 10 ms under Linux.

    When the timer delay is fixed to 5ms, the observed delays are:
       - about 15 ms under Windows;
       - 6 ms under MacOS;
       - 5.5 ms under Linux.

    When the timer delay is fixed to 1ms, the observed delays are:
       - about 15 ms under Windows;
       - 2 ms under MacOS;
       - 1.3 ms under Linux.

    """

    # Delay in seconds to update the position value in the stream & to notify
    TIMER_DELAY = 0.010

    # -----------------------------------------------------------------------

    def __init__(self, owner):
        """Create an instance of sppasAudioPlayer.

        :param owner: (wx.Window) Owner of this class.

        """
        wx.Timer.__init__(self, owner)
        sppasSimpleAudioPlayer.__init__(self)

        # A thread to load the frames of the audio
        self.__th = None

        # A time period to play the audio stream. Default is whole.
        self._period = None

    # -----------------------------------------------------------------------

    def __del__(self):
        self.reset()

    # -----------------------------------------------------------------------

    def reset(self):
        """Override. Re-initialize all known data and stop the timer."""
        self.Stop()
        self._period = None
        try:
            if self.__th is not None:
                if self.__th.is_alive():
                    # Python does not implement a "stop()" method for threads
                    del self.__th
                    self.__th = None
                # The audio was not created if the init raised a FeatureException
                sppasSimpleAudioPlayer.reset(self)
        except:
            pass

    # -----------------------------------------------------------------------

    def set_period(self, start_time, end_time):
        """Fix the range period of time to play.

        :param start_time: (float) Time to start playing in seconds
        :param end_time: (float) Time to stop playing in seconds

        """
        start_time = float(start_time)
        end_time = float(end_time)
        if end_time <= start_time:
            raise ValueError("End can't be greater or equal than start")

        self._period = (start_time, end_time)
        if self._ms in (MediaState().playing, MediaState().paused):
            self.stop()
            self.play()
            if self._ms == MediaState().paused:
                self.pause()

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Override. Load the file that filename refers to.

        :param filename: (str)
        :return: (bool) Always returns False

        """
        # Create a Thread with a function with args
        self.__th = threading.Thread(target=self.__threading_load,
                                     args=(filename,))
        # Start the thread
        self.__th.start()

    # -----------------------------------------------------------------------

    def play(self):
        """Override. Start to play the audio stream.

        Start playing only is the audio stream is currently stopped or
        paused.

        Start playing only if the defined period is inside or overlapping
        this audio stream AND if the the current position is inside the
        period.

        :return: (bool) True if the action of playing was started

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
        if self._sa_play is not None:
            self._sa_play.stop()
            self._ms = MediaState().stopped
            self.seek(self._period[0])
            self.Stop()
            return True
        return False

    # -----------------------------------------------------------------------

    def seek(self, time_pos=0.):
        """Seek the audio stream at the given position in time.

        :param time_pos: (float) Time in seconds

        """
        time_pos = float(time_pos)
        if time_pos < 0.:
            time_pos = 0.
        if time_pos > self.get_duration():
            time_pos = self.get_duration()
        if time_pos > self._period[1]:
            time_pos = self._period[1]
        if time_pos < self._period[0]:
            time_pos = self._period[0]

        return sppasSimpleAudioPlayer.seek(self, time_pos)

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the audio stream (float)."""
        offset = self._audio.tell()
        return float(offset * self._audio.get_nchannels()) / float(self._audio.get_framerate())

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def Notify(self):
        """Override. Notify the owner of the EVT_TIMER event.

        Manage the current position in the audio stream.

        """
        # Nothing to do if we are not playing (probably paused).
        if self._ms == MediaState().playing:
            # the audio stream is currently playing
            if self._sa_play.is_playing() is True:
                self._reposition()
            # the audio stream reached the end of the stream and it stopped
            else:
                self.stop()
            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)

        elif self._ms != MediaState().paused:
            self.stop()

    # -----------------------------------------------------------------------
    # Private & Protected methods
    # -----------------------------------------------------------------------

    def _extract_frames(self):
        """Override. Return the frames to play in the given period.

        """
        # Check if the current period is inside or overlapping this audio
        if self._period[0] < self.get_duration():
            # current position in time.
            cur_time = self.tell()
            # Check if the current position is inside the period
            if self._period[0] <= cur_time <= self._period[1]:
                start_time = max(self._period[0], cur_time)
                end_time = min(self._period[1], self.get_duration())
                # Convert the time (in seconds) into a position in the frames
                start_pos = self._time_to_frames(start_time)
                end_pos = self._time_to_frames(end_time)
                return self._frames[start_pos:end_pos]

        return b("")

    # -----------------------------------------------------------------------

    def __threading_load(self, filename):
        """Really load the file that filename refers to.

        Send a media event when loading is finished.

        :param filename: (str)

        """
        self._ms = MediaState().loading
        value = sppasSimpleAudioPlayer.load(self, filename)
        if value is True:
            evt = MediaEvents.MediaLoadedEvent()
            if self._period is None:
                self._period = (0., self.get_duration())
        else:
            evt = MediaEvents.MediaNotLoadedEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        self._ms = MediaState().stopped

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="Audio Player")

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
        duration = self.ap.get_duration()
        self.slider.SetRange(0, int(duration * 1000.))

        # self.ap.set_period(10., 12.)
        # self.ap.seek(10.)
        # self.slider.SetRange(10000, 12000)

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
