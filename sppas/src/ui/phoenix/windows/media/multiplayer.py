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
from .mediatest import sppasMediaPanel
from .mediactrl import MediaType
from .playerctrl import sppasPlayerControlsPanel

# ---------------------------------------------------------------------------


class sppasMultiPlayerPanel(sppasPlayerControlsPanel):
    """Create a panel with controls to manage a list of media.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    A player controls panel to play several media at a time.

    """

    def __init__(self, parent, id=-1,
                 media=list(),
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
        self._refreshtimer = 40
        self.Bind(wx.EVT_TIMER, self.OnTimer)

    # -----------------------------------------------------------------------

    def get_start_pos(self):
        return self.GetSlider().GetRange()[0]

    def get_end_pos(self):
        return self.GetSlider().GetRange()[1]

    def get_pos(self):
        return self.GetSlider().GetValue()

    def set_range(self, start, end):
        assert int(start) <= int(end)
        if start < 0:
            start = 0
        if end > self._length:
            end = self._length
        self.GetSlider().SetRange(start, end)
        if self.pos < start or self.pos > end:
            self.set_pos(start)

    def set_pos(self, offset):
        assert int(offset) >= 0
        # On MacOS (quicktime backend), the offset is not precise enough.
        # It can be + or - 3 compared to the expected value!
        if (offset-3) < self.start_pos or (offset+3) > self.end_pos:
            raise IntervalRangeException(offset, self.start_pos, self.end_pos)
        self.GetSlider().SetValue(offset)

    start_pos = property(get_start_pos, None)
    end_pos = property(get_end_pos, None)
    pos = property(get_pos, set_pos)

    # -----------------------------------------------------------------------

    def get_autoreplay(self):
        transport_panel = self.FindWindow("transport_panel")
        return transport_panel.FindWindow("media_repeat").IsPressed()

    autoreplay = property(get_autoreplay, None)

    # -----------------------------------------------------------------------

    def set_media(self, media_lst):
        """Set a new list of media.

        It is supposed that all media are already loaded.

        :param media_lst: (list)

        """
        self.__reset()
        self.__media = list()

        for m in media_lst:
            self.__append_media(m)

        if len(self.__media) > 0:
            # re-evaluate length
            self._length = max(m.Length() for m in self.__media)
            # validate current offsets
            self.__validate_offsets()
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
                wx.LogMessage("Media {:s} is added to the player."
                              "".format(m.GetFilename()))
                self.__media.append(m)
                return True

        return False

    # -----------------------------------------------------------------------

    def add_media(self, media):
        """Add a media into the list of media managed by this control."""
        if media in self.__media:
            return False
        ok = self.__append_media(media)
        if ok is True:
            # re-evaluate length
            self._length = max(m.Length() for m in self.__media)
            # seek the new media to the current position.
            media.seek(self.media_tell())
        return ok

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
        """Return the actual position in time in a media."""
        # In theory, all media should return the same value... but framerate
        # of the media are different. Tell() in an audio is more precise.
        # And in theory it should be equal to the cursor value.
        value = self.GetSlider().GetValue()
        wx.LogMessage("MEDIA TELL. SLIDER VALUE IS {:d}".format(value))
        # Search for an audio first
        for m in self.__media:
            if m.GetMediaType() == MediaType().audio:
                wx.LogMessage("MEDIA TELL. AUDIO VALUE IS {:d}".format(m.Tell()))
                return m.Tell()
        # No audio... search for a video
        for m in self.__media:
            if m.GetMediaType() == MediaType().video:
                wx.LogMessage("MEDIA TELL. VIDEO VALUE IS {:d}".format(m.Tell()))
                return m.Tell()

        # No audio nor video in the list of media
        wx.LogMessage("MEDIA TELL. No audio nor video. VALUE IS 0")
        return 0

    # -----------------------------------------------------------------------

    def media_seek(self, offset):

        if offset < self.start_pos:
            offset = self.start_pos
        if offset > self.end_pos:
            offset = self.end_pos

        self.set_pos(offset)
        for m in self.__media:
            m.Seek(offset)

    # -----------------------------------------------------------------------

    def play(self):
        """Override. Play the media and notify parent."""
        wx.LogMessage("Play media...")
        self._timer.Start(self._refreshtimer)
        self.notify(action="play", value=None)
        for m in self.__media:
            if m.GetMediaType() == MediaType().video:
                m.Play()
        for m in self.__media:
            if m.GetMediaType() == MediaType().audio:
                m.Play()

    # -----------------------------------------------------------------------

    def stop(self):
        """Override. Stop playing the media and notify parent."""
        self._timer.Stop()
        self.notify(action="stop", value=None)
        for m in self.__media:
            m.Stop()

    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------

    def OnTimer(self, event):
        """Call it if EVT_TIMER is captured."""

        new_offset = self.pos + self._refreshtimer
        new_real_pos = self.media_tell()

        # Move the slider at the new position, except if out of range
        try:
            self.set_pos(new_offset)
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

    def __validate_offsets(self):
        """Adjust if given offsets are not in an appropriate range."""
        if len(self.__media) > 0:
            offset = self.media_tell()
            if offset < self._offsets[0] or offset > self._offsets[1]:
                self.media_seek(self._offsets[0])
                self.GetSlider().SetValue(offset)

        # validate end position (no longer than the length)
        if self._offsets[1] > self._length:
            self._offsets = (self._offsets[0], self._length)
            self.GetSlider().SetRange(self._offsets[0], self._offsets[1])

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        self.mp = sppasMultiPlayerPanel(self)
        self.mc = sppasMediaPanel(self)
        self.mc.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.mp, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetBackgroundColour(wx.Colour(60, 60, 60))
        self.SetForegroundColour(wx.Colour(225, 225, 225))

        wx.CallAfter(
            self.DoLoadFile,
            os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))

    # ----------------------------------------------------------------------

    def OnMediaLoaded(self, evt):
        wx.LogDebug(" ON MEDIA LOADED DU TEST PANEL * * * ")
        self.mp.set_media([self.mc])

    # ----------------------------------------------------------------------

    def DoLoadFile(self, path):
        if self.mc.Load(path) is False:
            wx.MessageBox("Unable to load %s: Unsupported format?" % path,
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            # self.mc.SetInitialSize()
            # self.GetSizer().Layout()
            wx.LogMessage("File loaded. Length is {:d}".format(self.mc._length))
