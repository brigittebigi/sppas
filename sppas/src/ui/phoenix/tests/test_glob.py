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

    src.ui.phoenix.tests.test_glob.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import logging

from sppas.src.ui.cfg import sppasAppConfig
from sppas.src.ui.phoenix.main_settings import WxAppSettings

# Tested files are the ones with a TestPanel class:
import sppas.src.ui.phoenix.windows.toolbar as toolbar
import sppas.src.ui.phoenix.windows.line as line
import sppas.src.ui.phoenix.windows.button as button
import sppas.src.ui.phoenix.windows.panel as panel
import sppas.src.ui.phoenix.panels.option as option
import sppas.src.ui.phoenix.page_files.filesmanager as filesmanager
#import sppas.src.ui.phoenix.page_files.filestreectrl as filestreectrl
import sppas.src.ui.phoenix.page_files.refsmanager as refsmanager
import sppas.src.ui.phoenix.page_files.wksmanager as wksmanager
import sppas.src.ui.phoenix.page_analyze.anz_tabs as anz_tabs
import sppas.src.ui.phoenix.page_analyze.textview as textview
import sppas.src.ui.phoenix.page_analyze.baseview as baseview
import sppas.src.ui.phoenix.windows.buttonbox as buttonbox

# ----------------------------------------------------------------------------
# Panel to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(
            self,
            parent,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)

        self.SetBackgroundColour(wx.Colour(100, 100, 100))
        self.SetForegroundColour(wx.Colour(0, 0, 10))

        # Make the bunch of test panels for the choice book
        # self.AddPage(filestreectrl.TestPanel(self), "AGW Files tree ctrl")
        self.AddPage(panel.TestPanel(self), "Panels")
        self.AddPage(filesmanager.TestPanel(self), "Dataview Files manager")
        self.AddPage(textview.TestPanel(self), "Text view")
        self.AddPage(baseview.TestPanel(self), "Base view")
        self.AddPage(anz_tabs.TestPanel(self), "Tabs analyze")
        self.AddPage(refsmanager.TestPanel(self), "References manager")
        self.AddPage(wksmanager.TestPanel(self), "Workspaces manager")
        self.AddPage(option.TestPanel(self), "Configure options")
        self.AddPage(toolbar.TestPanel(self), "Toolbar")
        self.AddPage(buttonbox.TestPanel(self), "ButtonBox")
        self.AddPage(button.TestPanel(self), "Buttons")
        self.AddPage(line.TestPanel(self), "Lines")

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(wx.EVT_KEY_DOWN, self._process_key_event)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        # logging.debug('Test panel received the key event {:d}'.format(key_code))

        # Keeps on going the event to the current page of the book.
        event.Skip()

    # -----------------------------------------------------------------------

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

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

        # create the frame
        frm = wx.Frame(None, title='Test frame', size=wx.Size(800, 600))
        frm.SetMinSize(wx.Size(640, 480))
        self.SetTopWindow(frm)

        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.__cfg = sppasAppConfig()
        self.settings = WxAppSettings()
        self.setup_debug_logging()

        # create a panel in the frame
        sizer = wx.BoxSizer()
        sizer.Add(TestPanel(frm), 1, wx.EXPAND, 0)
        frm.SetSizer(sizer)

        # show result
        frm.Layout()
        frm.Show()

    @staticmethod
    def setup_debug_logging():
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logging.debug('Logging set to DEBUG level')

# ---------------------------------------------------------------------------


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
