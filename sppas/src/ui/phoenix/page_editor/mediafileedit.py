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

    ui.phoenix.page_editor.mediafileedit.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.lib
import wx.media

from sppas.src.config import paths

from ..windows.media import sppasMediaCtrl
from ..windows.media import MediaType
from ..windows.media import MediaEvents
from ..windows import sppasScrolledPanel

from .basefileedit import sppasFileViewPanel
from .editorevent import EVT_TIME_VIEW

# ---------------------------------------------------------------------------


class MediaViewPanel(sppasFileViewPanel):
    """A panel to display the content of an audio or a video.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The object embedded in this class is a sppasMediaCtrl.

    Events emitted by this class is EVT_TIME_VIEW:
        - action="close" to ask for closing the panel
        - action="media_loaded", value=boolean to inform the file was
        successfully or un-successfully loaded.

    """

    # -----------------------------------------------------------------------
    # List of accepted percentages of zooming
    ZOOMS = (25, 50, 75, 100, 125, 150, 200, 250, 300, 400)

    # -----------------------------------------------------------------------

    def __init__(self, parent, filename, name="media_view_panel"):
        """Create a MediaViewPanel.

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
        self.Collapse()

        mc = self.GetPane()
        mc.Load(self._filename)

    # -----------------------------------------------------------------------
    # Media management
    # -----------------------------------------------------------------------

    def GetMediaType(self):
        return self.GetPane().GetMediaType()
    
    def GetAudioProperties(self):
        return self.GetPane().GetAudioProperties()

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
            idx_zoom = MediaViewPanel.ZOOMS.index(self.GetPane().GetZoom())
            if direction < 0:
                new_idx_zoom = max(0, idx_zoom-1)
            else:
                new_idx_zoom = min(len(MediaViewPanel.ZOOMS)-1, idx_zoom+1)
            self.GetPane().SetZoom(MediaViewPanel.ZOOMS[new_idx_zoom])

        # Adapt our size to the new media size and the parent updates its layout
        self.Freeze()
        self.InvalidateBestSize()
        self.Thaw()
        best_size = self.GetBestSize()
        self.SetStateChange(best_size)

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

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_BUTTON, self.__process_tool_event)

        # Events related to the embedded media
        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__process_media_loaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__process_media_not_loaded)

    # -----------------------------------------------------------------------

    def __process_media_loaded(self, event):
        """Process the end of load of a media."""
        self.notify(action="media_loaded", value=True)

    # -----------------------------------------------------------------------

    def __process_media_not_loaded(self, event):
        """Process the end of a failed load of a media."""
        self.notify(action="media_loaded", value=False)

    # -----------------------------------------------------------------------

    def __process_tool_event(self, event):
        """Process a button event from the tools.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "zoom_in":
            self.media_zoom(1)
            self.notify("zoomed")

        elif name == "zoom_out":
            self.media_zoom(-1)
            self.notify("zoomed")

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
        p3 = MediaViewPanel(self, filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))

        p2.GetPane().SetDrawPeriod(2.300, 3.500)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND | wx.TOP, 2)
        s.Add(p2, 0, wx.EXPAND | wx.TOP, 2)
        s.Add(p3, 0, wx.EXPAND | wx.TOP, 2)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Bind(EVT_TIME_VIEW, self._process_action)

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action event from one of the media view panels.

        :param event: (wx.Event)

        """
        panel = event.GetEventObject()
        action = event.action
        value = event.value
        wx.LogDebug("{:s} received an event action {:s} of file {:s} with value {:s}"
                    "".format(self.GetName(), action, panel.get_filename(), str(value)))

        if action == "media_loaded":
            if value is True:
                audio_prop = panel.GetAudioProperties()
                if audio_prop is not None:
                    audio_prop.EnableInfos(False)
                    audio_prop.EnableWaveform(True)
                panel.Expand()
                self.Layout()

        event.Skip()
