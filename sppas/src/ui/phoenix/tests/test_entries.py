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

    src.ui.phoenix.views.test_entries.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import logging

from sppas import sppasAppConfig
from sppas.src.ui.phoenix.main_settings import WxAppSettings
from sppas.src.ui.phoenix.windows import sppasPanel
import sppas.src.ui.phoenix.windows.dialogs.entries as entries

# ---------------------------------------------------------------------------
# Tested Panels
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TestPanel-entries")

        btn1 = wx.Button(self,
                         pos=(10, 10), size=(180, 70),
                         label="Choices", name="choices_btn")
        btn2 = wx.Button(self,
                         pos=(200, 10), size=(180, 70),
                         label="Text entry", name="text_btn")

        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "choices_btn":
            dialog = entries.sppasChoiceDialog(
                "A message is here:",
                choices=["apples", "pears", "tomatoes"])
            response = dialog.ShowModal()
            selection = dialog.GetSelection()
            dialog.DestroyFadeOut()
            wx.LogMessage("Response was: {}. Selection was: {}".format(response, selection))

        elif event_name == "text_btn":
            dialog = entries.sppasTextEntryDialog(
                "A message is here:",
                value="default value")
            response = dialog.ShowModal()
            value = dialog.GetValue()
            dialog.Destroy()
            wx.LogMessage("Response was: {}. Text was: {}".format(response, value))

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


