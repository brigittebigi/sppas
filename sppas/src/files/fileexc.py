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

    src.files.fileexc.py
    ~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for file management.

        - FileOSError (error 9010)
        - FileTypeError (error 9012)
        - PathTypeError (error 9014)
        - FileAttributeError (error 9020)
        - FileRootValueError (error 9030)

"""
try:
    from sppas.src.config import error
except ImportError:
    def error(index, domain=None):
        """Return the string mathing the error index.

        Replace the original function which returns the error message 
        translated in the given domain.

        A generic error message is returned if no domain is given.

        :param index: (int) Index of the error.
        :param domain: (str) Translation domain [not used]
        :returns: (str) Error message. 

        """          
        if domain is not None:
            if index == 9010:
                return 'Name {!s:s} does not match a file or a directory.'
            if index == 9012:
                return 'Name {!s:s} does not match a valid file.'
            if index == 9014:
                return 'Name {!s:s} does not match a valid directory.'
            if index == 9020:
                return "{:s} has no attribute '{:s}'"
            if index == 9030:
                return "'{:s}' does not match root '{:s}'"
            if index == 9040:
                return "{!s:s} is locked."

        return ":ERROR " + str(index) + ": "

# ---------------------------------------------------------------------------


class FileOSError(OSError):
    """:ERROR 9010:.

    Name {!s:s} does not match a file or a directory.

    """

    def __init__(self, name):
        self.parameter = error(9010) + (error(9010, "ui")).format(name)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileTypeError(TypeError):
    """:ERROR 9012:.

    Name {!s:s} does not match a valid file.

    """

    def __init__(self, name):
        self.parameter = error(9012) + (error(9012, "ui")).format(name)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class PathTypeError(TypeError):
    """:ERROR 9014:.

    Name {!s:s} does not match a valid directory.

    """

    def __init__(self, name):
        self.parameter = error(9014) + (error(9014, "ui")).format(name)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileAttributeError(AttributeError):
    """:ERROR 9020:.

    {:s} has no attribute '{:s}'

    """

    def __init__(self, classname, method):
        self.parameter = error(9020) + (error(9020, "ui")).format(classname, method)

    def __str__(self):
        return repr(self.parameter)
    
# ---------------------------------------------------------------------------


class FileRootValueError(ValueError):
    """:ERROR 9030:.

    '{:s}' does not match root '{:s}'

    """

    def __init__(self, filename, rootname):
        self.parameter = error(9030) + (error(9030, "ui")).format(filename, rootname)

    def __str__(self):
        return repr(self.parameter)

# ---------------------------------------------------------------------------


class FileLockedError(IOError):
    """:ERROR 9040:.

    '{!s:s}' is locked.'

    """

    def __init__(self, filename):
        self.parameter = error(9040) + (error(9040, "ui")).format(filename)

    def __str__(self):
        return repr(self.parameter)
