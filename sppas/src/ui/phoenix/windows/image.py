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

    src.ui.phoenix.windows.image.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import logging

from ..tools import sppasSwissKnife

# ---------------------------------------------------------------------------


def ColorizeImage(img, current, colour):
    """Set new foreground to an image.

    :param img: (wx.Image)
    :param current: (wx.Colour) Current color
    :param colour: (wx.Colour) New colour

    """
    r = current.Red()
    g = current.Green()
    b = current.Blue()
    rr = colour.Red()
    gg = colour.Green()
    bb = colour.Blue()

    for i in range(0, 10):
        img.Replace(max(r - i, 0),
                    max(g - i, 0),
                    max(b - i, 0),
                    max(rr - i, 0),
                    max(gg - i, 0),
                    max(bb - i, 0))
        img.Replace(min(r + i, 255),
                    min(g + i, 255),
                    min(b + i, 255),
                    min(rr + i, 255),
                    min(gg + i, 255),
                    min(bb + i, 255))

# ---------------------------------------------------------------------------


class sppasStaticBitmap(wx.StaticBitmap):

    def __init__(self, parent, bmp_name, height=None):

        if height is None:
            height = int(parent.GetSize()[1]) - 2
        bmp = sppasSwissKnife.get_bmp_icon(bmp_name, height)

        super(sppasStaticBitmap, self).__init__(
            parent=parent,
            id=wx.ID_ANY,
            bitmap=bmp,
            name=bmp_name
        )

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to the image.

        :param colour: (wx.Colour)

        """
        try:
            bmp = self.GetBitmap()
            img = bmp.ConvertToImage()
            current = self.GetForegroundColour()
            ColorizeImage(img, current, colour)
            self.SetBitmap(wx.Bitmap(img))
        except:
            logging.debug('SetForegroundColour not applied to image'
                          'for button {:s}'.format(self.GetName()))

        wx.StaticBitmap.SetForegroundColour(self, colour)
