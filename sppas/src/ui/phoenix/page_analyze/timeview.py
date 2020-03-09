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
from sppas.src.anndata import sppasRW
import sppas.src.audiodata.aio

from ..windows import sppasScrolledPanel
from ..windows import sppasCollapsiblePanel
from .baseview import sppasBaseViewPanel
# from ..windows import sppasMediaPanel
from ..windows import sppasMediaCtrl
from ..windows import sppasPanel
from ..windows import MediaType
from ..windows import MediaEvents
from ..main_events import ViewEvent, EVT_VIEW

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

    The object this class is a sppasMediaCtrl.
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
        media = event.GetEventObject()
        media_size = media.DoGetBestSize()
        media.SetSize(media_size)
        self.Expand()

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
        """"""
        self._dirty = True
        return self.GetPane().update_ann(idx)

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        """"""
        self._dirty = True
        return self.GetPane().delete_ann(idx)

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

        :raises: AioFileExtensionError

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
        self.__selected = None
        self._create_content()
        self.Bind(EVT_VIEW, self._process_view_event)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for child in self.GetChildren():
            if child.get_tiername() != self.__selected:
                child.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def get_selected_tiername(self):
        return self.__selected

    # -----------------------------------------------------------------------

    def set_selected_tiername(self, tier_name=None):
        """Set the selected tier.

        :param tier_name: (str)

        """
        if tier_name is not None:
            assert tier_name in [t.get_name() for t in self.__trs]

        for child in self.GetChildren():
            if child.get_tiername() == tier_name:
                child.SetForegroundColour(wx.RED)
                child.SetBorderColour(wx.RED)
                child.Refresh()
            elif child.get_tiername() == self.__selected:
                child.SetForegroundColour(self.GetForegroundColour())
                child.SetBorderColour(self.GetForegroundColour())
                child.Refresh()
        self.__selected = tier_name

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        if self.__selected is None:
            return -1

        for child in self.GetChildren():
            if child.get_tiername() == self.__selected:
                return child.get_selected_ann()

        return -1

    # -----------------------------------------------------------------------

    def get_selected_period(self):
        if self.__selected is None:
            return 0, 0

        for child in self.GetChildren():
            if child.get_tiername() == self.__selected:
                period = child.get_selected_localization()
                start = int(period[0] * 1000.)
                end = int(period[1] * 1000.)
                return start, end

        return 0, 0

    # -----------------------------------------------------------------------

    def set_selected_ann(self, idx):
        for child in self.GetChildren():
            if child.get_tiername() == self.__selected:
                child.set_selected_ann(idx)

    # -----------------------------------------------------------------------

    def update_ann(self, idx):
        for child in self.GetChildren():
            if child.get_tiername() == self.__selected:
                child.update_ann(idx)

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        for child in self.GetChildren():
            if child.get_tiername() == self.__selected:
                child.delete_ann(idx)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for tier in self.__trs:
            tier_ctrl = TierTimeCtrl(self, tier)
            sizer.Add(tier_ctrl, 0, wx.EXPAND, 0)
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a EVT_VIEW event to the listener (if any)."""
        evt = ViewEvent(action="tier_selected")
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def _process_view_event(self, event):
        """Process a click on a tier.

        :param event: (wx.Event)

        """
        wx.LogDebug("... TIER SELECTED EVENT RECEIVED ...")
        try:
            if event.action == "tier_selected":
                tier = event.value
                if tier.get_name() != self.__selected:
                    self.set_selected_tiername(tier.get_name())
                    self.Notify()
        except AttributeError:
            return

# ---------------------------------------------------------------------------


class TierTimeCtrl(wx.Window):

    def __init__(self, parent, tier):
        super(TierTimeCtrl, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
            name=tier.get_name()+"_ctrl")

        self.__tier = tier
        self.__ann_idx = -1

        # Background
        self._bgcolor = None
        self._fgcolor = None
        self._bordercolor = wx.Colour(128, 128, 128, 128)
        self._borderwidth = 1

        # Setup Initial Size
        # self.InheritAttributes()
        self.SetInitialSize()

        # Bind the events related to our window
        self.Bind(wx.EVT_PAINT, lambda evt: self.Draw())
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

    # -----------------------------------------------------------------------

    def get_selected_ann(self):
        return self.__ann_idx

    # -----------------------------------------------------------------------

    def get_selected_localization(self):
        """Return begin and end time value (float)."""
        if self.__ann_idx == -1:
            return 0, 0
        ann = self.__tier[self.__ann_idx]

        start_point = ann.get_lowest_localization()
        start = start_point.get_midpoint()
        r = start_point.get_radius()
        if r is not None:
            start -= r
        end_point = ann.get_highest_localization()
        end = end_point.get_midpoint()
        r = end_point.get_radius()
        if r is not None:
            end += r

        return start, end

    # -----------------------------------------------------------------------

    def set_selected_ann(self, idx):
        logging.debug("annotation selected : {}".format(idx))
        self.__ann_idx = idx
        self.Refresh()

    # -----------------------------------------------------------------------

    def update_ann(self, idx):
        logging.debug("annotation modified : {}".format(idx))
        self.Refresh()

    # -----------------------------------------------------------------------

    def delete_ann(self, idx):
        logging.debug("annotation deleted : {}".format(idx))
        self.Refresh()

    # -----------------------------------------------------------------------

    def get_tiername(self):
        return self.__tier.get_name()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override. Apply bg colour instead of transparency.

        :param colour: (wx.Colour) None to be transparent

        """
        self._bgcolor = colour

    # -----------------------------------------------------------------------

    def SetBorderColour(self, colour):
        """

        :param colour: (wx.Colour)

        """
        self._bordercolor = colour

    # -----------------------------------------------------------------------

    def GetDefaultAttributes(self):
        """Overridden base class virtual.

        :returns: an instance of wx.VisualAttributes.

        """
        return self.GetParent().GetClassDefaultAttributes()

    # -----------------------------------------------------------------------

    def AcceptsFocusFromKeyboard(self):
        """Can this window be given focus by tab key?"""
        return False

    # -----------------------------------------------------------------------

    def ShouldInheritColours(self):
        """Overridden base class virtual.

        """
        return True

    # -----------------------------------------------------------------------

    def GetHighlightedBackgroundColour(self):
        if self._bgcolor is not None:
            color = self._bgcolor
        else:
            color = self.GetParent().GetBackgroundColour()
        r, g, b, a = color.Red(), color.Green(), color.Blue(), color.Alpha()

        delta = 15
        if (r + g + b) > 384:
            return wx.Colour(r, g, b, a).ChangeLightness(100 - delta)
        return wx.Colour(r, g, b, a).ChangeLightness(100 + delta)

    # -----------------------------------------------------------------------

    def OnErase(self, evt):
        """Trap the erase event to keep the background transparent on windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a wx.SizeEvent event to be processed.

        """
        event.Skip()
        self.Refresh()

    # -----------------------------------------------------------------------

    def OnMouseEvents(self, event):
        """Handle the wx.EVT_MOUSE_EVENTS event.

        Do not accept the event if the button is disabled.

        """
        if event.LeftUp():
            self.Notify()

    # -----------------------------------------------------------------------
    # Design
    # -----------------------------------------------------------------------

    def SetInitialSize(self, size=wx.DefaultSize):
        mw = sppasPanel.fix_size(256)
        mh = sppasPanel.fix_size(24)
        self.SetMinSize(wx.Size(mw, mh))
        if size is None:
            size = wx.DefaultSize

        (w, h) = size
        if w < mw:
            w = mw
        if h < mh:
            h = mh

        wx.Window.SetInitialSize(self, wx.Size(w, h))

    SetBestSize = SetInitialSize

    # -----------------------------------------------------------------------

    def Notify(self):
        """Sends a EVT_EVENT event to the listener (if any)."""
        evt = ViewEvent(action="tier_selected", value=self.__tier)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

    # -----------------------------------------------------------------------

    def GetBackgroundBrush(self, dc):
        """Get the brush for drawing the background of the button.

        :returns: (wx.Brush)

        """
        if self._bgcolor is None:
            if wx.Platform == '__WXMAC__':
                return wx.TRANSPARENT_BRUSH

            color = self.GetParent().GetBackgroundColour()
            return wx.Brush(color, wx.BRUSHSTYLE_TRANSPARENT)
        else:
            return wx.Brush(self._bgcolor, wx.SOLID)

    # -----------------------------------------------------------------------
    # Draw methods (private)
    # -----------------------------------------------------------------------

    def PrepareDraw(self):
        """Prepare the DC to draw the tier.

        :returns: (tuple) dc, gc

        """
        # Create the Graphic Context
        dc = wx.AutoBufferedPaintDCFactory(self)
        gc = wx.GCDC(dc)

        # In any case, the brush is transparent
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.SetBackgroundMode(wx.TRANSPARENT)

        # Font
        gc.SetFont(self.GetFont())
        dc.SetFont(self.GetFont())

        return dc, gc

    # -----------------------------------------------------------------------

    def Draw(self):
        """Draw the tier after the WX_EVT_PAINT event.

        """
        # Get the actual client size of ourselves
        width, height = self.GetClientSize()
        if not width or not height:
            # Nothing to do, we still don't have dimensions!
            return

        dc, gc = self.PrepareDraw()
        self._DrawBackground(dc, gc)

        x, y, w, h = self.GetClientRect()
        bd = max(self._borderwidth, 2)
        x += bd
        y += bd
        w -= (2 * bd)
        h -= (2 * bd)

        if w >= 4 and h >= 4:
            self._DrawContent(dc, gc, x, y, w, h)

        if self._borderwidth > 0:
            self._DrawBorder(dc, gc)

    # -----------------------------------------------------------------------

    def _DrawBorder(self, dc, gc):
        w, h = self.GetClientSize()

        pen = wx.Pen(self._bordercolor, 1, wx.SOLID)
        dc.SetPen(pen)

        # draw the upper left sides
        for i in range(self._borderwidth):
            # upper
            dc.DrawLine(0, i, w - i, i)
            # left
            dc.DrawLine(i, 0, i, h - i)

        # draw the lower right sides
        for i in range(self._borderwidth):
            dc.DrawLine(i, h - i - 1, w + 1, h - i - 1)
            dc.DrawLine(w - i - 1, i, w - i - 1, h)

    # -----------------------------------------------------------------------

    def _DrawContent(self, dc, gc, x, y, w, h):
        tier_name = self.__tier.get_name()
        tw, th = self.get_text_extend(dc, gc, tier_name)
        self.__draw_label(dc, gc, x, y + ((h - th) // 2), tier_name)
        self.__draw_label(dc, gc, x + 200, y + ((h - th) // 2), str(len(self.__tier))+" annotations")
        if self.__ann_idx > -1:
            self.__draw_label(dc, gc, x + 400, y + ((h - th) // 2),
                             "(-- {:d} -- is selected)".format(self.__ann_idx+1))

    # -----------------------------------------------------------------------

    def _DrawBackground(self, dc, gc):
        w, h = self.GetClientSize()

        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(brush)
        dc.DrawRectangle(self._borderwidth,
                         self._borderwidth,
                         w - (2 * self._borderwidth),
                         h - (2 * self._borderwidth))

    # -----------------------------------------------------------------------

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def __draw_label(self, dc, gc, x, y, label):
        font = self.GetParent().GetFont()
        gc.SetFont(font)
        dc.SetFont(font)
        if wx.Platform == '__WXGTK__':
            dc.SetTextForeground(self.GetForegroundColour())
            dc.DrawText(label, x, y)
        else:
            gc.SetTextForeground(self.GetForegroundColour())
            gc.DrawText(label, x, y)

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
