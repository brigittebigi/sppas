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

    src.ui.phoenix.windows.media.wxvideoplay.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    src.ui.players.wxvideoplay.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A player to play a single video file with tell and pause implemented and
    events.

"""

import logging
import os
import wx
import threading
import datetime
import time

from sppas.src.config import paths

from src.ui.phoenix.windows.frame import sppasImageFrame
from src.ui.phoenix.windows.media.mediaevents import MediaEvents

from .videoplayer import sppasSimpleVideoPlayer
from .pstate import PlayerState

# ---------------------------------------------------------------------------


class sppasVideoPlayer(sppasSimpleVideoPlayer, wx.Timer):
    """A video player based on opencv library and a timer.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This class is inheriting of a Timer in order to send events when
    loading and progressing.
    This class is using a thread to load the frames of the audio file
    and to play.

    Events emitted by this class:

        - wx.EVT_TIMER when the video is playing, every 1/fps seconds
        - MediaEvents.EVT_MEDIA_LOADED when the frames were loaded
        - MediaEvents.EVT_MEDIA_NOT_LOADED when an error occurred

    Notice that it's not doable to use the wx.Timer event to display the
    frames: the real timer delay is randomly close to the expected one...

    """

    # Delay in seconds to refresh the displayed video frame & to notify
    TIMER_DELAY = 0.040

    def __init__(self, owner):
        """Create an instance of sppasVideoPlayer.

        :param owner: (wx.Window) Owner of this class.

        """
        wx.Timer.__init__(self, owner)
        sppasSimpleVideoPlayer.__init__(self)

        # The frame in which images of the video are sent
        self._player = sppasImageFrame(
            parent=owner,   # if owner is destroyed, the frame will be too
            title="Video",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT)
        self._player.SetBackgroundColour(wx.WHITE)

        # A time period to play the video stream. Default is whole.
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
            # The audio was not created if the init raised a FeatureException
            sppasSimpleVideoPlayer.reset(self)
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
        cur_state = self._ms
        cur_pos = self.tell()
        # Stop playing (if any), and seek at the beginning of the period
        self.stop()

        # Restore the situation in which the audio was before stopping
        if cur_state in (PlayerState().playing, PlayerState().paused):
            if self._period[0] < cur_pos <= self._period[1]:
                # Restore the previous position in time if it was inside
                # the new period.
                self.seek(cur_pos)
            # Play again, then pause if it was the previous state.
            self.play()
            if cur_state == PlayerState().paused:
                self.pause()

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Override. Load the file that filename refers to.

        :param filename: (str)
        :return: (bool) Always returns False

        """
        value = sppasSimpleVideoPlayer.load(self, filename)
        if value is True:
            evt = MediaEvents.MediaLoadedEvent()
            if self._period is None:
                self._period = (0., self.get_duration())
        else:
            evt = MediaEvents.MediaNotLoadedEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        self._ms = PlayerState().stopped

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the video stream from the current position.

        Start playing only is the video stream is currently stopped or
        paused.

        :return: (bool) True if the action of playing was performed

        """
        played = False
        # current position in time.
        cur_time = self.tell()

        # Check if the current position is inside the period
        # if self._period[0] <= cur_time <= self._period[1]:
        start_time = max(self._period[0], cur_time)
        end_time = min(self._period[1], self.get_duration())

        if start_time < end_time:
            if self.prepare_play(start_time, end_time) is True:
                th = threading.Thread(target=self._play_process, args=())
                self._ms = PlayerState().playing
                self.Start(int(sppasVideoPlayer.TIMER_DELAY * 1000.))
                th.start()

        return played

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) True if the action of pausing was performed

        """
        if self._ms == PlayerState().playing:
            # stop playing
            self.Stop()
            self._ms = PlayerState().stopped
            # seek at the exact moment we stopped to play
            self._from_time = self.tell()
            # set our state
            self._ms = PlayerState().paused
            return True

        return False

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        if self._player.IsShown():
            self._player.Hide()
            # self._player.stop()
            self._ms = PlayerState().stopped
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

        return sppasSimpleVideoPlayer.seek(self, time_pos)

    # -----------------------------------------------------------------------

    def _play_process(self):
        """Run the process of playing.

        It is expected that reading a frame, converting it to an image and
        displaying it in the video frame is faster than the duration of a
        frame (1. / fps).
        If it's not the case, we should, sometimes, ignore a frame: not tested!

        """
        self._player.Show()
        # self.seek(self._period[0])
        time_delay = round(1. / self._media.get_framerate(), 3)
        min_sleep = time_delay / 4.

        # the position to start and to stop playing
        start_offset = self._media.tell()
        end_offset = int(self._period[1] * float(self._media.get_framerate()))

        # the time when we started to play and the number of frames we displayed.
        frm = 0
        self._start_datenow = datetime.datetime.now()

        while self._media.is_opened():
            if self._ms == PlayerState().playing:
                # read the next frame from the file
                frame = self._media.read_frame(process_image=False)
                frm += 1
                cur_offset = start_offset + frm

                if frame is None or cur_offset > end_offset:
                    # we reached the end of the file or the end of the period
                    self.stop()
                else:
                    self._player.SetBackgroundImageArray(frame.irgb())

                    expected_time = self._start_datenow + datetime.timedelta(seconds=(frm * time_delay))
                    cur_time = datetime.datetime.now()
                    delta = expected_time - cur_time
                    delta_seconds = delta.seconds + delta.microseconds / 1000000.
                    if delta_seconds > min_sleep:
                        # I'm reading too fast, wait a little time.
                        time.sleep(delta_seconds)

                    elif delta_seconds > time_delay:
                        # I'm reading too slow, I'm in late.
                        self._media.seek(self._media.tell()+1)
                        frm += 1
                        logging.warning("Ignored frame at {:f} seconds"
                                        "".format(float(cur_offset)*self._media.get_framerate()))

            else:
                # stop the loop at any other state than playing
                break

        if start_offset == 0:
            end_time_value = datetime.datetime.now()
            wx.LogDebug("Video duration: {}".format(self.get_duration()))
            wx.LogDebug(" - Play started at: {}".format(self._start_datenow))
            wx.LogDebug(" - Play finished at: {}".format(end_time_value))
            wx.LogDebug(" -> diff = {}".format((end_time_value-self._start_datenow).total_seconds()))
        self._start_datenow = None

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def Notify(self):
        """Override. Notify the owner of the EVT_TIMER event.

        Manage the current position in the audio stream.

        """
        # Nothing to do if we are not playing (probably paused).
        if self._ms == PlayerState().playing:
            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)
            # Refresh the video frame
            # Under MacOS, refreshing the frame inside the threading_play
            # instead of here does not have any effect... so we do it here
            # because it works... why?!
            self._player.Refresh()

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="VideoPlayer")

        # The player!
        self.ap = sppasVideoPlayer(owner=self)

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
        self.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        self.ap.load(os.path.join(paths.samples, "faces", "video_sample.mp4"))

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        wx.LogDebug("Video file loaded successfully")
        self.FindWindow("btn_play").Enable(True)
        duration = self.ap.get_duration()
        self.slider.SetRange(0, int(duration * 1000.))

        # self.ap.set_period(10., 12.)
        # self.ap.seek(10.)
        # self.slider.SetRange(10000, 12000)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        wx.LogError("Video file not loaded")
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
