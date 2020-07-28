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
from ..windows import sppasPanel
from ..tools import sppasSwissKnife

# ---------------------------------------------------------------------------


class LinkButton(Button):
    """A button to get access to an URL.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    This window is implemented as "the focus follows mouse" so that when the
    mouse is over the window, it gives it the focus.

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 name=wx.ButtonNameStr):
        """Create a custom button to get access to an URL.

        :param parent: the parent (required);
        :param id: window identifier.
        :param pos: the position;
        :param size: the size;
        :param name: the name of the bitmap.

        By default, the name of the button is the name of its image.
        The label is optional.
        The label is under the bitmap with a colored background.

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
            return wx.Size(self._min_width, self._min_height)

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

    # -----------------------------------------------------------------------

    def SetLinkBgColour(self, color):
        """Color of the background of the label.

        :param color: (wx.Colour)

        """
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
        self._url = str(url)

    # ------------------------------------------------------------------------
    # Methods to draw the button
    # ------------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Draw the link button with an image at top and a label at bottom.

        Don't draw if the size is not large enough.

        """
        x, y, w, h = self.GetContentRect()

        if w >= self._min_width and h >= self._min_height:

            # No label is defined.
            if self._label is None:
                self._DrawContentWithoutLabel(dc, gc, x, y, w, h)
            else:
                self._DrawContentWithLabel(dc, gc, x, y, w, h)

    # -----------------------------------------------------------------------

    def _DrawContentWithoutLabel(self, dc, gc, x, y, w, h):
        """Draw the square bitmap at the center with a margin all around.

        """
        x_pos, y_pos, bmp_size = self.__get_bitmap_properties(x, y, w, h)
        designed = self.__draw_bitmap(dc, gc, x_pos, y_pos, bmp_size)
        if designed is False:
            color = self.GetPenForegroundColour()
            pen = wx.Pen(color, 1, self._border_style)
            dc.SetPen(pen)
            pen.SetCap(wx.CAP_BUTT)
            dc.DrawRectangle(self._vert_border_width,
                             self._horiz_border_width,
                             w - (2 * self._vert_border_width),
                             h - (2 * self._horiz_border_width))

    # -----------------------------------------------------------------------

    def _DrawContentWithLabel(self, dc, gc, x, y, w, h):
        tw, th = self.get_text_extend(dc, gc, self._label)

        # a spacing is applied vertically
        spacing = th // 2
        x_bmp, y_pos, bmp_size = self.__get_bitmap_properties(
            x, y + th + spacing,
            w, h - th - (2 * spacing))
        if bmp_size > 15:
            margin = h - bmp_size - th - spacing
            y += (margin // 2)

        # Draw the bitmap at top
        self.__draw_bitmap(dc, gc, x_bmp, y, bmp_size)

        # Draw the background of the label at bottom
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self._color, wx.BRUSHSTYLE_SOLID))
        # we draw the background of the focus line with the same color
        bg_h = th + spacing + self._vert_border_width + self._focus_width + self._focus_spacing
        dc.DrawRectangle(x, h - th - spacing, w, bg_h)

        self.__draw_label(dc, gc, (w - tw) // 2, h - th)

    # -----------------------------------------------------------------------

    def __get_bitmap_properties(self, x, y, w, h):
        # w, h is the available size
        bmp_size = min(w, h)                  # force a squared button
        margin = max(int(bmp_size * 0.3), 2)  # optimal margin (30% of btn size)
        bmp_size -= margin
        y_pos = y + ((h - bmp_size) // 2)
        x_pos = x + ((w - bmp_size) // 2)

        return x_pos, y_pos, bmp_size

    # -----------------------------------------------------------------------

    def __draw_bitmap(self, dc, gc, x, y, btn_size):
        # if no image was given
        if self._image is None:
            return False
        if btn_size < 4:
            return

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

    def OnMouseLeftUp(self, event):
        """Handle the wx.EVT_LEFT_UP event.

        :param event: a wx.MouseEvent event to be processed.

        """
        # the link button is not enabled, or
        if self.IsEnabled() is False:
            return

        # Mouse was down outside of the window but is up inside.
        if self.HasCapture() is False:
            return

        # Stop to redirect all mouse inputs to this window
        self.ReleaseMouse()

        if self._state[1] == WindowState().selected:
            self._set_state(WindowState().focused)

            self.Refresh()
            # No URL was defined, or
            # the mouse was down outside of the button (but is up inside)
            if len(self._url) > 0:
                webbrowser.open(url=self._url)

# ----------------------------------------------------------------------------


class sppasLinksPanel(sppasPanel):
    """A panel with buttons to get access to SPPAS on the web.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasLinksPanel, self).__init__(
            parent=parent,
            name="welcome_panel",
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.TAB_TRAVERSAL
        )
        self._create_content()

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        b1 = LinkButton(self, name="sppas_colored")
        b1.SetLinkLabel("SPPAS Home")
        b1.SetLinkURL("http://www.sppas.org/")
        b1.SetLinkBgColour(wx.Colour(87, 109, 159, 128))
        b1.SetMinSize(wx.Size(sppasPanel.fix_size(82), sppasPanel.fix_size(112)))

        b2 = LinkButton(self, name="link_docweb")
        b2.SetLinkLabel("Documentation")
        b2.SetLinkURL("http://www.sppas.org/documentation.html")
        b2.SetLinkBgColour(wx.Colour(241, 211, 79, 128))
        b2.SetMinSize(wx.Size(sppasPanel.fix_size(82), sppasPanel.fix_size(112)))

        b3 = LinkButton(self, name="link_tutovideo")
        b3.SetLinkLabel("Tutorials")
        b3.SetLinkURL("http://www.sppas.org/tutorial.html")
        b3.SetLinkBgColour(wx.Colour(0, 160, 40, 128))
        b3.SetMinSize(wx.Size(sppasPanel.fix_size(82), sppasPanel.fix_size(112)))

        b4 = LinkButton(self, name="link_question")
        b4.SetLinkLabel("F.A.Q.")
        b4.SetLinkURL("http://www.sppas.org/faq.html")
        b4.SetLinkBgColour(wx.Colour(220, 120, 40, 128))
        b4.SetMinSize(wx.Size(sppasPanel.fix_size(82), sppasPanel.fix_size(112)))

        b5 = LinkButton(self, name="link_author")
        b5.SetLinkLabel("The author")
        b5.SetLinkURL("http://www.lpl-aix.fr/~bigi/")
        b5.SetLinkBgColour(wx.Colour(50, 50, 150, 128))
        b5.SetMinSize(wx.Size(sppasPanel.fix_size(82), sppasPanel.fix_size(112)))

        # Organize the title and message
        b = sppasPanel.fix_size(12)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(b1, 0, wx.ALL, b)
        sizer.Add(b2, 0, wx.TOP | wx.BOTTOM | wx.RIGHT, b)
        sizer.Add(b3, 0, wx.TOP | wx.BOTTOM | wx.RIGHT, b)
        sizer.Add(b4, 0, wx.TOP | wx.BOTTOM | wx.RIGHT, b)
        sizer.Add(b5, 0, wx.RIGHT | wx.TOP | wx.BOTTOM, b)

        self.SetSizer(sizer)

# ----------------------------------------------------------------------------


class TestPanelLinksButton(wx.Panel):

    def __init__(self, parent):
        super(TestPanelLinksButton, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test Links Buttons and Panel")

        p = sppasPanel(self)
        b1 = LinkButton(p, pos=(10, 10), size=(150, 150), name="SPPAS")
        b1.SetLinkLabel("SPPAS Home")
        b1.SetLinkBgColour(wx.Colour(200, 20, 20, 120))
        b2 = LinkButton(p, pos=(170, 10), size=(150, 150))
        b3 = LinkButton(p, pos=(340, 10), size=(200, 150), name="like")
        b4 = LinkButton(p, pos=(560, 10), size=(150, 100))
        b4.SetLinkLabel("Search...")
        b4.SetLinkURL("https://duckduckgo.com/")

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p, 0, wx.ALL, 0)
        s.AddStretchSpacer(1)
        s.Add(sppasLinksPanel(self), 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(s)



