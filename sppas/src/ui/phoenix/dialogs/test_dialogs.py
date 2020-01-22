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

from sppas import paths
from sppas.src.plugins import sppasPluginsManager
import sppas.src.audiodata.aio

from .audioroamer import AudioRoamer
from .about import About
from .about import AboutPlugin
from .settings import Settings
from ..windows import sppasPanel

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


