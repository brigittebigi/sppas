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

    src.annotations.TextNorm.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

The creation of text corpora requires a sequence of processing steps in
order to constitute, normalize, and then to directly exploit it by a given
application.
This package implements a generic approach for text normalization that can
be applied on a multipurpose multilingual text or transcribed corpus.
It consists in splitting the text normalization problem in a set of minor
sub-problems as language-independent as possible. The portability to a new
language consists of heritage of all language independent methods and
rapid adaptation of other language dependent methods or classes.

For details, read the following reference:

    | Brigitte Bigi (2011).
    | A Multilingual Text Normalization Approach.
    | 2nd Less-Resourced Languages workshop,
    | 5th Language & Technology Conference, Poznan (Poland).

"""
from .sppastextnorm import sppasTextNorm
from .orthotranscription import sppasOrthoTranscription
from .splitter import sppasSimpleSplitter
from .tokenize import sppasTokenSegmenter
from .normalize import TextNormalizer

__all__ = (
    'sppasTextNorm',
    'sppasOrthoTranscription',
    'sppasSimpleSplitter',
    'sppasTokenSegmenter',
    'TextNormalizer'
)
