# -*- coding: utf-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        use of this software is governed by the gnu public license, version 3.

        sppas is free software: you can redistribute it and/or modify
        it under the terms of the gnu general public license as published by
        the free software foundation, either version 3 of the license, or
        (at your option) any later version.

        sppas is distributed in the hope that it will be useful,
        but without any warranty; without even the implied warranty of
        merchantability or fitness for a particular purpose.  see the
        gnu general public license for more details.

        you should have received a copy of the gnu general public license
        along with sppas. if not, see <http://www.gnu.org/licenses/>.

        this banner notice must not be removed.

        ---------------------------------------------------------------------

    wkps.wio.wkpreadwrite.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
from collections import OrderedDict

from sppas import IOExtensionException
from sppas.src.utils.makeunicode import u
from sppas.src.anndata.anndataexc import AioEncodingError

from .wjson import sppasWJSON

# ----------------------------------------------------------------------------


class sppasWkpRW(object):
    """A reader/writer of any supported workspaces.

        :author:       Laurent Vouriot
        :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
        :contact:      contact@sppas.org
        :license:      GPL, v3
        :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    WORKSPACE_TYPES = OrderedDict()
    WORKSPACE_TYPES[sppasWJSON().default_extension.lower()] = sppasWJSON

    # ------------------------------------------------------------------------

    def __init__(self, filename):
        """Create a workspace reader/writer.

        :param filename: (str)

        """
        self.__filename = u(filename)

    # ------------------------------------------------------------------------

    @staticmethod
    def default_extension():
        """Return the default extension to read/write workspaces."""
        return sppasWJSON().default_extension

    # ------------------------------------------------------------------------

    @staticmethod
    def extensions():
        """Return the list of supported extensions in lower case."""
        return list(sppasWkpRW.WORKSPACE_TYPES.keys())

    # ------------------------------------------------------------------------

    def read(self):
        """Read a workspace from a file.

        :returns: (sppasWkpRW)

        """
        try:
            wkp = sppasWkpRW.create_wkp_from_extension(self.__filename)
            wkp.read(self.__filename)
        except Exception:
            raise

        return wkp

    # ------------------------------------------------------------------------

    @staticmethod
    def create_wkp_from_extension(filename):
        """Return a workspace according to a filename.

        :param filename: (str)
        :returns: sppasBaseWkpIO()

        """
        extension = os.path.splitext(filename)[1][1:]
        extension = extension.lower()

        if extension in sppasWkpRW.extensions():
            return sppasWkpRW.WORKSPACE_TYPES[extension]()

        raise IOExtensionException(filename)

    # ------------------------------------------------------------------------

    def write(self, wkp):
        """Write a workspace into a file.

        :param wkp: (sppasWorkspace) Data to be saved

        """
        wkp_rw = sppasWkpRW.create_wkp_from_extension(self.__filename)
        wkp_rw.set(wkp)

        try:
            wkp_rw.write(self.__filename)
        except UnicodeDecodeError as e:
            raise AioEncodingError(self.__filename, str(e))
        except Exception:
            raise

        return wkp_rw

# ---------------------------------------------------------------------------


class WkpFormatProperty(object):
    """Represent one format and its properties.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, extension):
        """Create a WkpFormatProperty instance.

        :param extension: (str) File name extension.

        """
        self._extension = extension
        if extension.startswith(".") is False:
            self._extension = "." + extension
        self._instance = sppasWkpRW.WORKSPACE_TYPES[extension.lower()]()
        self._software = self._instance.software

        try:
            self._instance.read("")
        except NotImplementedError:
            self._reader = False
        except Exception:
            self._reader = True
        try:
            self._instance.write("")
        except NotImplementedError:
            self._writer = False
        except Exception:
            self._writer = True

    # -----------------------------------------------------------------------

    def get_extension(self):
        """Return the extension, including the initial dot."""
        return self._extension

    def get_software(self):
        """Return the name of the software matching the extension."""
        return self._software

    def get_reader(self):
        """Return True if SPPAS can read files of the extension."""
        return self._reader

    def get_writer(self):
        """Return True if SPPAS can write files of the extension."""
        return self._writer

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __str__(self):
        return 'WkpFormatProperty() of extension {!s:s}' \
               ''.format(self._extension)

