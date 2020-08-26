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

    src.videodata.videodataexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for videodata package.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

"""

from sppas.src.config import error

# -----------------------------------------------------------------------


class VideoOpenError(IOError):
    """:ERROR 3610:.

    Video of file {filename} can't be opened by opencv library.

    """

    def __init__(self, name):
        self.parameter = error(3610) + (error(3610, "data")).format(filename=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class VideoWriteError(IOError):
    """:ERROR 3620:.

    Video of file {filename} can't be written by opencv library.

    """

    def __init__(self, name):
        self.parameter = error(3620) + (error(3620, "data")).format(filename=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class VideoBrowseError(IOError):
    """:ERROR 3630:.

    Video of file {filename} can't be read by OpenCV library.

    """

    def __init__(self, name):
        self.parameter = error(3630) + (error(3630, "data")).format(filename=name)

    def __str__(self):
        return repr(self.parameter)
