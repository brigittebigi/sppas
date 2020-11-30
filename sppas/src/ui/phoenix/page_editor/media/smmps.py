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

    src.ui.phoenix.windows.media.smmps.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The SPPAS Multi Media Player System
    ===================================

    Requires simpleaudio library to play the audio file streams. Raise a
    FeatureException at init if 'audioplay' feature is not enabled.

    A player to play several media files really synchronously: during the
    tests, the maximum time lag I observed was less than 15ms when playing
    4 audios and 1 video.

    Limitations:
    =============

    The followings will raise a Runtime error:

        1. can't add a new media when playing or paused;
        2. can't play if at least a media is loading;
        3. can't set period if at least a media is paused or playing.

"""

import os
import wx
import threading

from sppas.src.config import paths
from sppas.src.ui.players import sppasMultiMediaPlayer
from sppas.src.ui.players import sppasSimpleVideoPlayerWX
from sppas.src.ui.players import sppasBasePlayer, PlayerType

from .mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class sppasUndPlayer(sppasBasePlayer):
    """A media player that simply store a filename and its duration.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        super(sppasUndPlayer, self).__init__()
        self._duration = 0.

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Store the filename.

        :param filename: (str) Name of a file
        :return: (bool) True

        """
        self._filename = filename
        self._mt = PlayerType().unsupported
        return True

    # -----------------------------------------------------------------------

    def get_duration(self):
        return self._duration

    # -----------------------------------------------------------------------

    def set_duration(self, value):
        """Set the duration of the file."""
        self._duration = value

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play.

        :return: (bool) False

        """
        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) False

        """
        return False

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the audio stream.

        :return: (bool) False

        """
        return False

# ---------------------------------------------------------------------------


