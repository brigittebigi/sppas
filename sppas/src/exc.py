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

    src.sppasexc.py
    ~~~~~~~~~~~~~~~

Global exceptions for sppas.

"""

from sppas.src.config import error


# -----------------------------------------------------------------------


class sppasTypeError(TypeError):
    """:ERROR 100:.

    {!s:s} is not of the expected type '{:s}'.

    """

    def __init__(self, rtype, expected):
        self.parameter = error(100) + \
                         (error(100, "globals")).format(rtype, expected)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasIndexError(IndexError):
    """:ERROR 200:.

    Invalid index value {:d}.

    """

    def __init__(self, index):
        self.parameter = error(200) + \
                         (error(200, "globals")).format(index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class sppasKeyError(KeyError):
    """:ERROR 250:.

    Invalid key '{!s:s}' for data '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self.parameter = error(250) + \
                         (error(250, "globals")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class sppasValueError(ValueError):
    """:ERROR 300:.

    Invalid value '{!s:s}' for '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self.parameter = error(300) + \
                         (error(300, "globals")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class InstallationError(OSError):
    """:ERROR 500:.

    Installation failed with error: {error}.

    """

    def __init__(self, error_msg):
        self.parameter = error(500) + \
                         (error(500, "install")).format(error=error_msg)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class NegativeValueError(ValueError):
    """:ERROR 010:.

    Expected a positive value. Got {value}.

    """

    def __init__(self, value):
        self.parameter = error('010') + \
                         (error('010', "globals")).format(value=value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class RangeBoundsException(ValueError):
    """:ERROR 012:.

    Min value {} is bigger than max value {}.'

    """

    def __init__(self, min_value, max_value):
        self.parameter = error('012') + \
                         (error('012', "globals")).format(
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class IndexRangeException(IndexError):
    """:ERROR 014:.

    List index {} out of range [{},{}].

    """

    def __init__(self, value, min_value, max_value):
        self.parameter = error('014') + \
                         (error('014', "globals")).format(
                             value=value,
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class IntervalRangeException(ValueError):
    """:ERROR 016:.

    Value {} is out of range [{},{}].

    """

    def __init__(self, value, min_value, max_value):
        self.parameter = error('016') + \
                         (error('016', "globals")).format(
                             value=value,
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class IOExtensionException(IOError):
    """:ERROR 110:.

    Unknown extension for filename {:s}'

    """

    def __init__(self, filename):
        self.parameter = error('110') + \
                         (error('110', "globals")).format(filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class NoDirectoryError(IOError):
    """:ERROR 112:.

    The directory {dirname} does not exist.

    """

    def __init__(self, dirname):
        self.parameter = error(112) + \
                         (error(112, "globals")).format(dirname=dirname)

    def __str__(self):
        return repr(self.parameter)
