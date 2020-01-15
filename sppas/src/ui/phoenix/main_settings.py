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

    ui.phoenix.main_settings.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import json
import logging
import wx

from sppas.src.config import paths
from sppas.src.config import sppasBaseSettings

# ---------------------------------------------------------------------------


class WxAppSettings(sppasBaseSettings):
    """Manage the application global settings for look&feel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create or load the dictionary of settings for the application."""
        super(WxAppSettings, self).__init__()

        fh = self.__get_font_height()
        self.size_coeff = float(fh) / 10.

    # -----------------------------------------------------------------------

    def load(self):
        """Load the dictionary of settings from a dump file.

        """
        filename = os.path.join(paths.basedir, ".uisettings")
        # Messages are sent to the python logging and not the wx one because
        # our setup_logging occurs after the settings are loaded...
        if os.path.exists(filename):
            try:
                with open(filename, "r") as fd:
                    d = json.load(fd)
                    self.__parse(d)
                    logging.info("Settings loaded from {:s}"
                                 "".format(filename))
            except Exception as e:
                self.reset()
                logging.error("Settings not loaded: {:s}. Reset to default."
                              "".format(str(e)))
        else:
            logging.info("No settings defined. Set to default.")
            self.reset()

    # -----------------------------------------------------------------------

    def save(self):
        """Save the dictionary of settings in a file.

        """
        filename = os.path.join(paths.basedir, ".uisettings")
        try:
            with open(filename, 'w') as fd:
                json.dump(self.__serialize(), fd, indent=4,
                          separators=(',', ': '))
        except Exception as e:
            logging.error("Settings not saved: {:s}."
                          "".format(str(e)))

    # -----------------------------------------------------------------------

    def reset(self):
        """Fill the dictionary with the default values."""

        font_height = self.__get_font_height()
        self.size_coeff = float(font_height) / 10.

        self.__dict__ = dict(

            frame_style=wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX,
            frame_size=self.__frame_size(),

            default_icons_theme="Refine",
            icons_theme="Refine",

            fg_color=wx.Colour(20, 20, 20),
            header_fg_color=wx.Colour(240, 240, 230),
            action_fg_color=wx.Colour(230, 230, 225),

            bg_color=wx.Colour(240, 240, 235, alpha=wx.ALPHA_OPAQUE),
            header_bg_color=wx.Colour(80, 80, 100, alpha=wx.ALPHA_OPAQUE),
            action_bg_color=wx.Colour(70, 70, 90, alpha=wx.ALPHA_OPAQUE),

            text_font=self.__text_font(),
            header_text_font=self.__header_font(),
            action_text_font=self.__action_font(),
            mono_text_font=self.__mono_font(),

            title_height=font_height * 5,
            action_height=font_height * 3,
        )

    # -----------------------------------------------------------------------

    def set(self, key, value):
        """Set a new value to a key."""
        setattr(self, key, value)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __get_font_height(self):
        # No font defined? So use the default GUI font provided by the system
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        return font.GetPixelSize()[1]

    # -----------------------------------------------------------------------

    def __get_font_pointsize(self):
        # No font defined? So use the default GUI font provided by the system
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        return font.GetPointSize()

    # -----------------------------------------------------------------------

    def __text_font(self):
        s = self.__get_font_pointsize()
        text_font = wx.Font(s,                      # point size
                            wx.FONTFAMILY_DEFAULT,  # family,
                            wx.FONTSTYLE_NORMAL,    # style,
                            wx.FONTWEIGHT_NORMAL,   # weight,
                            underline=False,
                            faceName="Lucida sans",
                            encoding=wx.FONTENCODING_SYSTEM)
        return text_font

    # -----------------------------------------------------------------------

    def __header_font(self):
        s = self.__get_font_pointsize()

        title_font = wx.Font(int(float(s)*1.5),      # point size
                             wx.FONTFAMILY_DEFAULT,  # family,
                             wx.FONTSTYLE_NORMAL,    # style,
                             wx.FONTWEIGHT_BOLD,     # weight,
                             underline=False,
                             faceName="Lucida sans",
                             encoding=wx.FONTENCODING_SYSTEM)
        return title_font

    # -----------------------------------------------------------------------

    def __action_font(self):
        s = self.__get_font_pointsize()

        button_font = wx.Font(s,                      # point size
                              wx.FONTFAMILY_DEFAULT,  # family,
                              wx.FONTSTYLE_NORMAL,    # style,
                              wx.FONTWEIGHT_NORMAL,   # weight,
                              underline=False,
                              faceName="Lucida sans",
                              encoding=wx.FONTENCODING_SYSTEM)
        return button_font

    # -----------------------------------------------------------------------

    def __mono_font(self):
        s = self.__get_font_pointsize()

        mono_font = wx.Font(s,    # point size
                            wx.FONTFAMILY_MODERN,   # family,
                            wx.FONTSTYLE_NORMAL,    # style,
                            wx.FONTWEIGHT_NORMAL,   # weight,
                            underline=False,
                            encoding=wx.FONTENCODING_SYSTEM)
        return mono_font

    # -----------------------------------------------------------------------

    def __frame_size(self):
        (w, h) = wx.GetDisplaySize()
        w = float(w)
        h = float(h)
        ratio = h / w
        w = min(0.9 * w, w * 0.6 * self.size_coeff)
        h = min(0.9 * h, w * ratio)
        return wx.Size(max(int(w), 520), max(int(h), 480))

    # -----------------------------------------------------------------------

    def __serialize(self):
        """Convert this setting dictionary into a serializable data structure.

        :returns: (dict) a dictionary that can be serialized (without classes).

        """
        d = dict()
        for k in self.__dict__:
            v = self.__dict__[k]
            if isinstance(v, wx.Font):
                d[k] = list()
                d[k].append("font")
                d[k].append(v.GetPointSize())
                d[k].append(v.GetFamily())
                d[k].append(v.GetStyle())
                d[k].append(v.GetWeight())
                d[k].append(v.GetFaceName())
            elif isinstance(v, wx.Colour):
                d[k] = list()
                d[k].append("color")
                d[k].append(v.Red())
                d[k].append(v.Green())
                d[k].append(v.Blue())
                d[k].append(v.Alpha())
            elif isinstance(v, wx.Size):
                d[k] = list()
                d[k].append("size")
                d[k].append(v[0])
                d[k].append(v[1])

        return d

    # -----------------------------------------------------------------------

    def __parse(self, d):
        """Fill in the internal dictionary with data in the given dict.

        :param d: (dict) a dictionary that can be serialized (without classes).

        """
        self.reset()
        for k in d:
            v = d[k]
            if isinstance(v, list):
                if v[0] == "font":
                    typed_v = wx.Font(*(v[1:5]), faceName=v[5])
                    setattr(self, k, typed_v)
                elif v[0] == "color":
                    typed_v = wx.Colour(*(v[1:]))
                    setattr(self, k, typed_v)
                elif v[0] == "size":
                    typed_v = wx.Size(*(v[1:]))
                    setattr(self, k, typed_v)

