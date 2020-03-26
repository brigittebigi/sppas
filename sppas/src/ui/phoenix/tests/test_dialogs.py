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

    src.ui.phoenix.dialogs.test_dialogs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import logging

from sppas import paths
from sppas.src.plugins import sppasPluginsManager
import sppas.src.audiodata.aio
from sppas.src.anndata import sppasMetaData
from sppas.src.ui.cfg import sppasAppConfig
from sppas.src.ui.phoenix.main_settings import WxAppSettings
from sppas.src.ui.phoenix.windows import sppasPanel

from sppas.src.ui.phoenix.dialogs.audioroamer import AudioRoamer
from sppas.src.ui.phoenix.dialogs.about import About
from sppas.src.ui.phoenix.dialogs.about import AboutPlugin
from sppas.src.ui.phoenix.dialogs.settings import Settings
from sppas.src.ui.phoenix.dialogs.tiersview import TiersView
from sppas.src.ui.phoenix.dialogs.statsview import StatsView
from sppas.src.ui.phoenix.dialogs.metaedit import MetaDataEdit

# ----------------------------------------------------------------------------
# Panel tested by test_glob.py
# ----------------------------------------------------------------------------


class TestPanel(sppasPanel):

    audio_test = os.path.join(paths.samples, "samples-fra", "F_F_B003-P8.wav")

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="TestPanel-dialogs")

        btn1 = wx.Button(self,
                         pos=(10, 10), size=(180, 70),
                         label="About", name="about_btn")
        btn2 = wx.Button(self,
                         pos=(200, 10), size=(180, 70),
                         label="About plugin", name="about_plugin_btn")
        btn3 = wx.Button(self,
                         pos=(390, 10), size=(180, 70),
                         label="Settings", name="settings_btn")

        btn5 = wx.Button(self,
                         pos=(10, 100), size=(180, 70),
                         label="Audio Roamer", name="audio_btn")
        btn6 = wx.Button(self,
                         pos=(200, 100), size=(180, 70),
                         label="Tier View", name="tierview_btn")
        btn6 = wx.Button(self,
                         pos=(390, 100), size=(180, 70),
                         label="Stats View", name="statview_btn")

        btn7 = wx.Button(self,
                         pos=(10, 200), size=(180, 70),
                         label="Metadata Edit", name="metadata_btn")

        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "about_btn":
            About(self)

        elif event_name == "about_plugin_btn":
            _manager = sppasPluginsManager()
            _plugin = _manager.get_plugin("cleanipus")
            AboutPlugin(self, _plugin)

        elif event_name == "settings_btn":
            Settings(self)

        elif event_name == "audio_btn":
            _audio = sppas.src.audiodata.aio.open(TestPanel.audio_test)
            AudioRoamer(self, _audio)
            _audio.close()

        elif event_name == "tierview_btn":
            # TODO. Add a list of tiers to test TiersView
            TiersView(self, [])

        elif event_name == "statview_btn":
            # TODO. Add a list of tiers to test StatsView
            StatsView(self, [])

        elif event_name == "metadata_btn":
            print("METADATA")
            MetaDataEdit(self, sppasMetaData())

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


