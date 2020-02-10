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

    ui.phoenix.page_analyze.timeview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.media
import wx.lib.newevent

from sppas import paths

import sppas.src.audiodata.aio

from ..windows import sppasScrolledPanel
from ..windows import sppasCollapsiblePanel
from .baseview import sppasBaseViewPanel
from ..windows import sppasMediaPanel
from ..windows import MediaType
from ..windows import MediaEvents

# ---------------------------------------------------------------------------
# Internal use of an event, when an item is clicked.

ItemClickedEvent, EVT_ITEM_CLICKED = wx.lib.newevent.NewEvent()
ItemClickedCommandEvent, EVT_ITEM_CLICKED_COMMAND = wx.lib.newevent.NewCommandEvent()

# ---------------------------------------------------------------------------

ERROR_COLOUR = wx.Colour(220, 30, 10, 128)     # red
WARNING_COLOUR = wx.Colour(240, 190, 45, 128)  # orange

# ---------------------------------------------------------------------------


class MediaTimeViewPanel(sppasBaseViewPanel):
    """A panel to display the content of an audio or a video.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The object this class is displaying is a sppasAudio.
    Can not be constructed if the file is not supported and/or if an error
    occurred when opening or reading.

    """

    # List of accepted percentages of zooming
    ZOOMS = (10, 25, 50, 75, 100, 125, 150, 200, 250, 300)

    def __init__(self, parent, filename, name="media_timeview_panel"):
        media_type = sppasMediaPanel.ExpectedMediaType(filename)
        if media_type == MediaType().unknown:
            raise TypeError("File {:s} is of an unknown type "
                            "(no audio nor video).".format(filename))
        self._mt = media_type
        self._object = None

        super(MediaTimeViewPanel, self).__init__(parent, filename, name)

        # self.Bind(sppasMedia.EVT_MEDIA_ACTION, self._process_action)
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("zoom_in")
        self.AddButton("zoom_out")
        self.AddButton("zoom")
        self.AddButton("close")
        self._create_child_panel()
        self.Expand()

    # -----------------------------------------------------------------------

    def _create_child_panel(self):
        """Override. Create the child panel."""
        mc = sppasMediaPanel(self)
        self.SetPane(mc)
        self.media_zoom(0)  # 100% zoom = initial size
        mc = self.GetPane()
        # Load the media
        if mc.Load(self._filename) is True:
            # Under Windows, the Load methods always return True,
            # even if the media is not loaded...
            # time.sleep(0.1)
            self.__set_media_properties(mc)
        else:
            self.Collapse()
            mc.Bind(wx.media.EVT_MEDIA_LOADED, self.__process_media_loaded)

    # ------------------------------------------------------------------------

    def load_text(self):
        """Load the file content into an object.

        Raise an exception if the file is not supported or can't be read.

        """
        pass

    # -----------------------------------------------------------------------

    def __process_media_loaded(self, event):
        """Process the end of load of a media."""
        wx.LogMessage("Media loaded event received.")
        media = event.GetEventObject()
        self.__set_media_properties(media)

    # -----------------------------------------------------------------------

    def __set_media_properties(self, media):
        """Fix the properties of the media."""
        media_size = media.DoGetBestSize()
        media.SetSize(media_size)
        self.Expand()
        wx.LogDebug("Send MediaActionEvent with action=loaded to parent: {:s}".format(self.GetParent().GetName()))
        evt = MediaEvents.MediaActionEvent(action="loaded", value=None)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def GetMediaType(self):
        return self._child_panel.GetMediaType()

    # -----------------------------------------------------------------------

    def Layout(self):
        """Do the layout.

        Normally, the layout makes the child panel to be adjusted to the size
        of self. Instead, here we let the child panel suiting its best height,
        and we adjust its width with our borders.

        """
        # we need to complete the creation first
        if not self._tools_panel or not self._child_panel:
            return False

        w, h = self.GetSize()
        bw = w - self._border
        bh = self.GetButtonHeight()
        # fix pos and size of the top panel with tools
        self._tools_panel.SetPosition((self._border, 0))
        self._tools_panel.SetSize(wx.Size(bw, bh))

        if self.IsExpanded():
            cw, ch = self._child_panel.DoGetBestSize()
            # fix pos and size of the child window
            pw, ph = self.GetSize()
            x = self._border + bh  # shift of the icon size (a square).
            y = bh + self._border
            pw = pw - x - self._border      # left-right borders
            ph = ph - y - self._border      # top-bottom borders
            self._child_panel.SetSize(wx.Size(pw, ch))
            self._child_panel.SetPosition((x, y))
            self._child_panel.Show(True)

        return True

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """
        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "zoom":
            self.media_zoom(0)

        elif name == "zoom_in":
            self.media_zoom(1)

        elif name == "zoom_out":
            self.media_zoom(-1)

        elif name == "close":
            self.media_remove(obj)

        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def OnButton(self, event):
        """Override. Handle the wx.EVT_BUTTON event.

        :param event: a CommandEvent event to be processed.

        """
        sppasCollapsiblePanel.OnButton(self, event)
        if self.IsExpanded() is False:
            # The media was expanded, now it is collapsed.
            self._child_panel.Stop()
            self.EnableButton("zoom", False)
            self.EnableButton("zoom_in", False)
            self.EnableButton("zoom_out", False)
        else:
            self.EnableButton("zoom", True)
            self.EnableButton("zoom_in", True)
            self.EnableButton("zoom_out", True)
        event.Skip()

    # -----------------------------------------------------------------------
    # Media management
    # -----------------------------------------------------------------------

    def media_offset_get_start(self):
        """Return the start position of the current period (milliseconds)."""
        self.GetPane().GetOffsetPeriod()[0]

    def media_offset_get_end(self):
        """Return the end position of the current period (milliseconds)."""
        self.GetPane().GetOffsetPeriod()[1]

    def media_offset_period(self, start, end):
        """Fix a start position and a end position to play the media.

        Stop the media if playing or paused.

        :param start: (int) Start time in milliseconds
        :param end: (int) End time in milliseconds

        """
        self.GetPane().SetOffsetPeriod(start, end)

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

    def media_play(self, replay=None):
        """Play the media."""
        if replay is None:
            return self.GetPane().Play()
        if replay is False:
            return self.GetPane().NormalPlay()
        if replay is True:
            return self.GetPane().AutoPlay()
        return False

    # -----------------------------------------------------------------------

    def media_pause(self):
        """Pause the media (if playing)."""
        return self.GetPane().Pause()

    # -----------------------------------------------------------------------

    def media_stop(self):
        """Stop the media (if playing or paused)."""
        return self.GetPane().Stop()

    # -----------------------------------------------------------------------

    def media_length(self):
        """Return the duration of the media (milliseconds)."""
        return self.GetPane().Length()

    # -----------------------------------------------------------------------

    def media_tell(self):
        """Return the current position in time (milliseconds)."""
        return self.GetPane().Tell()

    # -----------------------------------------------------------------------

    def media_seek(self, position):
        """Seek to a position within the media (milliseconds)."""
        self.GetPane().Seek(position, mode=wx.FromStart)

    # -----------------------------------------------------------------------

    def media_volume(self, value=None):
        """Adjust the volume of the media, ranging 0.0 .. 1.0."""
        if value is not None:
            self.GetPane().SetVolume(value)
        return self.GetPane().GetVolume()

    # -----------------------------------------------------------------------

    def media_zoom(self, direction):
        """Zoom the media of the given panel.

        :param direction: (int) -1 to zoom out, +1 to zoom in and 0 to reset
        to the initial size.

        """
        if self.IsExpanded() is False:
            return

        if direction == 0:
            self._child_panel.SetZoom(100)
        else:
            idx_zoom = MediaTimeViewPanel.ZOOMS.index(self._child_panel.GetZoom())
            if direction < 0:
                new_idx_zoom = max(0, idx_zoom-1)
            else:
                new_idx_zoom = min(len(MediaTimeViewPanel.ZOOMS)-1, idx_zoom+1)
            self._child_panel.SetZoom(MediaTimeViewPanel.ZOOMS[new_idx_zoom])

        size = self.DoGetBestSize()
        self.SetSize(size)
        self.GetParent().Layout()

    # -----------------------------------------------------------------------

    def media_slider(self, slider):
        """Assign a slider to the media."""
        self.GetPane().SetSlider(slider)

    # -----------------------------------------------------------------------

    def media_remove(self, obj):
        """Remove the media we clicked on the collapsible panel close button."""
        self._child_panel.Destroy()
        self.Destroy()

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        p1 = MediaTimeViewPanel(self,
             filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
        p1.GetPane().Play()

        p2 = MediaTimeViewPanel(self,
             filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))

        p3 = MediaTimeViewPanel(self,
            filename=os.path.join(paths.samples, "samples-fra", "F_F_C006-P6.wav"))

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND)
        s.Add(p2, 0, wx.EXPAND)
        s.Add(p3, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

