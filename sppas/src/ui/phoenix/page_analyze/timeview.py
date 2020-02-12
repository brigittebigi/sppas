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

from sppas import paths
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasRW
import sppas.src.audiodata.aio

from ..windows import sppasScrolledPanel
from ..windows import sppasCollapsiblePanel
from .baseview import sppasBaseViewPanel
from ..windows import sppasMediaPanel
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
        return self.GetPane().GetOffsetPeriod()[0]

    def media_offset_get_end(self):
        """Return the end position of the current period (milliseconds)."""
        return self.GetPane().GetOffsetPeriod()[1]

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

    def get_selected_tier(self):
        """Return the name of the selected tier or None."""
        return self.GetPane().get_selected_tier()

    # -----------------------------------------------------------------------

    def set_selected_tier(self, tier_name):
        """Set the selected tier."""
        self.GetPane().set_selected_tier(tier_name)

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
        wx.LogDebug("... COLLAPSIBLE PANE RECEIVED A TIER SELECTED EVENT ...")
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
            if child.GetTierName() != self.__selected:
                child.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def get_selected_tier(self):
        return self.__selected

    # -----------------------------------------------------------------------

    def set_selected_tier(self, tier_name=None):
        """Set the selected tier.

        :param tier_name: (str)

        """
        if tier_name is not None:
            assert tier_name in [t.get_name() for t in self.__trs]

        for child in self.GetChildren():
            if child.GetTierName() == tier_name:
                child.SetForegroundColour(wx.RED)
                child.SetBorderColour(wx.RED)
                child.Refresh()
            elif child.GetTierName() == self.__selected:
                child.SetForegroundColour(self.GetForegroundColour())
                child.SetBorderColour(self.GetForegroundColour())
                child.Refresh()
        self.__selected = tier_name

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
                    self.set_selected_tier(tier.get_name())
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

    def GetTierName(self):
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
        p1.GetPane().Play()

        p2 = TrsTimeViewPanel(self,
             filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.TextGrid"))

        p3 = TrsTimeViewPanel(self,
                              filename=os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra"))

        p4 = MediaTimeViewPanel(self,
            filename=os.path.join(paths.samples, "samples-fra", "F_F_C006-P6.wav"))

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND)
        s.Add(p2, 0, wx.EXPAND)
        s.Add(p3, 0, wx.EXPAND)
        s.Add(p4, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

