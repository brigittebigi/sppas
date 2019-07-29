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
resources: access and manage linguistic resources
*****************************************************************************

This package includes classes to manage the data of linguistic types like
lexicons, pronunciation dictionaries, patterns, etc.

Requires the following other packages:

* config
* utils

"""
from .dictpron import sppasDictPron
from .dictrepl import sppasDictRepl
from .mapping import sppasMapping
from .wordstrain import sppasWordStrain
from .patterns import sppasPatterns
from .unigram import sppasUnigram
from .vocab import sppasVocabulary
from .dumpfile import sppasDumpFile

__all__ = (
    "sppasMapping",
    "sppasDictRepl",
    "sppasDictPron",
    "sppasWordStrain",
    "sppasPatterns",
    "sppasUnigram",
    "sppasVocabulary",
    "sppasDumpFile"
)
