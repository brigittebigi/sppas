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

import logging
import os
import wx
import wx.lib
import wx.media

from sppas import paths
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasRW

from ..windows import sppasPanel
from ..windows import sppasScrolledPanel
from ..windows import sppasCollapsiblePanel
from ..windows import sppasMediaCtrl
from ..windows import MediaType
from ..windows import MediaEvents
from ..windows.datactrls import sppasTierWindow
from ..main_events import ViewEvent, EVT_VIEW

from .baseview import sppasBaseViewPanel

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

    The object of this class is a sppasMediaCtrl.
    Can not be constructed if the file is not supported and/or if an error
    occurred when opening or reading.
    Send action 'loaded' with True or False value.

    """

    # -----------------------------------------------------------------------
    # List of accepted percentages of zooming
    ZOOMS = (25, 50, 75, 100, 125, 150, 200, 250, 300, 400)

    # -----------------------------------------------------------------------

    def __init__(self, parent, filename, name="media_timeview_panel"):
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

        self._object = None
        super(MediaTimeViewPanel, self).__init__(parent, filename, name)

        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__process_media_loaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__process_media_not_loaded)

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
            idx_zoom = MediaTimeViewPanel.ZOOMS.index(self._child_panel.GetZoom())
            if direction < 0:
                new_idx_zoom = max(0, idx_zoom-1)
            else:
                new_idx_zoom = min(len(MediaTimeViewPanel.ZOOMS)-1, idx_zoom+1)
            self._child_panel.SetZoom(MediaTimeViewPanel.ZOOMS[new_idx_zoom])

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
        self.AddButton("zoom")
        self.AddButton("close")
        self._create_child_panel()
        self.Collapse()

    # -----------------------------------------------------------------------

    def _create_child_panel(self):
        """Override. Create the child panel."""
        mc = sppasMediaCtrl(self)
        self.SetPane(mc)
        self.media_zoom(0)  # 100% zoom = initial size

    # ------------------------------------------------------------------------

    def load_text(self):
        """Override. Load the file content into an object."""
        pass

    # -----------------------------------------------------------------------

    def get_object(self):
        """Override. Return the sppasMediaCtrl."""
        return self.GetPane()

    # -----------------------------------------------------------------------
    # Events management
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
            self.notify("close")

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
            self.EnableButton("zoom", False)
            self.EnableButton("zoom_in", False)
            self.EnableButton("zoom_out", False)
        else:
            self.EnableButton("zoom", True)
            self.EnableButton("zoom_in", True)
            self.EnableButton("zoom_out", True)
        event.Skip()

# ---------------------------------------------------------------------------


class TrsTimeViewPanel(sppasBaseViewPanel):
    """A panel to display the content of an annotated files in a timeline.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020 Brigitte Bigi

    The object this class is displaying is a sppasTranscription.
    Can not be constructed if the file is not supported and/or if an error
    occurred when opening or reading.

    """

    def __init__(self, parent, filename, name="listview-panel"):
        self._object = sppasTranscription("NewDocument")
        self._dirty = False
        self._hicolor = wx.Colour(200, 200, 180)

        super(TrsTimeViewPanel, self).__init__(parent, filename, name)
        self.Bind(EVT_VIEW, self._process_view_event)

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight the filename if selected."""
        self._hicolor = color
        if self._object.get_meta("selected", "False") == "True":
            self.GetToolsPane().SetBackgroundColour(self._hicolor)
        else:
            self.GetToolsPane().SetBackgroundColour(self.GetBackgroundColour())
        self.Refresh()

    # -----------------------------------------------------------------------

    def is_selected(self):
        """Return True is this file is selected."""
        return self.IsExpanded()

    # -----------------------------------------------------------------------

    def get_tiernames(self):
        """Return the list of all tier names."""
        return [tier.get_name() for tier in self._object.get_tier_list()]

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        """Return the name of the selected tier or None."""
        return self.GetPane().get_selected_tiername()

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, tier_name):
        """Set the selected tier."""
        self.GetPane().set_selected_tiername(tier_name)

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        """Return the index of the selected ann or -1."""
        return self.GetPane().get_selected_ann()

    # -----------------------------------------------------------------------

    def set_selected_ann(self, idx):
        """Set the index of the selected ann or -1."""
        return self.GetPane().set_selected_ann(idx)

    # -----------------------------------------------------------------------

    def update_ann(self, idx):
        """An annotation was modified."""
        self._dirty = True
        return self.GetPane().update_ann(idx)

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        """An annotation was deleted."""
        self._dirty = True
        return self.GetPane().delete_ann(idx)

    # -----------------------------------------------------------------------

    def create_ann(self, idx):
        """An annotation was created."""
        self._dirty = True
        return self.GetPane().create_ann(idx)

    # -----------------------------------------------------------------------

    def set_draw_period(self, start, end):
        """Fix the time period to display.

        :param start: (int)
        :param end: (int) Time in milliseconds

        """
        self.GetPane().SetDrawPeriod(start, end)

    # -----------------------------------------------------------------------

    def get_selected_period(self):
        """Return the time period of the currently selected annotation.

        :return: (int, int) Start and end values in milliseconds

        """
        idx = self.GetPane().get_selected_ann()
        if idx == -1:
            return 0, 0

        return self.GetPane().get_selected_period()

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def get_object(self):
        """Return the object created from the opened file.

        :return: (sppasTranscription)

        """
        return self._object

    # -----------------------------------------------------------------------

    def load_text(self):
        """Override. Load filename in a sppasBaseIO.

        Add the appropriate metadata.
        The tiers, medias and controlled vocab lists are collapsed if empty.

        :raises: IOExtensionError

        """
        parser = sppasRW(self._filename)
        self._object = parser.read()

    # -----------------------------------------------------------------------

    def save(self, filename=None):
        """Save the displayed transcription into a file.

        :param filename: (str) To be used to "save as..."

        """
        parser = None
        if filename is None and self._dirty is True:
            # the writer will increase the file version
            parser = sppasRW(self._filename)
            self._dirty = False
        if filename is not None:
            parser = sppasRW(filename)

        if parser is not None:
            parser.write(self._object)
            return True
        return False

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("save")
        self.AddButton("close")

        self._create_child_panel()
        self.Expand()

    # -----------------------------------------------------------------------

    def _create_child_panel(self):
        self.SetPane(TrsTimePanel(self, self._object))

    # -----------------------------------------------------------------------

    def _process_view_event(self, event):
        """Process a click on a tier.

        :param event: (wx.Event)

        """
        evt = ViewEvent(action="tier_selected", value=self._filename)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------


