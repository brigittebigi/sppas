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

    src.ui.phoenix.windows.media.multiplayer.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.media

from sppas.src.config import paths
from sppas.src.exc import IntervalRangeException

from ..panel import sppasPanel
from ..button import BitmapTextButton
from .mediactrl import sppasMediaCtrl
from .mediactrl import MediaType
from .playerctrl import sppasPlayerControlsPanel
from .mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class sppasMultiPlayerPanel(sppasPlayerControlsPanel):
    """Create a panel with controls and manage a list of media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    A player controls panel to play several media at a time.
    It is supposed that all the given media are already loaded.

    """

    def __init__(self, parent, id=-1,
                 media=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="multi_player_panel"):
        """Create a sppasMultiPlayerPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param media: (list) List of wx.media.MediaCtrl
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        """
        super(sppasMultiPlayerPanel, self).__init__(
            parent, id, pos, size, style, name)

        if media is None:
            media = list()
        self.__media = media
        self._length = 0
        self._autoreplay = True
        self._timer = wx.Timer(self)
        self._refreshtimer = 10
        self.Bind(wx.EVT_TIMER, self.OnTimer)

    # -----------------------------------------------------------------------
    # Manage offset and period
    # -----------------------------------------------------------------------

    def get_start_pos(self):
        return self.GetSlider().GetRange()[0]

    # -----------------------------------------------------------------------

    def get_end_pos(self):
        return self.GetSlider().GetRange()[1]

    # -----------------------------------------------------------------------

    def get_pos(self):
        return self.GetSlider().GetValue()

    # -----------------------------------------------------------------------

    def set_range(self, start=None, end=None):
        """Fix period to be played (milliseconds).

        :param start: (int) Start time. Default is 0.
        :param end: (int) End time. Default is length.

        """
        if start is None:
            start = 0
        if end is None:
            end = self._length

        assert int(start) <= int(end)
        if start < 0:
            start = 0
        if end > self._length:
            end = self._length
        self.GetSlider().SetRange(start, end)
        if self.pos < start or self.pos > end:
            self.set_pos(start)

    # -----------------------------------------------------------------------

    def set_pos(self, offset):
        assert int(offset) >= 0
        if offset < self.start_pos or offset > self.end_pos:
            raise IntervalRangeException(offset, self.start_pos, self.end_pos)
        self.GetSlider().SetValue(offset)

    # -----------------------------------------------------------------------

    start_pos = property(get_start_pos, None)
    end_pos = property(get_end_pos, None)
    pos = property(get_pos, set_pos)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def get_autoreplay(self):
        transport_panel = self.FindWindow("transport_panel")
        return transport_panel.FindWindow("media_repeat").IsPressed()

    autoreplay = property(get_autoreplay, None)

    # -----------------------------------------------------------------------

    def set_media(self, media_lst):
        """Set a new list of media.

        It is supposed that all media are already loaded.
        If a media type is unsupported or unknown, the media is not added.

        :param media_lst: (list)

        """
        self.__reset()
        self.__media = list()

        for m in media_lst:
            self.__append_media(m)

        if len(self.__media) > 0:
            # re-evaluate length
            self._length = max(m.Length() for m in self.__media)
            # fix the largest range
            self.set_range()

            # seek at the beginning of the period
            self.media_seek(self.start_pos)

    # -----------------------------------------------------------------------

    def __append_media(self, m):
        mt = m.GetMediaType()
        if mt == MediaType().unknown:
            wx.LogError("Media {:s} is not added to the player: unknown format."
                        "".format(m.GetFilename()))

        elif mt == MediaType().unsupported:
            wx.LogError("Media {:s} is not added to the player: unsupported format."
                        "".format(m.GetFilename()))

        else:
            ml = m.Length()
            if ml == -1:
                wx.LogError("Media {:s} is not added to the player: load not completed."
                            "".format(m.GetFilename()))
            else:
                wx.LogDebug("Media {:s} is added to the player."
                            "".format(m.GetFilename()))
                self.__media.append(m)
                return True

        return False

    # -----------------------------------------------------------------------

    def add_media(self, media):
        """Add a media into the list of media managed by this control.

        Set also the range if media is the first media in the list.

        :param media:

        """
        if media in self.__media:
            return False
        ok = self.__append_media(media)
        if ok is True:
            # re-evaluate length
            self._length = max(m.Length() for m in self.__media)
            if len(self.__media) == 1 and self.end_pos == 0:
                self.set_range()

            self.__validate_offsets()
            # seek the new media to the current position.
            media.Seek(self.GetSlider().GetValue())
        return ok

    # -----------------------------------------------------------------------

    def remove_media(self, media):
        """Remove a media of the list of media managed by this control.

        :param media:

        """
        if media not in self.__media:
            return False
        media.Stop()
        self.__media.remove(media)

        # re-evaluate length
        if len(self.__media) > 0:
            self._length = max(m.Length() for m in self.__media)
        else:
            self.__reset()

    # -----------------------------------------------------------------------

    def media_playing(self):
        """Return the first media we found playing, None instead."""
        for m in self.__media:
            if m.GetState() == wx.media.MEDIASTATE_PLAYING:
                return m
        return None

    # -----------------------------------------------------------------------

    def media_paused(self):
        """Return the first media we found playing, None instead."""
        for m in self.__media:
            if m.GetState() == wx.media.MEDIASTATE_PAUSED:
                return m
        return None

    # -----------------------------------------------------------------------

    def media_stopped(self):
        """Return the first media we found playing, None instead."""
        for m in self.__media:
            if m.GetState() == wx.media.MEDIASTATE_STOPPED:
                return m
        return None

    # -----------------------------------------------------------------------

    def media_tell(self):
        """Return the actual position in time in a media.

        In theory, all media should return the same value... And in theory
        it should be equal to the cursor value. Actually this is not True.
        Observed differences on MacOS are about 11-24 ms between each media.

        """
        if len(self.__media) > 0:
            values = [m.Tell() for m in self.__media]
            wx.LogDebug("  --> TELL VALUES ARE {:s}".format(str(values)))
            return min(values)

        # No audio nor video in the list of media
        return 0

    # -----------------------------------------------------------------------

    def media_seek(self, offset):

        if offset < self.start_pos:
            offset = self.start_pos
        if offset > self.end_pos:
            offset = self.end_pos

        force_pause = False
        if self.media_playing() is not None:
            self.pause()
            force_pause = True

        try:
            self.set_pos(offset)
            for m in self.__media:
                m.Seek(offset)
        except IntervalRangeException as e:
            wx.LogError(str(e))
            return

        # BUG OF MACOS BACKEND:
        # Seek of media is not precise at all...
        # It produces messages like:
        # error of -0.040 introduced due to very low timescale
        cur_pos = self.media_tell()
        self.set_pos(cur_pos)
        if force_pause is True:
            self.play()

    # -----------------------------------------------------------------------

    def media_rewind(self):
        """Seek media to some time earlier."""
        new_pos = self.pos - 2000
        self.media_seek(new_pos)

    # -----------------------------------------------------------------------

    def media_forward(self):
        """Seek media to some time later on."""
        new_pos = self.pos + 2000
        self.media_seek(new_pos)

    # -----------------------------------------------------------------------

    def media_volume(self, value):
        """Adjust volume to the given scale value."""
        for m in self.__media:
            m.SetVolume(value)

    # -----------------------------------------------------------------------

    def play(self):
        """Override. Play/Pause the media and notify parent."""
        if self.media_playing() is not None:
            # Requested action is to pause.
            self.pause()
        else:
            # Requested action is to play.
            self._timer.Start(self._refreshtimer)
            self.notify(action="play", value=None)
            self.Paused(False)
            for m in self.__media:
                if m.GetMediaType() == MediaType().video:
                    m.Play()
            for m in self.__media:
                if m.GetMediaType() == MediaType().audio:
                    m.Play()

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause the media and notify parent."""
        self._timer.Stop()
        self.notify(action="pause", value=None)
        self.Paused(True)
        for m in self.__media:
            if m.GetMediaType() == MediaType().audio:
                m.Pause()
        for m in self.__media:
            if m.GetMediaType() == MediaType().video:
                m.Pause()

    # -----------------------------------------------------------------------

    def stop(self):
        """Override. Stop playing the media and notify parent."""
        self._timer.Stop()
        self.DeletePendingEvents()
        self.notify(action="stop", value=None)
        self.Paused(False)
        for m in self.__media:
            m.Stop()
            m.Seek(self.start_pos)
        self.set_pos(self.start_pos)

    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------

    def OnTimer(self, event):
        """Call it if EVT_TIMER is captured."""
        # There's a delay (about 450-500ms) between the time the timer
        # started and the time the media really starts to play.
        # If the media didn't started to play anymore...
        if self.pos == self.start_pos:
            new_pos = self.media_tell()
        else:
            new_pos = self.pos + self._refreshtimer

        if (new_pos % (self._refreshtimer*100)) < self._refreshtimer:
            new_pos = self.__resynchronize()

        # Move the slider at the new position, except if out of range
        try:
            self.set_pos(new_pos)
        except IntervalRangeException:
            self.stop()
            if self.autoreplay is True:
                self.play()

    # ----------------------------------------------------------------------

    def __reset(self):
        self.stop()
        self._length = 0
        self.set_range(0, 0)

    # ----------------------------------------------------------------------

    def __resynchronize(self):
        """Re-synchronize slider position and media tell() position."""
        # check where the media really are in time
        values = [m.Tell() for m in self.__media]
        wx.LogDebug("Position values of media: {:s}".format(str(values)))
        max_pos = max(values)

        # Cant re-synchronize under MacOS, either Seek:
        #  - prints message CMTimeMakeWithSeconds: warning: very low timescale
        #  - or goes at a wrong position.
        #if (self.start_pos + 5) < min_pos < (max_pos - 5):
        #    wx.LogDebug(" -->>>> Re-synchronize to {:d}".format(min_pos))
        #    for m in self.__media:
        #        m.Seek(min_pos)

        return max_pos

    # ----------------------------------------------------------------------

    def __validate_offsets(self):
        """Adjust if given offsets are not in an appropriate range."""
        # if len(self.__media) > 0:
        #    offset = self.media_tell()
        #    if offset < self.get_start_pos() or offset > self.get_end_pos():
        #        self.media_seek(self.get_start_pos())
        #        self.GetSlider().SetValue(offset)

        # validate end position (no longer than the length)
        if self.end_pos > self._length:
            self.GetSlider().SetRange(self.start_pos, self._length)

        offset = self.media_tell()
        if offset < self.start_pos or offset > self.end_pos:
            self.media_seek(self.start_pos)
            real_cur_pos = self.media_tell()
            self.GetSlider().SetValue(real_cur_pos)

        wx.LogDebug(" START {:d}  END {:d}  POS {:d}".format(self.start_pos, self.end_pos, self.pos))

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        self.mp = sppasMultiPlayerPanel(self)

        self.mc1 = sppasMediaCtrl(self)
        self.mc1.Hide()

        self.mc2 = sppasMediaCtrl(self)
        self.mc2.Hide()

        self.mc3 = sppasMediaCtrl(self)
        self.mc3.Hide()

        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.OnMediaLoaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.OnMediaNotLoaded)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.mp, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.SetForegroundColour(wx.Colour(225, 225, 225))

        wx.CallAfter(self.DoLoadFile)

    # ----------------------------------------------------------------------

    def OnMediaLoaded(self, evt):
        media = evt.GetEventObject()
        wx.LogDebug("Media loaded successfully:")
        wx.LogDebug(" - Media file: {:s}".format(media.GetFilename()))
        wx.LogDebug(" - Media length: {:d}".format(media.Length()))
        wx.LogDebug(" - Media type: {:s}".format(self.mediatype(media.GetMediaType())))
        self.mp.add_media(media)
        self.mp.set_range()

    # ----------------------------------------------------------------------

    def OnMediaNotLoaded(self, evt):
        media = evt.GetEventObject()
        wx.LogError("Media failed to be loaded: {:s}".format(media.GetFilename()))

    # ----------------------------------------------------------------------

    def DoLoadFile(self):
        wx.LogDebug("Start loading media...")
        self.mc1.Load(os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
        self.mc2.Load(os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))
        self.mc3.Load("/Users/bigi/Movies/Monsters_Inc.For_the_Birds.mpg")

    # ----------------------------------------------------------------------

    @staticmethod
    def mediatype(value):
        with MediaType() as m:
            if value == m.audio:
                return "audio"
            if value == m.video:
                return "video"
            if value == m.unknown:
                return "unknown"
            if value == m.unsupported:
                return "unsupported"
        return str(m)
