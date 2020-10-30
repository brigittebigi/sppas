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

    src.ui.phoenix.windows.panel.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A panel is a window on which controls are placed.
    Panels of SPPAS allow to propagate properly fonts and colors defined in
    the settings.

"""

import wx
import os
import wx.lib.scrolledpanel as sc

from sppas.src.config import paths   # used only for the test

# ---------------------------------------------------------------------------


class sppasPanel(wx.Panel):
    """A panel with colors and fonts defined in the settings.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    Possible constructors:

        - sppasPanel()
        - sppasPanel(parent, id=ID_ANY, pos=DefaultPosition, size=DefaultSize,
              style=TAB_TRAVERSAL, name=PanelNameStr)

    """

    def __init_(self, parent, id=-1,
                pos=wx.DefaultPosition, size=wx.DefaultSize,
                style=0, name="sppas_panel"):
        # always turn on tab traversal
        style |= wx.TAB_TRAVERSAL

        # and turn off any border styles
        style &= ~wx.BORDER_MASK
        style |= wx.BORDER_NONE

        super(sppasPanel, self).__init__(parent, id, pos, size, style, name)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.SetAutoLayout(True)
        self.SetMinSize(wx.Size(self.fix_size(320),
                                self.fix_size(200)))

    # -----------------------------------------------------------------------

    def ShouldInheritColours(self):
        try:
            wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # -----------------------------------------------------------------------

    def InheritsBackgroundColour(self):
        try:
            wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # -----------------------------------------------------------------------

    def InheritsForegroundColour(self):
        try:
            wx.GetApp().settings
            return False
        except AttributeError:
            return True

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        wx.Panel.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override."""
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        wx.Panel.SetFont(self, font)
        for c in self.GetChildren():
            c.SetFont(font)
        self.Layout()

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_size(value):
        """Return a proportional size value.

        :param value: (int)
        :returns: (int)

        """
        try:
            obj_size = int(float(value) * wx.GetApp().settings.size_coeff)
        except AttributeError:
            obj_size = int(value)
        return obj_size

    # -----------------------------------------------------------------------

    def get_font_height(self):
        """Return the height of the in-use font."""
        try:
            font = wx.GetApp().settings.text_font
        except AttributeError:
            font = self.GetFont()
        return int(float(font.GetPixelSize()[1]))

# ---------------------------------------------------------------------------


class sppasTransparentPanel(sppasPanel):
    """Create a panel with a transparent background.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="transparent_panel"):
        # always turn on transparency
        style |= wx.TRANSPARENT_WINDOW

        super(sppasTransparentPanel, self).__init__(parent, id, pos, size, style, name)

        # Bind the events related to our window
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        return

    # -----------------------------------------------------------------------

    def OnEraseBackground(self, evt):
        """Trap the erase event to be transparent even under windows.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        pass

# ---------------------------------------------------------------------------


class sppasImagePanel(sppasPanel):
    """Create a panel with an optional image as background.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 image=None,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=0,
                 name="imgbg_panel"):
        self._image = None
        super(sppasImagePanel, self).__init__(parent, id, pos, size, style, name)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(384),
                                sppasPanel.fix_size(128)))
        if image is not None:
            self.SetBackgroundImage(image)

        # Bind the events related to our window
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    # -----------------------------------------------------------------------

    def SetBackgroundImage(self, img_filename=None):
        """Set the image filename but do not refresh.

        :param img_filename: (str) None to disable the BG image

        """
        self._image = None
        if img_filename is not None and os.path.exists(img_filename) is True:
            try:
                self._image = wx.Image(img_filename, wx.BITMAP_TYPE_ANY)
                return True
            except:
                pass

        return False

    # -----------------------------------------------------------------------

    def SetBackgroundImageArray(self, img):
        """Set the image from a numpy array but do not refresh.

        :param img: (sppasImage) Numpy array of the image

        """
        try:
            width = img.shape[1]
            height = img.shape[0]
            self._image = wx.Image(width, height)
            self._image.SetData(img.tostring())
            return True
        except:
            pass
        self._image = None
        return False

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        return

    # -----------------------------------------------------------------------

    def OnEraseBackground(self, evt):
        """Trap the erase event to draw the image as background.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        if isinstance(self._image, wx.Image) is True:
            dc = evt.GetDC()
            if not dc:
                dc = wx.ClientDC(self)
            dc.Clear()
            w, h = self.GetClientSize()

            img = self._image.Copy()
            img.Rescale(w, h, wx.IMAGE_QUALITY_HIGH)
            bmp = wx.Bitmap(img, wx.BITMAP_TYPE_PNG)
            dc.DrawBitmap(bmp, 0, 0)

# ---------------------------------------------------------------------------
# Panel to test
# ---------------------------------------------------------------------------


class TestPanel(sc.ScrolledPanel):

    img1 = os.path.join(paths.samples, "faces", "BrigitteBigi_Aix2020.png")
    img2 = os.path.join(paths.etc, "images", "trbg1.png")

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.HSCROLL | wx.VSCROLL,
            name="Test Panels")

        p1 = sppasPanel(self)
        self.MakePanelContent(p1)

        p2 = sppasTransparentPanel(self)
        self.MakePanelContent(p2)

        # No image defined. It's the default one.
        p5 = sppasImagePanel(self)
        self.MakePanelContent(p5)
        # bg transparent image defined.
        p6 = sppasImagePanel(self, image=TestPanel.img2)
        self.MakePanelContent(p6)
        # A bg image defined.
        p7 = sppasImagePanel(self, image=TestPanel.img1)
        self.MakePanelContent(p7)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p1, 0, wx.EXPAND)
        sizer.Add(p2, 0, wx.EXPAND)
        sizer.Add(p5, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p6, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p7, 0, wx.EXPAND | wx.ALL, border=10)

        self.SetSizerAndFit(sizer)
        self.Layout()
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.SetAutoLayout(True)
        self.Refresh()

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def MakePanelContent(self, pane):
        """Just make a few controls to put on the collapsible pane."""
        nameLbl = wx.StaticText(pane, -1, "Name:")
        name = wx.TextCtrl(pane, -1, "")

        addrLbl = wx.StaticText(pane, -1, "Address:")
        addr1 = wx.TextCtrl(pane, -1, "")
        addr2 = wx.TextCtrl(pane, -1, "")

        cstLbl = wx.StaticText(pane, -1, "City, State, Zip:")
        city = wx.TextCtrl(pane, -1, "", size=(150, -1))
        state = wx.TextCtrl(pane, -1, "", size=(50, -1))
        zip = wx.TextCtrl(pane, -1, "", size=(70, -1))

        addrSizer = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        addrSizer.AddGrowableCol(1)
        addrSizer.Add(nameLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(name, 0, wx.EXPAND)
        addrSizer.Add(addrLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(addr1, 0, wx.EXPAND)
        addrSizer.Add((5, 5))
        addrSizer.Add(addr2, 0, wx.EXPAND)

        addrSizer.Add(cstLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        cstSizer = wx.BoxSizer(wx.HORIZONTAL)
        cstSizer.Add(city, 1)
        cstSizer.Add(state, 0, wx.LEFT | wx.RIGHT, 5)
        cstSizer.Add(zip)
        addrSizer.Add(cstSizer, 0, wx.EXPAND)

        border = wx.BoxSizer()
        border.Add(addrSizer, 1, wx.EXPAND | wx.ALL, 5)
        pane.SetSizer(border)
        pane.Layout()

    def OnSize(self, evt):
        self.Layout()
