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

    src.ui.phoenix.dialogs.settings.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx

from sppas.src.config import ui_translation

from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import sppasBitmapButton
from ..windows.book import sppasNotebook

from ..tools import sppasSwissKnife

# ---------------------------------------------------------------------------

MSG_HEADER_SETTINGS = ui_translation.gettext("Settings")

MSG_FONT = ui_translation.gettext("Font")
MSG_BG = ui_translation.gettext("Background color")
MSG_FG = ui_translation.gettext("Foreground color")
MSG_FONT_COLORS = ui_translation.gettext("Fonts and Colors")
MSG_HEADER = ui_translation.gettext("Top")
MSG_CONTENT = ui_translation.gettext("Main content")
MSG_ACTIONS = ui_translation.gettext("Bottom")

# ---------------------------------------------------------------------------


def GetColour(parent):
    """Return the color choose by the user.

    :param parent: (wx.Window)

    """
    # open the dialog
    dlg = wx.ColourDialog(parent)

    # Ensure the full colour dialog is displayed,
    # not the abbreviated version.
    dlg.GetColourData().SetChooseFull(True)

    c = None
    if dlg.ShowModal() == wx.ID_OK:
        color = dlg.GetColourData().GetColour()
        r = color.Red()
        g = color.Green()
        b = color.Blue()
        c = wx.Colour(r, g, b)
    dlg.Destroy()
    return c

# ----------------------------------------------------------------------------


class sppasSettingsDialog(sppasDialog):
    """Settings dialogs.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Returns either wx.ID_CANCEL or wx.ID_OK if ShowModal().

    """

    def __init__(self, parent):
        """Create a dialog to fix settings.

        :param parent: (wx.Window)

        """
        super(sppasSettingsDialog, self).__init__(
            parent=parent,
            title="Settings",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP)

        self._back_up = dict()
        self._backup_settings()

        self.CreateHeader(MSG_HEADER_SETTINGS, "settings")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_cancel)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn(deltaN=-8)

    # -----------------------------------------------------------------------

    def _backup_settings(self):
        """Store settings that can be modified."""
        settings = wx.GetApp().settings

        self._back_up['bg_color'] = settings.bg_color
        self._back_up['fg_color'] = settings.fg_color
        self._back_up['text_font'] = settings.text_font

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        # Make the notebook and an image list
        notebook = sppasNotebook(self, name="content")
        il = wx.ImageList(16, 16)
        idx1 = il.Add(sppasSwissKnife.get_bmp_icon("font_color", height=16))
        notebook.AssignImageList(il)

        page1 = WxSettingsPanel(notebook)
        # page2 = PrefsThemePanel(self.notebook, self.preferences)
        # page3 = PrefsAnnotationPanel(self.notebook, self.preferences)
        # add the pages to the notebook with the label to show on the tab

        notebook.AddPage(page1, MSG_FONT_COLORS)
        # self.notebook.AddPage(page2, "Icons Theme")
        # self.notebook.AddPage(page3, "Annotation")

        # put an image on the first tab
        notebook.SetPageImage(0, idx1)
        self.SetContent(notebook)

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "cancel":
            self.on_cancel(event)

        elif "color" in event_name or "font" in event_name:
            self.UpdateUI()

        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def on_cancel(self, event):
        """Restore initial settings and close dialog."""
        self._restore()
        # close the dialog with a wx.ID_CANCEL response
        self.SetReturnCode(wx.ID_CANCEL)
        event.Skip()

    # ------------------------------------------------------------------------

    def _restore(self):
        """Restore initial settings."""
        # Get initial settings from our backup: set to settings
        settings = wx.GetApp().settings
        for k in self._back_up:
            settings.set(k, self._back_up[k])

# ----------------------------------------------------------------------------


