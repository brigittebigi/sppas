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

    ui.phoenix.tools.py
    ~~~~~~~~~~~~~~~~~~~

"""

import os
import wx

from sppas.src.config import paths

# -----------------------------------------------------------------------


class sppasSwissKnife:
    """Create some useful tools.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    @staticmethod
    def get_bmp_icon(name, height=None, default="default"):
        """Return the bitmap corresponding to the name of an icon.

        :param name: (str) Name of an icon.
        :param height: (int) Height of the bitmap. Width=height.
        :param default: (str) Default icon if name is missing
        :returns: (wx.Bitmap)

        """
        try:
            img = sppasSwissKnife.get_image(name, default)
            w, h = img.GetSize()
            if w >= 0 and h >= 0 and height is not None:
                img.Rescale(height, height, wx.IMAGE_QUALITY_HIGH)
        except:
            img = sppasSwissKnife.get_image(default, default)
            if height is not None:
                img.Rescale(height, height, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(img)

    # ------------------------------------------------------------------------

    @staticmethod
    def get_image(name, default="default"):
        """Return the image corresponding to the name of an image or icon.

        :param name: (str) Name of an image or an icon.
        :param default: (str) Default icon if name is missing.
        :returns: (wx.Image)

        """
        img_name = sppasSwissKnife.get_image_filename(name, default)
        return wx.Image(img_name, wx.BITMAP_TYPE_ANY)

    # ------------------------------------------------------------------------

    @staticmethod
    def get_image_filename(name, default="default"):
        """Return the filename matching the given name or the default.

        :param name: (str) Name of an image or an icon.
        :param default: (str) Default icon if name is missing.

        """
        # Given "name" is already a filename
        if os.path.exists(name):
            img_name = name
        else:
            # search in the images file names
            img_name = os.path.join(paths.etc, "images", name + ".png")
            if os.path.exists(img_name) is False:
                # fix the image file name with the current icon's theme
                img_name = sppasSwissKnife.get_icon_filename(name, default)

        return img_name

    # ------------------------------------------------------------------------

    @staticmethod
    def get_icon_filename(name, default="default"):
        """Return the icon filename matching the given name or the default.

        :param name: (str) Name of an icon.
        :param default: (str) Default icon if name is missing.

        """
        # fix the icon file name with the current theme
        icon_name = os.path.join(
            paths.etc, "icons",
            wx.GetApp().settings.icons_theme,
            name + ".png")

        # instead, find the icon in the default set
        if os.path.exists(icon_name) is False:
            icon_name = os.path.join(
                paths.etc, "icons",
                "Refine",
                name + ".png")

        # instead, use the given default icon
        if os.path.exists(icon_name) is False:
            icon_name = os.path.join(
                paths.etc, "icons",
                "Refine",
                default + ".png")

        # instead, use the default icon
        if os.path.exists(icon_name) is False:
            icon_name = os.path.join(
                paths.etc, "icons",
                "Refine",
                "default.png")

        if os.path.exists(icon_name) is False:
            raise OSError("SPPAS Package corrupted: Missing default image.")

        return icon_name

    # ------------------------------------------------------------------------

    @staticmethod
    def rescale_image(img, height):
        """Rescale proportionally an image.

        :return: (int) width or -1 if failed.

        """
        w, h = img.GetSize()
        if w <= 0 or h <= 0:
            return -1
        proportion = float(height) / float(img.GetHeight())
        w = int(float(img.GetWidth()) * proportion)
        img.Rescale(w, height, wx.IMAGE_QUALITY_HIGH)
        return w

    # ------------------------------------------------------------------------

    @staticmethod
    def get_bmp_image(name, height=None):
        """Return the bitmap corresponding to the name of an image.

        :param name: (str) Name of an image or an icon.
        :param height: (int) Height of the bitmap, Width is proportional.
        :returns: (wx.Bitmap)

        """
        img = sppasSwissKnife.get_image(name)
        if height is not None:
            sppasSwissKnife.rescale_image(img, height)

        return wx.Bitmap(img)   # Cause pb under Windows: wx.BITMAP_TYPE_PNG
