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

    src.ui.phoenix.dialogs.about.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import wx
import webbrowser

from sppas.src.config import sg
from sppas.src.config import ui_translation

from ..tools import sppasSwissKnife
from ..windows import sppasScrolledPanel
from ..windows import sppasDialog
from ..windows import sppasMessageText

# ----------------------------------------------------------------------------

MSG_HEADER_ABOUT = ui_translation.gettext("About")

# ----------------------------------------------------------------------------


class sppasBaseAbout(sppasScrolledPanel):
    """An about base panel to include main information about a software.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent):
        super(sppasBaseAbout, self).__init__(
            parent=parent,
            style=wx.NO_BORDER
        )

        self.program = ""
        self.version = ""
        self.author = ""
        self.copyright = ""
        self.brief = ""
        self.url = ""
        self.license = ""
        self.license_text = ""
        self.icon = ""
        self.logo = 'sppas'

        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def create(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Logo
        if len(self.logo) > 0:
            bitmap = sppasSwissKnife.get_bmp_image(self.logo, height=48)
            sbmp = wx.StaticBitmap(self, wx.ID_ANY, bitmap)
            sizer.Add(sbmp, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)

        # Program name
        if len(self.program) > 0:
            text = wx.StaticText(self, -1, self.program + " " + sg.__version__)
            font = text.GetFont()
            font_size = font.GetPointSize()
            font.SetPointSize(font_size + 4)
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            text.SetFont(font)
            sizer.Add(text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)

        # Description
        if len(self.brief) > 0:
            text = wx.StaticText(self, -1, self.brief)
            sizer.Add(text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)

        # Copyright
        if len(self.copyright) > 0:
            text = wx.StaticText(self, -1, self.copyright)
            font = text.GetFont()
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            text.SetFont(font)
            sizer.Add(text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)

        # URL
        if len(self.url) > 0:
            text = sppasMessageText(self, self.url, name="url")
            text.Bind(wx.EVT_LEFT_UP, self.on_link, text)
            text.SetMinSize(wx.Size(200, sppasScrolledPanel.fix_size(20)))
            sizer.Add(text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)

        # License
        if len(self.license) > 0:
            text = wx.StaticText(self, -1, self.license)
            sizer.Add(text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)

        # License text content
        if len(self.license_text) > 0:
            text = wx.StaticText(self, -1, self.license_text)
            sizer.Add(text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)

        self.SetSizerAndFit(sizer)
        self.SetupScrolling(scroll_x=True, scroll_y=True)

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override.

        :param colour: (wx.Colour)

        Apply the foreground color change except on the url.

        """
        sppasScrolledPanel.SetForegroundColour(self, colour)
        url_text = self.FindWindow('url')
        if url_text is not None:
            url_text.SetForegroundColour(wx.Colour(80, 100, 220))

    # ------------------------------------------------------------------------

    def on_link(self, event):
        """Called when url was clicked.

        :param event: (wx.Event) Un-used

        """
        try:
            webbrowser.open(sg.__url__, 1)
        except:
            pass

# ----------------------------------------------------------------------------


class AboutSPPASPanel(sppasBaseAbout):
    """About SPPAS panel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent):
        super(AboutSPPASPanel, self).__init__(parent)

        # Fix members
        self.program = sg.__name__
        self.version = sg.__version__
        self.author = sg.__author__
        self.copyright = sg.__copyright__
        self.brief = sg.__summary__
        self.url = sg.__url__
        self.logo = "sppas"
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
        # Create the panel
        self.create()

# ------------------------------------------------------------------------


class AboutPluginPanel(sppasBaseAbout):
    """About a plugin.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent, plugin):
        super(AboutPluginPanel, self).__init__(parent)

        self.program = plugin.get_name()
        if len(plugin.get_icon()) > 0:
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
            except:
                pass

        self.create()
        self.SetAutoLayout(True)

# ------------------------------------------------------------------------


class sppasAboutDialog(sppasDialog):
    """Display an about frame for SPPAS software.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent):
        super(sppasAboutDialog, self).__init__(
            parent=parent,
            title="About",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX)

        self.CreateHeader(MSG_HEADER_ABOUT, 'about')
        p = AboutSPPASPanel(self)
        self.SetContent(p)
        self.CreateActions([wx.ID_OK])
        self.LayoutComponents()

        h = self.GetFont().GetPixelSize()[1] * 50
        self.SetSize(wx.Size(h, h))
        self.FadeIn(deltaN=-8)

# ------------------------------------------------------------------------


class sppasAboutPluginDialog(sppasDialog):
    """Display an about frame for a plugin.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """
    def __init__(self, parent, plugin):
        super(sppasAboutPluginDialog, self).__init__(
            parent=parent,
            title="About",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX)

        self.CreateHeader(MSG_HEADER_ABOUT + " " + plugin.get_key() + "...", 'about')
        p = AboutPluginPanel(self, plugin)
        self.SetContent(p)
        self.CreateActions([wx.ID_OK])
        self.LayoutComponents()

        h = self.GetFont().GetPixelSize()[1] * 50
        self.SetSize(wx.Size(h, h))
        self.FadeIn(deltaN=-8)

# -------------------------------------------------------------------------


def About(parent):
    """Display the about SPPAS dialog.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    :param parent: (wx.Window)
    :returns: the response

    wx.ID_CANCEL is returned if the dialog is destroyed.

    """
    dialog = sppasAboutDialog(parent)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response

# -------------------------------------------------------------------------


def AboutPlugin(parent, plugin):
    """Display an about plugin dialog.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    :param parent: (wx.Window)
    :returns: the response

    wx.ID_CANCEL is returned if the dialog is destroyed.

    """
    dialog = sppasAboutPluginDialog(parent, plugin)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response
