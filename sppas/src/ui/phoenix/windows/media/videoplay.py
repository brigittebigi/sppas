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

    src.ui.phoenix.windows.media.videoplay.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires opencv library to play the video file stream. Raise a
    FeatureException at init if 'video' feature is not enabled.

"""

import logging
import os
import wx
import threading
import cv2
import datetime
import time

from sppas.src.config import paths
from sppas.src.config import MediaState

from sppas.src.videodata import sppasSimpleVideoPlayer

from ..frame import sppasImageFrame

from .mediaevents import MediaEvents

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
    This class is using a thread to load the frames of the audio file.

    Events emitted by this class:

        - wx.EVT_TIMER when the audio is playing
        - MediaEvents.EVT_MEDIA_LOADED when the frames were loaded
        - MediaEvents.EVT_MEDIA_NOT_LOADED when an error occurred

    """

    # Delay in seconds to update the position value in the stream.
    TIMER_DELAY = 0.04

    # -----------------------------------------------------------------------

    def __init__(self, owner):
        """Create an instance of sppasVideoPlayer.

        :param owner: (wx.Window) Owner of this class.

        """
        wx.Timer.__init__(self, owner)
        sppasSimpleVideoPlayer.__init__(self)

        # A thread to load or play the frames of the video
        self.__th = None

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
        if self.__th is not None:
            if self.__th.is_alive():
                # Python does not implement a "stop()" method for threads
                del self.__th
                self.__th = None
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

    def is_unknown(self):
        """Return True if the media is unknown."""
        if self._filename is None:
            return False

        return self._ms == MediaState().unknown

    # -----------------------------------------------------------------------

    def is_loading(self):
        """Return True if the media is still loading."""
        if self._filename is None:
            return False

        return self._ms == MediaState().loading

    # -----------------------------------------------------------------------

    def is_playing(self):
        """Return True if the media is playing."""
        if self._filename is None:
            return False

        return self._ms == MediaState().playing

    # -----------------------------------------------------------------------

    def is_paused(self):
        """Return True if the media is paused."""
        if self._filename is None:
            return False

        return self._ms == MediaState().paused

    # -----------------------------------------------------------------------

    def is_stopped(self):
        """Return True if the media is stopped."""
        if self._filename is None:
            return False

        return self._ms == MediaState().stopped

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        if self._ms == MediaState().playing:
            self._ms = MediaState().paused

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the video stream from the current position.

        Start playing only is the video stream is currently stopped or
        paused.

        :return: (bool) True if the action of playing was performed

        """
        if self._filename is None:
            logging.error("No media file to play.")
            return False

        played = False
        with MediaState() as ms:
            if self._ms == ms.unknown:
                logging.error("The video stream of {:s} can't be played for "
                              "an unknown reason.".format(self._filename))

            elif self._ms == ms.loading:
                logging.error("The video stream of {:s} can't be played: "
                              "still loading".format(self._filename))

            elif self._ms == ms.playing:
                logging.warning("The video stream of {:s} is already "
                                "playing.".format(self._filename))

            elif self._ms == ms.stopped:
                self._ms = MediaState().playing
                # Create a Thread with a function without args
                self.__th = threading.Thread(target=self._play,
                                             args=())
                # Start the thread
                self.__th.start()
                played = True

            elif self._ms == ms.paused:
                self._ms = MediaState().playing
                played = True

        return played

    # -----------------------------------------------------------------------

    def _play(self):
        """Run the process of playing."""
        cv2.namedWindow("window", cv2.WINDOW_NORMAL)
        time_value = datetime.datetime.now()
        time_delay = round(1. / self._video.get_framerate(), 3)

        while self._video.is_opened():
            # stop the loop.
            # Either the stop() method was invoked or the reset() one.
            if self._ms in (MediaState().stopped, MediaState().unknown):
                break

            elif self._ms == MediaState().playing:
                # read the next frame from the file
                frame = self._video.read_frame(process_image=False)
                if frame is not None:
                    cv2.imshow('window', frame)
                    # Sleep as many time as required to get the appropriate read speed
                    cur_time = datetime.datetime.now()
                    delta = cur_time - time_value
                    delta_seconds = delta.seconds + delta.microseconds / 1000000.
                    waiting_time = round(time_delay - delta_seconds, 3)
                    if waiting_time > 0:
                        time.sleep(waiting_time)
                    time_value = datetime.datetime.now()
                else:
                    # we reached the end of the file
                    self.stop()

            elif self._ms == MediaState().paused:
                time.sleep(time_delay/4.)
                time_value = datetime.datetime.now()

            if cv2.waitKey(1) & 0xFF == 27:
                self.stop()

        cv2.destroyWindow("window")

    # -----------------------------------------------------------------------

    def __threading_load(self, filename):
        """Really load the file that filename refers to.

        Send a media event when loading is finished.

        :param filename: (str)

        """
        self._ms = MediaState().loading
        value = sppasSimpleVideoPlayer.load(self, filename)
        if value is True:
            evt = MediaEvents.MediaLoadedEvent()
            if self._period is None:
                self._period = (0., self.duration())
        else:
            evt = MediaEvents.MediaNotLoadedEvent()
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        self._ms = MediaState().stopped

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
        self.ap.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        self.ap.load(os.path.join(paths.samples, "faces", "video_sample.mp4"))

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        wx.LogDebug("Audio file loaded successfully")
        self.FindWindow("btn_play").Enable(True)
        duration = self.ap.duration()
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
