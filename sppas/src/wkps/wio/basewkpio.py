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

    wkps.wio.basewkpio.py
    ~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas import sppasTypeError
from ..sppasWorkspace import sppasWorkspace

# ---------------------------------------------------------------------------


class sppasBaseWkpIO(sppasWorkspace):
    """Base class for any reader-writer of a workspace.

    :author:       Laurent Vouriot
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, name=None):
        """Initialize a new workspace reader-writer instance.

        :param name: (str) A workspace name

        """
        super(sppasBaseWkpIO, self).__init__(name)

        self.default_extension = None
        self.software = "und"

    # -----------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        """Check whether a file is of an appropriate format or not."""
        return False

    # -----------------------------------------------------------------------

    def set(self, wkp):
        """Set the current workspace with the content of another one.

        :param wkp: (sppasWorkspace)

        """
        if isinstance(wkp, sppasWorkspace) is False:
            raise sppasTypeError(type(wkp), "sppasWorkspace")

        self._id = wkp.get_id()
        for reference in wkp.get_refs():
            self.add_ref(reference)
        for filepath in wkp.get_all_files():
            self.add(filepath)

    # -----------------------------------------------------------------------
    # Read/Write
    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a file and fill the workspace.

        :param filename: (str)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a workspace into a file.

        :param filename: (str)

        """
        raise NotImplementedError

