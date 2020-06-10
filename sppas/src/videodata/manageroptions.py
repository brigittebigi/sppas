# -*- coding : UTF-8 -*-
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
    src.videodata.manageroptions.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from sppas.src.structs.baseoption import sppasBaseOption
# ---------------------------------------------------------------------------


class ManagerOptions(object):
    """Class to manage options.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    # The framing options
    FRAMING = ["face", "portrait"]

    # The mode options
    MODE = ["full", "crop"]

    # The draw options
    DRAW = ["circle", "ellipse", "square"]

    def __init__(self, pattern, usable=False, csv=False, video=False, folder=False):
        """Create a new ManagerOptions instance."""

        # The dictionary of options
        self.__output = {"usable": sppasBaseOption("bool", False), "csv": sppasBaseOption("bool", False),
                         "video": sppasBaseOption("bool", False), "folder": sppasBaseOption("bool", False)}

        # The framing to use, face or portrait
        self.__framing = sppasBaseOption("str", None)
        # The mode to use, full or crop
        self.__mode = sppasBaseOption("str", None)
        # The shape to draw, circle, ellipse or rectangle
        self.__draw = sppasBaseOption("str", None)

        # The width you want for the outputs files
        self.__width = sppasBaseOption("int", -1)
        # The height you want for the outputs files
        self.__height = sppasBaseOption("int", -1)

        # Initialize outputs files
        self.__init_outputs(usable, csv, video, folder)

        # The pattern to use for the outputs files
        self.__pattern = sppasBaseOption("str", None)
        self.set_pattern(pattern)

    # -----------------------------------------------------------------------

    def __init_outputs(self, usable, csv, video, folder):
        """Init the values of the outputs options.

        :param usable: (boolean) If True create the usable videos.
        :param csv: (boolean) If True extract images in csv file.
        :param video: (boolean) If True extract images in a video.
        :param folder: (boolean) If True extract images in a folder.

        """
        # If csv is True set the csv outputs files to True
        if usable is True:
            self.set_usable(True)

        # If csv is True set the csv outputs files to True
        if csv is True:
            self.set_csv(True)

        # If video is True set the video outputs files to True
        if video is True:
            self.set_video(True)

        # If folder is True set the folders outputs to True
        if folder is True:
            self.set_folder(True)

    # -----------------------------------------------------------------------

    def set_options(self, framing, mode, draw, width, height):
        """Set the values of the options."""
        self.set_framing(framing)
        self.set_mode(mode)
        self.set_draw(draw)
        self.set_width(width)
        self.set_height(height)

    # -----------------------------------------------------------------------

    def get_all(self):
        """Return the pattern of the outputs files."""
        all_options = ""
        all_options += "usable: " + str(self.get_usable()) + "\n"
        all_options += "csv: " + str(self.get_csv()) + "\n"
        all_options += "video: " + str(self.get_video()) + "\n"
        all_options += "folder: " + str(self.get_folder()) + "\n"
        all_options += "framing: " + self.get_framing() + "\n"
        all_options += "mode: " + self.get_mode() + "\n"
        all_options += "draw: " + self.get_draw() + "\n"
        all_options += "width: " + str(self.get_width()) + "\n"
        all_options += "height: " + str(self.get_height()) + "\n"
        all_options += "pattern: " + self.get_pattern() + "\n"
        return all_options

    # -----------------------------------------------------------------------

    def get_usable(self):
        """Return True if the option usbale is enabled."""
        return self.__output["usable"].get_value()

    # -----------------------------------------------------------------------

    def set_usable(self, value):
        """Enable or not the usable output.

        :param value: (boolean) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.__output["usable"].set_value(value)

    # -----------------------------------------------------------------------

    def get_csv(self):
        """Return True if the option csv is enabled."""
        return self.__output["csv"].get_value()

    # -----------------------------------------------------------------------

    def set_csv(self, value):
        """Enable or not the csv output.

        :param value: (boolean) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.__output["csv"].set_value(value)

    # -----------------------------------------------------------------------

    def get_video(self):
        """Return True if the option video is enabled."""
        return self.__output["video"].get_value()

    # -----------------------------------------------------------------------

    def set_video(self, value):
        """Enable or not the video output.

        :param value: (boolean) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.__output["video"].set_value(value)

    # -----------------------------------------------------------------------

    def get_folder(self):
        """Return True if the option folder is enabled."""
        return self.__output["folder"].get_value()

    # -----------------------------------------------------------------------

    def set_folder(self, value):
        """Enable or not the folder output.

        :param value: (boolean) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self.__output["folder"].set_value(value)

    # -----------------------------------------------------------------------

    def get_framing(self):
        """Return the framing."""
        return self.__framing.get_value()

    # -----------------------------------------------------------------------

    def set_framing(self, value):
        """Set the framing.

        :param value: (str) The framing to use on each image of the buffer,
        face or portrait.

        """
        if isinstance(value, str) is False and value is not None:
            raise TypeError
        if value not in ManagerOptions.FRAMING and value is not None:
            raise ValueError
        self.__framing.set_value(value)

    # -----------------------------------------------------------------------

    def get_mode(self):
        """Return the mode."""
        return self.__mode.get_value()

    # -----------------------------------------------------------------------

    def set_mode(self, value):
        """Set the mode.

        :param value: (str) The mode to use on each image of the buffer,
        full or crop.

        """
        if isinstance(value, str) is False and value is not None:
            raise TypeError
        if value not in ManagerOptions.MODE and value is not None:
            raise ValueError
        self.__mode.set_value(value)

    # -----------------------------------------------------------------------

    def get_draw(self):
        """Return the draw."""
        return self.__draw.get_value()

    # -----------------------------------------------------------------------

    def set_draw(self, value):
        """Set the draw.

        :param value: (str) The shape to draw on each image of the buffer,
        circle, ellipse or square.

        """
        if isinstance(value, str) is False and value is not None:
            raise TypeError
        if value not in ManagerOptions.DRAW and value is not None:
            raise ValueError
        self.__draw.set_value(value)

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the outputs files."""
        return self.__width.get_value()

    # -----------------------------------------------------------------------

    def set_width(self, value):
        """Set the width of outputs.

        :param value: (int) The width of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 15360:
            raise ValueError
        self.__width.set_value(value)

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the outputs files."""
        return self.__height.get_value()

    # -----------------------------------------------------------------------

    def set_height(self, value):
        """Set the height of outputs.

        :param value: (int) The height of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > 8640:
            raise ValueError
        self.__height.set_value(value)

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return the size of the outputs files."""
        return self.__width, self.__height

    # -----------------------------------------------------------------------

    def set_size(self, width, height):
        """Set the size of outputs.

        :param width: (int) The width of outputs images and videos.
        :param height: (int) The height of outputs images and videos.

        """
        self.set_width(width)
        self.set_height(height)

    # -----------------------------------------------------------------------

    def get_pattern(self):
        """Return the pattern of the outputs files."""
        return self.__pattern.get_value()

    # -----------------------------------------------------------------------

    def set_pattern(self, value):
        """Set the pattern of the outputs files.

        :param value: (str) The pattern in all the outputs files.

        """
        if isinstance(value, str) is False:
            raise TypeError
        self.__pattern.set_value(value)

    # -----------------------------------------------------------------------

