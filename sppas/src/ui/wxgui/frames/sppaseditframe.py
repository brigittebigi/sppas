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

    src.wxgui.frames.sppaseditframe.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    GUI view of files for SPPAS.

"""
import wx
import logging

from sppas.src.ui.wxgui.clients.sppaseditclient import SppasEditClient
from sppas.src.ui.wxgui.views.settings import SettingsDialog

from sppas.src.ui.wxgui.structs.theme import sppasTheme
from sppas.src.ui.wxgui.structs.cthemes import all_themes
from sppas.src.ui.wxgui.cutils.textutils import TextAsNumericValidator
from sppas.src.ui.wxgui.cutils.textutils import TextAsPercentageValidator

from sppas.src.ui.wxgui.sp_icons import SPPASEDIT_APP_ICON

from .baseframe import ComponentFrame

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

DEMO_DISPLAY_WIZARD_ID = wx.NewId()
DEMO_POINT_ID = wx.NewId()
DEMO_LABEL_ID = wx.NewId()
DEMO_TIER_ID = wx.NewId()
DEMO_TRS_ID = wx.NewId()
DEMO_WAVE_ID = wx.NewId()
DEMO_DISPLAY_ID = wx.NewId()
DEMO_ZOOM_WIZARD_ID = wx.NewId()
DEMO_SCROLL_WIZARD_ID = wx.NewId()
DEMO_SOUND_WIZARD_ID = wx.NewId()
DEMO_TRS_WIZARD_ID = wx.NewId()

# ----------------------------------------------------------------------------


class SppasEditFrame(ComponentFrame):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SppasEdit allows to display annotations and sound files.

    """

    def __init__(self, parent, id, prefsIO):

        arguments = {}
        arguments['files'] = []
        arguments['title'] = "SPPAS - Vizualizer"
        arguments['type']  = "ANYFILES"
        arguments['icon']  = SPPASEDIT_APP_ICON
        arguments['prefs'] = prefsIO
        ComponentFrame.__init__(self, parent, id, arguments)

        self._append_in_menu()

    # ------------------------------------------------------------------------

    def _init_members(self, args):
        """Override.
        Sets the members settings.

        """
        ComponentFrame._init_members(self, args)

        if isinstance(self._prefsIO.GetTheme(), sppasTheme):
            self._prefsIO.SetTheme(all_themes.get_theme(u'Default'))

        self._fmtype = "ANYFILES"

    # ------------------------------------------------------------------------

    def _append_in_menu(self):
        """Append new items in a menu or a new menu in the menubar."""

        # DISABLED SINCE SPPAS-1.8.0

        return

    # ------------------------------------------------------------------------

    def CreateClient(self, parent, prefsIO):
        """Override."""

        return SppasEditClient(parent,prefsIO)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def OnSettings(self, event):
        """
        Open the Settings box.

        Override the baseframe.OnSettings to add specific anz_panels to
        the SettingsDialog().

        """
        p = self._prefsIO.Copy()

        prefdlg = SppasEditSettingsDialog( self, p )
        res = prefdlg.ShowModal()
        if res == wx.ID_OK:
            self.SetPrefs( prefdlg.GetPreferences() )
            if self.GetParent() is not None:
                try:
                    self.GetParent().SetPrefs( self._prefsIO )
                except Exception:
                    pass
        prefdlg.Destroy()
        self._LayoutFrame()

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# class SettingsDialog, with specific settings for SppasEdit
# ----------------------------------------------------------------------------


