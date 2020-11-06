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

    src.ui.phoenix.windows.media.audiomplay.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires simpleaudio library to play the audio file streams. Raise a
    FeatureException at init if 'audioplay' feature is not enabled.

    A player to play several audio files synchronously.

"""

import os
import wx
import threading

from sppas.src.config import paths
# from sppas.src.ui.players import sppasMultiMediaPlayer
from sppas.src.ui.players import sppasMultiMediaPlayer
from sppas.src.ui.players import sppasSimpleAudioPlayer
from sppas.src.ui.players import sppasSimpleVideoPlayer
from sppas.src.ui.players import sppasSimpleVideoPlayerWX

from .mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class sppasAudioPlayer(sppasMultiMediaPlayer, wx.Timer):
    """An audio player based on simpleaudio library and a timer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is inheriting of a Timer in order to update the position
    in the stream and thus to implement the 'tell' method.
    This class is using threads to load the frames of the audio files.
    It is also managing a period in time instead of considering the whole
    duration (to seek, play, etc).

    Events emitted by this class:

        - wx.EVT_TIMER when the audio is playing every TIMER_DELAY seconds
        - MediaEvents.EVT_MEDIA_LOADED when the frames were loaded
        - MediaEvents.EVT_MEDIA_NOT_LOADED when an error occurred

    The wx.Timer documentation indicates that its precision is
    platform-dependent, but in general will not be better than 1ms
    nor worse than 1s...

    When the timer delay is fixed to 10ms, the observed delays are:
       - about 15 ms under Windows;
       - 10-11 ms under MacOS;
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
    TIMER_DELAY = 0.015

    # -----------------------------------------------------------------------

    def __init__(self, owner):
        """Create an instance of sppasAudioPlayer.

        :param owner: (wx.Window) Owner of this class.

        """
        wx.Timer.__init__(self, owner)
        sppasMultiMediaPlayer.__init__(self)

        # A time period to play the audio stream. Default is whole.
        self._period = (0., 0.)

    # -----------------------------------------------------------------------

    def __del__(self):
        self.reset()

    # -----------------------------------------------------------------------

    def reset(self):
        """Override. Re-initialize all known data and stop the timer."""
        self.Stop()
        self._period = (0., 0.)
        try:
            # The audio was not created if the init raised a FeatureException
            sppasMultiMediaPlayer.reset(self)
        except:
            pass

    # -----------------------------------------------------------------------

    def get_period(self):
        """Return the currently defined period (start, end)."""
        p0, p1 = self._period
        return p0, p1

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
        cur_playing = self.is_playing()
        cur_paused = self.is_paused()
        cur_pos = self.tell()
        # Stop playing (if any), and seek at the beginning of the period
        self.stop()

        # Restore the situation in which the audio was before stopping
        if cur_playing is True or cur_paused is True:
            if self._period[0] < cur_pos <= self._period[1]:
                # Restore the previous position in time if it was inside
                # the new period.
                self.seek(cur_pos)
            # Play again, then pause if it was the previous state.
            self.play()
            if cur_paused is True:
                self.pause()

    # -----------------------------------------------------------------------

    def add_audio(self, filename):
        """Override. Load the files that filenames refers to.

        The event MediaLoaded or MediaNotLoaded is sent when the audio
        finished to load. Loaded successfully or not, the audio is disabled.

        :param filename: (str) Name of a file or list of file names
        :return: (bool) Always returns False

        """
        if isinstance(filename, (list, tuple)) is True:
            # Create threads with a target function of loading with name as args
            new_th = list()
            for name in filename:
                th = threading.Thread(target=self.__load, args=(name,))
                new_th.append(th)
            # Start the new threads
            for th in new_th:
                th.start()
        else:
            self.__load_audio(filename)

    # -----------------------------------------------------------------------

    def add_video(self, filename, player=None):
        """Add a video into the list of media managed by this control.

        The new video is disabled.

        :param filename: (str)
        :return: (bool)

        """
        if isinstance(filename, (list, tuple)) is True:
            # Create threads with a target function of loading with name as args
            new_th = list()
            for name in filename:
                th = threading.Thread(target=self.__load_video, args=(name, player))
                new_th.append(th)
            # Start the new threads
            for th in new_th:
                th.start()
        else:
            self.__load_video(filename, player)

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the audio streams.

        Start playing only if the audio streams are currently stopped or
        paused. Play in the range of the defined period.

        So, it starts playing an audio only if the defined period is inside
        or overlapping the audio stream AND if the the current position is
        inside the period. It stops at the end of the period or at the end
        of the stream.

        :return: (bool) True if the action of playing was started

        """
        played = False
        # current position in time.
        cur_time = self.tell()

        start_time = max(self._period[0], cur_time)
        end_time = min(self._period[1], self.get_duration())
        if start_time < end_time:

            played = self.play_interval(start_time, end_time)
            if played is True:
                # wx.Timer Start method needs milliseconds, not seconds.
                self.Start(int(sppasAudioPlayer.TIMER_DELAY * 1000.))

        return played

    # -----------------------------------------------------------------------

    def stop(self):
        """Override. Stop to play the audios.

        :return: (bool) True if the action of stopping was performed

        """
        self.Stop()
        self.DeletePendingEvents()
        stopped = sppasMultiMediaPlayer.stop(self)
        self.seek(self._period[0])
        return stopped

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

        return sppasMultiMediaPlayer.seek(self, time_pos)

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the audio stream (float)."""
        if len(self._medias) > 0:
            values = list()
            for media in self._medias:
                if media.is_unknown() is False and media.is_loading() is False:

                    # In theory, all media should return the same value...
                    if isinstance(media, sppasSimpleVideoPlayer):
                        time_value = media.tell()
                        values.append(time_value)

                    elif isinstance(media, sppasSimpleAudioPlayer):
                        offset = media.media_tell()
                        time_value = float(offset * media.get_nchannels()) / float(media.get_framerate())
                        values.append(time_value)
            # return the earlier time
            return min(values)

        return 0

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def Notify(self):
        """Override. Notify the owner of the EVT_TIMER event.

        Manage the current position in the audio stream.

        """
        # Nothing to do if we are not playing (probably paused).
        if self.is_playing():
            for media in self._medias:
                if isinstance(media, sppasSimpleAudioPlayer) is True:
                    media.update_playing()

                    # the audio stream is currently playing
                    if media.is_playing() is True:
                        # seek the audio at the time of the player.
                        # and stop if the audio reached its end.
                        media._reposition()

            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)

        elif self.is_paused() is False:
            self.stop()

    # -----------------------------------------------------------------------
    # Private & Protected methods
    # -----------------------------------------------------------------------

    def __load_audio(self, filename):
        """Really load and add the file that filename refers to.

        Send a media event when a loading is finished.

        :param filename: (str)

        """
        value = sppasMultiMediaPlayer.add_audio(self, filename)
        if value is True:
            evt = MediaEvents.MediaLoadedEvent(filename=filename)
        else:
            evt = MediaEvents.MediaNotLoadedEvent(filename=filename)
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        return value

    # -----------------------------------------------------------------------

    def __load_video(self, filename, player):
        """Really load and add the file that filename refers to.

        Send a media event when a loading is finished.

        :param filename: (str)

        """
        loaded = False
        if self.exists(filename) is False:
            new_video = sppasSimpleVideoPlayerWX(owner=self.GetOwner(), player=player)
            self._medias[new_video] = False
            loaded = new_video.load(filename)

        if loaded is True:
            evt = MediaEvents.MediaLoadedEvent(filename=filename)
        else:
            evt = MediaEvents.MediaNotLoadedEvent(filename=filename)
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        return loaded

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="Multi Audio Player")

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
        # Event received every 15ms (in theory) when the audio is playing
        self.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        m = sppasSimpleVideoPlayerWX(owner=self)
        m.load(os.path.join(paths.samples, "faces", "video_sample.mp4"))
        self.ap.add_media(m)
        print(len(self.ap))
        self.ap.enable(os.path.join(paths.samples, "faces", "video_sample.mp4"))
        print(self.ap.get_duration())

        self.ap.add_audio(
            [os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"),
             os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"),
             os.path.join(paths.samples, "samples-eng", "oriana1.wav"),
             os.path.join(paths.samples, "samples-eng", "oriana2.WAV"),
             'toto.xxx']
        )

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        filename = event.filename
        self.ap.enable(filename)
        wx.LogDebug("File loaded successfully: {}".format(filename))
        self.FindWindow("btn_play").Enable(True)
        duration = self.ap.get_duration()
        self.slider.SetRange(0, int(duration * 1000.))
        # the following line enters in an infinite loop with the message:
        # In file /Users/robind/projects/bb2/dist-osx-py38/build/ext/wxWidgets/src/unix/threadpsx.cpp at line 370: 'pthread_mutex_[timed]lock()' failed with error 0x00000023 (Resource temporarily unavailable).
        # self.ap.set_period(0., duration)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        filename = event.filename
        wx.LogError("Audio file {} not loaded".format(filename))

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        wx.LogDebug("................PLAY EVENT RECEIVED..................")
        duration = self.ap.get_duration()
        self.ap.set_period(0., duration)
        self.ap.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        wx.LogDebug("................PAUSE EVENT RECEIVED..................")
        self.ap.pause()

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        wx.LogDebug("................STOP EVENT RECEIVED..................")
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
