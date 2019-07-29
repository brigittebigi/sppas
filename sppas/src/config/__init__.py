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
from .support import PostInstall

# ---------------------------------------------------------------------------
# Fix the global un-modifiable settings
# ---------------------------------------------------------------------------

# create missing directories
PostInstall().sppas_directories()

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

# ---------------------------------------------------------------------------


def info(msg_id, domain=None):
    """Return the info message from gettext.

    :param msg_id: (str or int) Info id
    :param domain: (str) Name of the domain

    """
    msg = ":INFO " + str(msg_id) + ": "
    if domain is not None:
        try:
            st = sppasTranslate()
            translation = st.translation(domain)
            return translation.gettext(msg)
        except:
            pass

    return msg

# ---------------------------------------------------------------------------


def error(msg_id, domain=None):
    """Return the error message from gettext.

    :param msg_id: (str or int) Error id
    :param domain: (str) Name of the domain

    """
    msg = ":ERROR " + str(msg_id) + ": "
    if domain is not None:
        try:
            st = sppasTranslate()
            translation = st.translation(domain)
            return translation.gettext(msg)
        except:
            pass

    return msg

# ---------------------------------------------------------------------------


def msg(msg, domain=None):
    """Return the message from gettext.

    :param msg: (str or int) Message
    :param domain: (str) Name of the domain

    """
    if domain is not None:
        try:
            st = sppasTranslate()
            translation = st.translation(domain)
            return translation.gettext(msg)
        except:
            pass

    return msg

# ---------------------------------------------------------------------------


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
