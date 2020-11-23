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

    ui.phoenix.page_analyze.medialist.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import wx.dataview
import wx.lib.newevent

from sppas.src.config import paths

import sppas.src.audiodata.aio

from ..views import AudioRoamer
from ..windows.text import sppasStaticText
from ..windows.panels import sppasPanel
from ..windows.panels import sppasCollapsiblePanel

from .basefilelist import sppasFileSummaryPanel

# ---------------------------------------------------------------------------


LABEL_LIST = {"duration": "Duration (seconds): ",
              "framerate": "Frame rate (Hz): ",
              "sampwidth": "Sample width (bits): ",
              "channels": "Channels: "}

NO_INFO_LABEL = " ... "

ERROR_COLOUR = wx.Colour(220, 30, 10, 128)     # red
WARNING_COLOUR = wx.Colour(240, 190, 45, 128)  # orange

# ---------------------------------------------------------------------------


class AudioSummaryPanel(sppasFileSummaryPanel):
    """A panel to display the content of an audio as a list.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Can not be constructed if the file is not supported and/or if an error
    occurred when opening or reading.

    """

    def __init__(self, parent, filename, name="listview-panel"):
        # will raise an exception if the audio file is not supported.
        self._values = dict()
        self._labels = dict()
        self._audio = sppas.src.audiodata.aio.open(filename)

        # the audio sounds good, we can create this panel.
        super(AudioSummaryPanel, self).__init__(parent, filename, name)

        # Set values of the summary
        self.fix_values()
        if self._audio.get_duration() > 300.:
            self.FindWindow("window-more").Enable(False)
            wx.LogWarning("Audio Roamer is disabled: the audio file {} "
                          "is too long.".format(filename))

        # Finally, display the summary
        self.Expand()
        self._rgb1 = (190, 205, 250)
        self._rgb2 = (210, 215, 255)
        self.SetRandomBackgroundColour()

        self.Bind(wx.EVT_BUTTON, self.__process_tool_event)

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Set the foreground colour except for specific values."""
        sppasCollapsiblePanel.SetForegroundColour(self, colour)
        if self._audio is not None and len(self._values) > 0:
            self.fix_values()
            self.Refresh()

    # -----------------------------------------------------------------------

    def fix_values(self):
        """Display information of a sound file. """
        self.__fix_duration()
        self.__fix_framerate()
        self.__fix_sampwidth()
        self.__fix_nchannels()

    # -----------------------------------------------------------------------

    def cancel_values(self):
        """Reset displayed information. """
        for v in self._values:
            v.ChangeValue(NO_INFO_LABEL)
            v.SetForegroundColour(self.GetForegroundColour())
            self.Refresh()

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def Destroy(self):
        """Close the audio and destroy the wx object."""
        self._audio.close()
        wx.Window.Destroy(self)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        self.AddButton("window-more", direction=1)
        self.AddButton("close", direction=1)

        child_panel = self.GetPane()
        gbs = wx.GridBagSizer()

        for i, label in enumerate(LABEL_LIST):
            static_tx = sppasStaticText(child_panel, label=LABEL_LIST[label])
            self._labels[label] = static_tx
            gbs.Add(static_tx, (i, 0), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=sppasPanel.fix_size(2))

            # tx = sppasTextCtrl(child_panel, value=NO_INFO_LABEL, style=wx.TE_READONLY | wx.BORDER_NONE)
            tx = sppasStaticText(child_panel, label=NO_INFO_LABEL)
            tx.SetMinSize(wx.Size(sppasPanel.fix_size(200), -1))
            self._values[label] = tx
            gbs.Add(tx, (i, 1), flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=sppasPanel.fix_size(2))

        gbs.AddGrowableCol(1)
        child_panel.SetSizer(gbs)

    # -----------------------------------------------------------------------

    def __process_tool_event(self, event):
        """Process any kind of event.

        :param event: (wx.Event)

        """
        event_obj = event.GetButtonObj()
        name = event_obj.GetName()

        if name == "window-more":
            AudioRoamer(self, self._audio)

        elif name == "close":
            self.notify("close")

        else:
            event.Skip()

    # -----------------------------------------------------------------------
    # Private method to get the summary information
    # -----------------------------------------------------------------------

    def __fix_duration(self):
        duration = self._audio.get_duration()
        self._values["duration"].SetLabel(str(round(float(duration), 3)))
        self._values["duration"].SetForegroundColour(self.GetForegroundColour())

    def __fix_framerate(self):
        framerate = self._audio.get_framerate()
        self._values["framerate"].SetLabel(str(framerate))
        if framerate < 16000:
            self._values["framerate"].SetForegroundColour(ERROR_COLOUR)
        elif framerate in [16000, 32000, 48000]:
            self._values["framerate"].SetForegroundColour(self.GetForegroundColour())
        else:
            self._values["framerate"].SetForegroundColour(WARNING_COLOUR)

    def __fix_sampwidth(self):
        sampwidth = self._audio.get_sampwidth()
        # self._values["sampwidth"].ChangeValue(str(sampwidth*8))
        self._values["sampwidth"].SetLabel(str(sampwidth*8))
        if sampwidth == 1:
            self._values["sampwidth"].SetForegroundColour(ERROR_COLOUR)
        elif sampwidth == 2:
            self._values["sampwidth"].SetForegroundColour(self.GetForegroundColour())
        else:
            self._values["sampwidth"].SetForegroundColour(WARNING_COLOUR)

    def __fix_nchannels(self):
        nchannels = self._audio.get_nchannels()
        # self._values["channels"].ChangeValue(str(nchannels))
        self._values["channels"].SetLabel(str(nchannels))
        if nchannels == 1:
            self._values["channels"].SetForegroundColour(self.GetForegroundColour())
        else:
            self._values["channels"].SetForegroundColour(ERROR_COLOUR)

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test Media Summary Panel")

        f1 = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")
        f2 = os.path.join(paths.samples, "samples-eng", "oriana1.wav")
        p1 = AudioSummaryPanel(self, f1)
        p2 = AudioSummaryPanel(self, f2)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p1)
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, p2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(p2, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        panel.SetFocus()
        self.Layout()
