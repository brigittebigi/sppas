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

    src.annotations.annotationsexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exceptions for annotations package.

"""

from sppas.src.config import error

# -----------------------------------------------------------------------


class AnnotationSectionConfigFileError(ValueError):
    """:ERROR 4014:.

    Missing section {section_name} in the configuration file.

    """

    def __init__(self, section_name):
        self.parameter = error(4014) + \
                         (error(4014, "annotations")).format(
                             section_name=section_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnotationOptionError(KeyError):
    """:ERROR 1010:.

    Unknown option with key {key}.

    """

    def __init__(self, key):
        self.parameter = error(1010) + \
                         (error(1010, "annotations")).format(key=key)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class EmptyInputError(IOError):
    """:ERROR 1020:.

    Empty input tier {name}.

    """

    def __init__(self, name):
        self.parameter = error(1020) + \
                         (error(1020, "annotations")).format(name=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TooSmallInputError(IOError):
    """:ERROR 1021:.

    Input tier {name} does not contains enough annotations.

    """

    def __init__(self, name):
        self.parameter = error(1021) + \
                         (error(1021, "annotations")).format(name=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class EmptyOutputError(IOError):
    """:ERROR 1025:.

    Empty output result. No file created.

    """

    def __init__(self, name):
        self.parameter = error(1025) + \
                         (error(1025, "annotations")).format(name=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class NoInputError(IOError):
    """:ERROR 1030:.

    Missing input tier. Please read the documentation.

    """

    def __init__(self):
        self.parameter = error(1030) + \
                         (error(1030, "annotations"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class BadInputError(TypeError):
    """:ERROR 1040:.

    Bad input tier type. Expected time-aligned intervals.

    """

    def __init__(self):
        self.parameter = error(1040) + \
                         (error(1040, "annotations"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AudioChannelError(IOError):
    """:ERROR 1070:.

    An audio file with only one channel is expected. Got {nb} channels.

    """

    def __init__(self, nb):
        self.parameter = error(1070) + \
                         (error(1070, "annotations"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class SizeInputsError(IOError):
    """:ERROR 1050:.

    Inconsistency between the number of intervals of the input tiers.
    Got: {:d} and {:d}.

    """

    def __init__(self, number1, number2):
        self.parameter = error(1050) + \
                         (error(1050, "annotations")).format(number1, number2)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class SmallSizeInputError(IOError):
    """:ERROR 1060:.

    Not enough annotations in the input tier. At least {:d} are required.

    """

    def __init__(self, number):
        self.parameter = error(1060) + \
                         (error(1060, "annotations")).format(number)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class EmptyDirectoryError(IOError):
    """:ERROR 1220:.

    The directory {dirname} does not contain relevant data.

    """

    def __init__(self, dirname):
        self.parameter = error(1220) + \
                         (error(1220, "annotations")).format(dirname=dirname)

    def __str__(self):
        return repr(self.parameter)
