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

    - main exception: 001
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
    """:ERROR 0001:.

    The following error occurred: {message}.

    """

    def __init__(self, message):
        self._status = 1
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(message=message)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class sppasTypeError(TypeError):
    """:ERROR 0100:.

    {!s:s} is not of the expected type '{:s}'.

    """

    def __init__(self, rtype, expected):
        self._status = 100
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(rtype, expected)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class sppasIndexError(IndexError):
    """:ERROR 0200:.

    Invalid index value {:d}.

    """

    def __init__(self, index):
        self._status = 200
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(index)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class sppasValueError(ValueError):
    """:ERROR 0300:.

    Invalid value '{!s:s}' for '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self._status = 300
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class sppasKeyError(KeyError):
    """:ERROR 0400:.

    Invalid key '{!s:s}' for data '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self._status = 400
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class sppasOSError(OSError):
    """:ERROR 0500:.

    OS error: {error}.

    """

    def __init__(self, error_msg):
        self._status = 500
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(error=error_msg)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class sppasInstallationError(sppasOSError):
    """:ERROR 0510:.

    Installation failed with error: {error}.

    """

    def __init__(self, error_msg):
        super(sppasInstallationError, self).__init__(error_msg)
        self._status = 510
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(error=error_msg)

# -----------------------------------------------------------------------


class sppasEnableFeatureError(sppasOSError):
    """:ERROR 0520:.

    Feature {name} is not enabled; its installation should be processed
    first.

    """

    def __init__(self, name):
        super(sppasEnableFeatureError, self).__init__("")
        self._status = 520
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(name=name)

# -----------------------------------------------------------------------


class sppasPackageFeatureError(sppasOSError):
    """:ERROR 0530:.

    The package {package} can't be imported. The installation of the
    feature {name} should be processed first.

    """

    def __init__(self, package, name):
        super(sppasPackageFeatureError, self).__init__("")
        self._status = 530
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(
                             package=package, name=name)

# -----------------------------------------------------------------------


class sppasPackageUpdateFeatureError(sppasOSError):
    """:ERROR 0540:.

    The package {package} is not up-to-date. The re-installation of the
    feature {name} should be processed first."

    """

    def __init__(self, package, name):
        super(sppasPackageUpdateFeatureError, self).__init__("")
        self._status = 540
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(
                             package=package, name=name)

# -----------------------------------------------------------------------


class sppasIOError(IOError):
    """:ERROR 0600:.

    No such file or directory: {name}

    """

    def __init__(self, filename):
        self._status = 600
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(name=filename)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------
# Specialized Value errors (300-series)
# -----------------------------------------------------------------------


class NegativeValueError(sppasValueError):
    """:ERROR 0310:.

    Expected a positive value. Got {value}.

    """

    def __init__(self, value):
        super(NegativeValueError, self).__init__("", 0)
        self._status = 310
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(value=value)

# -----------------------------------------------------------------------


class RangeBoundsException(sppasValueError):
    """:ERROR 0320:.

    Min value {} is bigger than max value {}.'

    """

    def __init__(self, min_value, max_value):
        super(RangeBoundsException, self).__init__("", 0)
        self._status = 320
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(
                             min_value=min_value,
                             max_value=max_value)

# -----------------------------------------------------------------------


class IntervalRangeException(sppasValueError):
    """:ERROR 0330:.

    Value {} is out of range [{},{}].

    """

    def __init__(self, value, min_value, max_value):
        super(IntervalRangeException, self).__init__("", 0)
        self._status = 330
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(
                             value=value,
                             min_value=min_value,
                             max_value=max_value)

# -----------------------------------------------------------------------


class IndexRangeException(sppasValueError):
    """:ERROR 0340:.

    List index {} out of range [{},{}].

    """

    def __init__(self, value, min_value, max_value):
        super(IndexRangeException, self).__init__("", 0)
        self._status = 340
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(
                             value=value,
                             min_value=min_value,
                             max_value=max_value)

# -----------------------------------------------------------------------
# Specialized IO errors (600-series)
# -----------------------------------------------------------------------


class IOExtensionError(sppasIOError):
    """:ERROR 0610:.

    Unknown extension for filename '{:s}'.

    """

    def __init__(self, filename):
        super(IOExtensionError, self).__init__("")
        self._status = 610
        self.parameter = error(610) + \
                         (error(610, "globals")).format(filename)

# -----------------------------------------------------------------------


class NoDirectoryError(sppasIOError):
    """:ERROR 0620:.

    The directory {dirname} does not exist.

    """

    def __init__(self, dirname):
        super(NoDirectoryError, self).__init__("")
        self._status = 620
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(dirname=dirname)

# -----------------------------------------------------------------------


class sppasOpenError(sppasIOError):
    """:ERROR 0650:.

    File '{:s}' can't be open or read.

    """

    def __init__(self, filename):
        super(sppasOpenError, self).__init__("")
        self._status = 650
        self.parameter += error(self._status) + \
                          (error(self._status, "globals")).format(filename)

# -----------------------------------------------------------------------


class sppasWriteError(sppasIOError):
    """:ERROR 0660:.

    File '{:s}' can't be saved.

    """

    def __init__(self, filename):
        super(sppasWriteError, self).__init__("")
        self._status = 660
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(filename)

# -----------------------------------------------------------------------


class sppasExtensionReadError(sppasIOError):
    """:ERROR 0670:.

    Files with extension '{:s}' are not supported for reading.

    """

    def __init__(self, filename):
        super(sppasExtensionReadError, self).__init__("")
        self._status = 670
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(filename)

# -----------------------------------------------------------------------


class sppasExtensionWriteError(sppasIOError):
    """:ERROR 0680:.

    Files with extension '{:s}' are not supported for writing.

    """

    def __init__(self, filename):
        super(sppasExtensionWriteError, self).__init__("")
        self._status = 680
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(filename)