class TrsTimePanel(sppasPanel):
    """Display a transcription in a timeline view.

    """

    def __init__(self, parent, transcription, name="trs_panel"):
        super(TrsTimePanel, self).__init__(parent, name=name)
        self.__trs = transcription
        self._create_content()

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                return child.get_tiername()
        return None

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, tier_name=None):
        """Set the selected tier.

        :param tier_name: (str)

        """
        if tier_name is not None:
            assert tier_name in [t.get_name() for t in self.__trs]

        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.SetBorderColour(self.GetForegroundColour())
                child.SetSelected(False)
                child.Refresh()
            if child.get_tiername() == tier_name:
                child.SetBorderColour(wx.RED)
                child.SetSelected(True)
                child.Refresh()

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                return child.get_selected_ann()

        return -1

    # -----------------------------------------------------------------------

    def get_selected_period(self):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                period = child.get_selected_localization()
                start = int(period[0] * 1000.)
                end = int(period[1] * 1000.)
                return start, end

        return 0, 0

    # -----------------------------------------------------------------------

    def set_selected_ann(self, idx):
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.set_selected_ann(idx)

    # -----------------------------------------------------------------------

    def update_ann(self, idx):
        """An annotation was modified."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.update_ann(idx)

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        """An annotation was deleted."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.delete_ann(idx)

    # -----------------------------------------------------------------------

    def create_ann(self, idx):
        """An annotation was created."""
        for child in self.GetChildren():
            if child.IsSelected() is True:
                child.create_ann(idx)

    # -----------------------------------------------------------------------

    def SetDrawPeriod(self, start, end):
        """Period to display (in milliseconds)."""
        for child in self.GetChildren():
            child.SetDrawPeriod(
                float(start) / 1000.,
                float(end) / 1000.)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for tier in self.__trs:
            tier_ctrl = sppasTierWindow(self, data=tier)
            tier_ctrl.SetMinSize(wx.Size(-1, sppasPanel.fix_size(24)))
            tier_ctrl.Bind(wx.EVT_COMMAND_LEFT_CLICK, self._process_data_selected)

            sizer.Add(tier_ctrl, 0, wx.EXPAND, 0)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a EVT_VIEW event to the listener (if any)."""
        evt = ViewEvent(action="tier_selected")
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_data_selected(self, event):
        """Process a click on a tier.

        :param event: (wx.Event)

        """
        tier = event.GetObj()
        self.set_selected_tiername(tier.get_name())
        self.Notify()

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        p1 = MediaTimeViewPanel(self,
             filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
        # p1.GetPane().media_play()

        p2 = TrsTimeViewPanel(self,
             filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.TextGrid"))

        p3 = TrsTimeViewPanel(self,
                              filename=os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra"))

        p4 = MediaTimeViewPanel(self,
            #filename="/E/Videos/Monsters_Inc.For_the_Birds.mpg")
            filename="C:\\Users\\bigi\\Videos\\agay_2.mp4")

        p3.set_draw_period(2300, 3500)
        p3.set_selected_tiername("PhonAlign")

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND)
        s.Add(p2, 0, wx.EXPAND)
        s.Add(p3, 0, wx.EXPAND)
        s.Add(p4, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Bind(MediaEvents.EVT_MEDIA_ACTION, self._process_media_action)

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
                event.GetEventObject().get_object().Play()

        event.Skip()