class sppasMMPS(sppasMultiMediaPlayer, wx.Timer):
    """A media player using a timer to control time when playing.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is inheriting of a Timer in order to update the position
    in the audio stream and thus to implement the 'tell' method.
    This class is using threads to load the frames of the audio files.
    It is also managing a period in time instead of considering the whole
    duration (to seek, play, etc).

    Events emitted by this class:

        - wx.EVT_TIMER when the audio is playing every TIMER_DELAY seconds
        - MediaEvents.EVT_MEDIA_LOADED when the frames were loaded
        - MediaEvents.EVT_MEDIA_NOT_LOADED when an error occurred

    The wx.Timer documentation indicates that its precision is
    platform-dependent, but in general will not be better than 1ms
    nor worse than 1s... What I observed is that:

    1. When the timer delay is fixed to 10ms, the observed delays are:
       - about 15 ms under Windows;
       - between 10.5 and 11 ms under MacOS;
       - 10.1 ms under Linux.

    2. When the timer delay is fixed to 5ms, the observed delays are:
       - about 15 ms under Windows;
       - 6 ms under MacOS;
       - 5.5 ms under Linux.

    3. When the timer delay is fixed to 1ms, the observed delays are:
       - about 15 ms under Windows;
       - 2 ms under MacOS;
       - 1.3 ms under Linux.

    4. Under Windows, the timer delay is always a multiple of 15 - exactly
       like for the time.sleep() method. Under Linux&Mac, the delay is
       always slightly higher than requested.

    """

    # Delay in seconds to update the position value in the stream & to notify
    # A multiple of 15ms allows that all systems work more or less the same
    TIMER_DELAY = 0.015

    # -----------------------------------------------------------------------

    def __init__(self, owner):
        """Create an instance of sppasMMPS.

        :param owner: (wx.Window) Owner of this class.

        """
        wx.Timer.__init__(self, owner)
        sppasMultiMediaPlayer.__init__(self)

        # A time period to play the audio stream. Default is whole.
        self._period = (0., 0.)

    # -----------------------------------------------------------------------

    def __del__(self):
        if self.is_playing():
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
        if self.is_playing() or self.is_paused():
            raise RuntimeError("The period can't be changed while playing or paused.")

        start_time = float(start_time)
        end_time = float(end_time)
        if end_time <= start_time:
            raise ValueError("Invalid period of time: {:f} {:f}"
                             "".format(start_time, end_time))

        self._period = (start_time, end_time)
        self.seek(self._period[0])

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
                th = threading.Thread(target=self.__load_audio, args=(name,))
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

        :param filename: (str) A filename or a list of file names
        :param player: (wx.Window) a window or a list of wx windows
        :return: (bool)

        """
        if isinstance(filename, (list, tuple)) is True:
            # Invalidate the list of players if lengths don't match
            if isinstance(player, (list, tuple)):
                if len(player) != len(filename):
                    player = None

            # Create threads with a target function of loading
            new_th = list()
            for i, name in enumerate(filename):
                if isinstance(player, (list, tuple)):
                    dest_player = player[i]
                else:
                    dest_player = player

                th = threading.Thread(target=self.__load_video, args=(name, dest_player))
                new_th.append(th)
            # Start the new threads
            for th in new_th:
                th.start()
        else:
            self.__load_video(filename, player)

    # -----------------------------------------------------------------------

    def add_unsupported(self, filename, duration):
        """Add a file into the list of media in order to add only its duration.

        :param filename: (str)
        :param duration: (float) Time value in seconds.

        """
        if self.exists(filename) is False:
            fake_media = sppasUndPlayer()
            fake_media.load(filename)
            fake_media.set_duration(duration)
            self._medias[fake_media] = False

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
        if self.is_paused() is True:
            played = self.play_interval()
        else:
            if self.is_playing() is False:
                played = self.play_interval(self._period[0], self._period[1])

        if played is True:
            # wx.Timer Start method needs milliseconds, not seconds.
            self.Start(int(sppasMMPS.TIMER_DELAY * 1000.))

        return played

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause the medias that are currently playing."""
        # Stop the timer
        self.Stop()
        paused = sppasMultiMediaPlayer.pause(self)
        return paused

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
        """Return the latest time position in the media streams (float)."""
        if len(self._medias) > 0:
            values = list()
            for media in reversed(list(self._medias.keys())):
                if media.is_unknown() is False and media.is_unsupported() is False and media.is_loading() is False:
                    values.append(media.tell())

            # In theory, all media should return the same value except
            # when playing or paused after the max length of some media.
            return max(values)

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
            # Use this timer to seek the audios
            for media in self._medias:
                if media.is_playing() is True and media.is_audio() is True:
                    media.update_playing()
                    # the audio stream is currently playing
                    if media.is_playing() is True:
                        # seek the audio at the time of the player.
                        # and stop if the audio reached its end.
                        media.reposition_stream()

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
        self.ap = sppasMMPS(owner=self)

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
        # Example to add&enable a media:
        # >>> m = sppasSimpleVideoPlayerWX(owner=self)
        # >>> m.load(os.path.join(paths.samples, "faces", "video_sample.mp4"))
        # >>> if m.is_unknown() is False:
        # >>>     self.ap.add_media(m)
        # >>>     self.ap.enable(os.path.join(paths.samples, "faces", "video_sample.mp4"))

        self.ap.add_video(os.path.join(paths.samples, "faces", "video_sample.mp4"))
        self.ap.add_audio(
            [
                "toto.xyz",
                os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"),
                os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"),
                os.path.join(paths.samples, "samples-eng", "oriana1.wav"),
                os.path.join(paths.samples, "samples-eng", "oriana2.WAV")
            ]
        )
        self.ap.add_unsupported("a filename of a file", 65.)

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        filename = event.filename
        self.ap.enable(filename)
        wx.LogDebug("File loaded successfully: {}. Duration: {}".format(filename, self.ap.get_duration(filename)))
        self.FindWindow("btn_play").Enable(True)
        duration = self.ap.get_duration()
        self.slider.SetRange(0, int(duration * 1000.))

        # the following line enters in an infinite loop with the message:
        # In file /Users/robind/projects/bb2/dist-osx-py38/build/ext/wxWidgets/src/unix/threadpsx.cpp at line 370: 'pthread_mutex_[timed]lock()' failed with error 0x00000023 (Resource temporarily unavailable).
        # self.ap.set_period(0., duration)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        filename = event.filename
        wx.LogError("Media file {} not loaded".format(filename))

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        wx.LogDebug("................PLAY EVENT RECEIVED..................")
        if self.ap.is_playing() is False:
            if self.ap.is_paused() is False:
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
