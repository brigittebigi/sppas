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

    annotations.Align.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

This package includes the implementation of the Alignment annotation.

Alignment is the process of aligning speech with its corresponding
transcription at the phone level.
This phonetic segmentation problem consists in a time-matching between a
given speech unit along with a phonetic representation of the unit.
The goal is to generate an alignment between the speech signal and its
phonetic representation.

By default, alignment is based on the Julius Speech Recognition Engine (SRE)
for 3 reasons:
    1. it is  easy to install which is important for users;
    2. it is also easy to use then was easy to integrate in SPPAS;
    3. its performances correspond to the state-of-the-art of HMM-based
    systems and are quite good.

The HTK command "HVite" can also be used to perform Alignment.

A finite state grammar that describes sentence patterns to be recognized and
an acoustic model are needed. A grammar essentially defines constraints on
what the SRE can expect as input. It is a list of words that the SRE listens
to. Each word has a set of associated list of phonemes, extracted from the
dictionary. When given a speech input, Julius searches for the most likely
word sequence under constraint of the given grammar.

Speech Alignment also requires an Acoustic Model in order to align
speech. An acoustic model is a file that contains statistical
representations of each of the distinct sounds of one language.
Each phoneme is represented by one of these statistical representations.
SPPAS is based on the use of HTK-ASCII acoustic models.

"""

from .aligners import sppasAligners
from .tracksgmt import TrackSegmenter
from .tracksio import TracksReaderWriter
from .sppasalign import sppasAlign

__all__ = (
    'sppasAligners',
    'TrackSegmenter',
    'TracksReaderWriter',
    'sppasAlign'
)
