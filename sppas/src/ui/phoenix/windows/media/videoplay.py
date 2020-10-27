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
    This class is using a thread to load the frames of the audio file
    and to play.

    Events emitted by this class:

        - wx.EVT_TIMER when the video is playing, every 1/fps seconds
        - MediaEvents.EVT_MEDIA_LOADED when the frames were loaded
        - MediaEvents.EVT_MEDIA_NOT_LOADED when an error occurred

    """

    # Delay in seconds to refresh the displayed video frame & to notify
    TIMER_DELAY = 0.020

    def __init__(self, owner):
        """Create an instance of sppasVideoPlayer.

        :param owner: (wx.Window) Owner of this class.

        """
        wx.Timer.__init__(self, owner)
        sppasSimpleVideoPlayer.__init__(self)

        # The frame in which images of the video are sent
        self._img_frame = sppasImageFrame(
            parent=owner,   # if owner is destroyed, the frame will be too
            title="Video",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT)
        self._img_frame.SetBackgroundColour(wx.WHITE)

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
        try:
            self._period = None
            if self.__th is not None:
                if self.__th.is_alive():
                    # Python does not implement a "stop()" method for threads
                    del self.__th
                    self.__th = None
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
        self._img_frame.SetTitle(filename)
        # Create a Thread with a function with args
        self.__th = threading.Thread(target=self.__threading_load, args=(filename,))
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
                self._img_frame.Show()
                from_time, to_time = self.__get_from_to()
                if from_time is not None:

                    # Create a Thread with a function to play video in a toplevelwindow
                    self.__th = threading.Thread(target=self.__threading_play, args=(from_time, to_time))
                    self.__th.start()
                    played = True
                    self.Start(int(sppasVideoPlayer.TIMER_DELAY * 1000.))

                else:
                    # we are currently outside of the defined period
                    played = False

            elif self._ms == ms.paused:
                self._ms = MediaState().playing
                played = True

        return played

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        if self._ms == MediaState().playing:
            self._ms = MediaState().paused

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the video.

        :return: (bool) True if the action of stopping was performed

        """
        self._img_frame.Hide()
        if self._ms not in (MediaState().loading, MediaState().unknown):
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
        if time_pos > self.duration():
            time_pos = self.duration()
        if time_pos > self._period[1]:
            time_pos = self._period[1]
        if time_pos < self._period[0]:
            time_pos = self._period[0]

        return sppasSimpleVideoPlayer.seek(self, time_pos)

    # -----------------------------------------------------------------------

    def __threading_play(self, from_time, to_time):
        """Run the process of playing.

        It is expected that reading a frame, converting it to an image and
        displaying it in the video frame is faster than the duration of a
        frame (1. / fps).
        If it's not the case, we should, sometimes, ignore a frame... not implemented!

        """
        self.seek(from_time)
        time_value = datetime.datetime.now()
        time_delay = round(1. / self._video.get_framerate(), 3)

        # the time when we started to play and the number of frames we displayed.
        start_time_value = datetime.datetime.now()
        print("Start time value={}".format(start_time_value))
        frm = 0

        while self._video.is_opened():
            # stop the loop.
            # Either the stop() method was invoked or the reset() one.
            if self._ms in (MediaState().stopped, MediaState().unknown):
                break

            elif self._ms == MediaState().playing:
                # read the next frame from the file
                frame = self._video.read_frame(process_image=False)
                if frame is not None:
                    self._img_frame.SetBackgroundImageArray(frame.irgb())
                    # no effect under MacOS: self._img_frame.Refresh()

                    cur_time_in_video = self.tell()
                    if cur_time_in_video > to_time:
                        self.stop()
                    else:
                        frm += 1

                        expected_time = start_time_value + datetime.timedelta(seconds=((frm+1) * time_delay))
                        # print(" - read {} frames. expected_time={}".format(frm, expected_time))

                        cur_time = datetime.datetime.now()
                        # print(" - observed time = {}".format(cur_time))

                        if cur_time < expected_time:
                            # I'm reading too fast. I've to wait.
                            # Sleep as many time as required to get the appropriate read speed
                            delta = cur_time - time_value
                            delta_seconds = delta.seconds + delta.microseconds / 1000000.
                            waiting_time = round((time_delay - delta_seconds), 4)
                            if waiting_time > 0.005:
                                time.sleep(waiting_time)
                                # print("    ---> slept for {} seconds".format(waiting_time))
                        else:
                            pass
                            # I'm reading too slow, I'm in late.
                            #self._video.seek(self._video.tell()+2)
                            #frm += 1
                            #logging.warning("Ignored frame at time {}".format(cur_time_in_video))
                            # print("$$$$$$$$$$$$$$$$$$$$ I'm in late $$$$$$$$$$$$$$$$$$$$$$$$")

                else:
                    # we reached the end of the file
                    self.stop()

                time_value = datetime.datetime.now()

            elif self._ms == MediaState().paused:
                time.sleep(time_delay/4.)
                time_value = datetime.datetime.now()
                start_time_value = datetime.datetime.now()
                frm = 0

        end_time_value = datetime.datetime.now()
        print("Video duration: {}".format(self.duration()))
        print("Reading time: ")
        print(" - Play started at: {}".format(start_time_value))
        print(" - Play finished at: {}".format(end_time_value))
        print(" -> diff = {}".format((end_time_value-start_time_value).total_seconds()))

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def Notify(self):
        """Override. Notify the owner of the EVT_TIMER event.

        Manage the current position in the audio stream.

        """
        # Nothing to do if we are not playing (probably paused).
        if self._ms == MediaState().playing:
            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)
            # Refresh the video frame
            # Under MacOS, refreshing the frame inside the threading_play
            # instead of here does not have any effect... so we do it here
            # because it works... why?!
            self._img_frame.Refresh()
            print(" Refresh at {}".format(datetime.datetime.now()))

    # -----------------------------------------------------------------------
    # Private&Protected
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

    # -----------------------------------------------------------------------

    def __get_from_to(self):
        """Return the (start, end) time values to play.

        """
        # Check if the current period is inside or overlapping this audio
        if self._period[0] < self.duration():
            # current position in time.
            cur_time = self.tell()
            # Check if the current position is inside the period
            if self._period[0] <= cur_time <= self._period[1]:
                start_time = max(self._period[0], cur_time)
                end_time = min(self._period[1], self.duration())
                return start_time, end_time
                # Convert the time (in seconds) into a position in the frames
                # start_pos = start_time * self._video.get_framerate()
                # end_pos = end_time * self._video.get_framerate()
                # return int(start_pos), int(end_pos)

        return None, None

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
