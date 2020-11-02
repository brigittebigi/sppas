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

    src.ui.phoenix.windows.buttons.bitmapbutton.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A button with a bitmap, and eventually a label text.
    
"""

import random
import wx

from ...tools import sppasSwissKnife
from ..image import ColorizeImage
from ..basewindow import sppasWindow
from .textbutton import TextButton

# ---------------------------------------------------------------------------


class BitmapTextButton(TextButton):
    """BitmapTextButton is a custom button with a label text.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 label="",
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param label: label text of the check button;
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        """
        self._spacing = 4
        self._default_bitmapcolor =  wx.WHITE
        self._bitmapcolor = self._default_bitmapcolor
        self._labelpos = wx.CENTER
        self.img_margin = 0.2  # margin all around the image (20% of btn size)
        super(BitmapTextButton, self).__init__(parent, id, label, pos, size, name)

        # The icon image
        self._icon_image = None
        if name != wx.ButtonNameStr:
            self.SetImage(name)

        # Update colors
        self._default_bitmapcolor = self.GetPenForegroundColour()
        self._bitmapcolor = self._default_bitmapcolor

    # ----------------------------------------------------------------------

    def Enable(self, enable=True):
        """Enable or disable the window.

        :param enable: (bool) True to enable the window.

        """
        sppasWindow.Enable(self, enable)
        self.SetForegroundColour(self.GetForegroundColour())

    # -----------------------------------------------------------------------

    def SetImage(self, image_name):
        """Set a new image.

        :param image_name: (str) Name of the image or full filename

        """
        self._icon_image = image_name

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to both the image and the text.

        :param colour: (wx.Colour)

        """
        TextButton.SetForegroundColour(self, colour)

        if self._bitmapcolor == self._default_bitmapcolor:
            self._bitmapcolor = self.GetPenForegroundColour()
        self._default_bitmapcolor = self.GetPenForegroundColour()

    # -----------------------------------------------------------------------

    def GetBitmapColour(self):
        return self._bitmapcolor

    def SetBitmapColour(self, color):
        self._bitmapcolor = color

    # -----------------------------------------------------------------------

    def GetSpacing(self):
        return self._spacing

    def SetSpacing(self, value):
        self._spacing = max(int(value), 2)

    # -----------------------------------------------------------------------

    def GetLabelPosition(self):
        return self._labelpos

    def SetLabelPosition(self, pos=wx.BOTTOM):
        """Set the position of the label: top, bottom, left, right."""
        if pos not in [wx.TOP, wx.BOTTOM, wx.LEFT, wx.RIGHT]:
            return
        self._labelpos = pos

    # -----------------------------------------------------------------------

    BitmapColour = property(GetBitmapColour, SetBitmapColour)
    Spacing = property(GetSpacing, SetSpacing)
    LabelPosition = property(GetLabelPosition, SetLabelPosition)

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        x, y, w, h = self.GetContentRect()
        x += self._vert_border_width
        y += self._horiz_border_width
        w -= (2 * self._vert_border_width)
        h -= ((2 * self._horiz_border_width) + self._focus_width + 2)

        if w >= 4 and h >= 4:
            color = self.GetPenForegroundColour()
            pen = wx.Pen(color, 1, self._border_style)
            dc.SetPen(pen)

            # No label is defined.
            # Draw the square bitmap icon at the center with a 5% margin all around
            if self._label is None or len(self._label) == 0:
                x_pos, y_pos, bmp_size = self.__get_bitmap_properties(x, y, w, h)
                designed = self._draw_bitmap(dc, gc, x_pos, y_pos, bmp_size)
                if designed is False:
                    pen.SetCap(wx.CAP_BUTT)
                    dc.DrawRectangle(self._vert_border_width,
                                     self._horiz_border_width,
                                     w - (2 * self._vert_border_width),
                                     h - (2 * self._horiz_border_width))
            else:
                self._DrawContentLabel(dc, gc, x, y, w, h)

    # -----------------------------------------------------------------------

    def _DrawContentLabel(self, dc, gc, x, y, w, h):

        tw, th = self.get_text_extend(dc, gc, self._label)

        if self._labelpos == wx.BOTTOM or self._labelpos == wx.TOP:
            # spacing is applied vertically
            x_bmp, y_pos, bmp_size = self.__get_bitmap_properties(
                x, y + th + self._spacing,
                w, h - th - 2 * self._spacing)
            if bmp_size > 15:
                margin = h - bmp_size - th - self._spacing
                y += (margin // 2)

            if self._labelpos == wx.BOTTOM:
                #self.__draw_bitmap(dc, gc, (w - bmp_size) // 2, y, bmp_size)
                self._draw_bitmap(dc, gc, x_bmp, y, bmp_size)
                self._draw_label(dc, gc, (w - tw) // 2, h - th)

            if self._labelpos == wx.TOP:
                self._draw_label(dc, gc, (w - tw) // 2, y)
                self._draw_bitmap(dc, gc, x_bmp, y_pos, bmp_size)

        if self._labelpos == wx.LEFT or self._labelpos == wx.RIGHT:
            # spacing is applied horizontally
            x_bmp, y_bmp, bmp_size = self.__get_bitmap_properties(
                x, y, w - tw - self._spacing, h)

            if bmp_size > 8:
                margin = w - bmp_size - tw - self._spacing
                if self._align == wx.ALIGN_RIGHT:
                    x += margin
                elif self._align == wx.ALIGN_CENTER:
                    x += (margin // 2)

                if self._labelpos == wx.LEFT:
                    self._draw_label(dc, gc, x, (h - (th//2)) // 2)
                    self._draw_bitmap(dc, gc, x_bmp + self._spacing + tw, y_bmp, bmp_size)

                if self._labelpos == wx.RIGHT:
                    self._draw_bitmap(dc, gc, x_bmp, y_bmp, bmp_size)
                    self._draw_label(dc, gc, x_bmp + bmp_size + self._spacing, (h - (th//2)) // 2)

            else:
                # not enough room for a bitmap.
                if self._align == wx.ALIGN_CENTER:
                    self._draw_label(dc, gc, (w - tw) // 2, (h - (th//2)) // 2)
                elif self._align == wx.ALIGN_LEFT:
                    self._draw_label(dc, gc, x, (h - (th//2)) // 2)
                elif self._align == wx.ALIGN_RIGHT:
                    self._draw_label(dc, gc, (w - tw), (h - (th//2)) // 2)

    # -----------------------------------------------------------------------

    def __get_bitmap_properties(self, x, y, w, h):
        # w, h is the available size
        bmp_size = min(w, h)                  # force a squared button
        margin = max(int(bmp_size * self.img_margin), 2)
        bmp_size -= margin
        y_pos = y + (margin // 2)
        if self._align == wx.ALIGN_LEFT:
            x_pos = x
        elif self._align == wx.ALIGN_RIGHT:
            x_pos = w - bmp_size
        else:
            x_pos = x + (margin // 2)

        if w < h:
            y_pos = (h - bmp_size) // 2
        else:
            if self._align == wx.ALIGN_CENTER:
                x_pos = (w - bmp_size) // 2

        return x_pos, y_pos, bmp_size

    # -----------------------------------------------------------------------

    def _draw_bitmap(self, dc, gc, x, y, btn_size):
        # if no image was given
        if self._icon_image is None:
            return False

        try:
            # get the image from its name
            img = sppasSwissKnife.get_image(self._icon_image)
            # re-scale the image to the expected size
            sppasSwissKnife.rescale_image(img, btn_size)
            # re-colorize
            ColorizeImage(img, wx.BLACK, self._bitmapcolor)
            # convert to bitmap
            bitmap = wx.Bitmap(img)
            # draw it to the dc or gc
            if wx.Platform == '__WXGTK__':
                dc.DrawBitmap(bitmap, x, y)
            else:
                gc.DrawBitmap(bitmap, x, y)
        except Exception as e:
            wx.LogWarning('Draw image error: {:s}'.format(str(e)))
            return False

        return True

# ---------------------------------------------------------------------------


class BitmapButton(BitmapTextButton):
    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """A BitmapTextButton, without the text.

        :param parent: the parent (required);
        :param id: window identifier.
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        """
        super(BitmapButton, self).__init__(
            parent, id, None, pos, size, name)
        self._spacing = 0

# ---------------------------------------------------------------------------


class TestPanelBitmapButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelBitmapButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test BitmapButton")

        b1 = BitmapButton(self, pos=(10, 10), size=(50, 50))
        b2 = BitmapButton(self, pos=(70, 10), size=(50, 50))
        b3 = BitmapButton(self, pos=(130, 10), size=(100, 50), name="like")
        b4 = BitmapButton(self, pos=(240, 10), size=(30, 50), name="like")
        b5 = BitmapButton(self, pos=(280, 10), size=(30, 30), name="like")
        b6 = BitmapButton(self, pos=(320, 10), size=(50, 30), name="like")
        b7 = BitmapButton(self, pos=(380, 10), size=(50, 50), name="add")
        b7.SetFocusColour(wx.Colour(30, 120, 240))
        b7.SetFocusWidth(3)
        b7.SetFocusStyle(wx.PENSTYLE_SOLID)
        b8 = BitmapTextButton(self, pos=(440, 10), size=(50, 50), name="remove")
        b8.SetFocusColour(wx.Colour(30, 120, 240))
        b8.SetBitmapColour(wx.Colour(230, 120, 40))
        b8.SetFocusWidth(3)
        b8.SetFocusStyle(wx.PENSTYLE_SOLID)
        b9 = BitmapTextButton(self, pos=(500, 10), size=(50, 50), name="delete")
        b9.SetFocusColour(wx.Colour(30, 120, 240))
        b9.SetBitmapColour(wx.Colour(240, 10, 10))
        b9.SetFocusWidth(3)
        b9.SetFocusStyle(wx.PENSTYLE_SOLID)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

# ----------------------------------------------------------------------------


class TestPanelBitmapTextButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelBitmapTextButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test TextBitmapButton")

        bgpbtn = wx.Button(self, label="BG-panel", pos=(10, 10), size=(64, 64), name="bgp_color")
        bgbbtn = wx.Button(self, label="BG-buttons", pos=(110, 10), size=(64, 64), name="bgb_color")
        fgbtn = wx.Button(self, label="FG", pos=(210, 10), size=(64, 64), name="font_color")
        self.Bind(wx.EVT_BUTTON, self.on_bgp_color, bgpbtn)
        self.Bind(wx.EVT_BUTTON, self.on_bgb_color, bgbbtn)
        self.Bind(wx.EVT_BUTTON, self.on_fg_color, fgbtn)

        b1 = BitmapTextButton(self, label="button size is too small for this text",
                              pos=(10, 100), size=(50, 50),
                              name="sppas_64")

        b2 = BitmapTextButton(self, label="toto",
                              pos=(70, 100), size=(150, 50),
                              name="sppas_32")

        b3 = BitmapTextButton(self, label="sppas_colored",
                              pos=(300, 100), size=(50, 50),
                              name="sppas_colored")
        b3.SetBorderWidth(1)
        b3.SetLabel("RENAMED")
        b3.Refresh()

        b4 = BitmapTextButton(self, label="Add", pos=(40, 200), size=(200, 50), name="add")
        b4.SetBorderWidth(2)
        b4.SetLabel("ADD")
        b4.SetLabelPosition(wx.RIGHT)
        b4.Refresh()

        b5 = BitmapTextButton(self, label="Add", pos=(350, 200), size=(100, 50), name="add_lower")
        b5.SetLabelPosition(wx.LEFT)

        b6 = BitmapTextButton(self, label="Room for a tiny bitmap", pos=(460, 200), size=(150, 50), name="tiny")
        b6.SetLabelPosition(wx.LEFT)

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            c.SetForegroundColour(colour)

    # -----------------------------------------------------------------------

    def on_bgp_color(self, event):
        """Change BG color of the panel. It shouldn't change bg of buttons."""
        self.SetBackgroundColour(wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250)
        ))
        self.Refresh()

    # -----------------------------------------------------------------------

    def on_bgb_color(self, event):
        """Change BG color of the buttons. A refresh is needed."""
        for child in self.GetChildren():
            if isinstance(child, TextButton):
                child.SetBackgroundColour(wx.Colour(
                    random.randint(10, 250),
                    random.randint(10, 250),
                    random.randint(10, 250)
                    ))
                child.Refresh()

    # -----------------------------------------------------------------------

    def on_fg_color(self, event):
        color = wx.Colour(
            random.randint(10, 250),
            random.randint(10, 250),
            random.randint(10, 250))
        self.SetForegroundColour(color)
        for c in self.GetChildren():
            c.SetForegroundColour(color)
        self.Refresh()
