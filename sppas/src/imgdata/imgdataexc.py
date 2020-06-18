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

    src.imgdata.imgdataexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for imgdata package.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

"""

from sppas.src.config import sg
from sppas.src.config import error

# -----------------------------------------------------------------------


class ImageReadError(IOError):
    """:ERROR 2610:.

    Image of file {filename} can't be read by opencv library.

    """

    def __init__(self, name):
        self.parameter = error(2610) + (error(2610, "data")).format(filename=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageWriteError(IOError):
    """:ERROR 2620:.

    Image of file {filename} can't be written by opencv library.

    """

    def __init__(self, name):
        self.parameter = error(2620) + (error(2620, "data")).format(filename=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageBoundError(ValueError):
    """:ERROR 2330:.

    The value {} can't be superior to the one of the image {}.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2330) + \
                         (error(2330, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageWidthError(ValueError):
    """:ERROR 2332:.

    The width value {} can't be superior to the width {} of the image.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2332) + \
                         (error(2332, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageHeightError(ValueError):
    """:ERROR 2334:.

    The height value {} can't be superior to the height {} of the image.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2334) + \
                         (error(2334, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageEastingError(ValueError):
    """:ERROR 2336:.

    The x-axis value {} can't be superior to the width {} of the image.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2336) + \
                         (error(2336, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageNorthingError(ValueError):
    """:ERROR 2338:.

    The y-axis value {} can't be superior to the height {} of the image.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2338) + \
                         (error(2338, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)




