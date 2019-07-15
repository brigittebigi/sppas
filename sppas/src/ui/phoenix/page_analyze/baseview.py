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

    ui.phoenix.page_analyze.baseview.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import logging
import wx

from ..windows import sppasScrolledPanel
from ..windows import sppasPanel
from ..windows import CheckButton

from .text_view import TextViewPanel

# ----------------------------------------------------------------------------


class BaseViewPanel(sppasScrolledPanel):
    """Base class to display the content of one file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, parent, name="baseview", filename=""):
        super(BaseViewPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.NO_FULL_REPAINT_ON_RESIZE,
            name=name)

        # The file this panel is displaying
        self.__filename = filename
        self.__hicolor = self.GetForegroundColour()

        self._create_content()
        self._setup_events()

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.mono_text_font)

        self.Layout()

    # -----------------------------------------------------------------------

    def is_checked(self):
        """Return True if this file is checked."""
        return self.FindWindow("checkbtn").GetValue()

    # -----------------------------------------------------------------------

    def SetHighLightColor(self, color):
        """Set a color to highlight buttons, and for the focus."""
        self.__hicolor = color
        for child in self.GetChildren():
            if isinstance(child, CheckButton):
                if child.GetValue() is False:
                    child.FocusColour = self.__hicolor

    # -----------------------------------------------------------------------
    # Private methods to construct the panel.
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        btn = CheckButton(self, label=self.__filename, name="checkbtn")
        btn.SetSpacing(sppasScrolledPanel.fix_size(12))
        btn.SetMinSize(wx.Size(-1, sppasScrolledPanel.fix_size(32)))
        btn.SetSize(wx.Size(-1, sppasScrolledPanel.fix_size(32)))
        btn.SetValue(False)
        self.__set_normal_btn_style(btn)
        sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 2)

        view = TextViewPanel(self, filename=self.__filename)
        sizer.Add(view, 1, wx.EXPAND | wx.LEFT, sppasScrolledPanel.fix_size(34))

        self.SetSizer(sizer)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.SetMinSize(wx.Size(sppasScrolledPanel.fix_size(128),
                                sppasScrolledPanel.fix_size(32)))

    # -----------------------------------------------------------------------

    def __set_normal_btn_style(self, button):
        """Set a normal style to a button."""
        button.BorderWidth = 0
        button.BorderColour = self.GetForegroundColour()
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = self.__hicolor

    # -----------------------------------------------------------------------

    def __set_active_btn_style(self, button):
        """Set a special style to the button."""
        button.BorderWidth = 1
        button.BorderColour = self.__hicolor
        button.BorderStyle = wx.PENSTYLE_SOLID
        button.FocusColour = self.GetForegroundColour()

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(wx.EVT_RADIOBUTTON, self.__process_checked)

    # -----------------------------------------------------------------------

    def __process_checked(self, event):
        """Process a checkbox event.

        Skip the event in order to allow the parent to handle it: it's to
        update the other windows with data of the new selected workspace.

        :param event: (wx.Event)

        """
        # the button we want to switch on
        btn = event.GetButtonObj()
        state = btn.GetValue()
        if state is True:
            self.__set_active_btn_style(btn)
        else:
            self.__set_normal_btn_style(btn)
        btn.SetValue(state)
        btn.Refresh()
        logging.debug('Button {:s} is checked: {:s}'
                      ''.format(btn.GetLabel(), str(state)))
