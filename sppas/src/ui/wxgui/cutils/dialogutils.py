#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: dialogsutils.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os.path
import wx

# ----------------------------------------------------------------------------

def create_wildcard(text, extensions):
    """
    Create wildcard for use in open/save views.

    """
    return "%s (%s)|%s" % (text,
                           ", ".join(["*" + e for e in extensions]),
                           ";".join(["*" + e for e in extensions]))

# ----------------------------------------------------------------------------

def get_extension(filename):
    return os.path.splitext(filename)[1][1:]

# ----------------------------------------------------------------------------

def extend_path(path, valid_extensions, default_extension):
    """
    Return tuple (path, extension) ensuring that path has extension.

    """
    for extension in valid_extensions:
        if path.endswith("." + extension):
            return (path, extension)
    return (path + "." + default_extension, default_extension)

# ----------------------------------------------------------------------------
