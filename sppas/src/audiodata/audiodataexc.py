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

    src.audiodata.audiodataexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for audiodata package.

"""

from sppas.src.config import error

# -----------------------------------------------------------------------


class AudioError(Exception):
    """:ERROR 2000:.

    No audio file is defined.

    """

    def __init__(self):
        self.parameter = error(2000) + (error(2000, "data"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AudioTypeError(TypeError):
    """:ERROR 2005:.

    Audio type error: not supported file format {extension}.

    """

    def __init__(self, extension):
        self.parameter = error(2005) + \
                         (error(2005, "data")).format(extension=extension)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class AudioIOError(IOError):
    """:ERROR 2010:.

    Opening, reading or writing error.

    """

    def __init__(self, message="", filename=""):
        self.parameter = error(2010) + \
                         (error(2010, "data")).format(filename=filename, message=message)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AudioDataError(Exception):
    """:ERROR 2015:.

    No data or corrupted data in the audio file {filename}.

    """

    def __init__(self, filename=""):
        self.parameter = error(2015) + \
                         (error(2015, "data")).format(filename=filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ChannelIndexError(ValueError):
    """:ERROR 2020:.

    {number} is not a right index of channel.

    """

    def __init__(self, index):
        index = int(index)
        self.parameter = error(2020) + \
                         (error(2020, "data")).format(number=index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class IntervalError(ValueError):
    """:ERROR 2025:.

    From {value1} to {value2} is not a proper interval.

    """

    def __init__(self, value1, value2):
        value1 = int(value1)
        value2 = int(value2)
        self.parameter = error(2025) + \
                         (error(2025, "data")).format(value1=value1,
                                                           value2=value2)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ChannelError(Exception):
    """:ERROR 2050:.

    No channel defined.

    """

    def __init__(self):
        self.parameter = error(2050) + \
                         (error(2050, "data"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class MixChannelError(ValueError):
    """:ERROR 2060: :ERROR 2061: :ERROR 2062: :ERROR 2050: .

    Channels have not the same sample width.
    Channels have not the same frame rate.
    Channels have not the same number of frames.

    """

    def __init__(self, value=0):
        value = int(value)
        if value == 1:
            self.parameter = error(2060) + (error(2060, "data"))
        elif value == 2:
            self.parameter = error(2061) + (error(2061, "data"))
        elif value == 3:
            self.parameter = error(2062) + (error(2062, "data"))
        else:
            self.parameter = error(2050) + (error(2050, "data"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class SampleWidthError(ValueError):
    """:ERROR 2070:.

     Invalid sample width {value}.

     """

    def __init__(self, value):
        value = int(value)
        self.parameter = error(2070) + \
                         (error(2070, "data")).format(value=value)

    def __str__(self):
        return repr(self.parameter)
# -----------------------------------------------------------------------


class FrameRateError(ValueError):
    """:ERROR 2080:

    Invalid framerate {value}.

    """

    def __init__(self, value):
        value = int(value)
        self.parameter = error(2080) + \
                         (error(2080, "data")).format(value=value)

    def __str__(self):
        return repr(self.parameter)
