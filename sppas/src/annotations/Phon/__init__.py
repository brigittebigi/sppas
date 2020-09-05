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

    src.annotations.Phon
    ~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

Phonetization is the process of representing sounds with phonetic
signs. There are two general ways to construct a phonetization process:
dictionary based solutions which consist in storing a maximum of
phonological knowledge in a lexicon and rule based systems with rules
based on inference approaches or proposed by expert linguists.

A system based on a dictionary solution consists in storing a maximum
of phonological knowledge in a lexicon. In this sense, this approach
is language-independent unlike rule-based systems. The SPPAS
phonetization of the orthographic transcription produces a phonetic
transcription based on a phonetic dictionary. The phonetization is
the equivalent of a sequence of dictionary look-ups.

It is assumed that all words of the speech transcription are mentioned
in the pronunciation dictionary. Otherwise, SPPAS implements a
language-independent algorithm to phonetize unknown words. This
implementation is in its early stage. It consists in exploring the
unknown word from left to right and to find the longuest strings in
the dictionary. Since this algorithm uses the dictionary, the quality
of such a phonetization will depend on this resource.

Actually, some words can correspond to several entries in the dictionary
with various pronunciations. Unlike rule-based systems, in SPPAS the
pronunciation is not supposed to be ``standard''. Phonetic variants
are proposed for the aligner to choose the phoneme string. The
hypothesis is that the answer to the phonetization question is in the
signal.

SPPAS can take as input a tokenized standard orthographic transcription
and some enrichment only if the acoustic model includes them.
For example, the French transcriptions can contain laugh (represented
by the symbol '@' in the transcription).

The SPPAS phonetization follows the conventions:

    - whitespace separate tokens,
    - minus separate phonemes,
    - pipes separate phonetic variants.

For details, read the following reference:

    | Brigitte Bigi (2016).
    | A phonetization approach for the forced-alignment task in SPPAS.
    | Human Language Technology. Challenges for Computer Science and
    | Linguistics, LNAI 9561, Springer, pp. 515–526.

To summarize:
-------------

A phoneme is the smallest structural unit that distinguishes meaning
in a language. Phonemes are not the physical segments themselves, but
are cognitive abstractions or categorizations of them.
On the other hand, phones refer to the instances of phonemes in the actual
utterances - i.e. the physical segments.

Phonetization consists in searching the possible phones of the given
utterance. In the approach implemented in this package, phonetic variants
are included in the result.

"""

from .sppasphon import sppasPhon
from .phonunk import sppasPhonUnk
from .phonetize import sppasDictPhonetizer

__all__ = (
    'sppasPhon',
    'sppasPhonUnk',
    'sppasDictPhonetizer'
)
