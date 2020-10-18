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
from sppas.src.exceptions.exc import IntervalRangeException

from ..panels import sppasPanel
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
    All the media are requested to be played but depending on the backend,
    they'll really start to play at different time values.
    Observed differences:
        - Linux (Gstreamer): about 2-3 ms
        - MacOS (AvPlayer): about 11-13 ms
        - Windows (Wmp10): to do

    Notice that media are not displayed by this panel and it is supposed that
    all the given media are already loaded.

    Known problems while playing a media during a given period of time:

     - Under Windows, if a period is given to be played, the sound is played
       after the end is reached (about 400ms).

    """

    # -----------------------------------------------------------------------
    # The minimum duration the backend can play - empirically estimated.
    # We should fix these values depending on the backend system instead of
    # the operating system.
    # GStreamer = 40 // AvPlayer = 1000 // Wmp10 = 400
    if wx.Platform == "__WXMSW__":
        MIN_RANGE = 400
    elif wx.Platform == "__WXMAC__":
        MIN_RANGE = 1000
    else:
        MIN_RANGE = 40

    # -----------------------------------------------------------------------

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
        self.__shift = 1000
        self.min_range = sppasMultiPlayerPanel.MIN_RANGE

        self.Bind(wx.EVT_TIMER, self._on_timer)

    # -----------------------------------------------------------------------
    # Public methods to manage offset and period
    # -----------------------------------------------------------------------

    def get_start_pos(self):
        """Return the start position in time (milliseconds)."""
        # s = self._slider.get_range()[0]
        s = self._slider.GetRange()[0]
        return s  # int(s * 1000.)

    # -----------------------------------------------------------------------

    def get_end_pos(self):
        """Return the end position in time (milliseconds)."""
        # e = self._slider.get_range()[1]
        e = self._slider.GetRange()[1]
        return e  #  int(e * 1000.)

    # -----------------------------------------------------------------------

    def get_pos(self):
        """Return the current position in time (milliseconds)."""
        # p = self._slider.get_pos()
        p = self._slider.GetValue()
        return p  # int(p * 1000.)

    # -----------------------------------------------------------------------

    def set_range(self, start=None, end=None):
        """Fix the period to draw (milliseconds).

        It is also the period to be played if the toggle button of the
        visible part is selected. Then, the slider range, its position
        and the media position are modified.

        It is not verified that given end value is not larger than the
        length: it allows to fix the range before the media are defined.

        In theory, this range would be as wanted, but some backends have
        serious limitations:
        - Under Windows, the end offset is not respected. It's continuing to
        play about 400ms after the end offset.
        - Under MacOS, a period less than 1 sec is not played at all and it
        must start at X*1000 ms.
        Those problems are requiring to adapt requested start/end positions...

        :param start: (int) Start time. Default is 0.
        :param end: (int) End time. Default is length.
        :return: Real start and end positions fixed.

        """
        if start is None:
            start = 0
        if end is None:
            end = self._length

        if wx.Platform == "__WXMAC__":
            # To be consistent with AvPlayer backend (no comment!)
            if start % 1000 > 0:
                # Force to start at a timescale in seconds
                start = int(float(start) // 1000.) * 1000
        else:
            # Start 5ms before the requested start pos
            start = max(0, start - 5)

        # Move end to ensure a min range
        end = max(end, start + self.min_range)

        self._slider.SetRange(start, end)
        self._slider.Layout()
        self._slider.Refresh()

        self.media_seek(start)
        # TODO when slider will be a TimeSliderPanel:
        # s, _ = self._slider.get_range()
        # s = int(s * 1000.)
        # if s != self.get_pos():
        #     self.media_seek(s)

        for m in self.__media:
            m.SetDrawPeriod(start, end)
            m.Refresh()

        return start, end

    # -----------------------------------------------------------------------

    def set_pos(self, offset):
        """Set the current position in time (milliseconds) for the slider.

        Notice that it sets only the slider and not the position in the media.

        :param offset: (int) Time value in milliseconds

        """
        assert int(offset) >= 0
        if (offset+5) < self.start_pos or (offset+5) > self.end_pos:
            wx.LogError("Current range is [%d, %d], but requested offset is %d"
                        "" % (self.start_pos, self.end_pos, offset))
            raise IntervalRangeException(offset, self.start_pos, self.end_pos)

        # self._slider.set_pos(float(offset) / 1000.)
        self._slider.SetValue(offset)

    # -----------------------------------------------------------------------

    start_pos = property(get_start_pos, None)
    end_pos = property(get_end_pos, None)
    pos = property(get_pos, set_pos)

    # -----------------------------------------------------------------------
    # Public methods to manage the media
    # -----------------------------------------------------------------------

    def get_autoreplay(self):
        return self._transport_panel.FindWindow("media_repeat").IsPressed()

    autoreplay = property(get_autoreplay, None)

    # -----------------------------------------------------------------------

    def set_media(self, media_lst):
        """Set a new list of media.

        It is supposed that all media are already loaded.
        If a media type is unsupported or unknown, the media is not added.
        The range is set to the largest one.

        :param media_lst: (list)
        :return: (int) Number of media added.

        """
        self.__reset()
        self.__media = list()

        for m in media_lst:
            self.__append_media(m)

        if len(self.__media) > 0:
            # re-evaluate length
            self._length = max(m.Length() for m in self.__media)
            # fix the largest range and seek at the beginning of the period
            self.set_range()
            # TODO: when the slider will be a TimeSliderPanel
            # self._slider.set_duration(1000. * float(self._length))
            # self._slider.Layout()
            # self._slider.Refresh()
            # s, e = self._slider.get_range()
            # s = 1000. * float(s)
            # e = 1000. * float(e)
            # if s != self.get_start_pos() or e != self.get_end_pos():
            #     self.set_range(s, e)

        return len(self.__media)

    # -----------------------------------------------------------------------

    def add_media(self, media, filename=None):
        """Add a media into the list of media managed by this control.

        Re-evaluate our length, and set the range.
        Seek at the beginning of the range.

        :param media: ()
        :param filename: (str)
        :return: (bool)

        """
        if media in self.__media:
            return False

        ok = self.__append_media(media)
        if ok is True:
            wx.LogDebug("Media of file {} was added to the multi-player."
                        "".format(str(filename)))
            # re-evaluate length
            self._length = max(m.Length() for m in self.__media)

            # seek the new media to the current position is not possible with
            # macOS AvPlayer backend which must seek to X*1000 ms...
            # we'll seek all the media at the current start pos.
            cur_start = self.start_pos
            self.set_range()
            self.media_seek(cur_start)

        return ok

    # -----------------------------------------------------------------------

    def remove_media(self, media):
        """Remove a media of the list of media managed by this control.

        :param media:
        :return: (bool)

        """
        if media not in self.__media:
            return False
        media.Stop()
        self.__media.remove(media)
        wx.LogDebug("Media was removed to the multi-player.")

        # re-evaluate length
        if len(self.__media) > 0:
            self._length = max(m.Length() for m in self.__media)
        else:
            self._length = 0

        return True

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
            return min(values)

        # No audio nor video in the list of media
        return 0

    # -----------------------------------------------------------------------

    def media_seek(self, offset):
        """Seek all media to the given offset.

        LIMITATIONS: Under MacOS, some errors can occur. It produces messages
        like: error of -0.040 introduced due to very low timescale.
        The offset should always be a multiple of 1000 to work properly.

        :param offset: (int) Value in milliseconds.

        """
        if offset < self.start_pos:
            offset = self.start_pos
        if offset > self.end_pos:
            offset = self.end_pos

        force_pause = False
        if self.media_playing() is not None:
            self.pause()
            force_pause = True

        try:
            # Debug("Media seek to position {}".format(offset))
            self.set_pos(offset)
            for m in self.__media:
                m.Seek(offset)
                # wx.LogDebug(" -> tell after seek: {}".format(m.Tell()))

        except IntervalRangeException as e:
            wx.LogError("Media seek error: {:s}".format(str(e)))
            return

        if force_pause is True:
            self.play()

    # -----------------------------------------------------------------------

    def get_shift(self):
        """Return the time delay to rewind or forward. Default is 1000 ms."""
        return self.__shift

    # -----------------------------------------------------------------------

    def set_shift(self, value):
        """Set the time delay to rewind or forward.

        :param value: (int) Value (min is 50, max is length/2 of media)

        """
        value = int(value)
        if value < 50:
            self.__shift = 50
        elif self._length > 0 and value > (self._length // 2):
            self.__shift = self._length // 2
        else:
            self.__shift = value

    # -----------------------------------------------------------------------

    def media_rewind(self):
        """Seek media to some time earlier. Default is 1000 ms."""
        new_pos = self.get_pos() - self.__shift
        self.media_seek(new_pos)

    # -----------------------------------------------------------------------

    def media_forward(self):
        """Seek media to some time later on. Default is 1000 ms."""
        new_pos = self.get_pos() + self.__shift
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
    # Callbacks to events
    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        """Call it if EVT_TIMER is captured.

        Known BUGS of backends we're trying to manage:

        Under MacOS:
        There's a delay (about 450-500ms) between the moment the timer
        started and the moment the media really starts to play.

        Under Windows:
        The media is continuing to play after we requested it to stop
        (about 200ms-300ms).

        """
        # If the media didn't started to play... Use "tell" of the media to
        # know where we really are in time.
        if self.get_pos() == self.start_pos:
            new_pos = self.media_tell()
        else:
            new_pos = self.pos + self._refreshtimer

        if (new_pos % (self._refreshtimer*100)) < self._refreshtimer:
            new_pos = self.__resynchronize()

        # Move the slider at the new position, except if out of range
        try:
            # wx.LogDebug("On timer. set position to {}".format(new_pos))
            self.set_pos(new_pos)
        except IntervalRangeException:
            self.stop()
            if self.autoreplay is True:
                self.play()

    # ----------------------------------------------------------------------
    # Private methods
    # ----------------------------------------------------------------------

    def __reset(self):
        self.stop()
        self._length = 0
        self.set_range(0, 0)

    # ----------------------------------------------------------------------

    def __resynchronize(self):
        """Re-synchronize slider position at media tell() position."""
        if len(self.__media) == 0:
            return self.pos
        if len(self.__media) == 1:
            return self.__media[0].Tell()

        # check where the media really are in time
        values = [m.Tell() for m in self.__media]
        # wx.LogDebugMessage Positions (ms) in the media: %s." % str(values))
        max_pos = max(values)

        # Cant re-synchronize under MacOS, either Seek:
        #  - prints message CMTimeMakeWithSeconds: warning: very low timescale
        #  - or goes at a wrong position.
        #if (self.start_pos + 5) < min_pos < (max_pos - 5):
        #    wx.LogDebug(" -->>>> Re-synchronize to {:d}".format(min_pos))
        #    for m in self.__media:
        #        m.Seek(min_pos)

        return max_pos

    # -----------------------------------------------------------------------

    def __append_media(self, m):
        """Append a media to the list of media."""
        mt = m.GetMediaType()
        if mt == MediaType().unknown:
            wx.LogError("Media {:s} is not added to the player: "
                        "unknown format."
                        "".format(m.GetFilename()))

        elif mt == MediaType().unsupported:
            wx.LogError("Media {:s} is not added to the player: "
                        "unsupported format."
                        "".format(m.GetFilename()))

        else:
            ml = m.Length()
            if ml == -1:
                wx.LogError("Media {:s} is not added to the player: "
                            "load not completed."
                            "".format(m.GetFilename()))
            else:
                wx.LogDebug("Media {:s} is added to the player."
                            "".format(m.GetFilename()))
                self.__media.append(m)
                if mt == MediaType().audio:
                    self.__media_audio_properties(m)

                return True

        return False

    # -----------------------------------------------------------------------

    def __media_audio_properties(self, media):
        audio_prop = media.GetAudioProperties()
        if audio_prop is not None:
            # by default, show only the waveform of audio files
            audio_prop.EnableInfos(False)
            audio_prop.EnableWaveform(True)
            w = audio_prop.get_waveform()
            # disable the border of the waveform
            w.SetBorderWidth(0)
            # fix the period to draw
            media.SetDrawPeriod(self.start_pos, self.end_pos)

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
        # self.mc3.Load("/Users/bigi/Movies/Monsters_Inc.For_the_Birds.mpg")
        # self.mc3.Load("/E/Videos/Monsters_Inc.For_the_Birds.mpg")

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
