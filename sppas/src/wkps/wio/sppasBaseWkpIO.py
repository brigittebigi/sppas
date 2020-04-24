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

    wkps.wio.sppasBaseWkpIO.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""
from ..sppasWorkspace import sppasWorkspace

# ---------------------------------------------------------------------------


class sppasBaseWkpIO(sppasWorkspace):
    """

    :author:       Laurent Vouriot
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
    :summary:      Base object for readers and writers of workspaces
    """

    def __init__(self, name=None):
        """Initialize a new workspace reader-writer instance

        :param: (str) A workspace name

        """
        super(sppasBaseWkpIO, self).__init__(name)

        self.default_extension = None
        self.software = "Und"

    # -----------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        """Check wether a file is the appropriate format or not."""
        return False

    # -----------------------------------------------------------------------
    # Read/Write
    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a file and fill the workspace

        :param filename: (str)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a workspace into a file

        :param filename: (str)

        """

        raise NotImplementedError

