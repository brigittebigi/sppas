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
annotations: automatic annotations.
*****************************************************************************

This package includes all the automatic annotations, each one in a
package and classes to manage the data to be annotated and the resulting
annotated data.

Requires the following other packages:

* config
* utils
* files
* anndata
* audiodata
* resources
* structs

"""

from .Momel import sppasMomel
from .Intsint import sppasIntsint
from .FillIPUs import sppasFillIPUs
from .SearchIPUs import sppasSearchIPUs
from .TextNorm import sppasTextNorm
from .Phon import sppasPhon
from .Syll import sppasSyll
from .TGA import sppasTGA
from .Align import sppasAlign
from .SelfRepet import sppasSelfRepet
from .Activity import sppasActivity
from .RMS import sppasRMS
from .OtherRepet import sppasOtherRepet
from .ReOccurrences import sppasReOcc
from .StopWords import StopWords
from .StopWords import sppasStopWords
from .LexMetric import sppasLexMetric

from .searchtier import sppasFindTier
from .param import sppasParam
from .manager import sppasAnnotationsManager

# ---------------------------------------------------------------------------
#
__all__ = (
    'sppasMomel',
    'sppasIntsint',
    'sppasFillIPUs',
    'sppasSearchIPUs',
    'sppasTextNorm',
    'sppasPhon',
    'sppasAlign',
    'sppasSyll',
    'sppasTGA',
    'sppasSelfRepet',
    'sppasActivity',
    'sppasRMS',
    'sppasOtherRepet',
    'StopWords',
    'sppasStopWords',
    'sppasLexMetric',
    'sppasReOcc',
    'sppasFindTier',
    'sppasParam',
    'sppasAnnotationsManager',
)
