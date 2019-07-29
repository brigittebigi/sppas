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

    src.resources.resourcesexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import error

# -----------------------------------------------------------------------


class FileUnicodeError(UnicodeDecodeError):
    """:ERROR 5005:.

    Encoding error while trying to read the file: {name}.

    """

    def __init__(self, filename):
        self.parameter = error(5005) + \
                         (error(5005, "resources")).format(name=filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class FileIOError(Exception):
    """:ERROR 5010:.

    Error while trying to open and read the file: {name}.

    """

    def __init__(self, filename):
        self.parameter = error(5010) + \
                         (error(5010, "resources")).format(name=filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class FileFormatError(ValueError):
    """:ERROR 5015:.

    Read file failed at line number {number}: {string}.

    """

    def __init__(self, line_number, filename):
        line_number = int(line_number)
        self.parameter = error(5015) + \
                         (error(5015, "resources")).format(
                             number=line_number,
                             string=filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class NgramRangeError(ValueError):
    """:ERROR 5020:.

    The n value of n-grams pattern matching must range [1;{maximum}].
    Got {observed}.

    """

    def __init__(self, maxi, value):
        maxi = int(maxi)
        value = int(value)
        self.parameter = error(5020) + \
                         (error(5020, "resources")).format(
                             maximum=maxi,
                             observed=value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class GapRangeError(ValueError):
    """:ERROR 5022:.

    The gap value of pattern matching must range [0;{maximum}].
    Got {observed}.

    """

    def __init__(self, maxi, value):
        maxi = int(maxi)
        value = int(value)
        self.parameter = error(5022) + \
                         (error(5022, "resources")).format(
                             maximum=maxi,
                             observed=value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ScoreRangeError(ValueError):
    """:ERROR 5024:.

    The score value of unigrams pattern matching must range [0;1].
    Got {observed}.

    """

    def __init__(self, value):
        value = float(value)
        self.parameter = error(5024) + \
                         (error(5024, "resources")).format(observed=value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class DumpExtensionError(ValueError):
    """:ERROR 5030:.

    The dump file can't have the same extension as the ASCII file
    ({extension}).

    """

    def __init__(self, extension):
        self.parameter = error(5030) + \
                         (error(5030, "resources")).format(extension=extension)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class PositiveValueError(ValueError):
    """:ERROR 5040:.

    The count value must be positive. Got ({count}).

    """

    def __init__(self, count):
        self.parameter = error(5040) + \
                         (error(5040, "resources")).format(count=count)

    def __str__(self):
        return repr(self.parameter)
