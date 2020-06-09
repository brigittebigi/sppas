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

    ui.phoenix.windows.progress.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import time

from sppas.src.config import sppasAppConfig
from sppas.src.ui.progress import sppasBaseProgress

# ---------------------------------------------------------------------------


class sppasProgressDialog(wx.GenericProgressDialog, sppasBaseProgress):
    """Customized progress dialog.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create a dialog with a progress for the annotations."""
        super(sppasProgressDialog, self).__init__(
            title="In progress...",
            message="",
            style=wx.PD_SMOOTH)

        # Fix frame properties
        self._init_infos()

        # To fade-out the opacity
        self.opacity_out = 255
        self.timer2 = None

        self.SetAutoLayout(True)
        self.Layout()

    # -----------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        self.SetName("progress_dialog")
        self.SetRange(101)

        # Fix minimum frame size
        self.SetMinSize(wx.Size(self.fix_size(256),
                                self.fix_size(128)))

        # colors & font
        try:
            settings = wx.GetApp().settings
            self.SetBackgroundColour(settings.bg_color)
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
            for c in self.GetChildren():
                c.SetBackgroundColour(settings.bg_color)
                c.SetForegroundColour(settings.fg_color)
                c.SetFont(settings.text_font)
        except AttributeError:
            pass

    # -----------------------------------------------------------------------
    # Fade-in at start-up and Fade-out at close
    # -----------------------------------------------------------------------

    @staticmethod
    def fix_size(value):
        """Return a proportional size value.

        :param value: (int)
        :returns: (int)

        """
        try:
            obj_size = int(float(value) * wx.GetApp().settings.size_coeff)
        except AttributeError:
            obj_size = int(value)
        return obj_size

    # -----------------------------------------------------------------------

    def set_header(self, header):
        """Overridden. Set a new progress header text.

        :param header: (str) new progress header text.

        """
        self.SetTitle(header)
        self.Refresh()

    # -----------------------------------------------------------------------

    def update(self, percent=None, message=None):
        """Overridden. Update the progress box.

        :param percent: (float) progress bar value as percentage or fraction
        :param message: (str) progress bar text

        """
        if percent is not None:
            fraction = float(percent)
            # convert fraction to a percentage (if necessary)
            if fraction < 1:
                fraction = int(fraction * 100.)
            if fraction > 100:
                fraction = 100
        else:
            fraction = self.GetValue()

        if message is None:
            message = self.GetMessage()

        self.Update(fraction, message)
        wx.MilliSleep(50)

    # -----------------------------------------------------------------------

    def close(self):
        """Close the progress box."""
        self.timer2 = wx.Timer(self, -1)
        self.timer2.Start(1)
        self.Bind(wx.EVT_TIMER, self.__alpha_cycle_out, self.timer2)

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    def __alpha_cycle_out(self, *args):
        """Fade-out opacity of the dialog."""
        self.opacity_out -= 5

        if self.opacity_out > 0:
            self.SetTransparent(self.opacity_out)
        else:
            self.opacity_out = 0
            self.timer2.Stop()
            self.timer2 = None
            wx.CallAfter(self.Destroy)

# ----------------------------------------------------------------------------
# App to test
# ----------------------------------------------------------------------------


class TestApp(wx.App):

    def __init__(self):
        """Create a customized application."""
        # ensure the parent's __init__ is called with the args we want
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.__cfg = sppasAppConfig()

        # create the frame
        self.frm = wx.Frame(None, title='Progress test', size=(256, 128), name="main")
        self.SetTopWindow(self.frm)

        # create a panel in the frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.Button(self.frm, label="start"), 1, wx.EXPAND, 0)
        self.frm.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self._on_start)

        # show result
        self.frm.Show(True)


    def _on_start(self, event):

        self.progress = sppasProgressDialog()
        self.progress.set_new()
        self.progress.set_header("Annotation number 1")
        self.progress.set_fraction(0)
        self.progress.set_text("file one")

        time.sleep(1)
        self.progress.set_fraction(34)
        self.progress.set_text("file two")
        time.sleep(1)
        self.progress.set_fraction(70)
        self.progress.set_text("file three")
        time.sleep(1)
        self.progress.set_fraction(100)

        self.progress.set_new()
        self.progress.set_header("Another annotation")
        self.progress.set_fraction(0)
        self.progress.set_text("one file")
        time.sleep(1)
        self.progress.set_fraction(50)
        self.progress.set_text("two files")
        time.sleep(1)
        self.progress.set_fraction(100)

        self.progress.close()

# ----------------------------------------------------------------------------


if __name__ == "__main__":
    app = TestApp()
    app.MainLoop()
