#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2017  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: annotationoptions.py
# ----------------------------------------------------------------------------

import wx
import wx.lib.agw.floatspin

from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog
from sppas.src.ui.wxgui.panels.options import sppasOptionsPanel

from sppas.src.ui.wxgui.sp_icons import ANNOTATE_CONFIG_ICON
from sppas.src.ui.wxgui.sp_icons import RESTORE_ICON

# ----------------------------------------------------------------------------


class spAnnotationConfig(spBaseDialog):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      develop@sppas.org
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Dialog to configure the automatic annotation options.

    Parent must be a sppasFrame.

    """
    def __init__(self, parent, preferences, step, step_idx):
        """
        Constructor.

        :param parent must be the sppas main frame

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Options")
        wx.GetApp().SetAppName("option"+str(step_idx))

        self.step = step
        self.stepid = step_idx
        self._preferences = preferences

        self.LayoutComponents(self._create_title(),
                              self._create_content(),
                              self._create_buttons())

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_title(self):
        text = self.GetParent().parameters.get_step_name(self.stepid)+" sppasAppConfig"
        return self.CreateTitle(ANNOTATE_CONFIG_ICON, text)

    def _create_content(self):
        options_panel = sppasOptionsPanel(self, self._preferences, self.step.get_options())
        options_panel.SetBackgroundColour(self._preferences.GetValue('M_BG_COLOUR'))
        options_panel.SetForegroundColour(self._preferences.GetValue('M_FG_COLOUR'))
        options_panel.SetFont(self._preferences.GetValue('M_FONT'))
        self.items = options_panel.GetItems()
        return options_panel

    def _create_buttons(self):
        btn_restore = self.CreateButton( RESTORE_ICON, " Restore defaults ", "Reset options to their default values" )
        btn_cancel  = self.CreateCancelButton()
        btn_okay    = self.CreateOkayButton()
        self.Bind(wx.EVT_BUTTON, self._on_restore, btn_restore)
        self.Bind(wx.EVT_BUTTON, self._on_cancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self._on_okay, btn_okay)
        return self.CreateButtonBox([btn_restore], [btn_cancel, btn_okay])

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _on_okay(self, evt):
        # Save options
        for i, item in enumerate(self.items):
            self.step.get_option(i).set_value(item.GetValue())
        self.GetParent().Update()
        self.GetParent().Refresh()
        del self.GetParent().opened_frames[self.GetParent().ID_FRAME_ANNOTATION_CFG+self.stepid]
        self.Destroy()

    def _on_restore(self, evt):
        for i, item in enumerate(self.items):
            item.SetValue( self.step.get_option(i).get_value())

    def _on_cancel(self, evt):
        del self.GetParent().opened_frames[self.GetParent().ID_FRAME_ANNOTATION_CFG+self.stepid]
        self.Destroy()

# ----------------------------------------------------------------------------
