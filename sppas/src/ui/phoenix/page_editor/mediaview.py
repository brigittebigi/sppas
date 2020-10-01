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

    ui.phoenix.page_editor.mediaview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import os
import wx
import wx.lib
import wx.media

from sppas.src.config import paths

from ..windows import sppasMediaCtrl
from ..windows import MediaType
from ..windows import MediaEvents
from ..windows import sppasScrolledPanel
from ..main_events import ViewEvent, EVT_VIEW

from .baseview import sppasFileViewPanel

# ---------------------------------------------------------------------------
# Internal use of an event, when an item is clicked.

ItemClickedEvent, EVT_ITEM_CLICKED = wx.lib.newevent.NewEvent()
ItemClickedCommandEvent, EVT_ITEM_CLICKED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------

ERROR_COLOUR = wx.Colour(220, 30, 10, 128)     # red
WARNING_COLOUR = wx.Colour(240, 190, 45, 128)  # orange

# ---------------------------------------------------------------------------


class MediaViewPanel(sppasFileViewPanel):
    """A panel to display the content of an audio or a video.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The object embedded in this class is a sppasMediaCtrl.

    """

    # -----------------------------------------------------------------------
    # List of accepted percentages of zooming
    ZOOMS = (25, 50, 75, 100, 125, 150, 200, 250, 300, 400)

    # -----------------------------------------------------------------------

    def __init__(self, parent, filename, name="media_view_panel"):
        """Create a MediaTimeViewPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param filename: (str) The name of the file of the media
        :param name: (str) the widget name.

        """
        try:
            # Before creating the media, check if the file type is supported.
            media_type = sppasMediaCtrl.ExpectedMediaType(filename)
            if media_type == MediaType().unknown:
                raise TypeError("File {:s} is of an unknown type "
                                "(no audio nor video).".format(filename))
        except TypeError:
            self.Destroy()
            raise

        super(MediaViewPanel, self).__init__(parent, filename, name)
        self._setup_events()

        mc = self.GetPane()
        mc.Load(self._filename)

    # -----------------------------------------------------------------------
    # Media management
    # -----------------------------------------------------------------------

    def GetMediaType(self):
        return self.GetPane().GetMediaType()

    # -----------------------------------------------------------------------

    def media_playing(self):
        """Return True if the embedded media is playing."""
        return self.GetPane().IsPlaying()

    # -----------------------------------------------------------------------

    def media_paused(self):
        """Return True if the embedded media is paused."""
        return self.GetPane().IsPaused()

    # -----------------------------------------------------------------------

    def media_stopped(self):
        """Return True if the embedded media is stopped."""
        return self.GetPane().IsStopped()

    # -----------------------------------------------------------------------

    def media_loading(self):
        """Return True if the embedded media is loading."""
        return self.GetPane().IsLoading()

    # -----------------------------------------------------------------------

    def media_length(self):
        """Return the duration of the media (milliseconds)."""
        return self.GetPane().Length()

    # -----------------------------------------------------------------------

    def media_tell(self):
        """Return the current position in time (milliseconds)."""
        return self.GetPane().Tell()

    # -----------------------------------------------------------------------

    def media_zoom(self, direction):
        """Zoom the media of the given panel.

        :param direction: (int) -1 to zoom out, +1 to zoom in and 0 to reset
        to the initial size.

        """
        if self.IsExpanded() is False:
            return

        if direction == 0:
            self.GetPane().SetZoom(100)
        else:
            idx_zoom = MediaViewPanel.ZOOMS.index(self._child_panel.GetZoom())
            if direction < 0:
                new_idx_zoom = max(0, idx_zoom-1)
            else:
                new_idx_zoom = min(len(MediaViewPanel.ZOOMS)-1, idx_zoom+1)
            self._child_panel.SetZoom(MediaViewPanel.ZOOMS[new_idx_zoom])

        # Adapt our size to the new media size and the parent updates its layout
        self.Freeze()
        self.InvalidateBestSize()
        self.Thaw()
        self.SetStateChange(self.GetBestSize())

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("zoom_in")
        self.AddButton("zoom_out")
        self.AddButton("close")

        mc = sppasMediaCtrl(self)
        self.SetPane(mc)
        self.media_zoom(0)  # 100% zoom = initial size

        self.Collapse()

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_BUTTON, self.__process_tool_event)

        # Events related to the media
        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__process_media_loaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__process_media_not_loaded)

    # -----------------------------------------------------------------------

    def __process_media_loaded(self, event):
        """Process the end of load of a media."""
        # media = event.GetEventObject()
        # media_size = media.DoGetBestSize()
        # media.SetSize(media_size)
        # self.Expand()
        self.Collapse()

        evt = MediaEvents.MediaActionEvent(action="loaded", value=True)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def __process_media_not_loaded(self, event):
        """Process the end of a failed load of a media."""
        self.Collapse()

        evt = MediaEvents.MediaActionEvent(action="loaded", value=False)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def __process_tool_event(self, event):
        """Process a button event from the tools.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "zoom_in":
            self.media_zoom(1)

        elif name == "zoom_out":
            self.media_zoom(-1)

        elif name == "close":
            self.notify("close")

        else:
            event.Skip()

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test MediaView")

        p1 = MediaViewPanel(self, filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
        p2 = MediaViewPanel(self, filename=os.path.join(paths.samples, "faces", "video_sample.mp4"))

        p2.GetPane().SetDrawPeriod(2.300, 3.500)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p2, 0, wx.EXPAND)
        s.Add(p1, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Bind(MediaEvents.EVT_MEDIA_ACTION, self._process_media_action)
        p1.Bind(MediaEvents.EVT_MEDIA_LOADED, self.OnMediaLoaded)

    # -----------------------------------------------------------------------

    def _process_media_action(self, event):
        """Process an action event from the player.

        An action on media files has to be performed.

        :param event: (wx.Event)

        """
        name = event.action
        value = event.value

        if name == "loaded":
            if value is True:
                event.GetEventObject().GetPane().Play()

        event.Skip()

    # ----------------------------------------------------------------------

    def OnMediaLoaded(self, evt):
        media = evt.GetEventObject()
        wx.LogDebug(str(media))
        wx.LogDebug(media.GetFilename())

        audio_prop = media.GetAudioProperties()
        if audio_prop is not None:
            audio_prop.EnableWaveform(True)
            media.SetBestSize()

        self.Layout()
