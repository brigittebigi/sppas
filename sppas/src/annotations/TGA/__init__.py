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

    src.annotations.TGA.__init_.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

TGA: Time Group Analyzer is an online tool for speech annotation mining
written by Dafydd Gibbon, emeritus professor of English and General
Linguistics at Bielefeld University..

TGA software calculates, inter alia, mean, median, rPVI, nPVI, slope and
intercept functions within inter-pausal groups.

For details, read the following reference:
    | Dafydd Gibbon (2013).
    | TGA: a web tool for Time Group Analysis.
    | Tools ans Resources for the Analysis of Speech Prosody,
    | Aix-en-Provence, France, pp. 66-69.

See also: <http://wwwhomes.uni-bielefeld.de/gibbon/TGA/>

"""

from .timegroupanalysis import TimeGroupAnalysis
from .sppastga import sppasTGA

__all__ = (
    "TimeGroupAnalysis",
    "sppasTGA"
)
