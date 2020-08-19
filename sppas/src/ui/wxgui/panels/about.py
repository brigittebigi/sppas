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

    src.wxgui.anz_panels.about.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    GUI panel for displaying information about a software.

"""
import os
import wx
import wx.lib.scrolledpanel
import webbrowser

from sppas.src.config import sg
from sppas.src.ui.wxgui.cutils.imageutils import spBitmap
from sppas.src.ui.wxgui.sp_icons import APP_ICON

# ----------------------------------------------------------------------------


class sppasBaseAbout(wx.lib.scrolledpanel.ScrolledPanel):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      About panel including main information about a software.

    """
    def __init__(self, parent, preferences):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1,
                                                    size=wx.DefaultSize,
                                                    style=wx.NO_BORDER)
        self.SetBackgroundColour(preferences.GetValue('M_BG_COLOUR'))
        self.SetForegroundColour(preferences.GetValue('M_FG_COLOUR'))
        self.SetFont(preferences.GetValue('M_FONT'))

        self._preferences = preferences
        self.program = ""
        self.version = ""
        self.author = ""
        self.copyright = ""
        self.brief = ""
        self.url = ""
        self.license = ""
        self.license_text = ""
        self.icon = ""
        self.logo = ""

    # ------------------------------------------------------------------------

    def create(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Logo
        if len(self.logo) > 0:
            bitmap = spBitmap(self.logo, size=48)
            logo_bmp = wx.StaticBitmap(self, wx.ID_ANY, bitmap)
            sizer.Add(logo_bmp, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=8)

        # Program name
        if len(self.program) > 0:
            text_program_version = wx.StaticText(self, -1, self.program + " " + sg.__version__)
            self.__apply_preferences(text_program_version)
            font = self._preferences.GetValue('M_FONT')
            font_size = font.GetPointSize()
            font.SetPointSize(font_size + 4)
            font.SetWeight(wx.BOLD)
            text_program_version.SetFont(font)
            sizer.Add(text_program_version,
                      proportion=0,
                      flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL,
                      border=2)

        # Description
        if len(self.brief) > 0:
            text_descr = wx.StaticText(self, -1, self.brief)
            self.__apply_preferences(text_descr)
            sizer.Add(text_descr, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=2)

        # Copyright
        if len(self.copyright) > 0:
            text_copy = wx.StaticText(self, -1, self.copyright)
            self.__apply_preferences(text_copy)
            font = self._preferences.GetValue('M_FONT')
            font.SetWeight(wx.BOLD)
            text_copy.SetFont(font)
            sizer.Add(text_copy, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=2)

        # URL
        if len(self.url) > 0:
            text_url = wx.StaticText(self, -1, self.url)
            self.__apply_preferences(text_url)
            text_url.SetForegroundColour(wx.Colour(80, 100, 220))
            text_url.Bind(wx.EVT_LEFT_UP, self.on_link)
            sizer.Add(text_url, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=2)

        # License
        if len(self.license) > 0:
            text_license = wx.StaticText(self, -1, self.license)
            self.__apply_preferences(text_license)
            sizer.Add(text_license, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=2)

        # License text content
        if len(self.license_text) > 0:
            text_gpl = wx.StaticText(self, -1, self.license_text)
            self.__apply_preferences(text_gpl)
            sizer.Add(text_gpl, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=2)

        self.SetSizerAndFit(sizer)
        self.SetupScrolling(scroll_x=True, scroll_y=True)

    # ------------------------------------------------------------------------

    def on_link(self, event):
        try:
            webbrowser.open(sg.__url__, 1)
        except:
            pass

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __apply_preferences(self, wx_object):
        """Set font, background color and foreground color to an object."""

        wx_object.SetFont(self._preferences.GetValue('M_FONT'))
        wx_object.SetForegroundColour(self._preferences.GetValue('M_FG_COLOUR'))
        wx_object.SetBackgroundColour(self._preferences.GetValue('M_BG_COLOUR'))

# ----------------------------------------------------------------------------


class AboutSPPASPanel(sppasBaseAbout):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      About SPPAS panel.

    """
    def __init__(self, parent, preferences):
        sppasBaseAbout.__init__(self, parent, preferences)

        self.program = sg.__name__
        self.version = sg.__version__
        self.author = sg.__author__
        self.copyright = sg.__copyright__
        self.brief = sg.__summary__
        self.url = sg.__url__
        self.logo = APP_ICON
        self.license_text = """
------------------------------------------------------------

By using SPPAS, you agree to cite the reference in your publications:

Brigitte Bigi (2015),
SPPAS - Multi-lingual Approaches to the Automatic Annotation of Speech,
The Phonetician, International Society of Phonetic Sciences,
vol. 111-112, ISBN: 0741-6164, pages 54-69.

------------------------------------------------------------

SPPAS is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of
the License, or (at your option) any later version.

SPPAS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with File Hunter; if not, write to the Free Software Foundation,
Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

------------------------------------------------------------
"""
        self.create()
        self.SetAutoLayout(True)

# ------------------------------------------------------------------------


class AboutPluginPanel(sppasBaseAbout):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      About a plugin.

    """
    def __init__(self, parent, preferences, plugin):
        sppasBaseAbout.__init__(self, parent, preferences)

        self.program = plugin.get_name()
        self.logo = os.path.join(plugin.get_directory(), plugin.get_icon())

        self.brief = ""
        self.version = ""
        self.author = ""
        self.copyright = ""
        self.url = ""

        self.license_text = ""
        readme = os.path.join(plugin.get_directory(), "README.txt")
        if os.path.exists(readme):
            try:
                with open(readme, "r") as f:
                    self.license_text = f.read()
            except Exception:
                pass

        self.create()
        self.SetAutoLayout(True)
