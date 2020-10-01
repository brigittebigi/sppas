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

    ui.phoenix.page_edit.baseview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A base class for any object that displays the content of a file.

"""

import wx
import os

from sppas.src.config import paths

from ..windows.panels import sppasPanel
from ..windows.panels import sppasVerticalRisePanel
from ..main_events import ViewEvent

# ----------------------------------------------------------------------------


class sppasFileViewPanel(sppasVerticalRisePanel):
    """Panel to display the content of a file in a time-view style.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, filename, name="baseview_panel"):
        super(sppasFileViewPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            label=filename,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
            name=name)

        self._dirty = False
        self._filename = filename

        # Create the GUI
        self._create_content()

        # Look&feel
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()

    # ------------------------------------------------------------------------
    # About the file
    # ------------------------------------------------------------------------

    def get_filename(self):
        """Return the filename this panel is displaying."""
        return self._filename

    # ------------------------------------------------------------------------

    def set_filename(self, name):
        """Set a new name to the file.

        :param name: (str) Name of a file. It is not verified.

        """
        self._filename = name
        self.SetLabel(name)
        self._dirty = True

    # ------------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self._dirty

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        # The name of the file is Bold
        f = wx.Font(font.GetPointSize(),
                    font.GetFamily(),
                    font.GetStyle(),
                    wx.FONTWEIGHT_BOLD,
                    font.GetUnderlined(),
                    font.GetFaceName())
        sppasVerticalRisePanel.SetFont(self, f)
        self.GetPane().SetFont(font)
        self.Layout()

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action):
        wx.LogDebug("{:s} notifies its parent {:s} of action {:s}."
                    "".format(self.GetName(), self.GetParent().GetName(), action))
        evt = ViewEvent(action=action)
        evt.SetEventObject(self)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------


class TestPanel(sppasFileViewPanel):

    FILENAME = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, TestPanel.FILENAME,
                                        name="Test BaseView")
        self.Collapse(False)

    def _create_content(self):
        panel = sppasPanel(self)
        st = wx.StaticText(panel, -1, self.get_filename(), pos=(10, 100))
        sz = st.GetBestSize()
        panel.SetSize((sz.width + 20, sz.height + 20))
        self.SetPane(panel)

