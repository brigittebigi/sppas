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

    src.annotations.Syll
    ~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

The syllabification of phonemes is performed with a rule-based system.
This RBS phoneme-to-syllable segmentation system is based on 2 main
principles:

    - a syllable contains a vowel, and only one.
    - a pause is a syllable boundary.

These two principles focus the problem of the task of finding a syllabic
boundary between two vowels.
As in state-of-the-art systems, phonemes were grouped into classes and
rules established to deal with these classes.

For details, read the following reference:

    | B. Bigi, C. Meunier, I. Nesterenko, R. Bertrand (2010).
    | Automatic detection of syllable boundaries in spontaneous speech.
    | In Language Resource and Evaluation Conference, pp. 3285–3292,
    | La Valetta, Malta.

"""

from .rules import SyllRules
from .syllabify import Syllabifier
from .sppassyll import sppasSyll

__all__ = (
    'SyllRules',
    'Syllabifier',
    'sppasSyll'
)
