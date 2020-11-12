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

    ui.phoenix.page_editor.timeline.mediaview_risepanel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.lib

from sppas.src.config import paths

from sppas.src.ui.phoenix.windows import sppasScrolledPanel

from ..editorevent import EVT_TIME_VIEW
from .baseview_risepanel import sppasFileViewPanel
from .audiovista import sppasAudioVista

# ---------------------------------------------------------------------------


class AudioViewPanel(sppasFileViewPanel):
    """A panel to display the content of an audio.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    The object embedded in this class is a sppasAudioVista.

    Events emitted by this class is EVT_TIME_VIEW:
        - action="close" to ask for closing the panel
        - action="media_loaded", value=boolean to inform the file was
        successfully or un-successfully loaded.

    """

    # -----------------------------------------------------------------------
    # List of accepted percentages of zooming
    ZOOMS = (25, 50, 75, 100, 125, 150, 200, 250, 300, 400)

    # -----------------------------------------------------------------------

    def __init__(self, parent, filename, name="audioview_risepanel"):
        """Create an AudioViewPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param filename: (str) The name of the file of the media
        :param name: (str) the widget name.

        """
        # try:
        #     # Before creating the media, check if the file type is supported.
        #     media_type = sppasMediaCtrl.ExpectedMediaType(filename)
        #     if media_type == MediaType().unknown:
        #         raise TypeError("File {:s} is of an unknown type "
        #                         "(no audio nor video).".format(filename))
        # except TypeError:
        #     self.Destroy()
        #     raise

        super(AudioViewPanel, self).__init__(parent, filename, name)
        self._setup_events()
        self.Collapse()
        self.SetBackgroundColour(wx.BLUE)

    # -----------------------------------------------------------------------

    def media_zoom(self, direction):
        """Zoom the child.

        :param direction: (int) -1 to zoom out, +1 to zoom in and 0 to reset
        to the initial size.

        """
        if self.IsExpanded() is False:
            return

        if direction == 0:
            self.GetPane().SetZoom(100)
        else:
            idx_zoom = AudioViewPanel.ZOOMS.index(self.GetPane().GetZoom())
            if direction < 0:
                new_idx_zoom = max(0, idx_zoom-1)
            else:
                new_idx_zoom = min(len(AudioViewPanel.ZOOMS)-1, idx_zoom+1)
            self.GetPane().SetZoom(AudioViewPanel.ZOOMS[new_idx_zoom])

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
        self.AddButton("close")

        mc = sppasAudioVista(self)
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

    # -----------------------------------------------------------------------

    def __process_tool_event(self, event):
        """Process a button event from the tools.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()
        if name == "close":
            self.notify("close")
        else:
            event.Skip()

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="AudioView RisePanel")

        p1 = AudioViewPanel(self, filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav"))
        p3 = AudioViewPanel(self, filename=os.path.join(paths.samples, "samples-fra", "F_F_B003-P9.wav"))

        # p3.GetPane().SetDrawPeriod(2.300, 3.500)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND | wx.TOP, 2)
        s.Add(p3, 0, wx.EXPAND | wx.TOP, 2)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
