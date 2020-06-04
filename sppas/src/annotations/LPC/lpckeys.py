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

    src.annotations.lpckeys.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.config import separators
from .keyrules import KeyRules

# ----------------------------------------------------------------------------


class LPC(object):
    """LPC keys generation from a sequence of phonemes.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self, keys_filename=None):
        """Create a new LPC instance.

        Load keys from a text file, depending on the language and phonemes
        encoding. See documentation for details about this file.

        :param keys_filename: (str) Name of the file with the list of keys.

        """
        self.rules = KeyRules(keys_filename)

    # -----------------------------------------------------------------------

    def annotate(self, phonemes):
        """Return the key boundaries of a sequence of phonemes.

        Perform the segmentation of the sequence of phonemes into the
        syllables-structure of the LPC coding scheme.
        A syllable is CV, or V or C.

        >>> phonemes = ['b', 'o~', 'j', 'u', 'r']
        >>> LPC("fra-config-file").annotate(phonemes)
        >>> [ (0, 1), (2, 3), (4, 4) ]

        :param phonemes: (list)
        :returns: list of tuples (begin index, end index)

        """
        # Convert a list of phonemes into a list of key classes.
        classes = [self.rules.get_class(p) for p in phonemes]
        syll = list()

        i = 0
        while i < len(phonemes):
            c = classes[i]
            if c in ("V", "C"):
                # if we reach the end of the list of phonemes but a phoneme
                # is still in the list.
                if i+1 == len(phonemes):
                    syll.append((i, i))
                else:
                    # The current phoneme is a vowel
                    if c == "V":
                        syll.append((i, i))
                    else:
                        # The next phoneme is a vowel
                        if classes[i+1] == "V":
                            syll.append((i, i+1))
                            i += 1
                        else:
                            syll.append((i, i))

            i += 1

        return syll

    # -----------------------------------------------------------------------
    # Output formatting
    # -----------------------------------------------------------------------

    @staticmethod
    def phonetize_syllables(phonemes, syllables):
        """Return the phonetized sequence of syllables.

        >>> phonemes = ['b', 'o~', 'j', 'u', 'r']
        >>> lpc_keys = LPC("fra-config-file").annotate(phonemes)
        >>> lpc_keys.phonetize_syllables(phonemes, syllables)
        >>> "b-o~.j-u.r"

        :param phonemes: (list) List of phonemes
        :param syllables: list of tuples (begin index, end index)
        :returns: (str) String representing the syllables segmentation

        The output string is using the X-SAMPA standard to indicate the
        phonemes and syllables segmentation.

        """
        str_syll = list()
        for (begin, end) in syllables:
            str_syll.append(separators.phonemes.join(phonemes[begin:end+1]))

        return separators.syllables.join(str_syll)

    # -----------------------------------------------------------------------

    def keys_phonetized(self, phonetized_syllables):
        """Return the keys of a phonetized syllable as C-V sequences.

        The input string is using the X-SAMPA standard to indicate the
        phonemes and syllables segmentation.

        >>> syllable = "e.p-a.r"
        >>> lpc_keys.keys_phonetized(syllable)
        >>> "0-5.1-3.8-0"

        :param phonetized_syllables: (str) String representing the keys segments
        :return: (str)

        """
        c = list()
        for syll in phonetized_syllables.split(separators.syllables):
            try:
                consonant, vowel = self.rules.get_syll_key(syll)
                c.append(consonant + separators.phonemes + vowel)
            except ValueError:
                c.append(separators.phonemes)

        return separators.syllables.join(c)
