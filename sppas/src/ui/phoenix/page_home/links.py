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

    ui.phoenix.page_home.links.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import webbrowser

from ..windows import Button
from ..windows import WindowState
from ..tools import sppasSwissKnife

# ---------------------------------------------------------------------------


class LinkButton(Button):

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Default class constructor.

        :param parent: the parent (required);
        :param id: window identifier.
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        By default, the name of the button is the name of its bitmap.

        The label is optional.
        By default, the label is under the bitmap.

        """
        super(LinkButton, self).__init__(
            parent, id, pos, size, name)
        self.SetBorderWidth(1)
        # The url
        self._label = ""
        self._url = ""
        self._color = wx.Colour(128, 128, 128, 128)
        # The icon image
        self._image = None
        if name != wx.ButtonNameStr:
            self.SetImage(name)

    # ----------------------------------------------------------------------

    def Enable(self, enable=True):
        """Enable or disable the window.

        :param enable: (bool) True to enable the window.

        """
        Button.Enable(self, enable)
        self.SetForegroundColour(self.GetForegroundColour())

    # -----------------------------------------------------------------------

    def SetImage(self, image_name):
        """Set a new image.

        :param image_name: (str) Name of the image or full filename

        """
        self._image = image_name

    # -----------------------------------------------------------------------

    def DoGetBestSize(self):
        """Overridden base class virtual.

        Determines the best size of the button based on the label.

        """
        label = self.GetLabel()
        if not label:
            return wx.Size(32, 32)

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        ret_width, ret_height = dc.GetTextExtent(label)

        width = int(max(ret_width, ret_height*4) * 1.5)
        return wx.Size(width, width)

    # -----------------------------------------------------------------------

    def GetLinkLabel(self):
        """Return the label text as it was passed to SetLabel."""
        return self._label

    # ------------------------------------------------------------------------

    def SetLinkLabel(self, label):
        """Set the label text.

        :param label: (str) Label text.

        """
        self._label = label

    # -----------------------------------------------------------------------

    def GetLinkBgColour(self):
        """Color of the background of the label."""
        return self._color

    def SetLinkBgColour(self, color):
        self._color = color

    # -----------------------------------------------------------------------

    def GetLinkURL(self):
        """Return the url as it was passed to SetLabel."""
        return self._url

    # ------------------------------------------------------------------------

    def SetLinkURL(self, url):
        """Set the url to open when button is clicked.

        :param url: (str) URL to open.

        """
        self._url = url

    # ------------------------------------------------------------------------
    # Methods to draw the button
    # ------------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        x, y, w, h = self.GetContentRect()
        print("{} Draw content: x={}, h={}".format(self.GetName(), x, h))

        if w >= 4 and h >= 4:
            color = self.GetPenForegroundColour()
            pen = wx.Pen(color, 1, self._border_style)
            dc.SetPen(pen)

            # No label is defined.
            # Draw the square bitmap icon at the center with a 5% margin all around
            if self._label is None:
                x_pos, y_pos, bmp_size = self.__get_bitmap_properties(x, y, w, h)
                designed = self.__draw_bitmap(dc, gc, x_pos, y_pos, bmp_size)
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
        spacing = th // 2

        # spacing is applied vertically
        print("Draw content label: x={}, h={}".format(x, h))
        x_bmp, y_pos, bmp_size = self.__get_bitmap_properties(
            x, y + th + spacing,
            w, h - th - (2 * spacing))
        if bmp_size > 15:
            margin = h - bmp_size - th - spacing
            y += (margin // 2)

        self.__draw_bitmap(dc, gc, x_bmp, y, bmp_size)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self._color, wx.BRUSHSTYLE_SOLID))
        dc.DrawRectangle(self._horiz_border_width, h - th - spacing,
                         w, th+(2*spacing))
        self.__draw_label(dc, gc, (w - tw) // 2, h - th)

    # -----------------------------------------------------------------------

    def __get_bitmap_properties(self, x, y, w, h):
        # w, h is the available size
        bmp_size = min(w, h)                  # force a squared button
        margin = max(int(bmp_size * 0.2), 2)  # optimal margin (20% of btn size)
        bmp_size -= margin
        y_pos = y + ((h - bmp_size) // 2)
        x_pos = x + ((w - bmp_size) // 2)

        return x_pos, y_pos, bmp_size

    # -----------------------------------------------------------------------

    def __draw_bitmap(self, dc, gc, x, y, btn_size):
        # if no image was given
        if self._image is None:
            return False

        try:
            # get the image from its name
            img = sppasSwissKnife.get_image(self._image)
            # re-scale the image to the expected size
            sppasSwissKnife.rescale_image(img, btn_size)
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

    # -----------------------------------------------------------------------

    @staticmethod
    def get_text_extend(dc, gc, text):
        if wx.Platform == '__WXGTK__':
            return dc.GetTextExtent(text)
        return gc.GetTextExtent(text)

    # -----------------------------------------------------------------------

    def __draw_label(self, dc, gc, x, y):
        # self.DrawLabel(self._label, dc, gc, x, y)
        font = self.GetFont()
        gc.SetFont(font)
        gc.SetTextForeground(self.GetPenForegroundColour())
        gc.DrawText(self._label, x, y)

    # -----------------------------------------------------------------------

    def OnMouseLeftDown(self, event):
        """Handle the wx.EVT_LEFT_DOWN event.

        :param event: a wx.MouseEvent event to be processed.

        """
        if self.IsEnabled() is False:
            return

        self.CaptureMouse()
        self.SetFocus()
        self._set_state(WindowState().selected)

    # -----------------------------------------------------------------------

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        # No URL was defined, or
        # the link button is not enabled, or
        # the mouse was down outside of the button (but is up inside)
        if len(self._url) == 0 or self.IsEnabled() is False or \
                self.HasCapture() is False:
            return

        # Directs all mouse input to this window
        self.ReleaseMouse()

        webbrowser.open(url=self._url)

# ----------------------------------------------------------------------------


class TestPanelLinksButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelLinksButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test BitmapButton")

        b1 = LinkButton(self, pos=(10, 10), size=(150, 150), name="SPPAS")
        b1.SetLinkLabel("SPPAS Home")
        b1.SetLinkBgColour(wx.Colour(200, 20, 20, 120))
        b2 = LinkButton(self, pos=(170, 10), size=(150, 150))
        b3 = LinkButton(self, pos=(340, 10), size=(200, 150), name="like")
        b4 = LinkButton(self, pos=(560, 10), size=(150, 100))
        b4.SetLinkLabel("Search...")
        b4.SetLinkURL("https://duckduckgo.com/")




