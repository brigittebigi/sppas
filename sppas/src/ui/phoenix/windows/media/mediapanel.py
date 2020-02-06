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

    src.ui.phoenix.windows.media.mediapanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A sppasMedia embedded into a sppasCollapsiblePanel.

"""

import os
import time
import wx
import wx.media
import wx.lib.newevent

from sppas import paths
from ..panel import sppasCollapsiblePanel, sppasScrolledPanel
from .mediactrl import sppasMedia
from .mediactrl import MediaType

# ---------------------------------------------------------------------------


class sppasMediaPanel(sppasCollapsiblePanel):

    # List of accepted percentages of zooming
    ZOOMS = (10, 25, 50, 75, 100, 125, 150, 200, 250, 300)

    def __init__(self, parent, id=wx.ID_ANY, filename="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="CollapsiblePane"):
        """Create a CollapsiblePanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param id: (int) window identifier or -1
        :param filename: (string) Name of the media file
        :param pos: (wx.Pos) the control position
        :param size: (wx.Size) the control size
        :param style: (int) the underlying window style
        :param name: (str) the widget name.

        The parent can Bind the wx.EVT_COLLAPSIBLEPANE_CHANGED.

        """
        media_type = sppasMedia.ExpectedMediaType(filename)
        if media_type == MediaType().unknown:
            raise TypeError("File {:s} is of an unknown type "
                            "(no audio nor video).".format(filename))

        super(sppasMediaPanel, self).__init__(
            parent, id, filename, pos, size, style, name)
        self._mt = media_type

        self.AddButton("zoom_in")
        self.AddButton("zoom_out")
        self.AddButton("zoom")
        self.AddButton("close")
        mc = sppasMedia(self)
        self.SetPane(mc)
        self.media_zoom(0)  # 100% zoom = initial size
        # self.Bind(sppasMedia.EVT_MEDIA_ACTION, self._process_action)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        # Load the media
        if mc.Load(filename) is True:
            # Under Windows, the Load methods always return True,
            # even if the media is not loaded...
            time.sleep(0.1)
            self.__set_media_properties(mc)
        else:
            self.Collapse()
            mc.Bind(wx.media.EVT_MEDIA_LOADED, self.__process_media_loaded)

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
            idx_zoom = sppasMediaPanel.ZOOMS.index(self._child_panel.GetZoom())
            if direction < 0:
                new_idx_zoom = max(0, idx_zoom-1)
            else:
                new_idx_zoom = min(len(sppasMediaPanel.ZOOMS)-1, idx_zoom+1)
            self._child_panel.SetZoom(sppasMediaPanel.ZOOMS[new_idx_zoom])

        size = self.DoGetBestSize()
        self.SetSize(size)
        self.GetParent().Layout()

    # -----------------------------------------------------------------------

    def media_remove(self, obj):
        """Remove the media we clicked on the collapsible panel close button."""
        self._child_panel.Destroy()
        self.Destroy()

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent)

        p1 = sppasMediaPanel(self,
             filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
        p1.GetPane().Play()

        p2 = sppasMediaPanel(self,
             filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))

        p3 = sppasMediaPanel(self,
            filename=os.path.join(paths.samples, "samples-fra", "F_F_C006-P6.wav"))

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND)
        s.Add(p2, 0, wx.EXPAND)
        s.Add(p3, 0, wx.EXPAND)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

