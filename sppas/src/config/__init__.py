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

import sys
try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

from .settings import sppasBaseSettings
from .sglobal import sppasGlobalSettings
from .sglobal import sppasPathSettings
from .sglobal import sppasSymbolSettings
from .sglobal import sppasSeparatorSettings
from .sglobal import sppasAnnotationsSettings
from .po import sppasTranslate
from .po import error, info, msg
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

# Default input/output encoding
reload(sys)
try:
    sys.setdefaultencoding(sg.__encoding__)
except AttributeError:  # Python 2.7
    pass

# ---------------------------------------------------------------------------
# Fix the translation of each package
# ---------------------------------------------------------------------------

ui_translation = sppasTranslate().translation("ui")

__all__ = (
    "sppasBaseSettings",
    "sg",
    "paths",
    "symbols",
    "separators",
    "annots",
    "ui_translation",
    "info",
    "error",
    "msg"
)

