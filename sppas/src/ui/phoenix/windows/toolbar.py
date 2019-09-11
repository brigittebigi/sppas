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

    src.ui.phoenix.windows.toolbar.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import logging

from .panel import sppasPanel
from .text import sppasStaticText
from .button import BitmapTextButton, TextButton, ToggleButton

# ----------------------------------------------------------------------------


class sppasToolbar(sppasPanel):
    """Panel imitating the behaviors of an horizontal toolbar.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, orient=wx.HORIZONTAL, name="toolbar"):
        super(sppasToolbar, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.NO_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # Focus Color&Style
        self._fs = wx.PENSTYLE_SOLID
        self._fw = 3
        self._fc = wx.Colour(128, 128, 128, 128)

        # List of children with their own style (color, font)
        self.__fg = list()
        self.__ft = list()

        # Dictionary with all toggle groups
        self.__tg = dict()

        self.SetSizer(wx.BoxSizer(orient))
        self.SetAutoLayout(True)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.__on_tg_btn_event)

    # -----------------------------------------------------------------------

    def get_button(self, name, group_name=None):
        """Return the object matching the given name or None.

        Without "group_name", it is like "FindWindow(name)

        :param name: (str) Name of the object to search
        :param group_name: (str) Group name of the button to search
        :returns: (wx.Window) a button or None

        """
        if group_name is None:
            return self.FindWindow(name)
            #for b in self.GetSizer().GetChildren():
            #    w = b.GetWindow()
            #    if w is not None and w.GetName() == name:
            #        return w
        else:
            if group_name in self.__tg:
                for btn in self.__tg[group_name]:
                    if btn.GetName() == name:
                        return btn

        return None

    # -----------------------------------------------------------------------

    def AddTextButton(self, name="sppasButton", text=""):
        """Append a text button into the toolbar.

        :param name: (str) Name of the button
        :param text: (str) Label of the button

        """
        btn = self.create_button(text, None)
        btn.SetName(name)
        if self.GetSizer().GetOrientation() == wx.HORIZONTAL:
            self.GetSizer().Add(btn, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 2)
        else:
            self.GetSizer().Add(btn, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 2)
        return btn

    # -----------------------------------------------------------------------

    def AddToggleButton(self, icon, text="", value=False, group_name=None):
        """Append a toggle button into the toolbar.

        The button can contain either:
            - an icon only;
            - an icon with a text.

        :param icon: (str) Name of the .png file of the icon or None
        :param text: (str) Label of the button
        :param value: (bool) Toggle value of the button
        :param group_name: (str) Name of a toggle group

        """
        btn = self.create_toggle_button(text, icon)
        btn.SetValue(value)

        if group_name is not None:
            if group_name not in self.__tg:
                self.__tg[group_name] = list()
            else:
                if value is True:
                    for b in self.__tg[group_name]:
                        b.SetValue(False)
            self.__tg[group_name].append(btn)

        if self.GetSizer().GetOrientation() == wx.HORIZONTAL:
            self.GetSizer().Add(btn, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 2)
        else:
            self.GetSizer().Add(btn, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 2)

        return btn

    # -----------------------------------------------------------------------

    def AddButton(self, icon, text=""):
        """Append a button into the toolbar.

        The button can contain either:
            - an icon only;
            - an icon with a text.

        :param icon: (str) Name of the .png file of the icon or None
        :param text: (str) Label of the button

        """
        btn = self.create_button(text, icon)
        if self.GetSizer().GetOrientation() == wx.HORIZONTAL:
            self.GetSizer().Add(btn, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 2)
        else:
            self.GetSizer().Add(btn, 1, wx.TOP | wx.BOTTOM | wx.EXPAND, 2)
        return btn

    # -----------------------------------------------------------------------

    def AddSpacer(self, proportion=1):
        """Append a stretch space into the toolbar.

        :param proportion: (int)

        """
        self.GetSizer().AddStretchSpacer(proportion)

    # -----------------------------------------------------------------------

    def AddText(self, text="", color=None,
                align=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL,
                name=wx.StaticTextNameStr):
        """Append a colored static text into the toolbar.

        :param text: (str)
        :param color: (wx.Colour)
        :param align: (int) alignment style
        :param name: (str)

        """
        st = sppasStaticText(self, label=text, name=name)
        if color is not None:
            st.SetForegroundColour(color)
            self.__fg.append(st)
        self.GetSizer().Add(st, 0, align | wx.ALL, 6)

        return st

    # -----------------------------------------------------------------------

    def AddTitleText(self, text="", color=None,
                     align=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL,
                     name=wx.StaticTextNameStr):
        """Append a colored static text with an higher font into the toolbar.

        :param text: (str)
        :param color: (wx.Colour)
        :param align: (int) alignment style
        :param name: (str)

        """
        st = sppasStaticText(self, label=text, name=name)
        st.SetFont(self.__title_font())
        self.__ft.append(st)
        if color is not None:
            st.SetForegroundColour(color)
            self.__fg.append(st)
        self.GetSizer().Add(st, 0, align | wx.ALL, 6)

        return st

    # -----------------------------------------------------------------------

    def set_focus_color(self, value):
        self._fc = value
        for c in self.GetChildren():
            try:
                c.FocusColour = value
                c.Refresh()
            except:
                pass

    def set_focus_penstyle(self, value):
        self._fs = value
        for c in self.GetChildren():
            try:
                c.FocusStyle = value
                c.Refresh()
            except:
                pass

    def set_focus_width(self, value):
        self._fw = value
        for c in self.GetChildren():
            try:
                c.FocusWidth = value
                c.Refresh()
            except:
                pass

    # -----------------------------------------------------------------------

    def create_button(self, text, icon):
        if icon is not None:
            btn = BitmapTextButton(self, label=text, name=icon)
            btn.LabelPosition = wx.RIGHT

        else:
            btn = TextButton(self, label=text)
            btn.LabelPosition = wx.CENTRE

        btn.FocusStyle = self._fs
        btn.FocusWidth = self._fw
        btn.FocusColour = self._fc
        btn.Spacing = sppasPanel.fix_size(12)
        btn.BorderWidth = 0
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(sppasPanel.fix_size(32),
                               sppasPanel.fix_size(32)))

        return btn

    # -----------------------------------------------------------------------

    def create_toggle_button(self, text, icon):
        if icon is not None:
            btn = ToggleButton(self, label=text, name=icon)
            btn.LabelPosition = wx.RIGHT
        else:
            btn = ToggleButton(self, label=text)
            btn.LabelPosition = wx.CENTRE

        btn.FocusStyle = self._fs
        btn.FocusWidth = self._fw
        btn.FocusColour = self._fc
        btn.Spacing = sppasPanel.fix_size(12)
        btn.BorderWidth = 1
        btn.BitmapColour = self.GetForegroundColour()
        btn.SetMinSize(wx.Size(sppasPanel.fix_size(32), sppasPanel.fix_size(32)))

        return btn

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            if c not in self.__fg:
                c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.Panel.SetFont(self, font)
        for c in self.GetChildren():
            if c not in self.__ft:
                c.SetFont(font)

    # -----------------------------------------------------------------------

    def __title_font(self):
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        s = font.GetPointSize()

        title_font = wx.Font(int(float(s)*1.2),      # point size
                             wx.FONTFAMILY_DEFAULT,  # family,
                             wx.FONTSTYLE_NORMAL,    # style,
                             wx.FONTWEIGHT_BOLD,     # weight,
                             underline=False,
                             faceName="Calibri",
                             encoding=wx.FONTENCODING_SYSTEM)
        return title_font

    # -----------------------------------------------------------------------

    def __on_tg_btn_event(self, event):
        obj = event.GetEventObject()
        group = None
        for gp in self.__tg:
            for btn in self.__tg[gp]:
                if btn is obj:
                    group = gp
                    break

        if group is not None:
            value = obj.GetValue()
            if value is False:
                obj.SetValue(True)
                return

            for btn in self.__tg[group]:
                if btn is not obj:
                    btn.SetValue(False)

        event.Skip()

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test Toolbar")

        self.SetForegroundColour(wx.Colour(150, 160, 170))

        tbh = sppasToolbar(self, orient=wx.HORIZONTAL)
        tbh.AddTitleText("title:", wx.Colour(128, 196, 228))
        tbh.AddButton("sppas_32", "icon")
        tbh.AddButton("sppas_32")
        tbh.AddText("Text")
        tbh.AddSpacer()
        b1 = tbh.AddToggleButton("wifi", text="Wifi")
        b1.Enable(True)
        tbh.AddSpacer()
        tbh.AddToggleButton("at", text="xxx", value=False, group_name="mail")
        tbh.AddToggleButton("gmail", text="yyy", value=True, group_name="mail")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tbh, 0, wx.EXPAND, 2)
        sizer.Add(sppasPanel(self), 1, wx.EXPAND, 2)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.__on_btn_event)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.__on_btn_event)

    def __on_btn_event(self, event):
        btn = event.GetEventObject()
        logging.info('Event button {:s}'.format(btn.GetName()))
