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
    
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

*****************************************************************************
files: management of files into workspaces
*****************************************************************************

This package includes classes to manage a bunch of files organized into
workspaces. A workspace is made of data related to the filenames and a
list of references to make relations between files.

Requires the following other packages:

* config
* utils

"""

from .fileutils import sppasGUID
from .fileutils import sppasFileUtils
from .fileutils import sppasDirUtils
from .filebase import FileBase
from .filebase import States
from .filedata import FileData
from .filestructure import FileName, FileRoot, FilePath
from .fileref import FileReference, sppasAttribute
from .filedatafilters import sppasFileDataFilters

__all__ = (
    "FileBase",
    "States",
    "FileData",
    "FileName",
    "FileRoot",
    "FilePath",
    "sppasAttribute",
    "FileReference",
    "sppasFileDataFilters",
    "sppasFileUtils",
    "sppasDirUtils",
    "sppasGUID"
)
