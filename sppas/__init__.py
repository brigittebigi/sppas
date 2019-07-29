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

sppas: Global imports and some settings for external use.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2019  Brigitte Bigi

"""

from sppas.src.config import *
from sppas.src.exc import *
from sppas.src.structs import *
from sppas.src.anndata import *
from sppas.src.audiodata import *
from sppas.src.calculus import *
from sppas.src.models import *
from sppas.src.plugins import *
from sppas.src.resources import *
from sppas.src.utils import *
from sppas.src.files import *
from sppas.src.annotations import *
from sppas.src.ui import sppasLogSetup, sppasAppConfig

__version__ = sg.__version__
__name__ = sg.__name__
__author__ = sg.__author__
__docformat__ = sg.__docformat__
