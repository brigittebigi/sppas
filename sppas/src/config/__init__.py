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
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

*****************************************************************************
config: configuration for all global things.
*****************************************************************************

This package includes classes to fix all global parameters. It does not
requires any other package but all other packages of SPPAS are requiring it!

"""

# Utility class to execute and read a subprocess. No external requirement.
from .process import Process

# The global settings. They need to be imported first: others need them.
from .settings import sppasBaseSettings
from .settings import sppasGlobalSettings
from .settings import sppasPathSettings
from .settings import sppasSymbolSettings
from .settings import sppasSeparatorSettings
from .settings import sppasAnnotationsSettings

# Initialize the translation system.
# Requires settings to find .po files.
from .po import sppasTranslate
from .po import error, info, msg

# Utility classes to initialize logs with logging (stream or file).
# Requires settings to print the appropriate headers.
from .logs import sppasLogFile
from .logs import sppasLogSetup

# SPPAS Application configuration. Requires settings for paths, globals...
from .appcfg import sppasAppConfig

# Requires the settings, appcfg and process
from .support import sppasPostInstall

# ---------------------------------------------------------------------------
# Fix the global un-modifiable settings
# ---------------------------------------------------------------------------

# create missing directories
sppasPostInstall().sppas_directories()

# create an instance of each global settings
sg = sppasGlobalSettings()
paths = sppasPathSettings()
symbols = sppasSymbolSettings()
separators = sppasSeparatorSettings()
annots = sppasAnnotationsSettings()

# ---------------------------------------------------------------------------
# Fix the translation of each package
# ---------------------------------------------------------------------------

__all__ = (
    "Process",
    "sppasBaseSettings",
    "sppasGlobalSettings",
    "sppasPathSettings",
    "sppasAnnotationsSettings",
    "sppasSymbolSettings",
    "sppasSeparatorSettings",
    "sppasLogFile",
    "sppasLogSetup",
    "sppasAppConfig",
    "sppasPostInstall",
    "sg",
    "paths",
    "symbols",
    "separators",
    "annots",
    "info",
    "error",
    "msg"
)