class SppasEditSettingsDialog(SettingsDialog):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      This class is used to fix all user's settings, with a Dialog.

    Dialog for the user to fix all preferences.

    """
    def __init__(self, parent, prefsIO):
        """
        Create a new dialog fo fix preferences, sorted in a notebook.

        """

        SettingsDialog.__init__(self, parent, prefsIO)

        page4 = SppasEditAppearancePanel(self.notebook, self.preferences)
        self.notebook.AddPage(page4, "Appearance")

        page5 = SppasEditTimePanel(self.notebook, self.preferences)
        self.notebook.AddPage(page5, "Displayed Time")

# ----------------------------------------------------------------------------


class SppasEditAppearancePanel(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Drawing area settings.

    """
    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self._prefsIO = prefsIO

        gbs = self.__create_sizer()
        self.SetSizer(gbs)

    # ------------------------------------------------------------------------

    def __create_sizer(self):

        gbs = wx.GridBagSizer(hgap=5, vgap=5)

        # ---------- Vertical zoom step , percentage

        txt_fg = wx.StaticText(self, -1, 'Vertical zoom step (percentage): ')
        gbs.Add(txt_fg, (0,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.text_v_zoom = wx.TextCtrl(self, size=(150, -1), validator=TextAsPercentageValidator())
        self.text_v_zoom.SetValue( str(self._prefsIO.GetValue('D_V_ZOOM')) )
        gbs.Add(self.text_v_zoom, (0,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.text_v_zoom.Bind(wx.EVT_TEXT, self.onVZoomChanged)

        # ---------- Tier: Label position

        txt_fg = wx.StaticText(self, -1, 'Labels position: ')
        gbs.Add(txt_fg, (1,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelalign = wx.Choice(self, -1, choices=['Left' , 'Centre', 'Right'])
        current = self._prefsIO.GetValue('T_LABEL_ALIGN')
        if current == wx.ALIGN_LEFT:
            self.labelalign.SetSelection(0)
        elif current == wx.ALIGN_CENTRE:
            self.labelalign.SetSelection(1)
        else:
            self.labelalign.SetSelection(2)
        gbs.Add(self.labelalign, (1,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.labelalign.Bind(wx.EVT_CHOICE, self.onLabelAlignChanged)

        # ---------- Wave: auto-scroll

        txt_fg = wx.StaticText(self, -1, 'Wave auto-scrolling: ')
        gbs.Add(txt_fg, (2,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.wavescroll = wx.CheckBox(self, -1, '', style=wx.NO_BORDER)
        self.wavescroll.SetValue(self._prefsIO.GetValue('W_AUTOSCROLL'))
        gbs.Add(self.wavescroll, (2,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.wavescroll.Bind(wx.EVT_CHECKBOX, self.onWaveScrollChanged)

        # ---------- Color scheme

        self.theme = SppasEditColourSchemePanel(self, self._prefsIO)
        gbs.Add(self.theme, (3,0), (2,2), flag=wx.EXPAND|wx.ALL, border=5)

        gbs.AddGrowableCol(1)

        return gbs

    # ------------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------------

    def onVZoomChanged(self, event):
        """
        Change the vertical zoom coefficient,
        except if the validation fails.
        """
        success = self.text_v_zoom.GetValidator().Validate(self.text_v_zoom)
        if success is False:
            return

        self.text_v_zoom.SetFocus()
        self.text_v_zoom.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text_v_zoom.Refresh()
        try:
            v = float(self.text_v_zoom.GetValue())
            self._prefsIO.SetValue('D_V_ZOOM', 'float', v)
        except Exception:
            pass

    # ------------------------------------------------------------------------

    def onLabelAlignChanged(self, event):
        """
        Change the label alignment flag,
        except if the validation fails.
        """
        choice = self.labelalign.GetCurrentSelection()
        alignchoice = [wx.ALIGN_LEFT , wx.ALIGN_CENTRE, wx.ALIGN_RIGHT]
        self._prefsIO.SetValue('T_LABEL_ALIGN', 'wx.ALIGN', alignchoice[choice])

    # ------------------------------------------------------------------------

    def onWaveScrollChanged(self, event):
        """
        Activate/Disable the Wave vertical auto-scroll.
        """
        checked = self.wavescroll.GetValue()
        self._prefsIO.SetValue('W_AUTOSCROLL', 'bool', checked)

# -----------------------------------------------------------------------------


class SppasEditColourSchemePanel(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:     Panel with a radiobox to choose the SppasEdit Theme-Colour.

    """
    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO

        themekeys = sorted(all_themes.get_themes().keys())
        currenttheme = prefsIO.GetTheme()
        choices = []
        currentchoice = 0
        for (i,choice) in enumerate(themekeys):
            choices.append( choice )
            if currenttheme == all_themes.get_theme(choice):
                currentchoice = i

        self.radiobox = wx.RadioBox(self, label="Theme Colour scheme: ",
                                    choices=choices, majorDimension=4)

        # check the current theme
        self.radiobox.SetSelection( currentchoice )

        # bind any theme change
        self.Bind(wx.EVT_RADIOBOX, self.radioClick, self.radiobox)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.radiobox, 1, wx.EXPAND|wx.ALL, border=5)
        self.SetSizer(vbox)

    def radioClick(self, event):
        """Set the new theme."""
        theme = all_themes.get_theme( self.radiobox.GetStringSelection() )
        self.preferences.SetTheme( theme )

# ----------------------------------------------------------------------------


class SppasEditTimePanel(wx.Panel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Time settings.

    """
    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self._prefsIO = prefsIO

        gbs = self.__create_sizer()
        self.SetSizer(gbs)

    # ------------------------------------------------------------------------

    def __create_sizer(self):

        gbs = wx.GridBagSizer(hgap=5, vgap=5)

        # ---------- Duration at start-up

        txt_fg = wx.StaticText(self, -1, 'Duration (in seconds) of the displayed period at start-up: ')
        gbs.Add(txt_fg, (0,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.text_duration = wx.TextCtrl(self, size=(150, -1), validator=TextAsNumericValidator())
        self.text_duration.SetValue( str(self._prefsIO.GetValue('D_TIME_MAX')) )
        gbs.Add(self.text_duration, (0,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.text_duration.Bind(wx.EVT_TEXT, self.onTextDurationChanged)

        # ---------- Zoom step , percentage

        txt_fg = wx.StaticText(self, -1, 'Time zoom step (percentage): ')
        gbs.Add(txt_fg, (1,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.text_h_zoom = wx.TextCtrl(self, size=(150, -1), validator=TextAsPercentageValidator())
        self.text_h_zoom.SetValue( str(self._prefsIO.GetValue('D_H_ZOOM')) )
        gbs.Add(self.text_h_zoom, (1,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.text_h_zoom.Bind(wx.EVT_TEXT, self.onHZoomChanged)

        # ---------- Scroll step , percentage

        txt_fg = wx.StaticText(self, -1, 'Time scroll step (percentage): ')
        gbs.Add(txt_fg, (2,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.text_scroll = wx.TextCtrl(self, size=(150, -1), validator=TextAsPercentageValidator())
        self.text_scroll.SetValue( str(self._prefsIO.GetValue('D_SCROLL')) )
        gbs.Add(self.text_scroll, (2,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        self.text_scroll.Bind(wx.EVT_TEXT, self.onScrollChanged)

        gbs.AddGrowableCol(1)

        return gbs

    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------

    def onTextDurationChanged(self, event):
        """
        Change the displayed duration at start-up,
        except if the validation fails.
        """
        success = self.text_duration.GetValidator().Validate(self.text_duration)
        if success is False:
            return

        self.text_duration.SetFocus()
        self.text_duration.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text_duration.Refresh()
        try:
            v = float(self.text_duration.GetValue())
            self._prefsIO.SetValue('D_TIME_MAX', 'float', v)
        except Exception:
            pass

    # -------------------------------------------------------------------------

    def onHZoomChanged(self, event):
        """
        Change the horizontal zoom coefficient,
        except if the validation fails.
        """
        success = self.text_h_zoom.GetValidator().Validate(self.text_h_zoom)
        if success is False:
            return

        self.text_h_zoom.SetFocus()
        self.text_h_zoom.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text_h_zoom.Refresh()
        try:
            v = float(self.text_h_zoom.GetValue())
            self._prefsIO.SetValue('D_H_ZOOM', 'float', v)
        except Exception:
            pass

    # -------------------------------------------------------------------------

    def onScrollChanged(self, event):
        """
        Change the scrolling coefficient,
        except if the validation fails.
        """
        success = self.text_scroll.GetValidator().Validate(self.text_scroll)
        if success is False:
            return

        self.text_scroll.SetFocus()
        self.text_scroll.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.text_scroll.Refresh()
        try:
            v = float(self.text_scroll.GetValue())
            self._prefsIO.SetValue('D_SCROLL', 'float', v)
        except Exception:
            pass

# ----------------------------------------------------------------------------