class WxSettingsPanel(sppasPanel):
    """Settings for wx objects: background, foreground, font, etc.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent):
        super(WxSettingsPanel, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE
        )
        self._create_content()
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_top = self._create_content_colors_fonts()
        sizer.Add(sizer_top, 0, wx.EXPAND)
        # btn = sppasBitmapTextButton(
        #     parent=self,
        #     name="window-apply",
        #     label="Test on this window",
        #     style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)
        # btn.SetSize((-1, wx.GetApp().settings.action_height))
        # sizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL)
        # sizer.AddStretchSpacer(1)

        # ----------
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def _create_content_colors_fonts(self):
        """"""

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Colors&Fonts of the header panel
        p = sppasColoursFontPanel(
            parent=self,
            style=wx.BORDER_SUNKEN,
            name="colors_font_header",
            title=MSG_HEADER)
        sizer.Add(p, 1, wx.EXPAND | wx.ALL, border=10)

        # Colors&Fonts of the main panel
        p = sppasColoursFontPanel(
            parent=self,
            style=wx.BORDER_SUNKEN,
            name="colors_font_content",
            title=MSG_CONTENT)
        sizer.Add(p, 1, wx.EXPAND | wx.ALL, border=10)

        # Colors&Fonts of the actions panel
        p = sppasColoursFontPanel(
            parent=self,
            style=wx.BORDER_SUNKEN,
            name="colors_font_actions",
            title=MSG_ACTIONS)
        sizer.Add(p, 1, wx.EXPAND | wx.ALL, border=10)

        return sizer

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()
        event_id = event_obj.GetId()
        # wx.LogDebug("Received event id {:d} of {:s}".format(event_id, event_name))

        if "color" in event_name:
            self.on_color_dialog(event)
            event.Skip()

        elif "font" in event_name:
            self.on_select_font(event)
            event.Skip()

        else:
            event.Skip()

    # -----------------------------------------------------------------------
    # Callbacks to event
    # -----------------------------------------------------------------------

    def on_color_dialog(self, event):
        """Open a dialog to choose a color, then fix it.

        :param event: (wx.Event)

        """
        color = GetColour(self)
        if color is not None:

            # get the button that was clicked on
            button = event.GetEventObject()
            name = button.GetName()

            # new value in the settings for which panel?
            if "content" in button.GetParent().GetName():
                wx.GetApp().settings.set(name, color)

            elif "header" in button.GetParent().GetName():
                wx.GetApp().settings.set("header_"+name, color)

            elif "action" in button.GetParent().GetName():
                wx.GetApp().settings.set("action_"+name, color)

    # -----------------------------------------------------------------------

    def on_select_font(self, event):
        """Open a dialog to choose a font, then fix it.

        :param event: (wx.Event)

        """
        button = event.GetEventObject()

        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(wx.GetApp().settings.fg_color)
        data.SetInitialFont(wx.GetApp().settings.text_font)

        dlg = wx.FontDialog(self, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()

            if "content" in button.GetParent().GetName():
                wx.GetApp().settings.set('text_font', font)

            elif "header" in button.GetParent().GetName():
                wx.GetApp().settings.set('header_text_font', font)

            elif "action" in button.GetParent().GetName():
                wx.GetApp().settings.set('action_text_font', font)

        dlg.Destroy()

# ---------------------------------------------------------------------------


class sppasColoursFontPanel(sppasPanel):
    """Panel to propose the change of colors and font.

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.TAB_TRAVERSAL,
                 name=wx.PanelNameStr,
                 title=""):
        super(sppasColoursFontPanel, self).__init__(parent, id, pos, size, style, name)

        flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL
        gbs = wx.GridBagSizer(hgap=10, vgap=10)

        # ---------- Title

        txt = wx.StaticText(self, -1, title, name="title")
        gbs.Add(txt, (0, 0), flag=flag, border=5)

        # ---------- Background color

        txt_bg = wx.StaticText(self, -1, MSG_BG)
        gbs.Add(txt_bg, (1, 0), flag=flag, border=5)

        btn_color_bg = sppasBitmapButton(
            parent=self,
            name="bg_color",
            style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)
        btn_color_bg.SetSize((wx.GetApp().settings.action_height,
                              wx.GetApp().settings.action_height))
        gbs.Add(btn_color_bg, (1, 1), flag=flag, border=5)

        # ---------- Foreground color

        txt_fg = wx.StaticText(self, -1, MSG_FG)
        gbs.Add(txt_fg, (2, 0), flag=flag, border=5)

        btn_color_fg = sppasBitmapButton(
            parent=self,
            name="fg_color",
            style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)
        btn_color_fg.SetSize((wx.GetApp().settings.action_height,
                              wx.GetApp().settings.action_height))
        gbs.Add(btn_color_fg, (2, 1), flag=flag, border=5)

        # ---------- Font

        txt_font = wx.StaticText(self, -1, MSG_FONT)
        gbs.Add(txt_font, (3, 0), flag=flag, border=5)

        btn_font = sppasBitmapButton(
            parent=self,
            name="font",
            style=wx.BORDER_SIMPLE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)
        btn_font.SetSize((wx.GetApp().settings.action_height,
                          wx.GetApp().settings.action_height))
        gbs.Add(btn_font, (3, 1), flag=flag, border=5)

        gbs.AddGrowableCol(1)
        self.SetSizer(gbs)
        self.SetMinSize(wx.Size(180, 200))

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        sppasPanel.SetFont(self, font)
        current = wx.GetApp().settings.text_font
        f = wx.Font(int(current.GetPointSize() * 1.2),
                    wx.FONTFAMILY_SWISS,   # family,
                    wx.FONTSTYLE_NORMAL,   # style,
                    wx.FONTWEIGHT_BOLD,    # weight,
                    underline=False,
                    faceName=current.GetFaceName(),
                    encoding=wx.FONTENCODING_SYSTEM)
        self.FindWindow("title").SetFont(f)

# ---------------------------------------------------------------------------


def Settings(parent):
    """Display a dialog to fix new settings.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    :param parent: (wx.Window)
    :returns: the response

    Returns wx.ID_CANCEL if the dialog is destroyed or wx.ID_OK if some
    settings changed.

    """
    dialog = sppasSettingsDialog(parent)
    response = dialog.ShowModal()
    dialog.DestroyFadeOut()
    return response
