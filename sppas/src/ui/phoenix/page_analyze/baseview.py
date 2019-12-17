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

    ui.phoenix.page_analyze.baseview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from ..windows import sppasCollapsiblePanel
from ..main_events import ViewEvent


# ----------------------------------------------------------------------------


class sppasBaseViewPanel(sppasCollapsiblePanel):
    """Panel to display the content of a file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, filename, name="baseview"):

        # We wont create this panel if the file can't be loaded...
        self._dirty = False
        self._filename = filename
        if filename is not None:
            # The file this panel is displaying is loaded into an object
            self.load_text()

        super(sppasBaseViewPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            label=filename,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # Create the GUI
        self._hicolor = self.GetForegroundColour()
        self._create_content()
        self._setup_events()

        # Look&feel
        self.SetBackgroundColour(self.GetParent().GetBackgroundColour())
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self._dirty

    # ------------------------------------------------------------------------

    def load_text(self):
        """Load the file content into an object.

        Raise an exception if the file is not supported or can't be read.

        """
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def save(self):
        """Save the displayed text into a file."""
        return False

    # ------------------------------------------------------------------------

    def set_filename(self, name):
        """Set a new name to the file.

        :param name: (str) Name of a file. It is not verified.

        """
        self._filename = name
        self.SetLabel(name)
        self._dirty = True

    # ------------------------------------------------------------------------

    def get_object(self):
        """Return the object created from the opened file."""
        return None

    # -----------------------------------------------------------------------

    def get_line_height(self):
        font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))

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
        sppasCollapsiblePanel.SetFont(self, f)
        self.GetPane().SetFont(font)
        self.Layout()

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight something."""
        self._hicolor = color

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        self.AddButton("save")
        self.AddButton("close")
        self._create_child_panel()
        self.Collapse(True)

    # -----------------------------------------------------------------------

    def _create_child_panel(self):
        """Override. Create the child panel."""
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

    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.GetPane().Bind(wx.EVT_SIZE, self.OnSize)

        # The user pressed a key of its keyboard
        # self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

        # The user clicked a button of the collapsible panel toolbar
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of event.

        :param event: (wx.Event)

        """
        wx.LogDebug("{:s} received a button event.".format(self.GetName()))
        event_obj = event.GetButtonObj()
        event_name = event_obj.GetName()

        if event_name == "close":
            self.notify("close")

        elif event_name == "save":
            self.notify("save")

        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def OnSize(self, event):
        """Handle the wx.EVT_SIZE event.

        :param event: a SizeEvent event to be processed.

        """
        # each time our size is changed, the child panel needs a resize.
        self.Layout()

