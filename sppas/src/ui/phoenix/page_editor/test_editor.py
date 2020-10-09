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

    src.ui.phoenix.page_editor.test_editor.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import logging

from sppas.src.config import sppasAppConfig
from sppas.src.ui.phoenix.main_settings import WxAppSettings

import sppas.src.ui.phoenix.page_editor.timeslider as timeslider
import sppas.src.ui.phoenix.page_editor.annlabels as annlabels
import sppas.src.ui.phoenix.page_editor.tiersbook as tiersbook
import sppas.src.ui.phoenix.page_editor.tiersanns as tiersanns

import sppas.src.ui.phoenix.page_editor.basefileedit as baseview
import sppas.src.ui.phoenix.page_editor.errfileedit as errview
import sppas.src.ui.phoenix.page_editor.mediafileedit as mediaview
import sppas.src.ui.phoenix.page_editor.trsfileedit as trsview
import sppas.src.ui.phoenix.page_editor.filesedit as filesview

import sppas.src.ui.phoenix.page_editor.editorpanel as editorpanel
import sppas.src.ui.phoenix.page_editor.editor as editor

# ----------------------------------------------------------------------------
# Panel to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(
            self,
            parent,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)

        p = timeslider.TestPanel(self)
        self.AddPage(p, p.GetName())

        p = annlabels.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = tiersbook.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = tiersanns.TestPanel(self)
        self.AddPage(p, p.GetName())

        """
        p = baseview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = errview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = mediaview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = trsview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = filesview.TestPanel(self)
        self.AddPage(p, p.GetName())

        p = editorpanel.TestPanel(self)
        self.AddPage(p, p.GetName())

        p = editor.TestPanel(self)
        self.AddPage(p, p.GetName())
        """

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
