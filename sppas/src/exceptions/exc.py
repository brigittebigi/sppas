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

    src.exceptions.exc.py
    ~~~~~~~~~~~~~~~~~~~~~~

Global exceptions for sppas.

    - main exception: 000
    - type errors: 100-series
    - index errors: 200-series
    - value errors: 300-series
    - key errors: 400-series
    - os errors: 500-series
    - IO errors: 600-series

"""

from sppas.src.config import error


# -----------------------------------------------------------------------
# Main errors
# -----------------------------------------------------------------------


class sppasError(Exception):
    """:ERROR 0000:.

    The following error occurred: {message}.

    """

    def __init__(self, message):
        self.parameter = error(0) + \
                         (error(0, "globals")).format(message=message)

    def __str__(self):
        return repr(self.parameter)

    def __format__(self, fmt):
        return str(self).__format__(fmt)

# -----------------------------------------------------------------------


class sppasTypeError(TypeError):
    """:ERROR 0100:.

    {!s:s} is not of the expected type '{:s}'.

    """

    def __init__(self, rtype, expected):
        self.parameter = error(100) + \
                         (error(100, "globals")).format(rtype, expected)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasIndexError(IndexError):
    """:ERROR 0200:.

    Invalid index value {:d}.

    """

    def __init__(self, index):
        self.parameter = error(200) + \
                         (error(200, "globals")).format(index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasValueError(ValueError):
    """:ERROR 0300:.

    Invalid value '{!s:s}' for '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self.parameter = error(300) + \
                         (error(300, "globals")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasKeyError(KeyError):
    """:ERROR 0400:.

    Invalid key '{!s:s}' for data '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self.parameter = error(400) + \
                         (error(400, "globals")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasInstallationError(OSError):
    """:ERROR 0510:.

    Installation failed with error: {error}.

    """

    def __init__(self, error_msg):
        self.parameter = error(510) + \
                         (error(510, "globals")).format(error=error_msg)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasEnableFeatureError(OSError):
    """:ERROR 0520:.

    Feature {name} is not enabled; its installation should be processed first.

    """

    def __init__(self, name):
        self.parameter = error(520) + \
                         (error(520, "globals")).format(name=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasIOError(IOError):
    """:ERROR 0600:.

    No such file or directory: {name}

    """

    def __init__(self, filename):
        self.parameter = error(600) + \
                         (error(600, "globals")).format(name=filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------
# Specialized Value errors (300-series)
# -----------------------------------------------------------------------


class NegativeValueError(ValueError):
    """:ERROR 0310:.

    Expected a positive value. Got {value}.

    """

    def __init__(self, value):
        self.parameter = error(310) + \
                         (error(310, "globals")).format(value=value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class RangeBoundsException(ValueError):
    """:ERROR 0320:.

    Min value {} is bigger than max value {}.'

    """

    def __init__(self, min_value, max_value):
        self.parameter = error(320) + \
                         (error(320, "globals")).format(
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class IntervalRangeException(ValueError):
    """:ERROR 0330:.

    Value {} is out of range [{},{}].

    """

    def __init__(self, value, min_value, max_value):
        self.parameter = error(330) + \
                         (error(330, "globals")).format(
                             value=value,
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class IndexRangeException(ValueError):
    """:ERROR 0340:.

    List index {} out of range [{},{}].

    """

    def __init__(self, value, min_value, max_value):
        self.parameter = error(340) + \
                         (error(340, "globals")).format(
                             value=value,
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------
# Specialized IO errors (600-series)
# -----------------------------------------------------------------------


class IOExtensionError(IOError):
    """:ERROR 0610:.

    Unknown extension for filename '{:s}'

    """

    def __init__(self, filename):
        self.parameter = error(610) + \
                         (error(610, "globals")).format(filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class NoDirectoryError(IOError):
    """:ERROR 0620:.

    The directory {dirname} does not exist.

    """

    def __init__(self, dirname):
        self.parameter = error(620) + \
                         (error(620, "globals")).format(dirname=dirname)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasOpenError(IOError):
    """:ERROR 0650:.

    File '{:s}' can't be open or read.

    """

    def __init__(self, filename):
        self.parameter = error(650) + \
                         (error(650, "globals")).format(filename)

    def __str__(self):
        return repr(self.parameter)

