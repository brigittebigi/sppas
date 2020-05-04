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

    src.wkps.wkpexc.py
    ~~~~~~~~~~~~~~~~~~~

    Exceptions for file management.

        - FileOSError (error 9010)
        - FileTypeError (error 9012)
        - PathTypeError (error 9014)
        - FileAttributeError (error 9020)
        - FileRootValueError (error 9030)
        - FilesMatchingValueError (error 9032)
        - FileAddValueError (error 9034)
        - FileLockedError (error 9040)

"""

from sppas.src.config import error

# ---------------------------------------------------------------------------


class FileOSError(OSError):
    """:ERROR 9010:.

    Name {!s:s} does not match a file or a directory.

    """

    def __init__(self, name):
        self.parameter = error(9010) + (error(9010, "wkps")).format(name)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileTypeError(TypeError):
    """:ERROR 9012:.

    Name {!s:s} does not match a valid file.

    """

    def __init__(self, name):
        self.parameter = error(9012) + (error(9012, "wkps")).format(name)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class PathTypeError(TypeError):
    """:ERROR 9014:.

    Name {!s:s} does not match a valid directory.

    """

    def __init__(self, name):
        self.parameter = error(9014) + (error(9014, "wkps")).format(name)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileAttributeError(AttributeError):
    """:ERROR 9020:.

    {:s} has no attribute '{:s}'

    """

    def __init__(self, classname, method):
        self.parameter = error(9020) + (error(9020, "wkps")).format(classname, method)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileRootValueError(ValueError):
    """:ERROR 9030:.

    '{:s}' does not match root '{:s}'

    """

    def __init__(self, filename, rootname):
        self.parameter = error(9030) + (error(9030, "wkps")).format(filename, rootname)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileLockedError(IOError):
    """:ERROR 9040:.

    '{!s:s}' is locked.'

    """

    def __init__(self, filename):
        self.parameter = error(9040) + (error(9040, "wkps")).format(filename)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FilesMatchingValueError(ValueError):
    """:ERROR 9032:.

    '{:s}' does not match with '{:s}'

    """

    def __init__(self, name1, name2):
        self.parameter = error(9032) + (error(9032, "wkps")).format(name1, name2)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileAddValueError(ValueError):
    """:ERROR 9034:.

    '{:s}' cant be added because it already exists.

    """

    def __init__(self, name):
        self.parameter = error(9034) + (error(9034, "wkps")).format(name)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FilesMatchingValueError(ValueError):
    """:ERROR 9032:.

    '{:s}' does not match with '{:s}'

    """

    def __init__(self, name1, name2):
        self.parameter = error(9050) + (error(9050, "files")).format(name1, name2)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileAddValueError(ValueError):
    """:ERROR 9034:.

    '{:s}' cant be added because it already exists.

    """

    def __init__(self, name1, name2):
        self.parameter = error(9034) + (error(9034, "files")).format(name1, name2)

    def __str__(self):
        return repr(self.parameter)
