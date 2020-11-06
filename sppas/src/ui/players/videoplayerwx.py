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

    src.ui.players.wxvideoplay.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A player to play a single video file inside a wx frame.
    A wx.App() must be created first!

"""

import os
import datetime
import threading
import wx

from sppas.src.config import paths
from sppas.src.ui.phoenix.windows.frame import sppasImageFrame

from .pstate import PlayerState
from .videoplayer import sppasSimpleVideoPlayer

# ---------------------------------------------------------------------------


class sppasSimpleVideoPlayerWX(sppasSimpleVideoPlayer, wx.Timer):
    """A video player based on both cv2 library and wx.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

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

        # The delay to set the player bg image while playing
        self._timer_delay = 40  # in milliseconds

    # -----------------------------------------------------------------------

    def play(self):
        """Override. Start to play the video stream, start the timer.

        :return: (bool) True if the action of playing was performed

        """
        if self._ms in (PlayerState().paused, PlayerState().stopped):
            th = threading.Thread(target=self._play_process, args=())
            self._ms = PlayerState().playing
            self._player.Show(True)
            self._start_datenow = datetime.datetime.now()
            self.Start(self._timer_delay)
            th.start()
            return True

        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Override. Pause to play the video, stop the timer.

        :return: (bool) True if the action of stopping was performed

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
        """Override. Stop to play the video, stop the timer.

        :return: (bool) True if the action of stopping was performed

        """
        if self._player.IsShown():
            self._player.Hide()
            self._ms = PlayerState().stopped
            self._media.seek(0)
            self.Stop()
            return True
        return False

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def Notify(self):
        """Override. Notify the owner of the EVT_TIMER event.

        Manage the current position in the audio stream.

        """
        # Nothing to do if we are not playing
        if self._ms == PlayerState().playing:
            if self._current_image is not None:
                # Refresh the video frame
                self._player.SetBackgroundImageArray(self._current_image)
                self._player.Refresh()

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="Simple VideoPlayer WX")

        # The player!
        self.ap = sppasSimpleVideoPlayerWX(owner=self)

        # Actions to perform with the player
        btn2 = wx.Button(self, -1, "Play", name="btn_play")
        self.Bind(wx.EVT_BUTTON, self._on_play_ap, btn2)
        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self._on_pause_ap, btn3)
        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self._on_stop_ap, btn4)
        sizer = wx.BoxSizer()
        sizer.Add(btn2, 0, wx.ALL, 4)
        sizer.Add(btn3, 0, wx.ALL, 4)
        sizer.Add(btn4, 0, wx.ALL, 4)

        self.SetSizer(sizer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        self.ap.load(os.path.join(paths.samples, "faces", "video_sample.mp4"))

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        if self.ap.is_paused() is False:
            self.ap.prepare_play(0., self.ap.get_duration())
        self.ap.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        self.ap.pause()

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        self.ap.stop()
