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

    src.wxgui.views.processprogress.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx

from sppas.src.ui.wxgui.sp_icons import ANNOTATE_ICON
from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog

# ----------------------------------------------------------------------------


class ProcessProgressDialog(spBaseDialog):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Frame indicating a progress, with 2 text fields.

    """
    def __init__(self, parent, preferences, header_text="Processing..."):
        """Constructor.
        
        :param parent: (wx.Window)
        :param preferences: (Preferences)
        
        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Progress")
        wx.GetApp().SetAppName("progress")

        self.LayoutComponents(self.CreateTitle(ANNOTATE_ICON, header_text),
                              self._create_content())

        self.SetMinSize((420, 180))
        self.Layout()
        self.Show()
        self.Raise()
        self.SetFocus()
        self.Center()
        self.Refresh()

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_content(self):
        # an header text used to print the annotation step
        self.header = wx.StaticText(self, id=-1, label="", size=(400, -1), style=wx.ALIGN_CENTRE)
        # the gauge
        self.gauProgress = wx.Gauge(self, range=100, size=(400, 24))
        # a bottom text used to print the current file name
        self.text = wx.StaticText(self, id=-1, label="", size=(400, -1), style=wx.ALIGN_CENTRE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.header, 0, wx.ALL, 4)
        sizer.Add(self.gauProgress, 0, wx.ALL, 4)
        sizer.Add(self.text, 0, wx.ALL, 4)
        return sizer

    # ------------------------------------------------------------------------

    def set_new(self):
        """Initialize a new progress box."""
        self.set_header("")
        self.set_text("")
        self.set_fraction(0)
        self.Refresh()
        self.Update()

    # ------------------------------------------------------------------------

    def set_fraction(self, fraction):
        """Set a new progress value to the progress bar.

        :param fraction: new progress value

        """
        fraction = float(fraction)
        # convert fraction to a percentage (if necessary)
        if fraction < 1:
            fraction = int(fraction*100)
        self.gauProgress.SetValue(fraction)
        self.Refresh()
        self.Update()

    # ------------------------------------------------------------------------

    def set_text(self, text):
        """Set a new progress text to the progress bar.

        :param text: new progress text

        """
        self.text.SetLabel(text)
        self.Refresh()
        self.Update()

    # ------------------------------------------------------------------------

    def set_header(self, label):
        """Set a new progress label to the progress box.

        :param label: new progress label

        """
        self.header.SetLabel(label)
        self.Refresh()
        self.Update()

    # ------------------------------------------------------------------------

    def update(self, fraction, text):
        """Update the progress box.

        :param text:     progress bar text  (default: None)
        :param fraction: progress bar value (default: 0)

        """
        self.set_text(text)
        self.set_fraction(fraction)
        self.Refresh()
        self.Update()

    # ------------------------------------------------------------------------

    def close(self):
        """Close the progress box."""

        self.Destroy()
